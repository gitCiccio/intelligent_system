# 3-Coloring Graph Neural Network (3-COL GNN)

An intelligent system built with PyTorch Geometric (PyG) designed to solve and analyze the NP-Complete graph 3-coloring problem using Message Passing Neural Networks (MPNN).

## 🚀 Overview & Implementation

This project implements a complete machine learning pipeline to determine whether complex graphs are 3-colorable. Instead of relying purely on exponential brute-force search methods, our approach trains a Graph Neural Network (GNN) to act as a powerful heuristic ("super-heuristic") capable of learning topological invariants.

### Key Components Built:
1. **Dataset Generation & Backtracking Oracle (`generator.py`):**
   - Generates random regular graphs and Erdős-Rényi graphs under critical Phase Transition parameters.
   - Utilizes a protected backtracking algorithm (`is_3_color`) with robust timeout handling to accurately label whether a graph is 3-colorable (`1` for yes, `0` for no).

2. **Graph Data Structuring (`dataset.py`):**
   - Converts NetworkX graph representations into PyTorch Geometric `Data` objects.
   - Computes bidirectional `edge_index` matrices and uniform node features (`x`), securely caching the processed dataset to disk (`data/3col_dataset.pt`).

3. **GNN Architecture (`model.py`):**
   - Built using 4 stacked Graph Convolutional layers (`GCNConv`) with 64 hidden dimensions to capture local and multi-hop neighborhood features (cycles, cliques).
   - Incorporates a global pooling layer (`global_add_pool`) for permutation-invariant graph-level aggregation.
   - Features a linear classification head mapped through binary output layers.

4. **Training & Optimization Pipeline (`training.py` & `main.py`):**
   - Configured with `BCEWithLogitsLoss` and optimized using the adaptive `Adam` optimizer.
   - Manages custom batch processing via PyG's `DataLoader` with dynamic tensor shape alignments to ensure stable end-to-end training over multiple epochs.
   - **3-Coloring Specifics Addressed:** Implemented bidirectional edge creation for non-oriented graphs, handled phase-transition parameter bounds for Erdős-Rényi/Regular graphs, and mapped scalar-to-tensor output dimensions for binary cross-entropy loss computation.
```eof

