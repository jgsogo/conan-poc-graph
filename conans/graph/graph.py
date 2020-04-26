import networkx as nx

from .builders import BaseBuilder, BFSBuilder
# from .node import Node
from .proxy_types import ConanFile, Provider


class Graph(nx.DiGraph):
    context: int

    @classmethod
    def build(cls, provider: Provider, root: str, context: int = 0, builder_class: BaseBuilder = BFSBuilder):
        g = Graph(context=context)
        builder = builder_class(root, g, provider)
        builder.run()
        return g

    @property
    def context(self):
        return self.graph['context']

    def add_conanfile(self, conanfile: ConanFile):
        identifier = conanfile.name
        self.add_node(identifier, data=conanfile)
        return identifier
