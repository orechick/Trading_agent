"""
Portfolio configuration — risk tiers, asset universe, commission schedule, currency settings.
"""

# ── Account & Currency ───────────────────────────────────────────────
TOTAL_ILS = 150_000
USD_ILS_RATE = 3.2066  # updated from IBKR live quote
TOTAL_USD = TOTAL_ILS / USD_ILS_RATE  # ~$46,775

# IBKR margin loan rates (approximate, tiered)
IBKR_MARGIN_RATES = {
    "USD": {0: 6.83, 100_000: 6.33, 1_000_000: 5.83},      # BM + spread
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

# ── Asset Universe ───────────────────────────────────────────────────
# {ticker: (contract_id, asset_class, description)}
ASSET_UNIVERSE = {
    # Core equity
    "SPY":  (756733,    "equity_us_large",    "S&P 500 ETF"),
    "VT":   (52197301,  "equity_global",      "Vanguard Total World Stock"),
    "VTI":  (12340041,  "equity_us_total",    "Vanguard Total US Stock Market"),
    "SPYV": (45540652,  "equity_us_value",    "S&P 500 Value ETF"),
    "SPYG": (45540799,  "equity_us_growth",   "S&P 500 Growth ETF"),
    # Fixed income
    "BND":  (43645828,  "bond_us_total",      "Vanguard Total Bond Market"),
    "TLT":  (15547841,  "bond_us_long",       "iShares 20+ Year Treasury"),
    "BNDX": (128835017, "bond_intl",          "Vanguard Total International Bond"),
    "VWOB": (128835014, "bond_em",            "Vanguard Emerging Markets Gov Bond"),
    # Commodities / Real assets
    "GLD":  (51529211,  "commodity_gold",     "SPDR Gold Shares"),
    "GLDM": (543859629, "commodity_gold_mini", "SPDR Gold MiniShares (lower cost)"),
    # Existing positions
    "NVDA": (4815747,   "equity_us_tech",     "NVIDIA Corp"),
    "SNDK": (760250490, "equity_us_tech",     "Western Digital / SanDisk"),
}

# ── Risk Tiers ───────────────────────────────────────────────────────
# Each tier defines target allocation weights by asset class bucket.
# Weights must sum to 1.0
RISK_TIERS = {
    "conservative": {
        "description": "Capital preservation, low volatility, income focus",
        "target_vol": 0.06,
        "max_leverage": 1.0,
        "allocation": {
            "equity_us_large":  0.15,
            "equity_global":    0.05,
            "equity_us_value":  0.05,
            "bond_us_total":    0.35,
            "bond_us_long":     0.10,
            "bond_intl":        0.10,
            "commodity_gold":   0.10,
            "cash":             0.10,
        },
        "hedge_ratio": 0.20,  # % of equity hedged with puts
    },
    "moderate": {
        "description": "Balanced growth and income, moderate drawdowns",
        "target_vol": 0.12,
        "max_leverage": 1.0,
        "allocation": {
            "equity_us_large":  0.25,
            "equity_global":    0.10,
            "equity_us_growth": 0.05,
            "equity_us_value":  0.05,
            "bond_us_total":    0.20,
            "bond_us_long":     0.05,
            "bond_intl":        0.05,
            "bond_em":          0.05,
            "commodity_gold":   0.10,
            "cash":             0.10,
        },
        "hedge_ratio": 0.10,
    },
    "aggressive": {
        "description": "Maximum growth, tolerates large drawdowns",
        "target_vol": 0.20,
        "max_leverage": 1.3,
        "allocation": {
            "equity_us_large":  0.30,
            "equity_global":    0.15,
            "equity_us_growth": 0.15,
            "equity_us_total":  0.10,
            "bond_us_total":    0.05,
            "bond_em":          0.05,
            "commodity_gold":   0.10,
            "cash":             0.10,
        },
        "hedge_ratio": 0.05,
    },
}

# Map asset class buckets to preferred ticker
ASSET_CLASS_TO_TICKER = {
    "equity_us_large":  "SPY",
    "equity_global":    "VT",
    "equity_us_total":  "VTI",
    "equity_us_value":  "SPYV",
    "equity_us_growth": "SPYG",
    "equity_us_tech":   "NVDA",
    "bond_us_total":    "BND",
    "bond_us_long":     "TLT",
    "bond_intl":        "BNDX",
    "bond_em":          "VWOB",
    "commodity_gold":   "GLD",
    "commodity_gold_mini": "GLDM",
    "cash":             None,  # held as USD/ILS cash
}

# ── Backtest Parameters ──────────────────────────────────────────────
BACKTEST_START = "2021-11-15"
BACKTEST_END = "2026-11-14"
REBALANCE_FREQUENCY = "quarterly"  # monthly, quarterly, annual
RISK_FREE_RATE = 0.045  # ~4.5% USD risk-free (T-bills)
