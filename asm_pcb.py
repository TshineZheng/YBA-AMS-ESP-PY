import time

from machine import Pin

from servo import Servo

servo_deg_clamp = 110   # 夹紧
servo_deg_unclamp = 0   # 松开

def set_servo_deg(deg_clamp, deg_unclamp):
    global servo_deg_clamp
    global servo_deg_unclamp
    servo_deg_clamp = deg_clamp
    servo_deg_unclamp = deg_unclamp


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

servo_io = [
     Servo(SW1), Servo(SW2), Servo(SW3), Servo(SW4)
]

led_power_io = Pin(LED1, Pin.OUT, Pin.PULL_DOWN)
led_connect_io = Pin(LED2, Pin.OUT, Pin.PULL_DOWN)

channel_status = [ACTION.STOP, ACTION.STOP, ACTION.STOP, ACTION.STOP]
switch_status = [0, 0, 0, 0]

def motor_control(id: int, action: int, status_save=True):
    if action == ACTION.PULL:
        if ACTION.STOP == channel_status[id]:
            global servo_deg_clamp
            servo_io[id].write(servo_deg_clamp)
            time.sleep(0.3)
        ch_io[id][0].value(1)
        ch_io[id][1].value(0)

            
    elif action == ACTION.PUSH:
        if ACTION.STOP == channel_status[id]:
            global servo_deg_clamp
            servo_io[id].write(servo_deg_clamp)
            time.sleep(0.3)
        ch_io[id][0].value(0)
        ch_io[id][1].value(1)

    elif action == ACTION.STOP:
        ch_io[id][0].value(0)
        ch_io[id][1].value(0)
        if ACTION.STOP != channel_status[id]:
            global servo_deg_unclamp
            servo_io[id].write(servo_deg_unclamp)

    if status_save:
        channel_status[id] = action

def gpio_init():
    global servo_deg_unclamp

    for i in range(4):
        ch_io[i][0].value(servo_deg_unclamp)
        ch_io[i][1].value(servo_deg_unclamp)
        servo_io[i].write(servo_deg_unclamp)

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

if __name__ == '__main__':
    set_servo_deg(110, 0)
    gpio_init()
    try:
        while True:
            self_check()
    except KeyboardInterrupt:
        gpio_init()
 