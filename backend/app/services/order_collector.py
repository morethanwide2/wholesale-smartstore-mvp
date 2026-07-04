from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ChannelOptionMapping, ChannelProduct, Order, OrderItem
from app.services.api_log_service import create_api_log
from app.services.purchase_order_service import create_purchase_order_for_item
from app.services.smartstore.client import get_smartstore_client
from app.services.smartstore_upload_service import ensure_smartstore_channel


def collect_mock_orders(db: Session) -> dict:
    channel = ensure_smartstore_channel(db)
    client = get_smartstore_client()
    orders = client.collect_orders()

    first_mapping = db.scalar(select(ChannelOptionMapping).limit(1))
    if first_mapping:
        channel_product = db.get(ChannelProduct, first_mapping.channel_product_id)
        orders[0]["items"] = [
            {
                "channel_product_id": channel_product.channel_product_id if channel_product else None,
                "channel_option_id": first_mapping.channel_option_id,
                "quantity": 1,
                "paid_amount": 19900,
            }
        ]

    created_orders = 0
    created_items = 0
    created_purchase_orders = 0

    for payload in orders:
        existing = db.scalar(select(Order).where(Order.channel_order_id == payload["channel_order_id"]))
        if existing:
            continue
        order = Order(
            channel_id=channel.id,
            channel_order_id=payload["channel_order_id"],
            order_status=payload["order_status"],
            payment_status=payload["payment_status"],
            ordered_at=payload["ordered_at"],
            buyer_name=payload.get("buyer_name"),
            receiver_name=payload.get("receiver_name"),
            receiver_phone=payload.get("receiver_phone"),
            receiver_address=payload.get("receiver_address"),
            delivery_message=payload.get("delivery_message"),
            raw_payload_json=payload,
        )
        db.add(order)
        db.flush()
        created_orders += 1

        for item_payload in payload.get("items", []):
            mapping = db.scalar(
                select(ChannelOptionMapping).where(
                    ChannelOptionMapping.channel_option_id == item_payload.get("channel_option_id")
                )
            )
            channel_product = db.scalar(
                select(ChannelProduct).where(ChannelProduct.channel_product_id == item_payload.get("channel_product_id"))
            )
            item = OrderItem(
                order_id=order.id,
                channel_product_id=item_payload.get("channel_product_id"),
                channel_option_id=item_payload.get("channel_option_id"),
                master_product_id=channel_product.master_product_id if channel_product else None,
                master_option_id=mapping.master_option_id if mapping else None,
                product_name=None,
                option_name=None,
                quantity=item_payload.get("quantity", 1),
                paid_amount=item_payload.get("paid_amount", 0),
                mapping_status="matched" if mapping and channel_product else "needs_review",
            )
            db.add(item)
            db.flush()
            created_items += 1
            purchase_order = create_purchase_order_for_item(db, order, item)
            if purchase_order:
                created_purchase_orders += 1

    create_api_log(
        db=db,
        service_name="mock_smartstore",
        endpoint="/orders",
        method="GET",
        request_json={},
        response_json={"orders": created_orders, "items": created_items, "purchase_orders": created_purchase_orders},
        status_code=200,
        success=True,
    )
    db.commit()
    return {"orders": created_orders, "items": created_items, "purchase_orders": created_purchase_orders}
