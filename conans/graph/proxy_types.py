# from .reference import Reference
from typing import Dict, List, Tuple
from enum import Enum


class RequireType(Enum):
    """
    There are different types of requires:
     * regular requires
     * context-switch requires (tools, privates, plugins,...)
     * requires because of overrides
     * requires because of options
    """
    requires = 1
    context_switch = 2
    overrides = 3
    # TODO: Need a better classification here


class Require:
    type: RequireType = None
    name: str

    version_expr: str = ""
    options: Dict[str, str] = {}

    enabled: bool = True

    def __str__(self):
        if self.options:
            return f"{self.name}/{self.version_expr} ({self.type.name}, {self.options})"
        else:
            return f"{self.name}/{self.version_expr} ({self.type.name})"


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
        return self.name == other.name and self.version == other.version and self.options == other.options

    def get_requires(self) -> List[Require]:
        raise NotImplementedError


class Provider:
    def get_conanfile(self, name: str, constraints: List[Tuple[str, Require]]) -> ConanFile:
        raise NotImplementedError
