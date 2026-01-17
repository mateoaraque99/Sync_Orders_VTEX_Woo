import os
import requests
from requests.auth import HTTPBasicAuth


class WooClient:
    def __init__(self) -> None:
        base_url = os.getenv("WOO_BASE_URL")
        ck = os.getenv("WOO_CONSUMER_KEY")
        cs = os.getenv("WOO_CONSUMER_SECRET")

        if not base_url or not ck or not cs:
            raise RuntimeError("Missing WOO_BASE_URL / WOO_CONSUMER_KEY / WOO_CONSUMER_SECRET in .env")

        self.base_url = base_url.rstrip("/")
        self.auth = HTTPBasicAuth(ck, cs)

    def create_order(self, payload: dict) -> dict:
        url = f"{self.base_url}/wp-json/wc/v3/orders"
        r = requests.post(url, json=payload, auth=self.auth, timeout=30)
        r.raise_for_status()
        return r.json()
