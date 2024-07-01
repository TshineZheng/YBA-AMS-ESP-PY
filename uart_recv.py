import binascii
import utime
import struct
import time

from machine import UART, Pin

uart = UART(1, baudrate=115200, rx=4)

# CRC 校验函数
def calculate_crc(data):
    return binascii.crc32(data) & 0xFFFFFFFF

if __name__ == '__main__':
    try:
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
                                except struct.error as e:
                                    print(f"解码错误: {e}")
                            else:
                                print("CRC 校验错误")
                        else:
                            print("读取 CRC 错误")
                    else:
                        print("读取数据错误")
    except KeyboardInterrupt:
        pass
