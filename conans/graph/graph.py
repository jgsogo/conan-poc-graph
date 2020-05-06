import networkx as nx
import logging
from .proxy_types import ConanFile, RequireType, EdgeType, Require
from collections import defaultdict

log = logging.getLogger(__name__)


# TODO:: Use a MultiDiGraph and separate requires?
class Graph(nx.DiGraph):

    def __init__(self, context: int = 0, *args, **kwargs):
        super().__init__(context=context, *args, **kwargs)
        self._subgraphs = defaultdict(list)

    @property
    def context(self):
        return self.graph['context']

    def add_subgraph(self, vertex, graph: "Graph", require):
        self._subgraphs[vertex].append((graph, require))

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

    @staticmethod
    def printable_graph(graph: "Graph", scope=""):
        log.debug(f"Graph::printable_graph(graph, scope='{scope}')")
        printable = graph.copy()

        for (u, v, data) in graph.edges(data=True):
            style = "solid"
            color = "black"
            if not data.get('enabled', True):
                style = "dotted"
            elif data['require'].edge_type == EdgeType.override:
                color = "blue"

            printable.edges[(u, v)]['style'] = style
            printable.edges[(u, v)]['color'] = color
            printable.edges[(u, v)]['label'] = str(data['require'])

        for node, data in graph.nodes(data=True):
            if data.get('enabled', False):
                try:
                    printable.nodes[node]['label'] = str(data['conanfile'])
                except:
                    printable.nodes[node]['label'] = "no conanfile"
            else:
                printable.nodes[node]['style'] = "dotted"

        # Add the subgraphs
        for vertex, subgraphs in graph._subgraphs.items():
            for subgraph_, require in subgraphs:
                subgraph_printable = Graph.printable_graph(subgraph_, scope=f'{require.name}::')

                for n, data in subgraph_printable.nodes(data=True):
                    if n not in graph:
                        printable.add_node(n, **data)

                for u, v, data in subgraph_printable.edges(data=True):
                    printable.add_edge(u, v, **data)

                printable.add_edge(vertex, require.name, require=require, color='red')
        return printable


    @staticmethod
    def write_dot(graph: "Graph", output: str):
        log.debug(f"Graph::write_dot(graph, output='{output}')")
        graph = Graph.printable_graph(graph)
        graph.graph['graph'] = {'rankdir': 'BT'}
        nx.drawing.nx_agraph.write_dot(graph, output)
