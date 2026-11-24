import json
import subprocess

import networkx as nx
import numpy as np
import pandas as pd

import config


def _java_pagerank(tmp_path, edges: pd.DataFrame, nodes: list, directed: bool) -> pd.Series:
    import run_pipeline
    build = tmp_path / "jbuild"
    build.mkdir(exist_ok=True)
    subprocess.run(["javac", "-d", str(build), *map(str, run_pipeline.JAVA_SRC.glob("*.java"))],
                   check=True)
    e, n, o = tmp_path / "e.csv", tmp_path / "n.csv", tmp_path / "o.json"
    edges.to_csv(e, index=False)
    pd.DataFrame({"ticker": nodes}).to_csv(n, index=False)
    cmd = ["java", "-cp", str(build), "Main", str(e), str(n), str(o)] + (["--directed"] if directed else [])
    subprocess.run(cmd, check=True, capture_output=True)
    return pd.read_json(o).set_index("ticker")["pagerank"]


def test_java_pagerank_matches_networkx_undirected(tmp_path):
    edges = pd.DataFrame({"source": ["A", "A", "B", "D"], "target": ["B", "C", "C", "E"],
                          "weight": [0.7, 0.55, 0.6, 0.9]})
    nodes = list("ABCDEF")                     # F is isolated and must still get a score
    java = _java_pagerank(tmp_path, edges, nodes, directed=False)
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_weighted_edges_from(edges.itertuples(index=False))
    ref = pd.Series(nx.pagerank(G, alpha=0.85, weight="weight", tol=1e-12, max_iter=10000))
    assert set(java.index) == set(nodes)
    assert np.isclose(java.sum(), 1)
    assert np.allclose(java.sort_index(), ref.sort_index(), atol=1e-8)


def test_java_pagerank_matches_networkx_directed(tmp_path):
    edges = pd.DataFrame({"source": ["A", "B", "C", "C", "D"], "target": ["B", "C", "A", "D", "A"],
                          "weight": [1.0, 2.0, 0.5, 1.5, 3.0]})
    nodes = list("ABCDE")                      # E is dangling
    java = _java_pagerank(tmp_path, edges, nodes, directed=True)
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_weighted_edges_from(edges.itertuples(index=False))
    ref = pd.Series(nx.pagerank(G, alpha=0.85, weight="weight", tol=1e-12, max_iter=10000))
    assert np.allclose(java.sort_index(), ref.sort_index(), atol=1e-8)


def test_full_pipeline_on_synthetic_data(sandbox, monkeypatch):
    import run_pipeline
    monkeypatch.setattr(run_pipeline, "JAVA_BUILD", sandbox / "jbuild")
    import estimate, analysis
    monkeypatch.setattr(analysis, "R", config.RESULTS_DIR)

    estimate.main()
    run_pipeline.run_java()
    analysis.main()

    r = config.RESULTS_DIR
    meta = json.loads((r / "meta.json").read_text())
    # synthetic crash runs 2020-02-20 to 2020-03-23
    assert "2020-03-13" <= meta["crash"]["trough"] <= "2020-03-31"
    assert meta["crash"]["market_return"] < -0.2
    panel = pd.read_csv(r / "panel_main.csv", index_col="ticker")
    assert len(panel) == len(config.STOCKS)
    assert panel[["pr_corr", "pr_resid", "pr_spill"]].notna().all().all()
    assert np.allclose(panel[["pr_corr", "pr_resid", "pr_spill"]].sum(), 1)
    # betas were simulated as 0.6 + 0.05 * i; estimates should track them closely
    true_beta = pd.Series([0.6 + 0.05 * i for i in range(len(config.STOCKS))], index=list(config.STOCKS))
    assert np.corrcoef(panel.loc[true_beta.index, "beta"], true_beta)[0, 1] > 0.95
    # sector factors exist, so the market-adjusted network should be mostly within-sector
    assert meta["main"]["within_sector_share_resid"] > 0.8
    assert (r / "summary.md").read_text().startswith("# Results summary")
    assert len(pd.read_csv(r / "connectedness_rolling.csv")) > 5
