import logging
import random
from logging.handlers import RotatingFileHandler

import telegram
import vk_api as vk
from environs import Env
from vk_api.longpoll import VkLongPoll, VkEventType

from dialogflow_func import detect_intent

logger = logging.getLogger('database')


class TelegramLogsHandler(logging.Handler):
    def __init__(self, bot, chat_id):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(chat_id=self.chat_id, text=log_entry)


def echo(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=random.randint(1, 1000)
    )


def main():
    env = Env()
    env.read_env()
    vk_group_token = env.str('VK_API_KEY')
    project_id = env.str('GOOGLE_CLOUD_PROJECT_ID')
    bot_token = env.str('TELEGRAM_TOKEN_FOR_VK_BOT')
    bot = telegram.Bot(token=bot_token)
    chat_id = env.int('ADMIN_CHAT_ID')

    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler('vk_bot.log', maxBytes=100000, backupCount=3)
    file_handler.setFormatter(logging.Formatter('level=%(levelname)s time="%(asctime)s" message="%(message)s"'))
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('level=%(levelname)s time="%(asctime)s" message="%(message)s"'))
    logger.addHandler(stream_handler)
    logger.info('Бот запущен')

    telegram_handler = TelegramLogsHandler(bot, chat_id)
    telegram_handler.setFormatter(logging.Formatter('level=%(levelname)s time="%(asctime)s" message="%(message)s"'))
    logger.addHandler(telegram_handler)

    while True:
        try:
            vk_session = vk.VkApi(token=vk_group_token)
            vk_api = vk_session.get_api()
            longpoll = VkLongPoll(vk_session)
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    chat_id = event.chat_id
                    answer = detect_intent(project_id, chat_id, [(event.text)])
                    if answer.intent.is_fallback:
                        continue
                    else:
                        vk_api.messages.send(chat_id=chat_id, message=answer.fulfillment_text, random_id=random.randint(1, 1000))
                        vk_api.messages.send(user_id=event.user_id, message=answer.fulfillment_text, random_id=random.randint(1, 1000))
        except Exception as error:
            logger.exception(f'Ошибка из телеграмм бота: {error}')
            continue


if __name__ == '__main__':
    main()
