"""
Technical analysis indicators — RSI, MACD, Bollinger Bands, moving averages,
momentum, ATR (approximated from close), Stochastic oscillator.
Composite signal scoring for portfolio allocation overlay.
"""
import numpy as np
import pandas as pd


# ── Individual Indicators ───────────────────────────────────────────

def sma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period, min_periods=period).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def bollinger_bands(series: pd.Series, period: int = 20, num_std: float = 2.0):
    middle = sma(series, period)
    std = series.rolling(window=period, min_periods=period).std()
    upper = middle + num_std * std
    lower = middle - num_std * std
    return upper, middle, lower


def momentum_roc(series: pd.Series, period: int = 10) -> pd.Series:
    return series.pct_change(periods=period) * 100


def atr_from_close(series: pd.Series, period: int = 14) -> pd.Series:
    """Approximate ATR using close-to-close range (no high/low available)."""
    tr_approx = series.diff().abs()
    return tr_approx.rolling(window=period, min_periods=period).mean()


def stochastic(series: pd.Series, k_period: int = 14, d_period: int = 3):
    low_min = series.rolling(window=k_period, min_periods=k_period).min()
    high_max = series.rolling(window=k_period, min_periods=k_period).max()
    denom = high_max - low_min
    pct_k = 100 * (series - low_min) / denom.replace(0, np.nan)
    pct_d = sma(pct_k, d_period)
    return pct_k, pct_d


# ── Composite Signal Generator ─────────────────────────────────────

def _score_rsi(val: float) -> float:
    if val < 30:
        return 0.5
    if val < 40:
        return 0.2
    if val > 70:
        return -0.5
    if val > 60:
        return -0.2
    return 0.0


def _score_macd(macd_val: float, signal_val: float, hist: float) -> float:
    score = 0.0
    if macd_val > signal_val:
        score += 0.3
    else:
        score -= 0.3
    if hist > 0:
        score += 0.2
    else:
        score -= 0.2
    return np.clip(score, -0.5, 0.5)


def _score_bollinger(price: float, upper: float, lower: float, middle: float) -> float:
    if upper == lower:
        return 0.0
    position = (price - lower) / (upper - lower)
    if position < 0.2:
        return 0.4
    if position > 0.8:
        return -0.4
    return (0.5 - position) * 0.4


def _score_trend(price: float, sma20: float, sma50: float, sma200: float) -> float:
    score = 0.0
    if not np.isnan(sma20) and price > sma20:
        score += 0.15
    elif not np.isnan(sma20):
        score -= 0.15
    if not np.isnan(sma50) and price > sma50:
        score += 0.2
    elif not np.isnan(sma50):
        score -= 0.2
    if not np.isnan(sma200) and price > sma200:
        score += 0.3
    elif not np.isnan(sma200):
        score -= 0.3
    return np.clip(score, -0.5, 0.5)


def _score_stochastic(k: float, d: float) -> float:
    if k < 20 and d < 20:
        return 0.4
    if k > 80 and d > 80:
        return -0.4
    if k > d:
        return 0.1
    return -0.1


def generate_signals(prices_df: pd.DataFrame) -> dict:
    """
    Compute technical indicators and composite signals for each ticker.

    Parameters
    ----------
    prices_df : DataFrame with DatetimeIndex, columns are tickers, values are
                weekly close prices.

    Returns
    -------
    dict of {ticker: {trend, momentum, signal_score, indicators}}
    """
    results = {}

    for ticker in prices_df.columns:
        series = prices_df[ticker].dropna()
        if len(series) < 52:
            results[ticker] = {
                "trend": "neutral",
                "momentum": "weak",
                "signal_score": 0.0,
                "indicators": {},
            }
            continue

        price = series.iloc[-1]

        rsi_val = rsi(series).iloc[-1]
        macd_line, sig_line, hist = macd(series)
        macd_val = macd_line.iloc[-1]
        sig_val = sig_line.iloc[-1]
        hist_val = hist.iloc[-1]

        bb_upper, bb_mid, bb_lower = bollinger_bands(series)
        bb_u = bb_upper.iloc[-1]
        bb_m = bb_mid.iloc[-1]
        bb_l = bb_lower.iloc[-1]

        sma_20 = sma(series, 20).iloc[-1]
        sma_50 = sma(series, 50).iloc[-1]
        sma_200 = sma(series, 200).iloc[-1] if len(series) >= 200 else np.nan
        ema_20 = ema(series, 20).iloc[-1]
        ema_50 = ema(series, 50).iloc[-1]

        mom = momentum_roc(series, 10).iloc[-1]
        atr_val = atr_from_close(series).iloc[-1]

        stoch_k, stoch_d = stochastic(series)
        k_val = stoch_k.iloc[-1]
        d_val = stoch_d.iloc[-1]

        # Composite score: weighted sum of sub-scores, each in [-0.5, 0.5]
        s_rsi = _score_rsi(rsi_val)
        s_macd = _score_macd(macd_val, sig_val, hist_val)
        s_bb = _score_bollinger(price, bb_u, bb_l, bb_m)
        s_trend = _score_trend(price, sma_20, sma_50, sma_200)
        s_stoch = _score_stochastic(k_val, d_val)

        # Weights: trend (30%), MACD (25%), RSI (20%), Bollinger (15%), Stochastic (10%)
        composite = (
            0.30 * s_trend
            + 0.25 * s_macd
            + 0.20 * s_rsi
            + 0.15 * s_bb
            + 0.10 * s_stoch
        )
        signal_score = round(float(np.clip(composite * 2, -1, 1)), 3)

        if signal_score > 0.2:
            trend = "bullish"
        elif signal_score < -0.2:
            trend = "bearish"
        else:
            trend = "neutral"

        abs_score = abs(signal_score)
        if abs_score > 0.5:
            momentum_label = "strong"
        elif abs_score > 0.2:
            momentum_label = "moderate"
        else:
            momentum_label = "weak"

        results[ticker] = {
            "trend": trend,
            "momentum": momentum_label,
            "signal_score": signal_score,
            "indicators": {
                "price": round(price, 2),
                "rsi_14": round(float(rsi_val), 2),
                "macd": round(float(macd_val), 4),
                "macd_signal": round(float(sig_val), 4),
                "macd_histogram": round(float(hist_val), 4),
                "bb_upper": round(float(bb_u), 2),
                "bb_middle": round(float(bb_m), 2),
                "bb_lower": round(float(bb_l), 2),
                "sma_20": round(float(sma_20), 2),
                "sma_50": round(float(sma_50), 2),
                "sma_200": round(float(sma_200), 2) if not np.isnan(sma_200) else None,
                "ema_20": round(float(ema_20), 2),
                "ema_50": round(float(ema_50), 2),
                "momentum_10w": round(float(mom), 2),
                "atr_14": round(float(atr_val), 2),
                "stoch_k": round(float(k_val), 2),
                "stoch_d": round(float(d_val), 2),
            },
        }

    return results


def technical_summary(prices_df: pd.DataFrame) -> pd.DataFrame:
    """Return a summary table of all tickers with their signals."""
    signals = generate_signals(prices_df)
    rows = []
    for ticker, data in signals.items():
        ind = data["indicators"]
        rows.append({
            "Ticker": ticker,
            "Price": ind.get("price"),
            "Trend": data["trend"],
            "Momentum": data["momentum"],
            "Score": data["signal_score"],
            "RSI": ind.get("rsi_14"),
            "MACD_Hist": ind.get("macd_histogram"),
            "BB_Position": _bb_position_label(
                ind.get("price", 0),
                ind.get("bb_upper", 0),
                ind.get("bb_lower", 0),
            ),
            "SMA_200": ind.get("sma_200"),
            "Stoch_K": ind.get("stoch_k"),
        })
    df = pd.DataFrame(rows).sort_values("Score", ascending=False).reset_index(drop=True)
    return df


def _bb_position_label(price: float, upper: float, lower: float) -> str:
    if upper == lower or upper is None or lower is None:
        return "n/a"
    pos = (price - lower) / (upper - lower)
    if pos < 0.2:
        return "oversold"
    if pos > 0.8:
        return "overbought"
    if pos < 0.4:
        return "lower band"
    if pos > 0.6:
        return "upper band"
    return "middle"
