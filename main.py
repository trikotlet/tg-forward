import os
import logging
import logging.handlers
from pathlib import Path
from collections import defaultdict
import time
import signal
from aiogram import Bot, Dispatcher, types, Router
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Создаем папку logs если не существует
Path("logs").mkdir(exist_ok=True)

# Настройка структурированного логирования с ротацией
log_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Файловый логгер с ротацией (10MB, 5 файлов)
file_handler = logging.handlers.RotatingFileHandler(
    "logs/bot.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(log_formatter)

# Консольный логгер
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

# Настройка основного логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Отключаем дублирование логов от aiogram
logging.getLogger("aiogram").setLevel(logging.WARNING)

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

# Глобальные переменные для rate limiting
user_messages = defaultdict(list)  # {user_id: [timestamps]}

# Создаем бота и диспетчер
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Создаем роутер для дополнительных команд
router = Router()

# Health check команда
@router.message(Command("ping"))
async def ping(message: types.Message):
    """Проверка работоспособности бота"""
    await message.reply("🤖 Бот работает и готов к работе!")
    logger.info(f"Health check от пользователя {message.from_user.id}")

# Функция проверки rate limiting
def check_rate_limit(user_id: int) -> bool:
    """Проверяет, не превышает ли пользователь лимит сообщений"""
    now = time.time()

    # Очищаем старые сообщения (последние 60 секунд)
    user_messages[user_id] = [t for t in user_messages[user_id] if now - t < 60]

    # Проверяем лимит (не более 10 сообщений в минуту)
    if len(user_messages[user_id]) >= 10:
        logger.warning(f"Rate limit exceeded for user {user_id}")
        return False

    user_messages[user_id].append(now)
    return True

# Включаем роутер в диспетчер
dp.include_router(router)

@dp.message()
async def forward_message(message: types.Message):
    """Пересылает все сообщения администратору"""
    logger.info(f"Получено сообщение от пользователя {message.from_user.id if message.from_user else 'unknown'}")

    # Проверяем rate limiting
    if not check_rate_limit(message.from_user.id if message.from_user else 0):
        logger.warning(f"Сообщение от пользователя {message.from_user.id if message.from_user else 'unknown'} заблокировано rate limiting")
        return

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

    # Функция для graceful shutdown
    def signal_handler(signum, frame):
        logger.info("Получен сигнал завершения, останавливаю бота...")
        raise KeyboardInterrupt

    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Запускаем polling
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при работе бота: {e}")
        raise
    finally:
        logger.info("Завершение работы бота")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
