import json
import os
import sys
from rapidfuzz import process
from rapidfuzz.fuzz import WRatio
from sentence_transformers import SentenceTransformer, util

GRAPH_PATH = os.path.join("graphify-out", "graph.json")
TOP_K = 5


def load_graph_nodes():
    if not os.path.exists(GRAPH_PATH):
        print(f"Error: Could not find {GRAPH_PATH}")
        print("Run 'graphify .' first to generate the graph output.")
        return []

    with open(GRAPH_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    nodes = []
    for node in data.get("nodes", []):
        node_id = node.get("id", "")
        label = node.get("label", node_id)
        nodes.append({
            "id": node_id,
            "label": label,
            "type": node.get("type", "unknown"),
        })

    return nodes


def fuzzy_match(query, nodes, top_k=TOP_K):
    """Fast lexical string matching — handles typos and partial words."""
    labels = [n["label"] for n in nodes]
    results = process.extract(
        query,
        labels,
        scorer=WRatio,
        limit=top_k,
    )

    print("\n--- Fuzzy (Lexical) Matches ---")
    if not results:
        print("  No matches found.")
        return

    for match, score, index in results:
        node = nodes[index]
        print(f"  [{score:5.1f}%]  {node['label']}  ({node['type']})  ->  {node['id']}")


def semantic_match(query, nodes, model, node_embeddings, top_k=TOP_K):
    """Embedding-based semantic search using a pre-loaded model and cached embeddings."""
    labels = [n["label"] for n in nodes]

    query_embedding = model.encode(query, convert_to_tensor=True)
    cosine_scores = util.cos_sim(query_embedding, node_embeddings)[0]
    top_results = cosine_scores.topk(k=min(top_k, len(nodes)))

    print("\n--- Semantic (AI Concept) Matches ---")
    for score, idx in zip(top_results.values, top_results.indices):
        node = nodes[idx.item()]
        print(f"  [{score.item():.4f}]  {node['label']}  ({node['type']})  ->  {node['id']}")


def main():
    nodes = load_graph_nodes()
    if not nodes:
        sys.exit(1)

    print(f"\nLoaded {len(nodes)} nodes from {GRAPH_PATH}")

    # Load model and pre-compute embeddings once before the search loop
    print("Loading embedding model (all-MiniLM-L6-v2) — runs locally on CPU...")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    labels = [n["label"] for n in nodes]
    print("Computing node embeddings...")
    node_embeddings = model.encode(labels, convert_to_tensor=True)
    print("Ready. Type a query to search, or 'q' to quit.\n")

    while True:
        try:
            query = input("Search query: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if query.lower() in ("q", "quit", "exit"):
            break
        if not query:
            continue

        fuzzy_match(query, nodes)
        semantic_match(query, nodes, model, node_embeddings)
        print()


if __name__ == "__main__":
    main()
