import random

import vk_api as vk
from environs import Env
from vk_api.longpoll import VkLongPoll, VkEventType

from dialogflow_func import detect_intent_texts


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


if __name__ == '__main__':
    main()
