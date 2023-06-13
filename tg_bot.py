import asyncio
import logging
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher, types, executor
from environs import Env

from dialogflow_func import detect_intent

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.ERROR, format='level=%(levelname)s time="%(asctime)s" message="%(message)s"')


class TelegramLogsHandler(logging.Handler):
    def __init__(self, bot: Bot, chat_id: int):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        asyncio.create_task(self.send_log_message(log_entry))

    async def send_log_message(self, log_entry):
        await self.bot.send_message(chat_id=self.chat_id, text=log_entry)


def main():
    env = Env()
    env.read_env()
    bot_token = env.str('TELEGRAM_BOT_TOKEN')
    project_id = env.str('GOOGLE_CLOUD_PROJECT_ID')
    bot = Bot(bot_token, parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot)
    chat_id = env.int('ADMIN_CHAT_ID')

    logger.info('Бот запущен')
    file_handler = RotatingFileHandler('tg_bot.log', maxBytes=100000, backupCount=3)
    file_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(file_handler)

    telegram_handler = TelegramLogsHandler(bot, chat_id)
    telegram_handler.setFormatter(logging.Formatter('level=%(levelname)s time="%(asctime)s" message="%(message)s"'))
    logger.addHandler(telegram_handler)

    stream_handler = logging.StreamHandler()
    logger.addHandler(stream_handler)

    async def set_default_commands(dp):
        await dp.bot.set_my_commands(
            [
                types.BotCommand('start', 'Запустить бота'),
            ]
        )

    @dp.message_handler(commands=['start'])
    async def start(message: types.Message):
        await message.answer('Здравствуйте!')

    @dp.errors_handler()
    async def errors_handler(update: types.Update, exception: Exception):
        logger.exception(f'Ошибка из телеграмм бота: {exception}')

    @dp.message_handler()
    async def echo(message: types.Message):
        answer = detect_intent(project_id, message.from_user.id, [(message.text)])
        await message.answer(answer.fulfillment_text)

    executor.start_polling(dp, skip_updates=True, on_startup=set_default_commands)


if __name__ == '__main__':
    main()
