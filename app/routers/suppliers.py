from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/suppliers", tags=["suppliers"])

@router.get("/", response_model=List[schemas.Supplier])
async def read_suppliers(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    suppliers = await crud.get_suppliers(db, skip=skip, limit=limit)
    return suppliers

@router.get("/{supplier_id}", response_model=schemas.Supplier)
async def read_supplier(supplier_id: int, db: AsyncSession = Depends(get_db)):
    db_supplier = await crud.get_supplier(db, supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return db_supplier

@router.post("/", response_model=schemas.Supplier, status_code=201)
async def create_supplier(supplier: schemas.SupplierCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_supplier(db, supplier)

@router.put("/{supplier_id}", response_model=schemas.Supplier)
async def update_supplier(supplier_id: int, supplier_update: schemas.SupplierUpdate, db: AsyncSession = Depends(get_db)):
    db_supplier = await crud.update_supplier(db, supplier_id, supplier_update)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return db_supplier

@router.delete("/{supplier_id}", status_code=204)
async def delete_supplier(supplier_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_supplier(db, supplier_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Supplier not found")