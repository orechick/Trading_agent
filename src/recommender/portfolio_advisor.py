"""
Portfolio recommendation engine — analyzes account state, market conditions,
and generates actionable portfolio recommendations with full rationale.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config.portfolio_config import RISK_TIERS, TOTAL_USD, USD_ILS_RATE, TOTAL_ILS, ASSET_UNIVERSE
from src.market.market_data import get_all_prices, get_metrics, get_fx_rate
from src.portfolio.allocator import build_portfolio_plan
from src.currency.fx_manager import optimal_currency_split, loan_optimization_report
from src.hedging.hedge_engine import recommend_hedges
from src.risk.risk_engine import sharpe_ratio

EQUITY_TICKERS = {
    t for t, info in ASSET_UNIVERSE.items()
    if info[1].startswith("equity") or info[1].startswith("sector")
}


def analyze_current_portfolio() -> dict:
    """Analyze the existing IBKR portfolio and identify issues."""
    positions = [
        {
            "ticker": "NVDA",
            "shares": 40,
            "avg_price": 170.025,
            "current_price": 161.01,
            "market_value": 6440.40,
            "unrealized_pnl": -360.60,
            "asset_class": "equity_us_tech",
            "implied_vol": 0.594,
            "hist_vol": 0.652,
        },
        {
            "ticker": "SNDK",
            "shares": 6,
            "avg_price": 1567.45,
            "current_price": 865.23,
            "market_value": 5191.38,
            "unrealized_pnl": -4212.87,
            "asset_class": "equity_us_tech",
            "implied_vol": 0.854,
            "hist_vol": 1.027,
        },
    ]

    total_position_value = sum(p["market_value"] for p in positions)
    total_unrealized_pnl = sum(p["unrealized_pnl"] for p in positions)

    issues = []
    issues.append({
        "severity": "CRITICAL",
        "issue": "Extreme concentration risk",
        "detail": "100% allocation in 2 tech stocks. Zero diversification by sector, geography, or asset class.",
        "recommendation": "Diversify across equities, bonds, commodities, and geographies.",
    })
    issues.append({
        "severity": "CRITICAL",
        "issue": "Excessive leverage",
        "detail": "2.06x leverage with -$5,988 margin debt. Interest cost ~$400/year on a $5,646 portfolio.",
        "recommendation": "Reduce leverage to ≤1.0x for the new portfolio. Use margin only if aggressive tier.",
    })
    issues.append({
        "severity": "HIGH",
        "issue": "Extreme single-stock volatility",
        "detail": f"NVDA: 65% annual vol, SNDK: 103% annual vol. Portfolio vol likely >60%.",
        "recommendation": "Target portfolio vol of 6-20% depending on risk tier.",
    })
    issues.append({
        "severity": "HIGH",
        "issue": "No hedging or insurance",
        "detail": "Zero downside protection. Maximum drawdown -40% YTD.",
        "recommendation": "Implement protective puts or collars. Allocate 1-2% to tail-risk hedges.",
    })
    issues.append({
        "severity": "MEDIUM",
        "issue": "SNDK deep underwater",
        "detail": f"SNDK: -$4,213 unrealized loss (-44.8% from cost basis). High vol stock with 103% annual vol.",
        "recommendation": "Consider tax-loss harvesting — sell SNDK to realize the loss and offset future gains.",
    })
    issues.append({
        "severity": "MEDIUM",
        "issue": "Dual-currency borrowing inefficiency",
        "detail": "Borrowing in both USD (-$5,847) and ILS (-454 ILS). ILS rate is higher.",
        "recommendation": "Consolidate borrowing in USD where the rate is lower.",
    })

    return {
        "net_liquidation_usd": 5645.88,
        "positions": positions,
        "total_position_value": total_position_value,
        "total_unrealized_pnl": total_unrealized_pnl,
        "leverage": 2.06,
        "margin_debt_usd": -5988.32,
        "ytd_return_pct": -40.0,
        "issues": issues,
    }


def generate_recommendation(risk_tier: str = "moderate") -> dict:
    """Generate complete portfolio recommendation."""
    prices = get_all_prices()
    current_analysis = analyze_current_portfolio()

    fx_strategy = optimal_currency_split(
        total_ils=TOTAL_ILS,
        usd_ils_rate=get_fx_rate(),
        usd_allocation_pct=0.90,
    )

    loan_report = loan_optimization_report(
        usd_debit=-5847.04,
        ils_debit=-453.65,
        usd_ils_rate=get_fx_rate(),
    )

    plan = build_portfolio_plan(
        risk_tier=risk_tier,
        total_capital=TOTAL_USD,
        prices=prices,
    )

    tier_config = RISK_TIERS[risk_tier]
    equity_positions = [
        {
            "ticker": ticker,
            "market_value": pos["market_value"],
            "price": pos["price"],
            "asset_class": "equity",
            "implied_vol": get_metrics(ticker).get("iv", 0.20),
        }
        for ticker, pos in plan["positions"].items()
        if ticker not in ("CASH",) and ticker in EQUITY_TICKERS
    ]
    hedges = recommend_hedges(
        portfolio_value=TOTAL_USD,
        positions=equity_positions,
        risk_tier=risk_tier,
        hedge_ratio=tier_config["hedge_ratio"],
    )

    transition = _build_transition_plan(current_analysis, plan)

    return {
        "current_analysis": current_analysis,
        "risk_tier": risk_tier,
        "fx_strategy": fx_strategy,
        "loan_optimization": loan_report,
        "portfolio_plan": plan,
        "hedging_strategies": [
            {
                "name": h.name,
                "description": h.description,
                "annual_cost_pct": h.estimated_annual_cost_pct,
                "max_loss_pct": h.max_loss_pct,
                "upside_cap_pct": h.upside_cap_pct,
            }
            for h in hedges
        ],
        "transition_plan": transition,
    }


def _build_transition_plan(current: dict, target: dict) -> dict:
    """Plan the transition from current holdings to target portfolio."""
    steps = []

    steps.append({
        "step": 1,
        "action": "Tax-loss harvest SNDK",
        "detail": (
            "Sell 6 shares SNDK at ~$865.23 to realize -$4,213 capital loss. "
            "This loss offsets future capital gains. Wait 30 days before buying "
            "back to avoid wash sale rule (or buy a similar but not identical ETF like SOXX)."
        ),
        "proceeds_usd": 5191.38,
        "tax_benefit_estimated": "~$1,053 at 25% tax rate",
    })

    steps.append({
        "step": 2,
        "action": "Evaluate NVDA position",
        "detail": (
            "NVDA has -$361 unrealized loss. Can harvest this loss too. "
            "Or keep if you have strong conviction — NVDA is a quality name but "
            "represents extreme concentration at 65% annual vol."
        ),
        "options": ["Sell all (harvest loss)", "Keep reduced position (10 shares max)"],
    })

    steps.append({
        "step": 3,
        "action": "Convert ILS to USD",
        "detail": (
            f"Convert ~135,000 ILS to ~$42,097 USD at {current.get('fx_rate', 3.2066)}. "
            f"Keep ~15,000 ILS as cash buffer. FX cost: ~$8.40."
        ),
    })

    steps.append({
        "step": 4,
        "action": "Pay down margin debt",
        "detail": (
            "Use SNDK proceeds + new capital to eliminate the $5,988 margin debt. "
            "This saves ~$400/year in interest."
        ),
    })

    steps.append({
        "step": 5,
        "action": "Deploy target allocation",
        "detail": (
            f"Execute {len(target.get('orders', []))} buy orders per the "
            f"{target['risk_tier']} portfolio plan. Total commission: "
            f"${target['total_commission_usd']:.2f}."
        ),
    })

    steps.append({
        "step": 6,
        "action": "Implement hedging",
        "detail": "Buy protective puts or collar on SPY position. Allocate 1% to tail-risk hedge.",
    })

    steps.append({
        "step": 7,
        "action": "Set rebalancing schedule",
        "detail": "Quarterly rebalancing with 2% drift threshold to minimize transaction costs.",
    })

    return {
        "steps": steps,
        "estimated_total_transition_cost_usd": target["total_commission_usd"] + 8.40 + 1.0,
        "estimated_time_to_complete": "1-2 trading days",
    }
