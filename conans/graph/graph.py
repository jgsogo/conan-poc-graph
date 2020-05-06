import logging
from collections import defaultdict
from typing import Optional, Dict, List, Tuple

import networkx as nx

from .proxy_types import EdgeType, Require

log = logging.getLogger(__name__)


# TODO:: Use a MultiDiGraph and separate requires?
class Graph(nx.DiGraph):

    def __init__(self, context: Optional[str] = "", *args, **kwargs):
        super().__init__(context=context, *args, **kwargs)
        self._subgraphs: Dict[int, "Graph"] = dict()
        self._subgraph_edges: List[Tuple[str, Require]] = list()

    @property
    def context(self):
        return self.graph['context']

    @staticmethod
    def _hash_require(require: Require) -> int:
        return hash(require.name) ^ hash(require.context) ^ hash(str(require.options))

    def get_subgraph(self, require: Require):
        subraph_id = self._hash_require(require)
        return self._subgraphs.get(subraph_id, None)

    def add_subgraph(self, vertex, graph: "Graph", require: Require):
        subraph_id = self._hash_require(require)
        # TODO: Check graphs are the same (if already existing)
        self._subgraphs[subraph_id] = graph
        self._subgraph_edges.append((vertex, require),)

    def get_requires_graph(self):
        """ Returns the graph taking into account only actual 'requirements' """
        requires_edges = [(u, v) for (u, v, requires) in self.edges(data='require')
                          if requires.edge_type == EdgeType.topological]
        return self.edge_subgraph(requires_edges)

    def finish_graph(self):
        requires_graph = self.get_requires_graph()
        nx.set_node_attributes(self, {n: {'enabled': True} for n in requires_graph.nodes()})
        overrides_by_target = defaultdict(list)
        for (u, v, require) in self.edges(data='require'):
            if not requires_graph.has_node(u) or not requires_graph.has_node(v):
                self.edges[(u, v)]['enabled'] = False
            elif require.edge_type == EdgeType.override:
                try:
                    spath_len = nx.shortest_path_length(requires_graph, u, v)
                except nx.exception.NetworkXNoPath:
                    self.edges[(u, v)]['enabled'] = False
                else:
                    overrides_by_target[v].append((spath_len, u))

        # If there are different overrides to one single node, only one is used
        #  (otherwise, it should have raised a conflict)
        for v, ori_requires in overrides_by_target.items():
            if len(ori_requires) > 1:
                ordered_requires = sorted(ori_requires, key=lambda x: x[0], reverse=True)
                for _, u in ordered_requires[1:]:
                    self.edges[(u, v)]['enabled'] = False

    def plain_graph(self):
        conan_graph = Graph()
        self._plain_graph(conan_graph)
        return conan_graph

    def _plain_graph(self, conan_graph: "Graph", scope=""):
        """ Returns a new graph:
            * nodes will use a different ID: name + context + options
            * edges:
              + only topological ones
              + will preserve only the visibility and require_type information
        """
        log.debug(f"Graph::_plain_graph(graph, scope='{scope}')")

        def _node_id(name, context, options):
            return hash(name) ^ hash(f"{scope}{context}") ^ hash(str(options))

        for node, data in self.nodes(data=True):
            if data.get('enabled', False):
                node_id = _node_id(node, self.context, data['conanfile'].options)
                assert node_id not in conan_graph, f"{self.context}::{node} is already in the graph!"  # IMPORTANT! Check we are not removing nodes here
                conan_graph.add_node(node_id, conanfile=data['conanfile'], context=f"{scope}{self.context}",
                                     label=str(data['conanfile']))

        for (u, v, data) in self.edges(data=True):
            require: Require = data['require']
            if require.edge_type == EdgeType.topological:
                u_node = _node_id(u, self.context, self.nodes[u]['conanfile'].options)
                v_node = _node_id(v, self.context, self.nodes[v]['conanfile'].options)
                assert not conan_graph.has_edge(u_node, v_node)  # IMPORTANT! Check we are not removing edged here
                conan_graph.add_edge(u_node, v_node, visibility=require.visibility, type=require.require_type,
                                     label=f"{require.visibility.name}\n{require.require_type.name}")

        # Work on subgraphs
        for subgraph in self._subgraphs.values():
            log.debug(f" - expand subgraph with context {subgraph.context}")
            subgraph_scope = f"{scope}" if subgraph.context == self.context else f"{scope}{self.context}::"
            subgraph._plain_graph(conan_graph, scope=subgraph_scope)

        for vertex, require in self._subgraph_edges:
            subgraph = self._subgraphs[self._hash_require(require)]
            subgraph_scope = "" if subgraph.context == self.context else f"{self.context}::"
            u_node = _node_id(vertex, self.context, self.nodes[vertex]['conanfile'].options)
            v_node = _node_id(require.name, f"{subgraph_scope}{subgraph.context}", subgraph.nodes[require.name]['conanfile'].options)
            conan_graph.add_edge(u_node, v_node, visibility=require.visibility, type=require.require_type,
                                 label=f"{require.visibility.name}\n{require.require_type.name}",
                                 color='blue')
