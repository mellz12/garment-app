from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/contracts", tags=["contracts"])

@router.get("/", response_model=List[schemas.Contract])
async def read_contracts(
    supplier_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_contracts(db, supplier_id=supplier_id, status=status, skip=skip, limit=limit)

@router.get("/{contract_id}", response_model=schemas.Contract)
async def read_contract(contract_id: int, db: AsyncSession = Depends(get_db)):
    db_contract = await crud.get_contract(db, contract_id)
    if not db_contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return db_contract

@router.post("/", response_model=schemas.Contract, status_code=201)
async def create_contract(contract: schemas.ContractCreate, db: AsyncSession = Depends(get_db)):
    # Проверить существование поставщика
    supplier = await crud.get_supplier(db, contract.supplier_id)
    if not supplier:
        raise HTTPException(status_code=400, detail="Supplier not found")
    # Доп. проверки уникальности номера договора
    existing = await crud.get_contracts(db)
    if any(c.contract_number == contract.contract_number for c in existing):
        raise HTTPException(status_code=400, detail="Contract number already exists")
    return await crud.create_contract(db, contract)

@router.put("/{contract_id}", response_model=schemas.Contract)
async def update_contract(contract_id: int, contract_update: schemas.ContractUpdate, db: AsyncSession = Depends(get_db)):
    db_contract = await crud.update_contract(db, contract_id, contract_update)
    if not db_contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return db_contract

@router.delete("/{contract_id}", status_code=204)
async def delete_contract(contract_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_contract(db, contract_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Contract not found")

# Эндпоинты для работы с позициями договора (опционально)
@router.post("/{contract_id}/items", response_model=schemas.ContractItem, status_code=201)
async def add_contract_item(contract_id: int, item: schemas.ContractItemCreate, db: AsyncSession = Depends(get_db)):
    # Проверить существование договора
    contract = await crud.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    # Проверить материал
    material = await crud.get_material(db, item.material_id)
    if not material:
        raise HTTPException(status_code=400, detail="Material not found")
    return await crud.create_contract_item(db, item, contract_id)

@router.delete("/items/{item_id}", status_code=204)
async def delete_contract_item(item_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_contract_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Contract item not found")