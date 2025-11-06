import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from src.shared.patterns import Singletone


load_dotenv()

class Config(Singletone):
  DB_URL = os.getenv("DB_URL", "")
  ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
  TG_API_KEY = os.getenv("TG_API_KEY")
  bot = Bot(TG_API_KEY)
  dp = Dispatcher()


config = Config()