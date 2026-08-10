"""Correlated seeder for the TransactCo brownfield.

Everything here is driven by a single seeded RNG. The same TRANSACTCO_SEED
reproduces the customer/catalog generation and historical order shape for a
given seed-time anchor.

Time is deliberately relative. The window is anchored to the moment you seed,
because stale fixture data makes every freshness exercise meaningless. The
partial current day is generated only up to that moment, so laptops seeded at
different times can have slightly different final row counts. The answer key is
written against each laptop's own rows at injection time.

The baseline is deliberately clean on the seam that matters: for every order
that has a payment, payments.amount equals orders.total_amount to the cent. Real
noise on that relationship would drown the injected defects and make Day 4
scoring meaningless -- the student would be chasing our sloppiness instead of
the incident.
"""

from __future__ import annotations

import bisect
import random
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from itertools import accumulate

import psycopg

from .config import Settings
from .db import admin_connection, column_exists, execute, fetch_one

CENT = Decimal("0.01")

FIRST_NAMES = [
    "Ana", "Bruno", "Carla", "Diego", "Eduarda", "Felipe", "Gabriela", "Henrique",
    "Isabela", "Joao", "Karina", "Lucas", "Mariana", "Nicolas", "Olivia", "Paulo",
    "Rafaela", "Samuel", "Tatiana", "Vinicius", "Yasmin", "Andre", "Beatriz",
    "Caio", "Daniela", "Emerson", "Fernanda", "Gustavo", "Helena", "Igor",
    "Juliana", "Leandro", "Marcela", "Nathalia", "Otavio", "Patricia", "Renato",
    "Sabrina", "Thiago", "Vanessa",
]

LAST_NAMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves",
    "Pereira", "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho",
    "Almeida", "Lopes", "Soares", "Fernandes", "Vieira", "Barbosa", "Rocha",
    "Dias", "Nascimento", "Andrade", "Moreira", "Nunes", "Marques", "Machado",
    "Mendes", "Freitas",
]

EMAIL_DOMAINS = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com.br", "uol.com.br"]

CITIES = [
    ("Sao Paulo", "BR"), ("Rio de Janeiro", "BR"), ("Belo Horizonte", "BR"),
    ("Curitiba", "BR"), ("Porto Alegre", "BR"), ("Salvador", "BR"),
    ("Recife", "BR"), ("Fortaleza", "BR"), ("Brasilia", "BR"), ("Campinas", "BR"),
    ("Lisboa", "PT"), ("Porto", "PT"), ("Buenos Aires", "AR"),
    ("Santiago", "CL"), ("Mexico City", "MX"), ("Miami", "US"),
]
CITY_WEIGHTS = [22, 14, 8, 7, 6, 6, 5, 5, 6, 4, 4, 3, 4, 3, 2, 1]

SEGMENTS = ["consumer", "business", "enterprise"]
SEGMENT_WEIGHTS = [70, 22, 8]

# category -> (price floor, price ceiling, popularity weight)
CATEGORIES = {
    "electronics": (Decimal("189.00"), Decimal("6400.00"), 24),
    "home": (Decimal("39.90"), Decimal("1250.00"), 20),
    "fashion": (Decimal("29.90"), Decimal("899.00"), 22),
    "beauty": (Decimal("19.90"), Decimal("459.00"), 14),
    "sports": (Decimal("49.90"), Decimal("2100.00"), 11),
    "books": (Decimal("24.90"), Decimal("189.00"), 9),
}

PRODUCT_NOUNS = {
    "electronics": ["Headphone", "Smartphone", "Notebook", "Monitor", "Teclado", "Camera", "Tablet", "Roteador"],
    "home": ["Cafeteira", "Panela", "Luminaria", "Aspirador", "Ventilador", "Jogo de Toalhas", "Cadeira"],
    "fashion": ["Camiseta", "Tenis", "Jaqueta", "Calca", "Vestido", "Bolsa", "Oculos"],
    "beauty": ["Perfume", "Hidratante", "Shampoo", "Base", "Protetor Solar", "Batom"],
    "sports": ["Bicicleta", "Halter", "Esteira", "Bola", "Mochila", "Raquete"],
    "books": ["Romance", "Biografia", "Manual", "Guia", "Ensaio", "Antologia"],
}
PRODUCT_MODIFIERS = ["Pro", "Max", "Essential", "Compact", "Ultra", "Classic", "Prime", "Lite", "Plus", "Studio"]

CHANNELS = ["web", "mobile_app", "marketplace"]
CHANNEL_WEIGHTS = [62, 30, 8]

PAYMENT_METHODS = ["credit_card", "pix", "boleto", "voucher"]
PAYMENT_METHOD_WEIGHTS = [58, 27, 10, 5]

QUANTITY_CHOICES = [1, 2, 3, 4, 5]
QUANTITY_WEIGHTS = [60, 22, 10, 5, 3]

# Monday..Sunday. E-commerce peaks early in the week and softens on Saturday.
WEEKDAY_FACTORS = [1.12, 1.15, 1.05, 1.00, 0.96, 0.82, 0.90]

# Hour of day, 0..23. Lunch bump, evening peak.
HOUR_WEIGHTS = [
    2, 1, 1, 1, 1, 2, 4, 8, 14, 20, 26, 30,
    32, 28, 26, 27, 30, 36, 44, 48, 42, 30, 16, 7,
]

PAID_STATUSES = {"delivered", "shipped", "processing"}
REFUNDED_STATUSES = {"returned"}


class WeightedPicker:
    """Precomputed cumulative weights. rng.choices is O(n) per call and this is
    called once per order, which turns into hundreds of millions of operations
    on a 54k-order seed."""

    def __init__(self, population: list, weights: list[float]) -> None:
        self._population = population
        self._cumulative = list(accumulate(weights))
        self._total = self._cumulative[-1]

    def pick(self, rng: random.Random):
        cut = rng.random() * self._total
        return self._population[bisect.bisect_right(self._cumulative, cut)]


def _money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass
class SeedResult:
    customers: int
    products: int
    orders: int
    payments: int
    window_start: datetime
    window_end: datetime


def _repair_schema(conn: psycopg.Connection) -> None:
    """Undo schema_drift if it is still applied.

    Seeding writes to payments.amount by name. If a previous `make inject`
    renamed that column and the student re-seeds instead of resetting the
    container, every insert here would fail with a confusing error. Repairing is
    silent on purpose -- it happens before there is any data to lie about.
    """
    if column_exists(conn, "payments", "amount_paid") and not column_exists(conn, "payments", "amount"):
        execute(conn, "ALTER TABLE public.payments RENAME COLUMN amount_paid TO amount")


def _truncate(conn: psycopg.Connection) -> None:
    execute(conn, "TRUNCATE public.orders, public.payments, public.customers, public.products")
    execute(conn, "TRUNCATE _control.incident_rows, _control.injected_incidents CASCADE")


def _generate_customers(rng: random.Random, count: int, window_end: datetime) -> list[tuple]:
    city_picker = WeightedPicker(CITIES, CITY_WEIGHTS)
    segment_picker = WeightedPicker(SEGMENTS, SEGMENT_WEIGHTS)
    rows: list[tuple] = []

    for customer_id in range(1, count + 1):
        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)
        city, country = city_picker.pick(rng)
        # Signups spread over three years, denser recently.
        days_ago = int(1095 * (rng.random() ** 1.6))
        signup = (window_end - timedelta(days=days_ago)).date()
        # Clamped: a customer signing up today would otherwise get a created_at
        # later in the day than "now", and a future timestamp in a clean
        # baseline is a defect the answer key never recorded.
        created_at = min(
            datetime.combine(signup, datetime.min.time(), tzinfo=timezone.utc)
            + timedelta(hours=rng.randint(6, 22), minutes=rng.randint(0, 59)),
            window_end,
        )
        rows.append(
            (
                customer_id,
                f"{first} {last}",
                f"{first.lower()}.{last.lower()}{customer_id}@{rng.choice(EMAIL_DOMAINS)}",
                country,
                city,
                segment_picker.pick(rng),
                signup,
                rng.random() < 0.88,
                created_at,
                created_at,
                created_at + timedelta(seconds=rng.randint(1, 90)),
            )
        )
    return rows


def _generate_products(rng: random.Random, count: int, window_end: datetime) -> list[tuple]:
    names = list(CATEGORIES)
    picker = WeightedPicker(names, [CATEGORIES[name][2] for name in names])
    rows: list[tuple] = []

    for product_id in range(1, count + 1):
        category = picker.pick(rng)
        low, high, _ = CATEGORIES[category]
        # Skewed toward the cheap end of each category, like a real catalog.
        span = float(high - low)
        price = _money(low + Decimal(str(span * (rng.random() ** 2.1))))
        created_at = window_end - timedelta(days=rng.randint(30, 900), hours=rng.randint(0, 23))
        rows.append(
            (
                product_id,
                f"SKU-{product_id:05d}",
                f"{rng.choice(PRODUCT_NOUNS[category])} {rng.choice(PRODUCT_MODIFIERS)} {rng.randint(100, 999)}",
                category,
                price,
                _money(price * Decimal(str(rng.uniform(0.45, 0.72)))),
                rng.random() < 0.94,
                created_at,
                created_at,
                created_at + timedelta(seconds=rng.randint(1, 120)),
            )
        )
    return rows


def _status_for_age(rng: random.Random, age_days: float) -> str:
    if age_days > 12:
        return WeightedPicker(
            ["delivered", "returned", "cancelled"], [92, 5, 3]
        ).pick(rng)
    if age_days > 4:
        return WeightedPicker(
            ["delivered", "shipped", "returned", "cancelled"], [64, 28, 4, 4]
        ).pick(rng)
    if age_days > 1:
        return WeightedPicker(["shipped", "processing", "cancelled"], [58, 38, 4]).pick(rng)
    return WeightedPicker(["processing", "pending", "shipped"], [52, 36, 12]).pick(rng)


def _generate_orders_and_payments(
    rng: random.Random,
    settings: Settings,
    products: list[tuple],
    window_start: datetime,
    window_end: datetime,
) -> tuple[list[tuple], list[tuple]]:
    # Repeat buyers: a minority of customers place most of the orders.
    customer_ids = list(range(1, settings.customers + 1))
    customer_weights = [1.0 + 9.0 * (rng.random() ** 3) for _ in customer_ids]
    customer_picker = WeightedPicker(customer_ids, customer_weights)

    product_ids = [row[0] for row in products]
    product_prices = {row[0]: row[4] for row in products}
    product_weights = [1.0 + 12.0 * (rng.random() ** 2.6) for _ in product_ids]
    product_picker = WeightedPicker(product_ids, product_weights)

    hour_picker = WeightedPicker(list(range(24)), [float(w) for w in HOUR_WEIGHTS])
    quantity_picker = WeightedPicker(QUANTITY_CHOICES, QUANTITY_WEIGHTS)
    channel_picker = WeightedPicker(CHANNELS, CHANNEL_WEIGHTS)
    method_picker = WeightedPicker(PAYMENT_METHODS, PAYMENT_METHOD_WEIGHTS)

    orders: list[tuple] = []
    payments: list[tuple] = []
    order_id = 0
    payment_id = 0
    total_days = settings.days

    # days + 1 because the window starts at midnight: without the final partial
    # day the newest order would be from yesterday, and a freshness check on a
    # clean baseline would report the source as stalled.
    for day_offset in range(total_days + 1):
        day_start = window_start + timedelta(days=day_offset)
        # Gentle growth across the window plus weekday shape plus daily jitter.
        growth = 1.0 + 0.35 * (day_offset / max(total_days - 1, 1))
        factor = WEEKDAY_FACTORS[day_start.weekday()] * growth * rng.uniform(0.90, 1.10)
        day_orders = max(1, int(settings.orders_per_day * factor))

        for _ in range(day_orders):
            ordered_at = day_start + timedelta(
                hours=hour_picker.pick(rng), minutes=rng.randint(0, 59), seconds=rng.randint(0, 59)
            )
            if ordered_at > window_end:
                continue

            order_id += 1
            product_id = product_picker.pick(rng)
            unit_price = product_prices[product_id]
            quantity = quantity_picker.pick(rng)
            gross = _money(unit_price * quantity)
            discount = (
                _money(gross * Decimal(str(rng.uniform(0.05, 0.18))))
                if rng.random() < 0.18
                else Decimal("0.00")
            )
            total = _money(gross - discount)
            age_days = (window_end - ordered_at).total_seconds() / 86400
            status = _status_for_age(rng, age_days)
            # Replication lag on the healthy baseline is seconds, never days.
            ingested_at = min(ordered_at + timedelta(seconds=rng.randint(2, 240)), window_end)

            orders.append(
                (
                    order_id,
                    customer_picker.pick(rng),
                    product_id,
                    quantity,
                    unit_price,
                    discount,
                    total,
                    status,
                    channel_picker.pick(rng),
                    ordered_at,
                    ordered_at,
                    ingested_at,
                )
            )

            if status in PAID_STATUSES or status in REFUNDED_STATUSES:
                payment_id += 1
                paid_at = min(ordered_at + timedelta(minutes=rng.randint(1, 90)), window_end)
                payments.append(
                    (
                        payment_id,
                        order_id,
                        total,  # the seam: payment matches the order to the cent
                        method_picker.pick(rng),
                        "refunded" if status in REFUNDED_STATUSES else "captured",
                        paid_at,
                        min(paid_at + timedelta(seconds=rng.randint(2, 180)), window_end),
                    )
                )

    return orders, payments


def _copy_rows(conn: psycopg.Connection, table: str, columns: tuple[str, ...], rows: list[tuple]) -> None:
    column_list = ", ".join(columns)
    with conn.cursor() as cur:
        with cur.copy(f"COPY public.{table} ({column_list}) FROM STDIN") as copy:
            for row in rows:
                copy.write_row(row)


def run_seed(settings: Settings, progress=None) -> SeedResult:
    rng = random.Random(settings.seed)
    window_end = datetime.now(timezone.utc).replace(microsecond=0)
    window_start = (window_end - timedelta(days=settings.days)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    def step(message: str) -> None:
        if progress is not None:
            progress(message)

    with admin_connection(settings) as conn:
        step("repairing schema and clearing previous data")
        _repair_schema(conn)
        _truncate(conn)

        step(f"generating {settings.customers:,} customers")
        customers = _generate_customers(rng, settings.customers, window_end)
        _copy_rows(
            conn,
            "customers",
            ("customer_id", "full_name", "email", "country", "city", "segment",
             "signup_date", "is_active", "created_at", "updated_at", "ingested_at"),
            customers,
        )

        step(f"generating {settings.products:,} products")
        products = _generate_products(rng, settings.products, window_end)
        _copy_rows(
            conn,
            "products",
            ("product_id", "sku", "product_name", "category", "price", "cost",
             "is_active", "created_at", "updated_at", "ingested_at"),
            products,
        )

        step(f"generating {settings.days} days of orders and payments")
        orders, payments = _generate_orders_and_payments(
            rng, settings, products, window_start, window_end
        )

        step(f"loading {len(orders):,} orders")
        _copy_rows(
            conn,
            "orders",
            ("order_id", "customer_id", "product_id", "quantity", "unit_price",
             "discount", "total_amount", "status", "channel", "ordered_at",
             "updated_at", "ingested_at"),
            orders,
        )

        step(f"loading {len(payments):,} payments")
        _copy_rows(
            conn,
            "payments",
            ("payment_id", "order_id", "amount", "method", "status", "paid_at", "ingested_at"),
            payments,
        )

        step("analyzing tables")
        conn.commit()
        with conn.cursor() as cur:
            cur.execute("ANALYZE public.customers")
            cur.execute("ANALYZE public.products")
            cur.execute("ANALYZE public.orders")
            cur.execute("ANALYZE public.payments")
        conn.commit()

        return SeedResult(
            customers=len(customers),
            products=len(products),
            orders=len(orders),
            payments=len(payments),
            window_start=window_start,
            window_end=window_end,
        )


def assert_baseline_is_clean(settings: Settings) -> list[str]:
    """Prove the freshly seeded database contains no incident before injection.

    If any of these fail, a student's detector would find real defects that the
    answer key never recorded, and the Day 4 score would punish them for being
    right. Run as part of `make seed`.
    """
    checks = {
        "orphan orders (customer_id not in customers)": """
            SELECT count(*) FROM public.orders o
            LEFT JOIN public.customers c ON c.customer_id = o.customer_id
            WHERE c.customer_id IS NULL
        """,
        "orphan payments (order_id not in orders)": """
            SELECT count(*) FROM public.payments p
            LEFT JOIN public.orders o ON o.order_id = p.order_id
            WHERE o.order_id IS NULL
        """,
        "negative or zero prices": "SELECT count(*) FROM public.products WHERE price <= 0",
        "invalid quantities": "SELECT count(*) FROM public.orders WHERE quantity <= 0",
        "broken payment seam": """
            SELECT count(*) FROM public.payments p
            JOIN public.orders o ON o.order_id = p.order_id
            WHERE p.amount <> o.total_amount
        """,
        "ingest lag over 1 hour": """
            SELECT count(*) FROM public.orders
            WHERE ingested_at - ordered_at > interval '1 hour'
        """,
        "timestamps in the future": """
            SELECT (SELECT count(*) FROM public.orders WHERE ordered_at > now() OR ingested_at > now())
                 + (SELECT count(*) FROM public.customers WHERE created_at > now())
                 + (SELECT count(*) FROM public.payments WHERE paid_at > now())
        """,
        "orders source already stale (no order in the last 6 hours)": """
            SELECT CASE WHEN max(ordered_at) < now() - interval '6 hours' THEN 1 ELSE 0 END
            FROM public.orders
        """,
        "payments source already stale (no payment in the last 6 hours)": """
            SELECT CASE WHEN max(paid_at) < now() - interval '6 hours' THEN 1 ELSE 0 END
            FROM public.payments
        """,
    }

    failures: list[str] = []
    with admin_connection(settings) as conn:
        for label, sql in checks.items():
            row = fetch_one(conn, sql)
            count = row[0] if row else 0
            if count:
                failures.append(f"{label}: {count:,}")
    return failures
