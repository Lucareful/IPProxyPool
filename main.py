from multiprocessing import Process
from core.proxy_spider.run_spiders import RunSpider
from core.proxy_test import ProxyTest
from core.proxy_api import ProxyApi


"""
- 思路：
  - 开启三个进程，分别用于启动爬虫，检测代理IP，WEB服务
- 步骤：
- 定义一个run方法用于启动动代理池
  - 定义一个列表，用于存储要启动的进程创建启动爬虫的进程，添加到列表中创建启动检测的进程，添加到列表中
  - 创建启动提供API服务的进程，添加到列表中
  - 遍历进程列表，启动所有进程
  - 遍历进程列表，让主进程等待子进程的完成
- 在`if__name__=='__main__'：`中调用run方法
"""


def run():
    # 定义一个列表，用于存储要启动的进程
    proxy_list = []
    # 创建启动爬虫的进程，添加到列表中
    proxy_list.append(Process(target=RunSpider.start))
    # 创建启动检测的进程，添加到列表中
    proxy_list.append(Process(target=ProxyTest.start))
    # 创建启动提供API服务的进程，添加到列表中
    proxy_list.append(Process(target=ProxyApi.start))

    # 遍历进程列表，启动所有进程
    for process in proxy_list:
        # 设置守护进程
        process.daemon = True
        process.start()

    # 遍历进程列表，让主进程等待子进程的完成
    for process in proxy_list:
        process.join()


if __name__ == '__main__':
    run()
