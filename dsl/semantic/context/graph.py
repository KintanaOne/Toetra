from dataclasses import dataclass, field


@dataclass
class SemanticNode:
    """
    Node in the SemanticGraph.

    Represents a semantic entity in the program:
        - variable
        - feature
        - property
        - model element
    """

    id: str
    type: str
    data: dict = field(default_factory=dict)


@dataclass
class SemanticEdge:
    """
    Directed relationship between semantic nodes.
    """

    src: str
    dst: str
    relation: str


class SemanticGraph:
    """
    SemanticGraph is an OPTIONAL analysis structure.

    It is NOT required for validation or execution.

    It is used for:
        - global dependency analysis
        - debugging semantic resolution
        - future optimization passes
        - advanced reasoning over properties
    """

    def __init__(self):
        # Node registry
        self.nodes: dict[str, SemanticNode] = {}

        # Directed edges between nodes
        self.edges: list[SemanticEdge] = []

    # ─────────────────────────────────────────────
    # Node API
    # ─────────────────────────────────────────────

    def add_node(self, node_id: str, node_type: str, **data) -> None:
        """
        Register a semantic node.
        """
        self.nodes[node_id] = SemanticNode(
            id=node_id,
            type=node_type,
            data=data
        )

    # ─────────────────────────────────────────────
    # Edge API
    # ─────────────────────────────────────────────

    def add_edge(self, src: str, dst: str, relation: str) -> None:
        """
        Create a semantic relationship between two nodes.
        """
        self.edges.append(SemanticEdge(src, dst, relation))

    # ─────────────────────────────────────────────
    # Query API
    # ─────────────────────────────────────────────

    def neighbors(self, node_id: str) -> list[SemanticEdge]:
        """
        Return all outgoing edges from a node.
        """
        return [
            e for e in self.edges if e.src == node_id
        ]

    # ─────────────────────────────────────────────
    # Debug
    # ─────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"SemanticGraph(nodes={len(self.nodes)}, "
            f"edges={len(self.edges)})"
        )