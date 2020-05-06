import json
import os
import sys

import networkx as nx

from conans.graph import Graph
from conans.graph.builders import bfs_builder, BFSBuilderEx1
from .utils import ProviderExample
from conans.graph.printer import write_dot


def main(graphml, jsonfile):
    available_recipes = json.load(open(jsonfile))
    input_graph = nx.read_graphml(graphml)
    nx.drawing.nx_agraph.write_dot(input_graph, "input.dot")
    root = next(nx.topological_sort(input_graph))

    """
    STEP 1
    ------
    Build the graph of nodes resolving version ranges and overrides and
    reporting conflicts
    """
    provider = ProviderExample(input_graph, available_recipes)
    conanfile = provider.get_conanfile(root, [])
    graph = bfs_builder(root, provider, builder_class=BFSBuilderEx1, conanfile=conanfile)

    # Print raw
    conan_graph = graph.plain_graph()
    conan_graph.graph['graph'] = {'rankdir': 'BT'}
    nx.drawing.nx_agraph.write_dot(conan_graph, "output_raw.dot")
    os.system("dot -Tpng output_raw.dot -o output_raw.png")

    # Print beauty
    write_dot(graph, "output.dot")
    os.system("dot -Tpng output.dot -o output.png")


if __name__ == '__main__':
    import argparse
    import logging

    formatter_class = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description="Conans Graph: Example 1",
                                     formatter_class=formatter_class)
    parser.add_argument("-v", "--verbose", dest="verbose_count",
                        action="count", default=0,
                        help="increases log verbosity for each occurence.")
    parser.add_argument("example", default=None,
                        help="example to run.")
    arguments = parser.parse_args(sys.argv[1:])

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG,
                        format='%(name)s (%(levelname)s): %(message)s')
    log = logging.getLogger('conans')
    log.setLevel(max(3 - arguments.verbose_count, 0) * 10)
    log = logging.getLogger('examples')
    log.setLevel(max(3 - arguments.verbose_count, 0) * 10)

    sys.stdout.write(f"Example to run: {arguments.example}\n")
    graphml = os.path.abspath(os.path.join(os.path.dirname(__file__), 'inputs', f'{arguments.example}.xml'))
    jsonfile = os.path.abspath(os.path.join(os.path.dirname(__file__), 'inputs', f'server.json'))

    sys.stdout.write(f"Work on file:\n")
    sys.stdout.write(f" - GraphML: '{graphml}'\n")
    sys.stdout.write(f" - JSON: '{jsonfile}'\n")

    main(graphml, jsonfile)
