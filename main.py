import _thread
import gc
import json
import time

import esp  # type: ignore
import webrepl  # type: ignore

import asm_pcb as ams
from mpy_common import wifi_connect
from mpy_common.simple_log import log_boot
from mpy_common.time_util import sync_ntp
from socket_server import SocketServer

msg_type_gc = 0
msg_type_sys = 1
msg_type_broken_detect = 2


def on_socket_recv(client, data):
    data_len = len(data)

    # 简单检验客户端发送的数据是否正确
    if data_len == 8 and data[0:6] == b'\x2f\x2f\xff\xfe\x01\x02':  # YBA 原来的指令
        ch = int(data[-2])
        fx = int(data[-1])
        ams.motor_triiger(ch, fx)

    elif data_len >= 5 and data[0:4] == b'\x2f\x2f\xff\xfe':
        cmd = data[4:5]
        if b'\x02' == cmd:  # 同步所有通道
            channel_total = int.from_bytes(data[5:6], 'big')
            for i in range(channel_total):
                fx = int.from_bytes(data[6 + i:7 + i], 'big')
                if fx != 0:
                    ams.motor_triiger(i, fx)
        elif b'\xff' == cmd:    # gc
            free = gc.mem_free()
            alloc = gc.mem_alloc()
            gc.collect()
            gc_free = gc.mem_free()
            gc_alloc = gc.mem_alloc()
            socket_server.send(client, generate_msg(
                msg_type_gc, f'esp32c3 memory alloc:{alloc}, free:{free}, gc alloc:{gc_alloc}, gc free:{gc_free}'))
        elif b'\xfe' == cmd:    # 获取系统状态信息
            gc_free = gc.mem_free()
            gc_alloc = gc.mem_alloc()
            socket_server.send(client, generate_msg(
                msg_type_sys, f'esp32c3 memory alloc:{gc_alloc}, free:{gc_free}'))
        elif b'\xfd' == cmd:    # 获取断料状态
            sendBrokenState(ams.broken_detect.value())

    return True


def on_client_connect(client, address):
    ams.led_connect_io.value(1)


def on_client_disconnect(client, address):
    # TODO:此处最好判断下有几个客户端，如果还有客户端就不要关闭，虽然目前按逻辑只有一个
    ams.led_connect_io.value(0)


power_led_shake = True


def on_wifi_state(connected):
    global power_led_shake
    if connected:
        ams.led_power_io.value(1)
    else:
        ams.led_power_io.value(0 if power_led_shake else 1)
        power_led_shake = not power_led_shake


def sendBrokenState(state: int):
    socket_server.send_all(generate_msg(msg_type_broken_detect, str(state)))


def generate_msg(type: int, data: str):
    return json.dumps({
        'type': type,
        'data': data
    })


esp.osdebug(0)  # 禁用调试
# esp.sleep_type(esp.SLEEP_NONE)  # 禁用休眠

ams.gpio_init()
ams.led_power_io.value(1)
ams.led_connect_io.value(0)

gc.enable()  # 启用垃圾回收
print("已分配内存：", gc.mem_alloc())  # 查看当前已分配的内存
print("可用内存：", gc.mem_free())  # 查看当前可用的内存

# ams.self_check()

thread_id = _thread.start_new_thread(
    wifi_connect.wifi_check, (on_wifi_state, ))  # 启动Wifi检测线程

wifi_connect.wifi_init()  # 先连接网络
sync_ntp(sync_interval=0.1)  # 同步时间
log_boot()  # 记录启动

webrepl.start(password='123456')  # 启动 webrepl

socket_server = SocketServer('0.0.0.0', 3333, on_socket_recv,
                             need_send=True,
                             on_client_connect=on_client_connect,
                             on_client_disconnect=on_client_disconnect,
                             recive_size=512)
socket_server.start()

gc.collect()  # 执行垃圾回收
print(f"执行垃圾回收后的已分配内存：{gc.mem_alloc()}")
print(f"执行垃圾回收后的可用内存：{gc.mem_free()}")

try:
    while True:
        ams.logic(sendBrokenState)
        time.sleep(0.1)
except:
    ams.gpio_init()
    wifi_connect.stop_wifi_check()
    socket_server.stop()
    webrepl.stop()
    print('程序结束\n')
