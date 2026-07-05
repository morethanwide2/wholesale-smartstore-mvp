# 도매몰 스마트스토어 MVP

도매몰 상품 API에서 상품을 수집하고, 내부 상품 마스터에서 상품명/가격/옵션/재고/이미지/상세페이지/인증정보를 검수한 뒤 스마트스토어 Mock 등록과 API 전송 대기열까지 확인하는 MVP입니다.

## 주요 기능

- Mock 도매몰 상품 수집
- 도매몰 원본 상품/옵션 저장
- 판매상품 마스터 생성
- 상품명 정제와 판매가 계산
- 대표이미지, 상세이미지, 상세설명, 인증정보, 상품정보고시 수정
- 브랜드, 제조사, 원산지, 검색태그 관리
- 마스터 옵션명, 옵션값, 판매가, 재고, 상태 수정
- 스마트스토어 등록 전 검증
- 채널별 등록정보 관리
- 스마트스토어 Mock 등록
- API 전송 대기열과 호출 제한 구조
- 주문 Mock 수집과 발주대기 생성
- API 로그와 에러 확인

## 실행 방법

프로젝트 폴더로 이동합니다.

```cmd
cd C:\Users\SWIM\Documents\github\wholesale-smartstore-mvp
```

환경변수 파일을 만듭니다.

```cmd
copy .env.example .env
```

Docker Desktop을 실행한 뒤 전체 서비스를 올립니다.

```cmd
docker compose up --build
```

다른 CMD 창에서 DB 마이그레이션을 적용합니다.

```cmd
docker compose exec backend alembic upgrade head
```

접속 주소:

- FastAPI: http://localhost:8000
- Health Check: http://localhost:8000/health
- Streamlit 관리자: http://localhost:8501

## 기본 사용 흐름

1. Streamlit에서 `상품 수집` 메뉴를 엽니다.
2. `Mock 도매몰 상품 수집`을 실행합니다.
3. `상품 마스터` 메뉴에서 수집 상품을 판매상품 마스터로 생성합니다.
4. 상품 마스터에서 도매몰 원본, 판매정보, 옵션/재고, 이미지/상세/인증정보를 확인하고 수정합니다.
5. `등록 전 검증` 탭에서 스마트스토어 검증을 실행합니다.
6. 검증 통과 후 `스마트스토어 등록` 메뉴에서 JSON 미리보기, 전송대기열 등록, Mock 등록을 실행합니다.
7. `API 전송대기열` 메뉴에서 대기 작업, 실패 작업, 호출 제한을 확인합니다.

## 상품 마스터 검수 기준

상품 마스터는 도매몰 원본을 판매채널에 바로 보내지 않기 위한 중간 검수 단계입니다.

확인해야 하는 항목:

- 판매 상품명
- 카테고리/채널 매핑 코드
- 판매가와 배송비
- 브랜드, 제조사, 원산지
- 대표이미지와 상세이미지
- 상세설명 또는 상세페이지 HTML
- 인증정보
- 상품정보고시와 채널 필수속성
- 옵션명, 옵션값, 옵션별 판매가, 재고, 상태
- 금지어 또는 등록 오류 가능 문구

## 주요 API

- `GET /health`
- `POST /suppliers/{supplier_id}/import-products`
- `GET /supplier-products`
- `GET /supplier-products/{supplier_product_id}`
- `POST /master-products/from-supplier/{supplier_product_id}`
- `GET /master-products`
- `GET /master-products/{master_product_id}`
- `PATCH /master-products/{master_product_id}`
- `PATCH /master-product-options/{master_option_id}`
- `POST /master-products/{master_product_id}/approve`
- `POST /channels/smartstore/products/{master_product_id}/validate`
- `POST /channels/smartstore/products/{master_product_id}/build-payload`
- `POST /channels/smartstore/products/{master_product_id}/enqueue-upload`
- `POST /channels/smartstore/products/{master_product_id}/upload`
- `GET /channels/product-profiles`
- `GET /api-jobs`
- `POST /api-jobs/run-pending`
- `GET /settings/api-rate-limits`
- `POST /inventory/sync`
- `POST /orders/collect`
- `GET /purchase-orders`
- `GET /logs/api`

## 테스트

Docker 컨테이너 안에서 실행합니다.

```cmd
docker compose exec backend pytest
```

## API 키 설정

실제 API 키는 `.env`에만 입력합니다. `.env`는 GitHub에 올리지 않습니다.

현재는 Mock 모드로 동작합니다. 실제 연동 단계에서는 도매처 API 클라이언트와 각 채널 API 클라이언트만 교체하는 방향으로 확장합니다.
