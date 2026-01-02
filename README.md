# VTEX ↔ WooCommerce Order Integration

## Overview
This repository contains the groundwork for a bidirectional order synchronization between VTEX and WooCommerce. WooCommerce will serve as the operational hub where all orders are viewed and managed, while VTEX order events trigger the synchronization workflow.

## MVP scope
- Receive VTEX order events via Orders Hook (webhook).
- Fetch full order data from VTEX Orders API using the provided orderId.
- Create corresponding orders in WooCommerce through the REST API.
- Propagate basic order status updates from WooCommerce back to VTEX.

### Explicitly out of scope for the MVP
- Product or inventory sync
- Customer master data unification
- Advanced tax/promotion logic
- Complete VTEX workflow coverage
- UI/admin dashboards

## Repository structure
- `docs/` — architecture notes, scope, and platform-specific references.
- `middleware/` or `service/` — placeholder for the integration logic (language/framework TBD).
- `wp-plugin/` — placeholder for WordPress/WooCommerce-specific code if required.

## Getting started
This phase focuses on documentation and architecture. Implementation details and setup steps will be added once the technical decisions for the middleware are finalized. In the interim, review `docs/vtex-notes.md` for Orders Feed hook setup (VTEX → middleware) and `docs/woo-notes.md` for WooCommerce REST API considerations.

## Engineering principles
- Favor MVP-first deliverables over completeness.
- Keep logic explicit and documented.
- Avoid infinite update loops between platforms.
- Keep credentials and secrets server-side only.
