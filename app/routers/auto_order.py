from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app import crud, schemas
from app.database import get_db
from app.models import ContractStatus, ContractType
from datetime import datetime

router = APIRouter(prefix="/auto-order", tags=["auto-order"])

@router.post("/check-and-create")
async def auto_order(db: AsyncSession = Depends(get_db)):
    # Пороги
    VERY_LOW = 10
    LOW = 50
    TARGET = 200  # до какого уровня пополнять

    # Получаем остатки
    balances = await crud.get_material_balances(db)
    created_contracts = []

    for bal in balances:
        material_id = bal["material_id"]
        balance = bal["balance"]
        if balance < LOW:
            # нужно заказать
            # Найти лучшего поставщика для материала
            best_price = await crud.get_best_supplier_price(db, material_id)
            if not best_price:
                continue  # нет поставщика
            # Количество к заказу: до TARGET
            need = TARGET - balance
            if need <= 0:
                continue
            # Создаем договор
            contract_data = schemas.ContractCreate(
                supplier_id=best_price.supplier_id,
                contract_number=None,  # автогенерация
                date=datetime.now().date(),
                status=ContractStatus.CREATED,
                total_amount=need * best_price.price,
                contract_type=ContractType.ONETIME,
                items=[
                    schemas.ContractItemCreate(
                        material_id=material_id,
                        quantity=need,
                        price=best_price.price
                    )
                ]
            )
            try:
                contract = await crud.create_contract(db, contract_data)
                created_contracts.append({
                    "contract_id": contract.id,
                    "contract_number": contract.contract_number,
                    "material_id": material_id,
                    "material_name": bal["name"],
                    "quantity": need,
                    "supplier_id": best_price.supplier_id
                })
            except Exception as e:
                # Логируем ошибку
                continue

    return {"created_contracts": created_contracts}