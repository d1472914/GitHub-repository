<<<<<<< HEAD
"""
Models 套件初始化
匯出所有 sqlite3 Model 模組命名空間，方便其他模組 import
"""

import app.models.user as User
import app.models.group as Group
import app.models.agreement as Agreement
import app.models.agreement_version as AgreementVersion
import app.models.agreement_approval as AgreementApproval
import app.models.expense as Expense
import app.models.expense_split as ExpenseSplit
import app.models.electricity_bill as ElectricityBill
import app.models.meter_reading as MeterReading
import app.models.electricity_split as ElectricitySplit
import app.models.chore as Chore
import app.models.reminder as Reminder
import app.models.inventory_item as InventoryItem
import app.models.inventory_log as InventoryLog
import app.models.notification as Notification

# 為了與舊架構/工廠函式相容，建立一個虛擬的 db 物件
class DummyDB:
    def init_app(self, app):
        pass

db = DummyDB()
=======
# Models package initialization
# 匯出各模組，以 Namespace 形式使用，避免 create/get_all 等 CRUD 函式名稱衝突

from . import user
from . import group
from . import agreement
from . import expense
from . import electricity
from . import chore
from . import reminder
from . import inventory
from . import notification
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
