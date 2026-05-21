我負責共同開支帳本功能，這週已建立分支並準備開始開發。

1. SQL 資料庫結構設計
為了滿足共用帳本的功能，我們通常需要 5 個資料表（以下以 SQLite/MySQL 通用的結構為例）：

sql
-- 1. 使用者資料表 (Users)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
-- 2. 帳本 / 群組資料表 (Ledgers)
-- 每個帳本代表一次旅行或一個合租群組
CREATE TABLE ledgers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
-- 3. 帳本成員關聯表 (Ledger_Members)
-- 紀錄哪些使用者在哪個帳本裡 (多對多關聯)
CREATE TABLE ledger_members (
    ledger_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ledger_id, user_id),
    FOREIGN KEY (ledger_id) REFERENCES ledgers(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
-- 4. 支出紀錄主表 (Expenses)
-- 紀錄「這筆錢的總額」與「誰先墊了這筆錢」
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ledger_id INTEGER NOT NULL,
    payer_id INTEGER NOT NULL,        -- 先代墊付款的使用者
    amount DECIMAL(10, 2) NOT NULL,   -- 總金額
    description TEXT NOT NULL,        -- 項目名稱 (例如：晚餐、計程車)
    date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ledger_id) REFERENCES ledgers(id) ON DELETE CASCADE,
    FOREIGN KEY (payer_id) REFERENCES users(id)
);
-- 5. 分攤明細表 (Expense_Splits)
-- 紀錄這筆支出「有哪些人要付」，以及「每個人應負擔多少」
CREATE TABLE expense_splits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,              -- 參與分攤的使用者
    owed_amount DECIMAL(10, 2) NOT NULL,   -- 該使用者應付的金額
    FOREIGN KEY (expense_id) REFERENCES expenses(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
2. Python 分帳演算法範例 (Greedy Algorithm)
分帳的核心邏輯是先算出每個人的「淨餘額（Net Balance）」。

餘額為正：代表他代墊的錢比較多，他應該要收錢。
餘額為負：代表他被代墊的錢比較多，他應該要付錢給別人。
算出餘額後，我們將「欠錢的人」與「該收錢的人」互相抵銷，計算出最少次數的還款動作。

python
def calculate_settlements(expenses, users):
    """
    計算群組內的最終結算方式（誰該給誰多少錢）
    
    :param expenses: 支出列表
    :param users: 群組內的使用者名單
    :return: 結算動作列表
    """
    # 1. 初始化每個人的淨餘額
    balances = {user: 0.0 for user in users}
    
    # 2. 根據每筆支出計算餘額
    for exp in expenses:
        payer = exp['payer']
        amount = exp['amount']
        splits = exp['splits'] # dictionary: { 使用者: 應分攤金額 }
        
        # 付款人淨餘額增加（他可以拿回錢）
        balances[payer] += amount
        
        # 參與分攤的人淨餘額減少（他們欠了錢）
        for user, owed_amount in splits.items():
            balances[user] -= owed_amount
    # 3. 把使用者分為「欠錢的人 (debtors)」和「收錢的人 (creditors)」
    debtors = []
    creditors = []
    for user, balance in balances.items():
        if balance < -0.01: # 欠錢
            debtors.append({'user': user, 'amount': abs(balance)})
        elif balance > 0.01: # 收錢
            creditors.append({'user': user, 'amount': balance})
            
    # （可選）排序金額，讓大筆欠款先還，減少交易次數
    debtors.sort(key=lambda x: x['amount'], reverse=True)
    creditors.sort(key=lambda x: x['amount'], reverse=True)
    
    # 4. 開始匹配還款 (Greedy 演算法)
    settlements = []
    i, j = 0, 0
    
    while i < len(debtors) and j < len(creditors):
        debtor = debtors[i]
        creditor = creditors[j]
        
        # 決定這次還款的金額（取欠款和應收款的最小值）
        settle_amount = min(debtor['amount'], creditor['amount'])
        
        settlements.append({
            'from': debtor['user'],
            'to': creditor['user'],
            'amount': round(settle_amount, 2)
        })
        
        # 扣除已經結算的金額
        debtor['amount'] -= settle_amount
        creditor['amount'] -= settle_amount
        
        # 如果欠款還清了，換下一個欠錢的人
        if debtor['amount'] < 0.01:
            i += 1
        # 如果款項收齊了，換下一個收錢的人
        if creditor['amount'] < 0.01:
            j += 1
            
    return settlements
# ================= 測試範例 =================
if __name__ == "__main__":
    users = ["Alice", "Bob", "Charlie"]
    
    # 模擬支出情境
    mock_expenses = [
        {
            "description": "晚餐",
            "payer": "Alice",
            "amount": 900,
            "splits": {"Alice": 300, "Bob": 300, "Charlie": 300} # 平分
        },
        {
            "description": "計程車",
            "payer": "Bob",
            "amount": 200,
            "splits": {"Bob": 100, "Charlie": 100} # 只有 Bob 和 Charlie 坐車
        }
    ]
    
    # 執行結算
    transactions = calculate_settlements(mock_expenses, users)
    
    print("----- 最終結算清單 -----")
    for t in transactions:
        print(f"{t['from']} 需要支付給 {t['to']} 共 ${t['amount']}")
        
    # 預期結果:
    # Charlie 總共欠 Alice 300 + Bob 100 = 400
    # Bob 欠 Alice 300，但幫 Charlie 墊了 100，所以實際上他總共欠 200，並且要給 Alice。
    # Alice 總共被欠了 600。
    # 結算結果可能會是：
    # Charlie 需要支付給 Alice 共 $400
    # Bob 需要支付給 Alice 共 $200
