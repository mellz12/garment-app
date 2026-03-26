from sqlalchemy import (
    Column, Integer, String, Float, Date, Enum, ForeignKey, Text, DECIMAL, DateTime, func
)
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

class ContractStatus(str, enum.Enum):
    CREATED = "создан"
    APPROVED = "утверждён"
    SIGNED = "подписан"
    CANCELLED = "аннулирован"

class PaymentType(str, enum.Enum):
    PREPAYMENT = "предоплата"
    POSTPAYMENT = "постоплата"
    DEFERRED = "отсрочка платежа"

class WarehouseOperationType(str, enum.Enum):
    INCOME = "приход"
    EXPENSE = "расход"

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    inn = Column(String(12), nullable=False, unique=True)
    bank_name = Column(String(200))
    bik = Column(String(9))
    account_number = Column(String(20))
    director_name = Column(String(100))
    chief_accountant_name = Column(String(100))
    contact_info = Column(Text, nullable=True)

    # связи
    contracts = relationship("Contract", back_populates="supplier")
    supplier_prices = relationship("SupplierPrice", back_populates="supplier")

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    unit = Column(String(20), nullable=False)  # ед. измерения (м, шт, кг)
    description = Column(Text, nullable=True)

    # связи
    supplier_prices = relationship("SupplierPrice", back_populates="material")
    warehouse_operations = relationship("WarehouseOperation", back_populates="material")
    contract_items = relationship("ContractItem", back_populates="material")

class SupplierPrice(Base):
    __tablename__ = "supplier_prices"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    price = Column(DECIMAL(10,2), nullable=False)          # цена за единицу
    delivery_time_days = Column(Integer, nullable=True)    # срок поставки в днях

    supplier = relationship("Supplier", back_populates="supplier_prices")
    material = relationship("Material", back_populates="supplier_prices")

class ContractType(str, enum.Enum):
    ONETIME = "одноразовый"
    LONGTERM = "долгосрочный"

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False)
    contract_number = Column(String(50), nullable=False, unique=True)
    date = Column(Date, nullable=False, server_default=func.current_date())
    status = Column(Enum(ContractStatus), default=ContractStatus.CREATED)
    total_amount = Column(DECIMAL(12,2), nullable=True)
    delivery_terms = Column(Text, nullable=True)
    payment_terms = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    supplier = relationship("Supplier", back_populates="contracts")
    items = relationship("ContractItem", back_populates="contract", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="contract")
    contract_type = Column(Enum(ContractType), default=ContractType.ONETIME)

class ContractItem(Base):
    __tablename__ = "contract_items"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(DECIMAL(10,2), nullable=False)
    price = Column(DECIMAL(10,2), nullable=False)   # цена по договору

    contract = relationship("Contract", back_populates="items")
    material = relationship("Material", back_populates="contract_items")

class WarehouseOperation(Base):
    __tablename__ = "warehouse_operations"

    id = Column(Integer, primary_key=True, index=True)
    operation_type = Column(Enum(WarehouseOperationType), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(DECIMAL(10,2), nullable=False)
    price = Column(DECIMAL(10,2), nullable=False)   # цена на момент операции (можно брать из договора или текущую)
    document_number = Column(String(50), nullable=True)   # номер накладной/акта
    operation_date = Column(DateTime, server_default=func.now())
    contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="SET NULL"), nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)

    material = relationship("Material", back_populates="warehouse_operations")
    contract = relationship("Contract")
    supplier = relationship("Supplier")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False)
    amount = Column(DECIMAL(12,2), nullable=False)
    payment_date = Column(Date, nullable=False)
    payment_type = Column(Enum(PaymentType), default=PaymentType.POSTPAYMENT)
    status = Column(String(20), default="проведён")   # проведён / отменён
    notes = Column(Text, nullable=True)

    contract = relationship("Contract", back_populates="payments")