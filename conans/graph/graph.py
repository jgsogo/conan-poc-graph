import networkx as nx

from .proxy_types import ConanFile, RequireType


class Graph(nx.DiGraph):

    def __init__(self, context: int = 0, *args, **kwargs):
        super().__init__(context=context, *args, **kwargs)

    @property
    def context(self):
        return self.graph['context']

    def add_conanfile(self, conanfile: ConanFile):
        identifier = conanfile.name
        self.add_node(identifier, data=conanfile)
        return identifier

    def write_dot(self, output: str):
        self.graph['graph'] = {'rankdir': 'BT'}
        # Add labels to all the graphs
        for node in self.nodes:
            self.nodes[node]['label'] = str(self.nodes[node]['conanfile'])
        for edge in self.edges:
            require = self.edges[edge]['require']

            style = "solid"
            if not require.enabled and require.type == RequireType.overrides:
                style = "dotted"

            color = "black"
            if require.enabled and require.type == RequireType.overrides:
                color = "blue"

            self.edges[edge]['style'] = style
            self.edges[edge]['color'] = color
            self.edges[edge]['label'] = str(require)

        nx.drawing.nx_agraph.write_dot(self, output)
