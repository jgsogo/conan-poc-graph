from ..proxy_types import ConanFile, Provider


class BaseBuilder:
    def __init__(self, graph: "Graph", provider: Provider):
        self.provider = provider
        self.graph = graph

    def visit(self, conanfile: ConanFile):
        raise NotImplementedError
