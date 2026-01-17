from __future__ import annotations

from typing import Any

from .vtex_client import VtexClient
from .woo_client import WooClient
from storage.sqlite import (
    store_event_if_new,
    upsert_order_snapshot,
    get_order_snapshot,
    mark_connected_with_woo,
)


CREATABLE_STATUSES = {"ready-for-handling", "handling-shipping", "invoiced"}
NOT_CREATABLE_STATUSES = {"canceling", "canceled", "cancellation-requested"}


def _cents_to_decimal_str(v: int | None) -> str:
    if not v:
        return "0.00"
    return f"{v / 100:.2f}"


def build_order_snapshot(o: dict) -> dict:
    client = o.get("clientProfileData") or {}

    shipping_data = o.get("shippingData") or {}
    address = shipping_data.get("address") or {}
    logistics = shipping_data.get("logisticsInfo") or []
    logistics0 = logistics[0] if logistics else {}

    totals_list = o.get("totals") or []
    totals = {t.get("id"): t.get("value") for t in totals_list if t.get("id")}

    items_out = []
    for it in o.get("items") or []:
        add = it.get("additionalInfo") or {}
        dim = add.get("dimension") or {}
        items_out.append(
            {
                "item_id": it.get("id"),
                "seller_sku": it.get("sellerSku"),
                "ref_id": it.get("refId"),
                "name": it.get("name"),
                "quantity": it.get("quantity"),
                "selling_price": it.get("sellingPrice"),
                "price": it.get("price"),
                "list_price": it.get("listPrice"),
                "image_url": it.get("imageUrl"),
                "brand_name": add.get("brandName"),
                "weight": dim.get("weight"),
            }
        )

    return {
        "order_id": o.get("orderId"),
        "marketplace_order_id": o.get("marketplaceOrderId"),
        "affiliate_id": o.get("affiliateId"),
        "sales_channel": o.get("salesChannel"),
        "status": o.get("status"),
        "status_description": o.get("statusDescription"),
        "workflow_is_in_error": o.get("workflowIsInError"),
        "is_completed": o.get("isCompleted"),
        "creation_date": o.get("creationDate"),
        "last_change": o.get("lastChange"),
        "value": o.get("value"),
        "totals": totals,
        "customer": {
            "email": client.get("email"),
            "first_name": client.get("firstName"),
            "last_name": client.get("lastName"),
            "document_type": client.get("documentType"),
            "document": client.get("document"),
            "phone": client.get("phone"),
        },
        "shipping": {
            "receiver_name": address.get("receiverName"),
            "street": address.get("street"),
            "number": address.get("number"),
            "complement": address.get("complement"),
            "neighborhood": address.get("neighborhood"),
            "city": address.get("city"),
            "state": address.get("state"),
            "postal_code": address.get("postalCode"),
            "country": address.get("country"),
            "geo_coordinates": address.get("geoCoordinates"),
            "selected_sla": logistics0.get("selectedSla"),
            "delivery_company": logistics0.get("deliveryCompany"),
            "shipping_estimate": logistics0.get("shippingEstimate"),
            "shipping_estimate_date": logistics0.get("shippingEstimateDate"),
            "shipping_price": logistics0.get("price"),
        },
        "items": items_out,
    }


def build_woo_order_payload(snapshot: dict) -> dict:
    customer = snapshot.get("customer") or {}
    shipping = snapshot.get("shipping") or {}
    items = snapshot.get("items") or []
    totals = snapshot.get("totals") or {}

    receiver = (shipping.get("receiver_name") or "").strip()
    receiver_parts = receiver.split() if receiver else []

    first_name = customer.get("first_name") or (receiver_parts[0] if receiver_parts else "")
    last_name = customer.get("last_name") or (" ".join(receiver_parts[1:]) if len(receiver_parts) > 1 else "")

    line_items = []
    for it in items:
        qty = it.get("quantity") or 1
        unit_cents = it.get("selling_price") or it.get("price") or 0
        total_cents = unit_cents * qty

        line_items.append(
            {
                "name": it.get("name") or "Item",
                "quantity": qty,
                "total": _cents_to_decimal_str(total_cents),
            }
        )

    ship_cents = shipping.get("shipping_price") or totals.get("Shipping") or 0
    shipping_lines = []
    if ship_cents:
        shipping_lines.append(
            {
                "method_title": shipping.get("delivery_company") or "Shipping",
                "total": _cents_to_decimal_str(ship_cents),
            }
        )

    billing = {
        "first_name": first_name,
        "last_name": last_name,
        "email": customer.get("email") or "",
        "phone": customer.get("phone") or "",
        "address_1": shipping.get("street") or "",
        "address_2": shipping.get("complement") or "",
        "city": shipping.get("city") or "",
        "state": shipping.get("state") or "",
        "postcode": shipping.get("postal_code") or "",
        "country": shipping.get("country") or "CO",
    }

    return {
        "status": "processing",
        "billing": billing,
        "shipping": {
            "first_name": first_name,
            "last_name": last_name,
            "address_1": shipping.get("street") or "",
            "address_2": shipping.get("complement") or "",
            "city": shipping.get("city") or "",
            "state": shipping.get("state") or "",
            "postcode": shipping.get("postal_code") or "",
            "country": shipping.get("country") or "CO",
        },
        "line_items": line_items,
        "shipping_lines": shipping_lines,
        "meta_data": [
            {"key": "vtex_order_id", "value": snapshot.get("order_id")},
            {"key": "vtex_status", "value": snapshot.get("status")},
        ],
    }


def process_vtex_event(order_id: str, last_change: str) -> dict[str, Any]:
    """
    Entry point usado por app.py

    - Deduplica el evento.
    - Si es nuevo: consulta VTEX, crea snapshot, UPSERT.
    - Si el status está listo y no está conectado: crea orden en Woo y marca conectado.
    """
    inserted, event_id = store_event_if_new(order_id, last_change)

    result: dict[str, Any] = {
        "inserted": inserted,
        "event_id": event_id,
        "order_id": order_id,
        "last_change": last_change,
        "vtex_status": None,
        "woo_should_create": False,
        "woo_created": False,
        "woo_order_id": None,
        "error": None,
    }

    if not inserted:
        return result

    try:
        vtex = VtexClient()
        order = vtex.get_order(order_id)
        status = vtex.extract_status(order)

        result["vtex_status"] = status

        snapshot = build_order_snapshot(order)

        # Guardamos snapshot siempre, incluso si no está listo para Woo
        upsert_order_snapshot(
            order_id=order_id,
            status=status,
            snapshot=snapshot,
            connected_with_woo=False,
            woo_order_id=None,
        )

        # Decisión de negocio
        if status in NOT_CREATABLE_STATUSES:
            return result

        # Si está en estados "creables", intentamos crear en Woo si aún no está conectado
        if status in CREATABLE_STATUSES:
            result["woo_should_create"] = True

            current = get_order_snapshot(order_id)
            if current and current["connected_with_woo"]:
                result["woo_created"] = True
                result["woo_order_id"] = current["woo_order_id"]
                return result

            woo = WooClient()
            woo_payload = build_woo_order_payload(snapshot)
            woo_resp = woo.create_order(woo_payload)

            woo_order_id = str(woo_resp.get("id"))
            if woo_order_id and woo_order_id != "None":
                mark_connected_with_woo(order_id, woo_order_id)
                result["woo_created"] = True
                result["woo_order_id"] = woo_order_id

        return result

    except Exception as e:
        result["error"] = str(e)
        return result
