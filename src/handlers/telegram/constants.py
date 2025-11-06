from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Navigation:
    main = "MAIN"
    profile = "PROFILE"
    battle = "BATTLE"
    shop = "SHOP"
    inventory = "INVENTORY"
    tour = "TOUR"

    @dataclass(frozen=True, slots=True)
    class in_inventory:
        legendary = "LEGENDARY"
        


    @dataclass(frozen=True, slots=True)
    class in_battle:
        standard = "STANDARD"
        duo = "DUO"