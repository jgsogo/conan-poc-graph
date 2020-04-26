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

    def _append(self, vertex: str) -> None:
        self._queue.append(vertex)
        self.discover_vertex(vertex)
        self.graph.add_node(vertex, color='white')

    def _pop(self) -> str:
        vertex: str = self._queue.pop(0)
        self._examine_vertex(vertex)
        return vertex

    def run(self):
        # 1. Initialize all vertices
        # 2. Append initial vertex
        self._append(self._start)
        # 3. Iterate the queue
        while self._queue:
            print(self._queue)
            vertex = self._pop()
            conanfile: ConanFile = self.graph.nodes[vertex]['conanfile']
            for require in conanfile.get_requires():
                self.examine_edge(vertex, require)
                if not self.graph.has_node(require.name):  # First time we see this node
                    self._append(require.name)
                    self.tree_edge(vertex, require)
                else:
                    if require.name not in self._queue:
                        self._prune(require.name, raise_if_pruning=vertex)
                        self._append(require.name)
                    self.non_tree_edge(vertex, require)
                self.graph.add_edge(vertex, require.name, require=require)
            self.finish_vertex(vertex)
        # 4. Queue exhausted

    def _prune(self, vertex: str, raise_if_pruning: str):
        log.debug(f"BFSBuilder::_prune(vertex='{vertex}', raise_if_pruning='{raise_if_pruning}')")
        # We've discovered this vertex from another branch in the graph, it can potentially
        #   be resolved to a different version and have a different set of requirements/overrides,
        #   options,... we need to build again all this branch

        def collect_branch_nodes(node):
            for _, target in self.graph.out_edges(node):
                for it in collect_branch_nodes(target):
                    yield it
                yield target
        branch_nodes = set(list(collect_branch_nodes(vertex)))

        if raise_if_pruning in branch_nodes:
            raise Exception(f"There is cycle involving '{vertex}' and '{raise_if_pruning}'")

        # Remove these nodes from the queue and from the graph
        self._queue = [it for it in self._queue if it not in branch_nodes]
        self.graph.remove_nodes_from(branch_nodes)

    def discover_vertex(self, vertex: str):
        log.debug(f"BFSBuilder::discover_vertex(vertex='{vertex}')")

    def _examine_vertex(self, vertex: str):
        # If the queue is empty, we can be sure that this node has been resolved
        self.examine_vertex(vertex)
        if not self._queue:
            self.graph.nodes[vertex]['color'] = 'black'
            log.debug(f"Done with '{vertex}'")

    def examine_vertex(self, vertex: str):
        log.debug(f"BFSBuilder::examine_vertex(vertex='{vertex}')")

    def finish_vertex(self, vertex: str):
        log.debug(f"BFSBuilder::finish_vertex(vertex='{vertex}')")

    def examine_edge(self, origin: str, requires: Require):
        log.debug(f"BFSBuilder::examine_edge(origin='{origin}', requires='{requires.name}')")
        # TODO: This logic belongs here:
        """
        if requires.spawn_new_context:
            # subgraph = self.graph.build()
            pass
        elif requires.is_override:
            # Store this information to be consumed upstream
            pass
        else:
            #self.graph.add_edge(origin, requires.name, requires=requires)
            pass
        """

    def tree_edge(self, origin: str, requires: Require):
        log.debug(f"BFSBuilder::tree_edge(origin='{origin}', requires='{requires.name}')")

    def non_tree_edge(self, origin: str, requires: Require):
        log.debug(f"BFSBuilder::non_tree_edge(origin='{origin}', requires='{requires.name}')")
