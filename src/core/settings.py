import os

# from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from src.shared.patterns import Singletone


load_dotenv()
def _getenv(k: str) -> str:
  val = os.getenv(k)
  if val is None:
    raise Exception(
      f"can't load {k} from env!!!\n"
      f"Error from {__name__}"
    )
  return val

class Config(Singletone):
  ...
  # TG_API_KEY = _getenv("TG_API_KEY")
  # bot = Bot(TG_API_KEY)
  # dp = Dispatcher()


config = Config()