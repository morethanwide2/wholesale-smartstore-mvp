from app.database import SessionLocal
from app.services.inventory_sync import sync_inventory


def main() -> None:
    db = SessionLocal()
    try:
        print(sync_inventory(db))
    finally:
        db.close()


if __name__ == "__main__":
    main()
