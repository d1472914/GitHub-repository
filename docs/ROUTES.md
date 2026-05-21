# 路由設計文件：宿舍共好 — 室友公約與噪音管理系統

---

## 1. 路由總覽表格

### 1.1 身份驗證（auth）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :---: | :--- | :--- | :--- |
| 註冊頁面 | GET | /auth/register | auth/register.html | 顯示註冊表單 |
| 註冊處理 | POST | /auth/register | — | 建立帳號，重導向登入頁 |
| 登入頁面 | GET | /auth/login | auth/login.html | 顯示登入表單 |
| 登入處理 | POST | /auth/login | — | 驗證帳密，重導向儀表板 |
| 登出 | GET | /auth/logout | — | 清除 session，重導向登入頁 |

### 1.2 儀表板（dashboard）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :---: | :--- | :--- | :--- |
| 首頁 | GET | /dashboard | dashboard/index.html | 總覽通知、待辦、快捷入口 |

### 1.3 群組管理（group）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :---: | :--- | :--- | :--- |
| 建立群組頁面 | GET | /group/create | group/create.html | 顯示建立表單 |
| 建立群組處理 | POST | /group/create | — | 建立群組，重導向設定頁 |
| 加入群組頁面 | GET | /group/join | group/join.html | 顯示邀請碼輸入表單 |
| 加入群組處理 | POST | /group/join | — | 驗證邀請碼，加入群組 |
| 群組設定頁面 | GET | /group/settings | group/settings.html | 群組資訊與成員管理 |
| 更新群組設定 | POST | /group/settings | — | 儲存群組設定 |

### 1.4 公約異動記錄（agreement）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :---: | :--- | :--- | :--- |
| 公約列表 | GET | /agreements | agreement/list.html | 顯示群組所有公約 |
| 新增公約頁面 | GET | /agreements/new | agreement/form.html | 顯示新增表單 |
| 新增公約處理 | POST | /agreements | — | 建立公約與版本記錄 |
| 公約詳情 | GET | /agreements/\<id\> | agreement/detail.html | 條文與歷史版本 |
| 編輯公約頁面 | GET | /agreements/\<id\>/edit | agreement/form.html | 顯示編輯表單 |
| 更新公約 | POST | /agreements/\<id\>/update | — | 更新並記錄差異 |
| 刪除公約 | POST | /agreements/\<id\>/delete | — | 刪除後重導向列表 |
| 同意公約 | POST | /agreements/\<id\>/approve | — | 記錄同意，檢查是否全數通過 |

### 1.5 共同開支帳本（expense）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :---: | :--- | :--- | :--- |
| 帳本列表 | GET | /expenses | expense/list.html | 顯示消費記錄 |
| 新增記帳頁面 | GET | /expenses/new | expense/form.html | 顯示記帳表單 |
| 新增記帳處理 | POST | /expenses | — | 建立開支與分攤 |
| 餘額總覽 | GET | /expenses/balance | expense/balance.html | 各人應收應付 |
| 結算處理 | POST | /expenses/settle | — | 標記結清，重導向餘額頁 |

### 1.6 智慧電費（electricity）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :---: | :--- | :--- | :--- |
| 帳單列表 | GET | /electricity | electricity/list.html | 歷史電費帳單 |
| 新增帳單頁面 | GET | /electricity/new | electricity/form.html | 帳單登錄表單 |
| 新增帳單處理 | POST | /electricity | — | 建立帳單 |
| 帳單詳情 | GET | /electricity/\<id\> | electricity/detail.html | 分攤明細 |
| 登錄電表頁面 | GET | /electricity/\<id\>/meter | electricity/meter_form.html | 電表度數表單 |
| 登錄電表處理 | POST | /electricity/\<id\>/meter | — | 儲存度數並計算分攤 |

### 1.7 隱形管家（chore）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :---: | :--- | :--- | :--- |
| 任務列表 | GET | /chores | chore/list.html | 顯示所有任務 |
| 輪值日曆 | GET | /chores/calendar | chore/calendar.html | 視覺化排班 |
| 新增任務頁面 | GET | /chores/new | chore/form.html | 任務表單 |
| 新增任務處理 | POST | /chores | — | 建立任務 |
| 編輯任務頁面 | GET | /chores/\<id\>/edit | chore/form.html | 編輯表單 |
| 更新任務 | POST | /chores/\<id\>/update | — | 儲存修改 |
| 完成任務 | POST | /chores/\<id\>/complete | — | 標記完成 |

### 1.8 友善黑臉（reminder）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :---: | :--- | :--- | :--- |
| 發送提醒頁面 | GET | /reminders/send | reminder/send.html | 發送表單 |
| 發送提醒處理 | POST | /reminders/send | — | 建立匿名提醒 |
| 提醒收件匣 | GET | /reminders/inbox | reminder/inbox.html | 收到的提醒 |
| 統計摘要 | GET | /reminders/stats | reminder/stats.html | 管理者統計 |

### 1.9 共同物資庫存（inventory）

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :---: | :--- | :--- | :--- |
| 物資清單 | GET | /inventory | inventory/list.html | 所有物資品項 |
| 新增物資頁面 | GET | /inventory/new | inventory/form.html | 新增表單 |
| 新增物資處理 | POST | /inventory | — | 建立物資品項 |
| 物資詳情 | GET | /inventory/\<id\> | inventory/detail.html | 入出庫歷史 |
| 編輯物資頁面 | GET | /inventory/\<id\>/edit | inventory/form.html | 編輯表單 |
| 更新物資 | POST | /inventory/\<id\>/update | — | 儲存修改 |
| 入庫登記 | POST | /inventory/\<id\>/stock-in | — | 增加庫存 |
| 出庫登記 | POST | /inventory/\<id\>/stock-out | — | 減少庫存 |

---

## 2. 路由詳細說明

### 2.1 身份驗證（auth.py）

#### `GET /auth/register` — 註冊頁面
- **輸入**：無
- **處理**：渲染註冊表單
- **輸出**：`auth/register.html`
- **錯誤處理**：若已登入，重導向 `/dashboard`

#### `POST /auth/register` — 註冊處理
- **輸入**：表單欄位 `email`, `password`, `confirm_password`, `nickname`
- **處理**：驗證資料 → `User.get_by_email()` 確認不重複 → 密碼雜湊 → `User.create()`
- **輸出**：成功 → 重導向 `/auth/login`；失敗 → 回到註冊頁並顯示錯誤
- **錯誤處理**：Email 已存在、密碼不一致、欄位為空

#### `GET /auth/login` — 登入頁面
- **輸入**：無
- **處理**：渲染登入表單
- **輸出**：`auth/login.html`
- **錯誤處理**：若已登入，重導向 `/dashboard`

#### `POST /auth/login` — 登入處理
- **輸入**：表單欄位 `email`, `password`
- **處理**：`User.get_by_email()` → 驗證密碼雜湊 → `login_user()`
- **輸出**：成功 → 重導向 `/dashboard`；失敗 → 回到登入頁
- **錯誤處理**：帳號不存在、密碼錯誤

#### `GET /auth/logout` — 登出
- **輸入**：無
- **處理**：`logout_user()` 清除 session
- **輸出**：重導向 `/auth/login`

---

### 2.2 儀表板（dashboard.py）

#### `GET /dashboard` — 首頁
- **輸入**：無（從 session 取得 `current_user`）
- **處理**：`Notification.get_unread_by_user()` + `Chore.get_pending_by_user()` 取得待辦與通知
- **輸出**：`dashboard/index.html`（傳入通知、待辦、群組資訊）
- **錯誤處理**：未登入 → 重導向 `/auth/login`；未加入群組 → 重導向 `/group/create`

---

### 2.3 群組管理（group.py）

#### `POST /group/create` — 建立群組
- **輸入**：表單欄位 `name`
- **處理**：產生隨機邀請碼 → `Group.create()` → 更新 `current_user.group_id`
- **輸出**：重導向 `/group/settings`
- **錯誤處理**：名稱為空

#### `POST /group/join` — 加入群組
- **輸入**：表單欄位 `invite_code`
- **處理**：`Group.get_by_invite_code()` → 更新 `current_user.group_id`
- **輸出**：重導向 `/dashboard`
- **錯誤處理**：邀請碼無效（404）

---

### 2.4 公約異動記錄（agreement.py）

#### `POST /agreements` — 新增公約
- **輸入**：表單欄位 `title`, `category`, `content`
- **處理**：`Agreement.create()` → `AgreementVersion.create(version_number=1)` → 自動建立提案者的同意記錄
- **輸出**：重導向 `/agreements/<id>`
- **錯誤處理**：欄位為空

#### `POST /agreements/<id>/update` — 更新公約
- **輸入**：URL 參數 `id`；表單欄位 `title`, `category`, `content`
- **處理**：`Agreement.get_by_id()` → 記錄舊內容 → `AgreementVersion.create()` → `agreement.update()` → 重設同意記錄
- **輸出**：重導向 `/agreements/<id>`
- **錯誤處理**：公約不存在（404）

#### `POST /agreements/<id>/approve` — 同意公約
- **輸入**：URL 參數 `id`
- **處理**：`AgreementApproval.has_approved()` 檢查 → `AgreementApproval.create()` → 檢查是否全部同意 → 若是則 `agreement.update(status='active')`
- **輸出**：重導向 `/agreements/<id>`
- **錯誤處理**：已同意過（忽略）、公約不存在（404）

---

### 2.5 共同開支帳本（expense.py）

#### `POST /expenses` — 新增記帳
- **輸入**：表單欄位 `title`, `amount`, `category`, `split_users[]`（分攤對象勾選）
- **處理**：`Expense.create()` → 計算每人分攤金額 → 為每位分攤對象 `ExpenseSplit.create()`
- **輸出**：重導向 `/expenses`
- **錯誤處理**：金額非正數、未選擇分攤對象

#### `POST /expenses/settle` — 結算
- **輸入**：表單欄位 `settle_with_user_id`（結算對象）
- **處理**：找出雙方所有未結清的 `ExpenseSplit` → 標記 `is_settled=True`
- **輸出**：重導向 `/expenses/balance`

---

### 2.6 智慧電費（electricity.py）

#### `POST /electricity/<id>/meter` — 登錄電表
- **輸入**：URL 參數 `id`；表單欄位 `start_reading`, `end_reading`
- **處理**：`MeterReading.create()` → 檢查所有室友是否都已填寫 → 若是則呼叫 `calc_helpers` 計算分攤 → `ElectricitySplit.create()`
- **輸出**：重導向 `/electricity/<id>`
- **錯誤處理**：已登錄過（唯一約束）、度數不合理

---

### 2.7 隱形管家（chore.py）

#### `POST /chores/<id>/complete` — 完成任務
- **輸入**：URL 參數 `id`
- **處理**：`Chore.get_by_id()` → `chore.mark_completed()`
- **輸出**：重導向 `/chores`
- **錯誤處理**：非負責人操作、任務不存在（404）

---

### 2.8 友善黑臉（reminder.py）

#### `POST /reminders/send` — 發送提醒
- **輸入**：表單欄位 `receiver_id`, `category`, `message`
- **處理**：`Reminder.check_cooldown()` → `Reminder.create()` → `Notification.create()`（不含 sender 資訊）
- **輸出**：成功 → 重導向 `/reminders/send`（含成功訊息）；冷卻中 → 回到表單顯示提示
- **錯誤處理**：冷卻時間內重複發送、不能發給自己

#### `GET /reminders/stats` — 統計摘要
- **輸入**：無
- **處理**：`Reminder.get_stats_by_group()` 取得類別統計
- **輸出**：`reminder/stats.html`
- **錯誤處理**：非管理者 → 403 拒絕存取

---

### 2.9 共同物資庫存（inventory.py）

#### `POST /inventory/<id>/stock-in` — 入庫登記
- **輸入**：URL 參數 `id`；表單欄位 `quantity`, `note`, `sync_expense`（是否同步帳本）
- **處理**：`InventoryItem.get_by_id()` → `item.stock_in(qty)` → `InventoryLog.create(action='stock_in')` → 若 `sync_expense` 則同時 `Expense.create()`
- **輸出**：重導向 `/inventory/<id>`
- **錯誤處理**：數量非正整數

#### `POST /inventory/<id>/stock-out` — 出庫登記
- **輸入**：URL 參數 `id`；表單欄位 `quantity`, `note`
- **處理**：`item.stock_out(qty)` → `InventoryLog.create(action='stock_out')` → 若 `item.is_low_stock` 則 `Notification.create()` 通知所有室友
- **輸出**：重導向 `/inventory/<id>`
- **錯誤處理**：數量非正整數

---

## 3. Jinja2 模板清單

所有模板皆繼承 `base.html`（透過 `{% extends "base.html" %}`）。

| 模板路徑 | 繼承 | 說明 |
| :--- | :--- | :--- |
| `templates/base.html` | — | 基礎佈局（導覽列、頁尾、CSS/JS） |
| `templates/auth/login.html` | base.html | 登入表單 |
| `templates/auth/register.html` | base.html | 註冊表單 |
| `templates/dashboard/index.html` | base.html | 首頁儀表板 |
| `templates/group/create.html` | base.html | 建立群組表單 |
| `templates/group/join.html` | base.html | 加入群組表單 |
| `templates/group/settings.html` | base.html | 群組設定頁 |
| `templates/agreement/list.html` | base.html | 公約列表 |
| `templates/agreement/detail.html` | base.html | 公約詳情與版本歷史 |
| `templates/agreement/form.html` | base.html | 新增 / 編輯公約表單 |
| `templates/expense/list.html` | base.html | 帳本列表 |
| `templates/expense/form.html` | base.html | 新增消費表單 |
| `templates/expense/balance.html` | base.html | 餘額總覽 |
| `templates/electricity/list.html` | base.html | 電費帳單列表 |
| `templates/electricity/detail.html` | base.html | 分攤明細 |
| `templates/electricity/form.html` | base.html | 帳單登錄表單 |
| `templates/electricity/meter_form.html` | base.html | 電表度數登錄表單 |
| `templates/chore/list.html` | base.html | 任務列表 |
| `templates/chore/calendar.html` | base.html | 輪值日曆 |
| `templates/chore/form.html` | base.html | 新增 / 編輯任務表單 |
| `templates/reminder/send.html` | base.html | 發送匿名提醒表單 |
| `templates/reminder/inbox.html` | base.html | 提醒收件匣 |
| `templates/reminder/stats.html` | base.html | 統計摘要（管理者） |
| `templates/inventory/list.html` | base.html | 物資清單 |
| `templates/inventory/detail.html` | base.html | 物資詳情（入出庫歷史） |
| `templates/inventory/form.html` | base.html | 新增 / 編輯物資表單 |

---

> 📝 **本文件版本**：v1.0
> 📅 **建立日期**：2026-05-14
> 📄 **對應文件**：docs/PRD.md、docs/ARCHITECTURE.md、docs/DB_DESIGN.md
