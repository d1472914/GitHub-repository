-- =============================================
-- 宿舍共好 — 室友公約與噪音管理系統
-- SQLite 資料庫建表語法
-- =============================================

-- 啟用外鍵約束（SQLite 預設不啟用）
PRAGMA foreign_keys = ON;

-- ----- 1. 群組 -----
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    invite_code VARCHAR(20) NOT NULL UNIQUE,
    created_by INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----- 2. 使用者 -----
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    nickname VARCHAR(50) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'member',
    group_id INTEGER,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups (id)
);

-- 補上 groups.created_by 的外鍵（因建表順序，用觸發器或應用層保證）

-- ----- 3. 公約 -----
CREATE TABLE IF NOT EXISTS agreements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_by INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups (id),
    FOREIGN KEY (created_by) REFERENCES users (id)
);

-- ----- 4. 公約版本歷史 -----
CREATE TABLE IF NOT EXISTS agreement_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    agreement_id INTEGER NOT NULL,
    version_number INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    content_before TEXT,
    content_after TEXT NOT NULL,
    change_summary VARCHAR(250),
    modified_by INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agreement_id) REFERENCES agreements (id),
    FOREIGN KEY (modified_by) REFERENCES users (id)
);

-- ----- 5. 公約同意記錄 -----
CREATE TABLE IF NOT EXISTS agreement_approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agreement_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    approved_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agreement_id) REFERENCES agreements (id),
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE (agreement_id, user_id)
);

-- ----- 6. 共同開支 -----
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    amount FLOAT NOT NULL,
    category VARCHAR(50),
    paid_by INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups (id),
    FOREIGN KEY (paid_by) REFERENCES users (id)
);

-- ----- 7. 開支分攤 -----
CREATE TABLE IF NOT EXISTS expense_splits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    amount FLOAT NOT NULL,
    is_settled BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (expense_id) REFERENCES expenses (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- ----- 8. 電費帳單 -----
CREATE TABLE IF NOT EXISTS electricity_bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    total_amount FLOAT NOT NULL,
    total_kwh FLOAT,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    created_by INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups (id),
    FOREIGN KEY (created_by) REFERENCES users (id)
);

-- ----- 9. 電表度數 -----
CREATE TABLE IF NOT EXISTS meter_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    start_reading FLOAT NOT NULL,
    end_reading FLOAT NOT NULL,
    personal_kwh FLOAT NOT NULL,
    FOREIGN KEY (bill_id) REFERENCES electricity_bills (id),
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE (bill_id, user_id)
);

-- ----- 10. 電費分攤 -----
CREATE TABLE IF NOT EXISTS electricity_splits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    personal_amount FLOAT NOT NULL,
    shared_amount FLOAT NOT NULL,
    total_amount FLOAT NOT NULL,
    is_paid BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (bill_id) REFERENCES electricity_bills (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- ----- 11. 家事任務 -----
CREATE TABLE IF NOT EXISTS chores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    recurrence VARCHAR(20) NOT NULL DEFAULT 'once',
    due_date DATE NOT NULL,
    assigned_to INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_by INTEGER NOT NULL,
    completed_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups (id),
    FOREIGN KEY (assigned_to) REFERENCES users (id),
    FOREIGN KEY (created_by) REFERENCES users (id)
);

-- ----- 12. 匿名提醒 -----
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    category VARCHAR(30) NOT NULL,
    message TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups (id),
    FOREIGN KEY (sender_id) REFERENCES users (id),
    FOREIGN KEY (receiver_id) REFERENCES users (id)
);

-- ----- 13. 物資品項 -----
CREATE TABLE IF NOT EXISTS inventory_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    min_quantity INTEGER NOT NULL DEFAULT 0,
    created_by INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups (id),
    FOREIGN KEY (created_by) REFERENCES users (id)
);

-- ----- 14. 物資操作記錄 -----
CREATE TABLE IF NOT EXISTS inventory_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    action VARCHAR(10) NOT NULL,
    quantity INTEGER NOT NULL,
    note VARCHAR(200),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES inventory_items (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- ----- 15. 站內通知 -----
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    type VARCHAR(30) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT,
    is_read BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (group_id) REFERENCES groups (id)
);
