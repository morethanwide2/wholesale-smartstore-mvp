from app.config import get_settings
from app.services.supplier_api.base import SupplierApiClient
from app.services.supplier_api.mock_supplier import MockSupplierApiClient


def get_supplier_client() -> SupplierApiClient:
    settings = get_settings()
    if settings.supplier_api_type == "mock":
        return MockSupplierApiClient()
    raise NotImplementedError(f"Unsupported supplier API type: {settings.supplier_api_type}")
