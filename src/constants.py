from enum import Enum
from typing import Literal


class BattleState:
    class global_(Enum):
      start = 'START'
      end = 'END'
      in_process = 'IN_PROCESS'

    class local(Enum):
      wait_opponent = 'ROUND_IN_PROCESS'
      end = "END_OF_ROUND"


BattleInProcessOrEnd = Literal[
        BattleState.local.wait_opponent,
        BattleState.local.end,
        BattleState.global_.end,
]