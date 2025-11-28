from contextlib import asynccontextmanager
from aiohttp import web
from aiogram import Bot
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from fastapi import FastAPI

from src.database.core import init_db
from src.core.settings import config
from src.cards.raw_cards.copy import _create_raw_cards
from src.handlers.rabbit.core import rabbit


async def on_startup() -> None:
	await init_db()
	await rabbit.start()
	await _create_raw_cards()
	
	# bot: Bot = config.bot
	# await bot.delete_webhook(drop_pending_updates=False)
	
	# url = config.WEBHOOK_PATH
	# await bot.set_webhook(url)
  
async def on_shutdown() -> None:
	await rabbit.stop()


@asynccontextmanager
async def lifespan(app: FastAPI | None = None):
	await on_startup()
	yield
	await on_shutdown()


def create_web_app() -> web.Application:
	app = web.Application()

	bot: Bot = config.bot
	dp = config.dp
	aiogram_webhooks_request_handler = SimpleRequestHandler(
		dispatcher=dp,
		bot=bot,
		# secret_token="1488",
	)
	aiogram_webhooks_request_handler.register(app, config.WEBHOOK_PATH)

	setup_application(app, dp, bot=bot)
	return app