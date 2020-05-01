from enum import Enum
from typing import Dict, List, Tuple, Optional


class EdgeType(Enum):
    """
    Edge type: some edges introduce a topological relation (there is an actual
    requirement between two nodes) while other just introduce information like
    overrides or options
    """
    topological = 1  # Declares a dependency
    override = 2  # Overrides a version, defines default options,...


class RequireType(Enum):
    """
    Defines how the consumer will consume the required node
    """
    assets = 1
    library = 2
    tool = 3
    plugin = 4


class Visibility(Enum):
    interface = 1
    public = 2
    private = 3


class Context(Enum):
    host = 1
    other = 2


class LibraryType(Enum):
    header_only = 1
    static = 2
    shared = 3


class Require:
    name: str
    version_expr: str
    edge_type: EdgeType = None

    # A topological require will define these properties
    require_type: Optional[RequireType] = None
    visibility: Optional[Visibility] = None
    context: Optional[Context] = None

    # Options can be defined by a topological or overrides relation
    options: Dict[str, str] = {}

    def __str__(self):
        ret = f"{self.edge_type.name}\n{self.name}/{self.version_expr}"
        if self.edge_type == EdgeType.topological:
            ret += f"\n{self.visibility.name}\n{self.require_type.name}\n{self.context.name}"
        if self.options:
            ret += f"\n{self.options}"


class ConanFile:
    name: str
    version: str
    options: Dict[str, str] = {}

    def __init__(self, name, version):
        self.name = name
        self.version = version

    def __str__(self):
        if self.options:
            return f"{self.name}/{self.version}\n{self.options}"
        else:
            return f"{self.name}/{self.version}"

    def __hash__(self):
        return hash(self.name) ^ hash(self.version)

    def __eq__(self, other: "ConanFile") -> bool:
        return self.name == other.name and self.version == other.version\
               and self.options == other.options

    def get_type(self) -> LibraryType:
        raise NotImplementedError

    def get_requires(self) -> List[Require]:
        raise NotImplementedError


class Provider:
    def get_conanfile(self, name: str, constraints: List[Tuple[str, Require]]) -> ConanFile:
        raise NotImplementedError
