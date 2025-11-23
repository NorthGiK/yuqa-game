from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Annotated, Any, Collection, Optional, Union, overload

from src import constants
from src.battles.exceptions import InvalidDeckSizeError
from src.battles.schemas import SStandardBattleChoice
from src.cards.models import Ability, AbilityType, Card, Deck, MCard, SubAbility, TargetType
from src.logs import dev_configure, get_logger
from src.utils.decorators import log_func_call


log = get_logger(__name__)
dev_configure()

class Battle(ABC):
    """
    Родительский класс для всех типов боёв
    """

    @abstractmethod
    def create_battle(*args: Any, **kwargs: Any) -> Any:
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
class CommonUserInBattle(ABC):
    id: int
    step: Optional[SStandardBattleChoice] = None
    action_score: int = 2


JUST_DELETE = -1

@dataclass(slots=True)
class CommonCardInBattle:
    hp: int
    atk: int
    def_: int
    class_: int
    ability: Ability
    active_abilities: dict[SubAbility, int]

    @log_func_call(log)
    def _use_for_card(
        self: 'CommonCardInBattle',
        abil: SubAbility,
    ) -> None:
        previuous_value: int = getattr(self, abil.type.value)
        setattr(self, abil.type.value, previuous_value + abil.value)


    @log_func_call(log)
    @staticmethod
    def _use_ability_for_card(
            card: "CommonCardInBattle",
            abil: SubAbility,
            own_deck: list["CommonCardInBattle"],
            opponent_deck: list["CommonCardInBattle"],
            duration: int,
            add_to_active: bool = True,
        ) -> None:
        def use_for_deck(
                deck: Collection[CommonCardInBattle],
                abil: SubAbility,
                duration: Optional[int] = None,
            ) -> None:
            for _card in deck:
                _card._use_for_card(abil)
                if duration is not None:
                    _card._add_ability_to_active(abil, duration)
        
        match abil.target:
            case TargetType.ownself:
                deck = (card,)

            case TargetType.opponent:
                deck = opponent_deck

            case TargetType.teammates:
                deck = own_deck
            
            case TargetType.all:
                deck = opponent_deck + own_deck
            
            case _:
                raise DontValidTargetType() # TODO:
        
        use_for_deck(deck, abil, duration if add_to_active else None)


    @log_func_call(log)
    def _add_ability_to_active(
        self: 'CommonCardInBattle',
        abil: SubAbility,
        duration: int,
    ) -> None:
        self.active_abilities[abil] = duration


    @log_func_call(log)
    def add_ability(
        self,
        own_deck: list["CommonCardInBattle"],
        opponent_deck: list["CommonCardInBattle"],
    ) -> None:
        duration: int = self.ability.duration

        for sub_ability in self.ability.sub_abilities:
            self._use_ability_for_card(
                card=self,
                abil=sub_ability,
                duration=duration,
                own_deck=own_deck,
                opponent_deck=opponent_deck,
            )


    @log_func_call(log)
    def process_ability(
        self,
        
    ) -> None:
        active_abilities = self.active_abilities
        for abil in active_abilities.keys():
            active_abilities[abil] -= 1

            if active_abilities[abil] == 0:
                self._use_ability_for_card(
                    card=self,

                )


    @log_func_call(log)
    @staticmethod
    def _get_card(model: Union[MCard, Card]) -> "CommonCardInBattle":
        return CommonCardInBattle(
            hp=model.hp, #type:ignore
            atk=model.atk, #type:ignore
            def_=model.atk, #type:ignore
            class_=0,
            ability=..., # TODO:
        )


    @staticmethod
    @overload
    def from_model(model: Union[Card, MCard]) -> list["CommonCardInBattle"]:
        ...

    @staticmethod
    @overload
    def from_model(model: Union[list[Card], list[MCard]]) -> list["CommonCardInBattle"]:
        ...

    @log_func_call(log)
    @staticmethod
    def from_model(model: Union[Card, MCard, list[Card], list[MCard]]) -> list["CommonCardInBattle"]:
        self = CommonCardInBattle
        if isinstance(model, list):
            return [self._get_card(card) for card in model]

        return [self._get_card(model)]


@dataclass(slots=True, frozen=True)
class DeckSize:
    """
    неизменяемый класс для обозначения размера колоды в бою
    """
    value: int = 0

    def __post_init__(self) -> None:
        if self.value < 0:
            raise InvalidDeckSizeError()
