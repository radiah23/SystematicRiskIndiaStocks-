import java.io.BufferedReader;
import java.io.FileReader;

public class Main {
    public static void main(String[] args) throws Exception {
        Graph graph = new Graph();

        BufferedReader reader = new BufferedReader(new FileReader("../edges.csv"));
        String line;
        reader.readLine();

        while ((line = reader.readLine()) != null) {
            String[] parts = line.split(",");
            String stockA = parts[0].trim();
            String stockB = parts[1].trim();
            double weight = Double.parseDouble(parts[2].trim());

            graph.addNode(stockA);
            graph.addNode(stockB);
            graph.addEdge(stockA, stockB, weight);
        }
        reader.close();

        graph.printGraph();

        PageRankEngine engine = new PageRankEngine(graph);
        engine.run();

        System.out.println("\n--- Systemic Risk Rankings ---");
        graph.getNodes().values().stream()
            .sorted((a, b) -> Double.compare(b.getPageRankScore(), a.getPageRankScore()))
            .forEach(n -> System.out.println(n));

        GraphExporter exporter = new GraphExporter(graph);
        exporter.exportToJSON("../pagerank_results.json");
    }
}