from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True, eq=False, frozen=True)
class InvalidDeckSizeError(Exception):
    module_of_err: Optional[str] = None

    @property
    def message(self) -> str:
        return "Размер колоды игрока и необходимой для боя РАЗНЫЕ!"