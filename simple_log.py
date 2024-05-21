import os
import socket
import time

import utime


def log(msg: str):
    # 假设您已经有了时区偏移量，例如UTC+8
    timezone_offset = 28800 # 8 * 3600  # 8小时的秒数
    # 获取当前UTC时间的时间戳，并添加时区偏移量
    timestamp = time.time() + timezone_offset
    # 使用localtime()将时间戳转换为时间元组
    time_tuple = time.localtime(timestamp)
    # 手动格式化时间元组为年月日时分秒的字符串
    formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        time_tuple[0], time_tuple[1], time_tuple[2],
        time_tuple[3], time_tuple[4], time_tuple[5]
    )

    msg = f'[{formatted_time}] : {msg}'

    print(msg)

    # 检查日志文件大小
    log_file_size = os.path.getsize('log.txt')
    if log_file_size > 10 * 1024:  # 10K
        # 重命名日志文件为 log2.txt ，如果 log2.txt 存在，则删除它
        if os.path.exists('log2.txt'):
            os.remove('log2.txt')
        os.rename('log.txt', 'log2.txt')

    with open('log.txt', 'a') as f:
        f.write(f'{msg}\n')
        f.flush()


def read_log() -> str:
    with open('log.txt', 'r') as f:
        return f.read()


if __name__ == '__main__':
    log('hello')