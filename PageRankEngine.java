import java.util.HashMap;
import java.util.ArrayList;

public class PageRankEngine {
    private Graph graph;
    private double dampingFactor;
    private int maxIterations;
    private double tolerance;

    public PageRankEngine(Graph graph) {
        this.graph = graph;
        this.dampingFactor = 0.85;
        this.maxIterations = 100;
        this.tolerance = 0.0001;
    }

    public void run() {
        HashMap<String, Node> nodes = graph.getNodes();
        ArrayList<Edge> edges = graph.getEdges();
        int n = nodes.size();

        // initialize all scores to 1/n
        for (Node node : nodes.values()) {
            node.setPageRankScore(1.0 / n);
        }

        // iterate
        for (int i = 0; i < maxIterations; i++) {
            HashMap<String, Double> newScores = new HashMap<>();

            for (String ticker : nodes.keySet()) {
                newScores.put(ticker, (1.0 - dampingFactor) / n);
            }

            for (Edge edge : edges) {
                String source = edge.getSource().getTicker();
                String target = edge.getTarget().getTicker();
                double contribution = dampingFactor * edge.getSource().getPageRankScore() * edge.getWeight();
                newScores.put(target, newScores.get(target) + contribution);
            }

            // check convergence
            double diff = 0;
            for (String ticker : nodes.keySet()) {
                diff += Math.abs(newScores.get(ticker) - nodes.get(ticker).getPageRankScore());
                nodes.get(ticker).setPageRankScore(newScores.get(ticker));
            }

            if (diff < tolerance) {
                System.out.println("Converged after " + (i+1) + " iterations");
                break;
            }
        }
    }
}
