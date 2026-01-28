from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class UserNotFoundException(Exception):
    module: Optional[str] = None

    @property
    def message(self) -> str:
        msg = "User Not Found"
        if (mod := self.module) is not None:
            msg = msg + "\n" + f"from module {mod}"

        return msg
