复刻 [YBA-AMS-ESP](https://github.com/YBA0312/YBA-AMS-ESP/tree/main) 固件，调整缓冲器为单个。

## 固件
到 [Release页面](https://github.com/TshineZheng/YBA-AMS-ESP-PY/releases/) 页面，下载 single_buffer_****.bin


## 接线调整

| 功能   | 对应原版 | GPIO |
| ---- | ---- | ---- |
| 进料缓冲 | SW1U | 7    |
| 退料缓冲 | SW2U | 5    |
| 断料检测 | SW3U | 4    |

## 接线

单缓冲版每个通道只需要接马达即可，再接上对应的缓冲微动，若需要断料检测功能则再增加一个断料检测微动。

## 使用

* 理论上原上位机也可以使用本固件（未测试），需要更完善的功能则建议使用 [Filamentor](https://github.com/TshineZheng/Filamentor) ，比如断料检测。

* 缓冲器模型选择有两个开关的。比如：[双向缓冲器](https://makerworld.com/zh/models/507573#profileId-423335)

* 断料检测器只要一个开关，比如：[超顺滑低成本断料检测器](https://makerworld.com/zh/models/515238#profileId-431512)

* 连网和四通道说明参考 [主干版本](https://github.com/TshineZheng/YBA-AMS-ESP-PY)