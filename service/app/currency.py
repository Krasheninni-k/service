"""Скрипт для автоматического обновления курса валют."""
import requests
import time
from app.models import CustomSettings
from app.utils import update_exchange_rate

API_KEY = 'bd98b3a6354bb2880d0f890f40a235a6'
RETRY_PERIOD = 3600
ENDPOINT = 'http://data.fixer.io/api/latest'
CURRENCY_TIME = 0


# Делаем запрос к API, узнаем курс юаня, обновляем значение курса в модели.
def get_currency_rate():
    response = requests.get(f'{ENDPOINT}?access_key={API_KEY}&format=1')
    cny = response.json().get('rates').get('CNY')
    rub = response.json().get('rates').get('RUB')
    currency = round(rub/cny, 4)
    exchange_obj = CustomSettings.objects.last()
    exchange_obj.exchange_rate = currency
    exchange_obj.save()
    return exchange_obj.exchange_rate


# Используется в views.py (catalog, catalog_detail)
def change_prices():
    global CURRENCY_TIME
    print(CURRENCY_TIME)
    timestamp = int(time.time())
    if timestamp > CURRENCY_TIME + 3600:
        print(CURRENCY_TIME)
        print(timestamp)
        CURRENCY_TIME = timestamp
        print(CURRENCY_TIME)
        exchange_rate = get_currency_rate()
        update_exchange_rate(exchange_rate)
