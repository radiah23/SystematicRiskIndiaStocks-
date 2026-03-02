import json
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import streamlit as st

# load data
with open("pagerank_results.json", "r") as f:
    pagerank_data = json.load(f)

pr_df = pd.DataFrame(pagerank_data)

edges_df = pd.read_csv("edges.csv")

# build networkx graph
G = nx.Graph()

for _, row in edges_df.iterrows():
    G.add_edge(row["stock_a"], row["stock_b"], weight=row["weight"])

# get positions
pos = nx.spring_layout(G, seed=42)

# build plotly figure
edge_x, edge_y = [], []
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=1, color="#888"),
    hoverinfo="none",
    mode="lines"
)

node_x, node_y, node_text, node_size = [], [], [], []

for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    pr_score = pr_df[pr_df["ticker"] == node]["pagerank"].values[0]
    node_text.append(f"{node}<br>PageRank: {round(pr_score, 4)}")
    node_size.append(pr_score * 1000)

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode="markers+text",
    hoverinfo="text",
    text=[n.replace(".NS", "") for n in G.nodes()],
    textposition="top center",
    hovertext=node_text,
    marker=dict(
        size=node_size,
        color=node_size,
        colorscale="Reds",
        showscale=True,
        colorbar=dict(title="Systemic Risk")
    )
)

fig = go.Figure(data=[edge_trace, node_trace],
    layout=go.Layout(
        title="SysRisk-SA: India Equity Systemic Risk Network",
        showlegend=False,
        hovermode="closest",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
)

# streamlit app
st.title("SysRisk-SA")
st.subheader("Network-Based Systemic Risk Analyzer — Indian Equity Markets")
st.plotly_chart(fig, use_container_width=True)
st.subheader("PageRank Rankings")
st.dataframe(pr_df.sort_values("pagerank", ascending=False))