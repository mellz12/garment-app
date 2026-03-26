from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/supplier-prices", tags=["supplier-prices"])

@router.get("/", response_model=List[schemas.SupplierPrice])
async def get_supplier_prices(
    supplier_id: Optional[int] = None,
    material_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_supplier_prices(db, supplier_id, material_id, skip, limit)

@router.post("/", response_model=schemas.SupplierPrice, status_code=201)
async def create_supplier_price(price: schemas.SupplierPriceCreate, db: AsyncSession = Depends(get_db)):
    # Проверка существования поставщика и материала
    supplier = await crud.get_supplier(db, price.supplier_id)
    if not supplier:
        raise HTTPException(status_code=400, detail="Supplier not found")
    material = await crud.get_material(db, price.material_id)
    if not material:
        raise HTTPException(status_code=400, detail="Material not found")
    return await crud.create_supplier_price(db, price)

@router.put("/{price_id}", response_model=schemas.SupplierPrice)
async def update_supplier_price(price_id: int, price_update: schemas.SupplierPriceUpdate, db: AsyncSession = Depends(get_db)):
    db_price = await crud.update_supplier_price(db, price_id, price_update)
    if not db_price:
        raise HTTPException(status_code=404, detail="Price not found")
    return db_price

@router.delete("/{price_id}", status_code=204)
async def delete_supplier_price(price_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_supplier_price(db, price_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Price not found")

@router.delete("/by-supplier/{supplier_id}", status_code=204)
async def delete_all_supplier_prices(supplier_id: int, db: AsyncSession = Depends(get_db)):
    # Удалить все цены для данного поставщика
    prices = await crud.get_supplier_prices(db, supplier_id=supplier_id)
    for p in prices:
        await crud.delete_supplier_price(db, p.id)
    return