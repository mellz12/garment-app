from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import suppliers, materials, contracts, warehouse, payments, analytics
from app.database import engine
from app.models import Base

app = FastAPI(title="KIS Procurement (Швейное производство)")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(suppliers.router)
app.include_router(materials.router)
app.include_router(contracts.router)
app.include_router(warehouse.router)
app.include_router(payments.router)
app.include_router(analytics.router)

@app.on_event("startup")
async def startup():
    # Создание таблиц (для разработки)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "KIS Procurement API работает. Документация: /docs"}