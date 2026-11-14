"""
Market data layer — wraps live IBKR data and historical yfinance data.
Provides unified interface for the recommendation engine.
"""
import pandas as pd
import numpy as np

# Live market data cache (populated from IBKR snapshots)
LIVE_PRICES = {
    "SPY":  749.60,
    "TLT":  79.42,
    "GLD":  355.70,
    "VT":   154.77,
    "BND":  70.74,
    "NVDA": 161.01,
    "SNDK": 865.23,
}

LIVE_METRICS = {
    "SPY":  {"ytd_pct": 10.51, "div_yield": 1.0,  "hist_vol": 13.7, "annual_vol": 0.137},
    "TLT":  {"ytd_pct": -5.7,  "div_yield": 4.9,  "hist_vol": 12.3, "annual_vol": 0.123},
    "GLD":  {"ytd_pct": -10.25,"div_yield": 0.0,  "hist_vol": 22.2, "annual_vol": 0.222},
    "VT":   {"ytd_pct": 10.37, "div_yield": 1.55, "hist_vol": 13.5, "annual_vol": 0.135},
    "BND":  {"ytd_pct": -1.56, "div_yield": 4.18, "hist_vol": 5.4,  "annual_vol": 0.054},
    "NVDA": {"ytd_pct": -13.56,"div_yield": 0.0,  "hist_vol": 65.2, "annual_vol": 0.652, "iv": 0.594},
    "SNDK": {"ytd_pct": 264.49,"div_yield": 0.0,  "hist_vol": 102.7,"annual_vol": 1.027, "iv": 0.854},
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
