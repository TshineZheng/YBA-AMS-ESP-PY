
import time

_time_zone_offset = 0

def local_time() -> time.struct_time:
    """获取本地时间戳

    Returns:
        int: 本地时间戳
    """
    global _time_zone_offset
    return time.localtime(time.time() + _time_zone_offset)

def local_time_format() -> str:
    """获取本地时间字符串

    Returns:
        str: 本地时间字符串
    """
    time_tuple = local_time()
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        time_tuple[0], time_tuple[1], time_tuple[2],
        time_tuple[3], time_tuple[4], time_tuple[5]
    )

def sync_ntp(sync_max_retry=20, sync_interval=0.3, ntp_host = 'ntp1.aliyun.com', timezone_offset = 8):
    """时间同步

    Args:
        sync_max_retry (int, optional): 同步失败重试次数. Defaults to 20.
        sync_interval (float, optional): 重试间隔（秒）. Defaults to 0.3.
        ntp_host (str, optional): nptp服务器. Defaults to 'ntp1.aliyun.com'.
        timezone_offset (_type_, optional): 时区偏移. Defaults to 8*3600.
    """

    global _time_zone_offset
    _time_zone_offset = timezone_offset * 3600

    import ntptime  # type: ignore
    
    print("同步时间中...")

    ntptime.host = ntp_host
    
    i = 0
    while True:
        try:
            # 同步时间
            ntptime.settime()
            break
        except Exception as e:
            print(e)

            time.sleep(sync_interval)
            i += 1
            if i >= sync_max_retry:
                print("同步时间失败")
                break
            pass

    # 获取当前时间
    current_time = time.localtime()
    # 打印当前时间
    print("当前时间:", current_time)
    print("校准时区后的时间:", local_time())


if __name__ == '__main__':
    sync_ntp()
    print(local_time_format())