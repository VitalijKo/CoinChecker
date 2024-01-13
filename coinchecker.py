import pandas as pd
import requests
import threading
import sched
import os
import json
import time
from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import PictureMessage
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest
from matplotlib import pyplot as plt
from datetime import datetime

bot_dir = '/var/www/SberbankCoinsMonitorBot/'

headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ru-RU,ru;q=0.9',
    'cache-control': 'no-cache',
    'cookie': 'f5avraaaaaaaaaaaaaaaa_session_=HDPECFLANGIGCGMNOPLLABKKOPDGOILFONHKHOPGJFBKBFFGEHKOBFMBELMAJMAMECIDMLLE'
              'OJOFLCAAKKJAJDELNAEDOEPGODJMKAHKIHANDNPHJGONOBDACKOHGJCH; JSESSIONID=OV9u5xI-Ye41KYeuH-mRiAFlnvd7mENFER'
              'G2lLIF.gateway-58c7887975-j8qtv; TS019fab19=013ade2899c8f0a21331e1aea5e441ba784d46076b395b0ecd482eec74c'
              '35ce2be3dcd2467e52810ddd1da9d55e238828f1181019fa164306cd8f9f227fb4372abbb96e569f6e207a4ada060d3de100740'
              '0a05e24284ad9dfe4751788f431b7a87b73a94c2d3802c6610948833ca5f248b65a5a5b04a2a15d77f9c6676bdaf97789c91ded'
              '217263932b3439384d2e3afbcadc72cd83cf8f3b92258a422cba32c69ec3f47533da56adabd385d7a7978049ea695957c; _sv='
              'SA1.86604afd-8d2b-4268-b5e3-ecc9993a1d9d.1657209728; t2_sid_3122244=s1.1995504063.1657191629485.1657191'
              '687455.1.114.114; TS89e18e75077=08fbdc5594ab28007a7d01e34e381262c339fee9f53f802bf51dbdb432d65c929d313b0'
              '79828e0d179de67b37fcdb267081d9dab9717200035989474ed1cf122327d34ced15dab2c30328bc806997d8c08897fd48c06fd'
              'a3; BBTracking="Mw=="; anonymousUserId=62b98a5b-7db3-4567-a6c8-db44c1f3b1a1; fd4d781bd0c8fb3a051334d9d1'
              'fc792d=37b925c1bbe048862deb16d4222e7a1a; TS011f2bf6=013ade28994af6a8f507166e3da0570a254bdd92fc8d8f44e5d'
              '297b42dd46aeb2b821f1f3c07131fa2beac3768fffbb7a691fa582db28fd7418214a12413eaf11de01b03309bc2921b24f6aa85'
              'bc1a1951d118f5cfc1f259f10361a00fa5c27372740828a8b2891336a67b15dec5b10c1ec3363440bf25d14c61b06398aaae6b9'
              '859e60269bef0f287669b605f56fb8a3b02e29f596952ee1103ac475fdbd1daa45d5788b6400767aad0b52a34baa45adec072db'
              'ad15c5535f05242b244069296bc293a2a27e303fb86b7f440ac038be2d2866bb8f414d45612688d63a3e342dfe970c68b455928'
              '54f5baf49f38c8b418cc658e87dbdd672c7222c94ee0713190ae1ca58cece82aff19e561a717f10b46bd39c3d07; TS89e18e75'
              '029=08fbdc5594ab280063400062e753b030c92eb5f2032dfcbd3988c10502c963a63815da509393b2ee752e244401b0d6a3; p'
              'roduct_page=; f5_cspm=; _gcl_au=1.1.712626380.1657191629; TS1583a86a027=08fbdc5594ab2000e1fe4204302aad1'
              '21b26d24e787f719a4ff35d96571d4be8adfc78f19d46d13f08a6b1ee65113000def8b8203506c20a0f3d1b6456d259c8bcf07e'
              'ed1a29edd2f3cc7b8e508e007415ce270fa50e501434a32a4c846d0360; top100_id=t1.3122244.1211694403.16571916294'
              '83; adtech_uid=cd3d3a2b-3633-48e8-9513-8ce43dfd66ed%3Asberbank.ru; _sa=SA1.64967cac-edb5-4fb7-8b25-5fd5'
              '9d358fea.1657191629; ___dmpkit___=7850152f-16cc-462a-bc14-4b25746d0d1a; abc4e19df5455fc72f51575e0d5bd92'
              '8=25a745d83c3801bacb0a7665fb150619; x-session-id=f22e635b-ccda-fe35-45fc-a71cd9416a6e; sbrf.region_id=6'
              '4; sbrf.region_manual=true; 8f7f8c377e0f2a8171e27c3bfec6a87a=9a7783feb3862cc245cc70782847a0a6; cf44ad4b'
              'dad05ee181f953b4c4e5e921=4d2c58a189803767f7c446786b6ebb08; TS00000000076=08fbdc5594ab28007f6f93e98c01e0'
              '8db1e44090e1ece4de86ef79b4c983342a61df43562232b1897313717f98519a53085f57e9e209d0008934ae59c83534bf5bddd'
              '97a977c8d8994361c732282f3f85c7bd59028e70e542fc6b8f220e8e0fd2e329d76dc99567a005fd8a785fba944d3cefe950d1a'
              'e54848be90cdac777002692bd19047b10147dd80a69f91f90b9e814751cf104b39fbf0ca7e7029ed004a9f9f440475513cbbb0d'
              '4b499e519876f8504153dd332bc8d08bc33c51f4fc883159fb7e3ca8b435a5f927a30dce63bbab6c684787ee2b6efbfd912b7e4'
              '5be53e49c506bcf1b1b7d40ae3a6833f57e8d095e3512e4b0f775e65b5b31ecd47492b18165ecaf41b766e; TSPD_101_DID=08'
              'fbdc5594ab28007f6f93e98c01e08db1e44090e1ece4de86ef79b4c983342a61df43562232b1897313717f98519a53085f57e9e'
              '20638006ab90259e95199c34498bb0ab1e0d886f21983790deff3bd5020344e15f2e58649f4b86ecc187816f58a2f1fc216cb82'
              '544af7dbfcae9221; BBXSRF=85d5b470-2a5e-49ff-a63c-49a0d2a88be9; JSESSIONID=3nqgnAue-OdSmbUCgFLrIhEnIjLGD'
              'cO9mWL5Vv0f.portalserver-live-5fb5d47498-qq8mr; TSPD_101=08fbdc5594ab2800059a31835bfc7b6a24a198fab81e92'
              '5a331828a5156c4ce606fca0e157ed70bd37859eb7eef6d4e708e900685605180045c3a3c8fa9f4c639a73bc033e85f060ed8ad'
              'f5971dd1a02; f5avraaaaaaaaaaaaaaaa_session_=MBJFODLBIHMOMOEEPBJNDPDFFCNEBEGOAJGBEFBANMPPBGDGJPABFKDLFNF'
              'ODNFFKGFDACGCNJINCGBKDEPAKGFFNAHLFKHPNCIBGBNKHCJICMALEEPIJLFCHNLKIJBI; sbrf.pers_notice=1; TS89e18e7507'
              '8=08fbdc5594ab2000eeab5ab11de9a6737454137a92cfd37226f8112c724cc6a2f7ec0b4128ebb5f908ede90840185001a48ca'
              '62565aca7e7dcd02c0d6a86124bc34f57451b0933aa07d38453abf61ed49b25c76b3061bd3c84a9553d0a255a3f1b9d32d27695'
              'da453f459806764ffb49ce6b2e815962ffc780455c821f2fccc0e476b359175cb6c06bdfede9f2a0d0b3f2c6f6b017878c650f0'
              '4e9815b8e60d6d00d2a2569ff7876ffe8db00c3bd2a52badf5741919914b50188516821aaf05a485b8aabc7130676324f572602'
              'cd6d76b43e6d28088fa056d855971e17805a583ce3b894326bff59b0862b0ac73c8abf7e759138b02682f492912dddea945daae'
              '886f1d7e6634054570a298a64a6bcc3e841c4fed54c8715dfc13e84fe6c2e8a1807cdb626c598dde399c4e857451a285c1bf2b8'
              '5254d56ec68da5b639b5277e09b1337adfa9147854240d102ed93d833b3df4fd83dae17e9c779f669bf6fb77412fa8b3cdeeae7'
              '3b3af6a532d8d4d5ac94d05420246a1d2b934f4bbcc0deade; redirectPortal=retail',
    'pragma': 'no-cache',
    'referer': 'https://www.sberbank.ru/ru/person/investments/values/mon',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/103.0.5060.66 Safari/537.36'
}

coins_ids = [
    '5216-0060',
    '5215-0036',
    '5216-0080',
    '5217-0041',
    '5217-0038',
    '5216-0089',
    '5217-0040',
    '5216-0081',
    '5216-0095',
    '5216-0001',
    '5216-0055',
]


def get_users_ids():
    with open(bot_dir + 'ids.txt') as ids_file:
        users_ids = ids_file.read().splitlines()

    return users_ids


def write_user_id(user_id):
    with open(bot_dir + 'ids.txt', 'a') as ids_file:
        ids_file.write(user_id + '\n')


def get_coin_info(coin_id):
    global headers

    r = requests.get(f'https://www.sberbank.ru/proxy/services/coin-catalog/coins/{coin_id}?region=54&condition=1',
                     headers=headers)

    return json.loads(r.text)


def available_offices(coin_id):
    global headers

    r = requests.get(
        f'https://www.sberbank.ru/proxy/services/coin-catalog/vsp?ids={coin_id}'
        f'-1&region=54&query=%D0%A1%D0%B0%D1%80%D0%B0%D1%82%D0%BE%D0%B2&page=0&pageSize=5&fullMatch=false',
        headers=headers)

    return json.loads(r.text)


def monitor():
    coins = {'stats': {}}
    average_price = 0
    needed_coins = []

    for coin_id in coins_ids:
        coin_info = get_coin_info(coin_id)
        coin_offices = available_offices(coin_id)

        coins[coin_id] = {
            'name': coin_info['name'],
            'price': coin_info['price'],
            'offices': []
        }

        average_price += coin_info['price']

        for office in coin_offices['entities']:
            if 'Саратов' in office['address']:
                coins[coin_id]['offices'].append(
                    {
                        'address': office['address'],
                        'quantity': office['balance'].split(': ')[1]
                    }
                )

    coins['stats'] = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'average_price': average_price
    }

    if not os.path.exists(bot_dir + 'coins_data.json'):
        with open(bot_dir + 'coins_data.json', 'w', encoding='utf-8') as coins_data_file:
            json.dump([coins], coins_data_file, ensure_ascii=False)

    else:
        with open(bot_dir + 'coins_data.json', 'r', encoding='utf-8') as coins_data_file:
            loaded_coins = json.load(coins_data_file)
            loaded_coins.append(coins)

        with open(bot_dir + 'coins_data.json', 'w', encoding='utf-8') as coins_data_file:
            json.dump(loaded_coins, coins_data_file, ensure_ascii=False)

    for coin in coins:
        if coin != 'stats':
            if len(coins[coin]['offices']) > 0:
                needed_coins.append(coins[coin])

    return needed_coins


def plot():
    with open(bot_dir + 'coins_data.json', 'r', encoding='utf-8') as coins_data_file:
        data = json.load(coins_data_file)

    if os.path.exists(bot_dir + 'static/plot.png'):
        os.remove(bot_dir + 'static/plot.png')

    dates = []
    average_prices = []
    prev_date = ''

    for check in data:
        date = check['stats']['date']
        average_price = check['stats']['average_price']

        if date != prev_date:
            dates.append(date)
            average_prices.append(average_price)

    dates = pd.to_datetime(dates)
    df = pd.DataFrame()
    df['value'] = average_prices
    df = df.set_index(dates)
    plt.plot(df)
    plt.gcf().autofmt_xdate()
    plt.savefig(bot_dir + 'static/plot.png')


def wait(viber, keyboard):
    while True:
        if datetime.now().strftime('%H:%M') == '15:00':
            result = 'Офисов, продающих монеты в Саратове, не обнаружено!'

            try:
                needed_coins = monitor()
            except Exception as e:
                needed_coins = []

                result = f'При проверке произошла ошибка:\n{e}'

            if needed_coins:
                result = f'Обнаружено {len(needed_coins)} офисов, продающих монеты в Саратове! (smiley)\n'

                for coin in needed_coins:
                    result += f'\n{needed_coins.index(coin) + 1}. Название: {coin["name"]}\nЦена: {coin["price"]}\nОфисы:\n'

                    for office in coin['offices']:
                        result += office['address'] + ' - ' + office['quantity'] + ' шт.\n'

            for user_id in get_users_ids():
                try:
                    viber.send_messages(user_id, [
                        TextMessage(text=result, keyboard=keyboard)
                    ])
                except:
                    continue

            plot()

            time.sleep(60)

        time.sleep(30)


app = Flask(__name__)

viber = Api(BotConfiguration(
    name='CoinMonitorBot',
    avatar='https://cdn2.iconfinder.com/data/icons/business-and-finance-1-8/128/5-512.png',
    auth_token=''
))

keyboard = {
    'DefaultHeight': True,
    'BgColor': '#FFFFFF',
    'Type': 'keyboard',
    'Buttons':
        [
            {
                'Columns': 6,
                'Rows': 2,
                'BgColor': '#FFFFFF',
                'BgLoop': True,
                'ActionType': 'reply',
                'ActionBody': 'График',
                'ReplyType': 'message',
                'Text': 'График'
            }
        ]
}


@app.route('/', methods=['POST'])
def incoming():
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberMessageRequest):
        if viber_request.sender.id not in get_users_ids():
            write_user_id(viber_request.sender.id)

        message = viber_request.message.text

        try:
            if message == 'График':
                viber.send_messages(viber_request.sender.id, [
                    PictureMessage(media='https://vib.fvds.ru/static/plot.png', keyboard=keyboard)
                ])

            else:
                viber.send_messages(viber_request.sender.id, [
                    TextMessage(
                        text='Проверка золотых монет выполняется автоматически каждый день в 15:00.\n\nПри нажатии на кнопку "График" будет выведен график средних значений цен монет за каждый день.\n\nЕсли какая-либо монета будет найдена в городе Саратов, вам автоматически придет уведомление',
                        keyboard=keyboard)
                ])
        except:
            pass

    elif isinstance(viber_request, ViberConversationStartedRequest):
        viber.send_messages(viber_request.get_user.id, [
            TextMessage(text='Напишите любое сообщение, чтобы начать')
        ])

    elif isinstance(viber_request, ViberFailedRequest):
        print('Client failed receiving message. failure: {0}'.format(viber_request))

    return Response(status=200)


def set_webhook(viber):
    viber.set_webhook('https://vib.fvds.ru:443/')


if not os.path.exists(bot_dir + 'ids.txt'):
    open(bot_dir + 'ids.txt', 'x').close()

scheduler = sched.scheduler(time.time, time.sleep)
scheduler.enter(5, 1, set_webhook, (viber,))

t1 = threading.Thread(target=scheduler.run)
t1.start()

t2 = threading.Thread(target=wait, args=(viber, keyboard))
t2.start()

context = ('server.crt', 'server.key')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, ssl_context=context)
