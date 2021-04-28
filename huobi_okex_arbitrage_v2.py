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
okex_trade_amount = 1

'''Huobi info'''
# alaric001_arbitrage
Huobi_Access_key = '5310e140-ebecefe7-bg5t6ygr6y-99e40'
Huobi_Secret_key = 'cfddd838-7624facf-6360949f-90d96'

is_proxies_Huobi = False

# order settings
Huobi_contract_code = 'BTC-USDT'
Huobi_lever_rate = 10
Huobi_order_price_type='optimal_20'
huobi_trade_amount = 10

# contract info
Huobi_contract_decimal = 1

'''Params for Bollinger'''
ma_period = 140  # 上限不超过140

std_layer1 = 1.5
std_layer2 = 2
std_layer3 = 3
std_layer4 = 4
std_layer5 = 8



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

        '''火币 params'''
        self.huobi_price = None # 实时价格

        # huobi account info
        self.huobi_margin_balance = 0  # 账户权益
        self.huobi_margin_available = 0  # 可用保证金
        self.huobi_margin_frozen = 0  # 冻结保证金
        self.huobi_liquidation_price = 0  # 预估强平价格
        self.huobi_lever_rate = 0  # 杠杆倍数
        # huobi position info
        # buy position
        self.huobi_buy_volume = 0  # 当前多头总仓位
        self.huobi_buy_volume_available = 0  # 当前多头可用仓位
        self.huobi_buy_volume_frozen = 0  # 当前多头冻结仓位
        self.huobi_buy_cost_open = 0  # 多头开仓均价
        self.huobi_buy_position_margin = 0  # 多头持仓保证金
        # sell position
        self.huobi_sell_volume = 0  # 当前空头总仓位
        self.huobi_sell_volume_available = 0  # 当前空头可用仓位
        self.huobi_sell_volume_frozen = 0  # 当前空头冻结仓位
        self.huobi_sell_cost_open = 0  # 空头开仓均价
        self.huobi_sell_position_margin = 0  # 空头持仓保证金

        '''okex params'''
        self.okex_price = None

        # position infomation
        # buy positions
        self.okex_buy_volume = 0 # 当前多头总仓位
        self.okex_buy_available = 0 # 当前可平多头仓位
        self.okex_buy_cost_open = 0 # 多头开仓均价
        self.okex_buy_position_margin = 0 # 多头持仓保证金
        # sell positions
        self.okex_sell_volume = 0 # 当前空仓总仓位
        self.okex_sell_available = 0 # 当前可平空头仓位
        self.okex_sell_cost_open = 0 # 空头开仓均价
        self.okex_sell_position_margin = 0 # 空头持仓保证金

        '''arbitrage params'''
        self.price_diff = None # huobi_price - okex_price  只有在初始化的时候diff会等于None
        self.layer = {}

    def arbitrage_start(self):
        while True:
            # 初始化huobi和okex的价格
            self.huobi_price = None
            self.okex_price = None
            # 获取火币的最新成交价格
            huobi_price_thread = threading.Thread(target=self.get_huobi_price)
            huobi_price_thread.start()
            while huobi_price_thread.is_alive() is True:
                time.sleep(0.2)
            # 获取Okex的最新成交价格
            okex_price_thread = threading.Thread(target=self.get_okex_price)
            okex_price_thread.start()
            while okex_price_thread.is_alive() is True:
                time.sleep(0.2)
            # 如果火币或者okex的价格为None，则说明有价格信息没有拿到，则不进行价差判断
            if self.huobi_price == None or self.okex_price == None:
                # 如果火币的价格是None，则通过钉钉提醒没有拿到火币的价格
                if self.huobi_price == None:
                    message = 'Cannot get Huobi Price'
                    # self.dingding_notice(message)
                # 如果Okex的价格是None，则通过钉钉提醒没有拿到Okex的价格
                if self.okex_price == None:
                    message = 'Cannont get Okex Price'
                    # self.dingding_notice(message)
            # 如果火币和okex的价格都不为None，则表明拿到了两个交易所的价格，可计算并更新差价
            else:
                self.price_diff = round((self.huobi_price - self.okex_price),2)


            # 通过线程拿到历史差价的布林带数据
            get_diff_list_thread = threading.Thread(target= self.get_diff_list)
            get_diff_list_thread.start()
            while get_diff_list_thread.is_alive() is True:
                time.sleep(0.2)

            print(f'''Huobi Price is {self.huobi_price}, Okex price is {self.okex_price}, Price diff is {self.price_diff}
                    layer1 下限为{self.layer['layer1'][0]}，layer1 上限为{self.layer['layer1'][1]}
                    layer5 下限为{self.layer['layer5'][0]}，layer5 上限为{self.layer['layer5'][1]}
                    time: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
                    ''')

            # 通过线程获取huobi的仓位信息
            check_huobi_position_thread = threading.Thread(target=self.get_huobi_account_position_info)
            check_huobi_position_thread.run()
            while check_huobi_position_thread.is_alive() is True:
                time.sleep(0.2)
            # 通过线程获取okex的仓位信息
            check_okex_position_thread = threading.Thread(target=self.get_okex_account_position_info)
            check_okex_position_thread.start()
            while check_okex_position_thread.is_alive() is True:
                time.sleep(0.2)

            # 交易逻辑 【self.price_diff 的值是火币的价格减去okex的价格】
            # 如果diff 大于ma+5*std 则火币价格大于okex价格超过阈值，则应该火币做空，okex做多
            if self.price_diff >= self.layer['layer5'][1]:
                # 火币交易所此时应该持有做空的单
                # 此时多单应该为0，如果不为0，则平掉多单
                if self.huobi_buy_volume > 0:
                    close_long_order = self.huobi_swap_client.create_order(contract_code=Huobi_contract_code,
                                                                           volume=int(self.huobi_buy_volume),
                                                                           direction='sell',
                                                                           offset='close',
                                                                           lever_rate=Huobi_lever_rate,
                                                                           order_price_type=Huobi_order_price_type)
                    message = f'''
                                火币价格高于okex价格大于阈值，此时应该火币做空，okex做多：
                                当前diff值为： {self.price_diff},当前的阈值为： {self.layer['layer5'][1]};
                                当前火币多头仓位应该为0，此时多头仓位为： {self.huobi_buy_volume};
                                下单平掉多头仓位，下单结果为{close_long_order}
                                '''
                    print(message)
                    self.dingding_notice(message)
                else:
                    pass

                # 此时的空单应该为huobi trade amount，多则平，少则加，相等则pass
                if self.huobi_sell_volume > int(huobi_trade_amount):
                    close_sell_order = self.huobi_swap_client.create_order(contract_code=Huobi_contract_code,
                                                                           volume=self.huobi_sell_volume - int(huobi_trade_amount),
                                                                           direction='buy',
                                                                           offset='close',
                                                                           lever_rate=Huobi_lever_rate,
                                                                           order_price_type=Huobi_order_price_type)
                    message = f'''
                                火币价格高于okex价格大于阈值，此时应该火币做空，okex做多：
                                当前diff值为： {self.price_diff},当前的阈值为： {self.layer['layer5'][1]};
                                当前火币空头仓位应该为{int(huobi_trade_amount)}，此时空头仓位为： {self.huobi_sell_volume};
                                下单平掉过多的空头仓位，下单结果为{close_sell_order}
                                '''
                    print(message)
                    self.dingding_notice(message)
                elif self.huobi_sell_volume < int(huobi_trade_amount):
                    open_sell_order = self.huobi_swap_client.create_order(contract_code=Huobi_contract_code,
                                                                          volume=int(huobi_trade_amount)-self.huobi_sell_volume,
                                                                          direction='sell',
                                                                          offset='open',
                                                                          lever_rate=Huobi_lever_rate,
                                                                          order_price_type=Huobi_order_price_type)
                    message = f'''
                                火币价格高于okex价格大于阈值，此时应该火币做空，okex做多：
                                当前diff值为： {self.price_diff},当前的阈值为： {self.layer['layer5'][1]};
                                当前火币空头仓位应该为{int(huobi_trade_amount)}，此时空头仓位为： {self.huobi_sell_volume};
                                下单增加不够的空头仓位，下单结果为{open_sell_order}
                                '''
                    print(message)
                    self.dingding_notice(message)
                else:
                    pass

                # okex 交易所应该持有多单
                # 此时空单应该为0，如果不为0，则平掉
                if self.okex_sell_volume > 0:
                    close_sell_order = self.okex_swap_client.create_order(instrument_id=Okex_instrument_id,
                                                                          type='4',
                                                                          size=str(self.okex_sell_volume),
                                                                          order_type='4')
                    message = f'''
                                火币价格高于okex价格大于阈值，此时应该火币做空，okex做多：
                                当前diff值为： {self.price_diff},当前的阈值为： {self.layer['layer5'][1]};
                                当前okex空头仓位应该为0，此时空头仓位为： {self.okex_sell_volume};
                                下单平掉空头仓位，下单结果为{close_sell_order}
                                '''
                    print(message)
                    self.dingding_notice(message)
                else:
                    pass
                # 此时的多单应该为okex_trade_amount, 多则平，少则加， 相等则pass
                if self.okex_buy_volume > int(okex_trade_amount):
                    close_buy_order = self.okex_swap_client.create_order(instrument_id=Okex_instrument_id,
                                                                         type='3',
                                                                         size=str(self.okex_buy_volume-int(okex_trade_amount)),
                                                                         order_type='4')
                    message = f'''
                                火币价格高于okex价格大于阈值，此时应该火币做空，okex做多：
                                当前diff值为： {self.price_diff},当前的阈值为： {self.layer['layer5'][1]};
                                当前okex多头仓位应该为{int(okex_trade_amount)}，此时多头仓位为： {self.okex_buy_volume};
                                下单平掉过多的空头仓位，下单结果为{close_buy_order}
                                '''
                    print(message)
                    self.dingding_notice(message)

                elif int(okex_trade_amount) > self.okex_buy_volume:
                    open_buy_order = self.okex_swap_client.create_order(instrument_id=Okex_instrument_id,
                                                                        type='1',
                                                                        size=str(int(okex_trade_amount)-self.okex_buy_volume),
                                                                        order_type='4')
                    message = f'''
                                火币价格高于okex价格大于阈值，此时应该火币做空，okex做多：
                                当前diff值为： {self.price_diff},当前的阈值为： {self.layer['layer5'][1]};
                                当前okex多头仓位应该为{int(okex_trade_amount)}，此时多头仓位为： {self.okex_buy_volume};
                                下单增加不够的空头仓位，下单结果为{open_buy_order}
                                '''
                    print(message)
                    self.dingding_notice(message)
                else:
                    pass

            # 如果diff 小于ma+5*std 则火币价格小于okex价格超过阈值，则应该火币做多，okex做空
            elif self.price_diff <= self.layer['layer5'][0]:
                # 火币此时应该持有做多的单
                # 此时空单应该为0，如果不为0，则平掉多单
                if self.huobi_sell_volume > 0:
                    close_sell_order = self.huobi_swap_client.create_order(contract_code=Huobi_contract_code,
                                                                           volume=int(self.huobi_sell_volume),
                                                                           direction='buy',
                                                                           offset='close',
                                                                           lever_rate=Huobi_lever_rate,
                                                                           order_price_type=Huobi_order_price_type)
                    message = f'''
                                火币价格低于okex价格小于阈值，此时应该火币做多，okex做空;
                                当前diff值为： {self.price_diff},当前的阈值为： {self.layer['layer5'][0]};
                                当前火币做空仓位应该为0，此时空头仓位为{self.huobi_sell_volume};
                                下单平掉空头仓位，下单加过为{close_sell_order}
                                '''
                    print(message)
                    self.dingding_notice(message)
                else:
                    pass

                # 此时的多单应该为huobi trade amount, 多则平，少则加，相等则pass
                if self.huobi_buy_volume > int(huobi_trade_amount):
                    close_buy_order = self.huobi_swap_client.create_order(contract_code=Huobi_contract_code,
                                                                          volume=self.huobi_buy_volume - int(huobi_trade_amount),
                                                                          direction='sell',
                                                                          offset='close',
                                                                          lever_rate=Huobi_lever_rate,
                                                                          order_price_type=Huobi_order_price_type)
                    message = f'''
                                火币价格低于okex价格小于阈值，此时应该火币做多，okex做空;
                                当前diff值为： {self.price_diff},当前的阈值为： {self.layer['layer5'][0]};
                                当前火币多头仓位应该为{int(huobi_trade_amount)}，此时多头仓位为： {self.huobi_buy_volume};
                                下单平掉过多的多头仓位，下单结果为{close_buy_order}
                                '''
                    print(message)
                    self.dingding_notice(message)

                elif self.huobi_buy_volume < int(huobi_trade_amount):
                    open_buy_order = self.huobi_swap_client.create_order(contract_code=Huobi_contract_code,
                                                                         volume=int(huobi_trade_amount)-self.huobi_buy_volume,
                                                                         direction='buy',
                                                                         offset='open',
                                                                         lever_rate=Huobi_lever_rate,
                                                                         order_price_type=Huobi_order_price_type)
                    message = f'''
                                火币价格低于okex价格小于阈值，此时应该火币做多，okex做空;
                                当前diff值为： {self.price_diff},当前的阈值为： {self.layer['layer5'][0]};
                                当前火币多头仓位应该为{int(huobi_trade_amount)}，此时多头仓位为： {self.huobi_buy_volume};
                                下单增加不够的多头仓位，下单结果为{open_buy_order}
                                '''
                    print(message)
                    self.dingding_notice(message)
                else:
                    pass

                # okex 交易所应该持有空单
                # 此时多单为0，如果不为0，则平掉
                if self.okex_buy_volume > 0:
                    close_buy_order =  self.okex_swap_client.create_order(instrument_id=Okex_instrument_id,
                                                                          type='3',
                                                                          size=str(self.okex_buy_volume),
                                                                          order_type='4')
                    message = f'''
                                火币价格低于okex价格小于阈值，此时应该火币做多，okex做空;
                                当前diff值为： {self.price_diff},当前的阈值为： {self.layer['layer5'][0]};
                                当前okex多头仓位应该为0，此时空头仓位为： {self.okex_buy_volume};
                                下单平掉多头仓位，下单结果为{close_buy_order}
                                '''
                    print(message)
                    self.dingding_notice(message)

                else:
                    pass
                # 此时的空单应该为okex_trade_amount, 多则平，少则加，相等则pass
                if self.okex_sell_volume > int(okex_trade_amount):
                    close_sell_order = self.okex_swap_client.create_order(instrument_id=Okex_instrument_id,
                                                                          type='4',
                                                                          size=str(self.okex_sell_volume - int(okex_trade_amount)),
                                                                          order_type='4')
                    message = f'''
                                火币价格低于okex价格小于阈值，此时应该火币做多，okex做空;
                                当前diff值为： {self.price_diff},当前的阈值为： {self.layer['layer5'][0]};
                                当前okex空头仓位应该为{int(okex_trade_amount)}，此时空头仓位为： {self.okex_sell_volume};
                                下单平掉过多的空头仓位，下单结果为{close_sell_order}
                                '''
                    print(message)
                    self.dingding_notice(message)

                elif int(okex_trade_amount) > self.okex_sell_volume:
                    open_sell_order = self.okex_swap_client.create_order(instrument_id=Okex_instrument_id,
                                                                         type='2',
                                                                         size=str(int(okex_trade_amount) - self.okex_sell_volume),
                                                                         order_type='4')
                    message = f'''
                                火币价格低于okex价格小于阈值，此时应该火币做多，okex做空;
                                当前diff值为： {self.price_diff},当前的阈值为： {self.layer['layer5'][0]};
                                当前okex空头仓位应该为{int(okex_trade_amount)}，此时空头仓位为： {self.okex_sell_volume};
                                下单增加不够的空头仓位，下单结果为{open_sell_order}
                                '''
                    print(message)
                    self.dingding_notice(message)
                else:
                    pass

            # 如果diff 处于ma +- 1*std 则此时火币和okex的仓位都为空仓
            elif self.price_diff >= self.layer['layer1'][0] and self.price_diff <= self.layer['layer1'][1]:
                message = '此时火币和okex处于ma+-1*std，此时火币和okex都应该为空仓'
                # 此时火币交易所应该是空仓
                if self.huobi_buy_volume > 0:
                    close_buy_order = self.huobi_swap_client.create_order(contract_code=Huobi_contract_code,
                                                                          volume=self.huobi_buy_volume,
                                                                          direction='sell',
                                                                          offset='close',
                                                                          lever_rate=Huobi_lever_rate,
                                                                          order_price_type=Huobi_order_price_type)
                    message = f'''
                                此时火币与okex的差价在处于布林带的上下限之间，此时火币和okex都应该空仓;
                                当前diff值为:{self.price_diff},当前布林带的上限为：{self.layer['layer1'][1]}，当前布林带的下限为：{self.layer['layer1'][0]};
                                当前火币的多头仓位为{self.huobi_buy_volume},当前火币的空头仓位为{self.huobi_sell_volume};
                                平掉火币多单，平单结果为{close_buy_order}
                                '''
                    print(message)
                    self.dingding_notice(message)
                else:
                    pass

                if self.huobi_sell_volume > 0:
                    close_sell_order = self.huobi_swap_client.create_order(contract_code=Huobi_contract_code,
                                                                           volume=self.huobi_sell_volume,
                                                                           direction='buy',
                                                                           offset='close',
                                                                           lever_rate=Huobi_lever_rate,
                                                                           order_price_type=Huobi_order_price_type)
                    message = f'''
                                此时火币与okex的差价在处于布林带的上下限之间，此时火币和okex都应该空仓;
                                当前diff值为:{self.price_diff},当前布林带的上限为：{self.layer['layer1'][1]}，当前布林带的下限为：{self.layer['layer1'][0]};
                                当前火币的多头仓位为{self.huobi_buy_volume},当前火币的空头仓位为{self.huobi_sell_volume};
                                平掉火币空单，平单结果为{close_sell_order}
                                '''
                    print(message)
                    self.dingding_notice(message)
                else:
                    pass

                # 此时okex交易所应该是空仓
                if self.okex_buy_volume > 0:
                    close_buy_order = self.okex_swap_client.create_order(instrument_id=Okex_instrument_id,
                                                                         type='3',
                                                                         size=str(self.okex_buy_volume),
                                                                         order_type='4')
                    message = f'''
                                此时火币与okex的差价在处于布林带的上下限之间，此时火币和okex都应该空仓;
                                当前diff值为:{self.price_diff},当前布林带的上限为：{self.layer['layer1'][1]}，当前布林带的下限为：{self.layer['layer1'][0]};
                                当前okex的多头仓位为{self.okex_buy_volume},当前okex的空头仓位为{self.okex_sell_volume};
                                平掉okex多单，平单结果为{close_buy_order}
                                '''
                    print(message)
                    self.dingding_notice(message)
                else:
                    pass

                if self.okex_sell_volume > 0:
                    close_sell_order = self.okex_swap_client.create_order(instrument_id=Okex_instrument_id,
                                                                          type='4',
                                                                          size=str(self.okex_sell_volume),
                                                                          order_type='4')
                    message = f'''
                                此时火币与okex的差价在处于布林带的上下限之间，此时火币和okex都应该空仓;
                                当前diff值为:{self.price_diff},当前布林带的上限为：{self.layer['layer1'][1]}，当前布林带的下限为：{self.layer['layer1'][0]};
                                当前okex的多头仓位为{self.okex_buy_volume},当前okex的空头仓位为{self.okex_sell_volume};
                                平掉okex空单，平单结果为{close_sell_order}
                                '''
                    print(message)
                    self.dingding_notice(message)
            time.sleep(1)

    def get_diff_list(self):
        huobi_list = self.get_huobi_klines()
        okex_list = self.get_okex_klines()
        diff_list = list(map(lambda x: x[0]-x[1], zip(huobi_list,okex_list)))
        diff_ma = np.mean(diff_list)
        diff_std = np.std(diff_list)
        # print(f'''DIFF: MA is {diff_ma}, STD is {diff_std}''')
        self.layer = {}
        self.layer['Diff_ma'] = round(diff_ma,2)
        self.layer['Diff_std'] = round(diff_std,2)
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

    '''账户信息类函数'''

    def get_huobi_account_position_info(self):

        huobi_position = self.huobi_swap_client.get_swap_account_position_info(contract_code=Huobi_contract_code)
        # print(huobi_position)

        # huobi account info
        self.huobi_margin_balance = 0  # 账户权益
        self.huobi_margin_available = 0  # 可用保证金
        self.huobi_margin_frozen = 0  # 冻结保证金
        self.huobi_liquidation_price = 0  # 预估强平价格
        self.huobi_lever_rate = 0  # 杠杆倍数
        # huobi position info
        # buy position
        self.huobi_buy_volume = 0  # 当前多头总仓位
        self.huobi_buy_volume_available = 0  # 当前多头可用仓位
        self.huobi_buy_volume_frozen = 0  # 当前多头冻结仓位
        self.huobi_buy_cost_open = 0  # 多头开仓均价
        self.huobi_buy_position_margin = 0  # 多头持仓保证金
        # sell position
        self.huobi_sell_volume = 0  # 当前空头总仓位
        self.huobi_sell_volume_available = 0  # 当前空头可用仓位
        self.huobi_sell_volume_frozen = 0  # 当前空头冻结仓位
        self.huobi_sell_cost_open = 0  # 空头开仓均价
        self.huobi_sell_position_margin = 0  # 空头持仓保证金

        if huobi_position['status'] == 'ok':
            if len(huobi_position['data']) > 0:
                self.huobi_margin_balance = huobi_position['data'][0]['margin_balance']  # 账户权益
                self.huobi_margin_available = huobi_position['data'][0]['margin_available']  # 可用保证金
                self.huobi_margin_frozen = huobi_position['data'][0]['margin_frozen']  # 冻结保证金
                self.huobi_liquidation_price = huobi_position['data'][0]['liquidation_price']  # 预估强平价格
                self.huobi_lever_rate = huobi_position['data'][0]['lever_rate']  # 杠杆倍数
                message = 'Huobi Account info: \n' \
                          'margin balance is %s, margin available is %s, margin frozen is %s, liquidation price is ' \
                          '%s, lever rate is %s.\n Current time: %s.\n' \
                          % (self.huobi_margin_balance,
                             self.huobi_margin_available,
                             self.huobi_margin_frozen,
                             self.huobi_liquidation_price,
                             self.huobi_lever_rate,
                             time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
                # print(message)
                if huobi_position['data'][0]['positions'] != None:
                    for i in huobi_position['data'][0]['positions']:
                        if i['direction'] == 'buy':
                            self.huobi_buy_volume = int(i['volume'])  # 当前多头总仓位
                            self.huobi_buy_volume_available = i['available']  # 当前多头可用仓位
                            self.huobi_buy_volume_frozen = i['frozen']  # 当前多头冻结仓位
                            self.huobi_buy_cost_open = i['cost_open']  # 多头开仓均价
                            self.huobi_buy_position_margin = i['position_margin']  # 多头持仓保证金
                        if i['direction'] == 'sell':
                            self.huobi_sell_volume = int(i['volume'])  # 当前空头总仓位
                            self.huobi_sell_volume_available = i['available']  # 当前空头可用仓位
                            self.huobi_sell_volume_frozen = i['frozen']  # 当前空头冻结仓位
                            self.huobi_sell_cost_open = i['cost_open']  # 空头开仓均价
                            self.huobi_sell_position_margin = i['position_margin']  # 空头持仓保证金

                    message = 'Huobi Buy position: \n' \
                              'buy volume is %s, buy volume available is %s, buy volume frozen is: %s, \n' \
                              'buy cost open is %s, buy position margin is %s. \n \n' \
                              'Huobi Sell position: \n' \
                              'sell volume is %s, sell volume available is %s, sell volume frozen is: %s, \n' \
                              'sell cost open is %s, sell position margin is %s.\n' \
                              'Current time: %s.' \
                              % (self.huobi_buy_volume,
                                 self.huobi_buy_volume_available,
                                 self.huobi_buy_volume_frozen,
                                 self.huobi_buy_cost_open,
                                 self.huobi_buy_position_margin,
                                 self.huobi_sell_volume,
                                 self.huobi_sell_volume_available,
                                 self.huobi_sell_volume_frozen,
                                 self.huobi_sell_cost_open,
                                 self.huobi_sell_position_margin,
                                 time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                                 )
                    # print(message)
                else:
                    message = 'No position info'
                    # print(message)
                    # logger.info(message)
            else:
                message = 'Cannot get current account and position infomation. (situation 2)'
                print(message)
                # logger.info(message)
        else:
            message = 'Cannot get current account and position infomation. (situation 1)'
            print(message)
            # logger.info(message)

    def get_okex_account_position_info(self):

        okex_position = self.okex_swap_client.get_position(instrument_id=Okex_instrument_id)

        # position infomation
        # buy positions
        self.okex_buy_volume = 0 # 当前多头总仓位
        self.okex_buy_available = 0 # 当前可平多头仓位
        self.okex_buy_cost_open = 0 # 多头开仓均价
        self.okex_buy_position_margin = 0 # 多头持仓保证金
        # sell positions
        self.okex_sell_volume = 0 # 当前空仓总仓位
        self.okex_sell_available = 0 # 当前可平空头仓位
        self.okex_sell_cost_open = 0 # 空头开仓均价
        self.okex_sell_position_margin = 0 # 空头持仓保证金

        if len(okex_position['holding']) > 0:
            for i in okex_position['holding']:
                if i['side'] == 'long':
                    self.okex_buy_volume = int(i['position']) # 当前多头总仓位
                    self.okex_buy_available = int(i['avail_position']) # 当前可平多头仓位
                    self.okex_buy_cost_open = float(i['avg_cost']) # 多头开仓均价
                    self.okex_buy_position_margin = float(i['margin']) # 多头持仓保证金


                elif i['side'] == 'short':
                    self.okex_sell_volume = int(i['position']) # 当前空仓总仓位
                    self.okex_sell_available = int(i['avail_position']) # 当前可平空头仓位
                    self.okex_sell_cost_open = float(i['avg_cost']) # 空头开仓均价
                    self.okex_sell_position_margin = float(i['margin']) # 空头持仓保证金

            message = f'''
                        Huobi Buy position: \n
                        buy volume is {self.okex_buy_volume}, buy volume available is {self.okex_buy_available}\n
                        buy cost open is {self.okex_buy_cost_open}, buy position margin is {self.okex_buy_position_margin}. \n
                        Huobi Sell position: \n
                        sell volume is {self.okex_sell_volume}, sell volume available is {self.okex_sell_available}\n
                        sell cost open is {self.okex_sell_cost_open}, sell position margin is {self.okex_sell_position_margin}.\n
                        Current time: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
                        '''
            # print(message)
        else:
            message = 'Cannot get current account info'
            print(message)

    '''行情类函数'''

    def get_huobi_price(self):
        self.huobi_price = float(self.huobi_swap_client.get_market_trade(contract_code=Huobi_contract_code)['tick']['data'][0]['price'])
        # print(self.huobi_price)

    def get_okex_price(self):
        self.okex_price = float(self.okex_swap_client.get_ticker(instrument_id=Okex_instrument_id)['last'])
        # print(self.okex_price)

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

    '''工具类函数'''

    def ding_thread(self, out):
        self.xiaoding.send_text(out, is_at_all=False)

    def dingding_notice(self, message=None):
        self.get_huobi_account_position_info()
        time.sleep(0.2)
        self.get_okex_account_position_info()
        time.sleep(0.2)
        self.get_diff_list()
        time.sleep(0.2)
        basic_info = '\n--------------------------------\n' \
                    'Strategy name: %s, Strategy account: %s ;\n' \
                    '套利信息：' \
                     'diff: %s, layer1 low: %s, layer1 high: %s, layer5 low: %s. layer5 high: %s'\
                    '火币：\n' \
                    'Contract code: %s \n'\
                    'Long position: %s; Short position: %s \n'\
                    'OKex：\n' \
                    'Contract code: %s \n' \
                    'Long position: %s; Short position: %s \n' \
                    'Local time: %s \n ' \
                    '--------------------------------\n' \
                    % (self.strategy_name, self.strategy_account,
                       self.price_diff,self.layer['layer1'][0],self.layer['layer1'][1],self.layer['layer5'][0],self.layer['layer5'][1],
                       Huobi_contract_code,
                       self.huobi_buy_volume,self.huobi_sell_volume,
                       Okex_instrument_id,
                       self.okex_buy_volume,self.okex_sell_volume,
                       time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        out = message + basic_info
        t = threading.Thread(target=self.ding_thread, args=(out,),)
        t.start()

test = arbitrage_strategy()
test.arbitrage_start()
# test.dingding_notice('test')
# test.get_okex_account_position_info()
# test.get_huobi_account_position_info()


# test.get_current_price_diff()

# test.get_huobi_klines()
# test.get_okex_klines()
# test.get_diff_list()