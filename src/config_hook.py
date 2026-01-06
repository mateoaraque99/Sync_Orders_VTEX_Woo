import os
from pathlib import Path
import requests
from dotenv import load_dotenv


# Load environment variables from the .env file located at the project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def env(name: str) -> str: 
    """Get an environment variable or exit with a clear error."""
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Missing required variable in .env: {name}")
    return value


# Required VTEX configuration
VTEX_ACCOUNT = env("VTEX_ACCOUNT")
VTEX_ENV = env("VTEX_ENV")
VTEX_APP_KEY = env("VTEX_APP_KEY")
VTEX_APP_TOKEN = env("VTEX_APP_TOKEN")

# Public endpoint that will receive VTEX events (ngrok)
HOOK_URL = env("HOOK_URL")

# VTEX Orders Hook configuration endpoint
VTEX_CONFIG_URL = (
    f"https://{VTEX_ACCOUNT}.{VTEX_ENV}.com.br/api/orders/hook/config"
)

# Hook payload sent to VTEX
PAYLOAD = {
    "filter": {
        "type": "FromOrders",
        "expression": "value > 0",  # Easy condition for testing
        "disableSingleFire": False
    },
    "hook": {
        "url": HOOK_URL,
        "headers": {}
    }
}

# HTTP headers required by VTEX API
HEADERS = {
    "Content-Type": "application/json",
    "X-VTEX-API-AppKey": VTEX_APP_KEY,
    "X-VTEX-API-AppToken": VTEX_APP_TOKEN
}


def main():
    # Send hook configuration to VTEX
    response = requests.post(
        VTEX_CONFIG_URL,
        json=PAYLOAD,
        headers=HEADERS,
        timeout=30
    )

    print("HTTP:", response.status_code)
    print(response.text)

    # Raise an exception for any 4xx or 5xx response
    response.raise_for_status()


if __name__ == "__main__": # Execute the main function when the script is run directly
    main()