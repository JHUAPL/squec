from dataclasses import dataclass
from typing import Set, Union
from enum import Enum

import networkx as nx

_FLIP_COLOR = "#FF0000"
_FLIP_SIZE = 1.4
_HIGHLIGHT_COLOR = "#FFD700"
_HIGHLIGHT_SIZE = 1.8

_X_COLOR = "#53917E"
_Z_COLOR = "#CC8800"
_DQ_COLOR = "#63535B"


# Node type enum:
class QubitType(Enum):
    DATA = "data"
    ANCILLA = "ancilla"


class AncillaType(Enum):
    X = "X"
    Z = "Z"

    def __str__(self):
        return self.value


@dataclass
class VectorIJ:
    """
    Represents a vector with i and j components.
    """

    i: int
    j: int

    def __init__(
        self,
        *args: Union["VectorIJ", tuple[int, int], list[int], int],
    ):
        if isinstance(args[0], VectorIJ):
            self.i, self.j = args[0].i, args[0].j
        elif isinstance(args[0], (tuple, list)):
            self.i, self.j = args[0]
        else:
            self.i, self.j = args  # type: ignore

    def __eq__(self, other: "VectorIJ") -> bool:
        if isinstance(other, VectorIJ):
            return self.i == other.i and self.j == other.j
        if isinstance(other, (tuple, list)) and len(other) == 2:
            return self.i == other[0] and self.j == other[1]
        return False

    def __sub__(
        self, other: Union["VectorIJ", tuple[int, int], list[int]]
    ) -> "VectorIJ":
        """
        Subtract another vector or tuple from this vector.

        Uses Manhattan distance.
        """
        if isinstance(other, VectorIJ):
            return VectorIJ(self.i - other.i, self.j - other.j)
        elif isinstance(other, (tuple, list)) and len(other) == 2:
            return VectorIJ(self.i - other[0], self.j - other[1])
        else:
            raise ValueError(
                f"Invalid operand type for vector subtraction. Expected VectorIJ, tuple, or list, but got {type(other)}"
            )

    def __hash__(self) -> int:
        return hash((self.i, self.j))

    def separation_from(self, other: "VectorIJ") -> "VectorIJ":
        return self - other

    # VectorIJ.separation(a, b)
    @staticmethod
    def separation(a: "VectorIJ", b: "VectorIJ") -> "VectorIJ":
        return a - b

    def clone(self) -> "VectorIJ":
        """
        Create a new vector with the same i and j components.

        """
        return VectorIJ(self.i, self.j)

    def __add__(
        self, other: Union["VectorIJ", tuple[int, int], list[int]]
    ) -> "VectorIJ":
        """
        Add another vector or tuple to this vector.
        """
        if isinstance(other, VectorIJ):
            return VectorIJ(self.i + other.i, self.j + other.j)
        elif isinstance(other, (tuple, list)) and len(other) == 2:
            return VectorIJ(self.i + other[0], self.j + other[1])
        else:
            raise ValueError(
                f"Invalid operand type for vector addition. Expected VectorIJ, tuple, or list, but got {type(other)}"
            )

    def __repr__(self) -> str:
        return f"({self.i}, {self.j})"


class Qubit:
    loc: VectorIJ
    type: QubitType

    def __init__(self, loc: VectorIJ) -> None:
        self.loc = loc

    def separation_from(self, other: "Qubit") -> VectorIJ:
        return self.loc - other.loc

    def __repr__(self) -> str:
        return "<DQ>"


class Ancilla(Qubit):

    def __init__(self, loc: VectorIJ, ancilla_type: AncillaType) -> None:
        super().__init__(loc)
        self.ancilla_type = ancilla_type

    def __repr__(self) -> str:
        return f"<AQ({self.ancilla_type})>"


def _create_surface_graph(
    size_ij: VectorIJ, origin_ij: VectorIJ | None = None
) -> nx.Graph:
    """
    Create a NetworkX.Graph object that represents the Surface.

    The nodes of the graph are the qubits and the edges are the connections
    between them. The vertex IDs double as the qubit coordinates.

    Data qubits all land on odd i and j coordinates, while ancilla qubits land
    on even i and j coordinates (starting from 0).
    """
    if origin_ij is None:
        origin_ij = VectorIJ(0, 0)
    g = nx.Graph()
    # First create the grid of data qubits:
    for i in range(origin_ij.i + 1, size_ij.i + origin_ij.i, 2):
        for j in range(origin_ij.j + 1, size_ij.j + origin_ij.j, 2):
            g.add_node(
                VectorIJ(i, j), qubit_type=QubitType.DATA, qubit=Qubit(VectorIJ(i, j))
            )
            # Add edges to the left and right neighbors:
            if i > origin_ij.i + 1:
                g.add_edge(VectorIJ(i, j), VectorIJ(i - 2, j), weight=2)
            if i < (size_ij.i + origin_ij.i - 1):
                g.add_edge(VectorIJ(i, j), VectorIJ(i + 2, j), weight=2)
            # Add edges to the top and bottom neighbors:
            if j > origin_ij.j + 1:
                g.add_edge(VectorIJ(i, j), VectorIJ(i, j - 2), weight=2)
            if j < (size_ij.j + origin_ij.j - 1):
                g.add_edge(VectorIJ(i, j), VectorIJ(i, j + 2), weight=2)
    # Now create the grid of ancilla qubits:
    for i in range(origin_ij.i, size_ij.i + origin_ij.i, 2):
        for j in range(origin_ij.j, size_ij.j + origin_ij.j, 2):
            # Don't create the origin node if it's a data qubit:
            if i == origin_ij.i and j == origin_ij.j:
                continue

            # Don't create X-type ancillas on the row of the origin node:
            if i == origin_ij.i and j % 4 == 2:
                continue
            # Don't create Z-type ancillas on the column of the origin node:
            if j == origin_ij.j and i % 4 == 0:
                continue
            g.add_node(
                VectorIJ(i, j),
                qubit_type=QubitType.ANCILLA,
                ancilla_type=AncillaType.X if (i + j) % 4 == 0 else AncillaType.Z,
                qubit=Ancilla(
                    VectorIJ(i, j), AncillaType.X if (i + j) % 4 == 0 else AncillaType.Z
                ),
            )
            # Add the diagonal edges to the data qubits:
            if i > origin_ij.i and j > origin_ij.j and g.has_node((i - 1, j - 1)):
                g.add_edge(VectorIJ(i, j), VectorIJ(i - 1, j - 1), weight=1)
            if (
                i > origin_ij.i
                and j < (size_ij.j + origin_ij.j - 1)
                and g.has_node((i - 1, j + 1))
            ):
                g.add_edge(VectorIJ(i, j), VectorIJ(i - 1, j + 1), weight=1)
            if (
                i < (size_ij.i + origin_ij.i - 1)
                and j > origin_ij.j
                and g.has_node(VectorIJ(i + 1, j - 1))
            ):
                g.add_edge(VectorIJ(i, j), VectorIJ(i + 1, j - 1), weight=1)
            if (
                i < (size_ij.i + origin_ij.i - 1)
                and j < (size_ij.j + origin_ij.j - 1)
                and g.has_node(VectorIJ(i + 1, j + 1))
            ):
                g.add_edge(VectorIJ(i, j), VectorIJ(i + 1, j + 1), weight=1)

    # Remove any node that doesn't have a qubit object:
    for node in list(g.nodes()):
        if "qubit" not in g.nodes[node]:
            g.remove_node(node)

    # Remove degree-1 nodes:
    for node in list(g.nodes()):
        if g.degree(node) == 1:  # type: ignore
            g.remove_node(node)

    # Remove all Z-type ancillas that are at the right edge of the grid:
    max_i = max([node.i for node in g.nodes()])
    max_j = max([node.j for node in g.nodes()])
    for node in list(g.nodes()):
        if (
            g.nodes[node]["qubit_type"] == QubitType.ANCILLA
            and (
                g.nodes[node].get("ancilla_type", "") == AncillaType.Z
                and node.i == max_i
            )
            or (
                g.nodes[node].get("ancilla_type", "") == AncillaType.X
                and node.j == max_j
            )
        ):
            g.remove_node(node)
    return g


class Surface:
    """
    A Surface represents the network connectivity of SQuEC qubits.

    """

    def __init__(
        self,
        size_ij: Union["VectorIJ", tuple[int, int], list[int]],
        origin_ij: Union["VectorIJ", tuple[int, int], list[int]] | None = None,
        highlighted_vertices: list[VectorIJ] | None = None,
        flipped_ancillae: list[VectorIJ] | None = None,
    ) -> None:
        """
        Initialize a Surface object.

        Arguments:
            size_ij: the size of the Surface in i and j directions.
            origin_ij: the start coordinate in i and j directions.

        """
        self.size_ij = VectorIJ(size_ij)
        if origin_ij is not None:
            self.origin_ij = VectorIJ(origin_ij)
        else:
            self.origin_ij = VectorIJ(0, 0)
        self.graph = _create_surface_graph(self.size_ij, self.origin_ij)
        self._highlighted_vertices: Set[VectorIJ] = set(highlighted_vertices or [])
        self._flipped_ancillae: Set[VectorIJ] = set(flipped_ancillae or [])
        self.minimum_data_qbit_coordinate = VectorIJ(
            self.origin_ij.i if self.origin_ij.i % 2 != 0 else self.origin_ij.i + 1,
            self.origin_ij.j if self.origin_ij.j % 2 != 0 else self.origin_ij.j + 1,
        )
        self.maximum_data_qbit_coordinate = VectorIJ(
            (
                (self.origin_ij.i + self.size_ij.i - 2)
                if (self.origin_ij.i + self.size_ij.i) % 2 != 0
                else (self.origin_ij.i + self.size_ij.i) - 1
            ),
            (
                (self.origin_ij.j + self.size_ij.j - 2)
                if (self.origin_ij.j + self.size_ij.j) % 2 != 0
                else (self.origin_ij.j + self.size_ij.j) - 1
            ),
        )

    def clone(self) -> "Surface":
        """
        Create a deep copy of the Surface object.
        """
        surface = Surface(self.size_ij, self.origin_ij)
        surface.graph = self.graph.copy()
        surface._highlighted_vertices = self._highlighted_vertices.copy()
        surface._flipped_ancillae = self._flipped_ancillae.copy()
        return surface

    def highlight_vertices(self, vertices: list[VectorIJ] | VectorIJ) -> None:
        """
        Highlight the given vertices on the graph.
        """
        if isinstance(vertices, VectorIJ):
            vertices = [vertices]
        self._highlighted_vertices.update(vertices)

    def unhighlight_vertices(self, vertices: list[VectorIJ] | VectorIJ) -> None:
        """
        Unhighlight the given vertices on the graph.
        """
        if isinstance(vertices, VectorIJ):
            vertices = [vertices]
        self._highlighted_vertices.difference_update(vertices)

    def clear_highlights(self) -> None:
        """
        Clear all highlighted vertices.
        """
        self._highlighted_vertices.clear()

    def flip_ancilla(
        self, ancilla_id: VectorIJ, is_flipped: bool | None = None
    ) -> None:
        """
        Flip the ancilla qubit at the given location.
        """
        if is_flipped is None:
            is_flipped = ancilla_id not in self._flipped_ancillae
        if is_flipped:
            self._flipped_ancillae.add(ancilla_id)

    def unflip_ancilla(self, ancilla_id: VectorIJ) -> None:
        """
        Unflip the ancilla qubit at the given location.
        """
        self._flipped_ancillae.discard(ancilla_id)

    def is_flipped(self, ancilla_id: VectorIJ) -> bool:
        """
        Return whether the ancilla qubit at the given location is flipped.
        """
        return ancilla_id in self._flipped_ancillae

    def clear_flips(self) -> None:
        """
        Clear all flipped ancillae.
        """
        self._flipped_ancillae.clear()

    def get_flipped_ancillae(self) -> list[VectorIJ]:
        """
        Get the list of flipped ancillae.
        """
        return list(self._flipped_ancillae)

    def get_ancilla_type(self, coord: VectorIJ) -> AncillaType:
        """
        Get the ancilla type for the given coordinate.

        """
        return self.graph.nodes[coord]["ancilla_type"]

    def get_graph(self) -> nx.Graph:
        return self.graph

    def draw(
        self,
        highlighted_vertices: list[VectorIJ] | None = None,
        draw_kwargs: dict | None = None,
    ):
        """
        Draw the Surface graph.
        """
        draw_kwargs = draw_kwargs or {}
        g = self.graph
        highlighted_vertices = (
            highlighted_vertices or list(self._highlighted_vertices) or []
        )
        pos = {node: (node.i, node.j) for node in g.nodes()}
        nx.draw_networkx_edges(g, pos=pos, **draw_kwargs)
        # Several calls to draw data nodes:
        node_color = [
            (
                _DQ_COLOR
                if g.nodes[node]["qubit_type"] == QubitType.DATA
                else (
                    _X_COLOR
                    if g.nodes[node]["ancilla_type"] == AncillaType.X
                    else _Z_COLOR
                )
            )
            for node in g.nodes()
        ]

        # Draw highlighted data nodes:
        nx.draw_networkx_nodes(
            g,
            pos=pos,
            node_color=_HIGHLIGHT_COLOR,  # type: ignore
            node_size=[  # type: ignore
                (
                    0
                    if g.nodes[node]["qubit_type"] == QubitType.ANCILLA
                    else (500 * _HIGHLIGHT_SIZE if node in highlighted_vertices else 0)
                )
                for node in g.nodes()
            ],
            **draw_kwargs,
        )
        # Draw flipped data nodes:
        nx.draw_networkx_nodes(
            g,
            pos=pos,
            node_color=_FLIP_COLOR,  # type: ignore
            node_size=[  # type: ignore
                (
                    0
                    if g.nodes[node]["qubit_type"] == QubitType.ANCILLA
                    else (500 * _FLIP_SIZE if node in self._flipped_ancillae else 0)
                )
                for node in g.nodes()
            ],
            **draw_kwargs,
        )
        # Draw all other data nodes:
        nx.draw_networkx_nodes(
            g,
            pos=pos,
            node_color=node_color,  # type: ignore
            node_size=[  # type: ignore
                500 if g.nodes[node]["qubit_type"] == QubitType.DATA else 0
                for node in g.nodes()
            ],
            **draw_kwargs,
        )

        # Draw highlighted ancilla nodes:
        nx.draw_networkx_nodes(
            g,
            pos=pos,
            node_color=_HIGHLIGHT_COLOR,  # type: ignore
            node_size=[  # type: ignore
                (
                    0
                    if g.nodes[node]["qubit_type"] == QubitType.DATA
                    else (2000 * _HIGHLIGHT_SIZE if node in highlighted_vertices else 0)
                )
                for node in g.nodes()
            ],
            node_shape="s",
            **draw_kwargs,
        )
        # Draw flipped ancilla nodes:
        nx.draw_networkx_nodes(
            g,
            pos=pos,
            node_color=_FLIP_COLOR,  # type: ignore
            node_size=[  # type: ignore
                (
                    0
                    if g.nodes[node]["qubit_type"] == QubitType.DATA
                    else (2000 * _FLIP_SIZE if node in self._flipped_ancillae else 0)
                )
                for node in g.nodes()
            ],
            node_shape="s",
            **draw_kwargs,
        )
        # Draw ancilla nodes:
        nx.draw_networkx_nodes(
            g,
            pos=pos,
            node_color=node_color,  # type: ignore
            node_size=[  # type: ignore
                0 if g.nodes[node]["qubit_type"] == QubitType.DATA else 2000
                for node in g.nodes()
            ],
            node_shape="s",
            **draw_kwargs,
        )
        # Draw labels:
        nx.draw_networkx_labels(
            g,
            pos=pos,
            font_size=8,
            font_family="monospace",
            font_color="white",
            labels={
                nid: f"{node['qubit']}\n{node['qubit'].loc}"
                for nid, node in g.nodes(data=True)
            },
            **draw_kwargs,
        )
