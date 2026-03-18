from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from app.models import ContractStatus, PaymentType, WarehouseOperationType

# ---------- Supplier ----------
class SupplierBase(BaseModel):
    name: str
    inn: str
    bank_name: Optional[str] = None
    bik: Optional[str] = None
    account_number: Optional[str] = None
    director_name: Optional[str] = None
    chief_accountant_name: Optional[str] = None
    contact_info: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(SupplierBase):
    pass

class Supplier(SupplierBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ---------- Material ----------
class MaterialBase(BaseModel):
    name: str
    unit: str
    description: Optional[str] = None

class MaterialCreate(MaterialBase):
    pass

class Material(MaterialBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    unit: Optional[str] = None
    description: Optional[str] = None

# ---------- SupplierPrice ----------
class SupplierPriceBase(BaseModel):
    supplier_id: int
    material_id: int
    price: Decimal
    delivery_time_days: Optional[int] = None

class SupplierPriceCreate(SupplierPriceBase):
    pass

class SupplierPrice(SupplierPriceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class SupplierPriceUpdate(BaseModel):
    price: Optional[Decimal] = None
    delivery_time_days: Optional[int] = None

# ---------- Contract ----------
class ContractBase(BaseModel):
    supplier_id: int
    contract_number: str
    date: date
    status: ContractStatus = ContractStatus.CREATED
    total_amount: Optional[Decimal] = None
    delivery_terms: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None

class ContractCreate(ContractBase):
    pass

class ContractUpdate(BaseModel):
    status: Optional[ContractStatus] = None
    total_amount: Optional[Decimal] = None
    delivery_terms: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None

class Contract(ContractBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ---------- ContractItem ----------
class ContractItemBase(BaseModel):
    material_id: int
    quantity: Decimal
    price: Decimal

class ContractItemCreate(ContractItemBase):
    pass

class ContractItem(ContractItemBase):
    id: int
    contract_id: int
    model_config = ConfigDict(from_attributes=True)

class ContractItemCreate(BaseModel):
    material_id: int
    quantity: Decimal
    price: Decimal

class ContractCreate(ContractBase):
    contract_number: Optional[str] = None
    items: List[ContractItemCreate] = []

# ---------- WarehouseOperation ----------
class WarehouseOperationBase(BaseModel):
    operation_type: WarehouseOperationType
    material_id: int
    quantity: Decimal
    price: Decimal
    document_number: Optional[str] = None
    operation_date: Optional[datetime] = None
    contract_id: Optional[int] = None
    supplier_id: Optional[int] = None
    notes: Optional[str] = None

class WarehouseOperationCreate(WarehouseOperationBase):
    pass

class WarehouseOperation(WarehouseOperationBase):
    id: int
    operation_date: datetime
    model_config = ConfigDict(from_attributes=True)

class WarehouseOperationUpdate(BaseModel):
    quantity: Optional[Decimal] = None
    price: Optional[Decimal] = None
    document_number: Optional[str] = None
    notes: Optional[str] = None

# ---------- Payment ----------
class PaymentBase(BaseModel):
    contract_id: int
    amount: Decimal
    payment_date: date
    payment_type: PaymentType = PaymentType.POSTPAYMENT
    status: str = "проведён"
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class Payment(PaymentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class PaymentUpdate(BaseModel):
    amount: Optional[Decimal] = None
    payment_date: Optional[date] = None
    payment_type: Optional[PaymentType] = None
    status: Optional[str] = None
    notes: Optional[str] = None