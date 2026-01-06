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
