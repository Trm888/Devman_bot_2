import logging
import pathlib
from logging.handlers import RotatingFileHandler

from environs import Env
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from dialogflow_func import detect_intent

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Здравствуйте!')


def get_answer_from_dialog_flow(update: Update, context: CallbackContext, project_id):
    message = update.message
    answer = detect_intent(project_id, message.from_user.id, message.text)
    print(answer)
    context.bot.send_message(chat_id=message.chat_id, text=answer.fulfillment_text)


def submit_error(update: Update, context: CallbackContext, chat_id):
    context.bot.send_message(chat_id=chat_id, text=f'Бот упал с ошибкой {context.error}')


def main():
    env = Env()
    env.read_env()
    bot_token = env.str('TELEGRAM_BOT_TOKEN')
    project_id = env.str('GOOGLE_CLOUD_PROJECT_ID')
    chat_id = env.int('ADMIN_CHAT_ID')
    updater = Updater(bot_token, use_context=True)
    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler(pathlib.PurePath.joinpath(pathlib.Path.cwd(), 'tg_bot.log'),
                                       maxBytes=100000,
                                       backupCount=3)
    file_handler.setFormatter(logging.Formatter('level=%(levelname)s time="%(asctime)s" message="%(message)s"'))
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('level=%(levelname)s time="%(asctime)s" message="%(message)s"'))
    logger.addHandler(stream_handler)
    logger.info('Бот запущен')

    dp = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dp.add_handler(start_handler)

    echo_handler = MessageHandler(Filters.text & (~Filters.command),
                                  lambda update, context: get_answer_from_dialog_flow(update, context, project_id))
    dp.add_handler(echo_handler)
    dp.add_error_handler(lambda update, context: submit_error(update, context, chat_id))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
