"""
Models 套件初始化
匯出 SQLAlchemy db 物件、模型類別，以及其他 sqlite3 模組的命名空間。
"""

from flask_sqlalchemy import SQLAlchemy

# 初始化 SQLAlchemy db 物件
db = SQLAlchemy()

# 匯入並匯出 SQLAlchemy 核心模型類別 (供應用程式直接使用)
from app.models.user import User
from app.models.group import Group
from app.models.agreement import Agreement
from app.models.agreement_version import AgreementVersion
from app.models.agreement_approval import AgreementApproval

# 匯入並匯出其他 sqlite3 的功能模組 (以首字母大寫的別名匯出，相容於原 routes 設計)
import app.models.chore as Chore
import app.models.reminder as Reminder
import app.models.expense as Expense
import app.models.expense_split as ExpenseSplit
import app.models.electricity as Electricity
import app.models.electricity_bill as ElectricityBill
import app.models.electricity_split as ElectricitySplit
import app.models.meter_reading as MeterReading
import app.models.inventory_item as InventoryItem
import app.models.inventory_log as InventoryLog
import app.models.notification as Notification
