import logging
from typing import List, Tuple

import networkx as nx
from conans.graph.proxy_types import Require, Provider, RequireType, ConanFile

log = logging.getLogger(__name__)


class ConanFileExample(ConanFile):
    def __init__(self, node, graph: nx.DiGraph):
        super().__init__(node, "version")
        self._graph = graph
        self.node = node

    def get_requires(self) -> List[Require]:
        for _, target, data in self._graph.out_edges(self.node, data=True):
            require = Require()
            require.type = RequireType[data['type']]
            require.name = target
            require.version_expr = data['version']
            yield require


class ProviderExample(Provider):
    def __init__(self, g: nx.DiGraph):
        self.graph = g

    def get_conanfile(self, name: str, constraints: List[Tuple[str, Require]]) -> ConanFileExample:
        log.debug(f"ProviderExample::get_conanfile(name='{name}', constraints[{len(constraints)}])")
        for ori, req in constraints:
            log.debug(f" - {req.type}: {ori} -> {req.name}/{req.version_expr}")

        return ConanFileExample(name, self.graph)
