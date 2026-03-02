import java.io.FileWriter;
import java.util.ArrayList;
import java.util.List;

public class GraphExporter {
    private Graph graph;

    public GraphExporter(Graph graph) {
        this.graph = graph;
    }

    public void exportToJSON(String filename) throws Exception {
        FileWriter writer = new FileWriter(filename);
        
        writer.write("[\n");
        
        List<Node> nodes = new ArrayList<>(graph.getNodes().values());
        nodes.sort((a, b) -> Double.compare(b.getPageRankScore(), a.getPageRankScore()));
        
        for (int i = 0; i < nodes.size(); i++) {
            Node node = nodes.get(i);
            writer.write("  {\n");
            writer.write("    \"ticker\": \"" + node.getTicker() + "\",\n");
            writer.write("    \"pagerank\": " + node.getPageRankScore() + "\n");
            writer.write("  }");
            if (i < nodes.size() - 1) writer.write(",");
            writer.write("\n");
        }
        
        writer.write("]\n");
        writer.close();
        System.out.println("Exported to " + filename);
    }
}
