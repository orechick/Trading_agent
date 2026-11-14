"""
USD/ILS currency management — conversion, loan optimization, FX hedging cost analysis.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dataclasses import dataclass
from config.portfolio_config import IBKR_MARGIN_RATES, COMMISSIONS


@dataclass
class FXPosition:
    ils_cash: float
    usd_cash: float
    usd_ils_rate: float

    @property
    def total_usd(self) -> float:
        return self.usd_cash + self.ils_cash / self.usd_ils_rate

    @property
    def total_ils(self) -> float:
        return self.ils_cash + self.usd_cash * self.usd_ils_rate


def margin_rate(currency: str, balance: float) -> float:
    """Return the applicable IBKR margin interest rate for a given currency and debit balance."""
    rates = IBKR_MARGIN_RATES.get(currency, IBKR_MARGIN_RATES["USD"])
    applicable = 0.0
    for threshold, rate in sorted(rates.items()):
        if abs(balance) >= threshold:
            applicable = rate
    return applicable


def fx_conversion_cost(amount_usd: float) -> float:
    """Estimate IBKR forex conversion cost for a given USD notional."""
    bps = COMMISSIONS["FOREX"]["per_trade_bps"]
    cost = amount_usd * bps / 10_000
    return max(cost, COMMISSIONS["FOREX"]["min"])


def optimal_currency_split(
    total_ils: float,
    usd_ils_rate: float,
    usd_allocation_pct: float,
) -> dict:
    """
    Given total ILS and desired USD-denominated allocation %,
    compute optimal conversion amount accounting for FX costs
    and differential borrowing rates.
    """
    total_usd = total_ils / usd_ils_rate
    usd_needed = total_usd * usd_allocation_pct
    ils_kept = total_ils * (1 - usd_allocation_pct)

    conversion_cost = fx_conversion_cost(usd_needed)

    usd_borrow_rate = margin_rate("USD", 0)
    ils_borrow_rate = margin_rate("ILS", 0)
    rate_differential = ils_borrow_rate - usd_borrow_rate

    return {
        "total_ils": total_ils,
        "total_usd_equivalent": total_usd,
        "usd_to_convert": usd_needed,
        "ils_to_keep": ils_kept,
        "fx_conversion_cost_usd": conversion_cost,
        "usd_margin_rate": usd_borrow_rate,
        "ils_margin_rate": ils_borrow_rate,
        "rate_differential_pct": rate_differential,
        "recommendation": (
            "Convert most ILS to USD upfront — USD borrowing rate is lower, "
            "and most liquid assets trade in USD. Keep ~10% ILS as cash buffer."
            if rate_differential > 0
            else "Consider keeping a larger ILS allocation to reduce FX exposure."
        ),
    }


def loan_optimization_report(
    usd_debit: float,
    ils_debit: float,
    usd_ils_rate: float,
) -> dict:
    """Analyze current margin loan costs and suggest optimization."""
    usd_rate = margin_rate("USD", usd_debit)
    ils_rate = margin_rate("ILS", ils_debit)

    usd_annual_cost = abs(usd_debit) * usd_rate / 100
    ils_annual_cost = abs(ils_debit) * ils_rate / 100
    ils_cost_in_usd = ils_annual_cost / usd_ils_rate

    total_annual_cost = usd_annual_cost + ils_cost_in_usd

    return {
        "usd_debit": usd_debit,
        "usd_rate_pct": usd_rate,
        "usd_annual_interest": usd_annual_cost,
        "ils_debit": ils_debit,
        "ils_rate_pct": ils_rate,
        "ils_annual_interest_usd": ils_cost_in_usd,
        "total_annual_interest_usd": total_annual_cost,
        "optimization": (
            "Consolidate ILS debit into USD — lower rate saves "
            f"~${(ils_cost_in_usd - abs(ils_debit / usd_ils_rate) * usd_rate / 100):.2f}/year."
            if ils_rate > usd_rate and abs(ils_debit) > 100
            else "Current split is acceptable."
        ),
    }
