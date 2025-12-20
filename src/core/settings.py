from dataclasses import dataclass
import os
from typing import Optional, Any

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from src.utils.patterns import Singletone


load_dotenv()

@dataclass(frozen=True, slots=True, eq=False)
class EnvError(Exception):
	var: str

	@property
	def message(var: Any) -> str:
		return (
			"Error while loading enviroment!!\n"
			f"variable `{var}` can't be load!"
		)


def _custom_getenv(name: str, /, default: Any = None) -> str:
	"""
	чтобы линтеры не ругались на переменные не того типа
	"""
	data: Optional[str] = os.getenv(name)
	if data is None:
		if default is not None:
			return default
		raise EnvError(name)

	return data


@dataclass(frozen=True, eq=False)
class TGConnectionConfig(Singletone):
	LOCAL_WEBAPP_HOST = _custom_getenv("WEBHOOK_HOST")
	LOCAL_WEBAPP_PORT = int(_custom_getenv("WEBHOOK_PORT"))
	WEBHOOK_PATH = _custom_getenv("WEBHOOK_PATH")


@dataclass(frozen=True, eq=False)
class TGWorkflowConfig(Singletone):
	TG_API_KEY = _custom_getenv("TG_API_KEY")
	default = DefaultBotProperties(parse_mode="markdown")
	bot = Bot(TG_API_KEY, default=default)
	dp = Dispatcher()
	storage = MemoryStorage()
	ADMIN_ID = int(_custom_getenv("ADMIN_ID"))


@dataclass(frozen=True, eq=False)
class DBConfig(Singletone):
	DB_URL = _custom_getenv("DB_URL")


@dataclass(frozen=True, slots=True, eq=False)
class Config(Singletone):
	tg_connection = TGConnectionConfig()
	tg_workflow = TGWorkflowConfig()
	db = DBConfig()

config = Config()