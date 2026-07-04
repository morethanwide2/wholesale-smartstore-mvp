from abc import ABC, abstractmethod


class SupplierApiClient(ABC):
    @abstractmethod
    def list_products(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def get_product_detail(self, supplier_product_id: str) -> dict:
        raise NotImplementedError
