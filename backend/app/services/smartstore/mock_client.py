from app.services.smartstore.base import SmartstoreClient


class MockSmartstoreClient(SmartstoreClient):
    def upload_product(self, payload: dict) -> dict:
        product_code = abs(hash(payload["originProduct"]["name"])) % 90000 + 10000
        return {
            "success": True,
            "channel_product_id": f"SMARTSTORE-TEST-{product_code}",
            "option_mappings": [
                {
                    "internal_option_code": option["internalOptionCode"],
                    "channel_option_id": f"CH-{option['internalOptionCode']}",
                    "channel_sku_code": f"SKU-{option['internalOptionCode']}",
                }
                for option in payload.get("options", [])
            ],
        }

    def collect_orders(self) -> list[dict]:
        return [
            {
                "channel_order_id": "ORDER-TEST-10001",
                "ordered_at": "2026-07-04T10:00:00",
                "order_status": "paid",
                "payment_status": "paid",
                "buyer_name": "홍길동",
                "receiver_name": "홍길동",
                "receiver_phone": "010-0000-0000",
                "receiver_address": "서울특별시 테스트구 테스트로 1",
                "delivery_message": "문 앞에 놓아주세요",
                "items": [],
            }
        ]
