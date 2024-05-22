from mpy_common import file_util


def log(msg: str):
    import os

    from mpy_common import time_util
    
    msg = f'[{time_util.local_time_format()}] : {msg}'

    print(msg)

    if file_util.file_exists('log0.txt'):
        # 检查日志文件大小
        log_file_size = os.stat('log0.txt')[6]
        if log_file_size > 10 * 1024:  # 1K
            # 重命名日志文件为 log1.txt ，如果 log1.txt 存在，则删除它
            if file_util.file_exists('log1.txt'):
                os.remove('log1.txt')
            os.rename('log0.txt', 'log1.txt')

    with open('log0.txt', 'a') as f:
        f.write(f'{msg}\n')
        f.flush()


def read_log():
    """读取日志文件
        for chunk in read_log():
            print(chunk)
    """

    if file_util.file_exists('log1.txt'):
        for chunk in file_util.read_file_by_chunk('log1.txt'):
            yield chunk

    if file_util.file_exists('log0.txt'):
        for chunk in file_util.read_file_by_chunk('log0.txt'):
            yield chunk


def log_boot():
    import machine
    rc = machine.reset_cause()
    case = 'unknow'
    if rc == machine.PWRON_RESET:
        case = "power on reset"
    elif rc == machine.HARD_RESET:
        case = "hard reset"
    elif rc == machine.WDT_RESET:
        case = "watchdog reset"
    elif rc == machine.DEEPSLEEP_RESET:
        case = "deepsleep reset"
    elif rc == machine.SOFT_RESET:
        case = "soft reset"

    log(f'system boot by {case}')

if __name__ == '__main__':
    log('test')
    for chunk in read_log():
        print(chunk)
