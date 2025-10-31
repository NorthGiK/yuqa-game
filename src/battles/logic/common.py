from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, Self

from dataclasses import field

from src import constants
from src.battles.schemas import SSoloBattleChoice


class Battle(ABC):
    """
    Родительский класс для всех типов боёв
    """

    @abstractmethod
    def create_battle(self) -> Self:
        pass


    @abstractmethod
    def calc_step(self, *args: Any, **kwargs: Any) -> constants.BattleInProcessOrEnd:
        """
        метод для подсчёта ходов игроков, их валидации
        и внесения изменений в бою
        """
        pass

    @abstractmethod
    def add_step(self, *args: Any, **kwargs: Any) -> constants.BattleInProcessOrEnd:
        """
        метод для валидации и добавления хода игрока
        """
        pass


@dataclass
class CommonUserInBattle():
    """
    
    """
    id: int
    pos: int
    step: Optional[SSoloBattleChoice] = field(default=None)
    action_score: int = field(default=2)


@dataclass
class CommonCardInBattle():
    """

    """
    hp: int
    atk: int
    def_: int
    class_: int


@dataclass(frozen=True)
class DeckSize:
    """
    неизменяемый класс для обозначения размера колоды в бою
    """
    value: int = field(default=0)