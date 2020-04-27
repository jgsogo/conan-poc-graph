import logging
from collections import defaultdict
from typing import List, Tuple, Dict, Optional

import networkx as nx

from .bfs import BFSBuilder
from ..proxy_types import RequireType, Require, ConanFile

log = logging.getLogger(__name__)
from ..graph import Graph


class BFSBuilderEx1(BFSBuilder):

    def examine_vertex(self, vertex: str):
        log.debug(f"BFSBuilder::examine_vertex(conanfile='{vertex}')")
        # We are going to populate the graph based on the Conan information, so
        # the algorithm can keep running
        conanfile = self._get_conanfile(vertex)
        if not conanfile:
            return

        self.graph.nodes[vertex]['conanfile'] = conanfile
        for require in conanfile.get_requires():
            node_already_in_graph = self.graph.has_node(require.name)
            color = self.graph.nodes[require.name]['color'] if node_already_in_graph else 'white'
            if require.type == RequireType.requires:
                # Regular requires: add to graph and queue
                self.graph.add_node(require.name, color=color)
            elif require.type == RequireType.overrides:
                # Overrides: add to graph, but not to queue
                self.graph.add_node(require.name, color=color)
            elif require.type == RequireType.context_switch:
                # Context switch: spawn a new graph
                # TODO: This should be a call to bfs_builder
                print("spawn new graph")
                g = Graph()
                g.add_edge(vertex, require.name, require=require)
                builder = BFSBuilderEx1(g, self.provider)
                builder.run(require.name)
                g.finish_graph()
                print(g.nodes())
                print(require.name)
                self.graph.add_subgraph(vertex, g, require)
                continue
            else:
                raise NotImplementedError(f"Behaviour for require type '{require.type}'"
                                          f" not implemented")
            self.graph.add_edge(vertex, require.name, require=require)

    def non_tree_edge(self, origin: str, target: str):
        log.debug(f"BFSBuilder::non_tree_edge(origin='{origin}', requires='{target}')")
        # A new requirement just discovered, to a node that has already been evaluated, we will
        #  prune that branch of the graph just in case this new requirement would have resulted
        #  in a different conanfile.
        if target not in self._queue:
            self._prune(target, raise_if_pruning=origin)  # TODO: Optimization, check if the new require is going to modify anything (keep this minimal, implement in a child)
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

    def _get_conanfile(self, vertex: str) -> Optional[ConanFile]:
        """ Resolve precedence between requires, those closer to root take precedence
            (steps according to 'requires' relation)
        """
        in_edges = self.graph.in_edges(vertex, data='require')
        # Handle corner-case for the rootnode
        if not in_edges:
            return self.provider.get_conanfile(vertex, [])
        requires_graph = self.graph.get_requires_graph()

        # if the vertex is not in the requires graph, do not get the conanfile
        if not requires_graph.has_node(vertex):
            return

        # Filter requires by ancestors:
        requires_ancestors = nx.ancestors(requires_graph, vertex)
        requires = {ori: require for ori, _, require in in_edges if ori in requires_ancestors}
        # We need to consider all the topological orderings and check they resolve to the same
        #  conanfile, otherwise we have an ambiguity that should be reported as a conflict.
        candidate_conanfiles: List[ConanFile] = []
        for topo_order in nx.all_topological_sorts(requires_graph):
            log.info(f"Topological order: f{topo_order}")
            requires_given_order: List[Tuple[str, Require]] = []
            for it in topo_order:
                if it == vertex:  # Optimization
                    break
                req = requires.get(it, None)
                if req and req.type in [RequireType.requires, RequireType.overrides]:
                    requires_given_order.append((it, req))

            conanfile = self.provider.get_conanfile(vertex, requires_given_order)
            candidate_conanfiles.append(conanfile)

        # Validate that we get the same conanfile
        assert len(set(candidate_conanfiles)) == 1, "Multiple conanfiles --> ambiguity!"
        return candidate_conanfiles[0]
