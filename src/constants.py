from enum import Enum
from typing import Literal, Union


class BattleState:
    class global_(Enum):
      start = 'START'
      end = 'END'
      in_process = 'IN_PROCESS'

    class local(Enum):
      wait_opponent = 'ROUND_IN_PROCESS'
      end = "END_OF_ROUND"


BattleInProcessOrEnd = Union[
        Literal[BattleState.local.wait_opponent],
        Literal[BattleState.global_.end],
]