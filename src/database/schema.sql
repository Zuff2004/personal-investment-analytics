CREATE TABLE IF NOT EXISTS assets (
    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL UNIQUE,
    name TEXT,
    asset_type TEXT NOT NULL,
    currency TEXT NOT NULL,
    country TEXT,
    exchange TEXT,
    sector TEXT
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    broker_name TEXT NOT NULL,
    account_name TEXT NOT NULL,
    currency TEXT NOT NULL,
    country TEXT
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    account_id INTEGER NOT NULL,
    asset_id INTEGER,
    transaction_type TEXT NOT NULL,
    quantity REAL,
    price REAL,
    gross_value REAL,
    fees REAL DEFAULT 0,
    taxes REAL DEFAULT 0,
    net_value REAL,
    currency TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

CREATE TABLE IF NOT EXISTS income_events (
    income_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    account_id INTEGER NOT NULL,
    asset_id INTEGER NOT NULL,
    income_type TEXT NOT NULL,
    gross_amount REAL NOT NULL,
    tax_withheld REAL DEFAULT 0,
    net_amount REAL NOT NULL,
    currency TEXT NOT NULL,
    related_quantity REAL,
    notes TEXT,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

CREATE TABLE IF NOT EXISTS strategies (
    strategy_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    strategy_type TEXT,
    asset_universe TEXT,
    active INTEGER DEFAULT 1,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS signals (
    signal_id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    asset_id INTEGER NOT NULL,
    signal TEXT NOT NULL,
    signal_strength REAL,
    suggested_action TEXT,
    target_weight REAL,
    executed INTEGER DEFAULT 0,
    related_trade_id INTEGER,
    notes TEXT,
    FOREIGN KEY (strategy_id) REFERENCES strategies(strategy_id),
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

CREATE TABLE IF NOT EXISTS trades (
    trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id INTEGER,
    asset_id INTEGER NOT NULL,
    open_date TEXT,
    close_date TEXT,
    status TEXT NOT NULL,
    thesis TEXT,
    realized_pnl REAL,
    return_pct REAL,
    notes TEXT,
    FOREIGN KEY (strategy_id) REFERENCES strategies(strategy_id),
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

CREATE TABLE IF NOT EXISTS trade_legs (
    trade_leg_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id INTEGER NOT NULL,
    transaction_id INTEGER NOT NULL,
    side TEXT NOT NULL,
    quantity REAL NOT NULL,
    price REAL NOT NULL,
    fees REAL DEFAULT 0,
    FOREIGN KEY (trade_id) REFERENCES trades(trade_id),
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
);
CREATE TABLE IF NOT EXISTS portfolio_rotations (
    rotation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    from_asset_id INTEGER NOT NULL,
    to_asset_id INTEGER NOT NULL,
    strategy_id INTEGER,
    capital_rotated REAL,
    reason TEXT,
    status TEXT DEFAULT 'OPEN',
    notes TEXT,
    FOREIGN KEY (from_asset_id) REFERENCES assets(asset_id),
    FOREIGN KEY (to_asset_id) REFERENCES assets(asset_id),
    FOREIGN KEY (strategy_id) REFERENCES strategies(strategy_id)
);

CREATE TABLE IF NOT EXISTS rotation_legs (
    rotation_leg_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rotation_id INTEGER NOT NULL,
    transaction_id INTEGER NOT NULL,
    leg_type TEXT NOT NULL,
    asset_id INTEGER NOT NULL,
    quantity REAL,
    price REAL,
    value REAL,
    FOREIGN KEY (rotation_id) REFERENCES portfolio_rotations(rotation_id),
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);
CREATE TABLE IF NOT EXISTS realized_gains (
    realized_gain_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sell_transaction_id INTEGER NOT NULL,
    asset_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    quantity_sold REAL NOT NULL,
    proceeds REAL NOT NULL,
    cost_basis REAL NOT NULL,
    fees REAL DEFAULT 0,
    gross_gain REAL NOT NULL,
    net_gain REAL NOT NULL,
    taxable_gain REAL,
    tax_due REAL,
    FOREIGN KEY (sell_transaction_id) REFERENCES transactions(transaction_id),
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

CREATE TABLE IF NOT EXISTS loss_carryforward (
    carryforward_id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    asset_class TEXT NOT NULL,
    opening_loss REAL DEFAULT 0,
    new_loss REAL DEFAULT 0,
    loss_used REAL DEFAULT 0,
    closing_loss REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS market_prices (
    price_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    close_price REAL NOT NULL,
    currency TEXT NOT NULL,
    source TEXT,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id),
    UNIQUE(asset_id, date)
);

CREATE TABLE IF NOT EXISTS backtests (
    backtest_id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    initial_capital REAL,
    benchmark TEXT,
    assumptions TEXT,
    created_at TEXT,
    FOREIGN KEY (strategy_id) REFERENCES strategies(strategy_id)
);

CREATE TABLE IF NOT EXISTS backtest_results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    backtest_id INTEGER NOT NULL,
    total_return REAL,
    annualized_return REAL,
    volatility REAL,
    sharpe_ratio REAL,
    max_drawdown REAL,
    win_rate REAL,
    number_of_trades INTEGER,
    notes TEXT,
    FOREIGN KEY (backtest_id) REFERENCES backtests(backtest_id)
);

CREATE TABLE IF NOT EXISTS reports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL,
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    file_path TEXT,
    created_at TEXT,
    notes TEXT
);
