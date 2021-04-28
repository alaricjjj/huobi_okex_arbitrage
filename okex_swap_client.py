import utils
from requests import Request
from request_manager import RequestManager
import json
import time

class Okex_swap_client():
    def __init__(self, api_key, api_seceret_key, passphrase, use_server_time=False, is_proxies = False):
        self.API_KEY = api_key
        self.API_SECRET_KEY = api_seceret_key
        self.PASSPHRASE = passphrase
        self.use_server_time = use_server_time
        self.BASE_URL = 'https://www.okex.com'
        self.is_proxies = is_proxies

    '''交易类接口'''
    ### type:1 开多， 2 开空， 3 平多， 4 平空
    ### order type： 0 普通 4 市价
    def create_order(self, instrument_id, type, size, order_type, price = None):
        method = 'POST'
        path = '/api/swap/v3/order'
        if order_type == '4':
            data = {
                'instrument_id': instrument_id,
                'type': type,
                'size': size,
                'order_type': order_type
            }
        else:
            data = {
                'instrument_id': instrument_id,
                'type': type,
                'price': price,
                'size': size,
                'order_type': order_type
            }
        data = json.dumps(data)
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path, str(data))
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers,
            data=data
        )
        return RequestManager().send_request(my_request, self.is_proxies)

    '''行情类接口'''
    def get_ticker(self,instrument_id):
        method = 'GET'
        path = f'''/api/swap/v3/instruments/{instrument_id}/ticker'''
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers
        )
        return RequestManager().send_request(my_request,self.is_proxies)

    def get_k_lines(self, instrument_id, granularity):
        method = 'GET'
        path = f'''/api/swap/v3/instruments/{instrument_id}/candles?granularity={granularity}'''
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers
        )
        return RequestManager().send_request(my_request,self.is_proxies)

    '''账户类接口'''
    # 单个币种合约账户信息
    def get_account(self,instrument_id):
        method = 'GET'
        path = f'''/api/swap/v3/{instrument_id}/accounts'''
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers
        )
        return RequestManager().send_request(my_request,self.is_proxies)

    # 单个合约持仓信息
    def get_position(self, instrument_id):
        method = 'GET'
        path = f'''/api/swap/v3/{instrument_id}/position'''
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers
        )
        return RequestManager().send_request(my_request,self.is_proxies)


if __name__ == '__main__':

    Okex_api_key = '24b047df-e66d-4286-8d9d-853dd297d49e'
    Okex_seceret_key = 'D970633D207B9FDEBAF9C8CEF59BFE4D'
    Okex_passphrase = 'arbitrage'
    test = Okex_swap_client(api_key=Okex_api_key,
                            api_seceret_key=Okex_seceret_key,
                            passphrase=Okex_passphrase,
                            is_proxies=True)
    ### 限价单
    # aa = test.create_order(instrument_id='BTC-USDT-SWAP',
    #                        type='1',
    #                        price='63000',
    #                        size='1',
    #                        order_type='0')
    ### 市价单
    aa = test.create_order(instrument_id='BTC-USDT-SWAP',
                           type='1',
                           size='1',
                           order_type='4')

    print(aa)

    ### ticker数据
    # while True:
    #     aa = test.get_ticker(instrument_id='BTC-USDT-SWAP')
    #     print(aa['last'])
    #     time.sleep(0.05)

    ### 账户信息
    # aa = test.get_account(instrument_id='BTC-USDT-SWAP')
    # print(aa)

    # aa = test.get_position(instrument_id='BTC-USDT-SWAP')
    # print(aa)