from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, Union, overload

from src import constants
from src.battles.exceptions import InvalidDeckSizeError
from src.battles.schemas import SStandardBattleChoice
from src.cards.models import Ability, AbilityType, Card, MCard, SubAbility, TargetType
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
    def _apply_stat_change(self, ability_type: AbilityType, value: int) -> None:
        """изменение статистики с валидацией"""
        if not hasattr(self, ability_type.value):
            raise AttributeError(
                f"нет такого атрибута {ability_type.value}\n"
                f"{__file__}\n"
                f"class: `{self.__class__}` method: `{self.__class__._apply_stat_change.__name__}`\n"
            )

        current_value = getattr(self, ability_type.value)
        new_value = current_value + value
        
        # валидация что хп не меньше 0
        if ability_type == AbilityType.hp and new_value < 0:
            new_value = 0
            
        setattr(self, ability_type.value, new_value)


    type Card_List = list['CommonCardInBattle']
    @log_func_call(log)
    def _get_target_cards(
        self,
        target: TargetType,
        own_deck: Card_List,
        opponent_deck: Card_List,
    ) -> Card_List:
        """Получение карт-целей"""
        match target:
            case TargetType.ownself:
                return [self]
            
            case TargetType.opponent:
                return opponent_deck
            
            case TargetType.teammates_only:
                return [card for card in own_deck if card is not self]
            
            case TargetType.teammates_and_own:
                return own_deck
            
            case TargetType.all:
                return own_deck + opponent_deck

            case _:
                raise InvalidTargetTypeError(f"Invalid target type: {target}")


    def _apply_ability_to_targets(
        self,
        ability: SubAbility,
        own_deck: Card_List,
        opponent_deck: Card_List,
        duration: Optional[int],
    ) -> None:
        """Применение способности к целевым картам"""
        target_cards = self._get_target_cards(ability.target, own_deck, opponent_deck)
        
        for card in target_cards:
            card._apply_stat_change(ability.type, ability.value)
            if duration is not None:
                card._add_ability_to_active(ability, duration)
    

    def _add_ability_to_active(self, ability: SubAbility, duration: int) -> None:
        """Добавление способности в активные"""
        self.active_abilities[ability] = duration


    def use_ability(
        self,
        own_deck: Card_List,
        opponent_deck: Card_List,
    ) -> None:
        """метод для использования способности"""
        duration = self.ability.duration

        for sub_ability in self.ability.sub_abilities:
            self._apply_ability_to_targets(
                ability=sub_ability,
                own_deck=own_deck,
                opponent_deck=opponent_deck,
                duration=duration,
            )


    def process_abilities(self) -> None:
        """Обработка активных способностей с удалением"""
        expired_abilities: list[SubAbility] = []
        
        # Сначала собираем просроченные способности
        for ability, duration in self.active_abilities.items():
            new_duration = duration - 1
            if new_duration <= 0:
                expired_abilities.append(ability)
            else:
                self.active_abilities[ability] = new_duration
        
        # Затем применяем обратный эффект и удаляем
        for ability in expired_abilities:
            self._apply_stat_change(ability.type, -ability.value)
            del self.active_abilities[ability]


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
