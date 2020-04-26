import os
import sys

import networkx as nx
from conans.graph import Graph
from typing import List, Dict, Tuple
from conans.graph.proxy_types import Require, Provider

from conans.graph.builders.bfs_ex1 import BFSBuilderEx1


class ConanFileExample:
    def __init__(self, node, graph: nx.DiGraph):
        self._graph = graph
        self.node = node

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self.node

    def get_requires(self) -> List[Require]:
        for n in self._graph.adj[self.node]:
            require = Require()
            require.name = n
            require.version_expr = None
            yield require


class ProviderExample(Provider):
    def __init__(self, g: nx.DiGraph):
        self.graph = g

    def get_conanfile(self, name: str, constraints: List[Tuple[str, Require]]) -> ConanFileExample:
        log.info(f"ProviderExample::get_conanfile(name='{name}', constraints)")
        for ori, req in constraints:
            log.info(f" - {req.type}: {ori} -> {req.name}/{req.version_expr}")
        return ConanFileExample(name, self.graph)


def main(filename):
    input_graph = nx.read_graphml(filename)
    root = next(nx.topological_sort(input_graph))
    nx.drawing.nx_agraph.write_dot(input_graph, "input.dot")

    """
    STEP 1
    ------
    Build the graph of nodes resolving version ranges and overrides and
    reporting conflicts
    """
    provider = ProviderExample(input_graph)
    graph = Graph.build(provider, root, builder_class=BFSBuilderEx1)
    nx.drawing.nx_agraph.write_dot(graph, "output.dot")


if __name__ == '__main__':
    import argparse
    import logging

    formatter_class = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description="Conans Graph: Example 1",
                                     formatter_class=formatter_class)
    parser.add_argument("-v", "--verbose", dest="verbose_count",
                        action="count", default=0,
                        help="increases log verbosity for each occurence.")
    arguments = parser.parse_args(sys.argv[1:])

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG,
                        format='%(name)s (%(levelname)s): %(message)s')
    log = logging.getLogger('conans')
    log.setLevel(max(3 - arguments.verbose_count, 0) * 10)

    filename = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'inputs', 'basic_example.xml'))
    sys.stdout.write(f"Work on file: {filename}\n")
    main(filename)
