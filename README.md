# SQuEC - Surface Quantum Error Correction

SQuEC is a Python library for solving quantum error correction problems on surface codes. It implements an algorithm for finding optimal error correction solutions by modeling the problem as an optimization challenge on a graph.

## Overview

Surface codes are a leading approach for quantum error correction, organizing qubits in a 2D lattice where data qubits store quantum information and ancilla qubits detect errors. SQuEC provides tools to:

-   Model surface codes with configurable dimensions and layouts
-   Simulate error detection by flipping ancilla qubits
-   Find optimal error correction solutions using novel graph algorithms
-   Visualize surface codes and correction paths

## Key Features

### Surface Code Modeling

-   **Flexible Surface Construction**: Create surface codes of arbitrary dimensions using `VectorIJ` coordinates
-   **Error Simulation**: Flip ancilla qubits to simulate detected errors
-   **Visualization**: Rich matplotlib-based visualization showing data qubits, ancilla qubits (X and Z types), and error correction paths

### Algorithm Implementation

-   **Meta-graph Construction**: Transforms the surface code into a weighted graph where ancilla qubits are vertices and edge weights represent the cost of correction paths
-   **Partial Minimum Spanning Set (PMSS)**: A novel algorithm (possibly the first published implementation??) that finds optimal pairings of error syndromes while optionally connecting to boundaries
-   **Efficient Pathfinding**: Uses NetworkX for shortest-path calculations between ancilla qubits

### Error Correction Workflow

1. **State Detection**: Identify flipped ancilla qubits representing error syndromes
2. **Meta-graph Generation**: Create a weighted graph connecting all error syndromes
3. **Optimal Pairing**: Find the minimum-cost set of paths connecting syndromes to each other or to boundaries
4. **Path Traversal**: Flip data qubits along the optimal correction paths

## Installation

This project uses Poetry for dependency management:

```bash
poetry install
```

## Quick Start

```python
from squec import Surface, VectorIJ, squec_solve
import matplotlib.pyplot as plt

# Create a 7x7 surface code (Surface-17)
surface = Surface(VectorIJ(7, 7))

# Simulate some errors by flipping ancilla qubits
surface.flip_ancilla(VectorIJ(4, 4))
surface.flip_ancilla(VectorIJ(2, 2))

# Find the optimal correction
correction = squec_solve(surface)

# Visualize the result
surface.highlight_vertices(correction)
surface.draw()
plt.title(f"Correction: {correction}")
plt.show()
```

## Example Surface Codes

The library supports various surface code configurations:

-   **Surface-17**: 7×7 lattice with 17 logical qubits
-   **Surface-49**: 11×11 lattice with 49 logical qubits
-   **Surface-241**: 23×23 lattice with 241 logical qubits
-   **Custom geometries**: Non-square surfaces, offset origins, arbitrary dimensions

## Jupyter Notebooks

The repository includes several educational notebooks:

-   **`Draw.ipynb`**: Examples of different surface code sizes and configurations
-   **`Drawing-Example.ipynb`**: Basic workflow demonstration with before/after visualization
-   **`SQuEC-Illustrated.ipynb`**: Comprehensive tutorial explaining the algorithm step-by-step, including meta-graph construction and the PMSS algorithm
-   **`pmss-test.ipynb`**: Testing and demonstration of the Partial Minimum Spanning Set algorithm

## Algorithm Details

SQuEC's core innovation is the Partial Minimum Spanning Set (PMSS) algorithm, which efficiently finds optimal error correction paths by:

1. **Constructing a meta-graph** where each error syndrome (flipped ancilla) becomes a vertex
2. **Adding boundary vertices** for handling single-qubit errors that connect to the surface boundary
3. **Computing shortest paths** between all syndrome pairs with weights representing correction costs
4. **Finding optimal pairings** that minimize the total correction cost while ensuring all syndromes are addressed

The algorithm runs in O(|E|²) time complexity and handles both paired corrections (syndrome-to-syndrome) and boundary corrections (syndrome-to-edge).

## Development

The project includes comprehensive testing:

```bash
poetry run pytest
```

## Dependencies

-   **Python 3.11+**
-   **Poetry**: Dependency management and packaging

---

_For detailed examples and algorithm explanations, see the Jupyter notebooks in the `notebooks/` directory._


---


Copyright 2025 Johns Hopkins University Applied Physics Laboratory
