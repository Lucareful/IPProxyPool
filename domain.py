from settings import MAX_SCORE

'''
- 定义Proxy类，继承object
- 实现_init_方法，负责初始化，包含如下字段：
  - ip：代理的IP地址
  - port：代理IP的端口号
  - protocol：代理IP支持的协议类型，http是0，https是1，https和http都支持是2
  - nick_type：代理IP的匿名程度，高匿：0，匿名：1，透明：2
  - speed：代理IP的响应速度，单位s
  - area：代理IP所在地区
  - score：代理IP的评分，用于衡量代理的可用性；默认分值可以通过配置文件进行配置.在进行代理可用性检查的时候，每遇到一次请求失败就减1份，减到0的时候从池中删除.如果检查代理可用，就恢复默认分值
  - disable_domains：不可用域名列表，有些代理IP在某些域名下不可用，但是在其他域名下可用
  - 在配置文件：settings.py中定义MAX_SCORE=50，表示代理IP的默认最高分数
- 提供_str方法，返回数据字符串
'''


class Proxy(object):

    def __init__(self, ip, port, protocol=-1, nick_type=-1, speed=-1, area=None, score=MAX_SCORE, disable_domains = []):

        self.ip = ip
        self.port = port
        self.protocol = protocol
        self.nick_type = nick_type
        self.speed = speed
        self.area = area
        self.score = score
        self.disable_domains = disable_domains

    def __str__(self):
        return str(self.__dict__)

