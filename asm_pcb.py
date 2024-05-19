import time

from machine import Pin

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


class ACTION:
    STOP = 0
    PUSH = 1
    PULL = 2

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

sw_io = [
    Pin(SW1, Pin.IN, Pin.PULL_DOWN), Pin(SW2, Pin.IN, Pin.PULL_DOWN), 
    Pin(SW3, Pin.IN, Pin.PULL_DOWN), Pin(SW4, Pin.IN, Pin.PULL_DOWN)
]

led_power_io = Pin(LED1, Pin.OUT, Pin.PULL_DOWN)
led_connect_io = Pin(LED2, Pin.OUT, Pin.PULL_DOWN)

channel_status = [ACTION.STOP, ACTION.STOP, ACTION.STOP, ACTION.STOP]
switch_status = [0, 0, 0, 0]

def motor_control(id: int, action: int, status_save=True):
    if action == ACTION.PULL:
        ch_io[id][0].value(1)
        ch_io[id][1].value(0)
    elif action == ACTION.PUSH:
        ch_io[id][0].value(0)
        ch_io[id][1].value(1)
    elif action == ACTION.STOP:
        ch_io[id][0].value(0)
        ch_io[id][1].value(0)

    if status_save:
        channel_status[id] = action

def gpio_init():

    for i in range(4):
        ch_io[i][0].value(0)
        ch_io[i][1].value(0)

    led_power_io.value(1)
    led_connect_io.value(0)

def self_check():
    for i in range(4):
        print(f"channel {i} testing")
        motor_control(i, ACTION.PULL)
        time.sleep(0.5)
        motor_control(i, ACTION.PUSH)
        time.sleep(0.5)
        motor_control(i, ACTION.STOP)
        time.sleep(0.5)

def logic():
    for i in range(4):
        if channel_status[i] == ACTION.PULL:
            # 回抽时，如果上微动触发则停止回抽
            if sw_io[i].value() == 1:
                motor_control(i, ACTION.STOP, False)
            else:
                motor_control(i, ACTION.PULL, False)
        else:
            if sw_io[i].value() == 1:
                switch_status[i] = 5
                motor_control(i, ACTION.PUSH, False)
            elif switch_status[i] > 0:
                if switch_status[i] == 1:
                    motor_control(i, channel_status[i])
                switch_status[i] -= 1

if __name__ == '__main__':
    gpio_init()
    self_check()

    try:
        while True:
            logic()
            time.sleep(0.1)
    except KeyboardInterrupt:
        gpio_init()
 