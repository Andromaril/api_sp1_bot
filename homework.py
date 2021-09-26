import logging
import os
import sys
import time

import requests
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Filters, MessageHandler, Updater

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO, handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler(sys.stdout)
    ])


PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = Bot(token=TELEGRAM_TOKEN)


def say_hi(update, context):
    """Приветствие в ответ на любое текстовое сообщение пользователя."""
    update.effective_chat
    logger.info('Send message')
    text_hi = 'Привет,как будут обновления по домашке - сообщу!!!'
    context.bot.send_message(chat_id=CHAT_ID,
                             text=text_hi)


def parse_homework_status(homework):
    """Проверка статуса домашней работы,
       отправляет нужное сообщение к каждому статусу.
    """
    homework_name = homework.get('homework_name')
    if homework_name is None:
        logger.error('no server response')
        return 'нет ответа сервера'
    status = homework.get('status')
    if status is None:
        logger.error('no server response')
        return 'нет ответа сервера'
    if status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    """Получение статуса домашней работы."""
    url = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=payload)
    except requests.exceptions.RequestException as no_status:
        logging.error(f'Error {no_status}!')
    return homework_statuses.json()


def send_message(message):
    """Отправка сообщений."""
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    """Вызывает все функции."""
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
