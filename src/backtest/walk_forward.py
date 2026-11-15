"""
Walk-forward backtesting with out-of-sample validation.
Implements rolling and expanding window approaches with deflated Sharpe ratio
per Bailey & Lopez de Prado (2014).
"""
import numpy as np
import pandas as pd


def _sharpe(returns: np.ndarray, rf_weekly: float = 0.0) -> float:
    excess = returns - rf_weekly
    if len(excess) < 2 or np.std(excess, ddof=1) == 0:
        return 0.0
    return float(np.mean(excess) / np.std(excess, ddof=1) * np.sqrt(52))


def _sortino(returns: np.ndarray, rf_weekly: float = 0.0) -> float:
    excess = returns - rf_weekly
    downside = excess[excess < 0]
    if len(downside) < 2:
        return _sharpe(returns, rf_weekly)
    down_std = np.std(downside, ddof=1)
    if down_std == 0:
        return 0.0
    return float(np.mean(excess) / down_std * np.sqrt(52))


def _max_drawdown(cum_returns: np.ndarray) -> float:
    peak = np.maximum.accumulate(cum_returns)
    dd = (cum_returns - peak) / np.where(peak > 0, peak, 1)
    return float(np.min(dd))


def deflated_sharpe_ratio(
    observed_sr: float,
    num_trials: int,
    T: int,
    skew: float = 0.0,
    kurtosis: float = 3.0,
) -> float:
    """
    Deflated Sharpe Ratio (Bailey & Lopez de Prado, 2014).
    Adjusts for multiple testing by estimating the expected maximum SR
    under the null of zero true SR across `num_trials` independent strategies.

    Parameters
    ----------
    observed_sr : annualized Sharpe ratio of the selected strategy
    num_trials  : number of strategies tested (including discarded ones)
    T           : number of return observations
    skew        : skewness of returns
    kurtosis    : kurtosis of returns (3 = normal)
    """
    if num_trials < 1 or T < 2:
        return 0.0

    from math import log, sqrt, erfc

    e_max_sr = sqrt(2 * log(num_trials)) - (
        (log(log(num_trials)) + log(4 * 3.14159265))
        / (2 * sqrt(2 * log(num_trials)))
    ) if num_trials > 1 else 0.0

    sr_std = sqrt(
        (1 - skew * observed_sr + ((kurtosis - 1) / 4) * observed_sr ** 2) / (T - 1)
    )

    if sr_std == 0:
        return 1.0 if observed_sr > e_max_sr else 0.0

    z = (observed_sr - e_max_sr) / sr_std
    dsr = 1 - 0.5 * erfc(z / sqrt(2))
    return float(dsr)


def walk_forward_backtest(
    prices_df: pd.DataFrame,
    allocation_weights: dict,
    train_weeks: int = 104,
    test_weeks: int = 26,
    step_weeks: int = 13,
    rf_annual: float = 0.045,
    expanding: bool = False,
) -> dict:
    """
    Walk-forward backtest with rolling or expanding training window.

    Parameters
    ----------
    prices_df         : DataFrame, columns = tickers, rows = weekly dates
    allocation_weights: {ticker: weight} — static target allocation
    train_weeks       : in-sample training window (weeks)
    test_weeks        : out-of-sample test window (weeks)
    step_weeks        : step size between windows (weeks)
    rf_annual         : annual risk-free rate
    expanding         : if True, training window grows from initial size

    Returns
    -------
    dict with oos_returns, fold_metrics, aggregate_metrics, dsr
    """
    tickers = [t for t in allocation_weights if t in prices_df.columns and t != "cash"]
    weights = np.array([allocation_weights.get(t, 0) for t in tickers])
    cash_w = allocation_weights.get("cash", 0)
    if weights.sum() > 0:
        weights = weights / weights.sum() * (1 - cash_w)

    returns_df = prices_df[tickers].pct_change().dropna()
    n = len(returns_df)
    rf_weekly = (1 + rf_annual) ** (1 / 52) - 1

    folds = []
    all_oos_returns = []
    fold_id = 0

    start = 0
    while start + train_weeks + test_weeks <= n:
        if expanding:
            train_start = 0
        else:
            train_start = start

        train_end = start + train_weeks
        test_end = min(train_end + test_weeks, n)

        test_rets = returns_df.iloc[train_end:test_end].values
        port_rets = test_rets @ weights + cash_w * rf_weekly

        cum = np.cumprod(1 + port_rets)
        fold_sharpe = _sharpe(port_rets, rf_weekly)
        fold_sortino = _sortino(port_rets, rf_weekly)
        fold_mdd = _max_drawdown(cum)
        fold_return = float(cum[-1] - 1) if len(cum) > 0 else 0.0

        fold_info = {
            "fold": fold_id,
            "train_start": str(returns_df.index[train_start]) if hasattr(returns_df.index[train_start], 'strftime') else str(returns_df.index[train_start]),
            "train_end": str(returns_df.index[train_end - 1]) if hasattr(returns_df.index[train_end - 1], 'strftime') else str(returns_df.index[train_end - 1]),
            "test_start": str(returns_df.index[train_end]) if hasattr(returns_df.index[train_end], 'strftime') else str(returns_df.index[train_end]),
            "test_end": str(returns_df.index[test_end - 1]) if hasattr(returns_df.index[test_end - 1], 'strftime') else str(returns_df.index[test_end - 1]),
            "oos_return": round(fold_return * 100, 2),
            "oos_sharpe": round(fold_sharpe, 3),
            "oos_sortino": round(fold_sortino, 3),
            "oos_max_dd": round(fold_mdd * 100, 2),
            "n_weeks": test_end - train_end,
        }
        folds.append(fold_info)
        all_oos_returns.extend(port_rets.tolist())

        fold_id += 1
        start += step_weeks

    if not all_oos_returns:
        return {"error": "Not enough data for walk-forward backtest"}

    oos_arr = np.array(all_oos_returns)
    cum_oos = np.cumprod(1 + oos_arr)
    total_return = float(cum_oos[-1] - 1)
    ann_return = float((1 + total_return) ** (52 / len(oos_arr)) - 1)
    ann_vol = float(np.std(oos_arr, ddof=1) * np.sqrt(52))
    overall_sharpe = _sharpe(oos_arr, rf_weekly)
    overall_sortino = _sortino(oos_arr, rf_weekly)
    overall_mdd = _max_drawdown(cum_oos)
    calmar = ann_return / abs(overall_mdd) if overall_mdd != 0 else 0.0

    skew_val = float(pd.Series(oos_arr).skew())
    kurt_val = float(pd.Series(oos_arr).kurtosis() + 3)
    dsr = deflated_sharpe_ratio(
        observed_sr=overall_sharpe,
        num_trials=max(fold_id, 1),
        T=len(oos_arr),
        skew=skew_val,
        kurtosis=kurt_val,
    )

    return {
        "method": "expanding_window" if expanding else "rolling_window",
        "train_weeks": train_weeks,
        "test_weeks": test_weeks,
        "step_weeks": step_weeks,
        "n_folds": fold_id,
        "n_oos_weeks": len(oos_arr),
        "fold_metrics": folds,
        "aggregate": {
            "total_return_pct": round(total_return * 100, 2),
            "annualized_return_pct": round(ann_return * 100, 2),
            "annualized_volatility_pct": round(ann_vol * 100, 2),
            "sharpe_ratio": round(overall_sharpe, 3),
            "sortino_ratio": round(overall_sortino, 3),
            "max_drawdown_pct": round(overall_mdd * 100, 2),
            "calmar_ratio": round(calmar, 3),
            "skewness": round(skew_val, 3),
            "kurtosis": round(kurt_val, 3),
        },
        "deflated_sharpe_ratio": round(dsr, 4),
        "dsr_interpretation": _interpret_dsr(dsr),
    }


def _interpret_dsr(dsr: float) -> str:
    if dsr >= 0.95:
        return "Strong: strategy SR likely genuine (p<0.05 of overfitting)"
    if dsr >= 0.80:
        return "Moderate: reasonable confidence SR is not from overfitting"
    if dsr >= 0.50:
        return "Weak: SR may partly reflect overfitting / data snooping"
    return "Poor: high probability the observed SR is from overfitting"


def walk_forward_summary(results: dict) -> str:
    """Format walk-forward results as a readable report."""
    if "error" in results:
        return f"Walk-forward error: {results['error']}"

    agg = results["aggregate"]
    lines = [
        "=" * 60,
        "WALK-FORWARD OUT-OF-SAMPLE BACKTEST",
        "=" * 60,
        f"Method: {results['method']}",
        f"Training window: {results['train_weeks']} weeks | "
        f"Test window: {results['test_weeks']} weeks | "
        f"Step: {results['step_weeks']} weeks",
        f"Number of folds: {results['n_folds']} | "
        f"Total OOS weeks: {results['n_oos_weeks']}",
        "",
        "--- Aggregate OOS Performance ---",
        f"  Total return:       {agg['total_return_pct']:+.2f}%",
        f"  Annualized return:  {agg['annualized_return_pct']:+.2f}%",
        f"  Annualized vol:     {agg['annualized_volatility_pct']:.2f}%",
        f"  Sharpe ratio:       {agg['sharpe_ratio']:.3f}",
        f"  Sortino ratio:      {agg['sortino_ratio']:.3f}",
        f"  Max drawdown:       {agg['max_drawdown_pct']:.2f}%",
        f"  Calmar ratio:       {agg['calmar_ratio']:.3f}",
        "",
        "--- Overfitting Analysis (Bailey & Lopez de Prado) ---",
        f"  Deflated Sharpe Ratio: {results['deflated_sharpe_ratio']:.4f}",
        f"  Assessment: {results['dsr_interpretation']}",
        "",
        "--- Per-Fold OOS Results ---",
    ]

    for f in results["fold_metrics"]:
        lines.append(
            f"  Fold {f['fold']}: "
            f"return={f['oos_return']:+.2f}% "
            f"sharpe={f['oos_sharpe']:.3f} "
            f"mdd={f['oos_max_dd']:.2f}% "
            f"({f['test_start'][:10]} to {f['test_end'][:10]})"
        )

    return "\n".join(lines)
