#!/usr/bin/env python3
"""
Automatic Portfolio Management System — Main Entry Point

Connects to IBKR account data, generates portfolio recommendations across
risk tiers, backtests strategies with walk-forward validation,
and produces actionable trade plans backed by academic literature.

Usage:
    python main.py [--risk conservative|moderate|aggressive] [--backtest]
"""
import sys
import os
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from config.portfolio_config import (
    TOTAL_ILS, TOTAL_USD, USD_ILS_RATE, RISK_TIERS,
    BACKTEST_START, BACKTEST_END, ALLOCATION_TICKERS,
)
from src.recommender.portfolio_advisor import (
    analyze_current_portfolio,
    generate_recommendation,
)
from src.portfolio.allocator import get_target_allocation, build_portfolio_plan
from src.market.market_data import get_all_prices, get_fx_rate
from src.currency.fx_manager import optimal_currency_split, loan_optimization_report


def print_header(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_section(title: str):
    print(f"\n{'─'*50}")
    print(f"  {title}")
    print(f"{'─'*50}")


def format_usd(val: float) -> str:
    return f"${val:,.2f}"


def format_pct(val: float) -> str:
    return f"{val:+.2f}%"


def run_analysis(risk_tier: str, run_backtest: bool = False):
    print_header("AUTOMATIC PORTFOLIO MANAGEMENT SYSTEM")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Risk Tier: {risk_tier.upper()}")
    print(f"  Capital: {TOTAL_ILS:,.0f} ILS = {format_usd(TOTAL_USD)}")
    print(f"  USD/ILS: {USD_ILS_RATE}")
    print(f"  Asset Universe: {len(ALLOCATION_TICKERS)} ETFs across equities, bonds, commodities, sectors, intl, REITs, TIPS")

    # ── Current Portfolio Analysis ────────────────────────────────
    print_header("1. CURRENT PORTFOLIO ANALYSIS")
    current = analyze_current_portfolio()

    print(f"  Net Liquidation:    {format_usd(current['net_liquidation_usd'])}")
    print(f"  Leverage:           {current['leverage']:.2f}x")
    print(f"  Margin Debt:        {format_usd(abs(current['margin_debt_usd']))}")
    print(f"  YTD Return:         {format_pct(current['ytd_return_pct'])}")
    print(f"  Unrealized P&L:     {format_usd(current['total_unrealized_pnl'])}")

    print_section("Positions")
    for pos in current["positions"]:
        pnl_pct = pos["unrealized_pnl"] / (pos["avg_price"] * pos["shares"]) * 100
        print(f"  {pos['ticker']:6s}  {pos['shares']:4d} shares  "
              f"avg {format_usd(pos['avg_price']):>10s}  "
              f"now {format_usd(pos['current_price']):>10s}  "
              f"P&L {format_usd(pos['unrealized_pnl']):>10s} ({pnl_pct:+.1f}%)  "
              f"Vol {pos['hist_vol']*100:.0f}%")

    print_section("Issues Identified")
    for issue in current["issues"]:
        icon = {"CRITICAL": "!!!", "HIGH": "!! ", "MEDIUM": "!  "}.get(issue["severity"], "   ")
        print(f"  [{icon}] {issue['severity']:8s} | {issue['issue']}")
        print(f"           {issue['detail']}")
        print(f"           -> {issue['recommendation']}")
        print()

    # ── Currency & Loan Strategy ──────────────────────────────────
    print_header("2. CURRENCY & LOAN STRATEGY")
    fx = optimal_currency_split(TOTAL_ILS, USD_ILS_RATE, 0.90)
    print(f"  Total ILS:              {fx['total_ils']:,.0f} ILS")
    print(f"  USD Equivalent:         {format_usd(fx['total_usd_equivalent'])}")
    print(f"  Convert to USD:         {format_usd(fx['usd_to_convert'])}")
    print(f"  Keep as ILS:            {fx['ils_to_keep']:,.0f} ILS")
    print(f"  FX Conversion Cost:     {format_usd(fx['fx_conversion_cost_usd'])}")
    print(f"  USD Margin Rate:        {fx['usd_margin_rate']:.2f}%")
    print(f"  ILS Margin Rate:        {fx['ils_margin_rate']:.3f}%")
    print(f"  Rate Differential:      {fx['rate_differential_pct']:.3f}%")
    print(f"\n  Strategy: {fx['recommendation']}")

    loan = loan_optimization_report(-5847.04, -453.65, USD_ILS_RATE)
    print_section("Current Loan Cost")
    print(f"  USD Interest/Year:      {format_usd(loan['usd_annual_interest'])}")
    print(f"  ILS Interest/Year (USD):{format_usd(loan['ils_annual_interest_usd'])}")
    print(f"  Total Interest/Year:    {format_usd(loan['total_annual_interest_usd'])}")
    print(f"  Optimization:           {loan['optimization']}")

    # ── Portfolio Recommendation ──────────────────────────────────
    print_header(f"3. {risk_tier.upper()} PORTFOLIO RECOMMENDATION")
    rec = generate_recommendation(risk_tier)
    plan = rec["portfolio_plan"]

    print(f"  Description:     {plan['tier_description']}")
    print(f"  Target Vol:      {plan['target_volatility_pct']:.0f}%")
    print(f"  Max Leverage:    {plan['max_leverage']:.1f}x")
    print(f"  Total Capital:   {format_usd(plan['total_capital_usd'])}")
    print(f"  Total Commission:{format_usd(plan['total_commission_usd'])}")

    print_section("Target Allocation")
    print(f"  {'Ticker':<8s} {'Weight':>8s} {'Shares':>8s} {'Price':>10s} {'Value':>12s}")
    print(f"  {'-'*48}")
    for ticker, pos in sorted(plan["positions"].items(), key=lambda x: -x[1]["market_value"]):
        print(f"  {ticker:<8s} {pos['actual_weight']*100:>7.1f}% {pos['shares']:>8d} "
              f"{format_usd(pos['price']):>10s} {format_usd(pos['market_value']):>12s}")

    print_section("Trade Orders")
    for order in plan["orders"]:
        print(f"  {order['action']:4s} {order['shares']:>6d} {order['ticker']:<8s} "
              f"@ {format_usd(order['price']):>10s}  = {format_usd(order['notional']):>12s}  "
              f"comm {format_usd(order['commission'])}")

    # ── Technical Analysis ────────────────────────────────────────
    print_header("4. TECHNICAL ANALYSIS SIGNALS")
    try:
        from src.backtest.ibkr_price_cache import load_weekly_prices
        from src.analysis.technical import generate_signals, technical_summary

        prices_df = load_weekly_prices()
        signals = generate_signals(prices_df)

        print(f"  {'Ticker':<6s} {'Trend':<10s} {'Momentum':<10s} {'Score':>8s} "
              f"{'RSI':>8s} {'MACD_H':>10s} {'Stoch_K':>8s}")
        print(f"  {'-'*68}")
        for ticker in ALLOCATION_TICKERS:
            if ticker in signals:
                s = signals[ticker]
                ind = s["indicators"]
                print(f"  {ticker:<6s} {s['trend']:<10s} {s['momentum']:<10s} "
                      f"{s['signal_score']:>+7.3f} "
                      f"{ind.get('rsi_14', 0):>8.1f} "
                      f"{ind.get('macd_histogram', 0):>10.4f} "
                      f"{ind.get('stoch_k', 0):>8.1f}")
    except Exception as e:
        print(f"  Technical analysis error: {e}")

    # ── Hedging Strategies ────────────────────────────────────────
    print_header("5. HEDGING & INSURANCE")
    for hedge in rec["hedging_strategies"]:
        print(f"  Strategy: {hedge['name']}")
        print(f"  {hedge['description']}")
        print(f"  Annual Cost: {hedge['annual_cost_pct']:.2f}%")
        print(f"  Max Loss: {hedge['max_loss_pct']:.1f}%")
        if hedge["upside_cap_pct"]:
            print(f"  Upside Cap: {hedge['upside_cap_pct']:.1f}%")
        print()

    # ── Transition Plan ───────────────────────────────────────────
    print_header("6. TRANSITION PLAN")
    transition = rec["transition_plan"]
    for step in transition["steps"]:
        print(f"  Step {step['step']}: {step['action']}")
        print(f"         {step['detail']}")
        if "proceeds_usd" in step:
            print(f"         Proceeds: {format_usd(step['proceeds_usd'])}")
        if "tax_benefit_estimated" in step:
            print(f"         Tax benefit: {step['tax_benefit_estimated']}")
        print()
    print(f"  Total Transition Cost: {format_usd(transition['estimated_total_transition_cost_usd'])}")
    print(f"  Timeline: {transition['estimated_time_to_complete']}")

    # ── Risk Tier Comparison ──────────────────────────────────────
    print_header("7. RISK TIER COMPARISON")
    print(f"  {'Tier':<15s} {'Target Vol':>10s} {'Equity %':>10s} {'Bond %':>10s} "
          f"{'Real %':>10s} {'Cash %':>8s}")
    print(f"  {'-'*65}")
    equity_tickers = {"SPY", "VT", "XLK", "XLF", "XLE", "XLV", "EFA", "EEM", "IWM"}
    bond_tickers = {"BND", "TLT", "TIP"}
    real_tickers = {"GLD", "VNQ", "DBC"}
    for tier_name, tier_config in RISK_TIERS.items():
        alloc = tier_config["allocation"]
        equity = sum(v for k, v in alloc.items() if k in equity_tickers) * 100
        bonds = sum(v for k, v in alloc.items() if k in bond_tickers) * 100
        real_assets = sum(v for k, v in alloc.items() if k in real_tickers) * 100
        cash = alloc.get("cash", 0) * 100
        marker = " <--" if tier_name == risk_tier else ""
        print(f"  {tier_name:<15s} {tier_config['target_vol']*100:>9.0f}% "
              f"{equity:>9.0f}% {bonds:>9.0f}% {real_assets:>9.0f}% {cash:>7.0f}%{marker}")

    # ── Backtest ──────────────────────────────────────────────────
    if run_backtest:
        print_header("8. BACKTESTING RESULTS")
        try:
            from src.backtest.backtester import compare_strategies, run_walk_forward

            strategies = {}
            for tier_name in RISK_TIERS:
                strategies[tier_name] = get_target_allocation(tier_name)

            results = compare_strategies(strategies, BACKTEST_START, BACKTEST_END, TOTAL_USD)

            print(f"  Period: {BACKTEST_START} to {BACKTEST_END}")
            print(f"  Initial Capital: {format_usd(TOTAL_USD)}\n")
            print(f"  {'Tier':<15s} {'Total Ret':>10s} {'Annual Ret':>10s} "
                  f"{'Vol':>8s} {'Sharpe':>8s} {'MaxDD':>8s} {'Final Val':>12s}")
            print(f"  {'-'*75}")

            for name, result in results.items():
                m = result.get("metrics", {})
                if "error" in result:
                    print(f"  {name:<15s} ERROR: {result['error']}")
                    continue
                print(f"  {name:<15s} {m.get('total_return_pct', 0):>+9.1f}% "
                      f"{m.get('annual_return_pct', 0):>+9.1f}% "
                      f"{m.get('annual_volatility_pct', 0):>7.1f}% "
                      f"{m.get('sharpe_ratio', 0):>8.2f} "
                      f"{m.get('max_drawdown_pct', 0):>+7.1f}% "
                      f"{format_usd(m.get('final_value_usd', 0)):>12s}")

            # Walk-forward validation for the selected tier
            print_section(f"Walk-Forward Validation ({risk_tier})")
            wf_weights = get_target_allocation(risk_tier)
            wf = run_walk_forward(wf_weights)
            if "error" in wf:
                print(f"  {wf['error']}")
            else:
                print(wf["summary_text"])

        except Exception as e:
            print(f"  Backtest error: {e}")
            import traceback
            traceback.print_exc()

    # ── Academic Methodology ──────────────────────────────────────
    print_header("9. METHODOLOGY & ACADEMIC BACKING")
    try:
        from src.research.literature import get_all_citations, format_citation
        citations = get_all_citations()
        print(f"  This system's methodology is backed by {len(citations)} peer-reviewed papers:\n")
        by_cat = {}
        for c in citations:
            by_cat.setdefault(c["category"], []).append(c)
        for cat, papers in by_cat.items():
            print(f"  {cat.replace('_', ' ').title()}:")
            for p in papers:
                print(f"    - {format_citation(p)}")
            print()
    except Exception as e:
        print(f"  Literature module error: {e}")

    print_header("DISCLAIMER")
    print("  This is a quantitative analysis tool, NOT financial advice.")
    print("  Past performance does not guarantee future results.")
    print("  All investments carry risk of loss.")
    print("  Consult a licensed financial advisor before making trades.")
    print("  Data sourced from IBKR live feed and pre-fetched price history.")
    print()


def main():
    parser = argparse.ArgumentParser(description="Portfolio Management System")
    parser.add_argument("--risk", choices=["conservative", "moderate", "aggressive"],
                        default="moderate", help="Risk tier")
    parser.add_argument("--backtest", action="store_true", help="Run historical backtest")
    args = parser.parse_args()

    run_analysis(args.risk, args.backtest)


if __name__ == "__main__":
    main()
