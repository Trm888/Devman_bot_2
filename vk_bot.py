import logging
import random
from logging.handlers import RotatingFileHandler

import vk_api as vk
from environs import Env
from vk_api.longpoll import VkLongPoll, VkEventType

from dialogflow_func import detect_intent_texts

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO, format='level=%(levelname)s time="%(asctime)s" message="%(message)s"')


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

    logger.info('Бот запущен')
    file_handler = RotatingFileHandler('vk_bot.log', maxBytes=100000, backupCount=3)
    file_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    logger.addHandler(stream_handler)
    while True:
        try:
            vk_session = vk.VkApi(token=vk_group_token)
            vk_api = vk_session.get_api()
            longpoll = VkLongPoll(vk_session)
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    chat_id = event.chat_id
                    print([(event.text)])
                    answer = detect_intent_texts(project_id, chat_id, [(event.text)])
                    vk_api.messages.send(chat_id=chat_id, message=answer, random_id=random.randint(1, 1000))
                    vk_api.messages.send(user_id=event.user_id, message=answer, random_id=random.randint(1, 1000))

        except Exception as error:
            logger.exception(f'Ошибка при обработке запроса {error}')
            continue

if __name__ == '__main__':
    main()
