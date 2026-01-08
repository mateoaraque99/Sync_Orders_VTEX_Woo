## 2026-01-06

**Objective**
Set up a working VTEX Orders Hook and receive events in a local Flask server.

**What was accomplished**
- Created a local Flask server with `/health` and `/vtex-hook` endpoints.
- Exposed the local server using ngrok.
- Configured a VTEX Orders Hook via API.
- Successfully received VTEX hook validation pings (`hookConfig: "ping"`).
- Verified end-to-end communication: VTEX → ngrok → Flask.
- Understood hook filters and event-based delivery (no polling, no retroactive events).

**Issues encountered**
- 401 Unauthorized due to incorrect VTEX credentials.
- 400 Unable to check address when the ngrok endpoint was not reachable.
- 502 Bad Gateway when Flask was not running while ngrok was active.

**Current status**
- VTEX hook is active and validated.
- Local Flask server correctly receives hook requests.
- Filter temporarily set to `value > 0` for broad testing.

**Next steps**
- Trigger a real order event and capture the full hook payload.
- Fetch full order details from VTEX Orders API using `orderId`.
- Design order mapping strategy for WooCommerce.

## 2026-01-07

**Objective**  
Persist incoming VTEX order events by storing them in a local database and stabilizing the middleware data layer.

**What was accomplished**  
- Created a local SQLite database as the initial persistence layer for the middleware.
- Designed and created an events table to store incoming VTEX hook data.
- Built a dedicated database module, isolated from the Flask webhook logic.
- Connected the VTEX hook endpoint to the database module.
- Confirmed that each incoming VTEX event is automatically inserted into the database upon receipt.
- Validated that events are now traceable and no longer transient in memory.

**Issues encountered**  
- No blocking technical issues.
- Minor iteration while defining table structure and insert logic.

**Current status**  
- SQLite database is live and operational.
- Database module is stable and reusable.
- VTEX hook events are successfully persisted on every request.

**Next steps**  
- Normalize and validate stored payload data.
- Use stored `orderId` values to fetch full order details from the VTEX Orders API.
- Define data mapping rules between VTEX orders and WooCommerce orders.
