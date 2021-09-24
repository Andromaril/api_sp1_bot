import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Filters, MessageHandler, Updater

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO, handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ])


PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = Bot(token=TELEGRAM_TOKEN)


def say_hi(update, context):
    chat = update.effective_chat
    logger.info('Send message')
    text_hi = 'Привет,как будут обновления по домашке - сообщу!!!'
    context.bot.send_message(chat_id=CHAT_ID,
                             text=text_hi)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):

    url = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    homework_statuses = requests.get(url, headers=headers, params=payload)
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():

    current_timestamp = int(time.time())

    while True:
        try:
            logger.debug('Start')
            updater = Updater(TELEGRAM_TOKEN, use_context=True)
            updater.dispatcher.add_handler(MessageHandler
                                           (Filters.text, say_hi))
            new_homework = get_homeworks(current_timestamp)
            if new_homework.get('homeworks'):
                homework_now = new_homework.get('homeworks')[0]
                new_status = parse_homework_status(homework_now)
                logger.info('Send message')
                send_message(new_status)
            current_timestamp = new_homework.get(
                'current_date')
            updater.start_polling()
            updater.idle()
            time.sleep(20 * 60)

        except Exception as e:
            logging.error(f'Error {e}!')
            bot.send_message(chat_id=CHAT_ID, text='error!')
            time.sleep(5)


if __name__ == '__main__':
    main()
