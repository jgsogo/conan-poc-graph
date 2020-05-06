import logging
from collections import defaultdict
from typing import List, Tuple, Dict

import networkx as nx
from conans.graph.proxy_types import Require, Provider, RequireType, ConanFile, LibraryType, EdgeType, Visibility, Context

log = logging.getLogger(__name__)


class ConanFileExample(ConanFile):
    def __init__(self, name, version, graph: nx.DiGraph):
        super().__init__(name, version)
        self._graph = graph
        self.name = name

    @staticmethod
    def _parse_options(options) -> Dict[str, str]:
        ret = {}
        if options:
            for opt in options.split(';'):
                key, value = opt.split('=')
                ret[key] = value
        return ret

    def _parse_requires(self, name, data) -> Require:
        options = self._parse_options(data.pop('options', None))
        require = Require()
        require.name = name
        require.options = options
        for key in data:
            if key == 'version':
                require.version_expr = data[key]
            elif key == 'edge_type':
                require.edge_type = EdgeType(data[key])
            elif key == 'require_type':
                require.require_type = RequireType(data[key])
            elif key == 'visibility':
                require.visibility = Visibility(data[key])
            elif key == 'context':
                require.context = Context(data[key])
            else:
                raise NotImplementedError(f"Field '{key}' not expected for require")
        return require

    def get_type(self) -> LibraryType:
        return self._graph.nodes[self.name]["library_type"]

    def get_requires(self) -> List[Require]:
        requires_data = dict()
        for _, target, data in self._graph.out_edges(self.name, data=True):
            requires_data[target] = self._graph.graph['edge_default'].copy()
            requires_data[target].update(data)

        return [self._parse_requires(name=key, data=data) for key, data in requires_data.items()]


class ProviderExample(Provider):
    def __init__(self, g: nx.DiGraph, available_recipes):
        self.graph = g
        self.available_recipes = available_recipes

    def get_conanfile(self, name: str, constraints: List[Tuple[str, Require]]) -> ConanFileExample:
        log.debug(f"ProviderExample::get_conanfile(name='{name}', constraints ({len(constraints)}))")
        for ori, req in constraints:
            log.debug(f" - {req.edge_type.name}: {ori} -> {req.name}/{req.version_expr}")

        versions_available = self.available_recipes[name]
        version_selected = None
        overriden = False
        options = {}

        def add_options(opts):
            for key, value in opts.items():
                options[key] = options.get(key, value)

        for _, require in constraints:
            add_options(require.options)
            if require.edge_type == EdgeType.options:
                assert not require.version_expr, "An 'options' require know nothing about the version_range"
                continue
            if require.edge_type == EdgeType.override:
                if not overriden:
                    version_selected = require.version_expr
                overriden = True
            else:
                assert require.edge_type == EdgeType.topological
                if not overriden:
                    version_selected = require.version_expr

        assert version_selected in versions_available, f"{version_selected} not found in {versions_available}"
        conanfile = ConanFileExample(name=name, version=version_selected, graph=self.graph)
        conanfile.options = options
        return conanfile
