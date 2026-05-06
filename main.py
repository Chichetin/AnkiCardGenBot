import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from gigachat import GigaChat

from bot.handlers.card_flow import router
from config import settings
from services.anki import AnkiService
from services.gigachat import GigaChatService
from services.word_queue import WordQueue

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=settings.telegram_token)
    dp = Dispatcher(storage=MemoryStorage())

    gigachat_client = GigaChat(credentials=settings.gigachat_credentials, verify_ssl_certs=False)
    gigachat_service = GigaChatService(client=gigachat_client)
    anki_service = AnkiService(base_url=settings.anki_url, model=settings.anki_model)

    dp.include_router(router)
    dp["gigachat"] = gigachat_service
    dp["anki"] = anki_service
    dp["queue"] = WordQueue()

    logger.info("Bot started. Listening for messages...")
    try:
        await dp.start_polling(bot)
    finally:
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
