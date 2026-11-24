"""Streamlit dashboard.  Run:  streamlit run Dashboard.py  (after python run_pipeline.py)"""
import json

import networkx as nx
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import config

R = config.RESULTS_DIR
SECTOR_COLORS = dict(zip(sorted(set(config.STOCKS.values())), px.colors.qualitative.Safe))
NETWORKS = {
    "Correlation (threshold)": "corr",
    "Minimum spanning tree": "mst",
    "Market-adjusted correlation": "resid",
    "Diebold-Yilmaz spillovers (directed)": "spill",
}
WINDOWS = {"2020-2024 (main)": "main", "2018-2019 (pre-crisis)": "pre"}
LABELS = {
    "beta": "CAPM beta", "mes": "MES (5%)", "delta_covar": "Delta-CoVaR (5%)",
    "pr_corr": "PageRank: correlation", "pr_resid": "PageRank: market-adjusted",
    "pr_spill": "PageRank: spillover", "to_others": "Spillover TO others",
    "from_others": "Spillover FROM others", "net": "Net spillover", "ann_vol": "Volatility",
    "crash_return": "COVID crash return",
}

st.set_page_config(page_title="Systemic Risk in Indian Equities", layout="wide")
st.title("Systemic Risk in Indian Large-Cap Equities")
st.caption("Network centrality vs. market-based systemic-risk measures, 19 NSE stocks")

if not (R / "summary.md").exists():
    st.info("No results yet. Run `python run_pipeline.py` first, then reload this page.")
    st.stop()

meta = json.loads((R / "meta.json").read_text())
panels = {w: pd.read_csv(R / f"panel_{w}.csv", index_col="ticker") for w in ("main", "pre")}

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total connectedness 2020-24", f"{meta['main']['tci']:.1f}")
c2.metric("Total connectedness 2018-19", f"{meta['pre']['tci']:.1f}")
c3.metric("COVID crash, NIFTY 50", f"{meta['crash']['market_return']:.1%}")
c4.metric("Crash window", f"{meta['crash']['peak']} to {meta['crash']['trough']}")

tab_net, tab_tci, tab_risk, tab_crash = st.tabs(
    ["Network", "Connectedness over time", "Risk measures", "Pre-crisis test"])

# ---------------------------------------------------------------- network
with tab_net:
    a, b, c = st.columns(3)
    net_label = a.selectbox("Network", list(NETWORKS))
    win_label = b.selectbox("Window", list(WINDOWS))
    size_by = c.selectbox("Node size", ["pr_corr", "pr_resid", "pr_spill", "net", "beta", "mes"],
                          format_func=LABELS.get)
    net, win = NETWORKS[net_label], WINDOWS[win_label]
    panel = panels[win]

    directed = net == "spill"
    if net == "mst":
        edges = pd.read_csv(R / f"mst_{win}.csv").assign(weight=lambda d: d["rho"].abs())
    else:
        edges = pd.read_csv(R / f"edges_{net}_{win}.csv")
    if directed:
        top_n = st.slider("Strongest spillover links shown", 10, 100, 40, 5)
        # stored as receiver -> transmitter for PageRank; draw as transmitter -> receiver
        edges = edges.nlargest(top_n, "weight").rename(columns={"source": "target", "target": "source"})

    G = nx.DiGraph() if directed else nx.Graph()
    G.add_nodes_from(config.STOCKS)
    G.add_weighted_edges_from(edges[["source", "target", "weight"]].itertuples(index=False))
    pos = nx.spring_layout(G.to_undirected(), seed=7, weight="weight", k=0.9)

    fig = go.Figure()
    wmax = edges["weight"].max() if len(edges) else 1
    for s, t, w in edges[["source", "target", "weight"]].itertuples(index=False):
        (x0, y0), (x1, y1) = pos[s], pos[t]
        fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode="lines", hoverinfo="skip",
                                 line=dict(width=0.5 + 3 * w / wmax, color="rgba(120,120,120,0.5)"),
                                 showlegend=False))
        if directed:
            fig.add_annotation(x=x1, y=y1, ax=x0, ay=y0, xref="x", yref="y", axref="x", ayref="y",
                               showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1,
                               arrowcolor="rgba(120,120,120,0.6)", standoff=12)
    vals = panel[size_by]
    scaled = (vals - vals.min()) / (vals.max() - vals.min() + 1e-12)
    if size_by == "mes":
        scaled = 1 - scaled        # more negative MES = riskier = bigger
    for sector, color in SECTOR_COLORS.items():
        nodes = [t for t in config.STOCKS if config.STOCKS[t] == sector]
        fig.add_trace(go.Scatter(
            x=[pos[t][0] for t in nodes], y=[pos[t][1] for t in nodes], mode="markers+text",
            name=sector, text=[t.replace(".NS", "") for t in nodes], textposition="top center",
            marker=dict(size=[14 + 36 * scaled[t] for t in nodes], color=color,
                        line=dict(width=1, color="white")),
            hovertext=[f"{t}<br>{LABELS[size_by]}: {vals[t]:.4f}<br>beta {panel.at[t, 'beta']:.2f}"
                       f"<br>net spillover {panel.at[t, 'net']:.1f}" for t in nodes],
            hoverinfo="text"))
    fig.update_layout(height=620, xaxis=dict(visible=False), yaxis=dict(visible=False),
                      margin=dict(l=10, r=10, t=10, b=10), legend_title="Sector")
    st.plotly_chart(fig, width="stretch")
    st.caption({
        "corr": f"Edge when daily-return correlation exceeds {config.CORR_THRESHOLD}. Stocks below the cut for every pair are left isolated.",
        "mst": "Mantegna minimum spanning tree: every stock joined through its strongest correlations, 18 edges.",
        "resid": f"Correlation after removing each stock's exposure to NIFTY 50 (edge when > {config.RESID_THRESHOLD}). What is left is direct, mostly sector, linkage.",
        "spill": "Arrow from j to i: shocks to j explain part of i's 10-day forecast-error variance (Diebold-Yilmaz).",
    }[net])

# ---------------------------------------------------------------- rolling TCI
with tab_tci:
    tci = pd.read_csv(R / "connectedness_rolling.csv", parse_dates=["date"])
    fig = px.line(tci, x="date", y="tci", labels={"tci": "Total connectedness index", "date": ""})
    for d, label in config.EVENTS.items():
        fig.add_vline(x=pd.Timestamp(d), line_dash="dot", line_color="gray")
        fig.add_annotation(x=pd.Timestamp(d), y=tci["tci"].max(), text=label, showarrow=False,
                           textangle=-90, xanchor="right", font=dict(size=11))
    fig.update_layout(height=450)
    st.plotly_chart(fig, width="stretch")
    st.caption(f"Diebold-Yilmaz index on a rolling {config.ROLL_WINDOW}-day window, re-estimated every "
               f"{config.ROLL_STEP} days and dated at the window's last day. Higher = a larger share "
               "of each stock's risk comes from shocks to the other stocks.")

# ---------------------------------------------------------------- risk table + scatter
with tab_risk:
    win = WINDOWS[st.selectbox("Window ", list(WINDOWS))]
    panel = panels[win]
    cols = ["sector", "beta", "beta_t_nw", "mes", "delta_covar", "to_others", "from_others", "net",
            "pr_corr", "pr_resid", "pr_spill"]
    st.dataframe(panel[cols].sort_values("net", ascending=False).style.format(precision=3),
                 width="stretch")
    a, b = st.columns(2)
    x = a.selectbox("x", ["pr_corr", "pr_resid", "pr_spill", "to_others", "net"], format_func=LABELS.get)
    y = b.selectbox("y", ["mes", "delta_covar", "beta"], format_func=LABELS.get)
    d = panel.reset_index()
    fig = px.scatter(d, x=x, y=y, color="sector", text=d["ticker"].str.replace(".NS", ""),
                     color_discrete_map=SECTOR_COLORS, labels=LABELS, trendline="ols",
                     trendline_scope="overall")
    fig.update_traces(textposition="top center")
    st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------- crisis test
with tab_crash:
    st.markdown("Every measure below is estimated on **2018-2019 data only**, then compared with "
                f"each stock's return over the COVID crash ({meta['crash']['peak']} to "
                f"{meta['crash']['trough']}). Negative rho: higher score, bigger loss.")
    q2 = pd.read_csv(R / "q2_precrisis_vs_crash.csv")
    st.dataframe(q2.style.format({"spearman_rho": "{:.2f}", "p_value": "{:.3f}"}),
                 width="stretch", hide_index=True)
    st.markdown("**Does centrality add anything once beta is known?** (OLS, HC3 errors)")
    st.dataframe(pd.read_csv(R / "q2_incremental_over_beta.csv").style.format(precision=3),
                 width="stretch", hide_index=True)
    pre = panels["pre"].reset_index()
    pick = st.selectbox("Pre-crisis measure", ["beta", "mes", "delta_covar", "pr_corr", "pr_spill", "net"],
                        format_func=LABELS.get)
    fig = px.scatter(pre, x=pick, y="crash_return", color="sector", color_discrete_map=SECTOR_COLORS,
                     text=pre["ticker"].str.replace(".NS", ""), labels=LABELS, trendline="ols",
                     trendline_scope="overall")
    fig.update_traces(textposition="top center")
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig, width="stretch")
