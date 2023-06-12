import logging
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher, types, executor
from environs import Env

from run import detect_intent_texts

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO, format='level=%(levelname)s time="%(asctime)s" message="%(message)s"')


def main():
    logger.info('Бот запущен')
    file_handler = RotatingFileHandler('bot.log', maxBytes=100000, backupCount=3)
    file_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    logger.addHandler(stream_handler)

    env = Env()
    env.read_env()
    BOT_TOKEN = env.str('TELEGRAM_TOKEN')
    project_id = env.str('GOOGLE_CLOUD_PROJECT_ID')
    bot = Bot(BOT_TOKEN, parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot)

    async def set_default_commands(dp):
        await dp.bot.set_my_commands(
            [
                types.BotCommand('start', 'Запустить бота'),
            ]
        )

    @dp.message_handler(commands=['start'])
    async def start(message: types.Message):
        logger.info(f'Received start command from user {message.from_user.id}')
        await message.answer('Здравствуйте!')

    @dp.errors_handler()
    async def errors_handler(update: types.Update, exception: Exception):
        await update.message.reply("Произошла ошибка. Пожалуйста, попробуйте еще раз позже.")
        logger.exception(f'Ошибка при обработке запроса {exception}')

    @dp.message_handler()
    async def echo(message: types.Message):
        logger.info(f'Received message from user {message.from_user.id}')
        answer = detect_intent_texts(project_id, message.from_user.id, list(message.text))
        await message.answer(answer)

    executor.start_polling(dp, skip_updates=True, on_startup=set_default_commands)


if __name__ == '__main__':
    main()
