# conan-poc-graph
POC for an improved graph model.


## Graph libraries out there
 
There are very few graph libraries for Python out there, in the 
[python.org](https://wiki.python.org/moin/PythonGraphLibraries) we can find some of
them but they have too many dependencies, they are discontinued or too focused on
AI or plotting. We need a pure graph library: data and algorithm to traverse the graph.

In the C++ world there are many alternatives, but most opinions converge to Boost
Graph Library or LEMON as the most powerful and flexible alternatives.

Some _Python_ alternatives:
* [networkx](https://github.com/networkx/networkx): only requires `decorator` if no
  extras or optional features are requested.
* [igraph](https://github.com/igraph): C library with Python interface.
* [graph-tool](https://graph-tool.skewed.de/): C++ library on top of BGL with Python
  bindings 
* [bgl-python](https://github.com/erwinvaneijk/bgl-python): official Python bindings
  for BGL. No longer in Boost codebase and no further developed.
  
## Starting point

Networkx looks like the best candidate as it is only Python, stable, widely used and
with strong support in Github. Concerns:
* It requires Python 3.6: our lower version is Python 3.5, need to test if it works
* It would be an external dependency in the core model: current version is stable
  enough (v2.5) and our requirements are quite simple from a graph perspective. Will
  be ever face an issue that will require us to upgrade to a newer incompatible
  version?
  
This POC will implement a layer on top of NetworkX.