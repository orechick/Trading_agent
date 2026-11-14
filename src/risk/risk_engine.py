"""
Risk analytics — portfolio volatility, VaR, max drawdown, Sharpe, Sortino.
"""
import numpy as np
import pandas as pd
from config.portfolio_config import RISK_FREE_RATE


def portfolio_volatility(weights: np.ndarray, cov_matrix: np.ndarray) -> float:
    """Annualized portfolio volatility from weights and covariance matrix."""
    return float(np.sqrt(weights @ cov_matrix @ weights))


def portfolio_return(weights: np.ndarray, expected_returns: np.ndarray) -> float:
    return float(weights @ expected_returns)


def sharpe_ratio(ret: float, vol: float, rf: float = RISK_FREE_RATE) -> float:
    if vol == 0:
        return 0.0
    return (ret - rf) / vol


def sortino_ratio(returns: pd.Series, rf: float = RISK_FREE_RATE) -> float:
    excess = returns - rf / 252
    downside = excess[excess < 0]
    if len(downside) == 0 or downside.std() == 0:
        return 0.0
    return float(excess.mean() * np.sqrt(252) / (downside.std() * np.sqrt(252)))


def value_at_risk(returns: pd.Series, confidence: float = 0.95) -> float:
    """Historical VaR at given confidence level (daily)."""
    return float(np.percentile(returns, (1 - confidence) * 100))


def conditional_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """Expected Shortfall / CVaR."""
    var = value_at_risk(returns, confidence)
    return float(returns[returns <= var].mean())


def max_drawdown(cumulative_returns: pd.Series) -> float:
    peak = cumulative_returns.cummax()
    drawdown = (cumulative_returns - peak) / peak
    return float(drawdown.min())


def risk_report(
    daily_returns: pd.Series,
    annual_return: float,
    annual_vol: float,
) -> dict:
    """Comprehensive risk report for a return series."""
    cum_ret = (1 + daily_returns).cumprod()
    return {
        "annual_return_pct": annual_return * 100,
        "annual_volatility_pct": annual_vol * 100,
        "sharpe_ratio": sharpe_ratio(annual_return, annual_vol),
        "sortino_ratio": sortino_ratio(daily_returns),
        "var_95_daily_pct": value_at_risk(daily_returns) * 100,
        "cvar_95_daily_pct": conditional_var(daily_returns) * 100,
        "max_drawdown_pct": max_drawdown(cum_ret) * 100,
        "calmar_ratio": (
            annual_return / abs(max_drawdown(cum_ret))
            if max_drawdown(cum_ret) != 0 else 0
        ),
        "positive_days_pct": (daily_returns > 0).mean() * 100,
    }


def position_risk_contribution(
    weights: np.ndarray,
    cov_matrix: np.ndarray,
    tickers: list[str],
) -> dict[str, float]:
    """Marginal and % risk contribution per position."""
    port_vol = portfolio_volatility(weights, cov_matrix)
    marginal = cov_matrix @ weights / port_vol
    contrib = weights * marginal
    pct_contrib = contrib / port_vol

    return {
        ticker: {
            "weight_pct": w * 100,
            "marginal_risk": float(m),
            "risk_contribution": float(c),
            "pct_of_total_risk": float(p) * 100,
        }
        for ticker, w, m, c, p in zip(tickers, weights, marginal, contrib, pct_contrib)
    }
