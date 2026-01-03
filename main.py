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

# Получаем токены из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

if not BOT_TOKEN or not ADMIN_CHAT_ID:
    raise ValueError("BOT_TOKEN и ADMIN_CHAT_ID должны быть установлены в .env файле")

# Конвертируем ADMIN_CHAT_ID в int
try:
    ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)
except ValueError:
    raise ValueError("ADMIN_CHAT_ID должен быть числом (Chat ID)")

# Создаем бота и диспетчер
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message()
async def forward_message(message: types.Message):
    """Пересылает все сообщения администратору"""
    logger.info(f"Получено сообщение от пользователя {message.from_user.id if message.from_user else 'unknown'}")
    try:
        # Получаем информацию об отправителе
        user_info = f"👤 <b>Пользователь:</b> {message.from_user.full_name or 'Неизвестный'}\n"
        user_info += f"🆔 <b>ID:</b> <code>{message.from_user.id}</code>\n"

        if message.from_user.username:
            user_info += f"📱 <b>Username:</b> @{message.from_user.username}\n"

        user_info += f"💬 <b>Чат ID:</b> <code>{message.chat.id}</code>\n"
        user_info += f"📅 <b>Время:</b> {message.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
        user_info += f"📝 <b>Тип чата:</b> {message.chat.type}\n\n"

        # Если сообщение текстовое
        if message.text:
            user_info += f"💭 <b>Сообщение:</b>\n{message.text}"
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=user_info,
                parse_mode=ParseMode.HTML
            )

        # Если есть фото
        elif message.photo:
            # Берем самое качественное фото
            photo = message.photo[-1]
            caption = user_info + f"📷 <b>Фото с подписью:</b>\n{message.caption}" if message.caption else user_info + "📷 <b>Фото</b>"
            await bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=photo.file_id,
                caption=caption,
                parse_mode=ParseMode.HTML
            )

        # Если есть документ
        elif message.document:
            caption = user_info + f"📄 <b>Документ:</b>\n{message.caption}" if message.caption else user_info + "📄 <b>Документ</b>"
            await bot.send_document(
                chat_id=ADMIN_CHAT_ID,
                document=message.document.file_id,
                caption=caption,
                parse_mode=ParseMode.HTML
            )

        # Если есть аудио
        elif message.audio:
            caption = user_info + f"🎵 <b>Аудио:</b>\n{message.caption}" if message.caption else user_info + "🎵 <b>Аудио</b>"
            await bot.send_audio(
                chat_id=ADMIN_CHAT_ID,
                audio=message.audio.file_id,
                caption=caption,
                parse_mode=ParseMode.HTML
            )

        # Если есть видео
        elif message.video:
            caption = user_info + f"🎥 <b>Видео:</b>\n{message.caption}" if message.caption else user_info + "🎥 <b>Видео</b>"
            await bot.send_video(
                chat_id=ADMIN_CHAT_ID,
                video=message.video.file_id,
                caption=caption,
                parse_mode=ParseMode.HTML
            )

        # Если есть голосовое сообщение
        elif message.voice:
            caption = user_info + "🎤 <b>Голосовое сообщение</b>"
            await bot.send_voice(
                chat_id=ADMIN_CHAT_ID,
                voice=message.voice.file_id,
                caption=caption,
                parse_mode=ParseMode.HTML
            )

        # Если есть стикер
        elif message.sticker:
            caption = user_info + "🎭 <b>Стикер</b>"
            await bot.send_sticker(
                chat_id=ADMIN_CHAT_ID,
                sticker=message.sticker.file_id
            )
            # Отправляем информацию о стикере отдельно
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=caption,
                parse_mode=ParseMode.HTML
            )

        # Другие типы сообщений
        else:
            user_info += f"📦 <b>Неизвестный тип сообщения:</b> {message.content_type}"
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=user_info,
                parse_mode=ParseMode.HTML
            )

        logger.info(f"Переслано сообщение от пользователя {message.from_user.id}")

    except Exception as e:
        logger.error(f"Ошибка при пересылке сообщения: {e}")
        logger.error(f"Проверьте правильность ADMIN_CHAT_ID: {ADMIN_CHAT_ID}")
        # Не пытаемся отправить сообщение администратору об ошибке,
        # чтобы избежать рекурсивных ошибок

async def main():
    """Главная функция для запуска бота"""
    logger.info("Бот запущен и готов к работе!")
    logger.info(f"Администратор Chat ID: {ADMIN_CHAT_ID}")

    # Запускаем polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
