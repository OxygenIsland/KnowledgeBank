---
title: "[[Bootloader跳转后无法启动新的CDC接口]]"
type: Fleeting
status: done
Creation Date: 2026-08-04 10:49
tags:
---
Bootloader 在判断跳转之前，MX_USB_DEVICE_Init() 已经把 USB 作为 DFU 设备启动并让 D+上拉线得电（USBD_Start 里已经建立了一次 USB 枚举）。之后即使满足跳转条件，代码也是直接 JumpToApplication()，没有做任何 USB 断开动作——USB 外设的上拉状态和之前枚举给主机的 DFU 描述符信息都还保留着。

跳转到 APP 后，APP 会重新初始化 USB 为 CDC 设备，但由于主机没有检测到一次真正的"断开→重连"，Windows/主机端驱动可能仍然认为设备是之前枚举的那个（DFU 接口），不会重新枚举，于是新的 CDC 接口起不来，日志自然就看不到。

> [!note]+ USB 连接的基本原理（类比理解）
> USB 数据线里有两根信号线，叫 D+ 和 D-。设备内部有个小开关，可以把 D+ 拉高（这个动作叫"上拉"）。
> 
> 你可以把这个理解成举手示意：
> 
> 设备把 D+ 拉高 = "举手"，告诉电脑"有新设备插进来了！"
> 电脑（专业说法叫"主机 Host"）看到有人举手，就会走一套固定流程去"认识"这个新设备：
> 问它"你是谁？"（读取设备描述符）
> 设备回答"我是一个 USB 串口（CDC）"或者"我是一个升级设备（DFU）"
> 电脑根据回答，加载对应的驱动，比如给 CDC 设备开一个虚拟串口(COM口)
> 这个"举手 → 问答 → 电脑认出设备类型并加载驱动"的完整过程，就叫枚举（Enumeration）。

Bootloader 在还没确定要不要跳转之前，就已经无条件执行了 MX_USB_DEVICE_Init()，把自己"举手"变成了 DFU 设备，电脑已经认过一次了。等真正跳到 APP、APP 想重新举手变成 CDC 串口时，D+ 这根线其实从头到尾都没有放下过——对电脑来说，它没有观察到"设备拔出/插入"这个物理事件，所以根本不会重新走一遍"问你是谁"的流程，也就一直用着旧的（DFU）身份认知，看不到新出现的串口。

## FIX
```c
USBD_DeInit(&hUsbDeviceHS);   // 主动把 D+ 拉低，相当于"先拔线"
HAL_Delay(200);                // 保持"拔线"状态一段时间，让电脑真的反应过来
```
- [USBD_DeInit()](vscode-file://vscode-app/d:/Users/liubo32/AppData/Local/Programs/Microsoft%20VS%20Code/e4c7e7b1d6/resources/app/out/vs/code/electron-browser/workbench/workbench.html)：这是 USB 驱动库提供的"反初始化"函数，作用就是把 D+ 的上拉开关关掉，相当于**主动告诉电脑"这个设备不见了"**。
- `HAL_Delay(200)`：这里的关键是——电脑检测"设备被拔出"也需要一点反应时间（不是瞬间的），如果拔了又立刻插回去，电脑可能反应不过来。所以特意等 200 毫秒，确保电脑确实处理完了"设备消失"这件事。
- 之后再跳到 APP，APP 重新调用 MX_USB_DEVICE_Init() 把 D+ 重新拉高 = "举手"，电脑这时候才会认为"啊，有个新设备插进来了"，重新走一遍完整的问答流程，这次问出来的答案是"我是 CDC 串口"，于是就正确加载了串口驱动，日志也就能正常显示了。