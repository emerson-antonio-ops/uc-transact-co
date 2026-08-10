# TransactCo Data Guide

This guide describes what the supplied columns are intended to represent. It
does not give away every relationship or business invariant; validating those is
part of the investigation.

The executable source of schema truth is
[`infra/postgres/init/01_schema.sql`](../../infra/postgres/init/01_schema.sql).

## `public.customers`

| Column | Intended meaning |
| --- | --- |
| `customer_id` | Internal customer identifier |
| `full_name` | Display name |
| `email` | Contact email as received from the source |
| `country`, `city` | Customer location attributes |
| `segment` | Commercial customer segment |
| `signup_date` | Business date of registration |
| `is_active` | Current active flag |
| `created_at`, `updated_at` | Source lifecycle timestamps |
| `ingested_at` | Time the row reached this database |

## `public.products`

| Column | Intended meaning |
| --- | --- |
| `product_id` | Internal product identifier |
| `sku` | Commercial stock-keeping identifier |
| `product_name`, `category` | Catalog description |
| `price` | Current selling price in the source catalog |
| `cost` | Current product cost in the source catalog |
| `is_active` | Current catalog availability flag |
| `created_at`, `updated_at` | Source lifecycle timestamps |
| `ingested_at` | Time the row reached this database |

## `public.orders`

| Column | Intended meaning |
| --- | --- |
| `order_id` | Internal order-row identifier |
| `customer_id` | Customer reference supplied by the source |
| `product_id` | Product reference supplied by the source |
| `quantity` | Ordered quantity |
| `unit_price` | Price recorded on the order |
| `discount` | Discount recorded on the order |
| `total_amount` | Total recorded by the order system |
| `status` | Current order status supplied by the source |
| `channel` | Order acquisition channel |
| `ordered_at` | Business time of the order |
| `updated_at` | Last source update time |
| `ingested_at` | Time the row reached this database |

## `public.payments`

| Column | Intended meaning |
| --- | --- |
| `payment_id` | Internal payment-attempt identifier |
| `order_id` | Order reference supplied by the payment source |
| `amount` | Payment amount reported by the source |
| `method` | Payment method |
| `status` | Payment status |
| `paid_at` | Business time associated with the payment event |
| `ingested_at` | Time the row reached this database |

## Time vocabulary

- **Business time** describes when something happened in the domain, such as
  `ordered_at` or `paid_at`.
- **Source lifecycle time** describes when a record was created or updated in an
  operational system.
- **Ingestion time** describes when the row reached the database being inspected.

These timestamps answer different questions and must not be silently substituted
for one another.

## Investigation questions

- Which references behave like real relationships in the current data?
- Which statuses appear, and how frequently?
- Which timestamps are relevant to the CFO's question?
- Which numerical fields reconcile, and under what conditions?
- Which statements are supported by schema alone?
- Which statements require queries or business ownership?
