import uvicorn
from fastapi import APIRouter, FastAPI

from src.api.routes.v1 import (
    agreement_router,
    payments_router,
    developers_router,
    homes_router,
    locations_router,
    metro_router,
    seeder_router,
)
from src.infrastructure.components.base import StateManager
from src.settings import Settings


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(
        title="Estate Service",
        lifespan=StateManager(settings=settings).lifespan,
    )
    router = APIRouter(prefix="/api/v1")
    router.include_router(agreement_router)
    router.include_router(developers_router)
    router.include_router(payments_router)
    router.include_router(locations_router)
    router.include_router(metro_router)
    router.include_router(homes_router)
    router.include_router(seeder_router)
    app.include_router(router)

    return app


def main():
    settings = Settings()
    app = create_app(settings=settings)
    uvicorn.run(app, host="0.0.0.0", port=settings.port)


if __name__ == '__main__':
    main()
