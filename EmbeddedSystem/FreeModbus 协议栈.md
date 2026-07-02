---
title: "[[FreeModbus 协议栈]]"
type: Reference
status: ing
Creation Date: 2026-07-01 16:24
tags:
---
## 一、先搞懂 Modbus 协议本身
### 1.1 Modbus 是什么
Modbus 是一种**工业现场通信协议**，1979 年由 Modicon 提出，简单、开放、免费，现在是工业设备之间通信的事实标准。
一句话理解：**它规定了"谁问、怎么问、答什么"的一套规则**，让不同厂家的设备能互相读写数据。

### 1.2 主站 / 从站（Master / Slave）
Modbus 是典型的**一问一答（请求-响应）**模型：
```
主站 (Master) ──── 请求 ───▶ 从站 (Slave)

主站 (Master) ◀─── 响应 ──── 从站 (Slave)
```
- **主站（Master）**：主动发起请求的一方（"我要读你的第 3 号寄存器"）。
- **从站（Slave）**：被动等待、收到请求才回应的一方。
- 从站有唯一的**地址（Slave Address，1~247）**，主站靠这个地址点名要跟谁通信。
- 地址 **0 是广播地址**：主站发广播时，所有从站都执行但**都不回应**（所以广播只能用来"写"，不能用来"读"）。

> 关键点：**从站永远不会主动说话**，只能被问了才答。这也是为什么主站要不停地轮询各个从站。

> [!tip]+ 寄存器
> Modbus 的"寄存器"不是硬件寄存器，它只是内存里一个数组的下标（索引）。所谓"3 号寄存器"，本质就是 usSRegHoldBuf[3] 这个数组元素
> 在从站（STM32）代码里，"保持寄存器"就是这么一个数组（[user_mb_app.c](vscode-file://vscode-app/d:/Users/liubo32/AppData/Local/Programs/Microsoft%20VS%20Code/7e7950df89/resources/app/out/vs/code/electron-browser/workbench/workbench.html)）：
> ```c
> // 一个能放 100 个 16 位数的数组，就这么普通
USHORT usSRegHoldBuf[100];
//         ↑ 下标 0    下标 1   下标 2   下标 3 ...  就是"0号/1号/2号/3号寄存器"
> ```
> 所以**"3 号寄存器" = `usSRegHoldBuf[3]`**。没有任何魔法，没有任何硬件绑定。它现在就是一格 RAM 内存。
> 
> 协议栈（FreeModbus）根本不知道、也不关心 3 号寄存器是什么意思。 它只负责把 usSRegHoldBuf[3] 这个数字原样搬来搬去。
在本项目中，"3 号 = 开关机状态" ，这个含义是人为约定出来的，主站开发者和从站开发者之间的一个"合同/口头协议"。双方都必须按这张表来写代码：
>- 从站开发者：我保证把"开关机状态"这个值放在 usSRegHoldBuf[3]。
> - 主站开发者：我要控制开关机，就去读/写 3 号寄存器。
>
>** usSRegHoldBuf 是一个普通全局数组**：
>```c
>USHORT usSRegHoldBuf[S_REG_HOLDING_NREGS];   // S_REG_HOLDING_NREGS = 100
>```
>100 个 `USHORT`（16 位）= 200 字节的一块连续内存。开机时被创建，`usSRegHoldBuf[3]` 就是"3 号保持寄存器"。
>**每台物理从机设备（每颗 MCU）都有自己独立的一份。** 因为这数组是编译进每台设备固件里的全局变量，各跑各的。A 从机的 `usSRegHoldBuf[3]` 和 B 从机的 `usSRegHoldBuf[3]` 是两块完全不相干的内存，各存各的开关机状态。主站靠"从站地址"（帧里第一个字节）来区分现在读的是哪台。
>
> 它在 RAM（STM32 的 SRAM）里**，具体说是**全局静态存储区**。含义：
>- 掉电即失。重启后是初值（0 或代码里给的初值）。
>- 如果你想让某些参数掉电保存，得**自己**在写回调里把值额外存进 Flash/EEPROM，Modbus 不管这事。
>
>
>顺带厘清一个容易混的点：
>从站用一维数组 usSRegHoldBuf[地址]——因为它只需存"我自己"的数据。
>主站用二维数组 usMRegHoldBuf[从站号-1][地址]——因为一个主站要替很多台从站保存读回来的数据，多一个维度区分是哪台从站。

> [!example]+ 
> **方向 1：从站把"真实硬件数据" → 写进寄存器数组（让主站能读到）**
> 比如从站要把"当前电池电压"这个真实硬件测量值暴露出去。假设文档约定"10 号寄存器 = 电池电压"，那你在从站的业务代码里这样写：
> ```c
> // 你的某个采集任务里
uint16_t voltage = ADC_ReadBatteryVoltage();   // ← 从真实 ADC 硬件读电压
usSRegHoldBuf[10] = voltage;                    // ← 手动"接线"：塞进 10 号寄存器
> ```
> 之后主站来读 10 号寄存器时，FreeModbus 自动把 `usSRegHoldBuf[10]` 打包发回去。
>
>
> **方向 2：主站写进来的寄存器值 → 去控制真实硬件**
> 比如文档约定"3 号寄存器 = 开关机状态，写 1 就关机"。主站写了 3 号寄存器后，从站的回调 `eMBRegHoldingCB(..., MB_REG_WRITE)` 会自动把值存进 `usSRegHoldBuf[3]`。然后**你要写代码去检查它、并驱动真实硬件**：
> ```c
> // 你的某个控制任务里，轮询检查
>if (usSRegHoldBuf[3] == 1) {          // ← 主站写进来的关机命令
 >   Start_Shutdown_Countdown();       // ← 驱动真实硬件执行关机
>    usSRegHoldBuf[3] = 0;             // ← 按文档要求，关机中自动置 0
>}
> ```

### 1.3 四种数据模型（最核心的概念）
Modbus 把从站里的数据抽象成 **4 张表**，这是理解一切的基础：

| 数据类型  | 英文                | 读写    | 单位         | 类比               |
| :---- | :---------------- | :---- | :--------- | :--------------- |
| 线圈    | Coils             | 读 / 写 | 1 位（bit）   | 开关输出（继电器、LED）    |
| 离散输入  | Discrete Inputs   | 只读    | 1 位（bit）   | 数字输入（按钮、限位开关状态）  |
| 保持寄存器 | Holding Registers | 读 / 写 | 16 位（word） | 可读写参数（设定温度、目标转速） |
| 输入寄存器 | Input Registers   | 只读    | 16 位（word） | 只读测量值（当前温度、当前电压） |

记忆法：
- **"线圈/寄存器"可读可写；"离散输入/输入寄存器"只读。**
- **"线圈/离散"是 1 位；"寄存器"是 16 位。**
每张表内部都是按**地址**编号的（0、1、2……），主站读写时都要指定"读哪张表、从哪个地址开始、读几个"。

### 1.4 功能码（Function Code）
主站请求里有一个字节叫**功能码**，表示"要对哪张表做什么操作"。常用的有：

| 功能码  | 操作       | 对应数据表             |
| :--- | :------- | :---------------- |
| 0x01 | 读线圈      | Coils             |
| 0x02 | 读离散输入    | Discrete Inputs   |
| 0x03 | 读保持寄存器   | Holding Registers |
| 0x04 | 读输入寄存器   | Input Registers   |
| 0x05 | 写单个线圈    | Coils             |
| 0x06 | 写单个保持寄存器 | Holding Registers |
| 0x0F | 写多个线圈    | Coils             |
| 0x10 | 写多个保持寄存器 | Holding Registers |

### 1.5 传输模式：RTU / ASCII / TCP

- **Modbus RTU**：走串口（RS485/RS232），数据是**二进制**，紧凑高效，用 **CRC16** 校验。**工业上最常用，本工程就是用它。**
- **Modbus ASCII**：走串口，数据是**可见 ASCII 字符**，可读但效率低，用 LRC 校验。
- **Modbus TCP**：走以太网，去掉了 CRC（TCP 自己保证可靠），加了报文头。

### 1.6 一帧 RTU 报文长什么样
以"主站读从站保持寄存器"为例：
**请求帧（主站 → 从站）：**
```
┌─────────┬─────────┬─────────────────┬──────────────────┬─────────────┐
│ 从站地址 │ 功能码  │  起始地址(2字节) │  寄存器数量(2字节) │ CRC(2字节)  │
├─────────┼─────────┼─────────────────┼──────────────────┼─────────────┤
│  0x01   │  0x03   │  0x00 0x00      │  0x00 0x02       │ CRC_L CRC_H │
└─────────┴─────────┴─────────────────┴──────────────────┴─────────────┘
   含义：请 1 号从站，从保持寄存器地址 0 开始，读 2 个寄存器
```

> [!note]+ 起始地址是什么
> 这里的**"起始地址"就是"寄存器编号"本身**，它不是任何硬件物理地址。但它的实际含义就是"第几号寄存器"，等价于数组下标。
> 
> 看你工程主站发送代码（mbfuncholding_m.c），亲眼看它怎么把编号塞进帧：
>```c
>eMBMasterReqWriteHoldingRegister(this, ucSndAddr, usRegAddr, usRegData, lTimeOut)
{
 >   ...
>    ucMBFrame[MB_PDU_REQ_WRITE_ADDR_OFF]     = usRegAddr >> 8;  // 编号的高字节
>    ucMBFrame[MB_PDU_REQ_WRITE_ADDR_OFF + 1] = usRegAddr;       // 编号的低字节
>    ...
>}
>```
>如果你 `usRegAddr` 传 3，帧里那两个字节就是 `00 03`。**就是直接发编号，跟你想的一模一样。** 没有任何物理地址转换。
>
>那为什么叫"**起始**地址（Starting Address）而不只叫"地址"？因为 Modbus 一次请求可以**连续读/写多个寄存器**，所以帧里是"**起始地址 + 数量**"这一对，用来表示一段连续区间：
>- 起始地址 = 0，数量 = 5   →  读 0、1、2、3、4 号，共 5 个寄存器
>- 起始地址 = 3，数量 = 1   →  只读 3 号这一个

**响应帧（从站 → 主站）：**
```
┌─────────┬────────┬──────────┬─────────────────┬─────────────────┬──────────────┐
│ 从站地址 │ 功能码 │   字节数  │  寄存器1(2字节)  │  寄存器2(2字节)  │ CRC(2字节)   │
├─────────┼────────┼──────────┼─────────────────┼──────────────────┼─────────────┤
│  0x01   │  0x03  │   0x04   │  0x00 0x0A      │  0x01 0x2C       │ CRC_L CRC_H │
└─────────┴────────┴──────────┴─────────────────┴──────────────────┴─────────────┘
   含义：地址0的值=0x000A(10)，地址1的值=0x012C(300)
```

> RTU 靠**帧间静默时间（3.5 个字符时间）**来判断一帧结束，所以底层需要一个精确定时器来测这个间隔。这就是为什么协议栈移植时要用到一个硬件定时器。  

## 二、FreeModbus 协议栈是什么
FreeModbus 是一个**开源的 Modbus 协议栈实现**（C 语言写的），把上面那些"组帧、拆帧、CRC 校验、状态机、超时管理"这些又繁琐又容易出错的活儿全帮你做好了。你只需要：
1. 把它**移植**到你的硬件上（告诉它用哪个串口、哪个定时器）。
2. 在**回调函数**里告诉它"你的数据放在哪个数组里"。
3. 调用几个 **API** 就能收发数据。

> 官方开源版**只有从机**免费，**主机代码要收费**。本工程用的是 **Armink 改进的 V1.6 版本**，主机、从机都开源，而且支持"同一个协议栈同时跑主机和从机""支持 RTOS""支持多实例"。

### 2.1 三层结构（心智模型）
```
┌─────────────────────────────────────────────┐
│  应用层  你的业务代码（freertos.c 里的任务）   │
│  · 调用 eMBMasterReqXxx() 发请求             │
│  · 在回调里读写你的数据数组                   │
├─────────────────────────────────────────────┤
│  协议层  FreeModbus 核心（modbus/ 目录，别动）│
│  · 组帧/拆帧、CRC、功能码分发、状态机、超时    │
├─────────────────────────────────────────────┤
│  移植层  port/ 目录（对接你的芯片）           │
│  · 串口收发中断、定时器中断、485 方向控制      │
└─────────────────────────────────────────────┘
```
**你日常主要打交道的只有最上面的"应用层"和 `port/user_mb_app*.c` 里的回调。中间的协议层是黑盒，不要改。**

### 2.2 本工程的目录结构
```
APP/BSP/FreeModbus/
├── modbus/          ← 协议核心（黑盒，不要改）
│   ├── mb.c             从机对外接口（eMBInit/eMBEnable/eMBPoll）
│   ├── mb_m.c           主机对外接口（eMBMasterInit/.../eMBMasterReqXxx）
│   ├── functions/       各功能码的处理逻辑（读写线圈/寄存器）
│   ├── rtu/             RTU 模式状态机 + CRC
│   └── include/         头文件（mb.h / mb_m.h 是你要 include 的）
├── port/            ← 移植层（对接硬件，偶尔改）
│   ├── portserial*.c    串口收发移植
│   ├── porttimer*.c     定时器移植
│   ├── user_mb_app.c    【从机】数据缓冲区 + 4个回调函数
│   ├── user_mb_app_m.c  【主机】数据缓冲区 + 4个回调函数
│   └── user_mb_app.h    【重点】寄存器/线圈的数量、地址宏定义
└── mbStack/         ← 本版特有：把协议栈打包成"句柄结构体"，实现多实例
```
> `_m` 后缀 = master（主机）。没有 `_m` 的就是 slave（从机）。

## 三、本工程是怎么用的（结合真实代码）
本工程比较特殊：它同时开了 **4 个主站 + 1 个从站**，每个都是独立实例（独立串口、独立定时器）。这靠的就是"多实例"特性——每个协议栈是一个**结构体句柄**。
### 3.1 句柄（每个 Modbus 实例 = 一个结构体变量）
`freertos.c` 里：
```c
extern MB_M_StackTypeDef mbMasterStack;    // 主站1
extern MB_M_StackTypeDef mbMasterStack2;   // 主站2
extern MB_M_StackTypeDef mbMasterStack3;   // 主站3
extern MB_M_StackTypeDef mbMasterStack4;   // 主站4

// (从站是 mbStack，类型 MB_StackTypeDef)
```
每个句柄里存着：用哪个串口、485 方向脚是哪个、用哪个定时器等。

### 3.2 一个主站任务的完整流程
看 `MB_Master_poll` 这个 FreeRTOS 任务（`freertos.c`）：
```c
void MB_Master_poll(void *argument)
{
    // ① 配置硬件：这个主站用 UART4，485 方向脚 UART4_DIR，定时器 htim6
    mbMasterStack.hardware.max485.phuart   = &huart4;
    mbMasterStack.hardware.max485.dirPin   = UART4_DIR_Pin;
    mbMasterStack.hardware.max485.dirPort  = UART4_DIR_GPIO_Port;
    mbMasterStack.hardware.phtim           = &htim6;

    // ② 初始化：RTU 模式，本机地址 4，波特率 9600，无校验
    eMBMasterInit(&mbMasterStack, MB_RTU, 4, 9600, MB_PAR_NONE);

    // ③ 使能协议栈（打开串口中断、启动状态机）
    eMBMasterEnable(&mbMasterStack);

    // ④ 死循环里不停轮询——这是协议栈的"心跳"，必须一直调
    for(;;)
    {
        eMBMasterPoll(&mbMasterStack);
        osDelay(10);
    }
}
```

**四步套路：配置硬件 → Init → Enable → 循环 Poll。** 从站也是一样的套路（用 `eMBInit / eMBEnable / eMBPoll`）。
> `eMBXxxPoll()` 是整个状态机往前推进的动力。**只要漏调用了，收发就全停了。** 它必须放在循环里高频调用。


> [!question]+ 为什么要先配置硬件
> 因为 **FreeModbus 的核心代码是"通用的、不认识任何具体硬件"的**，它必须靠你告诉它"这个实例到底用哪个串口、哪个定时器、哪个方向脚"。
> `mbMasterStack` 的内部代码写的是"往 `hardware.max485.phuart` 指向的串口发数据"，但**具体是哪个串口，得你填进来它才知道**：
> ```c
> mbMasterStack.hardware.max485.phuart  = &huart4;          // 用 UART4 收发
>mbMasterStack.hardware.max485.dirPin  = UART4_DIR_Pin;    // 485 方向脚
>mbMasterStack.hardware.max485.dirPort = UART4_DIR_GPIO_Port;
>mbMasterStack.hardware.phtim          = &htim6;           // 判帧用的定时器
> ```
> - `phuart`：实际收发字节走哪个 UART。
>- `dirPin/dirPort`：RS485 半双工，发送前要拉高这个脚切到"发送"，发完拉低回"接收"。
>- `phtim`：RTU 靠"3.5 字符静默"判断一帧结束，用这个定时器来量这个时间间隔。
>

> [!note]+ eMBMasterPoll作用
> 只要线上来了一个字节，UART 硬件自动触发中断，在中断函数里把这个字节喂给协议栈的接收状态机
> ```c
> void UART4_IRQHandler(void) {
>    if (收到一个字节) 
>        mbMasterStack.peMBMasterFrameCBByteReceivedCur(&mbMasterStack); // 收进来
 >   ...
>}
> ```
> 这个过程**完全由硬件驱动，Poll 一次都不用调也照收不误**。字节一个一个进来，攒着。
>
>然后定时器中断发现"线路静默超过 3.5 字符时间了 → 一帧收完了"，就往一个**事件队列**里丢一个事件 `EV_MASTER_FRAME_RECEIVED`（"有一帧收好了，谁来处理下"）。
>
>
**eMBMasterPoll = 处理事件的活（消费者）**
>
`eMBMasterPoll` **根本不碰线路、不查串口**。它只干一件事：**看那个事件队列里有没有待办事件，有就处理，没有就立刻返回。** 看你工程 [mb.c](vscode-file://vscode-app/d:/Users/liubo32/AppData/Local/Programs/Microsoft%20VS%20Code/7e7950df89/resources/app/out/vs/code/electron-browser/workbench/workbench.html) 里 Poll 的真实逻辑：
>```c
>eMBErrorCode eMBPoll(void *this) {
>    // 就是问一句：事件队列里有东西吗？
>    if (xMBPortEventGet(..., &eEvent) == TRUE) {
>        switch (eEvent) {
>            case EV_FRAME_RECEIVED:   // 哦，有一帧收好了
>                解析这帧 → 调用你的回调 → 存数据;
>                break;
>            ...
>        }
>    }
>    // 没事件？那就啥也不干，直接 return
>}
>```

### 3.3 主站怎么发一次请求（读/写从站）
在任务循环里（或其它任务里），调用请求 API。常用的几个（在 `mb_m.h`）：
```c
// 写单个保持寄存器：给 3 号从站，地址 0，写入 100，超时 1000ms
eMBMasterReqWriteHoldingRegister(&mbMasterStack, 3, 0, 100, 1000);

// 写多个保持寄存器
eMBMasterReqWriteMultipleHoldingRegister(&mbMasterStack, 3, 0, 2, pDataBuf, 1000);

// 读保持寄存器：读 3 号从站，从地址 0 开始，读 5 个，超时 1000ms
eMBMasterReqReadHoldingRegister(&mbMasterStack, 3, 0, 5, 1000);

// 读输入寄存器
eMBMasterReqReadInputRegister(&mbMasterStack, 3, 0, 5, 1000);

// 写单个线圈
eMBMasterReqWriteCoil(&mbMasterStack, 3, 0, 0xFF00, 1000);  // 0xFF00=ON, 0x0000=OFF
```

请求 API 的通用返回值（判断是否成功）：

| 返回值                  | 含义           |
| :------------------- | :----------- |
| `MB_MRE_NO_ERR`      | 成功           |
| `MB_MRE_NO_REG`      | 地址错误         |
| `MB_MRE_ILL_ARG`     | 参数错误         |
| `MB_MRE_REV_DATA`    | 接收数据出错       |
| `MB_MRE_TIMEDOUT`    | 超时（从站没回应）    |
| `MB_MRE_MASTER_BUSY` | 主机忙（没抢到资源发送） |
| `MB_MRE_EXE_FUN`     | 处理响应时出错      |
  
> 请求 API 是**阻塞的、线程安全的**：调用后会一直等到"拿到结果"或"超时"才返回。所以适合放在独立的 FreeRTOS 任务里跑。

**重要：读回来的数据去哪了？** —— 不是靠返回值拿数据，而是协议栈收到响应后，**自动调用回调函数**把数据写进你的数组。你之后从数组里读即可（见下一节）。
### 3.3 从站实现案例
#### 第一步：在 `user_mb_app.h` 里定义地址宏
```c
/* salve mode: holding register's all address */
#define S_HD_HOUR           0   // 小时 (0-65535)，读写
#define S_HD_MIN            1   // 分钟 (0-59)，读写
#define S_HD_SEC            2   // 秒   (0-59)，读写
#define S_HD_POWER_STATE    3   // 开关机状态：1=执行软关机，读写
#define S_HD_BOOT_TYPE      4   // 启动类型：0=冷启动，1=热启动，读写
```
> 地址宏只是给自己用的"可读别名"，和 Modbus 报文里的地址数字一一对应，**不需要改协议栈任何东西**。
#### 第二步：在业务代码里更新缓冲区
把你的业务数据写进 `usSRegHoldBuf[]`，主站来读时协议栈会自动把这个数组里的值发出去。
```c
// 示例：RTC 定时任务，每秒把当前时间刷新到缓冲区
void vSlave_UpdateTimeTask(void *argument)
{
    RTC_TimeTypeDef sTime;
    RTC_DateTypeDef sDate;
    for (;;)
    {
        HAL_RTC_GetTime(&hrtc, &sTime, RTC_FORMAT_BIN);
        HAL_RTC_GetDate(&hrtc, &sDate, RTC_FORMAT_BIN);  // 必须读 Date，否则 Time 不更新
        // 直接写进寄存器缓冲区，主站来读时回调函数会自动把它发出去
        usSRegHoldBuf[S_HD_HOUR] = sTime.Hours;
        usSRegHoldBuf[S_HD_MIN]  = sTime.Minutes;
        usSRegHoldBuf[S_HD_SEC]  = sTime.Seconds;

        // S_HD_POWER_STATE 和 S_HD_BOOT_TYPE 由其他业务逻辑写入
        osDelay(1000);
    }
}
```
#### 第三步：在回调里响应主站的"写"操作
`eMBRegHoldingCB` 在 `user_mb_app.c` 里已经帮你写好了通用模板（把数据拷进/拷出数组）。**你只需要在回调之后（或回调内部）检测业务寄存器是否被修改**，然后触发对应动作：
```c
// 方式一（推荐）：在业务任务里轮询寄存器，检测变化后处理
void vSlave_MonitorTask(void *argument)
{
    for (;;)
    {
        // 主站写 S_HD_POWER_STATE=1 → 触发软关机
        if (usSRegHoldBuf[S_HD_POWER_STATE] == 1)
        {
            usSRegHoldBuf[S_HD_POWER_STATE] = 0;  // 清标志，避免反复触发
            // 执行软关机逻辑……
            StartShutdownCountdown();
        }

        // 主站写了新时间 → 同步 RTC
        // （此处可加 dirty flag 机制，避免每次都写 RTC）
        osDelay(100);
    }
}
```

  

```c
// 方式二：直接在 eMBRegHoldingCB 的 MB_REG_WRITE 分支末尾加钩子

// （适合实时性要求高的场景，但注意回调在中断/协议栈上下文里，不要做耗时操作）
case MB_REG_WRITE:
    while (usNRegs > 0)
    {
        pusRegHoldingBuf[iRegIndex] = *pucRegBuffer++ << 8;
        pusRegHoldingBuf[iRegIndex] |= *pucRegBuffer++;
        iRegIndex++;
        usNRegs--;
    }

    // 写完后通知业务任务（用信号量/事件组，不要直接操作外设）
    osSemaphoreRelease(xSlaveWriteSem);
    break;
```

#### 第四步：初始化从站并启动轮询
```c
void MB_Slave_poll(void *argument)
{
    // ① 配置硬件：从站用 UART2，485 方向脚，定时器 htim7
    mbStack.hardware.max485.phuart  = &huart2;
    mbStack.hardware.max485.dirPin  = UART2_DIR_Pin;
    mbStack.hardware.max485.dirPort = UART2_DIR_GPIO_Port;
    mbStack.hardware.phtim          = &htim7;

    // ② 初始化：RTU 模式，本机从站地址 3，波特率 9600，无校验
    eMBInit(&mbStack, MB_RTU, 3, 9600, MB_PAR_NONE);

    // ③ 设置初始值（可选）
    usSRegHoldBuf[S_HD_BOOT_TYPE]   = 1;  // 默认热启动

    // ④ 使能
    eMBEnable(&mbStack);
  
    // ⑤ 循环轮询（必须一直调，这是协议栈的心跳）
    for (;;)
    {
        eMBPoll(&mbStack);
        osDelay(5);
    }
}
```

#### 数据流总结
```
    主站 MB 发送请求                         PB 从站处理
    ─────────────────                       ──────────────────────────────────
    03 03 00 00 00 05 84 2B  ──串口──▶  eMBPoll() 接收并解析帧
                                              │
                                              ▼ 自动调用
                                        eMBRegHoldingCB(..., MB_REG_READ)
                                              │ 从 usSRegHoldBuf[] 拷贝数据
                                              ▼
    03 03 0A [时 分 秒 状态 类型] CRC  ◀──串口──  发出响应帧

    03 10 00 00 00 04 ... CRC  ──串口──▶  eMBPoll() 解析帧
                                              │
                                              ▼ 自动调用
                                        eMBRegHoldingCB(..., MB_REG_WRITE)
                                              │ 写入 usSRegHoldBuf[]
                                              ▼
                                        业务任务检测到 S_HD_POWER_STATE=1
                                        → 触发软关机
```

## 四、数据缓冲区与回调（新手最容易懵的地方）
FreeModbus 的数据流是"**协议栈 ⇄ 你的数组**"，中间的桥梁就是 **4 个回调函数**。
### 4.1 缓冲区在哪定义、有多大
大小在 `port/user_mb_app.h` 里用宏定义（本工程的从站配置）：
```c
/* 从站 Slave */
#define S_COIL_NCOILS          64    // 64 个线圈
#define S_DISCRETE_INPUT_NDISCRETES 16    // 16 个离散输入
#define S_REG_INPUT_NREGS      100   // 100 个输入寄存器
#define S_REG_HOLDING_NREGS    100   // 100 个保持寄存器
  
/* 主站 Master */
#define M_REG_HOLDING_NREGS    320   // 主站侧保持寄存器缓冲
```

对应的数组在 `user_mb_app.c` / `user_mb_app_m.c` 顶部定义，例如从站：
```c
USHORT usSRegHoldBuf[S_REG_HOLDING_NREGS];  // 保持寄存器数组
UCHAR  ucSCoilBuf[S_COIL_NCOILS/8];         // 线圈（1位1个，8个挤1字节）
```

  
> **从站用一维数组**（自己的数据）。
> **主站用二维数组** `usMRegHoldBuf[从站号][寄存器地址]`，因为一个主站要存很多个从站的数据。注意行号要"从站ID减1"，例如 `usMRegHoldBuf[2][1]` = 3 号从站的地址 1 寄存器。

  
### 4.2 四个回调函数（你要实现的接口）

| 从站回调               | 主站回调                     | 负责的数据表 |
| :----------------- | :----------------------- | :----- |
| `eMBRegInputCB`    | `eMBMasterRegInputCB`    | 输入寄存器  |
| `eMBRegHoldingCB`  | `eMBMasterRegHoldingCB`  | 保持寄存器  |
| `eMBRegCoilsCB`    | `eMBMasterRegCoilsCB`    | 线圈     |
| `eMBRegDiscreteCB` | `eMBMasterRegDiscreteCB` | 离散输入   |

**它们什么时候被调用？谁调的？**——协议栈内部自动调，你**永远不要手动调**它们。

以从站的保持寄存器为例（`user_mb_app.c` 已经帮你写好了模板）：
- 当**主站来读**你的保持寄存器时，协议栈自动调 `eMBRegHoldingCB(..., MB_REG_READ)`，函数把 `usSRegHoldBuf[]` 里的值拷进发送缓冲。
- 当**主站来写**你的保持寄存器时，协议栈自动调 `eMBRegHoldingCB(..., MB_REG_WRITE)`，函数把收到的数据写进 `usSRegHoldBuf[]`。

```c
eMBErrorCode eMBRegHoldingCB(UCHAR *pucRegBuffer, USHORT usAddress,
                             USHORT usNRegs, eMBRegisterMode eMode)
{
    usAddress--;  // 协议里地址从1算，数组从0算，所以减1
    if (地址在合法范围内) {
        if (eMode == MB_REG_READ)  {  从数组读 → 填进 pucRegBuffer（回给主站）  }
        else /* MB_REG_WRITE */    {  从 pucRegBuffer 取 → 写进数组  }
    }
    return MB_ENOERR;
}
```

**所以你的业务代码要做的其实很简单：**
- 从站侧：平时往 `usSRegHoldBuf[]`、`usSRegInBuf[]` 里更新数据，主站来读时协议栈自动把它发出去。
- 主站侧：调 `eMBMasterReqReadXxx()` 发读请求，返回成功后，去 `usMRegHoldBuf[从站-1][地址]` 里拿读回来的值。

> 16 位寄存器在 Modbus 里是**大端序（高字节在前）**，回调模板里的 `>>8` 和 `&0xFF` 就是在做大小端拆分，照抄即可。

## 五、移植层：协议栈是怎么接到硬件上的

这部分本工程已经移植好了，理解即可，一般不用改。核心是三件事：
### 5.1 串口收发（中断驱动）
在 `stm32f4xx_it.c` 的串口中断里，把"收到一个字节" "发送寄存器空" 这两个事件转交给协议栈：
```c
void UART4_IRQHandler(void)   // 某个主站的串口
{
    // 收到一个字节 → 交给协议栈接收状态机
    if (收到数据中断)  mbMasterStack.peMBMasterFrameCBByteReceivedCur(&mbMasterStack);

    // 发送寄存器空 → 交给协议栈继续发下一个字节
    if (发送空中断)    mbMasterStack.peMBMasterFrameCBTransmitterEmptyCur(&mbMasterStack);
    HAL_UART_IRQHandler(&huartX);
}
```
  
### 5.2 定时器（测 RTU 帧间隔）
RTU 靠 3.5 字符静默判断一帧结束，需要一个 ~50µs 分辨率的定时器。定时中断里通知协议栈"该判帧了"（`main.c` 的 `HAL_TIM_PeriodElapsedCallback`）：
```c
if (htim == &htim6)  mbMasterStack.peMBMasterPortCBTimerExpiredCur(&mbMasterStack);
```

> [!question]+ 为什么 RTU 需要用定时器判断"一帧结束"？
> **串口通信时，从站一直往线上发字节，主站怎么知道"这些字节是一帧"，还是"上一帧结束、下一帧开始了"？**
>
>TCP/IP 里报文有长度字段，协议栈知道"还差几个字节"。但 Modbus RTU 的串口上没有"帧开始"信号，字节一个一个光秃秃地来，中间没有分隔符。
>
**RTU 的解法是：靠"沉默时间"划分帧边界。** 约定如下：
>
> **一帧内**相邻两个字节之间，间隔很短（< 1.5 个字符时间）。  
> **两帧之间**，必须有 ≥ 3.5 个字符时间的"静默"（线上没有任何字节）。  
> 只要检测到"超过 3.5 字符时间没有收到新字节" → 判定"上一帧已经完整结束了"。
>
定时器的唯一职责就是**量这段静默时间够不够 3.5 个字符那么长**。

#### "3.5 个字符时间"到底是多久？

**"字符时间"= 串口发送 1 个字节需要多长时间**，这取决于**波特率**。

波特率 9600 bps，Modbus RTU 每个字符是 11 位（1起始位 + 8数据位 + 1停止位 + 1校验/停止位）：
$$1\text{个字符时间} = \frac{11\text{位}}{9600\text{bps}} \approx 1145\mu s \approx 1.15\text{ms}$$
$$3.5\text{个字符时间} = 3.5 \times 1145\mu s \approx 4\text{ms}$$
> 所以 9600 bps 下，帧间的静默只要超过约 **4ms**，就判定上一帧结束了。  
> 波特率越高，字符时间越短，这个静默窗口就越小，所以需要定时器分辨率越高（~50µs）。
### 5.3 RS485 方向控制
RS485 半双工，同一时刻只能收或发。发送前把方向脚拉高（发送使能），发完拉低（回到接收）。这就是句柄里配 `dirPin/dirPort` 的原因，切换动作协议栈移植层已自动处理。

## 六、快速上手清单（照着做）
### 我要在从站上新增一个"可被主站读写的参数"
1. 在 `user_mb_app.h` 里确认 `S_REG_HOLDING_NREGS` 够大（不够就调大）。
2. 给这个参数分配一个地址宏，例如 `#define S_HD_MY_PARAM 3`。
3. 在你的业务代码里读写 `usSRegHoldBuf[S_HD_MY_PARAM]` 即可。主站读写会自动同步。

### 我要让主站去读某个从站的数据
1. 在主站任务里调用：
   ```c
   eMBMasterReqErrCode err =
       eMBMasterReqReadHoldingRegister(&mbMasterStack, 从站地址, 起始地址, 数量, 1000);
   ```
2. 判断 `err == MB_MRE_NO_ERR`。
3. 成功后从 `usMRegHoldBuf[从站地址-1][起始地址]` 取值。

### 排查"通信不通"时先看这几点
- [ ] 主/从**波特率、校验、停止位**是否一致？（本工程 9600 / N / 1）
- [ ] 从站**地址**是否和主站请求的地址一致？
- [ ] `eMBXxxEnable()` 调了吗？`eMBXxxPoll()` 在循环里一直在跑吗？
- [ ] 串口中断、定时器中断的回调是否正确转接到了对应句柄？
- [ ] RS485 **A/B 接线**是否接反？方向脚是否正常翻转？
- [ ] 请求的地址/数量是否超出了 `user_mb_app.h` 里定义的范围？（会返回 `MB_MRE_NO_REG`）
- [ ] 返回 `MB_MRE_TIMEDOUT`：多半是没接通/从站没在跑/接线问题。

## 七、核心 API 速查表
  
### 从站（Slave）

| API                                                                  | 作用       |
| :------------------------------------------------------------------- | :------- |
| `eMBInit(&stack, MB_RTU, 地址, port, 波特率, 校验)`                         | 初始化      |
| `eMBEnable(&stack)`                                                  | 使能       |
| `eMBPoll(&stack)`                                                    | 轮询（循环里调） |
| `eMBRegHoldingCB / eMBRegInputCB / eMBRegCoilsCB / eMBRegDiscreteCB` | 4 个数据回调  |
  
### 主站（Master）

| API                                                                              | 作用       |
| :------------------------------------------------------------------------------- | :------- |
| `eMBMasterInit(&stack, MB_RTU, 地址, 波特率, 校验)`                                     | 初始化      |
| `eMBMasterEnable(&stack)`                                                        | 使能       |
| `eMBMasterPoll(&stack)`                                                          | 轮询（循环里调） |
| `eMBMasterReqReadHoldingRegister(...)`                                           | 读保持寄存器   |
| `eMBMasterReqWriteHoldingRegister(...)`                                          | 写单个保持寄存器 |
| `eMBMasterReqWriteMultipleHoldingRegister(...)`                                  | 写多个保持寄存器 |
| `eMBMasterReqReadInputRegister(...)`                                             | 读输入寄存器   |
| `eMBMasterReqReadCoils / eMBMasterReqWriteCoil / eMBMasterReqWriteMultipleCoils` | 线圈操作     |
| `eMBMasterReqReadDiscreteInputs(...)`                                            | 读离散输入    |

## 八、一图总结
```

        【主站视角】                               【从站视角】
   你的任务代码                                    你的任务代码
        │ 调用 eMBMasterReqReadHoldingRegister        ▲ 读写 usSRegHoldBuf[]
        ▼                                            │
  ┌──────────────┐    RTU 请求帧(串口/485)     ┌──────────────┐
  │ 主站协议栈     │ ───────────────────────▶  │  从站协议栈   │
  │ (eMBMasterPoll)│ ◀─────────────────────── │ (eMBPoll)     │
  └──────────────┘    RTU 响应帧               └──────────────┘
        │ 收到响应，自动调回调                         │ 收到请求，自动调回调
        ▼                                            ▼
  usMRegHoldBuf[从站][地址]                    eMBRegHoldingCB() ⇄ usSRegHoldBuf[]
   （你从这里取数据）
```