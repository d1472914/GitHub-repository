def calculate_expense_split(amount, num_people):
    """
    計算每人應均攤的開支金額。
    """
    if num_people <= 0:
        return 0
    return round(amount / num_people, 2)

def calculate_electricity_split(personal_kwh, total_shared_kwh, per_kwh_rate, num_people):
    """
    計算每人電費（個人用電 + 公共均攤用電）。
    """
    personal_cost = personal_kwh * per_kwh_rate
    shared_cost = (total_shared_kwh * per_kwh_rate) / num_people if num_people > 0 else 0
    return {
        'personal_amount': round(personal_cost, 2),
        'shared_amount': round(shared_cost, 2),
        'total_amount': round(personal_cost + shared_cost, 2)
    }
