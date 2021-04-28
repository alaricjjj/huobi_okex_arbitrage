from huobi_swap_client import Huobi_Swap_Client
from okex_swap_client import Okex_swap_client
from chatrobot import DingtalkChatbot
import numpy as np
import threading, time
import csv

# dingding address info
dingding_address = 'https://oapi.dingtalk.com/robot/send?access_token=140d1e6686588c070a5e4edce39beb5feb74003450bbac8f3c53bfa34e079baa'

'''Okex info'''
Okex_api_key = '24b047df-e66d-4286-8d9d-853dd297d49e'
Okex_seceret_key = 'D970633D207B9FDEBAF9C8CEF59BFE4D'
Okex_passphrase = 'arbitrage'

is_proxies_Okex = True

# order settings
Okex_instrument_id = 'BTC-USDT-SWAP'

'''Huobi info'''
# alaric001_arbitrage
Huobi_Access_key = '5310e140-ebecefe7-bg5t6ygr6y-99e40'
Huobi_Secret_key = 'cfddd838-7624facf-6360949f-90d96'

is_proxies_Huobi = False

# order settings
Huobi_contract_code = 'BTC-USDT'
Huobi_lever_rate = 10
Huobi_order_price_type='optimal_20'

# contract info
Huobi_contract_decimal = 1

'''Params for Bollinger'''
ma_period = 100  # 上限不超过140

std_layer1 = 1.5
std_layer2 = 2
std_layer3 = 3
std_layer4 = 4
std_layer5 = 5



class arbitrage_strategy():

    def __init__(self):
        # strategy info
        self.strategy_account = 'Alaric huobi002 and okex0001'
        self.strategy_name = 'arbitrage_strategy version 1'

        # dingding client
        self.xiaoding = DingtalkChatbot(dingding_address)

        # Huobi swap instance
        self.huobi_swap_client = Huobi_Swap_Client(Access_Key = Huobi_Access_key,
                                                   Secret_Key = Huobi_Secret_key,
                                                   is_proxies = is_proxies_Huobi)

        # Okex swap instance
        self.okex_swap_client = Okex_swap_client(api_key=Okex_api_key,
                                                 api_seceret_key=Okex_seceret_key,
                                                 passphrase=Okex_passphrase,
                                                 is_proxies=is_proxies_Okex)
        self.huobi_price = None
        self.okex_price = None
        self.price_diff = None # huobi_price - okex_price  只有在初始化的时候diff会等于None

        self.layer = {}

    def get_huobi_price(self):
        self.huobi_price = float(self.huobi_swap_client.get_market_trade(contract_code=Huobi_contract_code)['tick']['data'][0]['price'])
        # print(self.huobi_price)

    def get_okex_price(self):
        self.okex_price = float(self.okex_swap_client.get_ticker(instrument_id=Okex_instrument_id)['last'])
        # print(self.okex_price)

    def get_current_price_diff(self):
        # 写入csv
        # headers = ['Time', 'Diff', 'Diff ma','layer_1_up', 'layer_1_down', 'layer_2_up', 'layer_2_down',
        #            'layer_3_up', 'layer_3_down', 'layer_4_up', 'layer_4_down', 'layer_5_up', 'layer_5_down']
        # with open('Arbitrage Data.csv', 'w',newline='')as f:
        #     f_csv = csv.writer(f)
        #     f_csv.writerow(headers)

        while True:
            self.huobi_price = None
            self.okex_price = None

            huobi_price_thread = threading.Thread(target=self.get_huobi_price)
            huobi_price_thread.start()
            while huobi_price_thread.is_alive() is True:
                time.sleep(0.2)

            okex_price_thread = threading.Thread(target=self.get_okex_price)
            okex_price_thread.start()
            while okex_price_thread.is_alive() is True:
                time.sleep(0.2)

            if self.huobi_price == None or self.okex_price == None:
                if self.huobi_price == None:
                    message = 'Cannot get Huobi Price'
                    # self.dingding_notice(message)

                if self.okex_price == None:
                    message = 'Cannont get Okex Price'
                    # self.dingding_notice(message)
            else:
                self.price_diff = round(self.huobi_price - self.okex_price,2)
            print(f'''Huobi Price is {self.huobi_price}, Okex price is {self.okex_price}, Price diff is {self.price_diff}''')

            get_diff_list_thread = threading.Thread(target= self.get_diff_list)
            get_diff_list_thread.start()
            while get_diff_list_thread.is_alive() is True:
                time.sleep(0.2)

            if self.price_diff >= self.layer['layer1'][0] and self.price_diff <= self.layer['layer1'][1]:
                print('True')
            else:
                print('False')

            # row = [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            #        self.price_diff,
            #        self.layer['Diff_ma'],
            #        self.layer['layer1'][0],
            #        self.layer['layer1'][1],
            #        self.layer['layer2'][0],
            #        self.layer['layer2'][1],
            #        self.layer['layer3'][0],
            #        self.layer['layer3'][1],
            #        self.layer['layer4'][0],
            #        self.layer['layer4'][1],
            #        self.layer['layer5'][0],
            #        self.layer['layer5'][1]]
            # with open('Arbitrage Data.csv', 'a', newline='')as f:
            #     f_csv = csv.writer(f)
            #     f_csv.writerow(row)

            time.sleep(1)

    def get_huobi_klines(self):
        huobi_klines = self.huobi_swap_client.get_k_lines(contract_code=Huobi_contract_code,
                                                          period='1min')
        huobi_close_list = []
        for i in range(-1 - ma_period,-1,1):
            huobi_close_list.append(huobi_klines['data'][i]['close'])
        return huobi_close_list

    def get_okex_klines(self):
        okex_klines = self.okex_swap_client.get_k_lines(instrument_id=Okex_instrument_id,
                                                        granularity=60)
        okex_close_list = []
        for i in range(1, 1+ma_period,1):
            okex_close_list.append(float(okex_klines[i][4]))
        okex_close_list.reverse()
        return okex_close_list

    def get_diff_list(self):
        huobi_list = self.get_huobi_klines()
        okex_list = self.get_okex_klines()
        diff_list = list(map(lambda x: x[0]-x[1], zip(huobi_list,okex_list)))
        diff_ma = np.mean(diff_list)
        diff_std = np.std(diff_list)

        # print(f'''DIFF: MA is {diff_ma}, STD is {diff_std}
        #         ''')
        self.layer = {}
        self.layer['Diff_ma'] = round(diff_ma,2)
        layer_1 = [round(diff_ma - diff_std * std_layer1,2), round(diff_ma + diff_std * std_layer1,2)]
        self.layer['layer1'] = layer_1
        layer_2 = [round(diff_ma - diff_std * std_layer2,2), round(diff_ma + diff_std * std_layer2,2)]
        self.layer['layer2'] = layer_2
        layer_3 = [round(diff_ma - diff_std * std_layer3,2), round(diff_ma + diff_std * std_layer3,2)]
        self.layer['layer3'] = layer_3
        layer_4 = [round(diff_ma - diff_std * std_layer4,2), round(diff_ma + diff_std * std_layer4,2)]
        self.layer['layer4'] = layer_4
        layer_5 = [round(diff_ma - diff_std * std_layer5,2), round(diff_ma + diff_std * std_layer5,2)]
        self.layer['layer5'] = layer_5


    def ding_thread(self, out):
        self.xiaoding.send_text(out, is_at_all=False)

    def dingding_notice(self, message=None):
        # self.get_current_account_position_info()
        basic_info = '\n--------------------------------\n' \
                     # 'Strategy name: %s \n' \
                     # 'Contract code: %s \n' \
                     # 'Current long position: %s \n' \
                     # 'Current short position: %s \n' \
                     # 'Local time: %s \n ' \
                     # '--------------------------------\n' \
                     # % (self.strategy_name,
                     #    contract_code,
                     #    self.current_buy_volume,
                     #    self.current_sell_volume,
                     #    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        out = message + basic_info
        t = threading.Thread(target=self.ding_thread, args=(out,),)
        t.start()



test = arbitrage_strategy()
# test.get_huobi_price()
# test.get_okex_price()
test.get_current_price_diff()

# test.get_huobi_klines()
# test.get_okex_klines()
# test.get_diff_list()