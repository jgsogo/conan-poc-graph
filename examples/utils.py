import logging
from typing import List, Tuple

import networkx as nx
from conans.graph.proxy_types import Require, Provider

log = logging.getLogger(__name__)


class ConanFileExample:
    def __init__(self, node, graph: nx.DiGraph):
        self._graph = graph
        self.node = node

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self.node

    def get_requires(self) -> List[Require]:
        for n in self._graph.adj[self.node]:
            require = Require()
            require.name = n
            require.version_expr = None
            yield require


class ProviderExample(Provider):
    def __init__(self, g: nx.DiGraph):
        self.graph = g

    def get_conanfile(self, name: str, constraints: List[Tuple[str, Require]]) -> ConanFileExample:
        log.info(f"ProviderExample::get_conanfile(name='{name}', constraints)")
        for ori, req in constraints:
            log.info(f" - {req.type}: {ori} -> {req.name}/{req.version_expr}")
        return ConanFileExample(name, self.graph)
