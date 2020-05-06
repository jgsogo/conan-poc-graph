import logging

import networkx as nx

from .proxy_types import EdgeType, Require

log = logging.getLogger(__name__)

unique_require_ids = dict()


def _unique_require_id(require: Require) -> str:
    h = str(hash(require.context) ^ hash(str(require.options)))
    if h not in unique_require_ids:
        unique_require_ids[h] = len(unique_require_ids)
    return unique_require_ids[h]


def printable_graph(graph: "Graph", scope=""):
    log.debug(f"Graph::printable_graph(graph, scope='{scope}')")
    printable = graph.__class__()

    for node, data in graph.nodes(data=True):
        node = f"{scope}{node}"
        if data.get('enabled', False):
            printable.add_node(node, label=f"{scope}{str(data['conanfile'])}")
        else:
            printable.add_node(node, style="dotted")

    for (u, v, data) in graph.edges(data=True):
        style = "solid"
        color = "black"
        if not data.get('enabled', True):
            style = "dotted"
        elif data['require'].edge_type == EdgeType.override:
            color = "blue"

        u = f"{scope}{u}"
        v = f"{scope}{v}"
        printable.add_edge(u, v, style=style, color=color, label=str(data['require']))

    # Add the subgraphs
    for vertex, require in graph._subgraph_edges:
        subgraph_scope = f"{scope}{vertex}::"
        subgraph = graph._subgraphs[graph._hash_require(require)]

        subgraph_printable = printable_graph(subgraph, scope=subgraph_scope)

        for n, data in subgraph_printable.nodes(data=True):
            assert n not in printable, f"{n} already in printable"
            printable.add_node(n, **data)

        for u, v, data in subgraph_printable.edges(data=True):
            printable.add_edge(u, v, **data)

        color = 'red' if require.context else 'blue'
        printable.add_edge(f"{scope}{vertex}", f"{subgraph_scope}{require.name}", color=color, label=str(require))
    return printable


def write_dot(graph: "Graph", output: str):
    log.debug(f"Graph::write_dot(graph, output='{output}')")
    graph = printable_graph(graph)
    graph.graph['graph'] = {'rankdir': 'BT'}
    nx.drawing.nx_agraph.write_dot(graph, output)
