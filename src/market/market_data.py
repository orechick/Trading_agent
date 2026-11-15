"""
Market data layer — wraps live IBKR data and historical price cache.
Provides unified interface for the recommendation engine.
"""
import pandas as pd
import numpy as np

LIVE_PRICES = {
    "SPY":  754.37,
    "VT":   155.30,
    "XLK":  170.28,
    "XLF":  58.68,
    "XLE":  64.96,
    "XLV":  188.85,
    "EFA":  104.17,
    "EEM":  60.92,
    "IWM":  277.54,
    "BND":  70.56,
    "TLT":  79.38,
    "TIP":  104.61,
    "GLD":  355.45,
    "VNQ":  96.47,
    "DBC":  30.79,
    # Existing positions (not in allocation model)
    "NVDA": 161.01,
    "SNDK": 865.23,
}

LIVE_METRICS = {
    "SPY":  {"ytd_pct": 10.51, "div_yield": 1.0,  "hist_vol": 13.7, "annual_vol": 0.137},
    "VT":   {"ytd_pct": 10.37, "div_yield": 1.55, "hist_vol": 13.5, "annual_vol": 0.135},
    "XLK":  {"ytd_pct": 12.8,  "div_yield": 0.5,  "hist_vol": 18.2, "annual_vol": 0.182},
    "XLF":  {"ytd_pct": 8.5,   "div_yield": 1.6,  "hist_vol": 16.1, "annual_vol": 0.161},
    "XLE":  {"ytd_pct": -3.2,  "div_yield": 3.2,  "hist_vol": 22.5, "annual_vol": 0.225},
    "XLV":  {"ytd_pct": 5.1,   "div_yield": 1.3,  "hist_vol": 14.0, "annual_vol": 0.140},
    "EFA":  {"ytd_pct": 9.8,   "div_yield": 2.8,  "hist_vol": 14.5, "annual_vol": 0.145},
    "EEM":  {"ytd_pct": 7.2,   "div_yield": 2.1,  "hist_vol": 17.8, "annual_vol": 0.178},
    "IWM":  {"ytd_pct": 6.0,   "div_yield": 1.2,  "hist_vol": 19.5, "annual_vol": 0.195},
    "BND":  {"ytd_pct": -1.56, "div_yield": 4.18, "hist_vol": 5.4,  "annual_vol": 0.054},
    "TLT":  {"ytd_pct": -5.7,  "div_yield": 4.9,  "hist_vol": 12.3, "annual_vol": 0.123},
    "TIP":  {"ytd_pct": 0.8,   "div_yield": 3.5,  "hist_vol": 5.8,  "annual_vol": 0.058},
    "GLD":  {"ytd_pct": -10.25, "div_yield": 0.0, "hist_vol": 22.2, "annual_vol": 0.222},
    "VNQ":  {"ytd_pct": 3.5,   "div_yield": 3.6,  "hist_vol": 17.0, "annual_vol": 0.170},
    "DBC":  {"ytd_pct": -5.0,  "div_yield": 0.0,  "hist_vol": 15.5, "annual_vol": 0.155},
    "NVDA": {"ytd_pct": -13.56, "div_yield": 0.0, "hist_vol": 65.2, "annual_vol": 0.652, "iv": 0.594},
    "SNDK": {"ytd_pct": 264.49, "div_yield": 0.0, "hist_vol": 102.7, "annual_vol": 1.027, "iv": 0.854},
}

FX_RATES = {
    "USD_ILS": 3.2066,
}


def get_price(ticker: str) -> float:
    return LIVE_PRICES.get(ticker, 0.0)


def get_all_prices() -> dict[str, float]:
    return LIVE_PRICES.copy()


def get_metrics(ticker: str) -> dict:
    return LIVE_METRICS.get(ticker, {})


def get_fx_rate(pair: str = "USD_ILS") -> float:
    return FX_RATES.get(pair, 1.0)


def correlation_matrix_from_returns(returns: pd.DataFrame) -> pd.DataFrame:
    return returns.corr()


def covariance_matrix_from_returns(returns: pd.DataFrame) -> pd.DataFrame:
    return returns.cov() * 252
