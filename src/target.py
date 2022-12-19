from dataclasses import dataclass
from typing import Dict

from typing_extensions import Self


@dataclass
class Target:
    hostname: str
    username: str
    key_filename: str

    @staticmethod
    def from_(conf: Dict[str, str]) -> Self:
        return Target(
            hostname=conf["hostname"],
            username=conf["username"],
            key_filename=conf["key_filename"],
        )
