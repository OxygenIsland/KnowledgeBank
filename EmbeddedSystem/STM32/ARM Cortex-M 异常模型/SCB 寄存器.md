---
title: "[[SCB 寄存器]]"
type: Permanent
status: done
Creation Date: 2026-08-18 16:17
tags:
---
## 一句话定义
**SCB（System Control Block）** 是 ARM Cortex-M 内核里一组集中管理「系统异常、fault 处理、芯片配置」的寄存器块。固件通过读写它来了解"哪里出错了"、"开启了哪些中断"、"如何配置系统行为"。
## SCB 在哪里？

SCB 不是外设，是 **ARM Cortex-M 内核的一部分**。所有基于 Cortex-M 的芯片（STM32、LPC、NXP Kinetis 等）都有相同的 SCB 结构。
它的地址固定在内存映射的 **System address space** 区域：
```
0xE000E000 ────────────────── 私有外设总线（PPB）
  ├─ 0xE000E008  ── ITM (Instrumentation Trace)
  ├─ 0xE000ED00  ── SCB  ←
  ├─ 0xE000EF00  ── SysTick
  ├─ 0xE000EF10  ── NVIC
  └─ ...
```
SCB 的起始地址是 `0xE000ED00`，大小约 1KB。
## SCB 里装了什么？
SCB 内部由多个寄存器组成，按功能分成 4 类：
### 第一类：系统控制

| 寄存器 | 地址 | 作用 |
|---|---|---|
| `CPUID` | 0xE000ED00 | 只读，芯片 ID（内核版本、厂商） |
| `ICSR` | 0xE000ED04 | 中断控制与状态（挂起/激活） |
| `VTOR` | 0xE000ED08 | 中断向量表偏移地址 |
| `AIRCR` | 0xE000ED0C | 复位、优先级分组 |
| `SCR` | 0xE000ED10 | 睡眠/深度睡眠控制 |
| `CCR` | 0xE000ED14 | 栈对齐/除零/NRFX 等配置 |
| `SHP[0-11]` | 0xE000ED18 | 外设中断优先级配置 |

### 第二类：Fault 状态（最常用）

| 寄存器 | 地址 | 作用 |
|---|---|---|
| `CFSR` | 0xE000ED28 | **全部 fault 状态**，分 3 组 |
| `HFSR` | 0xE000ED2C | HardFault 专用状态 |
| `DFSR` | 0xE000ED30 | Debug fault 状态 |
| `MMFAR` | 0xE000ED34 | MemManage fault 地址 |
| `BFAR` | 0xE000ED38 | BusFault 地址 |
| `AFSR` | 0xE000ED3C | 辅助 fault 状态 |

### 第三类：CoreDebug（调试用）

| 寄存器 | 地址 | 作用 |
|---|---|---|
| `DHCSR` | 0xE000EDF00 | 调试 halt/步进控制 |
| `DCRDR` | 0xE000EDF08 | 调试寄存器读/写 |
| `DEMCR` | 0xE000EDFC | 调试异常控制 |
  
### 第四类：SHPRx（中断优先级）

| 寄存器 | 地址 | 作用 |
|---|---|---|
| `SHPR2` | 0xE000ED1C | SVC/PendSV/SysTick 优先级 |
| `SHPR3` | 0xE000ED20 | Pri 11-12 配置 |

## SCB 不是一个寄存器，是一个寄存器组
**常见误解**："SCB 寄存器"是一个寄存器。
**实际情况**：`SCB` 是一个结构体，里面包含 20+ 个寄存器。在 C 代码里：
```c
// 这是 CMSIS 标准的定义（stm32f4xx.h 中）
typedef struct {
    volatile uint32_t CPUID;      // 0xE000ED00
    volatile uint32_t ICSR;      // 0xE000ED04
    volatile uint32_t VTOR;      // 0xE000ED08
    volatile uint32_t AIRCR;     // 0xE000ED0C
    volatile uint32_t SCR;        // 0xE000ED10
    volatile uint32_t CCR;        // 0xE000ED14
    volatile uint32_t SHP[12];   // 0xE000ED18
    volatile uint32_t SHCSR;     // 0xE000ED24
    volatile uint32_t CFSR;      // 0xE000ED28
    volatile uint32_t HFSR;      // 0xE000ED2C
    volatile uint32_t DFSR;      // 0xE000ED30
    volatile uint32_t MMFAR;     // 0xE000ED34
    volatile uint32_t BFAR;      // 0xE000ED38
    volatile uint32_t AFSR;      // 0xE000ED3C
    // ...
} SCB_TypeDef;

  
// 使用方式：
SCB->CFSR  // 读 fault 状态
SCB->MMFAR // 读 MemManage fault 地址
SCB->SHCSR // 读 handler 使能状态
```

## SCB vs NVIC：别混淆

SCB 和 NVIC 都在 0xE000E000 区域，但职责不同：

|          | SCB                                     | NVIC                 |
| -------- | --------------------------------------- | -------------------- |
| **职责**   | 系统控制、异常/fault 管理                        | 外设中断的使能/优先级/挂起       |
| **管理对象** | Reset / NMI / HardFault / SysTick / SVC | 外设中断（UART、DMA、TIM 等） |
| **地址**   | 0xE000ED00                              | 0xE000E100           |
| **类比**   | 操作系统内核                                  | 外设中断管理器              |

**简单记忆**：
```
SCB  → 管"系统出问题了怎么办"（fault/异常）
NVIC → 管"外设想打断 CPU 怎么办"（中断优先级）
```

## 实际使用场景
### 场景 1：读 HardFault 状态
```c
// 当 HardFault 发生时，读取：
uint32_t cfsr = SCB->CFSR;  // fault 分类
uint32_t hfsr = SCB->HFSR;  // hardfault 专用
uint32_t mmfar = SCB->MMFAR; // 访问地址（如果是 DACCVIOL）
uint32_t bfar = SCB->BFAR;   // 访问地址（如果是 PRECISERR）
```
### 场景 2：配置栈对齐/除零检测
```c
// 启用除零 fault（默认关闭）
SCB->CCR |= (1 << 4); // SCB_CCR_DIV_0_TRP
```
### 场景 3：配置中断优先级分组
```c
// 在 AIRCR 里设置优先级分组
SCB->AIRCR = (0x5FA << 16) | (3 << 8) | (0x400); // 复位值，3=4位抢占2位响应
```
### 场景 4：跳转到指定地址（ bootloader 场景）
```c
// 从 Application 更新到 bootloader
void jump_to_bootloader(void) {
    SCB->VTOR = BOOTLOADER_ADDR; // 重定向向量表
    __set_MSP(*(volatile uint32_t *)BOOTLOADER_ADDR); // 设置栈指针
    ((void (*)(void))(*(volatile uint32_t *)(BOOTLOADER_ADDR + 4)))(); // 跳转
}
```
## 总结
```
SCB 是什么？
  ARM Cortex-M 内核里的"系统控制块"

为什么叫 SCB？
  它控制的是"系统级"的事：异常/fault/复位/睡眠/向量表
  不是外设（GPIO/UART/TIM），是内核自带的管理单元

它在哪里？
  0xE000ED00，固定地址，所有 Cortex-M 芯片通用

它管什么？
  1. Fault 状态（崩溃了？什么原因？）
  2. 中断/异常控制（向量表、优先级、挂起）
  3. 系统配置（睡眠模式、栈对齐、除零检测）
  4. 调试控制（halt、步进）

和 NVIC 的区别？
  SCB = 系统的（fault/异常）
  NVIC = 外设的（外设中断）
```