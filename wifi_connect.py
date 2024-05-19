import time

import network
import smartconfig  # type: ignore
import utime

TYPES = {
    smartconfig.TYPE_ESPTOUCH: 'ESPTOUCH',
    smartconfig.TYPE_AIRKISS: 'AIRKISS',
    smartconfig.TYPE_ESPTOUCH_AIRKISS: 'ESPTOUCH_AIRKISS',
    smartconfig.TYPE_ESPTOUCH_V2: 'ESPTOUCH_V2'
}

TIMEOUT = 120_000  # ms


def save_config(ssid: str, password: str):
    """
    保存 wifi ssid 和 password 到 json 文件

    Args:
                                    ssid (str): ssid
                                    password (str): pw
    """
    with open('wifi_config.json', 'w') as f:
        f.write(f'{{"ssid": "{ssid}", "password": "{password}"}}')


def read_config():
    """
    读取 wifi 配置并返回 ssid 和 password
    """
    with open('wifi_config.json', 'r') as f:
        config = eval(f.read())
        return config['ssid'], config['password']


def check_config():
    """
    检查 wifi 配置是否存在，返回 bool 值
    """
    try:
        read_config()
        return True
    except:
        return False


def wifi_smartconfig():
    sta = network.WLAN(network.STA_IF)
    _ = sta.active(True)

    smartconfig.type(smartconfig.TYPE_ESPTOUCH_AIRKISS)
    print(f'smartconfig type: {TYPES[smartconfig.type()]}')

    smartconfig.start()

    start_ms = time.ticks_ms()

    while not smartconfig.done():
        if time.ticks_ms() - start_ms > TIMEOUT:
            print('smartconfig timeout')
            smartconfig.stop()
            return

        time.sleep_ms(100)

    print('smartconfig done, ', end='')

    if sta.status() == network.STAT_GOT_IP:
        print('and connected to ap')
        print(f'smartconfig info: {smartconfig.info()}')
        print(f'  - ssid: "{smartconfig.ssid()}"')
        print(f'  - password: "{smartconfig.password()}"')
        print(f'  - bssid: {smartconfig.bssid()}')
        print(f'  - type: {smartconfig.type()}({TYPES[smartconfig.type()]})')
        if smartconfig.rvd_data():
            # EspTouch V2 custom data
            print(f'  - rvd_data: {smartconfig.rvd_data()}')

        save_config(smartconfig.ssid(), smartconfig.password())
    else:
        # maybe wrong password or other situations
        print('but failed connect to ap')

    smartconfig.stop()


def connect_wifi(wlan: network.WLAN, WIFI_SSID: str, WIFI_PASSWORD: str):
    """
    连接WiFi函数
    Args:
                    wlan (wlan): wlan对象
                    WIFI_SSID (str): wifi ssid
                    WIFI_PASSWORD (password): 密码
    """
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        print("Connecting to WiFi...")
        utime.sleep_ms(1000)
    print("WiFi Connected!")
    print("IP Address:", wlan.ifconfig()[0])

def wifi_init():
    """
    Wifi初始化，开机启动时先执行此函数
    """
    # 设置WiFi为station模式并激活
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if check_config():
        print('wifi config exists')
        WIFI_SSID, WIFI_PASSWORD = read_config()
        connect_wifi(wlan, WIFI_SSID, WIFI_PASSWORD)
    else:
        while not smartconfig.done():
            wifi_smartconfig()

_running = False

def wifi_check():
    """
    检测WiFi连接状态并重新连接(如果需要)
    """
    global _running
    _running = True
    print("Wifi 守护线程启动\n")
    wlan = network.WLAN(network.STA_IF)
    WIFI_SSID, WIFI_PASSWORD = read_config()
    while _running:
        if not wlan.isconnected():
            print("WiFi disconnected, reconnecting...")
            wlan.disconnect()
            connect_wifi(wlan, WIFI_SSID, WIFI_PASSWORD)

        time.sleep(1)  # 检测WiFi连接状态的间隔
    print("Wifi 守护线程结束\n")

def stop_wifi_check():
    global _running
    _running = False

if __name__ == '__main__':
    wifi_init()
