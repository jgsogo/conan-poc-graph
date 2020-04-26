#from .reference import Reference
from typing import Dict, List


class SemVer:
    pass


class Reference:
    name: str
    version: SemVer
    user: str = None
    channel: str = None

    def __init__(self, name: str, version: SemVer, user=None, channel=None):
        self.name = name
        self.version = version
        self.user = user
        self.channel = channel




class Require:
    name: str
    version_expr: str
    spawn_new_context: bool = False
    is_override: bool = False


class ConanFile:
    name: str

    def get_requires(self) -> List[Require]:
        raise NotImplementedError


class Provider:
    def get_conanfile(self, name: str, version_expr: str) -> ConanFile:
        raise NotImplementedError
