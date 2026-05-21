<<<<<<< HEAD
"""
計算輔助工具 (Calc Helpers)
提供電費分攤計算、帳務計算等共用邏輯
"""
=======
def calculate_electricity_splits(total_amount, total_kwh, readings, users_in_group):
    """
    計算本期電費帳單的分攤金額
    :param total_amount: float, 電費總金額
    :param total_kwh: float or None, 本期總用電度數
    :param readings: list of dict/Row, 包含 user_id, personal_kwh 的電表登錄
    :param users_in_group: list of dict/Row, 群組中的所有使用者
    :return: list of dict, 每個使用者的分攤結果，包含 user_id, personal_amount, shared_amount, total_amount
    """
    num_users = len(users_in_group)
    if num_users == 0:
        return []

    # 建立 user_id -> personal_kwh 的對照
    personal_kwh_dict = {u['id']: 0.0 for u in users_in_group}
    for r in readings:
        personal_kwh_dict[r['user_id']] = float(r['personal_kwh'])

    # 如果有總度數且總度數大於 0
    if total_kwh and float(total_kwh) > 0:
        total_kwh_val = float(total_kwh)
        unit_price = total_amount / total_kwh_val
        
        # 個人用電金額
        personal_amounts = {uid: kwh * unit_price for uid, kwh in personal_kwh_dict.items()}
        total_personal_amount = sum(personal_amounts.values())
        
        # 公共分攤金額（總金額減去個人加總，均分）
        shared_amount_total = max(0.0, total_amount - total_personal_amount)
        shared_amount_per_person = shared_amount_total / num_users
    else:
        # 沒有總度數，如果個人度數加總大於 0，就按個人度數比例分攤
        sum_personal_kwh = sum(personal_kwh_dict.values())
        if sum_personal_kwh > 0:
            personal_amounts = {uid: total_amount * (kwh / sum_personal_kwh) for uid, kwh in personal_kwh_dict.items()}
            shared_amount_per_person = 0.0
        else:
            # 完全均分
            personal_amounts = {uid: 0.0 for uid in personal_kwh_dict}
            shared_amount_per_person = total_amount / num_users

    results = []
    for u in users_in_group:
        uid = u['id']
        p_amt = round(personal_amounts[uid], 2)
        s_amt = round(shared_amount_per_person, 2)
        t_amt = round(p_amt + s_amt, 2)
        results.append({
            'user_id': uid,
            'personal_amount': p_amt,
            'shared_amount': s_amt,
            'total_amount': t_amt
        })
        
    return results


def calculate_expense_balances(members, expenses, splits):
    """
    計算成員間的收付款淨額餘額
    :param members: list of dict/Row, 包含使用者資訊 (id, nickname)
    :param expenses: list of dict/Row, 包含支出資訊 (id, paid_by)
    :param splits: list of dict/Row, 包含分攤資訊 (expense_id, user_id, amount, is_settled)
    :return: dict, user_id -> float (正數代表應收，負數代表應付，0 代表結清)
    """
    balances = {m['id']: 0.0 for m in members}
    
    # 建立 expense_id -> paid_by 的對照
    expense_paid_by = {e['id']: e['paid_by'] for e in expenses}
    
    for s in splits:
        if s['is_settled']:
            continue
            
        expense_id = s['expense_id']
        payer_id = expense_paid_by.get(expense_id)
        if not payer_id:
            continue
            
        amount = float(s['amount'])
        debtor_id = s['user_id']
        
        # 債務人（被分攤人）餘額減少
        if debtor_id in balances:
            balances[debtor_id] -= amount
        # 付款人（債權人）餘額增加
        if payer_id in balances:
            balances[payer_id] += amount
            
    # 四捨五入到小數點後兩位
    return {uid: round(bal, 2) for uid, bal in balances.items()}
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
