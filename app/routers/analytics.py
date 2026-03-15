from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud
from app.database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/material-balances", response_model=List[dict])
async def material_balances(db: AsyncSession = Depends(get_db)):
    """Остатки материалов на складе."""
    return await crud.get_material_balances(db)

@router.get("/accounts-payable", response_model=List[dict])
async def accounts_payable(db: AsyncSession = Depends(get_db)):
    """Кредиторская задолженность перед поставщиками."""
    return await crud.get_accounts_payable(db)

@router.get("/purchase-volume")
async def purchase_volume(
    start_date: str = Query(..., description="Начало периода (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Конец периода (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """Объём закупок за период."""
    return await crud.get_purchase_volume(db, start_date, end_date)

# Дополнительный KPI: количество договоров, средняя сумма и т.д.
@router.get("/contract-stats")
async def contract_stats(
    start_date: str = Query(..., description="Начало периода (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Конец периода (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import func, select
    from app.models import Contract

    # Количество договоров за период
    count_stmt = select(func.count()).where(Contract.date.between(start_date, end_date))
    count = (await db.execute(count_stmt)).scalar() or 0

    # Средняя сумма договоров
    avg_stmt = select(func.avg(Contract.total_amount)).where(
        Contract.date.between(start_date, end_date),
        Contract.total_amount.isnot(None)
    )
    avg = (await db.execute(avg_stmt)).scalar() or 0

    return {
        "period": {"start": start_date, "end": end_date},
        "contracts_count": count,
        "average_amount": float(avg)
    }