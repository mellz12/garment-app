from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/payments", tags=["payments"])

@router.get("/", response_model=List[schemas.Payment])
async def read_payments(
    contract_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_payments(db, contract_id=contract_id, skip=skip, limit=limit)

@router.get("/{payment_id}", response_model=schemas.Payment)
async def read_payment(payment_id: int, db: AsyncSession = Depends(get_db)):
    payment = await crud.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.post("/", response_model=schemas.Payment, status_code=201)
async def create_payment(payment: schemas.PaymentCreate, db: AsyncSession = Depends(get_db)):
    # Проверить договор
    contract = await crud.get_contract(db, payment.contract_id)
    if not contract:
        raise HTTPException(status_code=400, detail="Contract not found")
    return await crud.create_payment(db, payment)

@router.put("/{payment_id}", response_model=schemas.Payment)
async def update_payment(payment_id: int, payment_update: schemas.PaymentUpdate, db: AsyncSession = Depends(get_db)):
    payment = await crud.update_payment(db, payment_id, payment_update)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.delete("/{payment_id}", status_code=204)
async def delete_payment(payment_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_payment(db, payment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Payment not found")