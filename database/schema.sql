-- ================================================
-- YALANAMCHOU — Structure de la base de données
-- ================================================
-- À exécuter une seule fois pour créer les tables

-- Table des utilisateurs (passagers + chauffeurs + admins)
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    phone       TEXT    UNIQUE NOT NULL,
    name        TEXT    NOT NULL,
    role        TEXT    NOT NULL DEFAULT 'passager', -- 'passager' | 'chauffeur' | 'admin'
    password    TEXT,
    is_active   INTEGER DEFAULT 1,
    created_at  TEXT    DEFAULT (datetime('now'))
);

-- Informations spécifiques aux chauffeurs
CREATE TABLE IF NOT EXISTS drivers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(id),
    vehicle_type    TEXT    DEFAULT 'taxi',  -- 'moto' | 'taxi' | 'premium'
    vehicle_brand   TEXT,
    vehicle_color   TEXT,
    vehicle_plate   TEXT    UNIQUE,
    vehicle_year    INTEGER,
    license_number  TEXT,
    is_verified     INTEGER DEFAULT 0,
    is_online       INTEGER DEFAULT 0,
    current_lat     REAL    DEFAULT 12.1048,  -- N'Djaména par défaut
    current_lng     REAL    DEFAULT 15.0445,
    last_seen       TEXT,
    total_rides     INTEGER DEFAULT 0,
    total_earnings  INTEGER DEFAULT 0,
    average_rating  REAL    DEFAULT 5.0,
    subscription    TEXT    DEFAULT 'gratuit'
);

-- Courses
CREATE TABLE IF NOT EXISTS rides (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    passenger_id    INTEGER NOT NULL REFERENCES users(id),
    driver_id       INTEGER REFERENCES users(id),
    pickup_lat      REAL    NOT NULL,
    pickup_lng      REAL    NOT NULL,
    pickup_address  TEXT    NOT NULL,
    dropoff_lat     REAL    NOT NULL,
    dropoff_lng     REAL    NOT NULL,
    dropoff_address TEXT    NOT NULL,
    vehicle_type    TEXT    DEFAULT 'taxi',
    distance_km     REAL,
    duration_min    INTEGER,
    price_fcfa      INTEGER,
    commission_fcfa INTEGER,
    status          TEXT    DEFAULT 'pending',
    passenger_rating INTEGER,
    driver_rating    INTEGER,
    payment_method  TEXT    DEFAULT 'cash',
    requested_at    TEXT    DEFAULT (datetime('now')),
    accepted_at     TEXT,
    started_at      TEXT,
    completed_at    TEXT
);

-- Paiements
CREATE TABLE IF NOT EXISTS payments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ride_id         INTEGER NOT NULL REFERENCES rides(id),
    user_id         INTEGER NOT NULL REFERENCES users(id),
    amount_fcfa     INTEGER NOT NULL,
    commission_fcfa INTEGER,
    method          TEXT    DEFAULT 'cash',
    phone_number    TEXT,
    status          TEXT    DEFAULT 'pending',  -- 'pending' | 'success' | 'failed'
    transaction_id  TEXT,
    initiated_at    TEXT    DEFAULT (datetime('now')),
    completed_at    TEXT
);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    type        TEXT,   -- 'ride_accepted' | 'driver_arrived' | 'payment_confirmed'
    title       TEXT,
    message     TEXT,
    is_read     INTEGER DEFAULT 0,
    created_at  TEXT    DEFAULT (datetime('now'))
);

-- ===== DONNÉES DE TEST =====
INSERT OR IGNORE INTO users (id, phone, name, role) VALUES
    (1, '+23566100001', 'Amina Mahamat', 'passager'),
    (2, '+23566100002', 'Ibrahim Hassan', 'chauffeur'),
    (3, '+23566100003', 'Admin Yalanam', 'admin');

INSERT OR IGNORE INTO drivers (user_id, vehicle_type, vehicle_brand, vehicle_color, vehicle_plate, is_verified, is_online) VALUES
    (2, 'taxi', 'Toyota Corolla', 'Jaune', 'TD-2847-A', 1, 1);

-- ===== INDEX POUR LES PERFORMANCES =====
CREATE INDEX IF NOT EXISTS idx_rides_passenger ON rides(passenger_id);
CREATE INDEX IF NOT EXISTS idx_rides_driver ON rides(driver_id);
CREATE INDEX IF NOT EXISTS idx_rides_status ON rides(status);
CREATE INDEX IF NOT EXISTS idx_drivers_online ON drivers(is_online, vehicle_type);
