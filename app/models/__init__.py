"""
Models 套件初始化
匯出所有 SQLAlchemy Model，方便其他模組 import
"""

from flask_sqlalchemy import SQLAlchemy

# 建立 SQLAlchemy 實例（在 app/__init__.py 中初始化）
db = SQLAlchemy()

# 匯入所有 Model（讓 Flask-Migrate 能偵測到所有資料表）
from app.models.user import User
from app.models.group import Group
from app.models.agreement import Agreement
from app.models.agreement_version import AgreementVersion
from app.models.agreement_approval import AgreementApproval
from app.models.expense import Expense
from app.models.expense_split import ExpenseSplit
from app.models.electricity_bill import ElectricityBill
from app.models.meter_reading import MeterReading
from app.models.electricity_split import ElectricitySplit
from app.models.chore import Chore
from app.models.reminder import Reminder
from app.models.inventory_item import InventoryItem
from app.models.inventory_log import InventoryLog
from app.models.notification import Notification
