import binascii
import struct
import time

import utime
from machine import UART, Pin

from mpy_common.file_util import file_exists

# 串口编号设置
M1_UP = 0
M1_DOWN = 1
M2_UP = 18
M2_DOWN = 19
M3_UP = 2
M3_DOWN = 3
M4_UP = 10
M4_DOWN = 6
SW1 = 7
SW2 = 5
SW3 = 4
SW4 = 11
LED1 = 12
LED2 = 13

BUFFER_1 = SW1
BUFFER_2 = SW2
DETECT_IO = SW3
UART_IO = SW4


class ACTION:
    STOP = 0
    PUSH = 1
    PULL = 2


uart = UART(1, baudrate=115200, tx=UART_IO)

led_power_io = Pin(LED1, Pin.OUT, Pin.PULL_DOWN)
led_connect_io = Pin(LED2, Pin.OUT, Pin.PULL_DOWN)

buffer_1 = Pin(BUFFER_1, Pin.IN, Pin.PULL_DOWN)
buffer_2 = Pin(BUFFER_2, Pin.IN, Pin.PULL_DOWN)
broken_detect = Pin(DETECT_IO, Pin.IN, Pin.PULL_DOWN)


ch_io = [
        [Pin(M1_UP, Pin.OUT, Pin.PULL_DOWN),
         Pin(M1_DOWN, Pin.OUT, Pin.PULL_DOWN)],
        [Pin(M2_UP, Pin.OUT, Pin.PULL_DOWN),
         Pin(M2_DOWN, Pin.OUT, Pin.PULL_DOWN)],
        [Pin(M3_UP, Pin.OUT, Pin.PULL_DOWN),
         Pin(M3_DOWN, Pin.OUT, Pin.PULL_DOWN)],
        [Pin(M4_UP, Pin.OUT, Pin.PULL_DOWN),
         Pin(M4_DOWN, Pin.OUT, Pin.PULL_DOWN)],
]

cur_ch: int = 0
cur_ch_action: int = ACTION.STOP

latest_state = None

CHANNEL_FILE = 'channel_latest'

def update_latest_channel(channel: int):
    with open(CHANNEL_FILE, 'w') as f:
        f.write(str(channel))

def get_latest_channel() -> int:
    # 如果文件不存在，则返回 0
    if not file_exists(CHANNEL_FILE):
        return 0
    
    try:
        with open(CHANNEL_FILE, 'r') as f:
            return int(f.read())
    except:
        return 0


def calculate_crc(data):
    # CRC 校验函数
    return binascii.crc32(data) & 0xFFFFFFFF


def uart_motor_control(ch: int, fx: int):
    data = struct.pack('BBB', 0, ch, fx)
    uart_msg(data)


def uart_motor_set(ch: int, fx: int):
    data = struct.pack('BBB', 1, ch, fx)
    uart_msg(data)


def uart_msg(data):
    length = len(data)
    crc = calculate_crc(data)
    # 数据包格式：长度(1字节) + 数据 + CRC(4字节)
    packet = struct.pack('B', length) + data + struct.pack('I', crc)
    uart.write(packet)


def _motor_control(ch: int, action: int):
    if ch < 4:
        if action == ACTION.PULL:
            ch_io[ch][0].value(1)
            ch_io[ch][1].value(0)
        elif action == ACTION.PUSH:
            ch_io[ch][0].value(0)
            ch_io[ch][1].value(1)
        elif action == ACTION.STOP:
            ch_io[ch][0].value(0)
            ch_io[ch][1].value(0)
    else:
        uart_motor_control(ch-4, action)

def _motor_set(ch: int, action: int):
    for i in range(4):
        if i != ch:
            _motor_control(i, ACTION.STOP)
        else:
            _motor_control(i, action)

    if ch < 4:
        uart_motor_set(0, ACTION.STOP)
    else:
        uart_motor_set(ch-4, action)

def motor_triiger(ch: int, action: int, test = False):
    global cur_ch
    global cur_ch_action

    if cur_ch == ch and cur_ch_action == action:
        return

    cur_ch = ch
    cur_ch_action = action
    _motor_control(ch, action)

    if test:
        return

    update_latest_channel(ch)


def gpio_init():

    for i in range(4):
        ch_io[i][0].value(0)
        ch_io[i][1].value(0)

    led_power_io.value(1)
    led_connect_io.value(0)


def self_check():
    for i in range(4):
        print(f"channel {i} testing")
        _motor_control(i, ACTION.PULL)
        time.sleep(0.5)
        _motor_control(i, ACTION.PUSH)
        time.sleep(0.5)
        _motor_control(i, ACTION.STOP)
        time.sleep(0.5)


def get_broken_state():
    return broken_detect.value()


def logic(onbrokenSwitch):
    global cur_ch
    global cur_ch_action
    global latest_state

    currentState = broken_detect.value()
    if currentState != latest_state:
        latest_state = currentState
        if onbrokenSwitch:
            onbrokenSwitch(latest_state)

    if cur_ch_action == ACTION.PUSH:
        if buffer_2.value() == 1:
            _motor_set(cur_ch, ACTION.STOP)
        else:
            _motor_set(cur_ch, ACTION.PUSH)
    elif cur_ch_action == ACTION.PULL:
        if buffer_1.value() == 1:
            _motor_set(cur_ch, ACTION.STOP)
        else:
            _motor_set(cur_ch, ACTION.PULL)
    else:
        if buffer_1.value() == 1:
            _motor_set(cur_ch, ACTION.PUSH)
        elif buffer_2.value() == 1:
            _motor_set(cur_ch, ACTION.PULL)
        else:
            _motor_set(cur_ch, ACTION.STOP)


def test_logic():
    # save latest channel
    latest_channel = get_latest_channel()
    print('latest channel', latest_channel)

    print('test logic start')
    for ch in [1, 5, 0, 2, 3, 4, 6, 7]:
        print(f"channel {ch} testing")
        motor_triiger(ch, ACTION.STOP, True)
        end_time = utime.ticks_ms() + 500
        while utime.ticks_ms() < end_time:
            logic(None)

    # restore latest channel
    motor_triiger(latest_channel, ACTION.STOP, True)

    print('test logic end')


if __name__ == '__main__':
    gpio_init()
    test_logic()
    # self_check()
    # motor_triiger(3, ACTION.PUSH)

    try:
        while True:
            logic(None)
            time.sleep(0.1)
            uart_motor_control(0, 1)
    except KeyboardInterrupt:
        gpio_init()
