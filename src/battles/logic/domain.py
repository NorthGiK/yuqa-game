"""
Классы для управления боями
"""

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from pprint import pprint
from typing import (
    Annotated,
    Any,
    Optional,
    Union,
    override,
)
from uuid import UUID, uuid4

from src import constants
from src.battles.models import BattleType
from src.battles.schemas import SStandardBattleChoice, SSoloBattleChoice
from src.cards.crud import get_cards_by_user_id 
from src.utils.patterns import Singletone
from src.battles.logic.common import (
    Battle,
    CommonCardInBattle, 
    CommonUserInBattle,
    DeckSize,
)


type Battle_T = Union["Battle", "BattleWithDeck", "BattleStandard", "BattleDuo"]

@dataclass
class BattleWithDeck(Battle, ABC):
    user1: CommonUserInBattle
    user2: CommonUserInBattle
    deck1: list[CommonCardInBattle]
    deck2: list[CommonCardInBattle]
    deck_size: DeckSize = DeckSize(0)
    round: int = 1
    id: Annotated[str, UUID] = field(default_factory=lambda: str(uuid4()))

    @abstractmethod
    def create_battle(*args: Any, **kwargs: Any) -> Battle_T:
        pass


    @abstractmethod
    def check_cards_hp(self) -> str:
        if (not all(self.deck1)) and (not all(self.deck2)):
            return "NIL"
        elif not all(self.deck1):
            return "USER1"
        elif not all(self.deck2):
            return "USER2"
        return ""


    @abstractmethod
    def calc_curr_action_scores(self) -> None:
        self.round += 1
        self.user1.action_score = max(7, round(self.round * 1.5)) + self.user1.step.bonus #type:ignore
        self.user2.action_score = max(7, round(self.round * 1.5)) + self.user2.step.bonus #type:ignore


    @abstractmethod
    @override
    def calc_step(
        self,
    ) -> constants.BattleInProcessOrEnd:
        if (self.user1.step is None) or (self.user2.step is None):
            return constants.BattleState.local.wait_opponent

        user1_total_dmg = max(
            0,
            (self.user1.step.hits - self.user2.step.blocks)
            * self.deck1[self.user1.step.selected_card - 1].atk
            - self.deck2[self.user1.step.target - 1].def_
        )

        user2_total_dmg: int = max(
            0,
            (self.user2.step.hits - self.user1.step.blocks)
            * self.deck2[self.user2.step.selected_card - 1].atk
            - self.deck1[self.user2.step.selected_card - 1].def_
        )

        hp1 = self.deck1[self.user2.step.target - 1].hp
        hp2 = self.deck2[self.user1.step.target - 1].hp

        self.deck1[self.user2.step.target - 1].hp = max(0, hp1 - user2_total_dmg)
        self.deck2[self.user1.step.target - 1].hp = max(0, hp2 - user1_total_dmg)

        if not self.check_cards_hp():
            return constants.BattleState.global_.end

        self.calc_curr_action_scores()
        self.user1.step = None
        self.user2.step = None
        
        pprint(asdict(self))
        return constants.BattleState.local.end


    @abstractmethod
    @override
    def add_step(
        self,
        choice: SStandardBattleChoice,
    ) -> constants.BattleInProcessOrEnd:
        if choice.user_id == self.user1.id:
            self.user1.step = choice
        elif choice.user_id == self.user2.id:
            self.user2.step = choice
        else:
            raise Exception("WTF EXCEPTION!!??!!??")

        return self.calc_step()


@dataclass(slots=True)
class BattleDuo(BattleWithDeck):
    @override
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
        )


    @override
    def check_cards_hp(self) -> str:
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


@dataclass
class BattleStandard(BattleWithDeck):
    @override
    def create_battle(
        self,
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
        )


    @override
    def check_cards_hp(self) -> str:
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


@dataclass
class BattleSolo(Battle):
    """
    battle instance that provided battle between 2 players with 1 card only
    """

    user1: CommonUserInBattle
    user2: CommonUserInBattle
    card1: CommonCardInBattle
    card2: CommonCardInBattle

    user1_step: Optional[SSoloBattleChoice] = field(default=None)
    user2_step: Optional[SSoloBattleChoice] = field(default=None)

    id: str = field(default_factory=lambda : str(uuid4()))
    round: int = field(default=1)


    @override
    def create_battle(
        self,
        user1: CommonUserInBattle,
        user2: CommonUserInBattle,
        card1: CommonCardInBattle,
        card2: CommonCardInBattle,
    ) -> "BattleSolo":
        return BattleSolo(
            user1=user1,
            user2=user2,
            card1=card1,
            card2=card2,
        )


    def calc_current_action_scores(self) -> None:
        self.user1.action_score = max(7, self.round * 2) + self.user1.step.bonus #type:ignore
        self.user2.action_score = max(7, self.round * 2) + self.user2.step.bonus #type:ignore


    def calc_current_damages(self) -> None:
        user1_total_hits: int = max(0, self.user1_step.hits - self.user2_step.blocks) #type:ignore
        user2_total_hits: int = max(0, self.user2_step.hits - self.user1_step.blocks) #type:ignore
        self.card1.hp = max(0, self.card1.hp - user2_total_hits)
        self.card2.hp = max(0, self.card2.hp - user1_total_hits)        


    @override
    def calc_step(self) -> constants.BattleInProcessOrEnd:
        self.calc_current_damages()

        if (not self.card1.hp) or (not self.card2.hp):
            return constants.BattleState.global_.end

        self.calc_current_action_scores()
        self.user1.step = None
        self.user2.step = None
        self.round += 1

        return constants.BattleState.local.wait_opponent


    @override
    def add_step(
        self,
        user_id: int,
        choice: SStandardBattleChoice,
    ) -> constants.BattleInProcessOrEnd:
        if user_id == self.user1:
            self.user1.step = choice
        else:
            self.user2.step = choice

        if self.user1.step and self.user2.step:
            battle_status = self.calc_step()
            return battle_status

        return constants.BattleState.local.wait_opponent


@dataclass(slots=True)
class _BattlesManagement(Singletone):
    battles: dict[str, Battle_T] = field(default_factory=dict) #type:ignore

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
                return

        id: str = battle.id
        self.battles[id] = battle

        return id


    def get_battle(self, id: str) -> Optional[Battle_T]:
        return self.battles.get(id, None)


    def remove_battle(self, battle_id: str) -> bool:
        if self.battles.get(battle_id):
            del self.battles[battle_id]
            return True

        return False


BattlesManagement = _BattlesManagement()