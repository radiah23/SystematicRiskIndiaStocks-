import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/** Writes PageRank scores to JSON, sorted from most to least central. */
public class GraphExporter {
    private final Graph graph;

    public GraphExporter(Graph graph) {
        this.graph = graph;
    }

    public void exportToJSON(String filename) throws IOException {
        List<Node> nodes = new ArrayList<>(graph.getNodes().values());
        nodes.sort((a, b) -> Double.compare(b.getPageRankScore(), a.getPageRankScore()));

        try (FileWriter w = new FileWriter(filename)) {
            w.write("[\n");
            for (int i = 0; i < nodes.size(); i++) {
                Node node = nodes.get(i);
                w.write("  {\"ticker\": \"" + node.getTicker().replace("\"", "\\\"")
                    + "\", \"pagerank\": " + node.getPageRankScore()
                    + ", \"degree\": " + node.getOutEdges().size() + "}");
                w.write(i < nodes.size() - 1 ? ",\n" : "\n");
            }
            w.write("]\n");
        }
        System.out.println("Exported to " + filename);
    }
}
