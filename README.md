# Second Brain Knowledge Graph & Analysis Tools

A standalone suite of automation tools for generating navigable knowledge graphs, community clustering, structural AST extraction, and interactive HTML visualizers from any codebase or folder.

---

## 📁 Included Tools & Files

| File | Description |
| :--- | :--- |
| **`graphify.py`** | Automated end-to-end knowledge graph pipeline (File detection, parallel multi-core AST extraction, Louvain community clustering, diagnostics, report generation, and interactive HTML export). |
| **`finish_build.py`** | Fast post-processor and visualizer. Re-clusters extracted nodes, calculates cohesion scores, generates `GRAPH_REPORT.md`, and exports `graph.html`. |
| **`graph.html`** | Standalone interactive 3D/2D network visualizer for the codebase. Open directly in any web browser. |
| **`GRAPH_REPORT.md`** | Comprehensive audit report with community hubs, cohesion metrics, god nodes, and architectural questions. |

---

## 🚀 How to Use

### 1. Run the Full Graphify Pipeline
To scan and graph any directory or codebase:

```bash
# Graph the current directory
python graphify.py

# Graph a specific folder
python graphify.py "C:\path\to\your\project"

# Options:
python graphify.py "C:\path\to\your\project" --directed   # Preserve edge direction (source -> target)
python graphify.py "C:\path\to\your\project" --obsidian   # Also export an Obsidian markdown vault
python graphify.py "C:\path\to\your\project" --no-viz     # Headless mode (skip HTML generation)
```

### 2. Run the Fast Finalizer / Re-clustering (`finish_build.py`)
If extraction JSON already exists in `graphify-out/` and you want to re-run community detection, update labels, or re-export `graph.html`:

```bash
python finish_build.py
```

### 3. View the Interactive Graph
Simply double-click **`graph.html`** or open it in Google Chrome, Microsoft Edge, or Firefox:
* **Left Click + Drag**: Rotate and navigate 3D/2D space.
* **Scroll Wheel**: Zoom in/out.
* **Click Node**: Inspect connected methods, classes, and dependencies.
* **Community Colors**: Clusters are automatically color-coded by architectural module.

---

## ⚙️ Key Technical Features
* **Windows & Multi-Core Native**: Built with `multiprocessing.freeze_support()` and main process guards for maximum speed across all CPU cores without deadlocks.
* **Deterministic AST Extraction**: Extracts classes, methods, inheritance, and import chains via tree-sitter.
* **Community Clustering**: Detects architectural boundaries and module cohesion using Louvain algorithm.
* **Graph Diagnostics**: Verifies edge integrity, detecting and reporting dangling endpoints and cycles.
