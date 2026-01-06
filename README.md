# Sync Orders VTEX → WooCommerce

Backend integration to synchronize orders from VTEX into WooCommerce in a secure, controlled, and traceable way.

This project works as a middleware that receives order events from VTEX via Hooks and creates or updates corresponding orders in WooCommerce using its REST API.

VTEX is treated as the source of truth.  
WooCommerce acts as the operational and accounting layer.

---

## Purpose

Many operations use VTEX as their main commerce platform while relying on WooCommerce for invoicing, accounting, or internal processes.

This integration exists to:

- Centralize VTEX orders inside WooCommerce
- Remove manual order handling
- Enable downstream processes such as invoicing or ERP sync
- Ensure consistency between platforms
- Provide a reliable and auditable order flow

This is not a one-off script. It is a maintainable integration service.

---

## High-level Architecture

1. VTEX emits order events using Hooks.
2. The middleware receives the event through an HTTP endpoint.
3. The payload and headers are validated.
4. Order data is transformed into WooCommerce format.
5. The order is created or updated in WooCommerce via REST API.
6. The event is stored to prevent duplicate processing.

The service is built in Python and exposed through a Flask server.

---

## Project Structure

The project follows a clear and modular structure to separate responsibilities and keep the integration maintainable as it grows.

```text
.
├─ docs/
│  └─ progress-log.md        # Development log and daily updates
├─ src/
│  ├─ __init__.py            # Marks src as a Python package
│  ├─ app.py                 # Flask application entry point
│  ├─ config.py              # Environment variables and configuration loading
│  ├─ routes/
│  │  └─ vtex_hooks.py       # VTEX webhook endpoints
│  ├─ services/
│  │  ├─ vtex_client.py      # VTEX API client
│  │  ├─ woo_client.py       # WooCommerce API client
│  │  └─ order_sync.py       # Order synchronization logic
│  ├─ storage/
│  │  └─ sqlite.py           # Local persistence and deduplication
│  └─ utils/
│     └─ logger.py           # Logging utilities
├─ .env.example              # Environment variable template
├─ .gitignore
├─ README.md
└─ requirements.txt
