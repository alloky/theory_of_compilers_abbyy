import weakref
import itertools


class GraphElement:

    def __init__(self, graph, element_id, name):
        self._graph = weakref.ref(graph)
        self._id = element_id
        self.name = name

    @property
    def graph(self):
        graph = self._graph()
        if not graph:
            raise ValueError('The graph is dead')
        return graph

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._id == other._id and self.graph is other.graph

    def __hash__(self):
        return hash(self._id) ^ id(self.graph)


class Node(GraphElement):

    def add_edge_to(self, node, name=''):
        if node is None:
            return None
        return self.graph._add_edge(self, node, name)

    @property
    def edges(self):
        return self.graph._get_edges(self)

    @property
    def neighbors(self):
        return (edge.nodes[1] for edge in self.edges)

    def delete(self):
        self.graph._delete_node(self)


class Edge(GraphElement):

    def __init__(self, graph, edge_id, nodes, name):
        super().__init__(graph, edge_id, name)
        self._node_from, self._node_to = nodes

    @property
    def nodes(self):
        return (self._node_from, self._node_to)

    def delete(self):
        self.graph._delete_edge(self)


class NodesWrapper:

    def __init__(self, graph):
        self._graph = graph

    def __iter__(self):
        return iter(self._graph._nodes.values())

    def add(self, name='') -> Node:
        return self._graph._add_node(name)


class EdgesWrapper:

    def __init__(self, graph):
        self._graph = graph

    def __iter__(self):
        for edges in self._graph._edges.values():
            for edge in edges.values():
                if edge._node_from._id <= edge._node_to._id:
                    yield edge

    def add(self, node1, node2, name='') -> Edge:
        return self._graph._add_edge(node1, node2, name)


class Graph:

    def __init__(self):
        self._nodes = {}
        self._edges = {}
        self._node_id_generator = itertools.count()
        self._edge_id_generator = itertools.count()

    def _add_node(self, name: int):
        node_id = next(self._node_id_generator)
        node = Node(self, node_id, name)
        self._nodes[node_id] = node
        return node

    def _add_edge(self, node1, node2, name):
        if node1.graph is not self or node2.graph is not self:
            raise ValueError('Nodes should belong to the graph')
        edge_id = next(self._edge_id_generator)
        edge = Edge(self, edge_id, (node1, node2), name)
        self._edges.setdefault(node1._id, {})[edge_id] = edge
        if node1 != node2:
            self._edges.setdefault(node2._id, {})[edge_id] = Edge(self, edge_id, (node2, node1), name)
        return edge

    def _get_edges(self, node):
        return self._edges.get(node._id, {}).values()

    def _delete_edge(self, edge):
        if edge._id not in self._edges.get(edge._node_from._id, ()):
            raise ValueError('The edge has been deleted')
        del self._edges[edge._node_from._id][edge._id]
        if edge._node_from != edge._node_to:
            del self._edges[edge._node_to._id][edge._id]

    def _delete_node(self, node):
        if node._id not in self._nodes:
            raise ValueError('The node has been deleted')
        for edge in list(self._get_edges(node)):
            self._delete_edge(edge)
        del self._nodes[node._id]
        if node._id in self._edges:
            del self._edges[node._id]

    @property
    def nodes(self) -> NodesWrapper:
        return NodesWrapper(self)

    @property
    def edges(self) -> EdgesWrapper:
        return EdgesWrapper(self)

    def __contains__(self, item):
        if isinstance(item, Node):
            return item._graph() == self and item._id in self._nodes
        if isinstance(item, Edge):
            return item._graph() == self and item._id in self._edges.get(item._node_from._id, ())
        return False
