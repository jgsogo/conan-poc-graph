import logging

from .bfs import BFSBuilder, Require

log = logging.getLogger(__name__)


class BFSBuilderEx1(BFSBuilder):

    def discover_vertex(self, vertex: str):
        log.debug(f"BFSBuilder::discover_vertex(conanfile='{vertex}')")

    def examine_vertex(self, vertex: str):
        log.debug(f"BFSBuilder::examine_vertex(conanfile='{vertex}')")

        # Get the conanfile for this node with the information we have
        requires = [(ori, req) for ori, _, req in self.graph.in_edges(vertex, data='require')]
        # TODO: If all are overrides, remove this vertex
        conanfile = self.provider.get_conanfile(vertex, requires)
        self.graph.nodes[vertex]['conanfile'] = conanfile

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
            # self.graph.add_edge(origin, requires.name, requires=requires)
            pass

    def tree_edge(self, origin: str, requires: Require):
        log.debug(f"BFSBuilder::tree_edge(origin='{origin}', requires='{requires.name}')")
        pass

    def non_tree_edge(self, origin: str, requires: Require):
        log.debug(f"BFSBuilder::non_tree_edge(origin='{origin}', requires='{requires.name}')")
        # TODO: Check this new requires is compatible
        pass
