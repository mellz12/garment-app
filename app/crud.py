from sqlalchemy.ext.asyncio import AsyncSession
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import case, select, update, delete, func
from sqlalchemy.orm import selectinload
from typing import Optional, List
from app import models, schemas
from app.models import Material, WarehouseOperation, WarehouseOperationType

logger = logging.getLogger(__name__)
# ---------- Suppliers (уже есть, оставляем) ----------
async def get_supplier(db: AsyncSession, supplier_id: int) -> Optional[models.Supplier]:
    result = await db.execute(select(models.Supplier).where(models.Supplier.id == supplier_id))
    return result.scalar_one_or_none()

async def get_suppliers(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Supplier]:
    result = await db.execute(select(models.Supplier).offset(skip).limit(limit))
    return result.scalars().all()

async def create_supplier(db: AsyncSession, supplier: schemas.SupplierCreate) -> models.Supplier:
    db_supplier = models.Supplier(**supplier.model_dump())
    db.add(db_supplier)
    await db.commit()
    await db.refresh(db_supplier)
    return db_supplier

async def update_supplier(db: AsyncSession, supplier_id: int, supplier_update: schemas.SupplierUpdate) -> Optional[models.Supplier]:
    await db.execute(
        update(models.Supplier)
        .where(models.Supplier.id == supplier_id)
        .values(**supplier_update.model_dump(exclude_unset=True))
    )
    await db.commit()
    return await get_supplier(db, supplier_id)

async def delete_supplier(db: AsyncSession, supplier_id: int) -> bool:
    result = await db.execute(delete(models.Supplier).where(models.Supplier.id == supplier_id))
    await db.commit()
    return result.rowcount > 0

# ---------- Materials ----------
async def get_material(db: AsyncSession, material_id: int) -> Optional[models.Material]:
    result = await db.execute(select(models.Material).where(models.Material.id == material_id))
    return result.scalar_one_or_none()

async def get_materials(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Material]:
    result = await db.execute(select(models.Material).offset(skip).limit(limit))
    return result.scalars().all()

async def create_material(db: AsyncSession, material: schemas.MaterialCreate) -> models.Material:
    db_material = models.Material(**material.model_dump())
    db.add(db_material)
    await db.commit()
    await db.refresh(db_material)
    return db_material

async def update_material(db: AsyncSession, material_id: int, material_update: schemas.MaterialUpdate) -> Optional[models.Material]:
    await db.execute(
        update(models.Material)
        .where(models.Material.id == material_id)
        .values(**material_update.model_dump(exclude_unset=True))
    )
    await db.commit()
    return await get_material(db, material_id)

async def delete_material(db: AsyncSession, material_id: int) -> bool:
    result = await db.execute(delete(models.Material).where(models.Material.id == material_id))
    await db.commit()
    return result.rowcount > 0

# ---------- SupplierPrices ----------
async def get_supplier_price(db: AsyncSession, price_id: int) -> Optional[models.SupplierPrice]:
    result = await db.execute(select(models.SupplierPrice).where(models.SupplierPrice.id == price_id))
    return result.scalar_one_or_none()

async def get_supplier_prices(db: AsyncSession, supplier_id: Optional[int] = None, material_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[models.SupplierPrice]:
    query = select(models.SupplierPrice)
    if supplier_id:
        query = query.where(models.SupplierPrice.supplier_id == supplier_id)
    if material_id:
        query = query.where(models.SupplierPrice.material_id == material_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def create_supplier_price(db: AsyncSession, price: schemas.SupplierPriceCreate) -> models.SupplierPrice:
    db_price = models.SupplierPrice(**price.model_dump())
    db.add(db_price)
    await db.commit()
    await db.refresh(db_price)
    return db_price

async def update_supplier_price(db: AsyncSession, price_id: int, price_update: schemas.SupplierPriceUpdate) -> Optional[models.SupplierPrice]:
    await db.execute(
        update(models.SupplierPrice)
        .where(models.SupplierPrice.id == price_id)
        .values(**price_update.model_dump(exclude_unset=True))
    )
    await db.commit()
    return await get_supplier_price(db, price_id)

async def delete_supplier_price(db: AsyncSession, price_id: int) -> bool:
    result = await db.execute(delete(models.SupplierPrice).where(models.SupplierPrice.id == price_id))
    await db.commit()
    return result.rowcount > 0

# ---------- Contracts ----------
async def get_contract(db: AsyncSession, contract_id: int) -> Optional[models.Contract]:
    result = await db.execute(
        select(models.Contract)
        .where(models.Contract.id == contract_id)
        .options(selectinload(models.Contract.items).selectinload(models.ContractItem.material))
    )
    return result.scalar_one_or_none()

async def get_contracts(db: AsyncSession, supplier_id: Optional[int] = None, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[models.Contract]:
    query = select(models.Contract)
    if supplier_id:
        query = query.where(models.Contract.supplier_id == supplier_id)
    if status:
        query = query.where(models.Contract.status == status)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def create_contract(db: AsyncSession, contract: schemas.ContractCreate) -> models.Contract:
    # Сначала создаём договор без позиций
    contract_data = contract.model_dump(exclude={"items"})
    db_contract = models.Contract(**contract_data)
    db.add(db_contract)
    await db.flush()  # чтобы получить id договора

    # Добавляем позиции, если они есть
    if contract.items:
        for item in contract.items:
            db_item = models.ContractItem(
                contract_id=db_contract.id,
                material_id=item.material_id,
                quantity=item.quantity,
                price=item.price
            )
            db.add(db_item)
    await db.commit()
    await db.refresh(db_contract)
    return db_contract

async def update_contract(db: AsyncSession, contract_id: int, contract_update: schemas.ContractUpdate) -> Optional[models.Contract]:
    await db.execute(
        update(models.Contract)
        .where(models.Contract.id == contract_id)
        .values(**contract_update.model_dump(exclude_unset=True))
    )
    await db.commit()
    return await get_contract(db, contract_id)

async def delete_contract(db: AsyncSession, contract_id: int) -> bool:
    result = await db.execute(delete(models.Contract).where(models.Contract.id == contract_id))
    await db.commit()
    return result.rowcount > 0

# ---------- Contract Items (дополнительно, но могут управляться через договор) ----------
async def get_contract_item(db: AsyncSession, item_id: int) -> Optional[models.ContractItem]:
    result = await db.execute(select(models.ContractItem).where(models.ContractItem.id == item_id))
    return result.scalar_one_or_none()

async def create_contract_item(db: AsyncSession, item: schemas.ContractItemCreate, contract_id: int) -> models.ContractItem:
    db_item = models.ContractItem(contract_id=contract_id, **item.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def delete_contract_item(db: AsyncSession, item_id: int) -> bool:
    result = await db.execute(delete(models.ContractItem).where(models.ContractItem.id == item_id))
    await db.commit()
    return result.rowcount > 0

# ---------- Warehouse Operations ----------
async def get_warehouse_operation(db: AsyncSession, op_id: int) -> Optional[models.WarehouseOperation]:
    result = await db.execute(select(models.WarehouseOperation).where(models.WarehouseOperation.id == op_id))
    return result.scalar_one_or_none()

async def get_warehouse_operations(db: AsyncSession, material_id: Optional[int] = None, operation_type: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[models.WarehouseOperation]:
    query = select(models.WarehouseOperation)
    if material_id:
        query = query.where(models.WarehouseOperation.material_id == material_id)
    if operation_type:
        query = query.where(models.WarehouseOperation.operation_type == operation_type)
    query = query.offset(skip).limit(limit).order_by(models.WarehouseOperation.operation_date.desc())
    result = await db.execute(query)
    return result.scalars().all()

async def create_warehouse_operation(db: AsyncSession, op: schemas.WarehouseOperationCreate) -> models.WarehouseOperation:
    db_op = models.WarehouseOperation(**op.model_dump())
    db.add(db_op)
    await db.commit()
    await db.refresh(db_op)
    return db_op

async def update_warehouse_operation(db: AsyncSession, op_id: int, op_update: schemas.WarehouseOperationUpdate) -> Optional[models.WarehouseOperation]:
    await db.execute(
        update(models.WarehouseOperation)
        .where(models.WarehouseOperation.id == op_id)
        .values(**op_update.model_dump(exclude_unset=True))
    )
    await db.commit()
    return await get_warehouse_operation(db, op_id)

async def delete_warehouse_operation(db: AsyncSession, op_id: int) -> bool:
    result = await db.execute(delete(models.WarehouseOperation).where(models.WarehouseOperation.id == op_id))
    await db.commit()
    return result.rowcount > 0

# ---------- Payments ----------
async def get_payment(db: AsyncSession, payment_id: int) -> Optional[models.Payment]:
    result = await db.execute(select(models.Payment).where(models.Payment.id == payment_id))
    return result.scalar_one_or_none()

async def get_payments(db: AsyncSession, contract_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[models.Payment]:
    query = select(models.Payment)
    if contract_id:
        query = query.where(models.Payment.contract_id == contract_id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def create_payment(db: AsyncSession, payment: schemas.PaymentCreate) -> models.Payment:
    db_payment = models.Payment(**payment.model_dump())
    db.add(db_payment)
    await db.commit()
    await db.refresh(db_payment)
    return db_payment

async def update_payment(db: AsyncSession, payment_id: int, payment_update: schemas.PaymentUpdate) -> Optional[models.Payment]:
    await db.execute(
        update(models.Payment)
        .where(models.Payment.id == payment_id)
        .values(**payment_update.model_dump(exclude_unset=True))
    )
    await db.commit()
    return await get_payment(db, payment_id)

async def delete_payment(db: AsyncSession, payment_id: int) -> bool:
    result = await db.execute(delete(models.Payment).where(models.Payment.id == payment_id))
    await db.commit()
    return result.rowcount > 0

# ---------- Analytics ----------
async def get_material_balances(db: AsyncSession) -> List[dict]:
    try:
        # Подзапрос для расчёта остатков
        subq = select(
            WarehouseOperation.material_id,
            func.sum(
                case(
                    (WarehouseOperation.operation_type == WarehouseOperationType.INCOME, WarehouseOperation.quantity),
                    else_=-WarehouseOperation.quantity
                )
            ).label("balance")
        ).group_by(WarehouseOperation.material_id).subquery()

        stmt = select(
            Material.id,
            Material.name,
            func.coalesce(subq.c.balance, 0).label("balance")
        ).outerjoin(subq, Material.id == subq.c.material_id)

        result = await db.execute(stmt)
        rows = result.all()
        return [
            {
                "material_id": row.id,
                "name": row.name,
                "balance": float(row.balance)
            }
            for row in rows
        ]
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_material_balances: {e}")
        # Возвращаем пустой список, чтобы клиент не падал
        return []
    except Exception as e:
        logger.error(f"Unexpected error in get_material_balances: {e}")
        return []

async def get_accounts_payable(db: AsyncSession) -> List[dict]:
    """Кредиторская задолженность по поставщикам: supplier_id, name, total_debt."""
    # debt = сумма договоров - сумма оплат
    subq_paid = select(
        models.Payment.contract_id,
        func.sum(models.Payment.amount).label("paid")
    ).group_by(models.Payment.contract_id).subquery()

    stmt = select(
        models.Contract.supplier_id,
        models.Supplier.name,
        func.sum(models.Contract.total_amount - func.coalesce(subq_paid.c.paid, 0)).label("debt")
    ).join(models.Supplier, models.Contract.supplier_id == models.Supplier.id
    ).outerjoin(subq_paid, models.Contract.id == subq_paid.c.contract_id
    ).where(models.Contract.status.in_(["подписан", "утверждён"])
    ).group_by(models.Contract.supplier_id, models.Supplier.name)
    result = await db.execute(stmt)
    rows = result.all()
    return [{"supplier_id": r.supplier_id, "name": r.name, "debt": float(r.debt) if r.debt else 0} for r in rows]

async def get_purchase_volume(db: AsyncSession, start_date: str, end_date: str) -> dict:
    """Объём закупок за период (сумма договоров)."""
    stmt = select(func.sum(models.Contract.total_amount)).where(
        models.Contract.date.between(start_date, end_date),
        models.Contract.status.in_(["подписан", "утверждён"])
    )
    result = await db.execute(stmt)
    total = result.scalar() or 0
    return {"start_date": start_date, "end_date": end_date, "total_amount": float(total)}