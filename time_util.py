
def sync_ntp():
    import time

    import ntptime  # type: ignore
    
    print("同步时间中...")

    # 设置NTP服务器，这里使用阿里云的NTP服务器
    ntptime.host = 'ntp1.aliyun.com'

    while True:
        try:
            # 同步时间
            ntptime.settime()
            break
        except:
            pass

    # 获取当前时间
    current_time = time.localtime()

    # 打印当前时间
    print("当前时间:", current_time)
    # 如果需要设置时区（例如UTC+8），可以手动添加偏移量
    # 注意：这里的偏移量是以秒为单位
    timezone_offset = 8 * 3600
    adjusted_time = time.localtime(time.time() + timezone_offset)
    print("校准时区后的时间:", adjusted_time)