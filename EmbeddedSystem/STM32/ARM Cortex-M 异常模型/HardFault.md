---
title: "[[HardFault]]"
type: Permanent
status: done
Creation Date: 2026-08-18 16:00
tags:
---
## 一、为什么会有 HardFault？
### 1.1 从程序崩溃说起
CPU 执行程序，本质上是在不断做两件事：
```
取指令（Fetch）→ 解码（Decode）→ 执行（Execute）→ 写回（Writeback）
```
CPU 假设所有内存都乖乖听话：
- 指令存在 Flash 里 → 可以读
- 数据存在 RAM 里 → 可以读写
- 外设寄存器存在外设地址空间 → 可以读写

但硬件世界不总是如愿：
```
访问一个不存在的地址        → CPU 不知道怎么处理
执行一条不存在的指令        → CPU 不知道这是什么
违反 CPU 的安全规则         → CPU 必须停下来
```
**当 CPU 遇到「不知道怎么处理」的错误时，它必须停下来。**
停下来之后，CPU 需要做两件事：
1. 保存现场（哪些寄存器值？PC 在哪？出错了哪条指令？）
2. 跳转到固定地址（告诉软件："出事了，过来看看"）

这个「固定地址」就是 **HardFault handler**，它不是软件写的，是 ARM Cortex-M 架构规定的。

### 1.2 ARM Cortex-M 的异常体系
```
优先级
最高  ┌────────────────────────────────────┐
  -3  │ Reset         │ 复位               │
  -2  │ NMI           │ 不可屏蔽中断        │
  -1  │ HardFault     │ 硬件错误（总入口）   │
   0  │ MemManage     │ 内存管理 fault      │
   1  │ BusFault      │ 总线访问 fault      │
   2  │ UsageFault    │ 用法 fault          │
   3  │ SVC           │ 系统服务调用        │
   4  │ PendSV        │ 可挂起 SV           │
   5  │ SysTick       │ 系统定时器          │
      └────────────────────────────────────┘
  低 ──└ 外设中断（IRQ0-IRQ239）────────────┘
```
**为什么 HardFault 在最前面？**
因为它是「兜底」的。任何比它优先级低的 fault（MemManage/BusFault/UsageFault），如果被禁用了或者它们的 handler 里又出错了，都会一级一级上报到 HardFault。
### 1.3 什么时候触发 HardFault？
| 触发条件        | 具体例子                      |
| ----------- | ------------------------- |
| 访问了不存在的内存地址 | `int *p = NULL; *p = 1;`  |
| 执行了非法指令     | 函数指针 bit 0 不是 1（Thumb 模式） |
| 非对齐内存访问     | 在不支持的芯片上做 32 位访问          |
| 总线错误        | 访问一个时钟没开的 GPIO 寄存器        |
| 除零（可配置）     | `a / 0`，如果 `DIV_0_TRP` 置位 |
| 堆栈溢出        | 递归太深把栈写穿了                 |

### 1.4 为什么要理解 HardFault？
**不理解 HardFault 之前：**
```
固件跑着跑着死了
→ 重新上电
→ 好了，当作偶发问题
→ 过两天又死了
→ 换芯片
→ 继续死
→ ...
→ 产品上市后大规模召回
```
**理解 HardFault 之后：**
```
固件跑着跑着死了
→ 读 SCB 寄存器
→ 定位到 bms_task.c:187
→ 修复 NULL 指针
→ 稳定运行
```
## 二、HardFault 发生时 CPU 做了什么？
### 2.1 异常处理流程（硬件自动完成）
```
正常程序执行
     │
     │ （例如：访问 NULL 指针）
     ▼
CPU 检测到错误 ──────────────→ 跳转到 HardFault_Handler
     │                              │
     │ 硬件自动压栈:                 │ 软件开始执行:
     │ - PC (返回地址)               │
     │ - xPSR                       │
     │ - R0-R3, R12, LR             │
     │ - 如果 floating-point 开启   │
     │   还要压 S0-S15, FPSCR       │
     ▼                              ▼
   栈帧结构（R13/SP 指向这里）
```
### 2.2 栈帧结构（硬件压的）
```
高地址  ┌─────────────────────┐
        │      R0             │  ← 主调函数传给被调函数的参数
        ├─────────────────────┤
        │      R1             │
        ├─────────────────────┤
        │      R2             │
        ├─────────────────────┤
        │      R3             │
        ├─────────────────────┤
        │      R12            │  ← 调用者保存寄存器
        ├─────────────────────┤
        │      LR (R14)       │  ← 返回地址
        ├─────────────────────┤
        │      PC (R15)       │  ← 下一条要执行的指令
        ├─────────────────────┤
        │     xPSR            │  ← 程序状态
        └─────────────────────┘  ↑
低地址   (SP 指向这里)
```
**理解这个栈帧非常重要**：PC 寄存器的值就是「出错的指令地址」，LR 寄存器的值就是「调用者返回地址」。

### 2.3 异常返回值（LR 的值）
进入异常后，LR 寄存器的值不是随机的，它编码了异常返回的方式：

| LR 值 | 含义 |
|---|---|
| `0xFFFFFFF1` | 从主栈（MSP）返回，Handler 模式 |
| `0xFFFFFFF9` | 从主栈（MSP）返回，线程模式 |
| `0xFFFFFFFD` | 从进程栈（PSP）返回，线程模式 |
| `0xFFFFFFFB` | 从进程栈（PSP）返回，Handler 模式 |

通常固件只用 MSP，所以 LR = `0xFFFFFFF9`。知道这个值没有意义，但知道 LR 存的是返回地址很有意义。
## 三、Cortex-M 的 Fault 寄存器体系
### 3.1 为什么有 3 个 Fault？
ARM 设计了 3 个不同层级的 fault，它们的严重程度不同：
```
┌────────────────────────────────────────────┐
│                  HardFault                  │  ← 总是开启，不可禁用
├────────────────────────────────────────────┤
│   UsageFault   │  BusFault    │ MemManage  │  ← 可以禁用，可以设优先级
│   (用法错误)    │  (总线错误)   │ (内存错误)  │
└────────────────────────────────────────────┘
```

| 异常             | 触发原因                | 可否禁用 | 典型场景          |
| -------------- | ------------------- | ---- | ------------- |
| **MemManage**  | 访问 MPU 保护区域         | 可禁用  | RTOS 任务越界访问   |
| **BusFault**   | 总线 AHB 访问错误         | 可禁用  | 访问未使能时钟的外设    |
| **UsageFault** | 非法指令/对齐错误           | 可禁用  | 除零、Thumb 地址错误 |
| **HardFault**  | 以上任一上报，或无可用 handler | 不可禁用 | —             |

### 3.2 SCB 寄存器家族
所有的 fault 状态都集中在 **SCB（System Control Block）** 里：
```
SCB 结构（在 stm32f4xx.h 中定义）:
  - SCB->ICSR     中断控制状态寄存器
  - SCB->SHCSR    系统 handler 控制和状态寄存器
  - SCB->CFSR     Configurable Fault Status Register
  - SCB->HFSR     HardFault Status Register
  - SCB->DFSR     Debug Fault Status Register
  - SCB->MMFAR    MemManage Fault Address Register
  - SCB->BFAR     BusFault Address Register
  - SCB->AFSR     Auxiliary Fault Status Register
```
其中 **CFSR** 是最重要的，它被分成 3 组，每组 8 位：
```
CFSR (31-bit Configurable Fault Status Register)
┌──────────────────────────────────────────┐
│  [31:24] UFSR (UsageFault)   8 位         │
│  [23:16] BFSR  (BusFault)    8 位         │
│  [15: 8] MMFSR (MemManage)   8 位         │
│  [ 7: 0] 保留                         │
└──────────────────────────────────────────┘
```

## 四、CFSR 每一位的含义（查表版）
### 4.1 MemManage Fault Status (MMFSR) — CFSR[7:0]

| 位        | 名称          | 含义                              |
| -------- | ----------- | ------------------------------- |
| MMFSR[0] | `IACCVIOL`  | 指令访问违规：PC 指向了不存在/无权限的 Flash 地址  |
| MMFSR[1] | `DACCVIOL`  | 数据访问违规：**最常见**，写/读了无权访问的 RAM 地址 |
| MMFSR[2] | `MUNSTKERR` | MemManage fault 时压栈出错（栈被破坏了）    |
| MMFSR[3] | `MSTKERR`   | 入栈时发生 MemManage fault           |
| MMFSR[4] | `MLSPERR`   | floating-point lazy stacking 出错 |
| MMFSR[7] | `MMARVALID` | `MMFAR` 寄存器有效（保存了出错地址）          |

### 4.2 BusFault Status (BFSR) — CFSR[15:8]

| 位       | 名称            | 含义                              |
| ------- | ------------- | ------------------------------- |
| BFSR[0] | `IBUSERR`     | 指令总线错误                          |
| BFSR[1] | `PRECISERR`   | **精确总线错误**：和数据访问同一时刻发生，可定位      |
| BFSR[2] | `IMPRECISERR` | **不精确总线错误**：错误延迟报告，只能看地址范围      |
| BFSR[3] | `UNSTKERR`    | BusFault 时压栈出错                  |
| BFSR[4] | `STKERR`      | 入栈时发生 BusFault                  |
| BFSR[5] | `LSPERR`      | floating-point lazy stacking 出错 |
| BFSR[7] | `BFARVALID`   | `BFAR` 寄存器有效                    |

### 4.3 UsageFault Status (UFSR) — CFSR[31:16]

| 位       | 名称           | 含义                                    |
| ------- | ------------ | ------------------------------------- |
| UFSR[0] | `UNDEFINSTR` | 执行了不存在 Thumb 指令                       |
| UFSR[1] | `INVSTATE`   | 试图切换到 ARM 态（ARM 态指令写到了 Cortex-M 不支持的） |
| UFSR[2] | `INVPC`      | PC 寄存器值不合法（如奇数地址但不是 Thumb）            |
| UFSR[3] | `NOCP`       | 执行了无协处理器的指令                           |
| UFSR[4] | `STKOF`      | 堆栈溢出（设置了 `USER_SETMPU` 时触发）           |
| UFSR[8] | `UNALIGNED`  | **非对齐访问**（但目标地址是合法的）                  |
| UFSR[9] | `DIVBYZERO`  | **除零**（需 `DIV_0_TRP` 置位）              |

## 五、传统 Keil 调试中的 HardFault 分析流程
### 5.1 第一步：崩溃后先别重启，立刻读寄存器
**这是最重要的一条原则。**
重启后栈帧被覆盖，寄存器全部清零，hardfault 信息永久丢失。
在 Keil 里直接暂停（不是 reset），然后在 Memory 窗口或 Watch 窗口读：
```c
// 在调试界面直接读取：
0xE000ED24   // SCB->CFSR
0xE000ED34   // SCB->HFSR
0xE000ED38   // SCB->MMFAR
0xE000ED3C   // SCB->BFAR
0xE000EDF14  // SCB->CCR
```
或在 Watch 窗口直接写：`(*(volatile uint32_t *)0xE000ED24)`
### 5.2 第二步：解读 CFSR 值
#### 情况 1：CFSR = 0x00000002
```
二进制: 0000 0000 0000 0000 0000 0000 0000 0010
      MMFSR[7:0] = 0x02
```
对应 MMFSR：
```
bit 1 = 1 → DACCVIOL (数据访问违规)
bit 0 = 0 → 不是指令访问问题
```
**结论**：程序写/读了一个无权访问的内存地址。
此时必须看 **MMFAR**（`0xE000ED34`）的值：
- MMFAR = `0x20003FFC` → 访问了 RAM 末尾（很可能是栈溢出）
- MMFAR = `0x00000000` → 访问了 NULL 指针
#### 情况 2：CFSR = 0x00008200
```
MMFSR = 0x00（无 MemManage fault）
BFSR  = 0x82 → bit7=1(BFARVALID) + bit1=1(PRECISERR)
```
**结论**：精确总线错误，BFAR 保存了访问地址。
#### 情况 3：CFSR = 0x00010000
```
UFSR = 0x0001 → bit0 = 1 → UNDEFINSTR
```
**结论**：执行了非法指令。最常见原因：函数指针的 bit 0 不是 1。
#### 情况 4：CFSR = 0x00040000
```
UFSR = 0x0004 → bit2 = 1 → INVPC
```
**结论**：PC 寄存器指向了一个非法地址（不对齐或超出范围）。
#### 情况 5：HFSR = 0x40000000
```
HFSR = 0x40000000 → FORCED
```
**重要**：FORCED 不是一种具体错误，而是说「别的 fault 上报了，但处理不过来」。
此时需要继续看 CFSR 的值，才能找到真正的根因：
```
SCB->CFSR = 0x...  ← 继续分析这里
```
### 5.3 第三步：用 PC 地址定位源码（最关键一步）
假设从寄存器窗口读到：
```
PC  = 0x08004F2A
LR  = 0x08004F58
SP  = 0x20003FF0
```
**Keil 中操作：**
1. 在 Disassembly 窗口，点击 Go to Address，输入 `0x08004F2A`
2. 看到的是汇编指令
3. 在源码窗口对应行高亮
**更精确的方式：用 addr2line**
在 Keil 的 Command 窗口（或者 ARM GCC 命令行）：
```
arm-none-eabi-addr2line -e Project.elf -f 0x08004F2A
```
输出：
```
main_loop at src/main.c:187
```
这就是崩溃的具体文件和行号。
### 5.4 第四步：根据 fault 类型套修复路径
```
┌──────────────────────────────────────────┐
│            CFSR = 0x????                 │
│                                          │
│  DACCVIOL (bit1)    ──→ MMFAR 看地址    │
│  ├── MMFAR = 0x00000000    → NULL 指针  │
│  ├── MMFAR = 0x20003FFC    → 栈溢出     │
│  └── MMFAR = 外设地址       → 访问了未   │
│                               开时钟的外设│
│                                          │
│  PRECISERR (bit1)     ──→ BFAR 看地址   │
│  ├── BFAR = APB 地址    → RCC 时钟未开   │
│  └── BFAR = Flash 地址  → 代码跑飞了     │
│                                          │
│  UNDEFINSTR (bit0)     ──→ 函数指针问题  │
│  └── 检查所有函数指针 bit0 是否 = 1      │
│                                          │
│  INVPC (bit2)          ──→ PC 被破坏   │
│  └── 栈溢出 / 全局变量被覆写              │
│                                          │
│  UNALIGNED (bit8)      ──→ DMA buffer   │
│  └── 检查对齐: __attribute__((aligned(4))│
│                                          │
│  FORCED (HFSR bit30)  ──→ CFSR 非零位   │
│  └── 继续分析 CFSR                        │
└──────────────────────────────────────────┘
```
### 5.5 完整调试案例
**场景**：固件启动后 3 秒崩溃，无任何串口输出。
```
Step 1: 崩溃后立刻暂停（不要按 Reset）
Step 2: 在 Memory 窗口读:
  地址 0xE000ED24 → CFSR = 0x00000082
Step 3: 解读:
  BFSR = 0x82
  → bit7=1: BFARVALID（地址有效）
  → bit1=1: PRECISERR（精确总线错误）
Step 4: 读 BFAR:
  地址 0xE000ED3C → BFAR = 0x40011000
Step 5: 查芯片手册:
  0x40011000 = GPIOA 寄存器地址
  GPIOA 挂载在 APB2 总线上
Step 6: 检查代码:
  __HAL_RCC_GPIOA_CLK_ENABLE();  ← 是不是漏了？
Step 7: 确认:
  确实在某个初始化函数里用了 GPIOA 但没开时钟
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_1, 1);
  → 加上 __HAL_RCC_GPIOA_CLK_ENABLE();
Step 8: 重新编译烧录 → 稳定运行
```
## 六、Keil 调试环境的 HardFault 配置
### 6.1 开启 UsageFault 和 BusFault（推荐）
默认情况下 MemManage/BusFault/UsageFault 都是禁用的，发生 fault 时统一上报到 HardFault。
**开启方式（在 SystemInit() 或 main() 开始处）：**
```c
// 开启 MemManage、BusFault、UsageFault
SCB->SHCSR |= SCB_SHCSR_MEMFAULTENA_Msk
            | SCB_SHCSR_BUSFAULTENA_Msk
            | SCB_SHCSR_USGFAULTENA_Msk;

// 这样 fault 会精确分类：
// MemManage → MemManage_Handler
// BusFault  → BusFault_Handler
// UsageFault→ UsageFault_Handler
// 只有它们被禁用或处理不了时，才到 HardFault
```

**为什么推荐开启？**
- 分类更精确：DACCVIOL vs PRECISERR 修复方向完全不同
- 有独立的 handler，可以做更多事情（如 panic log）
### 6.2 在 HardFault_Handler 里做 panic dump
**裸机版（不做 RTOS）：**
```c
void HardFault_Handler(void) {
    // 读取关键寄存器
    uint32_t r0 = __asm volatile("mov r0, r0");
    volatile uint32_t cfsr = SCB->CFSR;
    volatile uint32_t hfsr = SCB->HFSR;
    volatile uint32_t mmfar = SCB->MMFAR;
    volatile uint32_t bfar = SCB->BFAR;
    volatile uint32_t pc  = __builtin_return_address(0);
    volatile uint32_t lr  = __builtin_return_address(1);
    // 通过 UART 输出（如果 UART 初始化了）
    printf("=== HARD FAULT ===\n");
    printf("CFSR=0x%08lX HFSR=0x%08lX\n", cfsr, hfsr);
    printf("MMFAR=0x%08lX BFAR=0x%08lX\n", mmfar, bfar);
    printf("PC=0x%08lX LR=0x%08lX\n", pc, lr);
    // 停在这里，等调试器介入
    while (1);
}
```
**注意**：这个 handler 里 `printf` 依赖 UART 已经初始化。如果时钟还没配好，UART 不可用，可以用 ITM（Instrumentation Trace Macrocell）或者直接 RTT 输出。
### 6.3 FreeRTOS 下的 HardFault 处理
在 FreeRTOS 里，HardFault 发生在中断上下文，有几个关键点：
```c
// FreeRTOS config:
#define configINCLUDE_FREERTOS_TASK_HELP_HOOK 1
#define configUSE_STATS_FORMATTING_FUNCTIONS 1

// vApplicationStackOverflowHook - 栈溢出检测
void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName) {
    printf("STACK OVERFLOW: %s\n", pcTaskName);
    while (1);
}

// vApplicationMallocFailedHook - 堆分配失败
void vApplicationMallocFailedHook(void) {
    printf("MALLOC FAILED\n");
    while (1);
}

```
## 七、HardFault 分析的常见误区
### 7.1 误区 1：重启后读寄存器
```
错误做法：
  固件崩溃 → 按 Reset → 调试器停下 → 读寄存器 → 全是 0xFFFFFFFF

正确做法：
  固件崩溃 → 直接暂停（不按 Reset）→ 读寄存器
```

### 7.2 误区 2：只看 HardFault 寄存器，忽略 CFSR
```
错误做法：
  读到 HFSR = 0x40000000 (FORCED) → 就认为"是 HardFault"
  → 不再分析 CFSR → 根因不明
正确做法：
  FORCED 只是"别的地方出了问题，上报到 HardFault"
  → 继续看 CFSR → 找到真正的 fault 类型
```
### 7.3 误区 3：用 MMFAR/BFAR 直接定位 bug
```
MMFAR = 0x20003FFC（RAM 末尾）
→ 很多人直接搜索 0x20003FFC 在哪里被写入
→ 找不到，因为 MMFAR 保存的是"被访问的地址"
→ 不是"造成问题的代码写入的地址"
正确做法：
  用 MMFAR 推断问题类型（栈溢出？NULL？外设未开时钟？）
  → 用 PC 寄存器定位代码行 → 找到真正的问题点
```
  
### 7.4 误区 4：忽略 IMPRECISERR
```
IMPRECISERR = 不精确总线错误
→ BFAR 的地址是错的（因为总线访问和错误检测不是同步的）
→ 不能用 BFAR 直接定位
正确做法：
  IMPRECISERR → 查 PC 和 LR
  → 看 LR 指向的调用栈
  → 缩小可疑范围
  → 用串口/RTT 在可疑位置加日志，逐步逼近
```

## 八、总结：从为什么到怎么做
```
为什么有 HardFault？
├── CPU 需要一种机制来处理"不知道怎么处理"的错误
├── ARM Cortex-M 设计了分层 fault 体系
├── HardFault 是所有 fault 的最终汇聚点
└── 硬件自动压栈 → 保存现场 → 软件接手

HardFault 发生时 CPU 做了什么？
├── 硬件自动压栈（PC/LR/xPSR/R0-R3/R12）
├── LR 编码了异常返回方式
└── PC 指向了出错指令（这是定位关键！）

怎么用 HardFault 定位问题？
├── 第一步：崩溃后不重启，立刻读 SCB 寄存器
├── 第二步：解读 CFSR → 确定 fault 类型
├── 第三步：用 PC 地址 → addr2line → 定位源码行
├── 第四步：按 fault 类型走对应修复路径
└── 工具：Keil Memory 窗口 / Keil Command 窗口 / arm-none-eabi-addr2line
  

HardFault 属于哪方面的知识？
├── 体系结构（ARM Cortex-M 异常模型）
├── 嵌入式调试（故障诊断方法论）
├── 操作系统基础（RTOS 与 fault 的关系）
└── 硬件接口（SCB 寄存器映射）
```

  