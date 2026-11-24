/** A weighted, directed link from source to target. Undirected graphs store one Edge each way. */
public class Edge {
    private final Node source;
    private final Node target;
    private final double weight;

    public Edge(Node source, Node target, double weight) {
        if (weight < 0) {
            throw new IllegalArgumentException("PageRank needs non-negative weights; got " + weight
                + " on " + source.getTicker() + " -> " + target.getTicker());
        }
        this.source = source;
        this.target = target;
        this.weight = weight;
    }

    public Node getSource() { return source; }
    public Node getTarget() { return target; }
    public double getWeight() { return weight; }

    @Override
    public String toString() {
        return source.getTicker() + " -> " + target.getTicker() + " (" + weight + ")";
    }
}
