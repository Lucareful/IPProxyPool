import pymongo
import random
from pymongo import MongoClient
from settings import MONGO_URL
from utils.log import logger
from domain import Proxy


"""
- 步骤：
  1.在init中，建立数据连接，获取要操作的集合，在del方法中关闭数据库连接
  2.提供基础的增删改查功能
  - 实现插入功能
  - 实现修改该功能
  - 实现删除代理：根据代理的IP删除代理
  - 查询所有代理IP的功能
- 3.提供代理API模块使用的功能
  - 实现查询功能：根据条件进行查询，可以指定查询数量，先分数降序，速度升序排，保证优质的代理IP在上面.
  - 实现根据协议类型和要访问网站的域名，获取代理IP列表
  - 实现根据协议类型和要访问完整的域名，随机获取一个代理IP
  - 实现把指定域名添加到指定IP的disable_domain列表中.
"""


class MongoPool(object):

    def __init__(self):
        # 在init中，建立数据连接，获取要操作的集合
        self.client = MongoClient(MONGO_URL)
        # 获取要操作的集合
        self.proxies = self.client['proxies_pool']['proxies']

    def __del__(self):
        # 关闭数据库的连接
        self.client.close()

    def insert_one(self, proxy):
        """实现插入功能"""

        count = self.proxies.count_documents({'_id': proxy.ip})
        if count == 0:
            # 使用proxyip作为MongoDB中数据的主键_id
            dic = proxy.__dict__
            dic['_id'] = proxy.ip
            self.proxies.insert_one(dic)
            logger.info('插入新的代理{}'.format(proxy.ip))
        else:
            logger.warning("已存在的代理：{}".format(proxy.ip))

    def update_one(self, proxy):
        """实现修改的功能"""
        self.proxies.update_one({'_id': proxy.ip}, {'$set': proxy.__dict__})

    def delete_one(self, proxy):
        """实现删除代理，根据ip删除代理"""
        self.proxies.delete_one({'_id': proxy.ip})
        logger.info("删除代理IPL{}".format(proxy.ip))

    def find_all(self):
        """查询所有代理ip的功能"""
        cusor = self.proxies.find()
        for item in cusor:
            # 删除_id这个key
            item.pop('_id')
            proxy = Proxy(**item)
            yield proxy

    def find(self, conditions={}, count=0):
        """
        实现查询功能：根据条件进行查询，可以指定查询数量，先分数降序，速度升序排，保证优质的代理IP在上面
        :param conditions:查询条件字典
        :param count:限制取出多少个代理IP
        :return:返回满足要求代理IP（proxy对象）列表
        """
        cursor = self.proxies.find(conditions, limit=count).sort([
            ('score', pymongo.DESCENDING), ('speed', pymongo.ASCENDING)
        ])

        # 准备列表，用于存储查询处理代理IP
        proxy_list = []
        # 遍历
        for item in cursor:
            item.pop('_id')
            proxy = Proxy(**item)
            proxy_list.append(proxy)

        # 返回满足要求代理IP（proxy对象）列表
        return proxy_list

    def get_proxies(self, protocol=None, domain=None, count=0, nick_type=0):
        """
        根据协议类型和要访问网站的域名，获取代理IP列表
        :param protocol:协议：http， https
        :param domain:域名：jd.com
        :param count:用于获取多个代理IP，默认是获取所有的
        :param nick_type:匿名类型，默认获取最高匿的代理IP
        :return:满足要求的代理IP列表
        """

        # 定义查询条件
        conditions = {'nick_type': nick_type}
        # 根据协议，指定查询条件
        if protocol is None:
            # 如果没有传入协议类型，返回支持http和https协议的代理IP
            conditions['protocol'] = 2
        elif protocol.lower() == 'http':
            conditions['protocol'] = {'$in': [0, 2]}
        else:
            conditions['protocol'] = {'$in': [1, 2]}

        if domain:
            conditions['disable_domains'] = {'$nin': [domain]}

        return self.find(conditions, count=count)

    def random_proxy(self, protocol=None, domain=None, count=0, nick_type=0):
        """
        根据协议类型和要访问网站的域名，随机获取一个代理
        :param protocol:协议：http， https
        :param domain:域名：jd.com
        :param count:用于获取多个代理IP，默认是获取所有的
        :param nick_type:匿名类型，默认获取最高匿的代理IP
        :return:满足要求的随机的一个代理IP（Proxy对象）
        """
        proxy_list = self.get_proxies(protocol=protocol, domain=domain, count=count, nick_type=nick_type)
        # 从proxy_list列表中随机取出一个代理IP返回

        return random.choice(proxy_list)

    def disable_domain(self, ip, domain):
        """
        把指定域名添加到指定IP的disable_domain列表中.
        :param ip:IP地址
        :param domain:域名
        :return:返回True表示添加成功，否则添加失败
        """
        if self.proxies.count_documents({'_id': ip, 'disable_domains': domain}) == 0:
            self.proxies.update_one({'_id': ip}, {'$push': {'disable_domains': domain}})
            return True
        return False


if __name__ == '__main__':

    mongo = MongoPool()
    # for i in mongo.get_proxies():
    #     print(i)
    # 测试更新功能
    # proxy = Proxy('202.104.113.35', port='8881')
    # mongo.update_one(proxy)
    # 测试插入功能
    # proxy = Proxy('202.104.113.36', port='23654')
    # mongo.insert_one(proxy)
    # 测试删除功能
    # proxy = Proxy('202.104.113.35', port='8881')
    # mongo.delete_one(proxy)

    # 测试查询功能
    # for proxy in mongo.find_all():
    #     print(proxy)

    # 根据条件查找功能测试
    # for proxy in mongo.find():
    #     print(proxy)

    # 查询功能测试
    # for proxy in mongo.get_proxies():
    #     print(proxy)

