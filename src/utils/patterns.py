from typing import Self


class Singletone:
    def __new__(cls) -> Self:
        if not hasattr(cls, "instance"):
            cls.instance = super(Singletone, cls).__new__(cls)
        return cls.instance
