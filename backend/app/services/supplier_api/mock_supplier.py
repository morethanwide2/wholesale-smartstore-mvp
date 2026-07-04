from app.services.supplier_api.base import SupplierApiClient


MOCK_PRODUCTS: list[dict] = [
    {
        "supplier_product_id": "SUP-10001",
        "raw_product_name": "[무료배송] 데일리 무지 반팔 티셔츠",
        "raw_description": "부드러운 코튼 반팔 티셔츠",
        "raw_category": "패션의류>상의",
        "brand": "MockWear",
        "manufacturer": "Mock Factory",
        "origin": "대한민국",
        "supply_price": 8000,
        "shipping_fee": 0,
        "stock_quantity": 120,
        "is_sold_out": False,
        "is_discontinued": False,
        "main_image_url": "https://example.com/images/tee-main.jpg",
        "detail_image_urls": ["https://example.com/images/tee-detail.jpg"],
        "certification_info": {},
        "options": [
            {"supplier_option_id": "SUP-10001-BLK-M", "option_name": "색상/사이즈", "option_value": "블랙/M", "option_price": 0, "supply_price": 8000, "stock_quantity": 40, "is_sold_out": False, "is_discontinued": False},
            {"supplier_option_id": "SUP-10001-WHT-L", "option_name": "색상/사이즈", "option_value": "화이트/L", "option_price": 0, "supply_price": 8000, "stock_quantity": 80, "is_sold_out": False, "is_discontinued": False},
        ],
    },
    {
        "supplier_product_id": "SUP-10002",
        "raw_product_name": "도매특가 스테인리스 텀블러 500ml",
        "raw_description": "보온 보냉 텀블러",
        "raw_category": "생활용품>주방",
        "brand": "MockLife",
        "manufacturer": "Mock Steel",
        "origin": "중국",
        "supply_price": 9500,
        "shipping_fee": 3000,
        "stock_quantity": 70,
        "is_sold_out": False,
        "is_discontinued": False,
        "main_image_url": "https://example.com/images/tumbler-main.jpg",
        "detail_image_urls": ["https://example.com/images/tumbler-detail.jpg"],
        "certification_info": {},
        "options": [
            {"supplier_option_id": "SUP-10002-SIL", "option_name": "색상", "option_value": "실버", "option_price": 0, "supply_price": 9500, "stock_quantity": 70, "is_sold_out": False, "is_discontinued": False}
        ],
    },
    {
        "supplier_product_id": "SUP-10003",
        "raw_product_name": "프리미엄 욕실 발매트",
        "raw_description": "흡수력이 좋은 발매트",
        "raw_category": "생활용품>욕실",
        "brand": "MockHome",
        "manufacturer": "Mock Textile",
        "origin": "대한민국",
        "supply_price": 6200,
        "shipping_fee": 2500,
        "stock_quantity": 0,
        "is_sold_out": True,
        "is_discontinued": False,
        "main_image_url": "https://example.com/images/mat-main.jpg",
        "detail_image_urls": [],
        "certification_info": {},
        "options": [
            {"supplier_option_id": "SUP-10003-GRY", "option_name": "색상", "option_value": "그레이", "option_price": 0, "supply_price": 6200, "stock_quantity": 0, "is_sold_out": True, "is_discontinued": False}
        ],
    },
    {
        "supplier_product_id": "SUP-10004",
        "raw_product_name": "어린이 안전 인증 물병",
        "raw_description": "KC 인증 완료",
        "raw_category": "출산/육아>외출용품",
        "brand": "MockKids",
        "manufacturer": "Mock Kids Factory",
        "origin": "대한민국",
        "supply_price": 7200,
        "shipping_fee": 3000,
        "stock_quantity": 35,
        "is_sold_out": False,
        "is_discontinued": False,
        "main_image_url": "https://example.com/images/bottle-main.jpg",
        "detail_image_urls": [],
        "certification_info": {"KC": "CB000-TEST"},
        "options": [
            {"supplier_option_id": "SUP-10004-PNK", "option_name": "색상", "option_value": "핑크", "option_price": 0, "supply_price": 7200, "stock_quantity": 15, "is_sold_out": False, "is_discontinued": False},
            {"supplier_option_id": "SUP-10004-BLU", "option_name": "색상", "option_value": "블루", "option_price": 0, "supply_price": 7200, "stock_quantity": 20, "is_sold_out": False, "is_discontinued": False},
        ],
    },
    {
        "supplier_product_id": "SUP-10005",
        "raw_product_name": "옵션 일부 품절 주방 장갑",
        "raw_description": "두꺼운 실리콘 장갑",
        "raw_category": "생활용품>주방",
        "brand": "MockCook",
        "manufacturer": "Mock Silicone",
        "origin": "중국",
        "supply_price": 4300,
        "shipping_fee": 3000,
        "stock_quantity": 20,
        "is_sold_out": False,
        "is_discontinued": False,
        "main_image_url": "https://example.com/images/glove-main.jpg",
        "detail_image_urls": [],
        "certification_info": {},
        "options": [
            {"supplier_option_id": "SUP-10005-RED", "option_name": "색상", "option_value": "레드", "option_price": 0, "supply_price": 4300, "stock_quantity": 0, "is_sold_out": True, "is_discontinued": False},
            {"supplier_option_id": "SUP-10005-GRN", "option_name": "색상", "option_value": "그린", "option_price": 0, "supply_price": 4300, "stock_quantity": 20, "is_sold_out": False, "is_discontinued": False},
        ],
    },
    {
        "supplier_product_id": "SUP-10006",
        "raw_product_name": "단종 예정 미니 선풍기",
        "raw_description": "휴대용 선풍기",
        "raw_category": "디지털/가전>계절가전",
        "brand": "MockAir",
        "manufacturer": "Mock Electronics",
        "origin": "중국",
        "supply_price": 11000,
        "shipping_fee": 3000,
        "stock_quantity": 10,
        "is_sold_out": False,
        "is_discontinued": True,
        "main_image_url": "https://example.com/images/fan-main.jpg",
        "detail_image_urls": [],
        "certification_info": {"KC": "HU000-TEST"},
        "options": [
            {"supplier_option_id": "SUP-10006-WHT", "option_name": "색상", "option_value": "화이트", "option_price": 0, "supply_price": 11000, "stock_quantity": 10, "is_sold_out": False, "is_discontinued": True}
        ],
    },
    {
        "supplier_product_id": "SUP-10007",
        "raw_product_name": "공급가 변경 테스트 상품",
        "raw_description": "가격 변동 감지용 상품",
        "raw_category": "테스트",
        "brand": "MockTest",
        "manufacturer": "Mock",
        "origin": "대한민국",
        "supply_price": 15000,
        "shipping_fee": 3000,
        "stock_quantity": 50,
        "is_sold_out": False,
        "is_discontinued": False,
        "main_image_url": "https://example.com/images/price-main.jpg",
        "detail_image_urls": [],
        "certification_info": {},
        "options": [
            {"supplier_option_id": "SUP-10007-ONE", "option_name": "기본", "option_value": "단일", "option_price": 0, "supply_price": 15000, "stock_quantity": 50, "is_sold_out": False, "is_discontinued": False}
        ],
    },
    {
        "supplier_product_id": "SUP-10008",
        "raw_product_name": "옵션 변경 테스트 양말 세트",
        "raw_description": "옵션 변경 감지용 상품",
        "raw_category": "패션잡화>양말",
        "brand": "MockSocks",
        "manufacturer": "Mock Textile",
        "origin": "대한민국",
        "supply_price": 3900,
        "shipping_fee": 2500,
        "stock_quantity": 100,
        "is_sold_out": False,
        "is_discontinued": False,
        "main_image_url": "https://example.com/images/socks-main.jpg",
        "detail_image_urls": [],
        "certification_info": {},
        "options": [
            {"supplier_option_id": "SUP-10008-M", "option_name": "사이즈", "option_value": "M", "option_price": 0, "supply_price": 3900, "stock_quantity": 100, "is_sold_out": False, "is_discontinued": False}
        ],
    },
    {
        "supplier_product_id": "SUP-10009",
        "raw_product_name": "가품 키워드 검수 필요 가방",
        "raw_description": "금지어 검수 테스트",
        "raw_category": "패션잡화>가방",
        "brand": "MockBag",
        "manufacturer": "Mock",
        "origin": "중국",
        "supply_price": 18000,
        "shipping_fee": 3000,
        "stock_quantity": 12,
        "is_sold_out": False,
        "is_discontinued": False,
        "main_image_url": "https://example.com/images/bag-main.jpg",
        "detail_image_urls": [],
        "certification_info": {},
        "options": [
            {"supplier_option_id": "SUP-10009-BLK", "option_name": "색상", "option_value": "블랙", "option_price": 0, "supply_price": 18000, "stock_quantity": 12, "is_sold_out": False, "is_discontinued": False}
        ],
    },
    {
        "supplier_product_id": "SUP-10010",
        "raw_product_name": "배송비 있는 접이식 수납박스",
        "raw_description": "공간 절약형 수납박스",
        "raw_category": "생활용품>수납",
        "brand": "MockBox",
        "manufacturer": "Mock Plastic",
        "origin": "중국",
        "supply_price": 12500,
        "shipping_fee": 4000,
        "stock_quantity": 44,
        "is_sold_out": False,
        "is_discontinued": False,
        "main_image_url": "https://example.com/images/box-main.jpg",
        "detail_image_urls": [],
        "certification_info": {},
        "options": [
            {"supplier_option_id": "SUP-10010-ONE", "option_name": "기본", "option_value": "단일", "option_price": 0, "supply_price": 12500, "stock_quantity": 44, "is_sold_out": False, "is_discontinued": False}
        ],
    },
]


class MockSupplierApiClient(SupplierApiClient):
    def list_products(self) -> list[dict]:
        return MOCK_PRODUCTS

    def get_product_detail(self, supplier_product_id: str) -> dict:
        for product in MOCK_PRODUCTS:
            if product["supplier_product_id"] == supplier_product_id:
                return product
        raise ValueError(f"Mock product not found: {supplier_product_id}")
