from dataclasses import dataclass
from typing import Optional


@dataclass
class IncorrectTargetError(Exception):
    msg: Optional[str] = None

    @property
    def message(self) -> str:
        return "Incorrect Target Type!" or self.msg
