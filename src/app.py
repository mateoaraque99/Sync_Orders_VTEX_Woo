import json
from datetime import datetime
from flask import Flask, request, jsonify
from storage.sqlite import init_db, store_event_if_new

app = Flask(__name__)

# Initialize DB tables once on startup (creates DB file + table if missing)
init_db()


@app.get("/health")
def health():
    return jsonify({"status": "up"}), 200


@app.post("/vtex-hook")
def vtex_hook():
    payload = request.get_json(silent=True) or {}

    # Extract only what we need from the VTEX event payload
    order_id = payload.get("OrderId")
    last_change = payload.get("LastChange")

    # Validate required fields
    if not order_id or not last_change:
        return jsonify({
            "status": "error",
            "message": "Missing OrderId or LastChange in payload"
        }), 400

    # Store event only if it's new (deduplication)
    inserted, event_id = store_event_if_new(order_id, last_change)

    print("\n" + "=" * 70)
    print("HOOK RECEIVED", datetime.utcnow().isoformat() + "Z")
    print("IP:", request.remote_addr)
    print("PATH:", request.path)
    print("DEDUPED:", "NEW" if inserted else "DUPLICATE")
    print("EVENT_ID:", event_id)
    print("ORDER_ID:", order_id)
    print("LAST_CHANGE:", last_change)
    print("BODY (JSON):")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("=" * 70 + "\n")

    # Always return 200 to prevent VTEX retry storms
    return jsonify({
        "status": "ok",
        "new": inserted,
        "event_id": event_id
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
