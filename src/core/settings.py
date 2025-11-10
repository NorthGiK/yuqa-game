from dataclasses import dataclass, asdict
import os
from typing import Optional, Any

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from src.shared.patterns import Singletone


load_dotenv()

class EnvError(Exception):
	@property
	def message(var: Any) -> str:
		return (
			"Error while loading enviroment!!\n"
			f"variable {var} can't be load!"
		)


def _custom_getenv[T: Optional[Any]](name: str, /, default: Any = None) -> str:
	"""
	чтобы линтеры не ругались на переменные не того типа
	"""
	data: Optional[str] = os.getenv(name)
	if data is None:
		if default is not None:
			return default
		raise EnvError()

	return data


@dataclass(frozen=True, slots=True)
class Config(Singletone):
	LOCAL_WEBAPP_HOST = _custom_getenv("WEBHOOK_HOST")
	LOCAL_WEBAPP_PORT = int(_custom_getenv("WEBHOOK_PORT"))
	WEBHOOK_PATH = _custom_getenv("WEBHOOK_PATH")
	DB_URL = _custom_getenv("DB_URL")
	ADMIN_ID = int(_custom_getenv("ADMIN_ID", 0))
	TG_API_KEY = _custom_getenv("TG_API_KEY")
	bot = Bot(TG_API_KEY)
	dp = Dispatcher()

	def __post_init__(self) -> None:
		for variable, value in asdict(self).items():
			if value is None:
				raise EnvError(variable)


config = Config()