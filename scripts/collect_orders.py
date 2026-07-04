from app.database import SessionLocal
from app.services.order_collector import collect_mock_orders


def main() -> None:
    db = SessionLocal()
    try:
        print(collect_mock_orders(db))
    finally:
        db.close()


if __name__ == "__main__":
    main()
