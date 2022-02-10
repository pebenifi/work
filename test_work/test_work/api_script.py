import os
import time
from dotenv import load_dotenv
import logging
import requests
import sys
from datetime import datetime

load_dotenv()

RETRY_TIME = 10
ENDPOINT_API_CONTACTS = 'http://127.0.0.1:8000/contacts/'
ENDPOINT_API_MAILINGS = 'http://127.0.0.1:8000/mailings/'
ENDPOINT_API_MESSAGES = 'http://127.0.0.1:8000/messages/'
ENDPOINT_SENDING_API = 'https://probe.fbrq.cloud/docs'
TIME_FORMAT = "%Y-%m-%d - %H:%M:%S"

end_mailing_id = [] # завершенные рассылки

message_id = [1] #последнее id

logging.basicConfig(
    format='%(asctime)s %(name)s %(levelname)s  %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
    level=logging.ERROR
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



class MissingKeyException(Exception): # ошибка сообщения
    pass


class MissingValueException(Exception): # ошибка отсутвующей переменной
    pass


class GetAPIException(Exception): # ошибка рассылки
    pass


API_TOKEN = os.getenv('API_TOKEN')
SENDING_API_TOKEN = os.getenv('SENDING_API_TOKEN')
if API_TOKEN is None or SENDING_API_TOKEN is None:
    logger.critical('Отсутствуют переменные окружения!')
    raise MissingValueException('Отсутствуют переменные окружения!')


def send_api_message(message_id, contact, message): # отправка сообщений через api
    headers = {'Authorization': f'Bearer {SENDING_API_TOKEN}'}
    json = {
        "id": message_id,
        "phone": contact,
        "text": message,
    }
    try:
        response = requests.post(
            f'{ENDPOINT_SENDING_API}{message_id}/',
            headers=headers,
            json=json
        )
        logger.info('Сообщение отправлено через венешний API')
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as error:
        logger.error(f'Сбой при отправке сообщения: {error}')
        return False


def send_mailing_api_message( # сообщение о выполненной рассылке
    sending_status, mailing_id, contact_id
):

    headers = {'Authorization': f'Bearer {API_TOKEN}'}
    json = {
        'status': sending_status,
        'mailing': mailing_id,
        'contact': contact_id
    }
    try:
        requests.post(
            ENDPOINT_API_MESSAGES, headers=headers, json=json
        )
        logger.info('Сообщение отправлено в API сервиса')
    except Exception:
        raise GetAPIException('API недоступен')


def get_mailing_api_answer(url, tag=None, code=None): # запрос к api рассылки
    headers = {'Authorization': f'Bearer {API_TOKEN}'}
    payload = {'tag': tag, 'code': code}
    try:
        if tag is not None or code is not None:
            response = requests.get(url, headers=headers, params=payload)
        else:
            response = requests.get(url, headers=headers)
        return response.json()
    except Exception:
        raise GetAPIException('API недоступен')


def main():
    logger.debug('-----------------')
    while True:
        try:
            logger.debug('Старт')
            mailings = get_mailing_api_answer(ENDPOINT_API_MAILINGS)
            for mailing in mailings:
                current_datetime = datetime.now()
                if (
                    datetime.strptime(
                        mailing['start_send_time'], TIME_FORMAT
                    ) <= current_datetime
                    and datetime.strptime(
                        mailing['end_send_time'], TIME_FORMAT
                    ) >= current_datetime
                    and mailing['id'] not in end_mailing_id
                ):
                    mailing_id = mailing['id']
                    tag = mailing['tag']
                    code = mailing['code']
                    text = mailing['text']
                    contacts = get_mailing_api_answer(
                        ENDPOINT_API_CONTACTS, tag=tag, code=code
                    )
                    for contact in contacts:
                        current_datetime = datetime.now()
                        contact_id = contact['id']
                        if (
                            current_datetime <= datetime.strptime(
                                mailing['end_send_time'], TIME_FORMAT
                            ) and send_api_message(message_id, contact, text)
                        ):
                            send_mailing_api_message(
                                'S', mailing_id, contact_id
                            )
                        else:
                            send_mailing_api_message(
                                'N', mailing_id, contact_id
                            )
                        message_id[0] += 1
                    end_mailing_id.append(mailing_id)
            logger.debug('Конец')
            logger.debug('-----------------')
            time.sleep(RETRY_TIME)
        except Exception as error:
            logger.error(f'Ошибка: {error}')
            logger.debug('-----------------')
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
