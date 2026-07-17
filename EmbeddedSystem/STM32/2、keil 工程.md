---
title: "[[2、keil 工程]]"
type: Permanent
status: done
Creation Date: 2026-07-12 10:19
tags:
  - STM32
  - Keil
  - 嵌入式
  - 开发环境
---
## STM32 开发方式概述
STM32 有三种主流开发方式：

| 开发方式 | 说明 | 优缺点 |
|---------|------|--------|
| **寄存器开发** | 直接配置寄存器，操作最底层 | 效率高，但 STM32 寄存器太多，不推荐 |
| **标准库（库函数）开发** | 调用 ST 官方封装的函数，间接配置寄存器 | 封装良好，效率与易用性兼顾，**本课程使用** |
| **HAL 库开发** | 图形化配置，快速上手 | 隐藏底层逻辑，不利于深入学习，暂不推荐 |

> 推荐先学标准库，再了解 HAL 库。

---

## STM32 标准外设库结构

固件库（`STM32F10x 标准外设库`）压缩包解压后目录如下：

```
STM32F10x_StdPeriph_Lib/
├── _htm01es/                # 两个图片文件（无用）
├── Libraries/                # ★ 库函数核心文件，建工程时使用
│   ├── CMSIS/               # ARM Cortex-M 内核相关
│   │   └── CM3/
│   │       ├── core_cm3.c / core_cm3.h     # 内核寄存器描述 + 内核配置函数
│   │       └── DeviceSupport/
│   │           └── ST/STM32F10x/
│   │               ├── stm32f10x.h         # 外设寄存器描述文件（类似 51 的头文件）
│   │               ├── system_stm32f10x.c / .h  # 时钟配置（72MHz 主频在此配置）
│   │               └── startup/arm/        # 启动文件（多个，按型号选择）
│   └── STM32F10x_StdPeriph_Driver/         # 各外设库函数源码
│       ├── src/                           # 库函数 .c 源文件
│       └── inc/                           # 库函数 .h 头文件
├── Project/                  # 官方工程示例和模板
│   └── STM32F10x_StdPeriph_Template/
│       ├── stm32f10x_conf.h               # 库函数头文件配置
│       ├── stm32f10x_it.c / .h           # 中断服务函数
│       └── main.c / .h
└── Utilities/               # STM32 官方评估板测评程序（无用）
    ├── Release_Notes.html    # 库函数发布文档
    └── stm32f10x_stdperiph_lib_um.chm    # 库函数使用手册
```

---

## 新建工程详细步骤

### 整体目录规划

在磁盘上新建项目总文件夹（如 `STM32Project/`），每次新建工程在其中创建子文件夹存放。

工程内文件夹结构：

```
工程名/
├── start/       # 启动文件 + 内核/外设寄存器描述
├── library/     # 库函数源码和头文件
└── user/        # 用户代码（main.c, stm32f10x_conf.h, stm32f10x_it.c/.h）
```

### 步骤一：创建 Keil 工程

1. Keil 中点击 `Project → New µVision Project`
2. 选择工程文件夹内的子文件夹（本次工程名：`2-1 STM32工程模板`）
3. 输入工程名称（如 `Project`），点击保存
4. 选择芯片型号：`STM32F103C8`

### 步骤二：添加 start 文件夹

从固件库 `Libraries/CMSIS/DeviceSupport/ST/STM32F10x/startup/arm/` 复制以下文件到工程的 `start/` 文件夹：

| 文件 | 说明 |
|------|------|
| `startup_stm32f10x_md.s` | **启动文件**（根据 Flash 大小选择后缀，本教程选 `_md.s`） |
| `stm32f10x.h` | 外设寄存器描述文件（类似 51 的 `reg52.h`） |
| `system_stm32f10x.c` / `.h` | 时钟配置（72MHz 主频由此配置） |
| `core_cm3.c` / `core_cm3.h` | ARM Cortex-M3 内核寄存器描述 + 内核配置函数 |

> 注意：内核寄存器描述和外设寄存器描述分开存放，因此两者都需要添加。

### 步骤三：在 Keil 中添加文件分组

1. 在 Keil 左侧 `Target` 上右键 → `Add Group`，命名为 `start`
2. 同上添加 `library` 和 `user` 分组
3. 选中 `start` 分组 → 右键 → `Add Existing Files to Group 'start'`
4. 选择 `start/` 文件夹，`Filter` 选 `*.*` 显示所有文件
5. **只添加一个**启动文件（`_md.s`），其余 `.c` 和 `.h` 文件全部添加

> 启动文件图标带小钥匙（🔒），表示只读文件，无需修改。

### 步骤四：配置头文件路径

1. 点击 `魔术棒` → `C/C++` → `Include Paths` → 新建路径
2. 添加 `start/` 文件夹路径（其他自建文件夹同样添加）
3. 点击 OK

### 步骤五：创建 main.c

1. 在工程文件夹的 `user/` 目录下新建 `main.c`
2. Keil 中 `user` 分组 → 右键 → `Add New File to Group 'user'` → 选择 `C File` → 命名为 `main`，路径选择 `user/` 目录

`main.c` 基本结构：

```c
#include "stm32f10x.h"

int main(void)
{
    while(1)
    {
        // 用户代码
    }
}
```

> 注意：
> - `main` 函数返回 `int`，有参数
> - 文件**最后一行为空行**，否则会报警告

### 步骤六：编译验证

点击编译按钮（`F7`），确认 `0 Error, 0 Warning`。

此时工程**不包含库函数**，属于寄存器开发方式，可直接使用。

---

## Keil 编辑器设置

点击扳手工具（`Configuration`）进行以下设置：

| 设置项 | 建议值 | 说明 |
|--------|--------|------|
| 字体大小 | 14 号 | C/C++ Editor 和 ASM Editor 均设为 14 |
| 编码格式 | **UTF-8** | 防止中文乱码。打开他人工程如遇中文乱码，先改此处 |
| Tab 大小 | 4 | 缩进保持一致 |

---

## 硬件连接（ST-Link 调试）

### 接线

使用 ST-Link + 4 根杜邦线（母对母），按最小系统板插针标识连接：

| ST-Link | STM32 最小系统板 |
|---------|----------------|
| 3.3V | 3.3V |
| GND | GND |
| SWDIO | SWDIO |
| SWCLK | SWCLK |

> 接线后板子上电，电源指示灯亮，PC13 测试灯默认闪烁（芯片出厂测试程序）。

### Keil 调试器配置

1. `魔术棒 → Debug`，选择 `ST-Link Debugger`（不是默认的 `ULink`）
2. 点击右侧 `Settings` → `Flash Download`，勾选 `Reset and Run`
   - 勾选后：下载程序后自动复位并运行，无需手动按复位键
3. 点击 OK 确认

### 编译并下载

1. 编译工程（`F7`）
2. 点击 `Load` 按钮下载程序

---

## 寄存器方式点灯（演示）
以点亮 PC13 端口 LED 为例，仅需配置 3 个寄存器：
### 第 1 步：使能 GPIOC 时钟
STM32 上电后外设默认无时钟，必须先使能：
```c
RCC->APB2ENR = 0x00000010;  // 置位 IOPCEN（APB2ENR 第 4 位）
```
> 对应寄存器：`RCC_APB2ENR`，在 `RCC->APB2ENR` 中置第 4 位。


> [!info]+ STM32 为什么需要使能时钟？
>
> **低功耗设计**：STM32 源自 ARM Cortex-M 内核，内核设计理念之一就是低功耗。STM32 片上集成了大量外设（GPIO、USART、SPI、I2C、ADC 等），如果所有外设上电即运行，会消耗大量电流。通过时钟门控（Clock Gating），未使用的外设可以完全停止时钟，从而实现极低的静态功耗。
>
> **STM32 的时钟门控机制**：STM32 的每个外设都连接有一条独立的时钟线。时钟线默认处于关闭状态，对这些寄存器写入数据时：
> - 若外设时钟未使能 → 写入操作被忽略，寄存器值不变，外设不工作
> - 若外设时钟已使能 → 写入操作生效，外设正常运行
>
> **RCC 模块**：STM32 的时钟管理由 **RCC**（Reset and Clock Control，复位和时钟控制）模块负责。RCC 挂载在 AHB 总线上，上电默认使能。本操作涉及的 `RCC_APB2ENR`（APB2 外设时钟使能寄存器）各位定义如下：
>
> | 位 | 外设 | 说明 |
> |----|------|------|
> | Bit 0 | AFIO | 复用 IO 时钟 |
> | Bit 2 | GPIOA | PA 端口时钟 |
> | Bit 3 | GPIOB | PB 端口时钟 |
> | Bit 4 | **GPIOC** | **PC 端口时钟（本操作使能的就是这个）** |
> | Bit 5 | GPIOD | PD 端口时钟 |
> | ... | ... | ... |
> | Bit 12 | ADC1 | ADC1 时钟 |
>
> 因此 `RCC->APB2ENR = 0x00000010`（二进制 `0001 0000`）将 Bit 4 置 1，即打开了 GPIOC 的时钟，之后才能对 `GPIOC` 相关寄存器进行读写操作。
>
> **总线映射**：GPIOC 挂在 **APB2 总线**上，所以使用 `RCC_APB2ENR`（而非 `RCC_APB1ENR`）。APB1 连接的是低速外设（如 I2C2/3、SPI2/3、UART4/5、DAC 等）。
>
> **操作任何外设前的通用步骤**：任何外设（GPIO、USART、SPI 等）在使用前，都必须先在对应的 RCC 时钟使能寄存器中将对应位置 1，否则外设不响应。这是一条所有 STM32 开发必须牢记的准则。

### 第 2 步：配置 PC13 端口模式
使用 `GPIOC->CRH` 配置端口：
- CNF13[1:0] = 00（通用推挽输出）
- MODE13[1:0] = 11（最大速度 50MHz）
```c
GPIOC->CRH = 0x00300000;  // 配置 PC13 为推挽输出，50MHz
```

> [!info]+ GPIO 端口模式配置：CRH/CRL 寄存器详解
>
> **为什么用 CRH 而不是 CRL**：STM32 每个 GPIO 端口有 16 个引脚（Pin 0 ~ Pin 15）。低 8 位（Pin 0~7）由 `GPIOx->CRL` 控制，高 8 位（Pin 8~15）由 `GPIOx->CRH` 控制。PC13 属于高 8 位，因此使用 `GPIOC->CRH`。
>
> **CRH/CRL 的结构**：每个引脚在 CRL/CRH 中占 4 位，由 `CNF[1:0]`（2位）和 `MODE[1:0]`（2位）组成：
>
> | 位段 | 名称 | 作用 |
> |------|------|------|
> | `CNF[1:0]` | 模式配置 | 选择输入/输出模式的具体类型 |
> | `MODE[1:0]` | 模式选择 | 选择输入模式还是输出模式，以及输出速度 |
>
> **MODE[1:0] 模式选择**：
>
> | MODE[1:0] | 含义 |
> |-----------|------|
> | `00` | 输入模式 |
> | `01` | 输出模式，最大速度 10MHz |
> | `10` | 输出模式，最大速度 2MHz |
> | `11` | 输出模式，最大速度 **50MHz** |
>
> **CNF[1:0] 输入模式配置（MODE=00 时）**：
>
> | CNF[1:0] | 含义 |
> |----------|------|
> | `00` | 模拟输入（ADC 或比较器） |
> | `01` | 浮空输入（默认，复位后状态） |
> | `10` | 复用功能输入（由片上外设驱动） |
> | `11` | 下拉输入（内部接下拉电阻） |
>
> **CNF[1:0] 输出模式配置（MODE≠00 时）**：
>
> | CNF[1:0] | 含义 |
> |----------|------|
> | `00` | **通用推挽输出**（本操作使用） |
> | `01` | 通用开漏输出 |
> | `10` | 复用功能推挽输出（由片上外设驱动，如 USART TX） |
> | `11` | 复用功能开漏输出 |
>
> **本操作值解析**：`CNF13=00 + MODE13=11` → 通用推挽输出，最大速度 50MHz。对应十六进制 `0x3`，4 个引脚的 4 位值组合后得到 `0x00300000`（PC13 对应 Bit 20~23）：
>
> ```
> CRH 寄存器（32 位，分 8 组，每组 4 位对应一个引脚）：
> [CNF15][MODE15] | [CNF14][MODE14] | [CNF13][MODE13] | ... | [CNF8][MODE8]
>       0    0    |      0    0    |  00 + 11 = 0x3 | ... |    0    0
>
> Bit 23:20 = 0011 (CNF13=00, MODE13=11)
> 其他位 = 0000
> → 十六进制 = 0x00300000
> ```
>
> **为什么选推挽输出（PP）**：推挽输出（Push-Pull）由 PMOS + NMOS 组成：
> - 输出高电平时，PMOS 导通，直接将引脚拉高到 VDD（强上拉）
> - 输出低电平时，NMOS 导通，直接将引脚拉低到 GND（强下拉）
>
> **LED 为什么低电平点亮**：最小系统板上 LED 连接在 PC13 与 VDD 之间（LED 阳极接 VDD，阴极接 PC13）。当 PC13 输出低电平，电流从 VDD → LED → PC13 流入地，LED 亮；PC13 输出高电平时两端无电势差，LED 灭。这就是典型的"低电平点亮"设计。

### 第 3 步：控制输出电平
使用 `GPIOC->ODR` 寄存器：
```c
GPIOC->ODR = 0x00000000;  // ODR13=0，LED 亮（低电平点亮）
// GPIOC->ODR = 0x00002000; // ODR13=1，LED 灭
```

### 寄存器方式的问题
- 需要不断查阅手册确认每一位的功能
- 直接赋值会覆盖其他位（影响其他端口原有配置）
- 若要不影响其他位，需用 `&=`（与等于）和 `|=`（或等于）操作，更麻烦

---

## 添加标准库函数
### 步骤一：复制库函数文件
1. 工程文件夹新建 `library/` 目录
2. 从固件库 `Libraries/STM32F10x_StdPeriph_Driver/src/` 复制**所有** `.c` 文件到 `library/`
3. 从 `Libraries/STM32F10x_StdPeriph_Driver/inc/` 复制**所有** `.h` 文件到 `library/`
### 步骤二：添加配置文件
从固件库 `Project/STM32F10x_StdPeriph_Template/` 复制以下 3 个文件到工程 `user/` 目录：

| 文件 | 作用 |
|------|------|
| `stm32f10x_conf.h` | 配置库函数头文件的包含关系 |
| `stm32f10x_it.c` | 中断服务函数定义 |
| `stm32f10x_it.h` | 中断服务函数声明 |

### 步骤三：Keil 中添加文件
1. 新建 `library` 分组，添加 `library/` 目录下所有文件
2. `user` 分组添加刚复制的 3 个文件

### 步骤四：配置工程选项

1. `魔术棒 → C/C++ → Define`：填入 `USE_STDPERIPH_DRIVER`
2. `魔术棒 → C/C++ → Include Paths`：添加 `library/` 和 `user/` 路径

### 步骤五：编译

首次编译较慢，确认 `0 Error, 0 Warning` 即成功。

> 库函数文件同样带只读钥匙（🔒），不需要修改。唯一需要修改的是 `user/` 分组下的文件。

---

## 库函数方式点灯
### 步骤一：使能 GPIOC 时钟
```c
RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOC, ENABLE);
```
### 步骤二：配置 GPIO 模式（结构体方式）
```c
GPIO_InitTypeDef GPIO_InitStructure;

// 选择 GPIOC 的 Pin 13
GPIO_InitStructure.GPIO_Pin = GPIO_Pin_13;
// 通用推挽输出模式
GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
// 输出速度 50MHz
GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;

// 初始化 GPIOC
GPIO_Init(GPIOC, &GPIO_InitStructure);
```

### 步骤三：控制电平
```c
// 设置高电平（灭）
GPIO_SetBits(GPIOC, GPIO_Pin_13);
// 设置低电平（亮）
GPIO_ResetBits(GPIOC, GPIO_Pin_13);
```

### 库函数 vs 寄存器

| 对比项 | 寄存器方式 | 库函数方式 |
|--------|-----------|-----------|
| 需要查手册 | 是 | 否 |
| 会影响其他位 | 是（直接赋值） | 否（函数内部已处理） |
| 代码可读性 | 低（数字含义不直观） | 高（语义明确） |
| 开发效率 | 低 | 高 |

---
## 启动文件选择指南
STM32F1 系列根据 Flash 大小分为不同型号，启动文件后缀对应如下：

| Flash 大小 | 后缀 | 型号示例 |
|-----------|------|---------|
| 小容量产品（16~32KB） | `_ld.s` | STM32F101x4/x6 |
| 中低容量产品（16~128KB） | `_md.s` | **STM32F103C8T6（64KB）选此** |
| 大容量产品（256~512KB） | `_hd.s` | STM32F103xE/xF |
| 加大容量产品（>512KB） | `_xl.s` | STM32F103xG |
| 超值系列（STM32F100） | `_vl.s` 前缀 | STM32F100xB/C/D/E |
| 互联型（STM32F105/107） | `_cl.s` | STM32F105xx / STM32F107xx |

> 本教程所用 `STM32F103C8T6`（64KB Flash）→ 选 `_md.s` 启动文件。

## 工程架构总结

![工程文件结构图](STM32工程文件结构图.png)
> 图：STM32 工程各文件关系与作用

### 主动执行文件（按顺序）
1. **启动文件（`.s` 汇编）**：程序入口
   - 定义中断向量表
   - 复位中断是整个程序入口：`SystemInit()` → `main()`
   - `SystemInit()` 在 `system_stm32f10x.c` 中定义，负责配置闪存接口、时钟、锁相环（72MHz）
   - 定义所有其他中断服务函数（空函数，用户需自行实现或重写）

2. **system_stm32f10x.c**：时钟初始化（72MHz 主频配置）

3. **main.c**：用户程序入口，必须包含 `while(1)` 死循环

### 被动执行文件（被调用）

| 文件 | 作用 |
|------|------|
| `stm32f10x.h` | 外设寄存器地址和位定义（寄存器开发用） |
| `core_cm3.c/.h` | Cortex-M3 内核寄存器定义 |
| 库函数 `src/` | 封装寄存器操作，提供易用函数 |
| `stm32f10x_conf.h` | 统一 include 所有库函数头文件 |

### 头文件包含关系
```
main.c
  └── #include "stm32f10x.h"
          └── #include "stm32f10x_conf.h"
                  └── #include "stm32f10x_gpio.h"  // 及其他所有外设头文件
```
> 因此用户代码只需 `#include "stm32f10x.h"`，即可调用所有库函数。
---

## 新建工程六步总览

| 步骤 | 操作 | 关键点 |
|------|------|--------|
| 1 | 创建工程，选择型号 | Keil 新建 → 选 `STM32F103C8` |
| 2 | 建立 `start/library/user` 文件夹，复制固件库文件 | **必须复制到工程文件夹内**，保持独立性 |
| 3 | Keil 中建立 `start/library/user` 分组，添加文件 | 启动文件只选一个（`_md.s`） |
| 4 | 配置 `C/C++ → Include Paths` | 所有自建文件夹路径都要添加 |
| 5 | 配置 `C/C++ → Define` | 填入 `USE_STDPERIPH_DRIVER`（库函数条件编译） |
| 6 | 配置 `Debug → ST-Link Debugger`，勾选 `Reset and Run` | SWD 方式下载调试 |

---

## 调试下载方式

| 方式 | 接口 | 所需引脚 | 说明 |
|------|------|---------|------|
| **SWD**（推荐） | ST-Link | SWDIO + SWCLK + GND + 3.3V（4 根） | 本教程使用，只需 PA13/PA14 |
| JTAG | ST-Link | 5 针 | 占用引脚多，一般不推荐 |

> 若误将所有调试端口配置为普通 IO 口导致无法下载，用串口方式（BOOT0=1）急救下载。
