import logging

from .bfs import BFSBuilder
from ..proxy_types import RequireType

log = logging.getLogger(__name__)


class BFSBuilderEx1(BFSBuilder):

    def discover_vertex(self, vertex: str):
        log.debug(f"BFSBuilder::discover_vertex(conanfile='{vertex}')")

    def examine_vertex(self, vertex: str):
        log.debug(f"BFSBuilder::examine_vertex(conanfile='{vertex}')")
        # We are going to populate the graph based on the Conan information, so
        # the algorithm can keep running
        requires = [(ori, req) for ori, _, req in self.graph.in_edges(vertex, data='require')]
        conanfile = self.provider.get_conanfile(vertex, requires)
        for require in conanfile.get_requires():
            node_already_in_graph = self.graph.has_node(require.name)
            color = self.graph.nodes[require.name]['color'] if node_already_in_graph else 'white'
            if require.type == RequireType.requires:
                # Regular requires: add to graph and queue
                self.graph.add_node(require.name, color=color)
            elif require.type == RequireType.context_switch:
                # Context switch: spawn a new graph
                pass
            elif require.type == RequireType.overrides:
                # Overrides: add to graph, but not to queue
                self.graph.add_node(require.name, color=color)
            elif require.type == RequireType.options:
                # Options: add to graph, but not to queue
                self.graph.add_node(require.name, color=color)
            else:
                raise NotImplementedError(f"Behaviour for require type '{require.type}'"
                                          f" not implemented")
            self.graph.add_edge(vertex, require.name, require=require, label=str(require))

    def finish_vertex(self, conanfile: str):
        log.debug(f"BFSBuilder::finish_vertex(conanfile='{conanfile}')")

    def examine_edge(self, origin: str, target: str):
        log.debug(f"BFSBuilder::examine_edge(origin='{origin}', require='{target}')")

    def tree_edge(self, origin: str, target: str):
        log.debug(f"BFSBuilder::tree_edge(origin='{origin}', require='{target}')")

    def non_tree_edge(self, origin: str, target: str):
        log.debug(f"BFSBuilder::non_tree_edge(origin='{origin}', requires='{target}')")
        # A new requirement just discovered, to a node that has already been evaluated, we will
        #  prune that branch of the graph just in case this new requirement would have resulted
        #  in a different conanfile.
        if target not in self._queue:
            self._prune(target, raise_if_pruning=origin)
            self._append(target)

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
