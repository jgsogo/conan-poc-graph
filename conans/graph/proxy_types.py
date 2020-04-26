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
    options = 4


class Require:
    name: str
    version_expr: str
    type: RequireType = RequireType.requires

    def __str__(self):
        return f"{self.name}/{self.version_expr} ({self.type})"


class ConanFile:
    name: str

    def get_requires(self) -> List[Require]:
        raise NotImplementedError


class Provider:
    def get_conanfile(self, name: str, constraints: List[Tuple[str, Require]]) -> ConanFile:
        raise NotImplementedError
