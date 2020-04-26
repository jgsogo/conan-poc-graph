import networkx as nx

from .proxy_types import ConanFile


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
