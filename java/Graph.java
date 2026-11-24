import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Weighted graph of stocks.
 *
 * Undirected mode (correlation network): each edge is stored in both directions, so a link
 * between A and B lets score flow both ways. The original version stored only A -> B in the
 * order the CSV listed the pair (alphabetical), which made the ranking depend on ticker names.
 *
 * Directed mode (spillover network): an edge i -> j means "part of i's forecast-error variance
 * comes from shocks to j", so PageRank flows toward the stocks that transmit shocks.
 */
public class Graph {
    private final boolean directed;
    private final Map<String, Node> nodes = new LinkedHashMap<>();
    private final List<Edge> edges = new ArrayList<>();

    public Graph(boolean directed) {
        this.directed = directed;
    }

    public boolean isDirected() { return directed; }

    public Node addNode(String ticker) {
        return nodes.computeIfAbsent(ticker, Node::new);
    }

    public void addEdge(String tickerA, String tickerB, double weight) {
        if (tickerA.equals(tickerB)) return;          // self-loops carry no network information
        Node a = addNode(tickerA);
        Node b = addNode(tickerB);
        link(a, b, weight);
        if (!directed) link(b, a, weight);
    }

    private void link(Node from, Node to, double weight) {
        Edge e = new Edge(from, to, weight);
        edges.add(e);
        from.addOutEdge(e);
    }

    public Map<String, Node> getNodes() { return nodes; }
    public List<Edge> getEdges() { return edges; }

    public void printGraph() {
        System.out.println((directed ? "Directed" : "Undirected") + " graph: "
            + nodes.size() + " nodes, " + (directed ? edges.size() : edges.size() / 2) + " edges");
    }
}
