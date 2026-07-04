from abc import ABC, abstractmethod


class SmartstoreClient(ABC):
    @abstractmethod
    def upload_product(self, payload: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def collect_orders(self) -> list[dict]:
        raise NotImplementedError
