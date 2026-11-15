"""
Portfolio configuration — risk tiers, expanded 15-ETF universe, commission schedule,
currency settings.

Asset universe spans: US large-cap, global, sectors (tech, financials, energy,
healthcare), international developed & emerging, small-cap, REITs, TIPS, long
treasury, broad bond, gold, and broad commodities.
"""

# ── Account & Currency ───────────────────────────────────────────────
TOTAL_ILS = 150_000
USD_ILS_RATE = 3.2066  # updated from IBKR live quote
TOTAL_USD = TOTAL_ILS / USD_ILS_RATE  # ~$46,775

# IBKR margin loan rates (approximate, tiered)
IBKR_MARGIN_RATES = {
    "USD": {0: 6.83, 100_000: 6.33, 1_000_000: 5.83},
    "ILS": {0: 7.198, 100_000: 6.698, 1_000_000: 6.198},
}

# IBKR commission schedule (USD, tiered pricing)
COMMISSIONS = {
    "US_STK": {"per_share": 0.005, "min": 1.00, "max_pct": 0.005},
    "US_ETF": {"per_share": 0.005, "min": 1.00, "max_pct": 0.005},
    "US_OPT": {"per_contract": 0.65, "min": 1.00},
    "FOREX":  {"per_trade_bps": 0.2, "min": 2.00},
    "BOND":   {"per_face_value_bps": 0.1, "min": 5.00},
}

# ── Asset Universe (15 ETFs) ────────────────────────────────────────
# {ticker: (contract_id, asset_class, description)}
ASSET_UNIVERSE = {
    # Core equity
    "SPY":  (756733,     "equity_us_large",     "S&P 500 ETF"),
    "VT":   (52197301,   "equity_global",       "Vanguard Total World Stock"),
    # Sectors
    "XLK":  (4215230,    "sector_technology",   "Technology Select Sector SPDR"),
    "XLF":  (4215220,    "sector_financials",   "Financial Select Sector SPDR"),
    "XLE":  (4215217,    "sector_energy",       "Energy Select Sector SPDR"),
    "XLV":  (4215205,    "sector_healthcare",   "Health Care Select Sector SPDR"),
    # International
    "EFA":  (13002510,   "equity_intl_dev",     "iShares MSCI EAFE (Developed ex-US)"),
    "EEM":  (6604766,    "equity_intl_em",      "iShares MSCI Emerging Markets"),
    # Small-cap
    "IWM":  (9579970,    "equity_us_small",     "iShares Russell 2000"),
    # Fixed income
    "BND":  (43645828,   "bond_us_total",       "Vanguard Total Bond Market"),
    "TLT":  (15547841,   "bond_us_long",        "iShares 20+ Year Treasury"),
    "TIP":  (26787475,   "bond_tips",           "iShares TIPS Bond ETF"),
    # Real assets
    "GLD":  (51529211,   "commodity_gold",      "SPDR Gold Shares"),
    "VNQ":  (31230302,   "reit",                "Vanguard Real Estate ETF"),
    "DBC":  (319355208,  "commodity_broad",     "Invesco DB Commodity Index"),
    # Existing positions (not in allocation model, tracked separately)
    "NVDA": (4815747,    "equity_us_tech",      "NVIDIA Corp"),
    "SNDK": (760250490,  "equity_us_tech",      "Western Digital / SanDisk"),
}

# Tickers in the allocation model (excludes individual stock positions)
ALLOCATION_TICKERS = [
    "SPY", "VT", "XLK", "XLF", "XLE", "XLV",
    "EFA", "EEM", "IWM",
    "BND", "TLT", "TIP",
    "GLD", "VNQ", "DBC",
]

# ── Risk Tiers ───────────────────────────────────────────────────────
# Direct ticker-based weights. Weights (including cash) sum to 1.0.
# Designed for broad diversification across asset classes, sectors,
# geographies, and real assets per Brinson-Hood (1986), Ang (2014).

RISK_TIERS = {
    "conservative": {
        "description": "Capital preservation, low volatility, income focus",
        "target_vol": 0.06,
        "max_leverage": 1.0,
        "allocation": {
            # Equities 20%
            "SPY": 0.10, "EFA": 0.05, "XLV": 0.05,
            # Fixed income 45%
            "BND": 0.25, "TLT": 0.10, "TIP": 0.10,
            # Real assets 20%
            "GLD": 0.08, "VNQ": 0.07, "DBC": 0.05,
            # Cash 15%
            "cash": 0.15,
        },
        "hedge_ratio": 0.20,
    },
    "moderate": {
        "description": "Balanced growth and income, moderate drawdowns",
        "target_vol": 0.12,
        "max_leverage": 1.0,
        "allocation": {
            # Equities 43%
            "SPY": 0.15, "VT": 0.08, "EFA": 0.05, "IWM": 0.05,
            "XLK": 0.05, "XLF": 0.03, "XLE": 0.02,
            # Fixed income 22%
            "BND": 0.12, "TLT": 0.05, "TIP": 0.05,
            # Real assets 25%
            "GLD": 0.08, "VNQ": 0.07, "DBC": 0.05, "XLV": 0.05,
            # Cash 10%
            "cash": 0.10,
        },
        "hedge_ratio": 0.10,
    },
    "aggressive": {
        "description": "Maximum growth, tolerates large drawdowns",
        "target_vol": 0.20,
        "max_leverage": 1.3,
        "allocation": {
            # Equities 58%
            "SPY": 0.15, "VT": 0.10, "EFA": 0.05, "EEM": 0.05,
            "IWM": 0.08, "XLK": 0.10, "XLE": 0.05,
            # Fixed income 9%
            "BND": 0.05, "TIP": 0.04,
            # Real assets 23%
            "GLD": 0.07, "VNQ": 0.05, "DBC": 0.08, "XLF": 0.03,
            # Cash 10%
            "cash": 0.10,
        },
        "hedge_ratio": 0.05,
    },
}

# ── Backtest Parameters ──────────────────────────────────────────────
BACKTEST_START = "2021-11-15"
BACKTEST_END = "2026-11-14"
REBALANCE_FREQUENCY = "quarterly"
RISK_FREE_RATE = 0.045  # ~4.5% USD risk-free (T-bills)
