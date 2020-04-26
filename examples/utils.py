import logging
from typing import List, Tuple

import networkx as nx
from conans.graph.proxy_types import Require, Provider, RequireType, ConanFile

log = logging.getLogger(__name__)


class ConanFileExample(ConanFile):
    def __init__(self, name, version, graph: nx.DiGraph):
        super().__init__(name, version)
        self._graph = graph
        self.name = name

    def get_requires(self) -> List[Require]:
        for _, target, data in self._graph.out_edges(self.name, data=True):
            require = Require()
            require.type = RequireType[data['type']]
            require.name = target
            require.version_expr = data['version']
            yield require


class ProviderExample(Provider):
    def __init__(self, g: nx.DiGraph, available_recipes):
        self.graph = g
        self.available_recipes = available_recipes

    def get_conanfile(self, name: str, constraints: List[Tuple[str, Require]]) -> ConanFileExample:
        log.debug(f"ProviderExample::get_conanfile(name='{name}', constraints[{len(constraints)}])")
        for ori, req in constraints:
            log.debug(f" - {req.type}: {ori} -> {req.name}/{req.version_expr}")

        versions_available = self.available_recipes[name]
        version_selected = None
        overriden = False
        for _, require in constraints:
            if require.type == RequireType.overrides:
                assert require.version_expr in versions_available
                version_selected = require.version_expr
                overriden = True
            elif require.type == RequireType.requires:
                assert not overriden, "Do not expect a requires after an override"
                version_selected = require.version_expr

        assert version_selected in versions_available, f"{version_selected} not found in {versions_available}"
        return ConanFileExample(name=name, version=version_selected, graph=self.graph)
