-- NordTrail Gear — SQLite enterprise-style schema (CAD)
-- Run via seed_database.py or: sqlite3 nordtrail.db < schema.sql

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS clients (
    client_id           TEXT PRIMARY KEY,
    first_name          TEXT NOT NULL,
    last_name           TEXT NOT NULL,
    email               TEXT NOT NULL UNIQUE,
    phone               TEXT,
    province            TEXT NOT NULL,
    country             TEXT NOT NULL DEFAULT 'CA',
    loyalty_level       TEXT NOT NULL CHECK (loyalty_level IN ('standard', 'silver', 'gold')),
    preferred_language  TEXT NOT NULL DEFAULT 'fr',
    created_at          TEXT NOT NULL,
    risk_flags          TEXT NOT NULL DEFAULT '[]',
    notes               TEXT
);

CREATE TABLE IF NOT EXISTS products (
    product_id          TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    category            TEXT NOT NULL,
    price               REAL NOT NULL,
    currency            TEXT NOT NULL DEFAULT 'CAD',
    available_sizes     TEXT,
    colors              TEXT,
    warranty_months     INTEGER NOT NULL DEFAULT 24,
    weight_g            INTEGER,
    recommended_use     TEXT,
    waterproof          TEXT,
    return_eligible     INTEGER NOT NULL DEFAULT 1,
    is_active           INTEGER NOT NULL DEFAULT 1,
    notes               TEXT
);

CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id        TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    city                TEXT NOT NULL,
    province            TEXT NOT NULL,
    country             TEXT NOT NULL DEFAULT 'CA',
    is_active           INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS inventory (
    product_id          TEXT NOT NULL REFERENCES products(product_id),
    warehouse_id        TEXT NOT NULL REFERENCES warehouses(warehouse_id),
    quantity            INTEGER NOT NULL CHECK (quantity >= 0),
    reorder_threshold   INTEGER NOT NULL DEFAULT 5,
    PRIMARY KEY (product_id, warehouse_id)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id            TEXT PRIMARY KEY,
    client_id           TEXT NOT NULL REFERENCES clients(client_id),
    status              TEXT NOT NULL CHECK (status IN (
        'en_attente', 'en_preparation', 'expediee',
        'livree', 'annulee', 'retour_demande'
    )),
    order_date          TEXT NOT NULL,
    payment_status      TEXT NOT NULL DEFAULT 'paye',
    shipping_province   TEXT NOT NULL,
    shipping_method     TEXT NOT NULL,
    tracking_number     TEXT,
    delivery_date       TEXT,
    subtotal_amount     REAL NOT NULL,
    shipping_amount     REAL NOT NULL DEFAULT 0,
    tax_amount          REAL NOT NULL DEFAULT 0,
    total_amount        REAL NOT NULL,
    currency            TEXT NOT NULL DEFAULT 'CAD',
    return_window_end   TEXT,
    notes               TEXT
);

CREATE TABLE IF NOT EXISTS order_items (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id            TEXT NOT NULL REFERENCES orders(order_id),
    product_id          TEXT NOT NULL REFERENCES products(product_id),
    size                TEXT NOT NULL,
    quantity            INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    unit_price          REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS returns (
    return_id           TEXT PRIMARY KEY,
    order_id            TEXT NOT NULL REFERENCES orders(order_id),
    product_id          TEXT NOT NULL REFERENCES products(product_id),
    reason              TEXT NOT NULL,
    status              TEXT NOT NULL CHECK (status IN (
        'pending', 'approved', 'rejected', 'refunded'
    )),
    requested_at        TEXT NOT NULL,
    resolved_at         TEXT,
    refund_amount       REAL,
    notes               TEXT
);

CREATE TABLE IF NOT EXISTS coupons (
    code                TEXT PRIMARY KEY,
    description         TEXT,
    discount_percent    REAL,
    discount_fixed      REAL,
    min_order_amount    REAL NOT NULL DEFAULT 0,
    valid_from          TEXT NOT NULL,
    valid_until         TEXT NOT NULL,
    applies_to_sale     INTEGER NOT NULL DEFAULT 0,
    loyalty_required    TEXT,
    is_active           INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_clients_email ON clients(email);
CREATE INDEX IF NOT EXISTS idx_orders_client ON orders(client_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_returns_order ON returns(order_id);
