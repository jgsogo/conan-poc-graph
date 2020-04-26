from .base import BaseBuilder
from ..proxy_types import ConanFile, Require
from typing import List, Dict

import logging

log = logging.getLogger(__name__)


class BFSBuilder(BaseBuilder):
    _queue: List[str] = []

    def __init__(self, vertex: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._start = vertex

    def _append(self, vertex_id: str, conanfile: ConanFile = None) -> None:
        self._queue.append(vertex_id)
        self.discover_vertex(vertex_id)

    def _pop(self) -> str:
        vertex: str = self._queue.pop(0)
        self.examine_vertex(vertex)
        return vertex

    def run(self):
        # 1. Initialize all vertices
        # 2. Append initial vertex
        self._append(self._start)
        # 3. Iterate the queue
        while self._queue:
            vertex = self._pop()
            conanfile = self.provider.get_conanfile(vertex, None)
            for require in conanfile.get_requires():
                self.examine_edge(vertex, require)
                if not self.graph.has_node(require.name):
                    # First time we see this node
                    self._append(require.name)
                    self.tree_edge(vertex, require)
                else:
                    self.non_tree_edge(vertex, require)
                self.graph.add_edge(vertex, require.name)
            self.finish_vertex(vertex)

    def discover_vertex(self, conanfile: str):
        log.debug(f"BFSBuilder::discover_vertex(conanfile='{conanfile}')")

    def examine_vertex(self, conanfile: str):
        log.debug(f"BFSBuilder::examine_vertex(conanfile='{conanfile}')")
        self.graph.add_node(conanfile, conanfile=conanfile)

    def finish_vertex(self, conanfile: str):
        log.debug(f"BFSBuilder::finish_vertex(conanfile='{conanfile}')")
        pass

    def examine_edge(self, origin: str, requires: Require):
        log.debug(f"BFSBuilder::examine_edge(origin='{origin}', requires='{requires.name}')")
        if requires.spawn_new_context:
            # subgraph = self.graph.build()
            pass
        elif requires.is_override:
            # Store this information to be consumed upstream
            pass
        else:
            #self.graph.add_edge(origin, requires.name, requires=requires)
            pass

    def tree_edge(self, origin: str, requires: Require):
        log.debug(f"BFSBuilder::tree_edge(origin='{origin}', requires='{requires.name}')")
        pass

    def non_tree_edge(self, origin: str, requires: Require):
        log.debug(f"BFSBuilder::non_tree_edge(origin='{origin}', requires='{requires.name}')")
        pass
