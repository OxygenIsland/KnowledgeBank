---
title: "[[UART(通用异步收发器)]]"
type: Permanent
status: ing
Creation Date: 2026-06-14 19:11
tags:
---
Universal Asynchronous Receiver Transmitter 即通用异步收发器，是一种通用的串行、[[通信基础#异步通信|异步通信]]总线，该总线有两条数据线。可以实现[[通信基础#全双工通信|全双工]]的发送和接收，在嵌入式系统中常用于主机于辅助设备之间的通信
## 一、为什么需要 UART？
### 1.1 芯片之间怎么"说话"？
两台电脑之间可以通过网络通信；但在嵌入式世界里，芯片与芯片、芯片与模块（蓝牙模组、GPS、传感器）之间，需要一种简单、通用的方式来**传递数据**。

最直觉的方法是：一根线表示一个 bit，"高电平 = 1，低电平 = 0"。  
问题是：如果要传 8 个 bit，就需要 8 根线。这就是**并行通信**——速度快，但线多、占引脚。

更实用的方案是：**用一根线，把数据一位一位地依次发出**。这就是**串行通信**的本质。  
UART 就是串行通信中最基础、最常用的一种。
```
并行通信（8位）：
发送方 ──D7─D6─D5─D4─D3─D2─D1─D0──► 接收方  （8根数据线，同时发完）

串行通信（UART）：
发送方 ──TX──────────────────────►  接收方  （1根线，逐位发送）
接收方 ──RX ◄────────────────────── 发送方  （对向1根线，逐位接收）
```
### 1.2 串行通信的核心问题：同步
把 8 个 bit 一位一位发出去，接收方怎么知道"什么时候一个新字节开始了"、"每个 bit 持续多长时间"？

解决方案分两大类：
- **同步通信**：专门用一根**时钟线（CLK）** 告诉接收方节拍（如 SPI、I2C）
- **异步通信**：收发双方**提前约定好速率**（波特率），靠"开始位/停止位"标记边界，没有时钟线

UART 就是**异步串行通信**，这也是它名字的来源：  
**U**niversal **A**synchronous **R**eceiver/**T**ransmitter（通用**异步**收发器）
> **为什么"异步"是优点？**  
> 少一根线（省引脚），双方可以跨越很长的距离通信，不需要严格同步时序。代价是双方必须提前商量好波特率，稍有误差就乱码。
## 二、UART 是什么？
### 2.1 信号线
最简单的 UART 只需要 **2 根线 + GND**：

| 引脚      | 全称           | 方向  | 说明              |
| ------- | ------------ | --- | --------------- |
| **TX**  | Transmit（发送） | 输出  | 本方发送数据，接到对方的 RX |
| **RX**  | Receive（接收）  | 输入  | 本方接收数据，接到对方的 TX |
| **GND** | 地            | —   | 必须共地，否则电平无法判断   |

> **新手常犯错误**：TX 接 TX，RX 接 RX。正确做法：**TX 接对方 RX，RX 接对方 TX**（交叉连接）。

### 2.2 波特率（Baud Rate）

波特率 = **每秒钟传输的符号（码元）数**，单位 bps（bits per second）。  
常见波特率：9600、19200、38400、115200、460800、921600……

> 本项目调试串口（USART6）用的是 **921600 bps** ——每秒钟发 921600 个 bit，约合每秒 92160 字节。

双方波特率必须**完全一致**（或误差 < 约 2%），否则接收方采样时序错误，收到的就是乱码。

### 2.3 空闲状态
UART 线路在没有数据时，保持**高电平（逻辑 1）**。这是约定好的"静止"状态。
## 三、UART 数据帧结构
每发送一个字节，UART 都遵循固定的帧格式：
```
  空闲   起始位  D0  D1  D2  D3  D4  D5  D6  D7  奇偶  停止位  空闲
   HIGH   LOW    b0  b1  b2  b3  b4  b5  b6  b7   P    HIGH    HIGH
     |     |                                       |      |
     |     └── 起始：强制拉低，接收方据此同步         |      └── 停止：回到高电平
     └── 一直高电平                                 └── 可选校验位
```

| 字段                 | 说明                | 典型配置                  |
| ------------------ | ----------------- | --------------------- |
| **起始位（Start Bit）** | 强制低电平，告诉接收方"数据来了" | 固定 1 bit              |
| **数据位（Data Bits）** | 实际数据，LSB（最低位）先发   | 8 bit（最常用），也有 7/9 bit |
| **奇偶校验位（Parity）**  | 可选，用于简单错误检测       | None（不校验，最常用）         |
| **停止位（Stop Bits）** | 强制高电平，标记帧结束       | 1 bit（最常用），也有 2 bit   |

> 最常见配置简写为 **"8N1"**：8 数据位、无校验、1 停止位。本项目所有串口都是 8N1。
### 3.1 一帧传输时序举例
假设波特率 9600，发送字节 `0x41`（'A' 的 ASCII = 0100 0001）：
```
每个 bit 持续时间 = 1 / 9600 ≈ 104 μs
HIGH ─┐      ┌───┐   ┌───────────────┐   ┌───
      │      │   │   │               │   │
LOW   └──────┘   └───┘               └───┘
      起始位  D0=1 D1=0  D2~D6=0  D7=1 停止位
              (LSB)                  (MSB)
```

## 四、UART / USART / RS232 / RS485 / TTL 串口的关系
这几个词经常混在一起，新手很困惑。用一张表理清层次：
```
┌─────────────────────────────────────────────────────────────┐
│                       应用层协议                             │
│         Modbus RTU / AT指令 / 自定义帧格式 / printf          │
├─────────────────────────────────────────────────────────────┤
│                    通信协议/标准（数字逻辑层）                │
│         UART / USART（异步串行，逻辑协议）                   │
├─────────────────────────────────────────────────────────────┤
│                      物理层（电气标准）                       │
│    TTL（0/3.3V）    RS232（±15V）    RS485（差分信号）        │
└─────────────────────────────────────────────────────────────┘
```

| 名称         | 是什么                        | 电平        | 距离     | 设备数   |
| ---------- | -------------------------- | --------- | ------ | ----- |
| **TTL 串口** | 电气标准：0V = 0，3.3V（或5V）= 1   | 0~3.3V    | <1m    | 1对1   |
| **RS232**  | 电气标准：负电压 = 1，正电压 = 0（反逻辑！） | ±3V～±15V  | <15m   | 1对1   |
| **RS485**  | 电气标准：差分信号（A-B电压判断0/1），抗干扰强 | 差分 ±7V 以内 | <1200m | 最多32个 |
| **UART**   | 通信协议：异步、起始位+数据+停止位         | 取决于物理层    | —      | —     |
| **USART**  | UART 的超集，多了**同步模式**（有时钟线）  | 取决于物理层    | —      | —     |

> **关键理解**：  
> STM32 内部的 UART 外设输出的是 **3.3V TTL 电平**。如果要接 RS232 设备（如老式电脑串口），需要加 **MAX232** 芯片转换电平；如果要走 RS485 总线，需要加 **SP485/MAX485** 芯片转换为差分信号。  

> 本项目中：STM32 的 UART4 → **SP485 芯片** → RS485 总线 → 电池板（Modbus RTU 通信）
## 五、STM32 中的 UART 外设
### 5.1 STM32F405 有哪些 UART？
STM32F405 共有 **6 个串口外设**：

| 外设名     | 挂载总线         | 最高波特率     | 特点                   |
| ------- | ------------ | --------- | -------------------- |
| USART1  | APB2（84 MHz） | 10.5 Mbps | 高速，支持同步模式、硬件流控       |
| USART2  | APB1（42 MHz） | 5.25 Mbps | 支持硬件流控（RTS/CTS）      |
| USART3  | APB1（42 MHz） | 5.25 Mbps | 支持硬件流控               |
| UART4   | APB1（42 MHz） | 5.25 Mbps | 仅异步，无同步/流控           |
| UART5   | APB1（42 MHz） | 5.25 Mbps | 仅异步，TX/RX 跨不同 GPIO 组 |
| USART6  | APB2（84 MHz） | 10.5 Mbps | 高速，与 USART1 同组       |

> **USART vs UART**：USART 多了同步模式（CLK 引脚）和流控（RTS/CTS 引脚）。  
> 实际上，USART 也可以工作在纯异步模式，和 UART 完全一样。  
> HAL 库里两者都用 `UART_HandleTypeDef`，函数也都用 `HAL_UART_xxx`。

### 5.2 UART 内部结构简图
```
                    ┌──────────────────────────────┐
                    │         UART 外设            │
  APB总线 ──────────┤   波特率发生器                │
                    │  ┌────────┐  ┌────────────┐  │
  中断线 ──────────►│   │ 发送器 │  │  接收器    │  │
                    │  │ TX移位 │  │  RX移位    │  │
  DMA请求 ──────────┤   │ 寄存器 │  │  寄存器    │  │
                    │  └───┬────┘  └──────┬─────┘  │
                    └──────┼─────────────┼─────────┘
                           │             │
                          TX引脚        RX引脚
                        （GPIO AF）   （GPIO AF）
```
## 六、引脚的"复用功能"
### 6.1 为什么同一个 GPIO 引脚可以用作 UART？
STM32 的每个 GPIO 引脚内部有一个**多路复用器（MUX）**，可以把引脚的控制权交给不同的内部外设。
```
PA2 引脚内部：
              ┌─── 普通 GPIO 输出（你手动控制电平）
PA2 ──── MUX ─┤─── USART2 TX 信号（外设自动控制电平）
              └─── TIM5_CH3 信号（定时器控制）
                   ...（最多16个AF可选）
```
这些可选的"外设功能"叫做 **复用功能（Alternate Function，AF）**，每个引脚支持哪些 AF 在 datasheet 的"引脚复用表"里写明了。
### 6.2 AF 编号
STM32F405 中，AF 用 AF0～AF15 编号。在 HAL 库里对应 `GPIO_AF0_xxx`～`GPIO_AF15_xxx`。
本项目使用的 UART 引脚与 AF 对应关系（从 usart.c 里读出）：

| 串口      | TX 引脚 | RX 引脚 | AF 编号 |
| ------- | ----- | ----- | ----- |
| USART1  | PB6   | PB7   | AF7   |
| USART2  | PA2   | PA3   | AF7   |
| USART3  | PB10  | PB11  | AF7   |
| UART4   | PC10  | PC11  | AF8   |
| UART5   | PC12  | PD2   | AF8   |
| USART6  | PC6   | PC7   | AF8   |

> 同一个串口可能有多组可选引脚（叫做"引脚重映射"），CubeMX 会帮你选择。  
> 例如 USART1 的 TX 还可以是 PA9，RX 可以是 PA10。
## 七、用 STM32CubeMX 配置 UART
下面以配置 **USART2（PA2=TX，PA3=RX，115200 baud）** 为例，完整讲解步骤。
### 7.1 打开 .ioc 文件
1. 在 VS Code 中用命令行打开，或直接双击 `.ioc` 文件（需安装 STM32CubeMX）。  
   本项目路径：`APP/MX_MB_PVT.ioc`
### 7.2 Pinout & Configuration 页面
#### 步骤 A：在引脚视图上直接配置
1. 找到左侧 **Pinout & Configuration** 标签（默认打开）
2. 在中间的芯片引脚图上，找到 **PA2** 引脚
3. 左键单击 PA2，弹出功能列表
4. 选择 **USART2_TX**
5. 同理，找到 **PA3**，选择 **USART2_RX**

此时引脚变为绿色，表示已分配给外设。

#### 步骤 B：在左侧外设列表配置参数
1. 左侧 **Connectivity** 分类下，找到 **USART2**
2. 点击进入，将 **Mode（模式）** 下拉菜单改为 **Asynchronous（异步）**
   > 其他模式说明：
   > - Asynchronous：最常用，就是普通 UART
   > - Synchronous：同步模式（需要 CLK 引脚），极少用
   > - Single Wire (Half-Duplex)：半双工单线模式
   > - IrDA：红外通信
3. 下方出现 **Configuration** 配置区，设置参数：

| 参数                 | 说明    | 典型值                         |
| ------------------ | ----- | --------------------------- |
| **Baud Rate**      | 波特率   | 115200 Bits/s               |
| **Word Length**    | 数据位长度 | 8 Bits (including Parity)   |
| **Parity**         | 奇偶校验  | None                        |
| **Stop Bits**      | 停止位   | 1                           |
| **Data Direction** | 收发方向  | Receive and Transmit        |
| **Over Sampling**  | 过采样倍数 | 16 Samples（标准，用16倍过采样提高可靠性） |

### 7.3 配置 NVIC（中断，如需要）
如果你要用**中断模式**接收数据（而不是一直等待的阻塞模式），需要在 NVIC 里使能对应中断。
1. 左侧 **System Core** → **NVIC**
2. 找到 **USART2 global interrupt**，勾选 **Enabled**
3. 设置优先级（Preemption Priority），数字越小越优先。  
   本项目里：USART1/2 用优先级 5，UART4/5 用优先级 4。
### 7.4 配置 DMA（如需要）
如果要用 **DMA 模式**收发大量数据（不占用 CPU），需要配置 DMA。
1. 在 USART2 配置页面，切换到 **DMA Settings** 子标签
2. 点击 **Add** 添加 DMA 通道：
   - 发送：`USART2_TX` → DMA1 Stream 6 → Direction: Memory To Peripheral
   - 接收：`USART2_RX` → DMA1 Stream 5 → Direction: Peripheral To Memory
1. Mode 选择 **Normal**（传完停止）或 **Circular**（循环接收）
### 7.5 配置时钟（Clock Configuration）
1. 切换到顶部 **Clock Configuration** 标签
2. 确认 APB1 总线频率（USART2 挂在这里）
3. STM32F405 典型配置：HCLK=168 MHz，APB1=42 MHz，APB2=84 MHz
4. 串口实际最高波特率 ≈ 总线频率 / 16（过采样16x时）
### 7.6 生成代码
1. 顶部菜单 **Project Manager** 标签
2. 填写项目路径和名称
3. Toolchain/IDE 选择 **MDK-ARM**（Keil）
4. 点击右上角 **GENERATE CODE**
生成后，CubeMX 会在 `Core/Src/usart.c` 和 `Core/Inc/usart.h` 中生成初始化代码。
## 八、CubeMX 生成的代码解读
### 8.1 usart.h —— 句柄声明
```c
// Core/Inc/usart.h
extern UART_HandleTypeDef huart2;  // huart2 就是 USART2 的"句柄"
void MX_USART2_UART_Init(void);    // 初始化函数声明
```

**句柄（Handle）** 是 HAL 库的核心设计：  
`UART_HandleTypeDef` 是一个结构体，存储了这个 UART 外设的所有状态（寄存器地址、配置参数、当前状态、缓冲区指针……）。  
你对 USART2 的所有操作，都要传入 `&huart2`。
### 8.2 usart.c —— 初始化函数
```c
// Core/Src/usart.c
UART_HandleTypeDef huart2;  // 实际变量定义
void MX_USART2_UART_Init(void)
{
    huart2.Instance = USART2;              // 指向哪个外设
    huart2.Init.BaudRate = 115200;         // 波特率
    huart2.Init.WordLength = UART_WORDLENGTH_8B;   // 8位数据
    huart2.Init.StopBits = UART_STOPBITS_1;        // 1位停止
    huart2.Init.Parity = UART_PARITY_NONE;         // 无校验
    huart2.Init.Mode = UART_MODE_TX_RX;            // 收发双向
    huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;   // 无硬件流控
    huart2.Init.OverSampling = UART_OVERSAMPLING_16; // 16倍过采样

    if (HAL_UART_Init(&huart2) != HAL_OK)  // 写入寄存器，真正初始化
    {
        Error_Handler();  // 初始化失败，死循环或报错
    }
}
```
### 8.3 HAL_UART_MspInit —— 底层引脚/时钟配置
```c
// 这个函数由 HAL_UART_Init() 内部自动调用
// MSP = MCU Support Package，负责"最底层"的硬件初始化

void HAL_UART_MspInit(UART_HandleTypeDef* uartHandle)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    if(uartHandle->Instance == USART2)
    {
        // 第1步：开启 USART2 的时钟（默认是关的，省电设计）
        __HAL_RCC_USART2_CLK_ENABLE();

        // 第2步：开启 GPIO 端口 A 的时钟
        __HAL_RCC_GPIOA_CLK_ENABLE();

        // 第3步：配置 PA2（TX）和 PA3（RX）为复用推挽输出
        GPIO_InitStruct.Pin = GPIO_PIN_2 | GPIO_PIN_3;
        GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;          // 复用推挽
        GPIO_InitStruct.Pull = GPIO_NOPULL;              // 无上下拉
        GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
        GPIO_InitStruct.Alternate = GPIO_AF7_USART2;     // 选择 AF7

        HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

        // 第4步：配置中断（如果 CubeMX 里勾选了 NVIC）
        HAL_NVIC_SetPriority(USART2_IRQn, 5, 0);
        HAL_NVIC_EnableIRQ(USART2_IRQn);
    }

}

```

> **为什么要分成 Init 和 MspInit 两层？**  
> `HAL_UART_Init()` 只管配置 UART 外设本身的寄存器（波特率、数据格式）；  
> `HAL_UART_MspInit()` 管"外围硬件"（引脚、时钟、中断）——不同板子的引脚不同，这部分需要自定义。  
> 这样设计让 HAL 库的上层代码可以在不同硬件上复用。

## 九、HAL 库三种收发模式
### 9.1 模式对比
| 模式                | 函数                                               | CPU 占用         | 适用场景       |
| ----------------- | ------------------------------------------------ | -------------- | ---------- |
| **轮询（Polling）**   | `HAL_UART_Transmit` / `HAL_UART_Receive`         | 高（等待期间 CPU 阻塞） | 调试、偶尔发一次数据 |
| **中断（Interrupt）** | `HAL_UART_Transmit_IT` / `HAL_UART_Receive_IT`   | 中（发完/收完后回调）    | 实时接收少量数据   |
| **DMA**           | `HAL_UART_Transmit_DMA` / `HAL_UART_Receive_DMA` | 极低（CPU 几乎不参与）  | 大量连续数据收发   |

### 9.2 轮询模式（最简单，适合入门）
```c
// 发送字符串
uint8_t msg[] = "Hello UART!\r\n";
HAL_UART_Transmit(&huart6, msg, sizeof(msg) - 1, 100);
//                 ↑句柄   ↑数据指针  ↑长度       ↑超时ms

// 接收1个字节（阻塞等待，最多等 1000ms）
uint8_t rx_byte;
HAL_StatusTypeDef ret = HAL_UART_Receive(&huart6, &rx_byte, 1, 1000);
if (ret == HAL_OK) {
    // 成功收到 rx_byte
} else if (ret == HAL_TIMEOUT) {
    // 超时，没收到
}
```

> **HAL_UART_Transmit 会阻塞 CPU**：发送期间 CPU 只是在等，什么都不做。  
> 在 FreeRTOS 中这意味着这个任务的时间片全浪费了，通常只用于调试输出。

### 9.3 中断模式
```c
// ① 先注册一次接收中断（只接收 1 个字节，收到后触发回调）
HAL_UART_Receive_IT(&huart2, &rx_buf, 1);

// ② 实现回调函数（HAL 库会在接收完成后自动调用）
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART2)
    {
        // rx_buf 里就是刚收到的字节
        process_byte(rx_buf);
        // 重新注册，等下一个字节（否则中断只触发一次）
        HAL_UART_Receive_IT(&huart2, &rx_buf, 1);
    }
}
```
> 中断回调函数在 **ISR 上下文**中执行，要尽量短，不能调用 `HAL_Delay`、不能用 `printf`，不能使用非线程安全的函数。

### 9.4 DMA 模式 + 空闲中断（最实用的接收方案）

实际项目中接收长度不定的数据帧，常用"DMA + IDLE 中断"方案：
```c
// ① 启动 DMA 循环接收（永远在接收，存入 dma_buf 循环缓冲区）
uint8_t dma_buf[256];
HAL_UART_Receive_DMA(&huart4, dma_buf, sizeof(dma_buf));

// ② 开启空闲中断（总线空闲时触发，意味着一帧数据发完了）
__HAL_UART_ENABLE_IT(&huart4, UART_IT_IDLE);

// ③ 在中断处理函数里检测空闲标志
void UART4_IRQHandler(void)
{
    if (__HAL_UART_GET_FLAG(&huart4, UART_FLAG_IDLE))
    {
        __HAL_UART_CLEAR_IDLEFLAG(&huart4);

        // 计算实际收到了多少字节
        uint16_t received = sizeof(dma_buf)
                          - __HAL_DMA_GET_COUNTER(huart4.hdmarx);
        // 处理 dma_buf[0..received-1]
        process_frame(dma_buf, received);
    }
    HAL_UART_IRQHandler(&huart4);  // 让 HAL 处理其他标志
}
```

## 十、printf 重定向到串口
嵌入式中经常需要用 `printf` 打印调试信息。C 标准库的 `printf` 默认输出到"标准输出"，  
在嵌入式里需要把它**重定向**到你的 UART。

### 方法：重写 `fputc`
在任意一个 `.c` 文件（通常是 `usart.c` 或 `main.c`）中加入：
```c
#include <stdio.h>

// 重定向 printf 到 USART6（调试串口）
int __io_putchar(int ch)
{
    HAL_UART_Transmit(&huart6, (uint8_t *)&ch, 1, HAL_MAX_DELAY);
    return ch;
}

// 有些工具链需要的是这个函数：
int fputc(int ch, FILE *f)
{
    HAL_UART_Transmit(&huart6, (uint8_t *)&ch, 1, HAL_MAX_DELAY);
    return ch;
}
```

Keil MDK 的 MicroLib 用 `__io_putchar`；标准库用 `fputc`。  
本项目 `usart.c` 里定义的 `DebugUart = huart6` 就是这个用途。

使用时正常 `printf`：
```c
printf("电压: %d mV, 电流: %d mA\r\n", voltage_mv, current_ma);
```

> **注意**：`\r\n` 是 Windows 换行，串口终端（如 SecureCRT、MobaXterm）一般需要 `\r\n`。  
> 只写 `\n` 在某些终端会导致光标不回到行首。

## 十一、RS485 方向控制（本项目实战）
### 11.1 为什么 RS485 需要方向控制？
RS485 是**半双工总线**：所有设备共享同一对差分线（A/B），**同一时刻只能有一个设备在发送**。  
SP485 芯片有一个 **DE/RE 引脚**（Driver Enable / Receiver Enable）：
- 高电平：发送模式（Drive Enable）
- 低电平：接收模式（Receive Enable）
```
STM32
 UART4 TX ──────────────────► SP485 DI  ──► RS485 总线 A/B
 UART4 RX ◄──────────────── SP485 RO
 PA4（DIR） ──────────────── SP485 DE/RE   ← 高=发，低=收
```

### 11.2 本项目的 RS485 发送函数
```c
// APP/Core/Src/usart.c

// EN_RS485_TX 为 1 时启用 RS485 发送控制
#define EN_RS485_TX   1

HAL_StatusTypeDef COM_UART_Transmit(UART_HandleTypeDef *huart,
                                     uint8_t *pData,
                                     uint16_t Size,
                                     uint32_t Timeout)
{
    HAL_StatusTypeDef status = HAL_OK;
#if EN_RS485_TX
    // 发送前：拉高 DIR 引脚，切换到发送模式
    HAL_GPIO_WritePin(UART4_DIR_GPIO_Port, UART4_DIR_Pin, GPIO_PIN_SET);
#endif
    status = HAL_UART_Transmit(huart, pData, Size, Timeout);
#if EN_RS485_TX
    // 发送后：拉低 DIR 引脚，切换回接收模式（准备接收响应）
    HAL_GPIO_WritePin(UART4_DIR_GPIO_Port, UART4_DIR_Pin, GPIO_PIN_RESET);
#endif
    return status;
}
```
> `UART4_DIR_Pin` 就是 `main.h` 里定义的 `PA4`——Modbus 主机发完一帧后立刻切回接收，等待从机的响应帧。
## 十二、常见问题与排查

### 12.1 乱码
| 原因 | 排查方法 |
|------|----------|
| 波特率不匹配 | 确认收发双方波特率一致，检查时钟配置 |
| 数据位/停止位/校验配置不一致 | 统一为 8N1 |
| TX/RX 接反 | 用万用表或示波器查 TX 是否有波形，检查接线 |
| 接地不共 | 确认 GND 相连 |
| 时钟配置错误 | 检查 CubeMX 时钟树，APB 频率是否正确 |

### 12.2 只能发不能收（或只能收不能发）
- 检查 GPIO 模式：TX 要配 `GPIO_MODE_AF_PP`（推挽），RX 也要配 `GPIO_MODE_AF_PP`（或 `AF_INPUT`）
- 检查 `UART_MODE_TX_RX` 是否配了双向
- RS485 场景：检查 DIR 脚默认电平，收时应为低

### 12.3 HAL_UART_Receive 卡死不返回
- 发送方没有发够指定长度的字节
- 用超时参数代替 `HAL_MAX_DELAY`，避免永久阻塞
- 或改用中断/DMA 模式
### 12.4 中断收到数据后不处理
- 检查 `HAL_NVIC_EnableIRQ` 是否调用
- 检查 `stm32f4xx_it.c` 里是否有对应的 `USARTx_IRQHandler` 并调用 `HAL_UART_IRQHandler`
- 检查 `HAL_UART_Receive_IT` 是否在回调里重新注册
### 12.5 printf 没输出
- 确认 `__io_putchar` 或 `fputc` 已实现
- Keil 工程设置里确认勾选了 **Use MicroLIB**（小型 C 库）
- 确认调试串口波特率和终端一致（本项目 USART6 = 921600）
## 十三、本项目 UART 分配速查表

| 外设      | TX 引脚 | RX 引脚 | 波特率     | AF  | 用途                             |
| ------- | ----- | ----- | ------- | --- | ------------------------------ |
| USART1  | PB6   | PB7   | 115200  | AF7 | —                              |
| USART2  | PA2   | PA3   | 115200  | AF7 | —                              |
| USART3  | PB10  | PB11  | 460800  | AF7 | —                              |
| UART4   | PC10  | PC11  | 19200   | AF8 | Modbus RTU（RS485，连电池板），DIR=PA4 |
| UART5   | PC12  | PD2   | 19200   | AF8 | Modbus RTU（RS485，连电池板2）        |
| USART6  | PC6   | PC7   | 921600  | AF8 | 调试串口（printf 输出，上位机通信）          |
  
> 调试串口 USART6 的 921600 bps 非常高，连接时务必选对终端波特率，否则全是乱码。

## 附录：关键词速查

| 术语 | 解释 |
|------|------|
| UART | 通用异步收发器，串行通信协议 |
| USART | UART 超集，增加同步模式（CLK 线） |
| 波特率 | 每秒传输的 bit 数 |
| 8N1 | 8数据位、无校验、1停止位，最常用格式 |
| TX | 发送引脚（接对方 RX） |
| RX | 接收引脚（接对方 TX） |
| AF | 复用功能，引脚切换给外设使用 |
| huartX | HAL 库中 UART 外设的句柄（Handle）结构体 |
| MspInit | HAL 底层硬件初始化（引脚/时钟/中断） |
| TTL | 3.3V/5V 电平标准（STM32 原生使用） |
| RS232 | ±15V 电平，老式 PC 串口，需 MAX232 转换 |
| RS485 | 差分信号，远距离、多节点，需 SP485 转换 |
| DE/RE | RS485 芯片的方向控制引脚 |
| DMA | 直接内存访问，数据搬运不经过 CPU |
| IDLE 中断 | 总线空闲中断，用于检测一帧数据接收完毕 |
