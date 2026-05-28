import os
import sqlite3
from werkzeug.security import generate_password_hash

DATABASE_PATH = os.path.join('instance', 'database.db')

def seed():
    print(f"Seeding database: {DATABASE_PATH}...")
    if not os.path.exists(DATABASE_PATH):
        print("Database does not exist. Please run init_db.py first!")
        return

    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    try:
        # Clear existing data
        cursor.execute("DELETE FROM notifications")
        cursor.execute("DELETE FROM inventory_logs")
        cursor.execute("DELETE FROM inventory_items")
        cursor.execute("DELETE FROM reminders")
        cursor.execute("DELETE FROM chores")
        cursor.execute("DELETE FROM electricity_splits")
        cursor.execute("DELETE FROM meter_readings")
        cursor.execute("DELETE FROM electricity_bills")
        cursor.execute("DELETE FROM expense_splits")
        cursor.execute("DELETE FROM expenses")
        cursor.execute("DELETE FROM agreement_approvals")
        cursor.execute("DELETE FROM agreement_versions")
        cursor.execute("DELETE FROM agreements")
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM groups")
        conn.commit()
        print("Cleared old data.")

        # 1. Create a group
        cursor.execute("""
            INSERT INTO groups (name, invite_code, created_by, created_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, ("幸福公寓 302 室", "TEST1234", 1))
        group_id = cursor.lastrowid
        print(f"Group created: ID={group_id}")

        # 2. Create users with hashed passwords
        pass_admin = generate_password_hash("admin123")
        pass_user = generate_password_hash("user123")

        users_data = [
            ("admin@dorm.com", pass_admin, "阿傑", "admin", group_id),
            ("user1@dorm.com", pass_user, "小明", "member", group_id),
            ("user2@dorm.com", pass_user, "大強", "member", group_id),
            ("user3@dorm.com", pass_user, "婷婷", "member", group_id),
        ]

        user_ids = {}
        for email, pass_hash, nickname, role, g_id in users_data:
            cursor.execute("""
                INSERT INTO users (email, password_hash, nickname, role, group_id)
                VALUES (?, ?, ?, ?, ?)
            """, (email, pass_hash, nickname, role, g_id))
            user_ids[nickname] = cursor.lastrowid
            print(f"User created: {nickname} (ID={user_ids[nickname]})")

        # Update group created_by to be the admin's actual ID (which is user_ids["阿傑"])
        cursor.execute("UPDATE groups SET created_by = ? WHERE id = ?", (user_ids["阿傑"], group_id))

        # 3. Create agreements
        agreements_data = [
            (
                "深夜安靜與噪音公約",
                "生活規範",
                "晚上 10 點至隔天早上 8 點為安靜時段。在此期間，若要播放音樂或語音通話，請配戴耳機；若需吹頭髮或使用高噪音電器，請在晚上 10 點前完成，或至公共浴室使用。",
                "approved",
                user_ids["阿傑"]
            ),
            (
                "廚房與碗盤清理",
                "環境衛生",
                "使用完廚房後，瓦斯爐面及水槽須擦拭乾淨。個人餐具與鍋具需在餐後 2 小時內清洗完畢並瀝乾，不可堆放過夜。公用鍋具使用後需立即清洗。",
                "pending",
                user_ids["小明"]
            )
        ]

        agreement_ids = []
        for title, category, content, status, creator_id in agreements_data:
            cursor.execute("""
                INSERT INTO agreements (group_id, title, category, content, status, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (group_id, title, category, content, status, creator_id))
            agreement_ids.append(cursor.lastrowid)

        # 4. Create agreement approvals
        # Everyone approves the noise agreement
        for nickname, uid in user_ids.items():
            cursor.execute("""
                INSERT INTO agreement_approvals (agreement_id, user_id)
                VALUES (?, ?)
            """, (agreement_ids[0], uid))
        # Only creator and one other person approves kitchen agreement
        cursor.execute("""
            INSERT INTO agreement_approvals (agreement_id, user_id)
            VALUES (?, ?)
        """, (agreement_ids[1], user_ids["小明"]))
        cursor.execute("""
            INSERT INTO agreement_approvals (agreement_id, user_id)
            VALUES (?, ?)
        """, (agreement_ids[1], user_ids["婷婷"]))

        # 5. Create expenses
        # Expense 1: 5月份公用衛生紙與洗碗精, Amount: 300, Paid by: 阿傑. Split among all 4.
        cursor.execute("""
            INSERT INTO expenses (group_id, title, amount, category, paid_by)
            VALUES (?, ?, ?, ?, ?)
        """, (group_id, "5月份公用衛生紙與洗碗精", 300.0, "日常用品", user_ids["阿傑"]))
        exp1_id = cursor.lastrowid

        for uid in user_ids.values():
            cursor.execute("""
                INSERT INTO expense_splits (expense_id, user_id, amount, is_settled)
                VALUES (?, ?, ?, ?)
            """, (exp1_id, uid, 75.0, 0))

        # Expense 2: 客廳冷氣清潔費, Amount: 2000, Paid by: 婷婷. Split among all 4.
        cursor.execute("""
            INSERT INTO expenses (group_id, title, amount, category, paid_by)
            VALUES (?, ?, ?, ?, ?)
        """, (group_id, "客廳冷氣清潔費", 2000.0, "公共維護", user_ids["婷婷"]))
        exp2_id = cursor.lastrowid

        for uid in user_ids.values():
            cursor.execute("""
                INSERT INTO expense_splits (expense_id, user_id, amount, is_settled)
                VALUES (?, ?, ?, ?)
            """, (exp2_id, uid, 500.0, 0))

        # 6. Electricity bill, readings, and splits
        # Total Amount = 1200, Total KWH = 400.
        cursor.execute("""
            INSERT INTO electricity_bills (group_id, total_amount, total_kwh, period_start, period_end, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (group_id, 1200.0, 400.0, "2026-05-01", "2026-05-28", user_ids["阿傑"]))
        bill_id = cursor.lastrowid

        # Readings:
        # 阿傑: 1000 - 1080 (80)
        # 小明: 2000 - 2100 (100)
        # 大強: 3000 - 3120 (120)
        # 婷婷: 4000 - 4060 (60)
        # Total personal = 360. Shared = 40. Shared/person = 10.
        # Price per KWH = 3.
        # Total: personal * 3 + 30.
        readings = [
            (user_ids["阿傑"], 1000.0, 1080.0, 80.0, 240.0, 30.0, 270.0, 1),
            (user_ids["小明"], 2000.0, 2100.0, 100.0, 300.0, 30.0, 330.0, 0),
            (user_ids["大強"], 3000.0, 3120.0, 120.0, 360.0, 30.0, 390.0, 0),
            (user_ids["婷婷"], 4000.0, 4060.0, 60.0, 180.0, 30.0, 210.0, 1),
        ]

        for uid, start, end, pkwh, pamt, shamt, totamt, is_paid in readings:
            cursor.execute("""
                INSERT INTO meter_readings (bill_id, user_id, start_reading, end_reading, personal_kwh)
                VALUES (?, ?, ?, ?, ?)
            """, (bill_id, uid, start, end, pkwh))

            cursor.execute("""
                INSERT INTO electricity_splits (bill_id, user_id, personal_amount, shared_amount, total_amount, is_paid)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (bill_id, uid, pamt, shamt, totamt, is_paid))

        # 7. Chores
        chores = [
            ("客廳地板吸地與拖地", "每週一次，包含沙發底下及角落塵埃。", "weekly", "2026-05-30", user_ids["小明"], "pending", user_ids["阿傑"], None),
            ("浴室垃圾打包與垃圾桶刷洗", "倒垃圾並更換垃圾袋，垃圾桶順手刷洗乾淨。", "weekly", "2026-05-27", user_ids["大強"], "completed", user_ids["阿傑"], "2026-05-27 19:00:00"),
            ("廚房水槽與廚餘清理", "每天晚上 10 點前需將廚餘打包拿去冰或倒掉，水槽濾網需刷洗。", "daily", "2026-05-28", user_ids["婷婷"], "pending", user_ids["阿傑"], None),
        ]

        for title, desc, rec, due, assigned, status, creator, comp_time in chores:
            cursor.execute("""
                INSERT INTO chores (group_id, title, description, recurrence, due_date, assigned_to, status, created_by, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (group_id, title, desc, rec, due, assigned, status, creator, comp_time))

        # 8. Reminders
        reminders = [
            (group_id, user_ids["阿傑"], user_ids["小明"], "噪音", "哈囉～現在的音量好像有點大喔！可以稍微降低一點點嗎？感謝啦！🙌"),
            (group_id, user_ids["婷婷"], user_ids["大強"], "環境衛生", "嗨大強，浴室的垃圾好像滿了，有空的話幫忙順手倒一下，謝啦！🙏"),
        ]

        for g_id, snd, rcv, cat, msg in reminders:
            cursor.execute("""
                INSERT INTO reminders (group_id, sender_id, receiver_id, category, message)
                VALUES (?, ?, ?, ?, ?)
            """, (g_id, snd, rcv, cat, msg))

        # 9. Inventory Items
        items = [
            ("公用衛生紙", "包", 2, 5, user_ids["阿傑"]),
            ("洗碗精", "瓶", 1, 1, user_ids["小明"]),
            ("垃圾袋 (大)", "張", 15, 10, user_ids["大強"]),
        ]

        item_ids = []
        for name, unit, qty, min_qty, creator in items:
            cursor.execute("""
                INSERT INTO inventory_items (group_id, name, unit, quantity, min_quantity, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (group_id, name, unit, qty, min_qty, creator))
            item_ids.append(cursor.lastrowid)

        # Inventory Logs
        logs = [
            (item_ids[0], user_ids["阿傑"], "out", 1, "客廳公用面紙盒補充"),
            (item_ids[0], user_ids["婷婷"], "in", 6, "美式賣場大包裝補充"),
        ]

        for it_id, uid, act, qty, note in logs:
            cursor.execute("""
                INSERT INTO inventory_logs (item_id, user_id, action, quantity, note)
                VALUES (?, ?, ?, ?, ?)
            """, (it_id, uid, act, qty, note))

        # 10. Notifications
        notifications = [
            (user_ids["小明"], group_id, "chore", "新家事任務指派", "阿傑指派了任務【客廳地板吸地與拖地】給您，期限至 2026-05-30。"),
            (user_ids["大強"], group_id, "reminder", "收到匿名溫馨提醒", "您收到了一則關於【環境衛生】的匿名提醒，請前往提醒專區查看。"),
        ]

        for uid, g_id, ntype, title, msg in notifications:
            cursor.execute("""
                INSERT INTO notifications (user_id, group_id, type, title, message, is_read)
                VALUES (?, ?, ?, ?, ?, 0)
            """, (uid, g_id, ntype, title, msg))

        conn.commit()
        print("Database seeded successfully with rich demo data!")

    except Exception as e:
        conn.rollback()
        print(f"Error seeding database: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    seed()
