import os
from typing import Optional, Union

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from src.shared.patterns import Singletone


load_dotenv()
def _getenv[T_](k: str, default: Optional[T_] = None) -> Union[str, T_]:
  val = os.getenv(k)
  if val is None:
    if default:
      return default

    raise Exception(
      f"can't load {k} from env!!!\n"
      f"Error from {__name__}"
    )
  
  return val

class Config(Singletone):
  db_url: str = "./db.sqlite3"
  ADMIN_ID = int(_getenv("ADMIN_ID", 0))
  TG_API_KEY = _getenv("TG_API_KEY", None)
  bot = Bot(TG_API_KEY)
  dp = Dispatcher()


config = Config()