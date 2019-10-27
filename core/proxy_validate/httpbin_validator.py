import requests
import time
import json
from utils import http
import settings
from domain import Proxy
from utils.log import logger


def _check_http_proxy(proxies, isHttp=True):
    # 匿名程度
    nick_type = -1
    # 响应速度
    speed = -1

    if isHttp:
        test_url = 'http://httpbin.org/get'
    else:
        test_url = 'https://httpbin.org/get'
    try:
        start = time.time()
        response = requests.get(url=test_url, headers=http.get_request_headers(), timeout=settings.TEST_TIMEOUT, proxies=proxies)
        if response.ok:
            # 计算响应速度
            speed = round(time.time() - start, 2)
            # 把响应内动转换为字符串
            content = json.loads(response.text)
            # 获取请求头
            headers = content['headers']
            # 获取origin ，请求来源的Ip地址
            ip = content['origin']
            # 获取请求头中的‘Proxy-Connection’如果有，说明是匿名代理
            proxy_connection = headers.get('Proxy-Connection', None)

            if ',' in ip:
                # 如果‘origin’中含有‘，’分割的两个代理就是透明代理IP
                nick_type = 2 # 透明代理
            elif proxy_connection:
                # 如果header中包含‘Proxy-Connection‘
                nick_type = 1 # 匿名代理
            else:
                # 否则就为高匿代理
                nick_type = 0 # 高匿
            return True, nick_type, speed
        else:
            return False, nick_type, speed
    except Exception as e:
        # 测试中可记录错误，实际开发中请注释此行
        # logger.exception(e)
        return False, nick_type, speed


def check_proxt(proxy):
    '''
    检测代理协议类型，匿名程度
    :param proxy:
    :return:（协议：http和https：2，https：1，http：0，匿名程度：高匿：0，匿名：1，透明：0，速度，单位s）
    '''

    # 根据proxy对象构建，请求使用的代理
    proxies = {
    'http': "http://{}:{}".format(proxy.ip, proxy.port),
    'https': "https://{}:{}".format(proxy.ip, proxy.port),
    }

    http, http_nick_type, http_speed = _check_http_proxy(proxies)
    https, http_nick_type, http_speed = _check_http_proxy(proxies)

    if http and https:
        # 如果是http和https都可以请求成功，说明两种协议都支持，协议类型为2
        proxy.protocol = 2
        proxy.nick_type = http_nick_type
        proxy.speed = http_speed
    elif http:
        # 如果是http可以请求成功,说只支持http协议 协议类型为0
        proxy.protocol = 0
        proxy.nick_type = http_nick_type
        proxy.speed = http_speed
    elif https:
        # 如果是https可以请求成功,说只支持https协议 协议类型为1
        proxy.protocol = 1
        proxy.nick_type = http_nick_type
        proxy.speed = http_speed
    else:
        proxy.protocol = -1
        proxy.nick_type = -1
        proxy.speed = -1

    logger.debug(proxy)
    return proxy


if __name__ == '__main__':

    proxy = Proxy('112.231.214.137', port='8118')
    print(check_proxt(proxy))
