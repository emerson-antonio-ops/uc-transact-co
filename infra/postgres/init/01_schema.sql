-- =============================================================================
-- TransactCo · operational schema (public)
--
-- This is the brownfield. It is the system that already runs: the store and the
-- analytics live in the same Postgres, and the two workloads fight for the same
-- resources. Four tables, one seam (payments.amount vs orders.total_amount).
--
-- Deliberately absent: foreign keys and check constraints.
--
-- This is not an oversight. The premise of the case is that the data lies in
-- silence: an orphan payment, a negative price, an order pointing at a customer
-- that does not exist. None of those rows can be written into a database that
-- enforces referential integrity, so a constrained schema would make the whole
-- exercise impossible. It is also what high-growth transactional systems
-- actually look like once constraints have been dropped "temporarily" to make a
-- migration land.
--
-- Every table carries two timestamps that mean different things:
--   * the business timestamp (ordered_at, paid_at, signup_date) -- when it
--     happened in the real world;
--   * ingested_at -- when the row reached this database.
-- The gap between the two is what makes late arrival and source staleness
-- detectable at all.
-- =============================================================================

CREATE TABLE public.customers (
    customer_id  BIGINT PRIMARY KEY,
    full_name    TEXT,
    email        TEXT,
    country      TEXT,
    city         TEXT,
    segment      TEXT,
    signup_date  DATE,
    is_active    BOOLEAN,
    created_at   TIMESTAMPTZ,
    updated_at   TIMESTAMPTZ,
    ingested_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE public.products (
    product_id   BIGINT PRIMARY KEY,
    sku          TEXT,
    product_name TEXT,
    category     TEXT,
    price        NUMERIC(12, 2),
    cost         NUMERIC(12, 2),
    is_active    BOOLEAN,
    created_at   TIMESTAMPTZ,
    updated_at   TIMESTAMPTZ,
    ingested_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE public.orders (
    order_id     BIGINT PRIMARY KEY,
    customer_id  BIGINT,
    product_id   BIGINT,
    quantity     INTEGER,
    unit_price   NUMERIC(12, 2),
    discount     NUMERIC(12, 2),
    total_amount NUMERIC(12, 2),
    status       TEXT,
    channel      TEXT,
    ordered_at   TIMESTAMPTZ,
    updated_at   TIMESTAMPTZ,
    ingested_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE public.payments (
    payment_id  BIGINT PRIMARY KEY,
    order_id    BIGINT,
    amount      NUMERIC(12, 2),
    method      TEXT,
    status      TEXT,
    paid_at     TIMESTAMPTZ,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes an OLTP store would realistically have: they serve the storefront,
-- not the analyst. The analytical scans are exactly what has no index here.
CREATE INDEX idx_orders_customer_id ON public.orders (customer_id);
CREATE INDEX idx_orders_ordered_at ON public.orders (ordered_at);
CREATE INDEX idx_orders_status ON public.orders (status);
CREATE INDEX idx_payments_order_id ON public.payments (order_id);
CREATE INDEX idx_payments_paid_at ON public.payments (paid_at);
CREATE INDEX idx_customers_email ON public.customers (email);

COMMENT ON TABLE public.customers IS 'Customer master. Migrated from the legacy store in 2021.';
COMMENT ON TABLE public.products IS 'Product catalog. Prices are current, not historical.';
COMMENT ON TABLE public.orders IS 'One row per order line. Denormalized on purpose.';
COMMENT ON TABLE public.payments IS 'Payment attempts and captures from the PSP webhook.';
