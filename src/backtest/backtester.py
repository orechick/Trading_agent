"""
Backtesting engine — historical simulation of portfolio strategies with rebalancing.
Uses IBKR price history data (no yfinance dependency).
"""
import numpy as np
import pandas as pd
from datetime import datetime

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config.portfolio_config import RISK_FREE_RATE, REBALANCE_FREQUENCY
from src.risk.risk_engine import risk_report, portfolio_volatility
from src.backtest.ibkr_price_cache import load_weekly_prices


def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change().dropna()


def rebalance_dates(index: pd.DatetimeIndex, frequency: str) -> list[pd.Timestamp]:
    if frequency == "monthly":
        return [g.index[-1] for _, g in pd.Series(index, index=index).groupby(pd.Grouper(freq="ME"))]
    elif frequency == "quarterly":
        return [g.index[-1] for _, g in pd.Series(index, index=index).groupby(pd.Grouper(freq="QE"))]
    elif frequency == "annual":
        return [g.index[-1] for _, g in pd.Series(index, index=index).groupby(pd.Grouper(freq="YE"))]
    return list(index)


def backtest_strategy(
    weights: dict[str, float],
    start: str = "2021-11-15",
    end: str = "2026-11-14",
    initial_capital: float = 46750.0,
    rebal_freq: str = REBALANCE_FREQUENCY,
    commission_per_trade: float = 1.0,
) -> dict:
    tickers = [t for t in weights if t != "CASH" and weights[t] > 0]
    if not tickers:
        return {"error": "No tickers to backtest"}

    all_prices = load_weekly_prices()
    available = [t for t in tickers if t in all_prices.columns]
    if not available:
        return {"error": f"No price data for {tickers}"}

    prices = all_prices[available].dropna()
    if start:
        prices = prices[prices.index >= start]
    if end:
        prices = prices[prices.index <= end]

    if len(prices) < 2:
        return {"error": "Insufficient price data"}

    returns = compute_returns(prices)
    rebal_dates_set = set(rebalance_dates(returns.index, rebal_freq))

    equity_weight = sum(weights.get(t, 0) for t in available)
    cash_weight = weights.get("CASH", 0)
    if equity_weight <= 0:
        return {"error": "Zero equity weight"}
    norm_weights = {t: weights.get(t, 0) / equity_weight * (1 - cash_weight) for t in available}

    portfolio_values = [initial_capital]
    portfolio_returns = []
    n_rebalances = 0
    total_commission = 0
    current_weights = {t: norm_weights[t] for t in available}

    for date in returns.index:
        day_returns = returns.loc[date]
        port_ret = sum(current_weights.get(t, 0) * day_returns.get(t, 0) for t in available)
        new_value = portfolio_values[-1] * (1 + port_ret)

        if date in rebal_dates_set:
            commission = len(available) * commission_per_trade
            new_value -= commission
            total_commission += commission
            current_weights = {t: norm_weights[t] for t in available}
            n_rebalances += 1
        else:
            total = sum(
                current_weights.get(t, 0) * (1 + day_returns.get(t, 0))
                for t in available
            )
            if total > 0:
                current_weights = {
                    t: current_weights.get(t, 0) * (1 + day_returns.get(t, 0)) / total
                    for t in available
                }

        portfolio_values.append(new_value)
        portfolio_returns.append(port_ret)

    equity_curve = pd.Series(portfolio_values[1:], index=returns.index)
    daily_rets = pd.Series(portfolio_returns, index=returns.index)

    total_return = (equity_curve.iloc[-1] / initial_capital) - 1
    years = len(returns) / 52  # weekly data
    annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
    annual_vol = daily_rets.std() * np.sqrt(52)  # weekly to annual

    metrics = risk_report(daily_rets, annual_return, annual_vol)
    metrics.update({
        "total_return_pct": total_return * 100,
        "final_value_usd": equity_curve.iloc[-1],
        "initial_capital_usd": initial_capital,
        "period_years": years,
        "n_rebalances": n_rebalances,
        "total_commission_usd": total_commission,
        "annual_return_pct": annual_return * 100,
        "annual_volatility_pct": annual_vol * 100,
    })

    return {
        "metrics": metrics,
        "equity_curve": equity_curve,
        "weights": weights,
        "tickers": available,
    }


def compare_strategies(
    strategies: dict[str, dict[str, float]],
    start: str = "2021-11-15",
    end: str = "2026-11-14",
    initial_capital: float = 46750.0,
) -> dict:
    results = {}
    for name, weights in strategies.items():
        results[name] = backtest_strategy(weights, start, end, initial_capital)
    return results
