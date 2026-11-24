"""Estimate networks and risk measures for each window and write them to results/.

Windows:
  main : 2020-2024, the full-sample description
  pre  : 2018-2019, everything measured before the COVID crash, for the out-of-sample test
"""
import json

import numpy as np
import pandas as pd

import config
import networks as nw
import risk_measures as rm
import spillover as sp
from data import load_prices, log_returns

WINDOWS = {
    "main": (config.MAIN_START, config.MAIN_END),
    "pre": (config.PRE_START, config.PRE_END),
}


def estimate_window(prices: pd.DataFrame, name: str, start, end, out) -> dict:
    rets = log_returns(prices, start, end)
    stocks, mkt = rets[list(config.STOCKS)], rets[config.MARKET]

    corr = stocks.corr()
    resid_corr = nw.market_residuals(stocks, mkt).corr()

    edges_corr = nw.threshold_edges(corr, config.CORR_THRESHOLD)
    edges_resid = nw.threshold_edges(resid_corr, config.RESID_THRESHOLD)

    edges_corr.to_csv(out / f"edges_corr_{name}.csv", index=False)
    edges_resid.to_csv(out / f"edges_resid_{name}.csv", index=False)
    nw.mst_edges(corr).to_csv(out / f"mst_{name}.csv", index=False)
    corr.to_csv(out / f"corr_{name}.csv")

    theta, dy_table, tci = sp.connectedness(stocks, config.VAR_LAGS, config.FEVD_HORIZON)
    theta.to_csv(out / f"theta_{name}.csv")
    sp.spillover_edges(theta).to_csv(out / f"edges_spill_{name}.csv", index=False)

    risk = rm.risk_table(stocks, mkt, config.TAIL_Q).join(dy_table)
    risk.insert(0, "sector", [config.STOCKS[t] for t in risk.index])
    risk.to_csv(out / f"risk_{name}.csv")

    return {
        "window": [str(rets.index[0].date()), str(rets.index[-1].date())],
        "n_days": int(len(rets)),
        "n_edges_corr": int(len(edges_corr)),
        "n_edges_resid": int(len(edges_resid)),
        "within_sector_share_corr": nw.within_sector_share(edges_corr, config.STOCKS),
        "within_sector_share_resid": nw.within_sector_share(edges_resid, config.STOCKS),
        "mean_pairwise_corr": float(corr.values[np.triu_indices(len(corr), 1)].mean()),
        "tci": tci,
    }


def main():
    out = config.RESULTS_DIR
    out.mkdir(exist_ok=True)
    prices = load_prices()

    pd.Series(config.STOCKS, name="sector").rename_axis("ticker").to_csv(out / "nodes.csv")

    meta = {name: estimate_window(prices, name, s, e, out) for name, (s, e) in WINDOWS.items()}

    peak, trough = rm.crash_window(prices[config.MARKET], config.CRASH_SEARCH_START,
                                   config.CRASH_SEARCH_END)
    crash = rm.crash_returns(prices, peak, trough)
    crash.rename("crash_return").rename_axis("ticker").to_csv(out / "crash_returns.csv")
    meta["crash"] = {"peak": str(peak.date()), "trough": str(trough.date()),
                     "market_return": float(crash[config.MARKET])}

    all_rets = log_returns(prices)[list(config.STOCKS)]
    sp.rolling_tci(all_rets, config.ROLL_WINDOW, config.ROLL_STEP, config.VAR_LAGS,
                   config.FEVD_HORIZON).rename_axis("date").to_csv(out / "connectedness_rolling.csv")

    with open(out / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
