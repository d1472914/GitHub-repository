# 流程圖文件：宿舍共好 — 室友公約與噪音管理系統

---

## 1. 使用者流程圖（User Flow）

以下流程圖描述使用者從進入網站到操作各功能的完整路徑。

### 1.1 總覽流程

```mermaid
flowchart LR
    A(["🌐 使用者開啟網站"]) --> B{已登入？}
    B -->|否| C["登入 / 註冊頁"]
    C --> D["輸入帳號密碼"]
    D --> E{驗證成功？}
    E -->|否| C
    E -->|是| F
    B -->|是| F["📊 首頁儀表板"]
    F --> G{選擇功能}
    G -->|公約異動記錄| H["📜 公約模組"]
    G -->|共同開支帳本| I["💰 帳本模組"]
    G -->|友善黑臉| J["😊 提醒模組"]
    G -->|智慧電費| K["⚡ 電費模組"]
    G -->|隱形管家| L["🧹 管家模組"]
    G -->|共同物資庫存| M["📦 物資模組"]
    G -->|群組管理| N["👥 群組模組"]
```

### 1.2 身份驗證流程

```mermaid
flowchart LR
    A(["開啟網站"]) --> B{有帳號？}
    B -->|否| C["註冊頁面"]
    C --> D["填寫 Email / 密碼 / 暱稱"]
    D --> E{資料合法？}
    E -->|否| C
    E -->|是| F["註冊成功"]
    F --> G["登入頁面"]
    B -->|是| G
    G --> H["輸入 Email / 密碼"]
    H --> I{驗證通過？}
    I -->|否| G
    I -->|是| J["進入儀表板"]
    J --> K{有群組？}
    K -->|否| L["建立或加入群組"]
    L --> J
    K -->|是| M["開始使用功能"]
```

### 1.3 公約異動記錄流程

```mermaid
flowchart LR
    A["📜 公約列表頁"] --> B{操作選擇}
    B -->|查看| C["公約詳情頁"]
    C --> D["檢視歷史版本"]
    B -->|新增| E["填寫公約表單"]
    E --> F["選擇分類 / 輸入條文"]
    F --> G["送出公約"]
    G --> H["等待室友同意"]
    H --> I{全部同意？}
    I -->|是| J["公約生效 ✅"]
    I -->|否| K["公約待確認中"]
    B -->|編輯| L["修改公約內容"]
    L --> M["系統記錄差異"]
    M --> H
    B -->|刪除| N["確認刪除？"]
    N -->|是| O["公約已刪除"]
    N -->|否| A
```

### 1.4 共同開支帳本流程

```mermaid
flowchart LR
    A["💰 帳本列表頁"] --> B{操作選擇}
    B -->|查看餘額| C["餘額總覽頁"]
    C --> D["查看應收/應付明細"]
    B -->|新增記帳| E["填寫消費表單"]
    E --> F["輸入項目/金額/付款人"]
    F --> G["選擇分攤對象"]
    G --> H["送出"]
    H --> I["系統自動計算分攤"]
    I --> A
    B -->|結算| J["標記已結清"]
    J --> K["重設餘額"]
    K --> A
    B -->|篩選| L["依日期/類別篩選"]
    L --> A
```

### 1.5 友善黑臉流程

```mermaid
flowchart LR
    A["😊 友善黑臉"] --> B{操作選擇}
    B -->|發送提醒| C["選擇提醒對象"]
    C --> D["選擇範本分類"]
    D --> E{自訂訊息？}
    E -->|是| F["輸入自訂內容"]
    E -->|否| G["使用預設範本"]
    F --> H["送出提醒"]
    G --> H
    H --> I{冷卻檢查}
    I -->|通過| J["提醒已發送 ✅"]
    I -->|未通過| K["請稍後再試 ⏳"]
    B -->|查看收件| L["提醒收件匣"]
    L --> M["查看系統提醒訊息"]
    B -->|統計摘要| N["管理者查看統計"]
```

### 1.6 智慧電費流程

```mermaid
flowchart LR
    A["⚡ 電費列表頁"] --> B{操作選擇}
    B -->|新增帳單| C["輸入總電費/計費期間"]
    C --> D["各室友輸入電表度數"]
    D --> E["系統自動計算分攤"]
    E --> F["顯示分攤明細"]
    B -->|查看歷史| G["歷史帳單列表"]
    G --> H["查看某期分攤明細"]
    B -->|提醒繳費| I["系統通知未繳室友"]
```

### 1.7 隱形管家流程

```mermaid
flowchart LR
    A["🧹 隱形管家"] --> B{操作選擇}
    B -->|建立任務| C["填寫任務表單"]
    C --> D["設定類型/週期/負責人"]
    D --> E["儲存排班"]
    B -->|查看日曆| F["輪值日曆頁"]
    F --> G["查看各室友值班時段"]
    B -->|完成任務| H["標記任務已完成 ✅"]
    B -->|查看任務| I["任務列表頁"]
    I --> J["檢視任務狀態"]
```

### 1.8 共同物資庫存流程

```mermaid
flowchart LR
    A["📦 物資清單頁"] --> B{操作選擇}
    B -->|新增物資| C["填寫品項表單"]
    C --> D["設定名稱/單位/最低庫存"]
    D --> E["儲存物資"]
    B -->|入庫| F["登記採購數量"]
    F --> G{同步帳本？}
    G -->|是| H["金額寫入開支帳本"]
    G -->|否| I["僅更新庫存"]
    B -->|出庫| J["登記消耗數量"]
    J --> K{低於最低庫存？}
    K -->|是| L["系統發出低庫存提醒 ⚠️"]
    K -->|否| A
    B -->|查看詳情| M["入出庫歷史"]
```

---

## 2. 系統序列圖（Sequence Diagram）

以下序列圖描述各核心功能中，資料從使用者操作到寫入資料庫的完整流動過程。

### 2.1 使用者註冊

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Route as Flask Route<br/>(auth.py)
    participant Model as Model<br/>(user.py)
    participant DB as SQLite

    User->>Browser: 填寫註冊表單（Email/密碼/暱稱）
    Browser->>Route: POST /auth/register
    Route->>Route: 驗證 CSRF Token
    Route->>Route: 驗證表單資料
    Route->>Model: 檢查 Email 是否已註冊
    Model->>DB: SELECT * FROM users WHERE email=?
    DB-->>Model: 查詢結果（無重複）
    Route->>Route: 密碼雜湊（Werkzeug）
    Route->>Model: 建立新使用者
    Model->>DB: INSERT INTO users
    DB-->>Model: 寫入成功
    Model-->>Route: 回傳 User 物件
    Route-->>Browser: 重導向至登入頁
    Browser-->>User: 顯示「註冊成功，請登入」
```

### 2.2 新增共同開支

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Route as Flask Route<br/>(expense.py)
    participant Model as Model<br/>(expense.py)
    participant DB as SQLite

    User->>Browser: 填寫消費表單（項目/金額/付款人/分攤對象）
    Browser->>Route: POST /expense/add
    Route->>Route: 驗證登入狀態 & CSRF Token
    Route->>Route: 驗證表單資料
    Route->>Model: 建立消費記錄
    Model->>DB: INSERT INTO expenses
    DB-->>Model: 寫入成功
    Route->>Model: 計算各人分攤金額
    Model->>DB: INSERT INTO expense_splits（每人一筆）
    DB-->>Model: 寫入成功
    Route->>Model: 更新餘額
    Model->>DB: UPDATE balances
    DB-->>Model: 更新成功
    Model-->>Route: 回傳計算結果
    Route-->>Browser: 重導向至帳本列表
    Browser-->>User: 顯示最新帳本記錄
```

### 2.3 發送友善黑臉提醒

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Route as Flask Route<br/>(reminder.py)
    participant Model as Model<br/>(reminder.py)
    participant NotiModel as Model<br/>(notification.py)
    participant DB as SQLite

    User->>Browser: 選擇對象、範本、輸入訊息
    Browser->>Route: POST /reminder/send
    Route->>Route: 驗證登入狀態 & CSRF Token
    Route->>Model: 檢查冷卻機制
    Model->>DB: SELECT 最近1小時對同一對象的提醒
    DB-->>Model: 查詢結果
    alt 冷卻時間內已發送過
        Model-->>Route: 冷卻未結束
        Route-->>Browser: 顯示「請稍後再試」
    else 可以發送
        Model-->>Route: 冷卻檢查通過
        Route->>Model: 建立匿名提醒記錄
        Model->>DB: INSERT INTO reminders
        DB-->>Model: 寫入成功
        Route->>NotiModel: 建立站內通知（不含發送者資訊）
        NotiModel->>DB: INSERT INTO notifications
        DB-->>NotiModel: 寫入成功
        Route-->>Browser: 重導向至發送頁
        Browser-->>User: 顯示「提醒已發送」
    end
```

### 2.4 新增公約與同意機制

```mermaid
sequenceDiagram
    actor User as 使用者（提案者）
    actor Member as 其他室友
    participant Browser as 瀏覽器
    participant Route as Flask Route<br/>(agreement.py)
    participant Model as Model<br/>(agreement.py)
    participant DB as SQLite

    User->>Browser: 填寫公約表單（分類/條文內容）
    Browser->>Route: POST /agreement/add
    Route->>Model: 建立公約（狀態：待確認）
    Model->>DB: INSERT INTO agreements
    DB-->>Model: 寫入成功
    Route->>Model: 建立版本記錄（v1）
    Model->>DB: INSERT INTO agreement_versions
    DB-->>Model: 寫入成功
    Route-->>Browser: 重導向至公約列表
    Browser-->>User: 顯示「等待室友同意」

    Note over Member, DB: 其他室友登入後看到待確認公約

    Member->>Browser: 點擊「同意」
    Browser->>Route: POST /agreement/{id}/approve
    Route->>Model: 記錄同意
    Model->>DB: INSERT INTO agreement_approvals
    DB-->>Model: 寫入成功
    Route->>Model: 檢查是否全部同意
    Model->>DB: SELECT COUNT 已同意人數
    DB-->>Model: 回傳數量
    alt 全部同意
        Model->>DB: UPDATE agreements SET status='生效'
        Route-->>Browser: 顯示「公約已生效 ✅」
    else 尚有人未確認
        Route-->>Browser: 顯示「等待其他室友確認」
    end
```

### 2.5 智慧電費分攤計算

```mermaid
sequenceDiagram
    actor Admin as 管理者
    actor Member as 室友
    participant Browser as 瀏覽器
    participant Route as Flask Route<br/>(electricity.py)
    participant Calc as Utils<br/>(calc_helpers.py)
    participant Model as Model<br/>(electricity.py)
    participant DB as SQLite

    Admin->>Browser: 輸入總電費金額與計費期間
    Browser->>Route: POST /electricity/add
    Route->>Model: 建立電費帳單
    Model->>DB: INSERT INTO electricity_bills
    DB-->>Model: 寫入成功
    Route-->>Browser: 導向電表登錄頁

    Note over Member, DB: 各室友分別輸入電表度數

    Member->>Browser: 輸入起始/結束度數
    Browser->>Route: POST /electricity/{id}/meter
    Route->>Model: 儲存電表度數
    Model->>DB: INSERT INTO meter_readings
    DB-->>Model: 寫入成功

    Note over Route, DB: 所有人都輸入完畢後

    Route->>Calc: 呼叫分攤計算函式
    Calc->>Calc: 個人用電 = 結束 − 起始
    Calc->>Calc: 公共用電 = 總度數 − 個人加總
    Calc->>Calc: 每人應繳 = 個人費用 + 公共均攤
    Calc-->>Route: 回傳計算結果
    Route->>Model: 儲存分攤結果
    Model->>DB: INSERT INTO electricity_splits
    DB-->>Model: 寫入成功
    Route-->>Browser: 顯示分攤明細
```

### 2.6 隱形管家任務完成

```mermaid
sequenceDiagram
    actor User as 值日室友
    participant Browser as 瀏覽器
    participant Route as Flask Route<br/>(chore.py)
    participant Model as Model<br/>(chore.py)
    participant DB as SQLite

    User->>Browser: 點擊「標記完成」
    Browser->>Route: POST /chore/{id}/complete
    Route->>Route: 驗證登入狀態
    Route->>Model: 更新任務狀態
    Model->>DB: UPDATE chores SET status='已完成'
    DB-->>Model: 更新成功
    Route->>Model: 記錄完成時間與完成人
    Model->>DB: UPDATE chores SET completed_at=NOW()
    DB-->>Model: 寫入成功
    Model-->>Route: 回傳更新結果
    Route-->>Browser: 重導向至任務列表
    Browser-->>User: 顯示任務狀態為「已完成 ✅」
```

---

## 3. 功能清單對照表

下表列出系統所有主要功能對應的 URL 路徑與 HTTP 方法：

### 3.1 身份驗證（auth）

| 功能 | URL 路徑 | HTTP 方法 | 說明 |
| :--- | :--- | :---: | :--- |
| 註冊頁面 | `/auth/register` | GET | 顯示註冊表單 |
| 註冊處理 | `/auth/register` | POST | 處理註冊資料 |
| 登入頁面 | `/auth/login` | GET | 顯示登入表單 |
| 登入處理 | `/auth/login` | POST | 驗證帳號密碼 |
| 登出 | `/auth/logout` | GET | 清除登入狀態 |

### 3.2 儀表板（dashboard）

| 功能 | URL 路徑 | HTTP 方法 | 說明 |
| :--- | :--- | :---: | :--- |
| 首頁 | `/dashboard` | GET | 總覽通知、待辦、快捷入口 |

### 3.3 群組管理（group）

| 功能 | URL 路徑 | HTTP 方法 | 說明 |
| :--- | :--- | :---: | :--- |
| 建立群組頁面 | `/group/create` | GET | 顯示建立群組表單 |
| 建立群組處理 | `/group/create` | POST | 建立新群組 |
| 加入群組頁面 | `/group/join` | GET | 顯示加入群組表單 |
| 加入群組處理 | `/group/join` | POST | 以邀請碼加入群組 |
| 群組設定 | `/group/settings` | GET | 群組資訊與成員管理 |
| 更新群組設定 | `/group/settings` | POST | 儲存群組設定變更 |

### 3.4 公約異動記錄（agreement）

| 功能 | URL 路徑 | HTTP 方法 | 說明 |
| :--- | :--- | :---: | :--- |
| 公約列表 | `/agreement` | GET | 顯示所有公約 |
| 新增公約頁面 | `/agreement/add` | GET | 顯示新增表單 |
| 新增公約處理 | `/agreement/add` | POST | 儲存新公約 |
| 公約詳情 | `/agreement/<id>` | GET | 查看條文與歷史版本 |
| 編輯公約頁面 | `/agreement/<id>/edit` | GET | 顯示編輯表單 |
| 編輯公約處理 | `/agreement/<id>/edit` | POST | 儲存修改並記錄差異 |
| 刪除公約 | `/agreement/<id>/delete` | POST | 刪除指定公約 |
| 同意公約 | `/agreement/<id>/approve` | POST | 室友確認同意 |

### 3.5 共同開支帳本（expense）

| 功能 | URL 路徑 | HTTP 方法 | 說明 |
| :--- | :--- | :---: | :--- |
| 帳本列表 | `/expense` | GET | 顯示所有消費記錄 |
| 新增記帳頁面 | `/expense/add` | GET | 顯示記帳表單 |
| 新增記帳處理 | `/expense/add` | POST | 儲存消費並計算分攤 |
| 餘額總覽 | `/expense/balance` | GET | 各人應收/應付金額 |
| 結算 | `/expense/settle` | POST | 標記已結清、重設餘額 |

### 3.6 智慧電費（electricity）

| 功能 | URL 路徑 | HTTP 方法 | 說明 |
| :--- | :--- | :---: | :--- |
| 帳單列表 | `/electricity` | GET | 顯示歷史電費帳單 |
| 新增帳單頁面 | `/electricity/add` | GET | 顯示帳單登錄表單 |
| 新增帳單處理 | `/electricity/add` | POST | 儲存帳單資料 |
| 帳單詳情 | `/electricity/<id>` | GET | 查看分攤明細 |
| 登錄電表頁面 | `/electricity/<id>/meter` | GET | 顯示電表登錄表單 |
| 登錄電表處理 | `/electricity/<id>/meter` | POST | 儲存度數並觸發計算 |

### 3.7 隱形管家（chore）

| 功能 | URL 路徑 | HTTP 方法 | 說明 |
| :--- | :--- | :---: | :--- |
| 任務列表 | `/chore` | GET | 顯示所有任務 |
| 輪值日曆 | `/chore/calendar` | GET | 視覺化顯示排班 |
| 新增任務頁面 | `/chore/add` | GET | 顯示任務表單 |
| 新增任務處理 | `/chore/add` | POST | 儲存任務與排班 |
| 編輯任務頁面 | `/chore/<id>/edit` | GET | 顯示編輯表單 |
| 編輯任務處理 | `/chore/<id>/edit` | POST | 儲存修改 |
| 完成任務 | `/chore/<id>/complete` | POST | 標記任務已完成 |

### 3.8 友善黑臉（reminder）

| 功能 | URL 路徑 | HTTP 方法 | 說明 |
| :--- | :--- | :---: | :--- |
| 發送提醒頁面 | `/reminder/send` | GET | 顯示發送表單 |
| 發送提醒處理 | `/reminder/send` | POST | 建立匿名提醒 |
| 提醒收件匣 | `/reminder/inbox` | GET | 查看收到的提醒 |
| 統計摘要 | `/reminder/stats` | GET | 管理者查看統計資料 |

### 3.9 共同物資庫存（inventory）

| 功能 | URL 路徑 | HTTP 方法 | 說明 |
| :--- | :--- | :---: | :--- |
| 物資清單 | `/inventory` | GET | 顯示所有物資品項 |
| 新增物資頁面 | `/inventory/add` | GET | 顯示新增表單 |
| 新增物資處理 | `/inventory/add` | POST | 儲存新物資品項 |
| 物資詳情 | `/inventory/<id>` | GET | 查看入出庫歷史 |
| 編輯物資頁面 | `/inventory/<id>/edit` | GET | 顯示編輯表單 |
| 編輯物資處理 | `/inventory/<id>/edit` | POST | 儲存修改 |
| 入庫登記 | `/inventory/<id>/stock-in` | POST | 登記採購數量 |
| 出庫登記 | `/inventory/<id>/stock-out` | POST | 登記消耗數量 |

---

> 📝 **本文件版本**：v1.0
> 📅 **建立日期**：2026-05-14
> 📄 **對應文件**：docs/PRD.md、docs/ARCHITECTURE.md
