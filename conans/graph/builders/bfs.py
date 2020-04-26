import logging
from typing import List

import networkx as nx

from .base import BaseBuilder
from ..proxy_types import Require

log = logging.getLogger(__name__)


class BFSBuilder(BaseBuilder):
    """ Not exactly a visitor, as we are building the graph at the same time we are
        visiting it (and there is logic between the two layers), this is the reason why
        I cannot use a standard algorithm, I need mine to modify the 'queue' while I'm
        consuming it
    """
    _queue: List[str] = []

    def _append(self, vertex: str) -> None:
        self._queue.append(vertex)
        self.discover_vertex(vertex)
        self.graph.nodes[vertex]['color'] = 'gray'

    def run(self, start_vertex: str):
        # 1. Initialize all vertices
        self._queue.clear()
        nx.set_node_attributes(self.graph, 'color', 'white')

        # 2. Append initial vertex
        self._append(start_vertex)

        # Iterate the queue
        while self._queue:
            vertex = self._queue.pop(0)
            self.examine_vertex(vertex)
            for _, target in self.graph.out_edges(vertex):
                self.examine_edge(vertex, target)
                if self.graph.nodes[target]['color'] == 'white':
                    self.tree_edge(vertex, target)
                    self._append(target)
                else:
                    self.non_tree_edge(vertex, target)
            self.graph.nodes[vertex]['color'] = 'black'
            self.finish_vertex(vertex)
        # Queue exhausted

    def discover_vertex(self, vertex: str):
        log.debug(f"BFSBuilder::discover_vertex(vertex='{vertex}')")

    def examine_vertex(self, vertex: str):
        log.debug(f"BFSBuilder::examine_vertex(vertex='{vertex}')")

    def finish_vertex(self, vertex: str):
        log.debug(f"BFSBuilder::finish_vertex(vertex='{vertex}')")

    def examine_edge(self, origin: str, target: str):
        log.debug(f"BFSBuilder::examine_edge(origin='{origin}', requires='{target}')")

    def tree_edge(self, origin: str, target: str):
        log.debug(f"BFSBuilder::tree_edge(origin='{origin}', requires='{target}')")

    def non_tree_edge(self, origin: str, target: str):
        log.debug(f"BFSBuilder::non_tree_edge(origin='{origin}', requires='{target}')")
