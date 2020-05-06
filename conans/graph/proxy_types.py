from enum import Enum, auto
from typing import Dict, List, Tuple, Optional


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class EdgeType(AutoName):
    """
    Edge type: some edges introduce a topological relation (there is an actual
    requirement between two nodes) while other just introduce information like
    overrides or options
    """
    topological = auto()  # Declares a dependency
    override = auto()  # Overrides a version
    options = auto()  # Overrides options (do not say anything about the version)


class RequireType(AutoName):
    """
    Defines how the consumer will consume the required node
    """
    assets = auto()
    library = auto()
    tool = auto()
    plugin = auto()


class Visibility(AutoName):
    interface = auto()
    public = auto()
    private = auto()


class Context(AutoName):
    host = auto()
    other = auto()


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
        return ret


class LibraryType(AutoName):
    header_only = auto()
    static = auto()
    shared = auto()


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
        return self.name == other.name and self.version == other.version \
               and self.options == other.options

    def get_type(self) -> LibraryType:
        raise NotImplementedError

    def get_requires(self) -> List[Require]:
        raise NotImplementedError


class Provider:
    def get_conanfile(self, name: str, constraints: List[Tuple[str, Require]]) -> ConanFile:
        raise NotImplementedError
