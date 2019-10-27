from settings import PROXIES_SPIDERS
from core.proxy_validate.httpbin_validator import check_proxt
from core.db.mongo_pool import MongoPool
from utils.log import logger
from settings import RUN_SPIDERS_INTERVAL

import importlib
import schedule
import time

# 打猴子补丁
from gevent import monkey
monkey.patch_all()
# 导入协程池
from gevent.pool import Pool


"""
- - 在`run_spider.py`中，创建`RunSpider`类
- 提供一个运行爬虫的run方法，作为运行爬虫的入口，实现核心的处理逻辑
  - 根据配置文件信息，获取爬虫对象列表.
  - 遍历爬虫对象列表，获取爬虫对象，遍历爬虫对象的get_proxies方法，获取代理IP
  - 检测代理IP（代理IP检测模块）
  - 如果可用，写入数据库（数据库模块）
  - 处理异常，防止一个爬虫内部出错了，影响其他的爬虫.
  
使用异步来执行每一个爬虫任务，以提高抓取代理IP效率
    - 在init 方法中创建协程池对象
    - 把处理一个代理爬虫的代码抽到一个方法
    - 使用异步执行这个方法
    - 调用协程的join方法，让当前线程等待队列任务的完成.
"""


class RunSpider(object):

    def __init__(self):
        # 创建mongo对象
        self.mongo_pool = MongoPool()
        # 创建协程池对象
        self.coroutine_pool = Pool()

    def get_spider_from_settings(self):
        """根据配置文件信息获取爬虫列表"""

        # 遍历配置文件中爬虫信息，获取每个爬虫全类名
        for full_class_name in PROXIES_SPIDERS:
            # core.proxy_spider.proxy_spiders.xiciSpider
            # 获取模块名 和 类名
            moudle_name, class_name = full_class_name.rsplit('.', maxsplit=1)
            # 根据模块名导入模块
            moudle = importlib.import_module(moudle_name)
            # 根据类名从模块中获取类
            clas = getattr(moudle, class_name)
            # 创建爬虫对象
            spider = clas()

            yield spider

    def run(self):

        # 根据配置文件信息，获取爬虫对象列表
        spiders = self.get_spider_from_settings()
        for spider in spiders:
            # 使用异步执行这个方法
            # self.__execute_one_spider_task(spider)
            self.coroutine_pool.apply_async(self.__execute_one_spider_task, args=(spider, ))
        self.coroutine_pool.join()

    def __execute_one_spider_task(self, spider):
        # 把处理一个代理爬虫的代码抽到一个方法
        """用于处理一个爬虫任务"""
        try:
            # 遍历爬虫对象get_proxies()方法，获取代理IP
            for proxy in spider.get_proxies():
                # print(proxy)
                # 检测代理IP是否可用（代理IP检测模块）
                proxy = check_proxt(proxy)
                # 如果可用，写入数据库（数据库模块）
                # 如果speed不为-1，就说明可用
                if proxy.speed != -1:
                    # 导入数据库（数据库模块）
                    self.mongo_pool.insert_one(proxy)
        except Exception as e:
            logger.exception(e)

    @classmethod
    def start(cls):
        # - 定义一个start的类方法
        # - 创建当前类的对象，调用run方法
        rs = RunSpider()
        rs.run()

        # 使用schedule模块，每隔一定的时间，执行当前对象的run方法
        schedule.every(RUN_SPIDERS_INTERVAL).hours.do(rs.run)
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == '__main__':
    # re = RunSpider()
    # re.run()
    RunSpider.start()

    # 测试schedule
    # def task():
    #     print("test")
    # schedule.every(5).seconds.do(task)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)


