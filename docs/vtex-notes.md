# VTEX Notes

## Orders Hook
- Configure the Orders Feed hook to point to the middleware webhook endpoint that will ingest events.
- Register or update the hook via `POST`/`PUT https://{accountName}.{environment}.com/api/orders/hook/config` with app key/token auth.
- Include a filter in the payload to scope which events arrive (e.g., `payment-approved`, `ready-for-handling`, or `invoiced`), avoiding unnecessary noise.
- The hook payload includes `orderId` and status transitions (`currentState`, `lastState`)—use `orderId` to retrieve the full order from the Orders API.
- Handle retries and potential duplicate deliveries gracefully; VTEX may redeliver when it does not receive a `200` from the webhook.
- Disable or narrow the hook during testing to prevent unexpected traffic in production accounts.

Reference: VTEX Orders Feed hook docs — https://developers.vtex.com/docs/guides/orders-feed#hook

## Orders API usage
- Use `orderId` from the webhook to fetch full order details via VTEX Orders API.
- Ensure API authentication is server-side and secure.
- Capture relevant fields for WooCommerce mapping: customer info, items, totals, payments, and shipping data.

## Status updates
- When WooCommerce statuses change, send updates back to VTEX using the appropriate Orders API endpoint.
- Maintain a mapping table between WooCommerce and VTEX statuses to prevent mismatches.
