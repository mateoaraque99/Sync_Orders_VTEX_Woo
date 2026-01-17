import os
import requests


class VtexClient:
    def __init__(self) -> None:
        base_url = os.getenv("VTEX_BASE_URL")
        app_key = os.getenv("VTEX_APP_KEY")
        app_token = os.getenv("VTEX_APP_TOKEN")

        if not base_url or not app_key or not app_token:
            raise RuntimeError("Missing VTEX_BASE_URL / VTEX_APP_KEY / VTEX_APP_TOKEN in .env")

        self.base_url = base_url.rstrip("/")
        self.headers = {
            "X-VTEX-API-AppKey": app_key,
            "X-VTEX-API-AppToken": app_token,
            "Accept": "application/json",
        }

    def get_order(self, order_id: str) -> dict:
        url = f"{self.base_url}/api/oms/pvt/orders/{order_id}"
        r = requests.get(url, headers=self.headers, timeout=20)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def extract_status(order: dict) -> str:
        return (
            order.get("status")
            or order.get("state")
            or order.get("currentState")
            or "unknown"
        )
