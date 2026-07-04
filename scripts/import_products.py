from app.database import SessionLocal
from app.services.product_importer import import_products


def main() -> None:
    db = SessionLocal()
    try:
        print(import_products(db, 1))
    finally:
        db.close()


if __name__ == "__main__":
    main()
