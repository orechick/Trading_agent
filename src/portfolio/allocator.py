"""
Portfolio allocation engine — builds target portfolios per risk tier,
computes trade orders, and handles rebalancing.
"""
import numpy as np
import pandas as pd
from config.portfolio_config import (
    RISK_TIERS, ASSET_CLASS_TO_TICKER, ASSET_UNIVERSE,
    COMMISSIONS, TOTAL_USD, USD_ILS_RATE,
)


def get_target_allocation(risk_tier: str) -> dict[str, float]:
    """Return {ticker: weight} for a risk tier."""
    tier = RISK_TIERS[risk_tier]
    result = {}
    for asset_class, weight in tier["allocation"].items():
        ticker = ASSET_CLASS_TO_TICKER.get(asset_class)
        if ticker and weight > 0:
            result[ticker] = result.get(ticker, 0) + weight
        elif asset_class == "cash":
            result["CASH"] = weight
    return result


def shares_from_weights(
    weights: dict[str, float],
    total_capital: float,
    prices: dict[str, float],
) -> dict[str, dict]:
    """Convert weights to concrete share counts and dollar amounts."""
    positions = {}
    invested = 0.0

    for ticker, weight in weights.items():
        if ticker == "CASH":
            continue
        target_usd = total_capital * weight
        price = prices.get(ticker, 0)
        if price <= 0:
            continue
        shares = int(target_usd / price)
        actual_usd = shares * price
        invested += actual_usd
        positions[ticker] = {
            "target_weight": weight,
            "shares": shares,
            "price": price,
            "market_value": actual_usd,
            "actual_weight": 0,  # filled below
        }

    target_cash_usd = total_capital * weights.get("CASH", 0)
    excess_cash = total_capital - invested - target_cash_usd

    # Redistribute rounding residual: buy more shares where affordable
    if excess_cash > 0:
        candidates = sorted(positions.items(), key=lambda x: x[1]["price"])
        for ticker, pos in candidates:
            price = pos["price"]
            extra = int(excess_cash / price)
            if extra > 0:
                pos["shares"] += extra
                added = extra * price
                pos["market_value"] += added
                invested += added
                excess_cash -= added

    cash_remaining = total_capital - invested
    for ticker in positions:
        positions[ticker]["actual_weight"] = positions[ticker]["market_value"] / total_capital

    positions["CASH"] = {
        "target_weight": weights.get("CASH", 0),
        "shares": 0,
        "price": 1.0,
        "market_value": cash_remaining,
        "actual_weight": cash_remaining / total_capital,
    }
    return positions


def estimate_commission(ticker: str, shares: int, price: float) -> float:
    """Estimate IBKR commission for a stock/ETF trade."""
    schedule = COMMISSIONS["US_ETF"]
    cost = shares * schedule["per_share"]
    cost = max(cost, schedule["min"])
    cost = min(cost, shares * price * schedule["max_pct"])
    return cost


def rebalance_orders(
    current_positions: dict[str, dict],
    target_positions: dict[str, dict],
    prices: dict[str, float],
    threshold_pct: float = 0.02,
) -> list[dict]:
    """
    Generate rebalance orders. Only trades when drift exceeds threshold.
    Returns list of {ticker, action, shares, est_cost, reason}.
    """
    orders = []
    all_tickers = set(list(current_positions.keys()) + list(target_positions.keys()))
    all_tickers.discard("CASH")

    for ticker in all_tickers:
        current = current_positions.get(ticker, {})
        target = target_positions.get(ticker, {})

        current_shares = current.get("shares", 0)
        target_shares = target.get("shares", 0)
        delta = target_shares - current_shares
        price = prices.get(ticker, 0)

        current_weight = current.get("actual_weight", 0)
        target_weight = target.get("target_weight", 0)
        drift = abs(target_weight - current_weight)

        if abs(delta) > 0 and drift > threshold_pct:
            action = "BUY" if delta > 0 else "SELL"
            commission = estimate_commission(ticker, abs(delta), price)
            orders.append({
                "ticker": ticker,
                "action": action,
                "shares": abs(delta),
                "price": price,
                "notional": abs(delta) * price,
                "commission": commission,
                "drift_pct": drift * 100,
                "reason": f"Rebalance: {current_weight*100:.1f}% → {target_weight*100:.1f}%",
            })

    orders.sort(key=lambda x: x["notional"], reverse=True)
    return orders


def build_portfolio_plan(
    risk_tier: str,
    total_capital: float,
    prices: dict[str, float],
    existing_positions: dict[str, dict] | None = None,
) -> dict:
    """
    Build complete portfolio plan: allocation, positions, orders, costs.
    """
    tier_config = RISK_TIERS[risk_tier]
    target_weights = get_target_allocation(risk_tier)
    target_positions = shares_from_weights(target_weights, total_capital, prices)

    orders = []
    if existing_positions:
        orders = rebalance_orders(existing_positions, target_positions, prices)
    else:
        for ticker, pos in target_positions.items():
            if ticker == "CASH" or pos["shares"] == 0:
                continue
            commission = estimate_commission(ticker, pos["shares"], pos["price"])
            orders.append({
                "ticker": ticker,
                "action": "BUY",
                "shares": pos["shares"],
                "price": pos["price"],
                "notional": pos["market_value"],
                "commission": commission,
                "reason": "Initial allocation",
            })

    total_commission = sum(o["commission"] for o in orders)
    total_invested = sum(
        p["market_value"] for t, p in target_positions.items() if t != "CASH"
    )

    return {
        "risk_tier": risk_tier,
        "tier_description": tier_config["description"],
        "total_capital_usd": total_capital,
        "total_capital_ils": total_capital * USD_ILS_RATE,
        "target_volatility_pct": tier_config["target_vol"] * 100,
        "max_leverage": tier_config["max_leverage"],
        "hedge_ratio": tier_config["hedge_ratio"],
        "positions": target_positions,
        "orders": orders,
        "total_commission_usd": total_commission,
        "total_invested_usd": total_invested,
        "cash_remaining_usd": total_capital - total_invested,
    }
