import json
import requests
import translators as ts
import conf
import time
from datetime import datetime


def read_file() -> dict:
    """Функция для чтения файла со списком магазинов"""
    with open('data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def write_file(data):
    """Функция для записи в файл со списком магазинов"""
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f)


def add_shop(shop_id: str):
    """Добавляет магазин в список"""
    data = read_file()
    if shop_id not in data:
        data[shop_id] = []
        write_file(data)


def get_dates() -> dict:
    data = read_file()
    dates = []
    for shop_id in data:
        items = data[shop_id]
        for item in items:
            date = item['date'][:-3]
            if date not in dates:
                dates.append(date)

    out = {}

    for date in dates:
        year = date.split(' ')[0]
        month = date.split(' ')[1]
        day = date.split(' ')[2]
        if year not in out:
            out[year] = {}
        if month not in out[year]:
            out[year][month] = []
        if day not in out[year][month]:
            out[year][month].append(day)

    return out


def check_date_shop(ord: str, shop: str):
    data = read_file()

    for item in data[shop]:
        if ord != 'last':
            if ord == item['date'][:-3]:
                return True
        else:
            now = datetime.now()
            seconds_in_day = 24 * 60 * 60
            date = datetime.strptime(item['date'], '%Y %m %d %H')
            difference = now - date
            seconds = (difference.days * seconds_in_day + difference.seconds)
            if seconds <= 86400:
                return True

    return False


def requests_shop_info(shop) -> dict:
    cookies = {
        'token': 'QkEwNTQ0REFGQ0MwODFCNTFBMzU4QjgwRjM5MDc4OUVFODcwQzg3MTd'
                 'EMTMwRUFDMTQ5QjZENEVBODYxQUUxRDUyNUE4NjhCRDA4NDdEMjI2MkQ5OUU2ODM5Rjk5RDE1',
        'client_type': 'net',
        'sensorsdata2015jssdkcross': '%7B%22distinct_id%22%3A%22_dirirC7SsDbNrx7VrVyfcM-irynK9R'
                                     '-14r0f7sA%22%2C%22first_id%22%3A%2218e7fd8cd09dee-053d1a'
                                     '5663075fc-367b7031-1049088-18e7fd8cd0aee5%22%2C%22props%'
                                     '22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%'
                                     'B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_k'
                                     'eyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%'
                                     '9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_refer'
                                     'rer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpd'
                                     'HlfbG9naW5faWQiOiJfZGlyaXJDN1NzRGJOcng3VnJWeWZjTS1pcnluS'
                                     'zlSLTE0cjBmN3NBIiwiJGlkZW50aXR5X2Nvb2tpZV9pZCI6IjE4ZTdmZD'
                                     'hjZDA5ZGVlLTA1M2QxYTU2NjMwNzVmYy0zNjdiNzAzMS0xMDQ5MDg4LTE'
                                     '4ZTdmZDhjZDBhZWU1In0%3D%22%2C%22history_login_id%22%3A%7B%'
                                     '22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%2'
                                     '2_dirirC7SsDbNrx7VrVyfcM-irynK9R-14r0f7sA%22%7D%2C%22%24d'
                                     'evice_id%22%3A%2218e7fd8cd09dee-053d1a5663075fc-367b7031-'
                                     '1049088-18e7fd8cd0aee5%22%7D',
        'JSESSIONID': '5785A4E842AB33B8BA65B2CC0E213061',
    }

    headers = {
        'authority': 'www.szwego.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru,en;q=0.9',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "YaBrowser";v="24.1", "Yowser";v="2.5"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36',
        'wego-albumid': '',
        'wego-channel': 'net',
        'wego-staging': '0',
        'wego-uuid': '',
        'wego-version': '',
    }

    params = {
        'targetAlbumId': str(shop),
    }

    response = requests.get(
        'https://www.szwego.com/albums/api/v3/contacts/getFriendAlbumInfo',
        params=params,
        cookies=cookies,
        headers=headers,
    ).json()

    return response


def get_shop_img(shop):

    img_url = requests_shop_info(shop)['result']['headerImgWxurl']

    return requests.get(img_url).content


def get_shop_name(shop):

    name = requests_shop_info(shop)['result']['nickName']

    return name


def get_shop_number(shop) -> str | list:

    response = requests_shop_info(shop)

    if 'result' in response:
        if 'wxNum' in response['result']:
            if response['result']['wxNum'] != '':
                return response['result']['wxNum']
        if 'wxNumQrcodeUrl' in response['result']:
            qr = response['result']['wxNumQrcodeUrl']
            if qr != '':
                return [response['result']['wxNumQrcodeUrl'], 1]
            else:
                return ' '
    else:
        return ' '


def pars_one(url: str) -> dict | None:
    url = url.split('/')
    shop = url[-2]
    prod = url[-1]
    cookies = {
        'token': 'QkEwNTQ0REFGQ0MwODFCNTFBMzU4QjgwRjM5MDc4OUVFODcwQzg3MTdEMTMwRUFDMTQ5QjZEN'
                 'EVBODYxQUUxRDUyNUE4NjhCRDA4NDdEMjI2MkQ5OUU2ODM5Rjk5RDE1',
        'client_type': 'net',
        'sensorsdata2015jssdkcross': '%7B%22distinct_id%22%3A%22_dirirC7SsDbNrx7VrVyfcM-irynK9R-'
                                     '14r0f7sA%22%2C%22first_id%22%3A%2218e7fd8cd09dee-053d1a5663075fc'
                                     '-367b7031-1049088-18e7fd8cd0aee5%22%2C%22props%22%3A%7B%22%24lat'
                                     'est_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87'
                                     '%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E'
                                     '5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24'
                                     'latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbn'
                                     'RpdHlfbG9naW5faWQiOiJfZGlyaXJDN1NzRGJOcng3VnJWeWZjTS1pcnluSzlSLTE0'
                                     'cjBmN3NBIiwiJGlkZW50aXR5X2Nvb2tpZV9pZCI6IjE4ZTdmZDhjZDA5ZGVlLTA1M2Q'
                                     'xYTU2NjMwNzVmYy0zNjdiNzAzMS0xMDQ5MDg4LTE4ZTdmZDhjZDBhZWU1In0%3D%22%'
                                     '2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%'
                                     '22%2C%22value%22%3A%22_dirirC7SsDbNrx7VrVyfcM-irynK9R-14r0f7sA%22%7D'
                                     '%2C%22%24device_id%22%3A%2218e7fd8cd09dee-053d1a5663075fc-367b7031-1'
                                     '049088-18e7fd8cd0aee5%22%7D',
        'JSESSIONID': 'A6802D722FE2D6834A2E362DA76FD489',
    }

    headers = {
        'authority': 'www.szwego.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru,en;q=0.9',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "YaBrowser";v="24.1", "Yowser";v="2.5"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36',
        'wego-albumid': '',
        'wego-channel': 'net',
        'wego-staging': '0',
        'wego-uuid': '',
        'wego-version': '',
    }

    params = {
        'targetAlbumId': shop,
        'itemId': prod,
        't': '1713181179965',
        'transLang': 'en',
    }

    response = requests.get('https://www.szwego.com/commodity/view',
                            params=params, cookies=cookies, headers=headers)
    try:
        response = response.json()['result']['commodity']
        item = {
            'imgs': response['imgsSrc'],
            'dis': response['title'],
            'shop': shop
        }
        return item
    except Exception as e:
        print(e)
        return None


def check_shop(shop: str) -> list | None:

    # куки для запроса к сервису
    cookies = {
        'token': 'QkEwNTQ0REFGQ0MwODFCNTFBMzU4QjgwRjM5MDc4OUVFODcwQzg3MTd'
                 'EMTMwRUFDMTQ5QjZENEVBODYxQUUxRDUyNUE4NjhCRDA4NDdEMjI2MkQ5OUU2ODM5Rjk5RDE1',
        'client_type': 'net',
        'sensorsdata2015jssdkcross': '%7B%22distinct_id%22%3A%22_dirirC7SsDbNrx7VrVyfcM'
                                     '-irynK9R-14r0f7sA%22%2C%22first_id%22%3A%2218e7fd8'
                                     'cd09dee-053d1a5663075fc-367b7031-1049088-18e7fd8cd0'
                                     'aee5%22%2C%22props%22%3A%7B%22%24latest_traffic_sou'
                                     'rce_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8'
                                     'F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%'
                                     'E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%9'
                                     '3%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%'
                                     '2C%22identities%22%3A%22eyIkaWRlbnRpdHlfbG9naW5faWQiOi'
                                     'JfZGlyaXJDN1NzRGJOcng3VnJWeWZjTS1pcnluSzlSLTE0cjBmN3N'
                                     'BIiwiJGlkZW50aXR5X2Nvb2tpZV9pZCI6IjE4ZTdmZDhjZDA5ZGVlL'
                                     'TA1M2QxYTU2NjMwNzVmYy0zNjdiNzAzMS0xMDQ5MDg4LTE4ZTdmZDh'
                                     'jZDBhZWU1In0%3D%22%2C%22history_login_id%22%3A%7B%22na'
                                     'me%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22'
                                     '_dirirC7SsDbNrx7VrVyfcM-irynK9R-14r0f7sA%22%7D%2C%22%2'
                                     '4device_id%22%3A%2218e7fd8cd09dee-053d1a5663075fc-367b'
                                     '7031-1049088-18e7fd8cd0aee5%22%7D',
        'producte_run_to_dev_tomcat': '',
        'JSESSIONID': 'ACE2CEDAC2C5AD7368BD62E3A3A021F7',
    }

    # заголовки для запроса
    headers = {
        'authority': 'www.szwego.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru,en;q=0.9',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://www.szwego.com',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "YaBrowser";v="24.1", "Yowser";v="2.5"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                      ' (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36',
        'wego-albumid': '',
        'wego-channel': 'net',
        'wego-staging': '0',
        'wego-uuid': '',
        'wego-version': '',
    }

    # фильтры запроса
    json_data = {
        'targetAlbumId': shop,
        'queryType': '7',
        'sortType': 2,
        'size': 20,
        'itemIdList': [],
        'minSize': 4,
        'transLang': 'en',
    }

    '''Выполняем запрос к серверу'''
    response = requests.post(
        'https://www.szwego.com/album/api/v3/decorate/getItemsCompInfo',
        cookies=cookies,
        headers=headers,
        json=json_data,
    ).json()

    try:
        response = response['result']
        return response
    except Exception as e:
        print(e)
        return None


def send_item(item, user_id, shop_id):
    # базовая ссылка API telegram
    base_url = f'https://api.telegram.org/bot{conf.BOT_TOKEN}/'

    # создаем список для картинок
    imgs = []
    try:
        dis = ts.translate_text(item['dis'], to_language='ru')
    except Exception as e:
        print(e)
        dis = item['dis']
    shop_number = get_shop_number(shop_id)
    print('--> ', shop_number)
    if type(shop_number) is str:
        dis += '\n\nid магазина:' + shop_number

    else:
        requests.post(f'{base_url}sendPhoto?chat_id={user_id}',
                      data={'caption': '👇👇👇id магазина:', 'photo': shop_number[0]})
    # Добавляем картинки в сообщение
    dis_send = 0
    for n, img in enumerate(item['imgs'][:8]):
        img = {
            'type': 'photo',
            'media': img
        }
        if n == 0:
            if len(dis) < 1024:
                # Прикрепляем текст к первой картинке
                img['caption'] = dis
            else:
                dis_send = 1

        imgs.append(img)

    if dis_send > 0:
        requests.post(f'{base_url}sendMessage?chat_id={user_id}',
                      data={'text': '👇👇👇Описание товара:\n' + dis[:3800]})
    # Отправляем медиа группу
    r = requests.post(base_url + f'sendMediaGroup?chat_id={user_id}',
                      data={
                        'chat_id': user_id,
                        'media': json.dumps(imgs, ensure_ascii=False)
                      }).json()

    if r['ok'] is True:
        time.sleep(4)
    elif r['ok'] is False:
        print(r)
        if r['error_code'] == 429:
            seconds = r['parameters']['retry_after']
            print(f'жду {seconds}')
            time.sleep(seconds)


def pars_shop(shop: str):
    """Находит новые товары в магазине"""
    response = check_shop(shop)

    # создаем список для выходных данных
    out = []

    # получаем уже известные товары
    data = read_file()
    shop_items = data[shop]

    ex_goods = []
    for item in shop_items:
        ex_goods.append(item['item_id'])

    "Проходимся по полученным товарам"
    for item in response:
        "Проверяем новый ли это товар"
        if item['goods_id'] not in ex_goods:

            "Если да, добавляем картинки и описание"
            goods = {
                'imgs': item['imgs'],
                'dis': item['title'],
                'item_id': item['goods_id'],
                'date': datetime.now().strftime('%Y %m %d %H')
            }
            shop_items.append(goods)
            out.append(goods)

    "Сохраняем новые товары"
    data[shop] = shop_items
    write_file(data)
    print('Обновлено!')


def send_shops(user_id: str, order: str, shop: str = 'all'):

    base_url = f'https://api.telegram.org/bot{conf.BOT_TOKEN}/'

    if shop == 'all':
        shops = list(read_file())
    else:
        shops = [shop]

    # получаем магазины из списка
    data = read_file()

    """Проходимся по магазинам"""
    for shop in shops:

        # отправляем сообщение с id магазина

        """проходимся по товарам"""
        for n, item in enumerate(data[shop]):
            if order == '24':
                now = datetime.now()
                seconds_in_day = 24 * 60 * 60
                date = datetime.strptime(item['date'], '%Y %m %d %H')
                difference = now - date
                seconds = (difference.days * seconds_in_day + difference.seconds)
                if seconds <= 86400:
                    print(n, shop)
                    send_item(item, user_id, shop)
            else:
                if order == item['date'][:-3]:
                    print(n, shop)
                    send_item(item, user_id, shop)

    requests.post(f'{base_url}sendMessage?chat_id={user_id}',
                  data={'text': 'На этом все!'})