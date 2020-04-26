# from .reference import Reference
from typing import Dict, List


class Require:
    name: str
    version_expr: str
    spawn_new_context: bool = False
    is_override: bool = False

    def __str__(self):
        return f"{self.name}/{self.version_expr}"


class ConanFile:
    name: str

    def get_requires(self) -> List[Require]:
        raise NotImplementedError


class Provider:
    def get_conanfile(self, name: str, version_expr: Dict[str, Require]) -> ConanFile:
        raise NotImplementedError
