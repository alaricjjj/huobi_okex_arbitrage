import hmac
import hashlib
import base64
import time
import pytz
import datetime
import consts as c


def sign(message, secretKey):
    mac = hmac.new(bytes(secretKey, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()
    return base64.b64encode(d)


def pre_hash(timestamp, method, request_path, body):
    return str(timestamp) + str.upper(method) + request_path + body


def get_header(api_key, sign, timestamp, passphrase):
    header = dict()
    header[c.CONTENT_TYPE] = c.APPLICATION_JSON
    header[c.OK_ACCESS_KEY] = api_key
    header[c.OK_ACCESS_SIGN] = sign
    header[c.OK_ACCESS_TIMESTAMP] = str(timestamp)
    header[c.OK_ACCESS_PASSPHRASE] = passphrase

    return header


def parse_params_to_str(params):
    url = '?'
    for key, value in params.items():
        url = url + str(key) + '=' + str(value) + '&'

    return url[0:-1]


def get_timestamp():
    # millis = int(round(time.time() * 1000))
    now = datetime.datetime.now(tz=pytz.timezone('UTC'))
    t = now.isoformat("T", "milliseconds")
    return t[:-6] + "Z"


def signature(timestamp, method, request_path, body, secret_key):
    if str(body) == '{}' or str(body) == 'None':
        body = ''
    message = str(timestamp) + str.upper(method) + request_path + str(body)
    mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()
    return base64.b64encode(d)


def create_headers(api_key, secret_key, passphrase, method, path, data=''):
    timestamp = get_timestamp()
    signature = sign(pre_hash(timestamp, method, path, data), secret_key)
    headers = get_header(api_key, signature, timestamp, passphrase)
    return headers

def create_params(api_key, secret_key, params_dict = None):
    params_dict['api_key'] = api_key
    params_dict['time'] = int(time.time() * 1000)
    sorted_keys = sorted(params_dict.keys())
    req_string = ''
    for item in sorted_keys:
        req_string += item
        req_string += str(params_dict[item])
    req_string += secret_key
    my_md5 = hashlib.md5()  # 获取一个MD5的加密算法对象
    my_md5.update(req_string.encode('utf-8'))  # 得到MD5消息摘要
    my_md5_Digest = my_md5.hexdigest()  # 以16进制返回消息摘要，32位
    params_dict['sign'] = my_md5_Digest
    return params_dict
