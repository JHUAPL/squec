from itertools import combinations
from typing import Hashable

VertexID = Hashable


def _edges_span_required(
    combo: list[tuple[VertexID, VertexID]], vbunch: list[VertexID]
) -> bool:
    """Return true if all vertices are included in the set."""
    for v in vbunch:
        found = False
        for edge in combo:
            if v in edge:
                found = True
                break
        if not found:
            return False
    return True


def partial_min_spanning_set(
    graph, required_vertices: list[VertexID], weight: str = "weight"
) -> list[tuple[VertexID, VertexID]]:
    """
    Produce a partial spanning set of edges such that the global weight of the
    set is minimized, and the set is selected so that all vertices V where
    vertices_required[V] == True must be included.

    Arguments:
        graph: nx.Graph
        required_vertices: A list of required verts
        weight: the attribute to use to indicate edge weights. If a weight is
            not specified, it will be assumed to be 1.

    """

    # Naive form: Produce all possible subsets of edges, with and without the
    # required vertices.
    possible_edge_sets = []
    possible_edge_costs = []

    # First produce the set of edges that connect required vertices:
    # required_vertex_subgraph = nx.subgraph(graph, required_vertices)
    # Candidate edge sets include even those that don't span all the required
    # vertices...
    all_combinations: list[list[tuple[VertexID, VertexID]]] = [
        list(item)
        # todo: start at len(reqs)/2
        for length in range(1, len(graph.edges) + 1)
        for item in combinations(graph.edges, length)
    ]
    combinations_containing_required = [
        combo
        for combo in all_combinations
        if _edges_span_required(combo, required_vertices)
    ]

    # Now loop through and remove any supersets. These can never be a valid
    # solution because there's guaranteed to be another option (the subset)
    # for which the weight is vacuously lower.
    # TODO: If weight can be 0, then this is not necessarily true...
    sorted_combinations_containing_required = sorted(
        combinations_containing_required, key=len
    )
    filtered_sorted_combinations_containing_required = []
    for combo in sorted_combinations_containing_required:
        if not any(
            set(combo).issuperset(set(old_combo))
            for old_combo in filtered_sorted_combinations_containing_required
        ):
            filtered_sorted_combinations_containing_required.append(combo)

    possible_edge_sets = filtered_sorted_combinations_containing_required
    possible_edge_costs = [
        sum(edge[weight] for u, v, edge in graph.edges(data=True) if (u, v) in edge_set)
        for edge_set in possible_edge_sets
    ]

    # The winning set is the one with the smallest cost:
    return min(zip(possible_edge_sets, possible_edge_costs), key=lambda x: x[1])[0]
