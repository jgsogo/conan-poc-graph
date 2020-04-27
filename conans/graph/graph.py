import networkx as nx

from .proxy_types import ConanFile, RequireType
from collections import defaultdict


class Graph(nx.DiGraph):

    def __init__(self, context: int = 0, *args, **kwargs):
        super().__init__(context=context, *args, **kwargs)

    @property
    def context(self):
        return self.graph['context']

    def get_requires_graph(self):
        """ Returns the graph taking into account only actual 'requirements' """
        requires_edges = [(u, v) for (u, v, requires) in self.edges(data='require')
                          if requires.type == RequireType.requires]
        return self.edge_subgraph(requires_edges)

    def finish_graph(self):
        requires_graph = self.get_requires_graph()
        nx.set_node_attributes(self, {n: {'enabled': True} for n in requires_graph.nodes()})
        overrides_by_target = defaultdict(list)
        for (u, v, require) in self.edges(data='require'):
            if not requires_graph.has_node(u) or not requires_graph.has_node(v):
                self.edges[(u, v)]['enabled'] = False
            elif require.type == RequireType.overrides:
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

    def write_dot(self, output: str):
        self.graph['graph'] = {'rankdir': 'BT'}

        for (u, v, data) in self.edges(data=True):
            style = "solid"
            color = "black"
            if not data.get('enabled', True):
                style = "dotted"
            elif data['require'].type == RequireType.overrides:
                color = "blue"

            self.edges[(u, v)]['style'] = style
            self.edges[(u, v)]['color'] = color
            self.edges[(u, v)]['label'] = str(data['require'])

        for node, data in self.nodes(data=True):
            if data.get('enabled', False):
                self.nodes[node]['label'] = str(data['conanfile'])
            else:
                self.nodes[node]['style'] = "dotted"

        nx.drawing.nx_agraph.write_dot(self, output)
