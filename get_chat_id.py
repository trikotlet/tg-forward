#!/usr/bin/env python3
"""
Скрипт для получения вашего Chat ID
Запустите этот скрипт, напишите боту, и он покажет ваш Chat ID
"""
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    print("❌ Ошибка: BOT_TOKEN не найден в .env файле")
    print("Создайте .env файл и добавьте ваш токен бота")
    exit(1)

# Создаем бота и диспетчер
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message()
async def show_chat_id(message: types.Message):
    """Показывает Chat ID пользователя"""
    user_info = f"👤 <b>Ваш профиль:</b>\n"
    user_info += f"🆔 <b>Chat ID:</b> <code>{message.chat.id}</code>\n"
    user_info += f"📝 <b>Тип чата:</b> {message.chat.type}\n"

    if message.from_user:
        user_info += f"\n👤 <b>Информация о пользователе:</b>\n"
        user_info += f"🆔 <b>User ID:</b> <code>{message.from_user.id}</code>\n"
        user_info += f"📱 <b>Имя:</b> {message.from_user.full_name or 'Неизвестно'}\n"
        if message.from_user.username:
            user_info += f"📱 <b>Username:</b> @{message.from_user.username}\n"

    await message.reply(
        text=user_info,
        parse_mode=ParseMode.HTML
    )

    logger.info(f"Показан Chat ID для пользователя {message.from_user.id if message.from_user else 'unknown'}")

async def main():
    """Главная функция"""
    print("🤖 Бот для получения Chat ID запущен!")
    print("📱 Напишите любое сообщение боту, и он покажет ваш Chat ID")
    print("❌ Для выхода нажмите Ctrl+C")

    # Запускаем polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
