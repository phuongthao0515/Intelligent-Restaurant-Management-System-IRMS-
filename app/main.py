from fastapi import FastAPI

from app.modules.kds.router import router as kds_router
from app.modules.kds.websocket import router as kds_ws_router
from app.modules.ordering.router import router as ordering_router


app = FastAPI(
    title="IRMS Backend Skeleton",
    version="0.1.0",
    description="Skeleton backend for Ordering and KDS modules.",
)

app.include_router(ordering_router, prefix="/api/v1")
app.include_router(kds_router, prefix="/api/v1")
app.include_router(kds_ws_router)


@app.get("/healthz", tags=["system"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
