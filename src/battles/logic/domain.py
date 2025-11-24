"""
Классы для управления боями
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Annotated,
    Any,
    Optional,
    Union,
    override,
)
from uuid import UUID, uuid4

from src import constants
from src.battles.exceptions import (
    SelectedCardWithZeroHP,
    TargetCardWithZeroHP,
    UserNotFoundInBattle,
)
from src.battles.models import BattleType
from src.battles.schemas import SStandardBattleChoice
from src.cards.crud import get_cards_by_user_id 
from src.logs import dev_configure, get_logger
from src.utils.decorators import log_func_call
from src.utils.patterns import Singletone
from src.battles.logic.common import (
    Battle,
    CommonCardInBattle, 
    CommonUserInBattle,
    DeckSize,
)


log = get_logger(__name__)
dev_configure()

type Battle_T = Union["Battle", "BattleWithDeck", "BattleStandard", "BattleDuo"]

@dataclass
class BattleWithDeck(Battle, ABC):
    user1: CommonUserInBattle
    user2: CommonUserInBattle
    deck1: list[CommonCardInBattle]
    deck2: list[CommonCardInBattle]
    deck_size: DeckSize
    round: int = 1
    id: Annotated[str, UUID] = field(default_factory=lambda: str(uuid4()))

    @staticmethod
    @abstractmethod
    @log_func_call(log)
    def create_battle(*args: Any, **kwargs: Any) -> Battle_T:
        pass


    @abstractmethod
    @log_func_call(log)
    def get_user(self, id: int) -> CommonUserInBattle:
        match id:
            case self.user1.id:
                return self.user1
            
            case self.user2.id:
                return self.user2
            
            case _:
                raise UserNotFoundInBattle(module_of_err=__file__)


    @abstractmethod
    @log_func_call(log)
    def check_cards_hp(self) -> Optional[str]:
        not_deck1 = not all(self.deck1)
        not_deck2 = not all(self.deck2)

        if not_deck1 and not_deck2:
            return "NIL"
        elif not_deck1:
            return "USER1"
        elif not_deck2:
            return "USER2"

        return None


    @abstractmethod
    @log_func_call(log)
    def calc_curr_action_scores(self) -> None:
        self.round += 1
        self.user1.action_score = max(7, self.round) + self.user1.step.bonus #type:ignore
        self.user2.action_score = max(7, self.round) + self.user2.step.bonus #type:ignore


    @abstractmethod
    @log_func_call(log)
    def validate_round(self) -> None:
        if (
            self.deck1[self.user1.step.selected_card].hp <= 0 #type:ignore
            or
            self.deck2[self.user2.step.selected_card].hp <= 0 #type:ignore
        ):
            raise SelectedCardWithZeroHP(module_of_err=__file__)

        if (
            self.deck2[self.user1.step.target].hp <= 0 #type:ignore
            and
            self.deck1[self.user2.step.target].hp <= 0 #type:ignore
        ):
            raise TargetCardWithZeroHP(module_of_err=__file__)                


    @abstractmethod
    @log_func_call(log)
    def calc_step(
        self,
    ) -> constants.BattleInProcessOrEnd:
        if (self.user1.step is None) or (self.user2.step is None):
            return constants.BattleState.local.wait_opponent
        
        self.user1.step.target -= 1
        self.user2.step.target -= 1
        
        self.user1.step.selected_card -= 1
        self.user2.step.selected_card -= 1

        self.validate_round()

        if self.user1.step.ability:
            self.deck1[self.user1.step.selected_card].use_ability(self.deck1, self.deck2)
        
        if self.user2.step.ability:
            self.deck2[self.user2.step.selected_card].use_ability(self.deck2, self.deck1)

        user1_total_dmg = max(
            0,
            (self.user1.step.hits - self.user2.step.blocks)
            * self.deck1[self.user1.step.selected_card].atk
            - self.deck2[self.user1.step.target].def_
        )

        user2_total_dmg: int = max(
            0,
            (self.user2.step.hits - self.user1.step.blocks)
            * self.deck2[self.user2.step.selected_card].atk
            - self.deck1[self.user2.step.selected_card].def_
        )

        hp1 = self.deck1[self.user2.step.target].hp
        hp2 = self.deck2[self.user1.step.target].hp

        self.deck1[self.user2.step.target].hp = max(0, hp1 - user2_total_dmg)
        self.deck2[self.user1.step.target].hp = max(0, hp2 - user1_total_dmg)

        if not self.check_cards_hp():
            return constants.BattleState.global_.end

        self.calc_curr_action_scores()
        self.user1.step = None
        self.user2.step = None
 
        return constants.BattleState.local.end


    @abstractmethod
    @log_func_call(log)
    def add_step(
        self,
        choice: SStandardBattleChoice,
    ) -> constants.BattleInProcessOrEnd:
        user = self.get_user(choice.user_id)
        user.step = choice

        return self.calc_step()


@dataclass(slots=True)
class BattleDuo(BattleWithDeck):
    @override
    @log_func_call(log)
    @staticmethod
    def create_battle(
        user1: CommonUserInBattle,
        user2: CommonUserInBattle,
        deck1: list[CommonCardInBattle],
        deck2: list[CommonCardInBattle],
    ) -> "BattleStandard":
        return BattleStandard(
            user1=user1,
            user2=user2,
            deck1=deck1,
            deck2=deck2,
            deck_size=DeckSize(len(deck1)),
        )


    def check_cards_hp(self) -> Optional[str]:
        return super().check_cards_hp()

    def calc_curr_action_scores(self) -> None:
        return super().calc_curr_action_scores()

    def validate_round(self) -> None:
        return super().validate_round()

    def calc_step(self) -> constants.BattleInProcessOrEnd:
        return super().calc_step()


    def add_step(
        self,
        choice: SStandardBattleChoice,
    ) -> constants.BattleInProcessOrEnd:
        return super().add_step(choice)


@dataclass
class BattleStandard(BattleWithDeck):
    @staticmethod
    @log_func_call(log)
    @override
    def create_battle(
        user1: CommonUserInBattle,
        user2: CommonUserInBattle,
        deck1: list[CommonCardInBattle],
        deck2: list[CommonCardInBattle],
    ) -> "BattleStandard":
        return BattleStandard(
            user1=user1,
            user2=user2,
            deck1=deck1,
            deck2=deck2,
            deck_size=DeckSize(len(deck1)),
        )


    @override
    def get_user(self, id: int) -> CommonUserInBattle:
        match id:
            case self.user1.id:
                return self.user1

            case self.user2.id:
                return self.user2

            case _:
                raise UserNotFoundInBattle(module_of_err=__file__)


    @override
    def validate_round(self) -> None:
        return super().validate_round()

    @override
    def check_cards_hp(self) -> Optional[str]:
        return super().check_cards_hp()


    @override
    def calc_curr_action_scores(self):
        return super().calc_curr_action_scores()


    @override
    def calc_step(
        self,
    ) -> constants.BattleInProcessOrEnd:
        return super().calc_step()


    @override
    def add_step(
        self,
        choice: SStandardBattleChoice,
    ) -> constants.BattleInProcessOrEnd:
        return super().add_step(choice)


@dataclass(slots=True)
class _BattlesManagement(Singletone):
    battles: dict[str, Battle_T] = field(default_factory=dict) #type:ignore

    @log_func_call(log)
    async def create_battle(
        self,
        usr1: int,
        usr2: int,
        type: Annotated[str, BattleType],
    ) -> Optional[str]:
        deck1 = await get_cards_by_user_id(usr1)
        deck2 = await get_cards_by_user_id(usr2)

        if (not deck1) or (not deck2):
            return None

        match type:
            case BattleType.duo:
                battle = BattleDuo.create_battle(
                    user1=CommonUserInBattle(usr1),
                    user2=CommonUserInBattle(usr2),
                    deck1=deck1,
                    deck2=deck2,
                )

            case _:
                print("pizdec")
                return None

        id: str = battle.id
        self.battles[id] = battle

        return id


    @log_func_call(log)
    def get_battle(self, id: str) -> Optional[Battle_T]:
        return self.battles.get(id, None)


    @log_func_call(log)
    def remove_battle(self, battle_id: str) -> bool:
        if self.battles.get(battle_id):
            is_delete = self.battles.pop(battle_id, False)
            return bool(is_delete)

        return False


BattlesManagement = _BattlesManagement()