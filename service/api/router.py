from api.endpoints import (
    ui_settings
)

api_router = routing.APIRouter()

api_router.include_router(
    ui_settings.ui_settings_router, tags=["ui_settings_routes"]
)