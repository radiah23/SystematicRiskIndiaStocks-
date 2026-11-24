import java.util.HashMap;
import java.util.Map;

/**
 * Weighted PageRank by power iteration:
 *
 *   PR(v) = (1 - d) / N
 *         + d * sum_{u -> v} PR(u) * w(u,v) / W_out(u)
 *         + d * (sum of PR over dangling nodes) / N
 *
 * Each node splits its score across its outgoing edges in proportion to their weights, and a
 * node with no edges (a stock uncorrelated with everything above the threshold) spreads its
 * score evenly. Scores therefore always sum to 1.
 */
public class PageRankEngine {
    private final Graph graph;
    private final double dampingFactor;
    private final int maxIterations;
    private final double tolerance;
    private int iterationsUsed = 0;

    public PageRankEngine(Graph graph) {
        this(graph, 0.85, 1000, 1e-12);
    }

    public PageRankEngine(Graph graph, double dampingFactor, int maxIterations, double tolerance) {
        this.graph = graph;
        this.dampingFactor = dampingFactor;
        this.maxIterations = maxIterations;
        this.tolerance = tolerance;
    }

    public void run() {
        Map<String, Node> nodes = graph.getNodes();
        int n = nodes.size();
        if (n == 0) return;

        for (Node node : nodes.values()) node.setPageRankScore(1.0 / n);

        for (int it = 1; it <= maxIterations; it++) {
            double danglingMass = 0.0;
            for (Node node : nodes.values()) {
                if (node.isDangling()) danglingMass += node.getPageRankScore();
            }
            double base = (1.0 - dampingFactor) / n + dampingFactor * danglingMass / n;

            Map<String, Double> next = new HashMap<>();
            for (String t : nodes.keySet()) next.put(t, base);

            for (Node u : nodes.values()) {
                if (u.isDangling()) continue;
                double share = dampingFactor * u.getPageRankScore() / u.getOutWeight();
                for (Edge e : u.getOutEdges()) {
                    String v = e.getTarget().getTicker();
                    next.put(v, next.get(v) + share * e.getWeight());
                }
            }

            double diff = 0.0;
            for (Node node : nodes.values()) {
                double s = next.get(node.getTicker());
                diff += Math.abs(s - node.getPageRankScore());
                node.setPageRankScore(s);
            }
            iterationsUsed = it;
            if (diff < tolerance) break;
        }
        System.out.println("PageRank converged after " + iterationsUsed + " iterations");
    }

    public int getIterationsUsed() { return iterationsUsed; }
}
