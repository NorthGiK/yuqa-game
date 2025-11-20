from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, Union

from dataclasses import field

from src import constants
from src.battles.schemas import SStandardBattleChoice
from src.cards.models import Card, MCard


class Battle(ABC):
    """
    Родительский класс для всех типов боёв
    """

    @abstractmethod
    def create_battle() -> Any:
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


@dataclass(slots=True)
class CommonUserInBattle():
    id: int
    step: Optional[SStandardBattleChoice] = field(default=None)
    action_score: int = field(default=2)


@dataclass(slots=True)
class CommonCardInBattle():
    hp: int
    atk: int
    def_: int
    class_: int

    @staticmethod
    def _get_card(model: Union[MCard, Card]) -> "CommonCardInBattle":
        return CommonCardInBattle(
            hp=model.hp, #type:ignore
            atk=model.atk, #type:ignore
            def_=model.atk, #type:ignore
            class_=0,
        )

    @staticmethod
    def from_model(model):
        self = CommonCardInBattle
        if isinstance(model, list):
            return [self._get_card(card) for card in model]
        
        return self._get_card(model)


@dataclass(slots=True, frozen=True)
class DeckSize:
    """
    неизменяемый класс для обозначения размера колоды в бою
    """
    value: int = field(default=0)