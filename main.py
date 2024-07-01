import binascii
import struct
import time

from machine import UART, Pin

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

UART_IO = SW4


class ACTION:
    STOP = 0
    PUSH = 1
    PULL = 2


led_power_io = Pin(LED1, Pin.OUT, Pin.PULL_DOWN)
led_connect_io = Pin(LED2, Pin.OUT, Pin.PULL_DOWN)
uart = UART(1, baudrate=115200, rx=UART_IO)

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


def _motor_control(id: int, action: int):
    if action == ACTION.PULL:
        ch_io[id][0].value(1)
        ch_io[id][1].value(0)
    elif action == ACTION.PUSH:
        ch_io[id][0].value(0)
        ch_io[id][1].value(1)
    elif action == ACTION.STOP:
        ch_io[id][0].value(0)
        ch_io[id][1].value(0)


def _motor_set(id: int, action: int):
    for i in range(4):
        if i != id:
            _motor_control(i, ACTION.STOP)
        else:
            _motor_control(i, action)


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

# CRC 校验函数
def calculate_crc(data):
    return binascii.crc32(data) & 0xFFFFFFFF

def read_uart():
    while True:
        if uart.any():
            length_byte = uart.read(1)  # 读取长度字节
            if length_byte:
                length = struct.unpack('B', length_byte)[0]
                data = uart.read(length)  # 读取数据
                if data:
                    crc_bytes = uart.read(4)  # 读取 CRC 校验
                    if crc_bytes and len(crc_bytes) == 4:
                        received_crc = struct.unpack('I', crc_bytes)[0]
                        calculated_crc = calculate_crc(data)
                        if received_crc == calculated_crc:
                            try:
                                command_id, channel, action = struct.unpack('BBB', data)
                                print(f"接收到 - 命令ID: {command_id}, 通道: {channel}, 动作: {action}")
                                if command_id == 0:
                                    _motor_control(channel, action)
                                elif command_id == 1:
                                    _motor_set(channel, action)
                            except struct.error as e:
                                print(f"解码错误: {e}")
                        else:
                            print("CRC 校验错误")
                    else:
                        print("读取 CRC 错误")
                else:
                    print("读取数据错误")


if __name__ == '__main__':
    gpio_init()
    # self_check()

    try:
        while True:
            read_uart()
    except KeyboardInterrupt:
        gpio_init()
