import os
import sqlite3
import unittest
import sys
from datetime import date, datetime

# 將 app 目錄加入 sys.path，避開載入 app/__init__.py 以免需要 Flask 依賴
sys.path.insert(0, os.path.join(os.getcwd(), 'app'))

import models.user as user_model
import models.group as group_model
import models.agreement as agreement_model
import models.expense as expense_model
import models.electricity as electricity_model
import models.chore as chore_model
import models.reminder as reminder_model
import models.inventory as inventory_model
import models.notification as notification_model

class TestModels(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """
        初始化測試資料庫。
        """
        db_path = os.path.join(os.getcwd(), 'instance', 'database.db')
        # 確保 instance 目錄存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 若資料庫已存在，先刪除以確保全新測試環境
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except OSError:
                pass
                
        # 讀取並執行 schema.sql 建立所有 Table
        schema_path = os.path.join(os.getcwd(), 'database', 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            
        conn = sqlite3.connect(db_path)
        conn.executescript(schema_sql)
        conn.close()

    def test_01_user_and_group_crud(self):
        """
        測試 User 與 Group 的 CRUD 流程。
        """
        # 1. 建立 Group
        group_id = group_model.create({
            'name': '測試寢室301',
            'invite_code': 'INV301',
            'created_by': 1 # 暫設，因為還沒 user
        })
        self.assertIsNotNone(group_id)
        
        # 2. 建立 User
        user_id = user_model.create({
            'email': 'test@example.com',
            'password_hash': 'hashed_password_string',
            'nickname': '小明',
            'role': 'admin',
            'group_id': group_id
        })
        self.assertIsNotNone(user_id)
        
        # 更新 Group 的建立人 ID
        group_model.update(group_id, {'created_by': user_id})
        
        # 3. 測試讀取
        user = user_model.get_by_id(user_id)
        self.assertEqual(user['email'], 'test@example.com')
        self.assertEqual(user['nickname'], '小明')
        self.assertEqual(user['role'], 'admin')
        self.assertEqual(user['group_id'], group_id)
        
        user_by_email = user_model.get_by_email('test@example.com')
        self.assertEqual(user_by_email['id'], user_id)
        
        # 4. 測試更新
        update_success = user_model.update(user_id, {'nickname': '大明'})
        self.assertTrue(update_success)
        user_updated = user_model.get_by_id(user_id)
        self.assertEqual(user_updated['nickname'], '大明')
        
        # 5. 測試取得所有記錄
        users = user_model.get_all()
        self.assertEqual(len(users), 1)

    def test_02_agreement_crud(self):
        """
        測試公約的 CRUD、版本歷史與同意記錄。
        """
        # 取得剛才建立的 user
        user = user_model.get_all()[0]
        group = group_model.get_all()[0]
        
        # 1. 新增公約 (預設會自動寫入第一版版本歷史)
        agreement_id = agreement_model.create({
            'group_id': group['id'],
            'title': '安靜公約',
            'category': 'noise',
            'content': '晚上11點後不開喇叭',
            'status': 'pending',
            'created_by': user['id']
        })
        self.assertIsNotNone(agreement_id)
        
        # 2. 取得公約
        agr = agreement_model.get_by_id(agreement_id)
        self.assertEqual(agr['title'], '安靜公約')
        
        # 3. 取得群組公約
        agrs = agreement_model.get_by_group(group['id'])
        self.assertEqual(len(agrs), 1)
        
        # 4. 修改公約 (應自動寫入第二版變更記錄)
        update_success = agreement_model.update(agreement_id, {
            'content': '晚上11點後不開喇叭，且講電話請至陽台',
            'modified_by': user['id']
        })
        self.assertTrue(update_success)
        
        # 5. 檢查版本歷史
        versions = agreement_model.get_versions(agreement_id)
        self.assertEqual(len(versions), 2)
        self.assertEqual(versions[0]['version_number'], 2)
        
        # 6. 同意投票
        approve_success = agreement_model.approve(agreement_id, user['id'])
        self.assertTrue(approve_success)
        
        approvals = agreement_model.get_approvals(agreement_id)
        self.assertEqual(len(approvals), 1)
        self.assertEqual(approvals[0]['nickname'], user['nickname'])

    def test_03_expense_crud(self):
        """
        測試記帳與分攤計算。
        """
        user = user_model.get_all()[0]
        group = group_model.get_all()[0]
        
        # 再新增一個成員以測試分攤
        user2_id = user_model.create({
            'email': 'roommate@example.com',
            'password_hash': 'hash',
            'nickname': '室友A',
            'role': 'member',
            'group_id': group['id']
        })
        
        # 1. 建立一筆共同開支（均攤）
        expense_id = expense_model.create({
            'group_id': group['id'],
            'title': '公共衛生紙',
            'amount': 200.0,
            'category': '日用品',
            'paid_by': user['id']
        })
        self.assertIsNotNone(expense_id)
        
        # 2. 檢查分攤明細
        splits = expense_model.get_splits(expense_id)
        self.assertEqual(len(splits), 2) # 兩位成員
        
        # 付款人為 user (大明)，他的分攤應自動標記為 is_settled = 1
        for s in splits:
            if s['user_id'] == user['id']:
                self.assertEqual(s['is_settled'], 1)
            else:
                self.assertEqual(s['is_settled'], 0)
                self.assertEqual(s['amount'], 100.0)
                
        # 3. 取得群組開支列表
        expenses = expense_model.get_by_group(group['id'])
        self.assertEqual(len(expenses), 1)
        
        # 4. 檢查財務餘額總覽
        balances = expense_model.get_group_balances(group['id'])
        # 大明付了 200，分攤 100 給室友A。大明應收 100。
        self.assertEqual(balances[user['id']]['receivable'], 100.0)
        self.assertEqual(balances[user['id']]['payable'], 0.0)
        self.assertEqual(balances[user['id']]['net'], 100.0)
        
        # 室友A應付 100。
        self.assertEqual(balances[user2_id]['receivable'], 0.0)
        self.assertEqual(balances[user2_id]['payable'], 100.0)
        self.assertEqual(balances[user2_id]['net'], -100.0)
        
        # 5. 結清帳務
        settle_success = expense_model.settle_group_expenses(group['id'], user2_id)
        self.assertTrue(settle_success)
        
        # 結清後，餘額應歸零
        balances_after = expense_model.get_group_balances(group['id'])
        self.assertEqual(balances_after[user['id']]['net'], 0.0)
        self.assertEqual(balances_after[user2_id]['net'], 0.0)

    def test_04_electricity_crud(self):
        """
        測試電費模組。
        """
        user = user_model.get_all()[0]
        group = group_model.get_all()[0]
        
        # 1. 建立電費帳單
        bill_id = electricity_model.create({
            'group_id': group['id'],
            'total_amount': 1500.0,
            'total_kwh': 500.0,
            'period_start': '2026-04-01',
            'period_end': '2026-05-01',
            'created_by': user['id']
        })
        self.assertIsNotNone(bill_id)
        
        # 2. 登錄個人度數
        reading_id = electricity_model.create_meter_reading({
            'bill_id': bill_id,
            'user_id': user['id'],
            'start_reading': 100.0,
            'end_reading': 250.0
        })
        self.assertIsNotNone(reading_id)
        
        # 3. 取得度數登錄
        readings = electricity_model.get_meter_readings(bill_id)
        self.assertEqual(len(readings), 1)
        self.assertEqual(readings[0]['personal_kwh'], 150.0)
        
        # 4. 寫入電費分攤並繳費
        split_id = electricity_model.create_split({
            'bill_id': bill_id,
            'user_id': user['id'],
            'personal_amount': 450.0,
            'shared_amount': 300.0,
            'total_amount': 750.0,
            'is_paid': 0
        })
        self.assertIsNotNone(split_id)
        
        # 繳費
        pay_success = electricity_model.mark_split_paid(split_id)
        self.assertTrue(pay_success)
        
        splits = electricity_model.get_splits(bill_id)
        self.assertEqual(splits[0]['is_paid'], 1)

    def test_05_chore_crud(self):
        """
        測試家事排班。
        """
        user = user_model.get_all()[0]
        group = group_model.get_all()[0]
        
        # 1. 建立家事
        chore_id = chore_model.create({
            'group_id': group['id'],
            'title': '倒廚餘',
            'description': '倒黑色桶子的廚餘',
            'recurrence': 'weekly',
            'due_date': '2026-05-25',
            'assigned_to': user['id'],
            'created_by': user['id']
        })
        self.assertIsNotNone(chore_id)
        
        # 2. 查詢個人待辦家事
        chores = chore_model.get_by_user(user['id'])
        self.assertEqual(len(chores), 1)
        self.assertEqual(chores[0]['title'], '倒廚餘')
        
        # 3. 完成家事
        complete_success = chore_model.mark_completed(chore_id)
        self.assertTrue(complete_success)
        
        # 再次查詢已無待辦
        chores_after = chore_model.get_by_user(user['id'])
        self.assertEqual(len(chores_after), 0)

    def test_06_reminder_crud(self):
        """
        測試匿名提醒、匿名性與冷卻狀態。
        """
        users = user_model.get_all()
        user1 = users[0]
        user2 = users[1]
        group = group_model.get_all()[0]
        
        # 1. 發送匿名提醒
        reminder_id = reminder_model.create({
            'group_id': group['id'],
            'sender_id': user1['id'],
            'receiver_id': user2['id'],
            'category': 'noise',
            'message': '深夜音量稍大，感謝配合'
        })
        self.assertIsNotNone(reminder_id)
        
        # 2. 測試冷卻狀態
        is_cooling = reminder_model.get_cooldown_status(user1['id'], user2['id'])
        self.assertTrue(is_cooling) # 發送後 1 小時內應處於冷卻中
        
        # 3. 測試接收者查詢 (不應包含 sender_id)
        received = reminder_model.get_received_reminders(user2['id'])
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['message'], '深夜音量稍大，感謝配合')
        self.assertNotIn('sender_id', received[0].keys()) # 絕對不能有 sender_id
        
        # 4. 統計資料
        stats = reminder_model.get_group_stats(group['id'])
        self.assertEqual(stats['noise'], 1)
        self.assertEqual(stats['hygiene'], 0)

    def test_07_inventory_crud(self):
        """
        測試庫存管理與交易原子性。
        """
        user = user_model.get_all()[0]
        group = group_model.get_all()[0]
        
        # 1. 建立物資品項（包含初始庫存 10）
        item_id = inventory_model.create({
            'group_id': group['id'],
            'name': '垃圾袋',
            'unit': '包',
            'quantity': 10,
            'min_quantity': 2,
            'created_by': user['id']
        })
        self.assertIsNotNone(item_id)
        
        # 2. 進行消耗出庫
        log_id = inventory_model.log_transaction({
            'item_id': item_id,
            'user_id': user['id'],
            'action': 'stock_out',
            'quantity': 3,
            'note': '打掃公區使用'
        })
        self.assertIsNotNone(log_id)
        
        # 3. 驗證庫存量 (10 - 3 = 7)
        item = inventory_model.get_by_id(item_id)
        self.assertEqual(item['quantity'], 7)
        
        # 4. 驗證日誌記錄
        logs = inventory_model.get_logs(item_id)
        self.assertEqual(len(logs), 2) # 初始建立 (stock_in) + 消耗出庫 (stock_out)
        self.assertEqual(logs[0]['action'], 'stock_out')
        self.assertEqual(logs[0]['quantity'], 3)

    def test_08_notification_crud(self):
        """
        測試站內通知。
        """
        user = user_model.get_all()[0]
        group = group_model.get_all()[0]
        
        # 1. 建立通知
        noti_id = notification_model.create({
            'user_id': user['id'],
            'group_id': group['id'],
            'type': 'chore',
            'title': '新家事指派',
            'message': '您已被指派負責「倒廚餘」任務。'
        })
        self.assertIsNotNone(noti_id)
        
        # 2. 查詢未讀通知
        unreads = notification_model.get_unread_notifications(user['id'])
        self.assertEqual(len(unreads), 1)
        self.assertEqual(unreads[0]['title'], '新家事指派')
        
        # 3. 批次標記已讀
        read_success = notification_model.mark_all_read(user['id'])
        self.assertTrue(read_success)
        
        # 再次查詢已無未讀
        unreads_after = notification_model.get_unread_notifications(user['id'])
        self.assertEqual(len(unreads_after), 0)

if __name__ == '__main__':
    unittest.main()
