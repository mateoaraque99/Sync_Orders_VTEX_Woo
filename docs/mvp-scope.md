# MVP Scope

## Goals
- Receive VTEX order notifications and retrieve full order data.
- Create corresponding orders in WooCommerce using VTEX data.
- Sync essential order status updates from WooCommerce back to VTEX.

## Non-goals
- Product/catalog synchronization.
- Inventory synchronization.
- Advanced tax or promotion logic.
- Customer identity unification.
- Admin UI or dashboards.

## Success criteria
- New VTEX orders appear in WooCommerce with core customer, item, payment, and shipping details.
- Basic status changes in WooCommerce reflect back to VTEX without looping.
- Clear logging for order creation attempts and status updates.
