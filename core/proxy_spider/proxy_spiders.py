import time
import random
from core.proxy_spider.base_spider import BaseSpider

'''
1.实现西刺代理爬虫：http://www.xicidaili.com/nn1
    - 定义一个类，继承通用爬虫类（`BasicSpider`）
    - 提供urls，group_xpath 和detail_xpath
'''


class xiciSpider(BaseSpider):

    # 准备url列表
    urls = ['https://www.xicidaili.com/nn/{}'.format(i) for i in range(1, 10)]

    # 分组的xpath，用于获取iP信息的标签列表
    group_xpath = '//*[@id="ip_list"]/tr[position()>1]'

    # 组内的xpath，提取IP，prot， area
    detail_xpath = {
        'ip': './td[2]/text()',
        'port': './td[3]/text()',
        'area': './td[4]/a/text()'
    }


"""
2.实现ip3366代理爬虫：http://www.ip3366.net/free/？stype=1&page=1

- 定义一个类，继承通用爬虫类（BasicSpider）
- 提供urls，group_xpath 和detail_xpath
"""


class Ip366Spider(BaseSpider):

    # 准备url列表
    urls = ['http://www.ip3366.net/free/?stype={}&page={}'.format(i, j) for i in range(1, 3) for j in range(1, 8)]

    # 分组的xpath，用于获取iP信息的标签列表
    group_xpath = '//*[@id="list"]/table/tbody/tr'

    # 组内的xpath，提取IP，prot， area
    detail_xpath = {
        'ip': './td[1]/text()',
        'port': './td[2]/text()',
        'area': './td[5]/text()'
    }


class KuaidialiSpider(BaseSpider):
    # 实现快代理爬虫
    # 准备url列表
    urls = ['https://www.kuaidaili.com/free/inha/{}/'.format(j) for j in range(1, 11)]

    # 分组的xpath，用于获取iP信息的标签列表
    group_xpath = '//*[@id="list"]/table/tbody/tr'

    # 组内的xpath，提取IP，prot， area
    detail_xpath = {
        'ip': './td[1]/text()',
        'port': './td[2]/text()',
        'area': './td[5]/text()'
    }

    # 当我们两个页面访问时间太短了，就会被禁止访问（反扒虫手段）
    def get_page_from_url(self, url):
        # 随机等待1-3秒
        time.sleep(random.uniform(2, 5))
        # 调用父类的方法，发送请求，获取响应数据
        return super().get_page_from_url(url)


class FPBSpider(BaseSpider):
    # proxylistplus代理
    # 准备url列表
    urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-{}'.format(i) for i in range(1, 7)]

    # 分组的xpath，用于获取iP信息的标签列表
    group_xpath = '//*[@id="page"]/table[2]/tr[position()>2]'

    # 组内的xpath，提取IP，prot， area
    detail_xpath = {
        'ip': './td[2]/text()',
        'port': './td[3]/text()',
        'area': './td[5]/text()'
    }

"""
5.实现66ip爬虫：http://www.66ip.cn/1.html

- 定义一个类，继承通用爬虫类（BasicSpider）
- 提供urls，group_xpath和detail_xpath
- 由于66ip网页进行js+cookie反爬，需要重写父类的get_page_from_url 方法
"""


class Ip66Spider(BaseSpider):

    # 生成 'Cookie': 'Hm_lvt_1761fabf3c988e7f04bec51acd4073f4 = 1572000341, 1572054731;'信息
    # 确定Hm_lvt_1761fabf3c988e7f04bec51acd4073f4从哪里来
    # 观察发现：这个cookie信息不使用通过服务器响应设置来的；那么它就是通过js生成的
    # 准备url列表
    urls = ['http://www.66ip.cn/{}.html'.format(i) for i in range(1, 16)]

    # 分组的xpath，用于获取iP信息的标签列表
    group_xpath = '//*[@id="main"]/div/div[1]/table/tr[position()>1]'

    # 组内的xpath，提取IP，prot， area
    detail_xpath = {
        'ip': './td[1]/text()',
        'port': './td[2]/text()',
        'area': './td[3]/text()'
    }


if __name__ == '__main__':
    pass
    # spider = xiciSpider()
    # for proxy in spider.get_proxies():
    #     print(proxy)
    # spider = KuaidialiSpider()
    # for proxy in spider.get_proxies():
    #     print(proxy)
    #
    # spider = Ip66Spider()
    # for proxy in spider.get_proxies():
    #     print(proxy)


