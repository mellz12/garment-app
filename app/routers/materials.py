from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/materials", tags=["materials"])

@router.get("/", response_model=List[schemas.Material])
async def read_materials(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_materials(db, skip=skip, limit=limit)

@router.get("/{material_id}", response_model=schemas.Material)
async def read_material(material_id: int, db: AsyncSession = Depends(get_db)):
    db_material = await crud.get_material(db, material_id)
    if not db_material:
        raise HTTPException(status_code=404, detail="Material not found")
    return db_material

@router.post("/", response_model=schemas.Material, status_code=201)
async def create_material(material: schemas.MaterialCreate, db: AsyncSession = Depends(get_db)):
    # Проверка на дубликат названия (опционально)
    existing = await crud.get_materials(db)
    if any(m.name == material.name for m in existing):
        raise HTTPException(status_code=400, detail="Material with this name already exists")
    return await crud.create_material(db, material)

@router.put("/{material_id}", response_model=schemas.Material)
async def update_material(material_id: int, material_update: schemas.MaterialUpdate, db: AsyncSession = Depends(get_db)):
    db_material = await crud.update_material(db, material_id, material_update)
    if not db_material:
        raise HTTPException(status_code=404, detail="Material not found")
    return db_material

@router.delete("/{material_id}", status_code=204)
async def delete_material(material_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_material(db, material_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Material not found")