import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

/**
 * Usage:
 *   java -cp java/build Main <edges.csv> <nodes.csv> <output.json> [--directed]
 *
 * edges.csv : header row, then source,target,weight
 * nodes.csv : header row, then one ticker per line (first column). Every stock is included,
 *             even ones with no edges, so the ranking always covers the full universe.
 */
public class Main {
    public static void main(String[] args) throws IOException {
        if (args.length < 3) {
            System.err.println("Usage: java Main <edges.csv> <nodes.csv> <output.json> [--directed]");
            System.exit(1);
        }
        String edgesPath = args[0];
        String nodesPath = args[1];
        String outPath = args[2];
        boolean directed = args.length > 3 && args[3].equals("--directed");

        Graph graph = new Graph(directed);

        try (BufferedReader r = new BufferedReader(new FileReader(nodesPath))) {
            r.readLine();
            String line;
            while ((line = r.readLine()) != null) {
                if (!line.isBlank()) graph.addNode(line.split(",")[0].trim());
            }
        }

        try (BufferedReader r = new BufferedReader(new FileReader(edgesPath))) {
            r.readLine();
            String line;
            while ((line = r.readLine()) != null) {
                if (line.isBlank()) continue;
                String[] p = line.split(",");
                graph.addEdge(p[0].trim(), p[1].trim(), Double.parseDouble(p[2].trim()));
            }
        }

        graph.printGraph();
        PageRankEngine engine = new PageRankEngine(graph);
        engine.run();

        System.out.println("\n--- Centrality ranking ---");
        graph.getNodes().values().stream()
            .sorted((a, b) -> Double.compare(b.getPageRankScore(), a.getPageRankScore()))
            .forEach(System.out::println);

        new GraphExporter(graph).exportToJSON(outPath);
    }
}
