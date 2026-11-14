"""
Hedging & insurance strategies — protective puts, collar, tail-risk hedging.
Uses simplified Black-Scholes for option pricing.
"""
import math
from dataclasses import dataclass
from config.portfolio_config import COMMISSIONS, RISK_FREE_RATE


@dataclass
class HedgeStrategy:
    name: str
    description: str
    instruments: list[dict]
    estimated_annual_cost_pct: float
    max_loss_pct: float
    upside_cap_pct: float | None


def _norm_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def _bs_put_price(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Black-Scholes European put price."""
    if T <= 0 or sigma <= 0:
        return max(K - S, 0.0)
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return K * math.exp(-r * T) * _norm_cdf(-d2) - S * _norm_cdf(-d1)


def _bs_call_price(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Black-Scholes European call price."""
    if T <= 0 or sigma <= 0:
        return max(S - K, 0.0)
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return S * _norm_cdf(d1) - K * math.exp(-r * T) * _norm_cdf(d2)


def protective_put(
    equity_value: float,
    ticker: str,
    current_price: float,
    implied_vol: float,
    hedge_pct: float = 1.0,
    otm_pct: float = 0.05,
    days_to_expiry: int = 90,
) -> HedgeStrategy:
    notional_to_hedge = equity_value * hedge_pct
    shares_to_hedge = notional_to_hedge / current_price
    contracts_needed = int(shares_to_hedge / 100) or 1

    strike = current_price * (1 - otm_pct)
    t = days_to_expiry / 365

    premium_per_share = _bs_put_price(current_price, strike, t, RISK_FREE_RATE, implied_vol)
    premium_per_share = max(premium_per_share, 0.01)

    total_premium = contracts_needed * 100 * premium_per_share
    commission = contracts_needed * COMMISSIONS["US_OPT"]["per_contract"]
    total_cost = total_premium + commission
    annual_cost_pct = (total_cost / equity_value) * (365 / days_to_expiry) * 100

    return HedgeStrategy(
        name=f"Protective Put on {ticker}",
        description=(
            f"Buy {contracts_needed} put contracts at ${strike:.2f} strike, "
            f"{days_to_expiry} DTE. Premium ${premium_per_share:.2f}/share. "
            f"Limits loss to {otm_pct*100:.0f}% + premium."
        ),
        instruments=[{
            "type": "PUT",
            "ticker": ticker,
            "strike": round(strike, 2),
            "contracts": contracts_needed,
            "days_to_expiry": days_to_expiry,
            "premium_per_share": round(premium_per_share, 2),
            "total_premium": round(total_premium, 2),
            "commission": round(commission, 2),
        }],
        estimated_annual_cost_pct=round(annual_cost_pct, 2),
        max_loss_pct=round((otm_pct + total_cost / equity_value) * 100, 2),
        upside_cap_pct=None,
    )


def collar_strategy(
    equity_value: float,
    ticker: str,
    current_price: float,
    implied_vol: float,
    put_otm_pct: float = 0.05,
    call_otm_pct: float = 0.10,
    days_to_expiry: int = 90,
) -> HedgeStrategy:
    shares = equity_value / current_price
    contracts = int(shares / 100) or 1
    t = days_to_expiry / 365

    put_strike = current_price * (1 - put_otm_pct)
    call_strike = current_price * (1 + call_otm_pct)

    put_premium = _bs_put_price(current_price, put_strike, t, RISK_FREE_RATE, implied_vol)
    call_premium = _bs_call_price(current_price, call_strike, t, RISK_FREE_RATE, implied_vol)

    put_premium = max(put_premium, 0.01)
    call_premium = max(call_premium, 0.01)

    net_cost = (put_premium - call_premium) * contracts * 100
    commission = contracts * 2 * COMMISSIONS["US_OPT"]["per_contract"]

    return HedgeStrategy(
        name=f"Collar on {ticker}",
        description=(
            f"Buy {contracts} puts at ${put_strike:.2f}, sell {contracts} calls at ${call_strike:.2f}. "
            f"Net cost: ${net_cost:.2f}."
        ),
        instruments=[
            {"type": "PUT", "ticker": ticker, "strike": round(put_strike, 2),
             "contracts": contracts, "action": "BUY"},
            {"type": "CALL", "ticker": ticker, "strike": round(call_strike, 2),
             "contracts": contracts, "action": "SELL"},
        ],
        estimated_annual_cost_pct=round(abs(net_cost) / equity_value * (365 / days_to_expiry) * 100, 2),
        max_loss_pct=round(put_otm_pct * 100, 2),
        upside_cap_pct=round(call_otm_pct * 100, 2),
    )


def tail_risk_hedge(
    portfolio_value: float,
    hedge_budget_pct: float = 0.02,
) -> HedgeStrategy:
    budget = portfolio_value * hedge_budget_pct
    spy_price = 749.60
    strike = spy_price * 0.80
    t = 90 / 365
    premium_per_share = _bs_put_price(spy_price, strike, t, RISK_FREE_RATE, 0.16)
    premium_per_share = max(premium_per_share, 0.50)
    contracts = max(int(budget / (premium_per_share * 100)), 1)
    total_cost = contracts * premium_per_share * 100

    return HedgeStrategy(
        name="Tail-Risk SPY Put Hedge",
        description=(
            f"Buy {contracts} deep OTM SPY puts at ~${strike:.0f} strike. "
            f"Pays off in >20% market crash. Budget: ${total_cost:.0f}/quarter."
        ),
        instruments=[{
            "type": "PUT",
            "ticker": "SPY",
            "strike": round(strike, 0),
            "contracts": contracts,
            "days_to_expiry": 90,
            "total_cost": round(total_cost, 2),
        }],
        estimated_annual_cost_pct=round(total_cost / portfolio_value * 4 * 100, 2),
        max_loss_pct=0,
        upside_cap_pct=None,
    )


def recommend_hedges(
    portfolio_value: float,
    positions: list[dict],
    risk_tier: str,
    hedge_ratio: float,
) -> list[HedgeStrategy]:
    strategies = []
    strategies.append(tail_risk_hedge(portfolio_value, hedge_budget_pct=0.01))

    if hedge_ratio <= 0:
        return strategies

    for pos in positions:
        if pos.get("asset_class", "").startswith("equity"):
            mv = pos.get("market_value", 0)
            iv = pos.get("implied_vol", 0.20)
            price = pos.get("price", 100)
            ticker = pos.get("ticker", "SPY")

            if mv > portfolio_value * 0.05:
                if risk_tier == "conservative":
                    strategies.append(collar_strategy(mv, ticker, price, iv))
                else:
                    strategies.append(protective_put(
                        mv, ticker, price, iv,
                        hedge_pct=hedge_ratio,
                        otm_pct=0.07 if risk_tier == "moderate" else 0.10,
                    ))

    return strategies
