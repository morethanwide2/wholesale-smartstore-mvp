# 도매몰-판매채널 자동등록 MVP

도매몰 상품 API를 수집해 내부 DB에 저장하고, 상품 마스터 검수 후 스마트스토어 등록용 데이터로 변환하는 MVP입니다.  
이번 단계는 스마트스토어 Mock 등록을 중심으로 만들었고, 지마켓/옥션/11번가/토스쇼핑/쿠팡/롯데온으로 확장할 수 있도록 채널별 상품정보와 API 전송 대기열 구조를 포함합니다.

## 핵심 구조

- 도매몰 원본 상품: `supplier_products`, `supplier_product_options`
- 내 판매상품 마스터: `master_products`, `master_product_options`
- 채널별 상품정보: `channel_product_profiles`
- 채널 등록 결과: `channel_products`, `channel_option_mapping`
- API 호출 기록: `api_logs`
- API 전송 대기열: `api_jobs`
- 채널별 호출 제한: `api_rate_limit_settings`

## 실행 방법

1. 환경변수 파일을 만듭니다.

```powershell
Copy-Item .env.example .env
```

CMD에서는 아래 명령을 사용합니다.

```cmd
copy .env.example .env
```

2. Docker Compose를 실행합니다.

```bash
docker compose up --build
```

3. DB 마이그레이션을 적용합니다.

```bash
docker compose exec backend alembic upgrade head
```

4. 접속 주소

- FastAPI: http://localhost:8000
- Health Check: http://localhost:8000/health
- Streamlit 관리자: http://localhost:8501

## API 키 설정

실제 API 키는 채팅에 올리지 말고 로컬 `.env` 파일에만 입력하세요.

```env
SMARTSTORE_CLIENT_ID=
SMARTSTORE_CLIENT_SECRET=
SMARTSTORE_SELLER_ID=

GMARKET_API_KEY=
AUCTION_API_KEY=
ELEVENSTREET_API_KEY=
TOSS_SHOPPING_API_KEY=
COUPANG_ACCESS_KEY=
COUPANG_SECRET_KEY=
COUPANG_VENDOR_ID=
LOTTEON_API_KEY=
```

현재는 `mock` 모드로 동작합니다. 실제 연동 시 각 채널 클라이언트만 교체하면 내부 상품 마스터와 대기열 구조는 그대로 사용할 수 있습니다.

## 기본 사용 흐름

1. Streamlit에서 `상품 수집` 페이지로 이동합니다.
2. Mock 도매몰 상품을 수집합니다.
3. `상품 마스터` 페이지에서 판매할 상품을 마스터로 생성하고 승인합니다.
4. `상품 마스터` 페이지에서 도매몰 원본, 내 판매정보, 옵션/재고, 이미지/상세/인증정보를 확인하고 수정합니다.
5. `스마트스토어 등록` 페이지에서 등록 전 검증을 실행합니다.
6. 검증 통과 상품은 `전송 대기열 넣기` 또는 `Mock 등록 실행`을 선택합니다.
7. `API 전송대기열` 페이지에서 채널별 호출 제한과 대기 작업을 확인합니다.

## 주요 엔드포인트

- `GET /health`
- `POST /suppliers/{supplier_id}/import-products`
- `GET /supplier-products`
- `POST /master-products/from-supplier/{supplier_product_id}`
- `GET /master-products`
- `GET /master-products/{master_product_id}`
- `PATCH /master-products/{master_product_id}`
- `POST /master-products/{master_product_id}/approve`
- `POST /channels/smartstore/products/{master_product_id}/validate`
- `POST /channels/smartstore/products/{master_product_id}/build-payload`
- `POST /channels/smartstore/products/{master_product_id}/enqueue-upload`
- `POST /channels/smartstore/products/{master_product_id}/upload`
- `GET /channels/product-profiles`
- `GET /api-jobs`
- `GET /settings/api-rate-limits`
- `POST /inventory/sync`
- `POST /orders/collect`
- `GET /purchase-orders`
- `GET /logs/api`

## 테스트

```powershell
$env:PYTHONPATH="backend"; pytest
```

Docker 컨테이너 안에서 실행할 수도 있습니다.

```bash
docker compose exec backend pytest
```

## 다음 개발 단계

- 실제 도매처 API 클라이언트 연결
- 스마트스토어 실제 상품등록/재고수정/주문수집 연결
- 쿠팡, 지마켓/옥션, 11번가, 토스쇼핑, 롯데온 채널 클라이언트 추가
- API 작업 대기열 실행 워커 추가
- 채널별 카테고리/옵션/금지어 검증 강화
- 주문 수집 후 발주대기 및 송장 전송 자동화
