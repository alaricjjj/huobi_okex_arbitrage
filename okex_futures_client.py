import utils
from requests import Request
from request_manager import RequestManager
import json



class FuturesClient():

    def __init__(self, api_key, api_seceret_key, passphrase, use_server_time=False,is_proxies = False):
        self.API_KEY = api_key
        self.API_SECRET_KEY = api_seceret_key
        self.PASSPHRASE = passphrase
        self.use_server_time = use_server_time
        self.BASE_URL = 'https://www.okex.com'
        self.is_proxies = is_proxies

    '''交割合约API'''

    # 获取合约持仓信息
    def get_position(self, instrument_id=None):
        method = 'GET'
        if instrument_id:
            path = '/api/futures/v3/{instrument_id}/position'.format(instrument_id=instrument_id)
        else:
            path = '/api/futures/v3/position'
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers
        )
        return RequestManager().send_request(my_request,self.is_proxies)

    # 获取合约账户信息
    def get_accounts(self, currency=None):
        method = 'GET'
        if currency:
            path = '/api/futures/v3/accounts/{currency}'.format(currency=currency)
        else:
            path = '/api/futures/v3/accounts'
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers
        )
        # print(my_request)
        return RequestManager().send_request(my_request,self.is_proxies)

    # 获取合约币种杠杆倍数
    def get_leverage(self, currency):
        method = 'GET'
        path = '/api/futures/v3/accounts/{currency}/leverage'.format(currency=currency)
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers
        )
        return RequestManager().send_request(my_request,self.is_proxies)

    # # 设定合约币种杠杆倍数
    # def post_leverage(self, currency, leverage):
    #     leverage = json.dumps(leverage)
    #     method = 'POST'
    #     path = '/api/futures/v3/accounts/{currency}/leverage'.format(currency=currency)
    #     headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path, str(leverage))
    #     my_request = Request(
    #         method=method,
    #         url=self.BASE_URL + path,
    #         headers=headers,
    #         data=leverage
    #     )
    #     return RequestManager().send_request(my_request,self.is_proxies)

    # 设定全仓合约杠杆倍数
    def post_crossed_leverage(self, underlying, leverage):
        method = 'POST'
        path = '/api/futures/v3/accounts/{underlying}/leverage'.format(underlying=underlying)
        data = {
            'leverage': leverage
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

    # 设定逐仓合约杠杆倍数
    def post_fixed_leverage(self, underlying, instrument_id, direction, leverage):
        method = 'POST'
        path = '/api/futures/v3/accounts/' + underlying + '/leverage'
        data = {
            'instrument_id':instrument_id,
            'direction': direction,
            'leverage': leverage
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


    # 获取账单流水查询
    def get_ledger(self, currency):
        method = 'GET'
        path = '/api/futures/v3/accounts/{currency}/ledger'.format(currency=currency)
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers
        )
        return RequestManager().send_request(my_request,self.is_proxies)

    # 下单
    # type种类：1:开多2:开空3:平多4:平空
    def post_order(self, instrument_id, type, price, size):
        method = 'POST'
        path = '/api/futures/v3/order'
        data = {
            'instrument_id':instrument_id,
            'type':type,
            'price':price,
            'size':size
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

    # 批量下单
    def batch_orders(self, orders_data_input , instrument_id_input , client_oid_input = 'BlockPulse'):
        # orders = json.dumps(orders)
        method = 'POST'
        path = '/api/futures/v3/orders/'
        data = {
            'instrument_id': instrument_id_input,
            'orders_data': orders_data_input,
            'client_oid': client_oid_input
        }
        data = json.dumps(data)
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path,str(data))
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers,
            data=data
        )
        return RequestManager().send_request(my_request,self.is_proxies)

    # 撤销指定订单
    def cancel_order_by_order_id(self, order_id, instrument_id):
        method = 'POST'
        path = '/api/futures/v3/cancel_order/{instrument_id}/{order_id}'.format(instrument_id=instrument_id,
                                                                                order_id=order_id)
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers
        )
        return RequestManager().send_request(my_request,self.is_proxies)

    # # 批量撤销订单
    # def cancel_batch_orders(self, instrument_id, order_ids):
    #     orders = json.dumps(order_ids)
    #     method = 'POST'
    #     path = '/api/futures/v3/cancel_batch_orders/{instrument_id}'.format(instrument_id=instrument_id)
    #     headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path, str(orders))
    #     my_request = Request(
    #         method=method,
    #         url=self.BASE_URL + path,
    #         headers=headers,
    #         data=orders
    #     )
    #     return RequestManager().send_request(my_request,self.is_proxies)

    # 批量撤销订单
    def cancel_batch_orders(self, instrument_id, order_ids):
        data = {
            'order_ids': order_ids
        }
        data = json.dumps(data)
        method = 'POST'
        path = '/api/futures/v3/cancel_batch_orders/{instrument_id}'.format(instrument_id=instrument_id)
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path, str(data))
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers,
            data=data
        )
        return RequestManager().send_request(my_request, self.is_proxies)

    # 获取订单列表
    # def get_orders(self, instrument_id):
    #     method = 'GET'
    #     path = '/api/futures/v3/orders/{instrument_id}'.format(instrument_id=instrument_id)
    #     headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
    #     my_request = Request(
    #         method=method,
    #         url=self.BASE_URL + path,
    #         headers=headers
    #     )
    #     return RequestManager().send_request(my_request,self.is_proxies)

    # 获取订单列表
    # state种类：
    # -2:失败
    # -1:撤单成功
    # 0:等待成交
    # 1:部分成交
    # 2:完全成交
    # 3:下单中
    # 4:撤单中
    # 6: 未完成（等待成交+部分成交）
    # 7:已完成（撤单成功+完全成交）

    def get_orders(self, instrument_id,state):
        method = 'GET'
        path = '/api/futures/v3/orders/{instrument_id}?state={state}'.format(instrument_id=instrument_id,state=state)
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers
        )
        return RequestManager().send_request(my_request,self.is_proxies)


    # 获取某一订单信息
    def get_order_by_id(self, instrument_id, order_id):
        method = 'GET'
        path = '/api/futures/v3/orders/{instrument_id}/{order_id}'.format(instrument_id=instrument_id, order_id=order_id)
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers
        )
        return RequestManager().send_request(my_request,self.is_proxies)



    # 获取成交明细
    # def get_fills(self):
    #     method = 'GET'
    #     path = '/api/futures/v3/fills'
    #     headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
    #     my_request = Request(
    #         method=method,
    #         url=self.BASE_URL + path,
    #         headers=headers
    #     )
    #     return RequestManager().send_request(my_request,self.is_proxies)


    # 获取成交明细
    def get_fills(self,instrument_id):
        method = 'GET'
        path = '/api/futures/v3/fills?instrument_id={instrument_id}'.format(instrument_id=instrument_id)
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers
        )
        return RequestManager().send_request(my_request,self.is_proxies)

    ###加入修改

    # 设置合约币种账户模式
    def margin_mode(self,underlying, margin_mode):
        method='POST'
        path = '/api/futures/v3/accounts/margin_mode'
        data = {
            'underlying': underlying,
            'margin_mode': margin_mode
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






    ###公共信息
    # 获取合约信息
    def get_instruments(self):
        method = 'GET'
        path = '/api/futures/v3/instruments'
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers
        )
        return RequestManager().send_request(my_request,self.is_proxies)

    # 获取深度数据
    def get_depth(self,instrument_id):
        method = 'GET'
        path = '/api/futures/v3/instruments/{instrument_id}/book'.format(instrument_id=instrument_id)
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers
        )
        return RequestManager().send_request(my_request,self.is_proxies)

    # 获取ticker信息
    def get_ticker(self, instrument_id):
        method = 'GET'
        if instrument_id:
            path = '/api/futures/v3/instruments/{instrument_id}/ticker'.format(instrument_id=instrument_id)
        else:
            path = '/api/futures/v3/instruments/ticker'
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers
        )
        return RequestManager().send_request(my_request,self.is_proxies)

    # 获取k线数据
    def get_k_line(self,instrument_id,start=None,end=None,granularity=None):
        method ='GET'
        data = {
            'instrument_id':instrument_id,
            # 'start':start,
            # 'end':end,
            'granularity':'' + str(granularity) + ''
        }

        data = json.dumps(data)
        path = '/api/futures/v3/instruments/{instrument_id}/candles'.format(instrument_id=instrument_id)+'?granularity='+str(granularity)
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers
        )
        return RequestManager().send_request(my_request, self.is_proxies)

    def get_history_klines(self, instrument_id,from_time = None, to_time = None, granularity='60'):
        if from_time == None and to_time == None:
            params = f'''?granularity={granularity}'''
        else:
            params = f'''?start={to_time}&end={from_time}&granularity={granularity}'''

        method ='GET'
        path = '/api/swap/v3/instruments/{instrument_id}/history/candles'.format(instrument_id=instrument_id)
        path = path + params

        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers
        )
        return RequestManager().send_request(my_request, self.is_proxies)



    # 获取预估交割价
    def get_estimated_price(self,instrument_id):
        method ='GET'
        path = '/api/futures/v3/instruments/{instrument_id}/estimated_price'.format(instrument_id=instrument_id)
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers
        )
        return RequestManager().send_request(my_request,self.is_proxies)

    # 获取当前限价
    def get_limit_price(self,instrument_id):
        method ='GET'
        path = '/api/futures/v3/instruments/{instrument_id}/price_limit'.format(instrument_id=instrument_id)
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers
        )
        return RequestManager().send_request(my_request,self.is_proxies)

    # 获取标记价格
    def get_mark_price(self,instrument_id):
        method ='GET'
        path = '/api/futures/v3/instruments/{instrument_id}/mark_limit'.format(instrument_id=instrument_id)
        headers = utils.create_headers(self.API_KEY, self.API_SECRET_KEY, self.PASSPHRASE, method, path)
        my_request = Request(
            method=method,
            url=self.BASE_URL + path,
            headers=headers
        )
        return RequestManager().send_request(my_request,self.is_proxies)

if __name__ == '__main__':
    test = FuturesClient(api_key = '',
                         api_seceret_key = '',
                         passphrase = '',
                         use_server_time=False,
                         is_proxies = True)

    from_time = '2019-09-30T00:00:00.000Z'
    to_time =   '2019-10-05T08:00:00.000Z'

    print(test.get_history_klines(instrument_id = 'BTC-USD-SWAP',
                                  granularity = 3600,
                                  from_time = from_time,
                                  to_time = to_time))
