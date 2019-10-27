# -*- coding: utf-8 -*-

import telnetlib

print('------------------------connect---------------------------')
# 连接Telnet服务器
try:
    tn = telnetlib.Telnet('112.231.214.137', port='8118', timeout=20)
except:
    print('失败')
else:
    print('成功')

print('-------------------------end----------------------------')