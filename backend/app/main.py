from fastapi import FastAPI

from app.routers import api_jobs, channels, logs, orders, products, purchase_orders, suppliers

app = FastAPI(title="Wholesale Smartstore MVP", version="0.1.0")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(suppliers.router)
app.include_router(products.router)
app.include_router(channels.router)
app.include_router(orders.router)
app.include_router(purchase_orders.router)
app.include_router(logs.router)
app.include_router(api_jobs.router)
