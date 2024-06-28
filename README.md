复刻 [YBA-AMS-ESP](https://github.com/YBA0312/YBA-AMS-ESP/tree/main) 固件，修复第4通道无法使用BUG，优化断连问题。
> 需要单缓冲请参看 [single buffer](https://github.com/TshineZheng/YBA-AMS-ESP-PY/tree/single_buffer) 分支

## 固件
[下载](https://github.com/TshineZheng/YBA-AMS-ESP-PY/releases)

## 使用
唯一的区别是配网, 微信小程序搜索 **一键配网**

操作步骤：切换协议 > SmartConfig 配网 > 输入 Wifi 密码。

或者下载 `SmartConfig` 相关 App 工具，比如：[EspTouch](https://play.google.com/store/apps/details?id=com.fyent.esptouch.android) ，[EspTouch iOS](https://apps.apple.com/us/app/espressif-esptouch/id1071176700)

## 关于第四通道
1. 需要将原来的 gpio8 更换为 gipo11，如果你的PCB是原版的话需要飞线操作。
2. 既然换了 gpio 则必须更换固件，你可以自行修改原版代码，也可以使用这里的 python版。

下面是新手飞线教程，（技术熟练的大佬请自由发挥）
![](doc/飞线教程.jpg)
