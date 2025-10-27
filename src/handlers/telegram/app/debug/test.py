import asyncio
import os

from aiogram import Bot, Router, Dispatcher, F
from aiogram.types import Message


router = Router()

MEDIA_DIR = 'dir'

@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot):
  photo = message.photo[-1]
  file_id = photo.file_id

  file = await bot.get_file(file_id)
  file_path = file.file_path

  user_id = message.from_user.id
  timestamp = int(message.date.timestamp())
  filename = f"photo_{user_id}_{timestamp}.jpg"
  save_path = os.path.join(MEDIA_DIR, filename)

  await bot.download_file(file_path, save_path)

@router.message(F.document)
async def handle_document_image(message: Message, bot: Bot):
  document = message.document
  
  if document.mime_type and document.mime_type.startswith('image/'):
    file_id = document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    
    if document.file_name:
      ext = os.path.splitext(document.file_name)[1] or '.jpg'
    else:
      mime_to_ext = {
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/webp': '.webp',
      }
      ext = mime_to_ext.get(document.mime_type, '.jpg')
    
    user_id = message.from_user.id
    timestamp = int(message.date.timestamp())
    filename = f"doc_image_{user_id}_{timestamp}{ext}"
    save_path = os.path.join(MEDIA_DIR, filename)
    
    await bot.download_file(file_path, save_path)
            
async def _():
  dp = Dispatcher()
  bot = Bot('8032324406:AAFNPf-kYPTPztIxmE_D-AfOdDOpt59uo8w')
  await dp.start_polling(bot)

asyncio.run(_())