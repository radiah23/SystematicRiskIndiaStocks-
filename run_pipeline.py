"""Run the whole project end to end:

  python run_pipeline.py            # uses cached data/prices.csv if present
  python run_pipeline.py --refresh  # re-download prices first
"""
import subprocess
import sys

import config
import analysis
import estimate
from data import load_prices

JAVA_SRC = config.ROOT / "java"
JAVA_BUILD = JAVA_SRC / "build"


def run_java():
    JAVA_BUILD.mkdir(exist_ok=True)
    subprocess.run(["javac", "-d", str(JAVA_BUILD), *map(str, JAVA_SRC.glob("*.java"))], check=True)
    r, nodes = config.RESULTS_DIR, config.RESULTS_DIR / "nodes.csv"
    for window in estimate.WINDOWS:
        for net, directed in (("corr", False), ("resid", False), ("spill", True)):
            cmd = ["java", "-cp", str(JAVA_BUILD), "Main", str(r / f"edges_{net}_{window}.csv"),
                   str(nodes), str(r / f"pagerank_{net}_{window}.json")]
            if directed:
                cmd.append("--directed")
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)


if __name__ == "__main__":
    load_prices(refresh="--refresh" in sys.argv)
    estimate.main()
    run_java()
    analysis.main()
    print("\nDone. See results/summary.md, or run:  streamlit run Dashboard.py")
