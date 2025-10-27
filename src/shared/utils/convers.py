from src.cards.models import (
    Ability, 
    Card,
    MAbility, 
    MCard,
)


def MCard2Card(card: MCard) -> Card: ...
def MAbility2Ability(ability: MAbility) -> Ability: ...
# def MUser2User(user: MUser)