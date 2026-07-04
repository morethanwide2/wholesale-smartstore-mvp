from app.database import SessionLocal
from app.services.product_importer import ensure_mock_supplier
from app.services.smartstore_upload_service import ensure_smartstore_channel


def main() -> None:
    db = SessionLocal()
    try:
        ensure_mock_supplier(db, 1)
        ensure_smartstore_channel(db)
        db.commit()
        print("seed data created")
    finally:
        db.close()


if __name__ == "__main__":
    main()
