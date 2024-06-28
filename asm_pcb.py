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

led_power_io = Pin(LED1, Pin.OUT, Pin.PULL_DOWN)
led_connect_io = Pin(LED2, Pin.OUT, Pin.PULL_DOWN)

cur_ch: int = 0
cur_ch_action: int = ACTION.STOP

latest_state = None

buffer_1 = Pin(SW1, Pin.IN, Pin.PULL_DOWN)
buffer_2 = Pin(SW2, Pin.IN, Pin.PULL_DOWN)
broken_detect = Pin(SW3, Pin.IN, Pin.PULL_DOWN)


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


def motor_triiger(id: int, action: int):
    global cur_ch
    global cur_ch_action
    
    if cur_ch == id and cur_ch_action == action:
        return
    
    cur_ch = id
    cur_ch_action = action
    _motor_control(id, action)


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


if __name__ == '__main__':
    gpio_init()
    # self_check()
    motor_triiger(3, ACTION.PUSH)

    try:
        while True:
            logic()
            time.sleep(0.05)
    except KeyboardInterrupt:
        gpio_init()
