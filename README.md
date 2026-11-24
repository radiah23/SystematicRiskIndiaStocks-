# Systemic Risk in Indian Equities: Network Centrality vs. Market-Based Risk Measures

**Which Indian large caps would spread a shock to the rest of the market, and could you have spotted them before the COVID crash?**

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Java](https://img.shields.io/badge/Java-ED8B00?logo=openjdk&logoColor=white)
![statsmodels](https://img.shields.io/badge/statsmodels-4051B5)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)

Regulators care about *systemic* risk: not how risky a firm is on its own, but how much its distress would spill over to everyone else. The Reserve Bank of India, for example, names SBI, HDFC Bank and ICICI Bank as domestic systemically important banks (D-SIBs) and makes them hold extra capital. This project measures systemic importance for 19 NSE large caps in two ways and checks whether they agree:

1. **Network measures:** build a network of stocks and score how central each one is, using PageRank engines written from scratch in Java.
2. **Market-based measures from the finance literature:** CAPM beta, Marginal Expected Shortfall, Delta-CoVaR, and Diebold-Yilmaz spillovers.

It then runs an **out-of-sample test**: using only 2018-2019 data, which measure best predicts how much each stock lost in the COVID crash of early 2020?

---

## Research questions

| | Question | Method |
|---|---|---|
| Q1 | Do network-centrality scores line up with standard systemic-risk measures? | Spearman rank correlations, 2020-2024 |
| Q2 | Which pre-crisis (2018-2019) measure best predicts each stock's COVID-crash loss? | Spearman correlation with peak-to-trough return |
| Q2b | Does network centrality add information once you know a stock's beta? | OLS of crash return on beta + centrality, HC3 standard errors |
| Benchmark | Do the measures rank the RBI's three D-SIBs as systemically important? | Rank of SBI, HDFC Bank, ICICI Bank under each measure |

## Measures

**Networks** (`networks.py`, `spillover.py`, `java/`)

| Network | Link between two stocks | Why |
|---|---|---|
| Correlation | daily-return correlation > 0.5 | the original project's network |
| Minimum spanning tree | strongest correlations joining all 19 stocks (Mantegna, 1999) | a fixed threshold leaves stocks isolated; the tree never does |
| Market-adjusted | correlation of CAPM residuals > 0.2 | raw correlation mixes common NIFTY exposure with direct links; this keeps only the direct links |
| Diebold-Yilmaz spillover | share of stock *i*'s 10-day forecast-error variance caused by shocks to *j*, from a VAR(1) with generalized variance decomposition (Diebold & Yilmaz, 2012, 2014) | correlation is symmetric; spillovers have a direction, so you can separate net **transmitters** of shocks from net **receivers** |

PageRank (damping 0.85) is computed on each network. For the spillover network, edges point from receiver to transmitter, so PageRank rewards the stocks whose shocks explain the variance of other important stocks.

**Market-based risk measures** (`risk_measures.py`)

| Measure | Definition | Source |
|---|---|---|
| CAPM beta | slope of stock on NIFTY 50 returns, Newey-West t-stat | — |
| MES (5%) | stock's average return on the market's worst 5% of days | Acharya, Pedersen, Philippon & Richardson (2017) |
| Delta-CoVaR (5%) | change in the market's 5% quantile when the stock moves from its median to its own 5% quantile (quantile regression) | Adrian & Brunnermeier (2016) |
| Total connectedness index | average share of each stock's risk coming from the others, on a rolling 250-day window | Diebold & Yilmaz (2014) |

## Pipeline

```
yfinance adjusted prices, 19 stocks + NIFTY 50, 2018-2024   data.py  -> data/prices.csv
        │
        ├── estimate.py   for each window (2018-19 pre-crisis, 2020-24 main):
        │                   correlation / MST / market-adjusted networks
        │                   VAR + generalized FEVD spillover network
        │                   beta, MES, Delta-CoVaR
        │                 COVID crash window (NIFTY peak to trough), rolling connectedness
        ├── java/         weighted PageRank on each network (undirected or directed)
        ├── analysis.py   Q1, Q2, D-SIB benchmark -> results/summary.md
        └── Dashboard.py  Streamlit: networks, rolling connectedness, risk table, crisis test
```

## Run it

```bash
pip install -r requirements.txt
python run_pipeline.py          # downloads prices on first run, then reuses data/prices.csv
streamlit run Dashboard.py
python -m pytest tests          # unit tests on synthetic data with known answers
```

Requires Java 11+ (`javac` on your PATH). Results land in `results/`; `results/summary.md` has every table.

## Correction to the earlier version

The first version's Java PageRank had a bug: it stored each correlation edge in one direction only (alphabetical order of the tickers) and did not divide a node's score by its total edge weight. The ranking therefore depended on ticker names. HCL Tech, alphabetically first, could only receive the minimum score, and the scores did not sum to 1. It also dropped the 9 stocks with no edge above 0.5.

On the same 12-edge network, the fixed engine (checked against `networkx`) gives:

| | Old (buggy) | Fixed |
|---|---|---|
| #1 | Wipro | ICICI Bank |
| #2 | TCS | HDFC Bank |
| #3 | SBI | Infosys |
| Wipro | 1st | 8th |
| Stocks ranked | 10 | 19 |

Reliance, the largest stock in the NIFTY 50, still comes last in the fixed threshold network because none of its correlations clears 0.5. That shows how much a fixed threshold can hide, and it's why the minimum spanning tree, market-adjusted and spillover networks were added.

## Results

Run `python run_pipeline.py` to produce `results/summary.md`. It reports network structure, the net-spillover ranking, Q1, Q2 and the D-SIB benchmark.

## Limitations

- **19 stocks.** Cross-sectional tests have little power. Treat p-values as suggestive, not conclusive. Extending to the full NIFTY 50 is the obvious next step, but historical index membership would be needed to avoid survivorship bias.
- **Daily data, VAR(1).** At a daily frequency, much of the generalized variance decomposition reflects same-day correlation rather than lead-lag effects, so "direction" partly mirrors how strongly each stock loads on common shocks. Volatility-based spillovers or intraday data would sharpen this.
- **Unconditional Delta-CoVaR.** It omits the macro state variables (rates, volatility index) used by Adrian & Brunnermeier.
- **One crisis.** The out-of-sample test uses one event. Other stress episodes, such as the January 2023 Adani sell-off, would show whether the result generalizes.
- **Equity data only.** Market-based measures miss balance-sheet exposures (interbank lending, common asset holdings) that regulators use for D-SIB scoring.

## References

- Acharya, V., Pedersen, L., Philippon, T., & Richardson, M. (2017). Measuring systemic risk. *Review of Financial Studies*, 30(1), 2-47.
- Adrian, T., & Brunnermeier, M. (2016). CoVaR. *American Economic Review*, 106(7), 1705-1741.
- Diebold, F., & Yilmaz, K. (2012). Better to give than to receive: Predictive directional measurement of volatility spillovers. *International Journal of Forecasting*, 28(1), 57-66.
- Diebold, F., & Yilmaz, K. (2014). On the network topology of variance decompositions: Measuring the connectedness of financial firms. *Journal of Econometrics*, 182(1), 119-134.
- Mantegna, R. (1999). Hierarchical structure in financial markets. *European Physical Journal B*, 11(1), 193-197.
- Pesaran, H., & Shin, Y. (1998). Generalized impulse response analysis in linear multivariate models. *Economics Letters*, 58(1), 17-29.
- Reserve Bank of India (2025). 2025 list of Domestic Systemically Important Banks.

## Author

**Radiah Khan** · [Portfolio](https://radiah23.github.io) · [LinkedIn](https://www.linkedin.com/in/radiah-khan/)
