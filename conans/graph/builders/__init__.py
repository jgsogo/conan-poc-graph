from typing import Type

from .base import BaseBuilder
from .bfs_ex1 import BFSBuilderEx1
from ..graph import Graph
from ..proxy_types import Provider


def bfs_builder(vertex: str, provider: Type[Provider],
                builder_class: Type[BaseBuilder] = BFSBuilderEx1):
    g = Graph()
    g.add_node(vertex)
    builder = builder_class(g, provider)
    builder.run(vertex)
    g.finish_graph()
    return g
