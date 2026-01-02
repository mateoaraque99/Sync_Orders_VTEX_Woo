# WooCommerce Notes

## REST API integration
- Use WooCommerce REST API to create orders with VTEX-derived data.
- Keep API credentials server-side; never expose keys in client code.
- Consider idempotency by checking for existing orders tied to VTEX `orderId` (e.g., via meta fields).

## Order fields to populate
- Customer details and shipping/billing addresses.
- Line items with quantities and prices from VTEX data.
- Shipping rates and payment information available at creation time.
- Custom meta to store VTEX identifiers for traceability.

## Status updates
- Track WooCommerce status changes and push essential updates back to VTEX.
- Prevent loops by storing the origin of updates and skipping mirrored callbacks.
