"""The 14 injectable defects and the sealed answer key they write.

Each defect corrupts public.* the way a real incident would and records in
_control exactly what it did: which defect, which severity, which window, and
which primary keys. The student's detector never sees this. In the Incident Exercise it is the
only thing their detector is scored against.

Three of these are not simple corruptions and carry most of the teaching weight:

  ambiguous_anomaly     A real marketing campaign. It looks exactly like a
                        volume incident and is not one. is_true_incident is
                        False, so a detector that flags it loses precision.
                        This is what separates "found the incident" from
                        "flagged everything that looked odd".

  recurring_incident    The same corruption every night for five nights. A
                        detector that only compares against yesterday sees
                        nothing wrong, because yesterday was broken too.

  multi_failure_cascade One bad deploy, three symptoms in three tables. The
                        children carry root_cause_incident_id back to the root,
                        so the scorer can ask whether the detector reported one
                        incident or three unrelated ones.

Ordering matters when injecting several at once. See SCENARIOS at the bottom.
"""

from __future__ import annotations

import random
import zlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable

import psycopg

from .config import Settings
from .db import admin_connection, column_exists, execute, fetch_all, fetch_column, fetch_one

GHOST_ID_OFFSET = 500_000
ID_BLOCK = 1_000_000

# slow_source empties the last 36 hours of payments. Any other defect whose
# answer key names a payment -- or an order that must still have one -- keeps
# clear of that window, otherwise slow_source deletes rows the student is being
# scored on and row recall is capped below 100% through no fault of theirs.
STALL_SAFE_WINDOW = "2 days"


@dataclass
class Incident:
    defect_type: str
    severity: str
    target_table: str
    target_column: str | None
    detection_hint: str
    rows: list[tuple[str, str]] = field(default_factory=list)
    business_window_start: datetime | None = None
    business_window_end: datetime | None = None
    is_true_incident: bool = True
    root_cause_defect: str | None = None
    notes: str | None = None


@dataclass
class InjectionContext:
    conn: psycopg.Connection
    rng: random.Random
    settings: Settings

    def fetch_column(self, sql: str, params=None) -> list:
        return fetch_column(self.conn, sql, params)

    def fetch_all(self, sql: str, params=None) -> list[tuple]:
        return fetch_all(self.conn, sql, params)

    def fetch_scalar(self, sql: str, params=None):
        row = fetch_one(self.conn, sql, params)
        return row[0] if row else None

    def execute(self, sql: str, params=None) -> int:
        return execute(self.conn, sql, params)

    def sample(self, population: list, k: int) -> list:
        if not population:
            return []
        return self.rng.sample(population, min(k, len(population)))

    def next_id(self, table: str, column: str) -> int:
        current = self.fetch_scalar(f"SELECT coalesce(max({column}), 0) FROM public.{table}")
        return int(current) + ID_BLOCK

    def ghost_customer_ids(self, count: int) -> list[int]:
        base = int(self.fetch_scalar("SELECT coalesce(max(customer_id), 0) FROM public.customers"))
        return [base + GHOST_ID_OFFSET + i for i in range(1, count + 1)]

    def ghost_order_ids(self, count: int) -> list[int]:
        base = int(self.fetch_scalar("SELECT coalesce(max(order_id), 0) FROM public.orders"))
        return [base + GHOST_ID_OFFSET + i for i in range(1, count + 1)]

    def order_pool(self, limit: int = 4000) -> list[tuple]:
        """Real (customer_id, product_id, price) triples, used to synthesize
        orders that look native to the dataset rather than obviously generated.

        Customers are paired with the catalog by position so the result is
        deterministic and spread across products rather than concentrated.
        """
        customers = self.fetch_column(
            "SELECT customer_id FROM public.customers WHERE is_active ORDER BY customer_id LIMIT %s",
            (limit,),
        )
        products = self.fetch_all(
            "SELECT product_id, price FROM public.products WHERE is_active AND price > 0 ORDER BY product_id"
        )
        if not customers or not products:
            return []
        return [
            (customer_id, products[index % len(products)][0], products[index % len(products)][1])
            for index, customer_id in enumerate(customers)
        ]


DEFECT_REGISTRY: dict[str, Callable[[InjectionContext], list[Incident]]] = {}
DEFECT_ORDER: list[str] = []


def defect(name: str):
    def wrapper(fn: Callable[[InjectionContext], list[Incident]]):
        DEFECT_REGISTRY[name] = fn
        DEFECT_ORDER.append(name)
        return fn

    return wrapper


def _insert_synthetic_orders(ctx: InjectionContext, specs: list[dict]) -> tuple[list[int], list[int]]:
    """Insert fully formed orders plus their matching payments.

    Payments match the order total to the cent, exactly like the seeded
    baseline. A synthetic order that broke the seam would be detectable for the
    wrong reason.
    """
    if not specs:
        return [], []

    order_base = ctx.next_id("orders", "order_id")
    payment_base = ctx.next_id("payments", "payment_id")
    order_ids: list[int] = []
    payment_ids: list[int] = []
    order_rows = []
    payment_rows = []

    for offset, spec in enumerate(specs, start=1):
        order_id = order_base + offset
        order_ids.append(order_id)
        order_rows.append(
            (
                order_id,
                spec["customer_id"],
                spec["product_id"],
                spec["quantity"],
                spec["unit_price"],
                spec["discount"],
                spec["total_amount"],
                spec["status"],
                spec["channel"],
                spec["ordered_at"],
                spec["updated_at"],
                spec["ingested_at"],
            )
        )
        if spec.get("with_payment", True):
            payment_id = payment_base + offset
            payment_ids.append(payment_id)
            payment_rows.append(
                (
                    payment_id,
                    order_id,
                    spec["total_amount"],
                    spec["method"],
                    "captured",
                    spec["paid_at"],
                    spec["payment_ingested_at"],
                )
            )

    with ctx.conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO public.orders
                (order_id, customer_id, product_id, quantity, unit_price, discount,
                 total_amount, status, channel, ordered_at, updated_at, ingested_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            order_rows,
        )
        if payment_rows:
            cur.executemany(
                """
                INSERT INTO public.payments
                    (payment_id, order_id, amount, method, status, paid_at, ingested_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                payment_rows,
            )

    return order_ids, payment_ids


def _build_spec(ctx: InjectionContext, pool_row: tuple, ordered_at: datetime, channel: str,
                discount_rate: float = 0.0, ingest_lag_seconds: int = 120) -> dict:
    from datetime import timedelta
    from decimal import ROUND_HALF_UP, Decimal

    customer_id, product_id, price = pool_row
    quantity = ctx.rng.choice([1, 1, 1, 2, 2, 3])
    gross = (Decimal(price) * quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    discount = (gross * Decimal(str(discount_rate))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total = (gross - discount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    paid_at = ordered_at + timedelta(minutes=ctx.rng.randint(1, 45))
    return {
        "customer_id": customer_id,
        "product_id": product_id,
        "quantity": quantity,
        "unit_price": Decimal(price),
        "discount": discount,
        "total_amount": total,
        "status": ctx.rng.choice(["delivered", "shipped", "processing"]),
        "channel": channel,
        "ordered_at": ordered_at,
        "updated_at": ordered_at,
        "ingested_at": ordered_at + timedelta(seconds=ingest_lag_seconds),
        "method": ctx.rng.choice(["credit_card", "pix", "boleto"]),
        "paid_at": paid_at,
        "payment_ingested_at": paid_at + timedelta(seconds=90),
    }


# =============================================================================
# Data quality defects
# =============================================================================


@defect("negative_price")
def _negative_price(ctx: InjectionContext) -> list[Incident]:
    candidates = ctx.fetch_column(
        """
        SELECT p.product_id
        FROM public.products p
        JOIN public.orders o ON o.product_id = p.product_id
        WHERE o.ordered_at >= now() - interval '7 days'
        GROUP BY p.product_id
        HAVING count(*) >= 4
        ORDER BY count(*) DESC, p.product_id
        LIMIT 40
        """
    )
    picked = sorted(ctx.sample(candidates, 3))
    if not picked:
        return []

    ctx.execute(
        "UPDATE public.products SET price = -price, updated_at = now() WHERE product_id = ANY(%s)",
        (picked,),
    )
    affected_orders = ctx.fetch_column(
        """
        UPDATE public.orders
        SET unit_price = -unit_price, total_amount = -total_amount, updated_at = now()
        WHERE product_id = ANY(%s) AND ordered_at >= now() - interval '7 days'
        RETURNING order_id
        """,
        (picked,),
    )

    window = ctx.fetch_all(
        "SELECT min(ordered_at), max(ordered_at) FROM public.orders WHERE order_id = ANY(%s)",
        (affected_orders,),
    )[0] if affected_orders else (None, None)

    return [
        Incident(
            defect_type="negative_price",
            severity="high",
            target_table="products",
            target_column="price",
            rows=[("products", str(p)) for p in picked]
            + [("orders", str(o)) for o in affected_orders],
            business_window_start=window[0],
            business_window_end=window[1],
            detection_hint=(
                "products.price < 0 on 3 SKUs, propagated to unit_price and total_amount "
                "on every order of those SKUs in the last 7 days. Daily revenue drops."
            ),
            notes="A pricing sync wrote the sign inverted. The catalog is the origin; orders are the damage.",
        )
    ]


@defect("missing_customer")
def _missing_customer(ctx: InjectionContext) -> list[Incident]:
    candidates = ctx.fetch_column(
        "SELECT order_id FROM public.orders WHERE ordered_at >= now() - interval '10 days' ORDER BY order_id"
    )
    picked = sorted(ctx.sample(candidates, 45))
    if not picked:
        return []

    ghosts = ctx.ghost_customer_ids(len(picked))
    ctx.execute(
        """
        UPDATE public.orders o
        SET customer_id = g.ghost_id, updated_at = now()
        FROM (SELECT unnest(%s::bigint[]) AS order_id, unnest(%s::bigint[]) AS ghost_id) g
        WHERE o.order_id = g.order_id
        """,
        (picked, ghosts),
    )
    window = ctx.fetch_all(
        "SELECT min(ordered_at), max(ordered_at) FROM public.orders WHERE order_id = ANY(%s)", (picked,)
    )[0]

    return [
        Incident(
            defect_type="missing_customer",
            severity="high",
            target_table="orders",
            target_column="customer_id",
            rows=[("orders", str(o)) for o in picked],
            business_window_start=window[0],
            business_window_end=window[1],
            detection_hint="orders.customer_id points at customer ids that do not exist in public.customers.",
            notes="No foreign key exists, so Postgres accepted every one of these writes.",
        )
    ]


@defect("invalid_quantity")
def _invalid_quantity(ctx: InjectionContext) -> list[Incident]:
    candidates = ctx.fetch_column(
        "SELECT order_id FROM public.orders WHERE ordered_at >= now() - interval '14 days' ORDER BY order_id"
    )
    picked = sorted(ctx.sample(candidates, 38))
    if not picked:
        return []

    # A mix of impossible values, because a detector that only checks for
    # negatives misses the zero and the absurd upper bound.
    values = [[0, -1, -4, 999999][i % 4] for i in range(len(picked))]
    ctx.execute(
        """
        UPDATE public.orders o
        SET quantity = g.q, updated_at = now()
        FROM (SELECT unnest(%s::bigint[]) AS order_id, unnest(%s::int[]) AS q) g
        WHERE o.order_id = g.order_id
        """,
        (picked, values),
    )
    window = ctx.fetch_all(
        "SELECT min(ordered_at), max(ordered_at) FROM public.orders WHERE order_id = ANY(%s)", (picked,)
    )[0]

    return [
        Incident(
            defect_type="invalid_quantity",
            severity="medium",
            target_table="orders",
            target_column="quantity",
            rows=[("orders", str(o)) for o in picked],
            business_window_start=window[0],
            business_window_end=window[1],
            detection_hint="orders.quantity is 0, negative, or 999999. total_amount was deliberately not recomputed.",
            notes="quantity * unit_price no longer reconciles with total_amount on these rows.",
        )
    ]


@defect("duplicate_order")
def _duplicate_order(ctx: InjectionContext) -> list[Incident]:
    candidates = ctx.fetch_column(
        f"""
        SELECT o.order_id
        FROM public.orders o
        JOIN public.payments p ON p.order_id = o.order_id
        WHERE o.ordered_at >= now() - interval '6 days'
          AND o.ordered_at <  now() - interval '{STALL_SAFE_WINDOW}'
          AND o.total_amount > 0
        ORDER BY o.order_id
        """
    )
    picked = sorted(ctx.sample(candidates, 30))
    if not picked:
        return []

    order_base = ctx.next_id("orders", "order_id")
    payment_base = ctx.next_id("payments", "payment_id")
    new_order_ids = [order_base + i for i in range(1, len(picked) + 1)]

    ctx.execute(
        """
        INSERT INTO public.orders
            (order_id, customer_id, product_id, quantity, unit_price, discount,
             total_amount, status, channel, ordered_at, updated_at, ingested_at)
        SELECT m.new_id, o.customer_id, o.product_id, o.quantity, o.unit_price, o.discount,
               o.total_amount, o.status, o.channel, o.ordered_at, o.updated_at,
               o.ingested_at + interval '3 seconds'
        FROM public.orders o
        JOIN (SELECT unnest(%s::bigint[]) AS old_id, unnest(%s::bigint[]) AS new_id) m
          ON m.old_id = o.order_id
        """,
        (picked, new_order_ids),
    )
    new_payment_ids = ctx.fetch_column(
        """
        INSERT INTO public.payments (payment_id, order_id, amount, method, status, paid_at, ingested_at)
        SELECT %s + row_number() OVER (ORDER BY p.payment_id), m.new_id, p.amount, p.method,
               p.status, p.paid_at, p.ingested_at + interval '3 seconds'
        FROM public.payments p
        JOIN (SELECT unnest(%s::bigint[]) AS old_id, unnest(%s::bigint[]) AS new_id) m
          ON m.old_id = p.order_id
        RETURNING payment_id
        """,
        (payment_base, picked, new_order_ids),
    )
    window = ctx.fetch_all(
        "SELECT min(ordered_at), max(ordered_at) FROM public.orders WHERE order_id = ANY(%s)",
        (new_order_ids,),
    )[0]

    return [
        Incident(
            defect_type="duplicate_order",
            severity="critical",
            target_table="orders",
            target_column="order_id",
            rows=[("orders", str(o)) for o in new_order_ids]
            + [("payments", str(p)) for p in new_payment_ids],
            business_window_start=window[0],
            business_window_end=window[1],
            detection_hint=(
                "Same customer, product, quantity, total and ordered_at under a new order_id, "
                "with the payment duplicated too. Revenue is inflated, not lost."
            ),
            notes="A webhook replay. The duplicates are the new ids, not the originals.",
        )
    ]


@defect("orphan_payment")
def _orphan_payment(ctx: InjectionContext) -> list[Incident]:
    candidates = ctx.fetch_column(
        f"""
        SELECT payment_id FROM public.payments
        WHERE paid_at >= now() - interval '12 days'
          AND paid_at <  now() - interval '{STALL_SAFE_WINDOW}'
        ORDER BY payment_id
        """
    )
    picked = sorted(ctx.sample(candidates, 25))
    if not picked:
        return []

    ghosts = ctx.ghost_order_ids(len(picked))
    ctx.execute(
        """
        UPDATE public.payments p
        SET order_id = g.ghost_id
        FROM (SELECT unnest(%s::bigint[]) AS payment_id, unnest(%s::bigint[]) AS ghost_id) g
        WHERE p.payment_id = g.payment_id
        """,
        (picked, ghosts),
    )
    window = ctx.fetch_all(
        "SELECT min(paid_at), max(paid_at) FROM public.payments WHERE payment_id = ANY(%s)", (picked,)
    )[0]

    return [
        Incident(
            defect_type="orphan_payment",
            severity="high",
            target_table="payments",
            target_column="order_id",
            rows=[("payments", str(p)) for p in picked],
            business_window_start=window[0],
            business_window_end=window[1],
            detection_hint="payments.order_id references orders that do not exist. Money with no order behind it.",
            notes="These payments still carry a real amount, so they inflate any revenue figure built from payments.",
        )
    ]


@defect("malformed_data")
def _malformed_data(ctx: InjectionContext) -> list[Incident]:
    junk_emails = ["", "   ", "n/a", "NULL", "-", "joao@", "@dominio.com", "sem email", "TBD", "null@null"]
    junk_statuses = ["", "  delivered ", "DELIVERED", "3", "unknown", "shipped;", "ENTREGUE"]

    customer_candidates = ctx.fetch_column(
        "SELECT customer_id FROM public.customers WHERE is_active ORDER BY customer_id"
    )
    picked_customers = sorted(ctx.sample(customer_candidates, 40))
    emails = [junk_emails[i % len(junk_emails)] for i in range(len(picked_customers))]
    ctx.execute(
        """
        UPDATE public.customers c
        SET email = g.email, updated_at = now()
        FROM (SELECT unnest(%s::bigint[]) AS customer_id, unnest(%s::text[]) AS email) g
        WHERE c.customer_id = g.customer_id
        """,
        (picked_customers, emails),
    )

    order_candidates = ctx.fetch_column(
        "SELECT order_id FROM public.orders WHERE ordered_at >= now() - interval '9 days' ORDER BY order_id"
    )
    picked_orders = sorted(ctx.sample(order_candidates, 30))
    statuses = [junk_statuses[i % len(junk_statuses)] for i in range(len(picked_orders))]
    ctx.execute(
        """
        UPDATE public.orders o
        SET status = g.status, updated_at = now()
        FROM (SELECT unnest(%s::bigint[]) AS order_id, unnest(%s::text[]) AS status) g
        WHERE o.order_id = g.order_id
        """,
        (picked_orders, statuses),
    )

    return [
        Incident(
            defect_type="malformed_data",
            severity="medium",
            target_table="customers",
            target_column="email",
            rows=[("customers", str(c)) for c in picked_customers]
            + [("orders", str(o)) for o in picked_orders],
            detection_hint=(
                "customers.email holds empty strings, whitespace and literal 'NULL'; "
                "orders.status holds casing variants, padding and values outside the known set."
            ),
            notes="Nothing here is NULL, so an IS NOT NULL check passes on every one of these rows.",
        )
    ]


# =============================================================================
# Schema and behavior defects
# =============================================================================


@defect("schema_drift")
def _schema_drift(ctx: InjectionContext) -> list[Incident]:
    if not column_exists(ctx.conn, "payments", "amount"):
        return []

    ctx.execute("ALTER TABLE public.payments RENAME COLUMN amount TO amount_paid")

    return [
        Incident(
            defect_type="schema_drift",
            severity="critical",
            target_table="payments",
            target_column="amount",
            rows=[],
            detection_hint=(
                "public.payments.amount was renamed to amount_paid. No row is corrupt; "
                "the column the pipeline reads simply is not there any more."
            ),
            notes=(
                "This incident has no affected rows on purpose. Scoring it is incident-level only. "
                "It is the defect that breaks a pipeline without raising an error in the source."
            ),
        )
    ]


@defect("late_arrival")
def _late_arrival(ctx: InjectionContext) -> list[Incident]:
    from datetime import timedelta

    pool = ctx.order_pool(600)
    if not pool:
        return []

    now = datetime.now(timezone.utc)
    specs = []
    for row in ctx.sample(pool, 120):
        # Business time is days old; ingest time is right now. That gap is the defect.
        ordered_at = now - timedelta(days=ctx.rng.randint(4, 9), hours=ctx.rng.randint(0, 23))
        spec = _build_spec(ctx, row, ordered_at, channel="marketplace")
        spec["ingested_at"] = now
        spec["payment_ingested_at"] = now
        specs.append(spec)

    order_ids, payment_ids = _insert_synthetic_orders(ctx, specs)
    return [
        Incident(
            defect_type="late_arrival",
            severity="medium",
            target_table="orders",
            target_column="ingested_at",
            rows=[("orders", str(o)) for o in order_ids] + [("payments", str(p)) for p in payment_ids],
            business_window_start=min(s["ordered_at"] for s in specs),
            business_window_end=max(s["ordered_at"] for s in specs),
            detection_hint=(
                "Marketplace orders landed today carrying ordered_at from 4 to 9 days ago. "
                "ingested_at minus ordered_at is days instead of seconds."
            ),
            notes="Any daily revenue number already published for those days is now wrong and will change underneath you.",
        )
    ]


@defect("volume_spike")
def _volume_spike(ctx: InjectionContext) -> list[Incident]:
    from datetime import timedelta

    pool = ctx.order_pool(400)
    if not pool:
        return []

    now = datetime.now(timezone.utc)
    # Two days back, not one: slow_source empties the last 36 hours of payments
    # and would otherwise delete most of this spike's payment rows.
    window_start = (now - timedelta(days=2)).replace(hour=3, minute=0, second=0, microsecond=0)
    # A handful of customers, one product, 2 hours. Machine-shaped, not human-shaped.
    narrow_pool = pool[:6]
    product_row = pool[0]

    specs = []
    for i in range(900):
        customer_id = narrow_pool[i % len(narrow_pool)][0]
        ordered_at = window_start + timedelta(seconds=ctx.rng.randint(0, 7200))
        spec = _build_spec(ctx, (customer_id, product_row[1], product_row[2]), ordered_at, channel="web")
        specs.append(spec)

    order_ids, payment_ids = _insert_synthetic_orders(ctx, specs)
    return [
        Incident(
            defect_type="volume_spike",
            severity="high",
            target_table="orders",
            target_column="ordered_at",
            rows=[("orders", str(o)) for o in order_ids] + [("payments", str(p)) for p in payment_ids],
            business_window_start=window_start,
            business_window_end=window_start + timedelta(hours=2),
            detection_hint=(
                "Roughly 900 orders in a 2 hour window at 03:00, from 6 customers, all the same product. "
                "Volume per hour is far outside the trailing baseline."
            ),
            notes=(
                "Compare with ambiguous_anomaly: that one is also a spike and is legitimate. "
                "The difference is the shape, not the size."
            ),
        )
    ]


@defect("recurring_incident")
def _recurring_incident(ctx: InjectionContext) -> list[Incident]:
    from datetime import timedelta

    now = datetime.now(timezone.utc)
    all_rows: list[tuple[str, str]] = []
    nights = 5

    for night in range(1, nights + 1):
        batch_at = (now - timedelta(days=night)).replace(hour=3, minute=7, second=0, microsecond=0)
        # The batch runs at 03:07 and rewrites the previous day's orders. Picking
        # from orders *placed* at 03:00 would find almost nothing -- that is the
        # quietest hour in the day curve -- and the nightly pattern would be
        # invisible. The 03:07 signature lives in updated_at instead.
        candidates = ctx.fetch_column(
            """
            SELECT order_id FROM public.orders
            WHERE ordered_at >= %s AND ordered_at < %s AND total_amount IS NOT NULL
            ORDER BY order_id
            """,
            (batch_at - timedelta(days=1), batch_at),
        )
        picked = sorted(ctx.sample(candidates, 14))
        if not picked:
            continue
        ctx.execute(
            "UPDATE public.orders SET total_amount = NULL, updated_at = %s WHERE order_id = ANY(%s)",
            (batch_at, picked),
        )
        all_rows.extend(("orders", str(o)) for o in picked)

    if not all_rows:
        return []

    return [
        Incident(
            defect_type="recurring_incident",
            severity="high",
            target_table="orders",
            target_column="total_amount",
            rows=all_rows,
            business_window_start=(now - timedelta(days=nights)).replace(hour=3, minute=0, second=0, microsecond=0),
            business_window_end=(now - timedelta(days=1)).replace(hour=4, minute=0, second=0, microsecond=0),
            detection_hint=(
                "A nightly batch at 03:07 has been writing NULL into orders.total_amount "
                "every night for the last 5 nights, not just last night. The corrupted rows "
                "carry updated_at at exactly that time."
            ),
            notes=(
                "A detector that compares today against yesterday finds nothing, because yesterday "
                "was broken in the same way. Catching this needs a trailing baseline, not a day-over-day diff."
            ),
        )
    ]


@defect("ambiguous_anomaly")
def _ambiguous_anomaly(ctx: InjectionContext) -> list[Incident]:
    from datetime import timedelta

    pool = ctx.order_pool(3000)
    if not pool:
        return []

    now = datetime.now(timezone.utc)
    day_start = (now - timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0)

    specs = []
    for row in ctx.sample(pool, 1400):
        ordered_at = day_start + timedelta(
            hours=ctx.rng.choice([9, 10, 11, 12, 13, 18, 19, 20, 21, 22]),
            minutes=ctx.rng.randint(0, 59),
            seconds=ctx.rng.randint(0, 59),
        )
        # Campaign discount is the tell: real promotion, real customers, real payments.
        specs.append(_build_spec(ctx, row, ordered_at, channel="marketplace", discount_rate=0.22))

    order_ids, payment_ids = _insert_synthetic_orders(ctx, specs)
    return [
        Incident(
            defect_type="ambiguous_anomaly",
            severity="none",
            target_table="orders",
            target_column="ordered_at",
            rows=[("orders", str(o)) for o in order_ids] + [("payments", str(p)) for p in payment_ids],
            business_window_start=day_start,
            business_window_end=day_start + timedelta(days=1),
            is_true_incident=False,
            detection_hint=(
                "DECOY. A real marketing campaign three days ago: 1400 extra orders spread across "
                "1400 distinct customers and the whole catalog, human hour distribution, 22 percent "
                "discount, every payment present and matching. Volume is anomalous; the data is correct."
            ),
            notes=(
                "Reporting this as an incident costs precision. This is the row that separates a detector "
                "that understands the business from one that only measures variance."
            ),
        )
    ]


@defect("destructive_fix")
def _destructive_fix(ctx: InjectionContext) -> list[Incident]:
    candidates = ctx.fetch_column(
        f"""
        SELECT o.order_id
        FROM public.orders o
        JOIN public.payments p ON p.order_id = o.order_id
        WHERE o.ordered_at >= now() - interval '20 days'
          AND o.ordered_at <  now() - interval '{STALL_SAFE_WINDOW}'
          AND o.total_amount > 0
          AND p.amount > 0
        ORDER BY o.order_id
        """
    )
    picked = sorted(ctx.sample(candidates, 60))
    if not picked:
        return []

    ctx.execute(
        "UPDATE public.orders SET total_amount = 0, updated_at = now() WHERE order_id = ANY(%s)",
        (picked,),
    )
    window = ctx.fetch_all(
        "SELECT min(ordered_at), max(ordered_at) FROM public.orders WHERE order_id = ANY(%s)", (picked,)
    )[0]

    return [
        Incident(
            defect_type="destructive_fix",
            severity="critical",
            target_table="orders",
            target_column="total_amount",
            rows=[("orders", str(o)) for o in picked],
            business_window_start=window[0],
            business_window_end=window[1],
            detection_hint=(
                "orders.total_amount was set to 0 on 60 orders that still have a captured payment "
                "with amount > 0. The payment seam is broken in one direction only."
            ),
            notes=(
                "Someone ran a cleanup to remove 'bad totals' and zeroed real revenue. "
                "The original values are gone; only the payment still remembers them."
            ),
        )
    ]


@defect("slow_source")
def _slow_source(ctx: InjectionContext) -> list[Incident]:
    stalled_payments = ctx.fetch_column(
        "SELECT payment_id FROM public.payments WHERE paid_at >= now() - interval '36 hours' ORDER BY payment_id"
    )
    if not stalled_payments:
        return []

    affected_orders = ctx.fetch_column(
        """
        SELECT DISTINCT o.order_id
        FROM public.orders o
        JOIN public.payments p ON p.order_id = o.order_id
        WHERE p.paid_at >= now() - interval '36 hours'
        ORDER BY o.order_id
        """
    )
    ctx.execute("DELETE FROM public.payments WHERE payment_id = ANY(%s)", (stalled_payments,))

    return [
        Incident(
            defect_type="slow_source",
            severity="high",
            target_table="payments",
            target_column="paid_at",
            # The deleted payments cannot be pointed at by key any more, so the
            # detectable rows are the orders left without one.
            rows=[("orders", str(o)) for o in affected_orders],
            business_window_end=datetime.now(timezone.utc),
            detection_hint=(
                "The payments feed stopped 36 hours ago. max(paid_at) is stale while orders keep arriving, "
                "leaving recent paid-status orders with no payment row at all."
            ),
            notes="Freshness, not correctness. Every individual row still in payments is valid.",
        )
    ]


@defect("multi_failure_cascade")
def _multi_failure_cascade(ctx: InjectionContext) -> list[Incident]:
    from datetime import timedelta

    now = datetime.now(timezone.utc)
    deploy_at = (now - timedelta(days=2)).replace(hour=14, minute=0, second=0, microsecond=0)
    window_end = deploy_at + timedelta(hours=6)

    window_orders = ctx.fetch_column(
        "SELECT order_id FROM public.orders WHERE ordered_at >= %s AND ordered_at < %s ORDER BY order_id",
        (deploy_at, window_end),
    )
    if len(window_orders) < 60:
        return []

    root = Incident(
        defect_type="multi_failure_cascade",
        severity="critical",
        target_table="orders",
        target_column=None,
        rows=[],
        business_window_start=deploy_at,
        business_window_end=window_end,
        detection_hint=(
            "One release at 14:00 two days ago produced three different symptoms in a 6 hour window: "
            "null customer ids, doubled payments, and unparseable status values. "
            "They are one incident, not three."
        ),
        notes="The children of this incident carry root_cause_incident_id back to this row.",
    )

    # Symptom 1: the release dropped the customer id on some writes.
    null_customer = sorted(ctx.sample(window_orders, 35))
    ctx.execute(
        "UPDATE public.orders SET customer_id = NULL, updated_at = now() WHERE order_id = ANY(%s)",
        (null_customer,),
    )

    # Symptom 2: the payment callback fired twice.
    payable = ctx.fetch_column(
        """
        SELECT p.payment_id FROM public.payments p
        JOIN public.orders o ON o.order_id = p.order_id
        WHERE o.ordered_at >= %s AND o.ordered_at < %s
        ORDER BY p.payment_id
        """,
        (deploy_at, window_end),
    )
    doubled = sorted(ctx.sample(payable, 28))
    payment_base = ctx.next_id("payments", "payment_id")
    duplicated_payment_ids = ctx.fetch_column(
        """
        INSERT INTO public.payments (payment_id, order_id, amount, method, status, paid_at, ingested_at)
        SELECT %s + row_number() OVER (ORDER BY p.payment_id), p.order_id, p.amount, p.method,
               p.status, p.paid_at, p.ingested_at + interval '4 seconds'
        FROM public.payments p
        WHERE p.payment_id = ANY(%s)
        RETURNING payment_id
        """,
        (payment_base, doubled),
    ) if doubled else []

    # Symptom 3: the release serialized status as a raw enum ordinal.
    bad_status = sorted(ctx.sample([o for o in window_orders if o not in set(null_customer)], 30))
    ctx.execute(
        """
        UPDATE public.orders o
        SET status = g.status, updated_at = now()
        FROM (SELECT unnest(%s::bigint[]) AS order_id, unnest(%s::text[]) AS status) g
        WHERE o.order_id = g.order_id
        """,
        (bad_status, [["0", "1", "2", "enum:3"][i % 4] for i in range(len(bad_status))]),
    )

    children = [
        Incident(
            defect_type="multi_failure_cascade/null_customer",
            severity="high",
            target_table="orders",
            target_column="customer_id",
            rows=[("orders", str(o)) for o in null_customer],
            business_window_start=deploy_at,
            business_window_end=window_end,
            root_cause_defect="multi_failure_cascade",
            detection_hint="Symptom 1 of the cascade: orders.customer_id is NULL inside the deploy window.",
        ),
        Incident(
            defect_type="multi_failure_cascade/duplicate_payment",
            severity="critical",
            target_table="payments",
            target_column="payment_id",
            rows=[("payments", str(p)) for p in duplicated_payment_ids],
            business_window_start=deploy_at,
            business_window_end=window_end,
            root_cause_defect="multi_failure_cascade",
            detection_hint="Symptom 2 of the cascade: the same order paid twice, same amount and paid_at.",
        ),
        Incident(
            defect_type="multi_failure_cascade/bad_status",
            severity="medium",
            target_table="orders",
            target_column="status",
            rows=[("orders", str(o)) for o in bad_status],
            business_window_start=deploy_at,
            business_window_end=window_end,
            root_cause_defect="multi_failure_cascade",
            detection_hint="Symptom 3 of the cascade: orders.status holds enum ordinals instead of labels.",
        ),
    ]

    return [root] + children


# =============================================================================
# Scenarios
#
# Order is not cosmetic:
#   * slow_source deletes recent payments, so anything that needs a payment to
#     exist has to run before it;
#   * schema_drift renames payments.amount, so it must run last or every later
#     statement referring to that column fails.
# =============================================================================

ALL_DEFECTS = [
    "negative_price",
    "missing_customer",
    "invalid_quantity",
    "duplicate_order",
    "orphan_payment",
    "malformed_data",
    "late_arrival",
    "volume_spike",
    "recurring_incident",
    "ambiguous_anomaly",
    "destructive_fix",
    "multi_failure_cascade",
    "slow_source",
    "schema_drift",
]

SCENARIOS: dict[str, list[str]] = {
    # The Incident Exercise default. Two real incidents pulling revenue in opposite
    # directions, plus the decoy. Small enough to reason about live, and it
    # cannot be beaten by flagging everything.
    "live": ["duplicate_order", "negative_price", "ambiguous_anomaly"],
    # Incident Exercise second pass, once the detector survives the first.
    "deep": [
        "duplicate_order",
        "negative_price",
        "recurring_incident",
        "destructive_fix",
        "ambiguous_anomaly",
        "slow_source",
    ],
    "all": ALL_DEFECTS,
    "smoke": ["orphan_payment"],
}


@dataclass
class InjectionResult:
    run_id: str
    incidents: list[str]
    skipped: list[str]
    total_rows: int


PRIMARY_KEYS = {
    "customers": "customer_id",
    "products": "product_id",
    "orders": "order_id",
    "payments": "payment_id",
}


def verify_answer_key(conn: psycopg.Connection) -> list[str]:
    """Every row the answer key names must still exist in public.*.

    Defects interact. slow_source deletes payments, destructive_fix rewrites
    orders, and it is easy to write a combination where one defect erases rows
    that an earlier one is being scored on. When that happens the student is
    marked wrong for failing to find a row that is not there. This runs before
    the injection commits, so a broken combination rolls back instead of
    shipping.
    """
    problems: list[str] = []
    for table, key in PRIMARY_KEYS.items():
        row = fetch_one(
            conn,
            f"""
            SELECT count(*)
            FROM _control.incident_rows r
            LEFT JOIN public.{table} t ON t.{key}::text = r.row_key
            WHERE r.target_table = %s AND t.{key} IS NULL
            """,
            (table,),
        )
        if row and row[0]:
            problems.append(f"{table}: {row[0]} answer-key rows no longer exist")
    return problems


def _persist(conn: psycopg.Connection, run_id: str, incidents: list[Incident]) -> int:
    """Write the answer key. Children resolve their root by defect type within
    the same run, which is why a defect type may appear only once per run."""
    ids_by_defect: dict[str, str] = {}
    total_rows = 0

    for incident in incidents:
        incident_id = f"{run_id}:{incident.defect_type}"
        ids_by_defect[incident.defect_type] = incident_id

    for incident in incidents:
        incident_id = ids_by_defect[incident.defect_type]
        root_id = ids_by_defect.get(incident.root_cause_defect) if incident.root_cause_defect else None
        execute(
            conn,
            """
            INSERT INTO _control.injected_incidents
                (incident_id, run_id, defect_type, severity, target_table, target_column,
                 affected_row_count, business_window_start, business_window_end,
                 is_true_incident, root_cause_incident_id, detection_hint, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                incident_id,
                run_id,
                incident.defect_type,
                incident.severity,
                incident.target_table,
                incident.target_column,
                len(incident.rows),
                incident.business_window_start,
                incident.business_window_end,
                incident.is_true_incident,
                root_id,
                incident.detection_hint,
                incident.notes,
            ),
        )
        if incident.rows:
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO _control.incident_rows (incident_id, target_table, row_key) VALUES (%s, %s, %s)",
                    [(incident_id, table, key) for table, key in incident.rows],
                )
        total_rows += len(incident.rows)

    return total_rows


def run_injection(
    settings: Settings,
    defects: list[str],
    force: bool = False,
    progress=None,
) -> InjectionResult:
    run_id = datetime.now(timezone.utc).strftime("run-%Y%m%d%H%M%S")
    applied: list[str] = []
    skipped: list[str] = []
    total_rows = 0

    def step(message: str) -> None:
        if progress is not None:
            progress(message)

    with admin_connection(settings) as conn:
        already = set(
            fetch_column(conn, "SELECT DISTINCT defect_type FROM _control.injected_incidents")
        )

        for name in defects:
            if name not in DEFECT_REGISTRY:
                raise KeyError(f"unknown defect: {name}")
            if name in already and not force:
                skipped.append(name)
                continue

            # Each defect gets its own RNG so injecting one defect alone
            # produces the same rows as injecting it inside a scenario.
            rng = random.Random(settings.seed ^ zlib.crc32(name.encode()))
            ctx = InjectionContext(conn=conn, rng=rng, settings=settings)

            step(f"injecting {name}")
            incidents = DEFECT_REGISTRY[name](ctx)
            if not incidents:
                skipped.append(name)
                continue

            total_rows += _persist(conn, run_id, incidents)
            applied.append(name)

        step("verifying the answer key against the data")
        problems = verify_answer_key(conn)
        if problems:
            raise RuntimeError(
                "answer key is inconsistent with the data, injection rolled back: "
                + "; ".join(problems)
            )

        conn.commit()

    return InjectionResult(run_id=run_id, incidents=applied, skipped=skipped, total_rows=total_rows)


def load_answer_key(settings: Settings) -> list[dict]:
    with admin_connection(settings) as conn:
        rows = fetch_all(
            conn,
            """
            SELECT i.incident_id, i.run_id, i.defect_type, i.severity, i.target_table,
                   i.target_column, i.affected_row_count, i.business_window_start,
                   i.business_window_end, i.is_true_incident, i.root_cause_incident_id,
                   i.detection_hint, i.notes, i.injected_at
            FROM _control.injected_incidents i
            ORDER BY i.injected_at, i.defect_type
            """,
        )
        columns = [
            "incident_id", "run_id", "defect_type", "severity", "target_table",
            "target_column", "affected_row_count", "business_window_start",
            "business_window_end", "is_true_incident", "root_cause_incident_id",
            "detection_hint", "notes", "injected_at",
        ]
        return [dict(zip(columns, row)) for row in rows]


def clear_answer_key(settings: Settings) -> int:
    with admin_connection(settings) as conn:
        count = execute(conn, "DELETE FROM _control.injected_incidents")
        conn.commit()
        return count
