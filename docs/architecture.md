# Architecture Overview

## Event-driven flow
1. **VTEX → Webhook:** VTEX Orders Hook sends order events (e.g., creation or status changes) to a middleware endpoint.
2. **Data fetch:** Middleware retrieves full order details from the VTEX Orders API using the received `orderId`.
3. **WooCommerce creation:** Middleware creates the order in WooCommerce via the REST API, mapping VTEX order data to Woo order schema.
4. **Status sync back:** Basic status updates in WooCommerce are pushed back to VTEX to keep both platforms aligned.

## Components
- **Middleware/service:** Hosts webhook endpoints, orchestrates VTEX and WooCommerce API calls, and enforces idempotency and loop prevention.
- **WooCommerce (WordPress):** Serves as the operational hub for order management.
- **VTEX:** Origin of order events and recipient of status updates.

## Key considerations
- **Idempotency:** Ensure repeated webhook deliveries or retries do not create duplicate WooCommerce orders.
- **Loop prevention:** Tag or track origin of updates to avoid infinite status update cycles between platforms.
- **Security:** Keep API keys secret and server-side; never expose in client code.
- **Logging/observability:** Log incoming events, outbound API requests, and error states for troubleshooting.
- **Error handling:** Design for retries when upstream APIs are temporarily unavailable.

## Next steps
- Choose language/runtime for the middleware.
- Define payload contracts for VTEX webhook intake and WooCommerce order creation.
- Establish mapping rules for statuses, payments, and shipping information.
