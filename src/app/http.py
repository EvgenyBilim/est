import uvicorn
from fastapi import APIRouter, FastAPI

from src.http.routes.v1.agreements import router as agreement_router
from src.http.routes.v1.developers import router as developers_router
from src.http.routes.v1.homes import router as homes_router
from src.http.routes.v1.locations import router as locations_router
from src.http.routes.v1.metro import router as metro_router
from src.http.routes.v1.payments import router as payments_router
from src.http.routes.v1.seeder import router as seeder_router
from src.infra.components.base import StateManager
from src.settings import Settings


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(
        title="Estate Service",
        lifespan=StateManager(settings=settings).lifespan,
    )
    router = APIRouter(prefix="/http/v1")
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


if __name__ == "__main__":
    main()
