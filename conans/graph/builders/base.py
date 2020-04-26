from typing import Type

from ..graph import Graph
from ..proxy_types import Provider


class BaseBuilder:
    def __init__(self, graph: Graph, provider: Type[Provider]):
        self.provider = provider
        self.graph = graph

    def run(self, start_vertex: str):
        raise NotImplementedError
