public class Node {
    private String ticker;
    private double pageRankScore;

    public Node(String ticker) {
        this.ticker = ticker;
        this.pageRankScore = 1.0;
    }

    public String getTicker() {
        return ticker;
    }

    public double getPageRankScore() {
        return pageRankScore;
    }

    public void setPageRankScore(double score) {
        this.pageRankScore = score;
    }

    @Override
    public String toString() {
        return ticker + " (PageRank: " + pageRankScore + ")";
    }
}