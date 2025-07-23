import networkx as nx

from .surface import VectorIJ, Surface, QubitType, AncillaType
from .pmss import partial_min_spanning_set


def get_optimal_pairing(
    state: Surface, vertex_set: list[VectorIJ] | None = None
) -> list[tuple[VectorIJ, VectorIJ]]:
    """
    Given a set of AQs, construct an optimal pairing of nearest neighbors.

    There are two ways to pair an AQ: It can either be paired with another AQ,
    subject to globally minimizing all separations; or it can be a single-flip
    error, in which case the path goes not to another AQ but to a blind edge,
    following the criteria below:

    * For an X AQ, find the nearest horizontal edge (minimizing or maximizing
      the j coordinate).
    * For a Y AQ, find the nearest vertical edge (min/max i coordinate).

    The optimal set must include every qubit once, but it does not necessarily
    need to include any blind edges.

    If no vertex_set is specified, will use the state's flipped ancillae.

    """
    vertex_set = vertex_set or state.get_flipped_ancillae()
    return partial_min_spanning_set(
        get_metagraph(state, vertex_set), vertex_set, weight="dq_count"  # type: ignore
    )


def get_metagraph(state: Surface, vertex_set: list[VectorIJ] | None = None) -> nx.Graph:
    """
    Construct a meta-represntation that indicates the relationship between AQs
    and the DQs that must be used to connect them.


    """
    min_ij = state.minimum_data_qbit_coordinate
    max_ij = state.maximum_data_qbit_coordinate

    vertex_set = vertex_set or state.get_flipped_ancillae()

    g = state.get_graph()

    # First construct the weighted graph of all AQs' pairwise separations, as
    # well as the "ground" for each:
    metagraph = nx.Graph()
    flipped_ancillae = vertex_set
    for u in range(len(flipped_ancillae)):
        a_u = flipped_ancillae[u]
        for v in range(u + 1, len(flipped_ancillae)):
            # Create the edge (i,j):
            a_v = flipped_ancillae[v]

            path = nx.shortest_path(g, a_u, a_v, weight="weight")

            metagraph.add_edge(
                a_u,
                a_v,
                dq_count=len([v for v in path if v.i % 2 == 1]),
                length=len(path),
                is_to_edge=False,
                path=path,
            )

        # For each ancilla, also compute its separation to "ground":
        if state.get_ancilla_type(a_u) == AncillaType.X:
            # Check the closest VERTICAL edges (j axis):
            dist_to_min_j = a_u.j - min_ij.j
            dist_to_max_j = max_ij.j - a_u.j
            if dist_to_min_j < dist_to_max_j:
                best_j_node = (
                    VectorIJ(a_u.i - 1, min_ij.j)
                    if VectorIJ(a_u.i - 1, min_ij.j) in g
                    else VectorIJ(a_u.i + 1, min_ij.j)
                )
            else:
                best_j_node = (
                    VectorIJ(a_u.i - 1, max_ij.j)
                    if VectorIJ(a_u.i - 1, max_ij.j) in g
                    else VectorIJ(a_u.i + 1, max_ij.j)
                )
            path = nx.shortest_path(g, a_u, best_j_node, weight="weight")
            path_length = len(path)
            # Add 1 to accommodate offset; subtract one to remove source vertex
            metagraph.add_edge(
                a_u,
                best_j_node,
                dq_count=len([v for v in path if v.i % 2 == 1]),
                length=path_length,
                is_to_edge=True,
                path=path,
            )

        else:
            raise NotImplementedError("Y ancillae not yet supported.")

    return metagraph


def squec_solve(
    state: Surface, vertex_set: list[VectorIJ] | None = None
) -> list[VectorIJ]:
    """
    Perform the SQuEC error correction algorithm on the given state.

    Returns a list of DQs to flip (by vertex ID).

    """
    # Get the list of flipped ancillae:
    flipped_ancillae = state.get_flipped_ancillae()
    vertex_set = vertex_set or flipped_ancillae
    max_i = state.size_ij.i + state.origin_ij.i
    max_j = state.size_ij.j + state.origin_ij.j
    max_i_aq = max_i if max_i % 2 == 0 else max_i - 1
    max_j_aq = max_j if max_j % 2 == 0 else max_j - 1

    # Get the graph state:
    g = state.get_graph()

    # The first step is to check for the single-flip case, which can be solved
    # through simple heuristics:
    if len(vertex_set) == 1:
        # First we check for the simple case where the ancilla is on a corner.
        # These ancillae can only see two data qubits, only one of which is a
        # valid option (since the other can be seen by a minimum of 2 AQs),
        # so we can trivially flip the correct DQ.
        ancilla = vertex_set[0]
        ancilla_type = g.nodes[ancilla]["ancilla_type"]
        if (
            # Degree of 2 means the AQ's on an edge:
            g.degree(ancilla) == 2  # type: ignore
            # And on an edge:
            and (
                ancilla.i == state.origin_ij.i
                or ancilla.j == state.origin_ij.j
                or (ancilla.i == max_i_aq)
                or (ancilla.j == max_j_aq)
            )
        ):
            dq_candidates = [
                node
                for node in g.neighbors(ancilla)
                if g.nodes[node]["qubit_type"] == QubitType.DATA
            ]
            # There will be only one option of the two candidates that is valid
            # to flip: It must be a data qubit with only one ancilla neighbor.
            for dq in dq_candidates:
                if (
                    len(
                        [
                            node
                            for node in g.neighbors(dq)
                            if g.nodes[node]["qubit_type"] == QubitType.ANCILLA
                            and g.nodes[node]["ancilla_type"] == ancilla_type
                        ]
                    )
                    == 1
                ):
                    return [dq]
            else:
                # This is the "else" for the for loop, NOT the if...
                # If we reach this point, we have an invalid ancilla flip;
                # this should never happen because it means we've encountered
                # an ambiguous surface topology where multiple data qubits
                # are adjacent to the flipped ancilla but no other AQs flipped.
                raise ValueError(
                    "Invalid ancilla flip detected: Ambiguous solution found. "
                    "The following DQs are both valid solutions: {dq_candidates}"
                )

    # Now we handle the even-parity error correction.
    # We start by finding the optimal pairing of flipped ancillae:
    pairs = get_optimal_pairing(state, vertex_set)

    # Get the paths:
    pairs_with_paths = [
        (pair, nx.shortest_path(g, pair[0], pair[1], weight="weight")) for pair in pairs
    ]

    # Now we can walk along each path and flip the data qubits along the way.
    # If you flip an already-flipped data qubit, you'll unflip it.
    dq_to_flip = []
    for (_source, _target), path in pairs_with_paths:
        for node in path:
            if g.nodes[node]["qubit_type"] == QubitType.DATA:
                if node in dq_to_flip:
                    dq_to_flip.remove(node)
                else:
                    dq_to_flip.append(node)

    return dq_to_flip
