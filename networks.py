"""Correlation networks: raw, market-adjusted, and the minimum spanning tree.

Why a market-adjusted network: every Indian large cap loads on the same market factor, so raw
correlations mix two things, common exposure to NIFTY and direct links between firms. Removing
each stock's CAPM fit and correlating the residuals isolates the second.
"""
import numpy as np
import pandas as pd
import networkx as nx


def market_residuals(stock_rets: pd.DataFrame, mkt: pd.Series) -> pd.DataFrame:
    """Residuals from r_i = a_i + b_i * r_m + e_i, estimated stock by stock."""
    X = np.column_stack([np.ones(len(mkt)), mkt.values])
    coef, *_ = np.linalg.lstsq(X, stock_rets.values, rcond=None)
    return pd.DataFrame(stock_rets.values - X @ coef, index=stock_rets.index,
                        columns=stock_rets.columns)


def threshold_edges(corr: pd.DataFrame, threshold: float) -> pd.DataFrame:
    """Every pair with |rho| > threshold. Weight is |rho| (PageRank needs non-negative weights);
    the signed value is kept in `rho`."""
    cols = corr.columns
    rows = []
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            rho = corr.iat[i, j]
            if abs(rho) > threshold:
                rows.append((cols[i], cols[j], round(abs(rho), 6), round(rho, 6)))
    return pd.DataFrame(rows, columns=["source", "target", "weight", "rho"])


def mst_edges(corr: pd.DataFrame) -> pd.DataFrame:
    """Mantegna (1999) minimum spanning tree on the distance d_ij = sqrt(2 * (1 - rho_ij)).
    Unlike a threshold, it keeps every stock connected through its strongest link."""
    dist = np.sqrt(np.clip(2 * (1 - corr.values), 0, None))
    G = nx.Graph()
    cols = list(corr.columns)
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            G.add_edge(cols[i], cols[j], distance=dist[i, j], rho=corr.iat[i, j])
    T = nx.minimum_spanning_tree(G, weight="distance")
    return pd.DataFrame([(a, b, round(d["rho"], 6)) for a, b, d in T.edges(data=True)],
                        columns=["source", "target", "rho"])


def within_sector_share(edges: pd.DataFrame, sectors: dict) -> float:
    if edges.empty:
        return float("nan")
    same = [sectors[a] == sectors[b] for a, b in zip(edges["source"], edges["target"])]
    return float(np.mean(same))
