import logging
from collections import defaultdict
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
        requires = defaultdict(Require)
        for _, target, data in self._graph.out_edges(self.name, data=True):
            require = requires[target]
            require.type = RequireType[data['type']]
            require.name = target
            if 'version' in data:
                require.version_expr = data['version']
            if 'options' in data:
                options = {}
                for opt in data['options'].split(';'):
                    key, value = opt.split('=')
                    options[key] = value
                require.options = options

        return requires.values()


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
        options = {}

        def add_options(opts):
            for key, value in opts.items():
                options[key] = options.get(key, value)

        for _, require in constraints:
            assert require.version_expr in versions_available
            add_options(require.options)
            if require.type == RequireType.overrides:
                if not overriden:
                    version_selected = require.version_expr
                overriden = True
            elif require.type == RequireType.requires:
                if not overriden:
                    version_selected = require.version_expr

        assert version_selected in versions_available, f"{version_selected} not found in {versions_available}"
        conanfile = ConanFileExample(name=name, version=version_selected, graph=self.graph)
        conanfile.options = options
        return conanfile
