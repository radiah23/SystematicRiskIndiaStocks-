import java.util.ArrayList;
import java.util.List;

/** A stock in the network. Holds its outgoing edges so PageRank can split its score across them. */
public class Node {
    private final String ticker;
    private final List<Edge> outEdges = new ArrayList<>();
    private double outWeight = 0.0;
    private double pageRankScore = 0.0;

    public Node(String ticker) {
        this.ticker = ticker;
    }

    void addOutEdge(Edge e) {
        outEdges.add(e);
        outWeight += e.getWeight();
    }

    public String getTicker() { return ticker; }
    public List<Edge> getOutEdges() { return outEdges; }
    public double getOutWeight() { return outWeight; }
    public boolean isDangling() { return outWeight <= 0.0; }
    public double getPageRankScore() { return pageRankScore; }
    public void setPageRankScore(double score) { this.pageRankScore = score; }

    @Override
    public String toString() {
        return String.format("%-15s PageRank: %.4f", ticker, pageRankScore);
    }
}
