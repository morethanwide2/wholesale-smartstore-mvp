from app.config import get_settings
from app.services.smartstore.base import SmartstoreClient
from app.services.smartstore.mock_client import MockSmartstoreClient


def get_smartstore_client() -> SmartstoreClient:
    settings = get_settings()
    if settings.smartstore_api_mode == "mock":
        return MockSmartstoreClient()
    raise NotImplementedError(f"Unsupported smartstore mode: {settings.smartstore_api_mode}")
