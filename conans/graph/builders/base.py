from ..proxy_types import ConanFile, Provider
from typing import Type

class BaseBuilder:
    def __init__(self, graph: "Graph", provider: Type[Provider]):
        self.provider = provider
        self.graph = graph

    def visit(self, conanfile: ConanFile):
        raise NotImplementedError
