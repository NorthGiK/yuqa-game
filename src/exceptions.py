from dataclasses import dataclass


@dataclass(frozen=True, slots=True, eq=False)
class UndefinedBattleTypeError(Exception):
    @property
    def message(self) -> str:
        return "Undefined Battle Type!"

@dataclass(frozen=True, slots=True, eq=False)
class UndefinedCardIdError(Exception):
    @property
    def message(self) -> str:
        return ("Undefined Card Id!")
