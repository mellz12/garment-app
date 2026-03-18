from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/warehouse", tags=["warehouse"])

@router.get("/operations", response_model=List[schemas.WarehouseOperation])
async def read_operations(
    material_id: Optional[int] = None,
    operation_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_warehouse_operations(db, material_id=material_id, operation_type=operation_type, skip=skip, limit=limit)

@router.get("/operations/{op_id}", response_model=schemas.WarehouseOperation)
async def read_operation(op_id: int, db: AsyncSession = Depends(get_db)):
    op = await crud.get_warehouse_operation(db, op_id)
    if not op:
        raise HTTPException(status_code=404, detail="Operation not found")
    return op

from datetime import datetime

@router.post("/operations", response_model=schemas.WarehouseOperation, status_code=201)
async def create_operation(
    op: schemas.WarehouseOperationCreate,
    db: AsyncSession = Depends(get_db)
):
    # Проверка существования материала
    material = await crud.get_material(db, op.material_id)
    if not material:
        raise HTTPException(status_code=400, detail="Material not found")

    # Если передан contract_id, проверяем его существование
    if op.contract_id:
        contract = await crud.get_contract(db, op.contract_id)
        if not contract:
            raise HTTPException(status_code=400, detail="Contract not found")

    # Генерация номера документа, если не указан
    if not op.document_number:
        now = datetime.now()
        prefix = "ПР" if op.operation_type == "приход" else "РС"
        # Формат: ПР-YYYYMMDD-HHMMSS (например, ПР-20250318-143022)
        doc_number = f"{prefix}-{now.strftime('%Y%m%d-%H%M%S')}"
        # Создаём копию объекта с обновлённым полем (Pydantic v2)
        op = op.model_copy(update={"document_number": doc_number})

    # Создаём операцию через CRUD
    db_op = await crud.create_warehouse_operation(db, op)
    return db_op

@router.put("/operations/{op_id}", response_model=schemas.WarehouseOperation)
async def update_operation(op_id: int, op_update: schemas.WarehouseOperationUpdate, db: AsyncSession = Depends(get_db)):
    op = await crud.update_warehouse_operation(db, op_id, op_update)
    if not op:
        raise HTTPException(status_code=404, detail="Operation not found")
    return op

@router.delete("/operations/{op_id}", status_code=204)
async def delete_operation(op_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_warehouse_operation(db, op_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Operation not found")

# @router.get("/balances", response_model=List[dict])
# async def get_balances(db: AsyncSession = Depends(get_db)):
#     # временная заглушка
#     return [
#         {"material_id": 1, "name": "Тестовый материал", "balance": 100},
#         {"material_id": 2, "name": "Ещё материал", "balance": 50}
#     ]

# Эндпоинт для получения текущих остатков (аналитика, но можно и здесь)
@router.get("/balances", response_model=List[dict])
async def get_balances(db: AsyncSession = Depends(get_db)):
    return await crud.get_material_balances(db)