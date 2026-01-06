import json
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify({"status": "up"}), 200

@app.post("/vtex-hook")
def vtex_hook():
    payload = request.get_json(silent=True)

    print("\n" + "=" * 70)
    print("HOOK RECIBIDO", datetime.utcnow().isoformat() + "Z")
    print("IP:", request.remote_addr)
    print("PATH:", request.path)
    print("Content-Type:", request.headers.get("Content-Type"))
    print("BODY (JSON):")
    print(json.dumps(payload, indent=2, ensure_ascii=False) if payload else "(sin JSON)")
    print("=" * 70 + "\n")

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)