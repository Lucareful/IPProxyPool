import sys
import logging

# 导入settngs.py配置信息
from settings import LOG_FMT, LOG_LEVEL, LOG_FILENAME, LOG_DATEFMT


class Logger(object):
    def __init__(self):
        # 1.获取一个logger对象
        self._logger = logging.getLogger()
        # 2.设置format对象
        self.formatter = logging.Formatter(fmt=LOG_FMT, datefmt=LOG_DATEFMT)
        # 3.设置日志输出
        # 3.1设置文件日志模式
        self._logger.addHandler(self._get_file_handle(LOG_FILENAME))
        # 3.2 设置终端日志模式
        self._logger.addHandler(self._get_console_handle())
        # 4.设置日志等级
        self._logger.setLevel(LOG_LEVEL)

    def _get_file_handle(self, filename):
        '''返回一个文件日志handler'''
        # 1. 获取一个文件日志handler
        filehandler = logging.FileHandler(filename=filename, encoding='utf-8')
        # 2.设置日志格式
        filehandler.setFormatter(self.formatter)

        return filehandler

    def _get_console_handle(self):
        '''返回一个输入到终端日志的handler'''
        # 1. 获取一个输出到终端日志的handler
        console_handler = logging.StreamHandler(sys.stdout)
        # 2. 设置日志格式
        console_handler.setFormatter(self.formatter)

        return console_handler

    @property
    def logger(self):
        return self._logger


# 初始化并配一个logger对象,类的实例化
# 使用时，直接导入logger就可以使用
logger = Logger().logger


if __name__ == '__main__':
    logger.debug("调试信息")
    logger.info("状态信息")
    logger.warning("警告信息")
    logger.error("错误信息")
    logger.critical("严重错误信息")
