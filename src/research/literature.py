"""
Academic literature backing for portfolio construction methodology.
Each citation includes: authors, year, title, journal, and relevance to our system.
"""

LITERATURE = {
    "portfolio_theory": [
        {
            "id": "markowitz1952",
            "authors": "Markowitz, H.",
            "year": 1952,
            "title": "Portfolio Selection",
            "journal": "The Journal of Finance, 7(1), 77-91",
            "relevance": "Foundation of Modern Portfolio Theory (MPT). Our mean-variance "
                         "optimization and efficient frontier construction derive directly "
                         "from this seminal work.",
        },
        {
            "id": "black_litterman1992",
            "authors": "Black, F. & Litterman, R.",
            "year": 1992,
            "title": "Global Portfolio Optimization",
            "journal": "Financial Analysts Journal, 48(5), 28-43",
            "relevance": "Black-Litterman model combines equilibrium returns with investor "
                         "views. Informs our tactical overlay on strategic allocation.",
        },
        {
            "id": "merton1969",
            "authors": "Merton, R.C.",
            "year": 1969,
            "title": "Lifetime Portfolio Selection under Uncertainty: The Continuous-Time Case",
            "journal": "Review of Economics and Statistics, 51(3), 247-257",
            "relevance": "Continuous-time portfolio theory. Supports our dynamic rebalancing "
                         "approach and leverage constraints across risk tiers.",
        },
    ],
    "risk_management": [
        {
            "id": "rockafellar_uryasev2000",
            "authors": "Rockafellar, R.T. & Uryasev, S.",
            "year": 2000,
            "title": "Optimization of Conditional Value-at-Risk",
            "journal": "Journal of Risk, 2(3), 21-42",
            "relevance": "CVaR optimization framework. Our tail risk metrics (VaR, CVaR) "
                         "and hedging decisions are grounded in this methodology.",
        },
        {
            "id": "jorion2006",
            "authors": "Jorion, P.",
            "year": 2006,
            "title": "Value at Risk: The New Benchmark for Managing Financial Risk",
            "journal": "McGraw-Hill, 3rd Edition",
            "relevance": "Industry-standard VaR methodology. Our 95% and 99% VaR "
                         "calculations follow the parametric and historical approaches described.",
        },
        {
            "id": "maillard_roncalli2010",
            "authors": "Maillard, S., Roncalli, T., & Teiletche, J.",
            "year": 2010,
            "title": "The Properties of Equally Weighted Risk Contribution Portfolios",
            "journal": "Journal of Portfolio Management, 36(4), 60-70",
            "relevance": "Risk parity allocation. Our equal risk contribution approach "
                         "for the moderate tier draws on this framework.",
        },
    ],
    "factor_investing": [
        {
            "id": "fama_french1993",
            "authors": "Fama, E.F. & French, K.R.",
            "year": 1993,
            "title": "Common Risk Factors in the Returns on Stocks and Bonds",
            "journal": "Journal of Financial Economics, 33(1), 3-56",
            "relevance": "Three-factor model (market, size, value). Our inclusion of IWM "
                         "(small-cap) and sector ETFs captures these systematic risk premia.",
        },
        {
            "id": "carhart1997",
            "authors": "Carhart, M.M.",
            "year": 1997,
            "title": "On Persistence in Mutual Fund Performance",
            "journal": "Journal of Finance, 52(1), 57-82",
            "relevance": "Four-factor model adding momentum. Our technical analysis "
                         "momentum signals are informed by this empirical evidence.",
        },
        {
            "id": "asness_moskowitz2013",
            "authors": "Asness, C.S., Moskowitz, T.J., & Pedersen, L.H.",
            "year": 2013,
            "title": "Value and Momentum Everywhere",
            "journal": "Journal of Finance, 68(3), 929-985",
            "relevance": "Cross-asset value and momentum. Supports our multi-asset "
                         "technical signal overlay across equities, bonds, and commodities.",
        },
    ],
    "diversification": [
        {
            "id": "brinson_hood1986",
            "authors": "Brinson, G.P., Hood, L.R., & Beebower, G.L.",
            "year": 1986,
            "title": "Determinants of Portfolio Performance",
            "journal": "Financial Analysts Journal, 42(4), 39-44",
            "relevance": "Asset allocation explains >90% of return variation. Justifies "
                         "our emphasis on strategic allocation across 15 ETFs spanning "
                         "equities, bonds, commodities, REITs, and TIPS.",
        },
        {
            "id": "ilmanen2011",
            "authors": "Ilmanen, A.",
            "year": 2011,
            "title": "Expected Returns: An Investor's Guide to Harvesting Market Rewards",
            "journal": "Wiley Finance",
            "relevance": "Comprehensive expected returns framework. Informs our multi-asset "
                         "class selection including TIPS for inflation protection and DBC "
                         "for commodity exposure.",
        },
        {
            "id": "ang2014",
            "authors": "Ang, A.",
            "year": 2014,
            "title": "Asset Management: A Systematic Approach to Factor Investing",
            "journal": "Oxford University Press",
            "relevance": "Systematic factor-based allocation. Supports our sector rotation "
                         "(XLK, XLF, XLE, XLV) and international diversification (EFA, EEM).",
        },
    ],
    "technical_analysis": [
        {
            "id": "jegadeesh_titman1993",
            "authors": "Jegadeesh, N. & Titman, S.",
            "year": 1993,
            "title": "Returns to Buying Winners and Selling Losers",
            "journal": "Journal of Finance, 48(1), 65-91",
            "relevance": "Empirical evidence for momentum strategies. Our RSI and "
                         "momentum indicators build on this cross-sectional momentum effect.",
        },
        {
            "id": "brock_lakonishok1992",
            "authors": "Brock, W., Lakonishok, J., & LeBaron, B.",
            "year": 1992,
            "title": "Simple Technical Trading Rules and the Stochastic Properties of Stock Returns",
            "journal": "Journal of Finance, 47(5), 1731-1764",
            "relevance": "Statistical validation of moving average and trading range "
                         "breakout rules. Supports our SMA/EMA crossover and Bollinger "
                         "Band signals.",
        },
        {
            "id": "han_yang2013",
            "authors": "Han, Y., Yang, K., & Zhou, G.",
            "year": 2013,
            "title": "A New Anomaly: The Cross-Sectional Profitability of Technical Analysis",
            "journal": "Journal of Financial and Quantitative Analysis, 48(5), 1433-1461",
            "relevance": "Cross-sectional technical analysis profitability. Validates our "
                         "composite signal scoring across multiple indicators.",
        },
    ],
    "backtesting": [
        {
            "id": "bailey_lopezdeprado2014",
            "authors": "Bailey, D.H. & Lopez de Prado, M.",
            "year": 2014,
            "title": "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest "
                     "Overfitting, and Non-Normality",
            "journal": "Journal of Portfolio Management, 40(5), 94-107",
            "relevance": "Deflated Sharpe Ratio corrects for multiple testing. Our "
                         "walk-forward backtester implements DSR to guard against overfitting.",
        },
        {
            "id": "bailey_lopezdeprado2017",
            "authors": "Bailey, D.H., Borwein, J.M., Lopez de Prado, M., & Zhu, Q.J.",
            "year": 2017,
            "title": "The Probability of Backtest Overfitting",
            "journal": "Journal of Computational Finance, 20(4), 39-69",
            "relevance": "Probability of Backtest Overfitting (PBO). Our walk-forward "
                         "methodology with out-of-sample validation directly addresses this.",
        },
        {
            "id": "harvey_liu2015",
            "authors": "Harvey, C.R., Liu, Y., & Zhu, H.",
            "year": 2015,
            "title": "... and the Cross-Section of Expected Returns",
            "journal": "Review of Financial Studies, 29(1), 5-68",
            "relevance": "Multiple testing correction for factor discovery. Informs our "
                         "conservative approach to signal validation and out-of-sample testing.",
        },
    ],
    "hedging": [
        {
            "id": "black_scholes1973",
            "authors": "Black, F. & Scholes, M.",
            "year": 1973,
            "title": "The Pricing of Options and Corporate Liabilities",
            "journal": "Journal of Political Economy, 81(3), 637-654",
            "relevance": "Black-Scholes option pricing model. Our protective put and "
                         "collar strategy pricing uses this framework.",
        },
        {
            "id": "hull2017",
            "authors": "Hull, J.C.",
            "year": 2017,
            "title": "Options, Futures, and Other Derivatives",
            "journal": "Pearson, 10th Edition",
            "relevance": "Standard derivatives pricing reference. Our tail risk hedging "
                         "and collar implementations follow the methodologies described.",
        },
    ],
    "currency_management": [
        {
            "id": "campbell_serfaty2010",
            "authors": "Campbell, J.Y., Serfaty-de Medeiros, K., & Viceira, L.M.",
            "year": 2010,
            "title": "Global Currency Hedging",
            "journal": "Journal of Finance, 65(1), 87-121",
            "relevance": "Optimal currency hedging ratios for international portfolios. "
                         "Informs our USD/ILS currency management strategy.",
        },
    ],
    "rebalancing": [
        {
            "id": "sun_fan2006",
            "authors": "Sun, W., Fan, A., Chen, L., Schouwenaars, T., & Albota, M.",
            "year": 2006,
            "title": "Optimal Rebalancing for Institutional Portfolios",
            "journal": "Journal of Portfolio Management, 32(2), 33-43",
            "relevance": "Optimal rebalancing with transaction costs. Our quarterly "
                         "rebalancing with drift thresholds follows this cost-aware approach.",
        },
        {
            "id": "masters2003",
            "authors": "Masters, S.J.",
            "year": 2003,
            "title": "Rebalancing",
            "journal": "Journal of Portfolio Management, 29(3), 52-57",
            "relevance": "Rebalancing return premium. Supports our systematic quarterly "
                         "rebalancing policy as a source of incremental return.",
        },
    ],
}


def get_all_citations() -> list:
    """Return flat list of all citations."""
    all_cites = []
    for category, papers in LITERATURE.items():
        for paper in papers:
            paper_copy = dict(paper)
            paper_copy["category"] = category
            all_cites.append(paper_copy)
    return all_cites


def get_citations_by_category(category: str) -> list:
    """Return citations for a specific methodology category."""
    return LITERATURE.get(category, [])


def format_citation(paper: dict) -> str:
    """Format a single citation in APA-like style."""
    return f"{paper['authors']} ({paper['year']}). {paper['title']}. {paper['journal']}."


def methodology_summary() -> str:
    """Return a formatted summary of all methodology backing."""
    lines = ["=" * 70, "ACADEMIC LITERATURE BACKING", "=" * 70, ""]
    for category, papers in LITERATURE.items():
        header = category.replace("_", " ").title()
        lines.append(f"--- {header} ---")
        for p in papers:
            lines.append(f"  [{p['id']}] {format_citation(p)}")
            lines.append(f"    Relevance: {p['relevance']}")
            lines.append("")
        lines.append("")
    lines.append(f"Total references: {len(get_all_citations())}")
    return "\n".join(lines)
