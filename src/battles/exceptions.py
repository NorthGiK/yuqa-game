from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, eq=False, frozen=True, kw_only=True)
class InvalidDeckSizeError(Exception):
    module_of_err: str = ""

    @property
    def message(self) -> str:
        return (
            "Размер колоды игрока и необходимой для боя РАЗНЫЕ!"
            "\n"
            + self.module_of_err
        )


@dataclass(slots=True, frozen=True, eq=False, kw_only=True)
class UserNotFoundInBattle(Exception):
    module_of_err: str = ""

    @property
    def message(self) -> str:
        return (
            "Пользователь не найден в сессии боя!"
            "\n"
            + self.module_of_err
        )


@dataclass(slots=True, frozen=True, eq=False, kw_only=True)
class SelectedCardWithZeroHP(Exception):
    module_of_err: str = ""

    @property
    def message(self) -> str:
        return (
            "Выбрана карта с нулевым здоровьем!"
            "\n"
            + self.module_of_err
        )


@dataclass(slots=True, frozen=True, eq=False, kw_only=True)
class TargetCardWithZeroHP(Exception):
    module_of_err: str = ""

    @property
    def message(self) -> str:
        return (
            "выбрана карта для атаки с нулевым здоровьем!"
            "\n"
            + self.module_of_err
        )


@dataclass(slots=True, eq=False, frozen=True, kw_only=True)
class InvalidTargetTypeError(Exception):
    module_of_err: str = ""
    target: Any = None

    @property
    def message(self) -> str:
        return (
            f"Invalid Target Type {self.target if self.target else ""}"
            "\n"
            + self. module_of_err
        )
