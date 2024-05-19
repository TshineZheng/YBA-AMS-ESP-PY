import _thread
import gc
import time

import esp  # type: ignore
import network

import asm_pcb as ams
import wifi_connect
from socket_server import SocketServer


def on_socket_recv(client, data):
    if len(data) <= 0:
        print("socket 断开")
        return False
    
    # 简单检验客户端发送的数据是否正确
    if len(data) == 8 and data[0:6] == b'\x2f\x2f\xff\xfe\x01\x02': # YBA 原来的指令
        ch = int(data[-2])
        fx = int(data[-1])
        ams.motor_control(ch, fx)

    elif len(data) >= 5 and data[0:4] == b'\x2f\x2f\xff\xfe': # 获取内存数据
        cmd = data[4:5]

        if cmd == b'\xff':
            free = gc.mem_free()
            alloc = gc.mem_alloc()

            gc.collect()

            gc_free = gc.mem_free()
            gc_alloc = gc.mem_alloc()

            socket_server.send(client, f'esp32c3 memory alloc:{alloc}, free:{free}, gc alloc:{gc_alloc}, gc free:{gc_free}')

    return True

def on_client_connect(client, address):
    ams.led_connect_io.value(1)

def on_client_disconnect(client, address):
    # TODO:此处最好判断下有几个客户端，如果还有客户端就不要关闭，虽然目前按逻辑只有一个
    ams.led_connect_io.value(0)

esp.osdebug(0)  # 禁用调试
# esp.sleep_type(esp.SLEEP_NONE)  # 禁用休眠

ams.gpio_init()
ams.led_power_io.value(1)
ams.led_connect_io.value(0)

gc.enable()  # 启用垃圾回收
print("已分配内存：", gc.mem_alloc())  # 查看当前已分配的内存
print("可用内存：", gc.mem_free())  # 查看当前可用的内存

# ams.self_check()

wifi_connect.wifi_init()  # 先连接网络

_thread.start_new_thread(wifi_connect.wifi_check, ())  # 启动Wifi检测线程

socket_server = SocketServer('0.0.0.0', 3333, on_socket_recv, 
                             need_send=True, 
                             on_client_connect=on_client_connect, 
                             on_client_disconnect=on_client_disconnect, 
                             recive_size=8)
socket_server.start()

gc.collect()  # 执行垃圾回收
# 再次查看内存使用情况
print(f"执行垃圾回收后的已分配内存：{gc.mem_alloc()}")
print(f"执行垃圾回收后的可用内存：{gc.mem_free()}")

try:
    while True:
        ams.logic()
        time.sleep(0.1)
except:
    ams.gpio_init()
    wifi_connect.stop_wifi_check()
    socket_server.stop()
    print('程序结束\n')
