from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.routers import suppliers, materials, contracts, warehouse, payments, analytics, auto_order, supplier_prices
from app.database import engine
from app.models import Base

app = FastAPI(title="KIS Procurement")

# CORS (если фронтенд будет на другом порту, для разработки можно оставить "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры API (префиксы уже заданы внутри каждого роутера)
app.include_router(suppliers.router, tags=["suppliers"])
app.include_router(materials.router, tags=["materials"])
app.include_router(contracts.router, tags=["contracts"])
app.include_router(warehouse.router, tags=["warehouse"])
app.include_router(payments.router, tags=["payments"])
app.include_router(analytics.router, tags=["analytics"])
app.include_router(auto_order.router)
app.include_router(supplier_prices.router)



@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Раздача статических файлов (HTML, CSS, JS) из папки static
# ВАЖНО: монтируем после роутеров, чтобы API обрабатывалось первым
app.mount("/", StaticFiles(directory="static", html=True), name="static")