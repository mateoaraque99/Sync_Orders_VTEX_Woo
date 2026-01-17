import json
from datetime import datetime
from flask import Flask, request, jsonify

from storage.sqlite import init_db
from services.order_sync import process_vtex_event

app = Flask(__name__)

init_db()


@app.get("/health")
def health():
    return jsonify({"status": "up"}), 200


@app.post("/vtex-hook")
def vtex_hook():
    payload = request.get_json(silent=True) or {}

    if payload.get("hookConfig") == "ping":
        return jsonify({"status": "ok", "type": "ping"}), 200

    order_id = payload.get("OrderId")
    last_change = payload.get("LastChange")

    if not order_id or not last_change:
        return jsonify({
            "status": "error",
            "message": "Missing OrderId or LastChange in payload"
        }), 400

    out = process_vtex_event(order_id, last_change)

    print("\n" + "=" * 70)
    print("HOOK RECEIVED", datetime.utcnow().isoformat() + "Z")
    print("IP:", request.remote_addr)
    print("PATH:", request.path)
    print("DEDUPED:", "NEW" if out["inserted"] else "DUPLICATE")
    print("EVENT_ID:", out["event_id"])
    print("ORDER_ID:", order_id)
    print("LAST_CHANGE:", last_change)
    print("VTEX_STATUS:", out["vtex_status"])
    print("WOO_SHOULD_CREATE:", out["woo_should_create"])
    print("WOO_CREATED:", out["woo_created"])
    print("WOO_ORDER_ID:", out["woo_order_id"])
    if out["error"]:
        print("ERROR:", out["error"])
    print("BODY (JSON):")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("=" * 70 + "\n")

    return jsonify({
        "status": "ok",
        "new": out["inserted"],
        "event_id": out["event_id"],
        "vtex_status": out["vtex_status"],
        "woo_should_create": out["woo_should_create"],
        "woo_created": out["woo_created"],
        "woo_order_id": out["woo_order_id"],
        "error": out["error"],
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
