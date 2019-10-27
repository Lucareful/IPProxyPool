from core.db.mongo_pool import MongoPool
from core.proxy_validate.httpbin_validator import check_proxt
from settings import MAX_SCORE, TES_PROXIES_ASYNC_COUNT, TEST_SPIDERS_INTERVAL

from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool
from queue import Queue

import schedule
import time


"""
- 目的：检查代理IP可用性，保证代理池中代理IP基本可用
- 思路
  - 1.在`proxy_test.py`中，创建`Proxy Tester`类
  - 2.提供一个run 方法，用于处理检测代理命核心逻辑
    - 从数据库中获取所有代理IP
    - 遍历代理IP列表
    - 检查代理可用性
      - 如果代理不可用，让代理分数-1，如果代理分数等于0就从数据库中删除该代理，否则更新该代理IP
      - 如果代理可用，就恢复该代理的分数，更新到数据库中

为了提高检查的速度，使用异步来执行检测任务
- 在`init`方法中，创建队列和协程池
  - 把要检测的代理IP，放到队列中
  - i.把检查一个代理可用性的代码，抽取到一个方法中；从队列中获取代理IP，进行检查；检查完毕，调度队列的task_done方法
  - ii.通过异步回调，使用死循环不断执行这个方法，
  - iv.开启多个异步任务，来处理代理IP的检测；可以通过配置文件指定异步数量

使用schedule模块，每隔一定的时间，执行一次检测任务

  - 定义类方法start，用于启动检测模块
  - 在start方法中
    - i.创建本类对象
    - i.调用run方法
    - i.每间隔一定时间，执行一下，run方法
"""


class ProxyTest(object):

    def __init__(self):
        # 创建操作数据库的MongoPool对象
        self.mongo_pool = MongoPool()
        # 创建队列和协程池
        self.queue = Queue()
        self.coroutine_pool = Pool()

    def __check_callback(self, temp):
        self.coroutine_pool.apply_async(self.__check_one_proxy)

    def run(self):
        # 提供一个run 方法，用于处理检测代理命核心逻辑
        # - 从数据库中获取所有代理IP
        proxies = self.mongo_pool.find_all()

        # - 遍历代理IP列表
        for proxy in proxies:
            # 把代理IP添加到队列中
            self.queue.put(proxy)

        # .开启多个异步任务，来处理代理IP的检测；可以通过配置文件指定异步数量
        for i in range(TES_PROXIES_ASYNC_COUNT):
            # 通过异步回调，使用死循环不断执行这个方法
            self.coroutine_pool.apply_async(self.__check_one_proxy, callback=self.__check_callback)

        # 让当前线程等待队列的完成
        self.queue.join()

    def __check_one_proxy(self):
        # 从队列中获取代理IP，进行检查
        proxy = self.queue.get()
        # 检查代理可用性
        proxy = check_proxt(proxy)

        # 如果代理不可用，让代理分数 - 1，如果代理分数等于0就从数据库中删除该代理
        if proxy.speed == -1:
            proxy.score -= 1
            if proxy.score == 0:
                self.mongo_pool.delete_one(proxy)
            else:
                # 否则更新该代理IP
                self.mongo_pool.update_one(proxy)
        else:
            # 如果代理可用，就恢复该代理的分数，更新到数据库中
            proxy.score = MAX_SCORE
            self.mongo_pool.update_one(proxy)

        # 检查完毕，调度队列的task_done方法
        self.queue.task_done()

    @classmethod
    def start(cls):
        # 创建本类对象
        proxy_tester = cls()
        # 调用run方法
        proxy_tester.run()

        # 每间隔一定时间，执行一下，run方法
        schedule.every(TEST_SPIDERS_INTERVAL).hours.do(proxy_tester.run())
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == '__main__':

    ProxyTest.start()

