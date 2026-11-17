# SysRisk-SA: Network-Based Systemic Risk in Indian Equities

**Which Indian large-cap stocks sit at the center of the market, so that trouble there would spread fastest?**

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Java](https://img.shields.io/badge/Java-ED8B00?logo=openjdk&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?logo=plotly&logoColor=white)

This project treats 19 NSE-listed stocks as a network: two stocks are linked when their daily returns move together strongly. A PageRank engine written from scratch in Java then scores how central each stock is in that network, which serves as a proxy for systemic importance. Finally, the scores are tested against each stock's market beta and shown in an interactive Streamlit dashboard.

---

## Pipeline

```
yfinance prices (2020–2024)
        │  scrape_india.py
        ▼
daily returns → correlation matrix → edges.csv   (|ρ| > 0.5)
        │  Main.java + PageRankEngine.java
        ▼
weighted PageRank (damping 0.85) → pagerank_results.json
        │                                   │
        │  analysis.py                      │  Dashboard.py
        ▼                                   ▼
beta vs. NIFTY 50 + regression      interactive network (Streamlit + Plotly)
```

1. **Build the network** (`scrape_india.py`): downloads five years of daily closing prices for 19 stocks across banking, IT, energy, FMCG, pharma, telecom and autos; computes daily returns and the pairwise correlation matrix; keeps an edge wherever the correlation is above 0.5.
2. **Score centrality** (`Main.java`, `Graph.java`, `Node.java`, `Edge.java`, `PageRankEngine.java`, `GraphExporter.java`): an object-oriented graph implementation and an iterative, correlation-weighted PageRank (damping factor 0.85, runs until convergence), exported to JSON.
3. **Test against market risk** (`analysis.py`): computes each stock's beta against the NIFTY 50 and regresses beta on PageRank score.
4. **Visualize** (`Dashboard.py`): a Streamlit app with a spring-layout network where node size and color scale with PageRank, plus a ranked table.

## Results

**The network splits into three sector clusters.** Of 171 possible stock pairs, 12 cleared the 0.5 correlation threshold, and every one of them links two stocks in the same sector:

- **IT**: TCS, Infosys, Wipro, HCL Tech (all six pairs connected; strongest link TCS–Infosys, ρ = 0.71)
- **Private and public banks**: HDFC Bank, ICICI Bank, Kotak Mahindra Bank, SBI
- **Consumer staples**: Hindustan Unilever–Nestlé India

**Most central stocks (PageRank):**

| Rank | Stock | PageRank |
|---|---|---|
| 1 | Wipro | 0.055 |
| 2 | TCS | 0.038 |
| 3 | State Bank of India | 0.035 |
| 4 | Kotak Mahindra Bank | 0.034 |
| 5 | Infosys | 0.024 |

**Centrality did not predict beta.** The regression of market beta on PageRank score was not statistically significant. Being tightly linked to sector peers is a different kind of risk from moving with the overall index, which suggests the two measures capture different things.

## Tech stack

- **Python**: `yfinance`, `pandas`, `NumPy`, `SciPy` (linear regression), `networkx`, `Plotly`, `Streamlit`
- **Java**: custom `Graph` / `Node` / `Edge` classes, PageRank engine, JSON exporter

## Run it yourself

```bash
pip install yfinance pandas numpy scipy networkx plotly streamlit

# 1. Download prices and build the correlation network (writes edges.csv)
python scrape_india.py

# 2. Compute PageRank in Java (writes pagerank_results.json)
#    Main.java reads ../edges.csv and writes ../pagerank_results.json,
#    so compile and run it from a folder one level below this one,
#    or change those two paths to "edges.csv" / "pagerank_results.json".
javac *.java
java Main

# 3. Beta vs. PageRank regression
python analysis.py

# 4. Launch the dashboard
streamlit run Dashboard.py
```

`edges.csv` and `pagerank_results.json` are already included, so you can jump straight to steps 3 and 4.

## Limitations and next steps

- A fixed 0.5 threshold drops weaker cross-sector links; a threshold sweep or a minimum spanning tree would show more of the structure.
- Correlations are measured over the whole 2020–2024 window; rolling windows would show how the network tightens during stress periods.
- 19 stocks is a small sample; extending to the full NIFTY 50 would give the beta regression more power.

## Author

**Radiah Khan** · [Portfolio](https://radiah23.github.io) · [LinkedIn](https://www.linkedin.com/in/radiah-khan/)
