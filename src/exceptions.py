class UndefinedBattleTypeError(Exception):
  @property
  def message(self) -> str:
    return "Undefined Battle Type!"


class UndefinedCardIdError(Exception):
  @property
  def message(self) -> str:
    return ("Undefined Card Id!")