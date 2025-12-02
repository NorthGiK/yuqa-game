from typing import Optional, TypedDict, Union

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile

from src.cards.models import MCard
from src.core.settings import Config
from src.gacha.random import RandomManager
from src.handlers.rabbit.constants import PIT_GOLD
from src.handlers.telegram.components import tabs
from src.handlers.telegram.constants import Navigation
from src.handlers.telegram.gacha.raw import GETTING_CARD_MESSAGE, MAIN_GACHA_MESSAGE
from src.users.crud import UserRepository


router = Router()

async def show_main_gacha_message(
	msg: Union[Message, CallbackQuery, None] = None,
	user_id: Optional[int] = None,
) -> None:
	if (msg is None) and (user_id is None):
		raise Exception("dont given neither user id nor msg")

	send_data = dict(
		text=MAIN_GACHA_MESSAGE,
		reply_markup=tabs.gacha,
		parse_mode="markdown",
	)

	async def send_callback() -> None:
		await msg.answer()
		await msg.message.answer(**send_data)

	async def send_message() -> None:
		await msg.answer(**send_data)

	async def send_bot() -> None:
		bot = Config().tg_workflow.bot
		await bot.send_message(
			user_id,
			**send_data,
		)

	if msg is not None:
		if isinstance(msg, CallbackQuery):
			await send_callback()
		else:
			await send_message()
		return
	
	await send_bot()


@router.callback_query(F.data == Navigation.gacha)
async def show_main_gacha_handler(clbk: CallbackQuery) -> None:
	await show_main_gacha_message(clbk)


@router.callback_query(F.data == str(PIT_GOLD))
async def pit_legendary_handler(clbk: CallbackQuery) -> None:
	await clbk.answer()

	rarity = RandomManager().choose_rarity().value

	earned_card: MCard = await RandomManager().choose_card(rarity, universe=None)
	await UserRepository.add_new_card(clbk.from_user.id, earned_card.id)

	await clbk.message.answer_photo(
		photo=FSInputFile(f"static/{earned_card.image}"),
		caption=GETTING_CARD_MESSAGE(earned_card),
		parse_mode=None,
	)

	user_id: int = clbk.from_user.id
	card_id: int = earned_card.id
	if earned_card.id not in await UserRepository.get_user_inventory(user_id):
		await UserRepository.add_new_card(user_id, card_id)
