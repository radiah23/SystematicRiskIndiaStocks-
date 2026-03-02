import java.util.ArrayList;
import java.util.HashMap;

public class Graph {
    private HashMap<String, Node> nodes;
    private ArrayList<Edge> edges;

    public Graph() {
        this.nodes = new HashMap<>();
        this.edges = new ArrayList<>();
    }

    public void addNode(String ticker) {
        if (!nodes.containsKey(ticker)) {
            nodes.put(ticker, new Node(ticker));
        }
    }

    public void addEdge(String tickerA, String tickerB, double weight) {
        Node source = nodes.get(tickerA);
        Node target = nodes.get(tickerB);
        if (source != null && target != null) {
            edges.add(new Edge(source, target, weight));
        }
    }

    public HashMap<String, Node> getNodes() {
        return nodes;
    }

    public ArrayList<Edge> getEdges() {
        return edges;
    }

    public void printGraph() {
        System.out.println("Nodes: " + nodes.keySet());
        System.out.println("Edges:");
        for (Edge e : edges) {
            System.out.println("  " + e);
        }
    }
}
