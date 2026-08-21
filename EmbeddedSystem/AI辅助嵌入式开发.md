---
title: "[[AI辅助嵌入式开发]]"
type: Permanent
status: ing
Creation Date: 2026-08-18 15:33
tags:
---
## 一、传统嵌入式开发的困境
### 1-1 调试循环的痛苦
```
写代码 → 编译 → 烧录 → 串口观察 → 猜问题 → 改代码 → 循环
```
- **编译-烧录-观察** 每次 3-5 分钟人工等待
- HardFault 只能靠 SCB 寄存器手工查手册翻译
- 总线协议（Modbus/CAN/I2C）没有自动化验证手段
- 寄存器文档靠记忆或翻 PDF
- 固件 bug 和硬件 bug 混在一起，极难定位
### 1-2 典型 [[HardFault|HardFault]]调试场景
```c
// 固件崩溃后，工程师手工操作：
1. 读 SCB_CFSR → 0x00000002
2. 翻手册 → "DACCVIOL: Data access violation"
3. 读 MMFAR → 0x20003FFC
4. 猜 → 可能是 NULL 指针
5. 搜索代码 → 找可疑位置
6. 加日志 → 重新编译烧录
// 每次迭代 5 分钟以上
```

### 1-3 传统工具链的断层
| 环节  | 工具              | 断层       |
| --- | --------------- | -------- |
| 知识  | PDF / 手册 / 搜索   | 碎片化，难以复用 |
| 编码  | IDE + Copilot   | 不理解硬件上下文 |
| 编译  | gcc / Keil      | 孤立工具，无闭环 |
| 烧录  | ST-Link Utility | 手动操作     |
| 调试  | 串口 + 经验         | 纯人工推理    |
## 二、AI 辅助嵌入式开发的演进路径
### 2-1 Level 0：纯手工（基线）
> 人 → 编译器 → 烧录器 → 手工验证
### 2-2 Level 1：AI 辅助编码
> 人 + AI 写代码 → 传统编译/烧录工具
- **进步**：代码生成效率提升
- **局限**：无法验证正确性，不知道是否真的 work
### 2-3 Level 2：带编译检查的 AI
> AI 写代码 → 编译器检查错误 → 人烧录验证
- **进步**：消灭语法错误
- **局限**：烧录和验证仍需人工
### 2-4 Level 3：[[MCP]] 工具链连接（当前主流）
> AI + 串口读取 + 部分寄存器 → 人确认烧录
- **进步**：部分自动化
- **局限**：无结构化诊断、无闭环迭代
### 2-5 Level 4：完整闭环（本次分享的工作流）←
> AI → 编译 → 烧录 → 结构化诊断 → 自愈修复 → 再次验证
>                                    ↑
                              AI 自主决策

## 三、系统框架总览
### 3-1 整体架构图
```
┌──────────────────────────────────────────────────────────────────┐
│                         Cursor AI Agent                          │
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐   │
│  │  Rules/     │    │  AGENTS.md  │    │  embedded-feature-  │   │
│  │  *.mdc      │    │  (项目事实)  │    │  loop.mdc (Agent)   │   │
│  └─────────────┘    └─────────────┘    └─────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                    MCP 工具层                                │  │
│  │                                                             │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐     │  │
│  │  │ stm32-build  │  │st32-hardware │  │st32-diagnostics│     │  │
│  │  │              │  │              │  │                │     │  │
│  │  │ cmake_full_  │  │ auto_flash_  │  │ modbus_read/   │     │  │
│  │  │ build        │  │ cycle        │  │ can_send       │     │  │
│  │  │              │  │              │  │                │     │  │
│  │  │ stm32_recom- │  │ stm32_snaps- │  │ stm32_svd_     │     │  │
│  │  │ pile         │  │ hot          │  │ decode         │     │  │
│  │  │              │  │              │  │                │     │  │
│  │  │ stm32_rtos_  │  │ stm32_analyze│  │ analyze_pid_   │     │  │
│  │  │ suggest      │  │ _fault       │  │ response       │     │  │
│  │  └──────────────┘  └──────────────┘  └────────────────┘     │  │
│  │                          │                                  │  │
│  │                  ┌───────┴───────┐                          │  │
│  │                  │  rag-knowledge │                         │  │
│  │                  │  (项目文档库)   │                         │  │
│  │                  └────────────────┘                         │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                   │
└──────────────────────────────│───────────────────────────────────┘
                               │ pyOCD / J-Link / Serial
                               ▼
                   ┌───────────────────────┐
                   │    STM32 目标板       │
                   │  (SWD + 串口 + RTT)   │
                   └───────────────────────┘
```

### 3-2 四大 MCP 服务器职责

| 服务器                   | 定位   | 核心能力                                           |
| --------------------- | ---- | ---------------------------------------------- |
| **stm32-build**       | 构建   | cmake_full_build / stm32_recompile / RTOS 配置建议 |
| **stm32-hardware**    | 硬件交互 | 烧录 / 寄存器 / 串口 / RTT / 结构化 fault 诊断             |
| **stm32-diagnostics** | 协议诊断 | Modbus / CAN / I2C / PWM / PID 分析 / 信号处理       |
| **rag-knowledge**     | 知识管理 | 芯片手册 / 协议文档 / 寄存器映射的向量检索                       |

### 3-3 Cursor Rules 分层体系

```
始终生效（alwaysApply）：
  ├─ stm32-conventions.mdc   → 编码规范 / HAL 约定 / 内存管理
  └─ mcp-workflow.mdc        → 工具调用顺序 / 重试上限 / RAG 优先

路径触发（glob）：
  ├─ stm32-rtos.mdc          → glob: Tasks/** / freertos.c
  └─ stm32-build.mdc         → glob: CMakeLists.txt

命名触发（name）：
  └─ embedded-feature-loop.mdc → 功能开发完整 Agent

项目继承：
  ├─ mx_board/AGENTS.md              → 根级项目事实
  └─ MX_MB_PVT/AGENTS.md            → 子项目覆盖
```

## 四、核心模块详解
### 4-1 rag-knowledge：永不失效的项目记忆
**痛点**：AI 凭记忆生成寄存器配置，结果地址错了一个 bit。
**解决方案**：芯片手册、通信协议、原理图要点全部向量化入库。
```
用户问："USART1 的 BRR 寄存器怎么配置？"
AI 查询 rag-knowledge
  → 找到 STM32F405 手册中 USART_BRR 的 bit 定义
  → 找到本项目中实际使用的波特率配置代码
  → 综合给出精确答案

不用 rag-knowledge 的 AI：
  → 靠记忆猜 → 大概率有错

```

**rag-knowledge 支持的文档类型**：
- 芯片参考手册（寄存器映射）
- 通信协议规格书（帧格式、时序）
- 原理图摘要（引脚复用、外设分配）
- 代码规范文档（项目约定）

### 4-2 stm32-hardware：硬件交互层
**包含的工具**：
```
连接层：
  stm32_connect         → SWD + 串口一键连接
  stm32_disconnect      → 断开连接
  
烧录：
  stm32_flash           → 基础烧录
  stm32_auto_flash_cycle→ 烧录 + 等待 Boot 标记 + 失败时自动诊断

寄存器：
  stm32_read_registers  → 读取 CPU/SCB 寄存器
  stm32_analyze_fault   → SCB 寄存器 → 结构化故障分析

日志：
  stm32_serial_read     → 串口增量读取（cursor 支持）
  stm32_rtt_read        → RTT 零开销日志

诊断：
  stm32_snapshot        → 一次调用拿全部诊断数据
  stm32_elf_symbol      → ELF 符号查找 / PC 地址 → 源码定位
  stm32_svd_decode      → SVD 寄存器位域解析
  stm32_stack_unwind    → DWARF 栈回溯

```

  

### 4-3 fault_data：结构化自愈诊断
**旧方案**（MCP 前）：
```python
# AI 只收到一行字符串：
fault_analysis = "IACCVIOL: Instruction access violation"
# AI 需要：查手册 → 猜根因 → 试方案 → 再验证
# 每次迭代：5分钟以上
```

**新方案**（fault_data）：
```json
{
  "fault_class": "DACCVIOL",
  "likely_causes": [
    "Accessed NULL or invalid pointer (faulting address: 0x20003FFC)",
    "Dereferencing a pointer that was never initialized"
  ],
  "addresses": {
    "faulting_pc": 134514730,
    "faulting_pc_hex": "0x08004F2A",
    "mmfar": 536846780,
    "mmfar_hex": "0x20003FFC"
  },
  "fix_suggestion": "Faulting address (MMFAR): 0x20003FFC\n1. Check RCC peripheral clock enable...\n2. Search for NULL-pointer usages..."
}
```

**AI 的改变**：不再猜，直接按 fault_class 走预设修复路径表。
### 4-4 stm32_snapshot：一步到位诊断
传统流程：
```
1. stm32_read_registers    → 读寄存器
2. stm32_analyze_fault     → 解析 fault
3. stm32_rtt_read          → 读 RTT
4. stm32_serial_read       → 读串口
5. stm32_elf_symbol        → 定位崩溃地址
// 5 个工具调用，5 次网络往返
```
`stm32_snapshot` 一次完成：
```python
result = stm32_snapshot(elf_path="build/Debug/MX_MB_PVT.elf")
# result 包含：
# - registers: CPU 全部寄存器
# - fault: fault_class + likely_causes + fix_suggestion
# - stack_trace: DWARF 栈回溯（函数名 + 源码位置）
# - rtt: RTT 日志文本
# - serial: 串口日志文本
```
### 4-5 stm32-diagnostics：协议层自动化验证
**Modbus 寄存器回读**：
```python
# 固件写入了某个保持寄存器，AI 想验证是否成功
modbus_read(address=1, register=0x0003, quantity=2)
# 返回实际寄存器值 → 与预期对比 → pass/fail
```
**CAN 总线诊断**：
```python
can_send(can_id=0x123, data=[0x01, 0x02])
can_listen(timeout_ms=500)
# 验证固件的 CAN 发送是否被正确接收
```
**PID 响应分析**：
```python
analyze_pid_response(serial_output="...PID: t=100 sp=50 pv=48...")
# 自动计算：overshoot / rise_time / settling_time / oscillation_count
# 给出调参建议
```

## 五、8 步闭环工作流（核心）
### 5-1 流程图
```
┌─────────────────────────┐
│ Step 1: 定义验收标准      │  ← 可机器验证的指标（寄存器值/日志标记）
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ Step 2: rag-knowledge    │  ← 项目文档检索（寄存器/帧格式/引脚）
│         知识检索         │
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ Step 3: 读懂现有代码      │  ← 找最近似实现，通读后再改
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ Step 4: 最小改动         │  ← 遵循接口约定，不发明平行模式
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ Step 5: stm32_recompile  │  ← 增量编译，错误不过夜
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│ Step 6: stm32_auto_flash│  ← 烧录 + 等 Boot 标记
│         _cycle          │
└────────────┬────────────┘
             ▼
      ┌──────┴──────┐
      │ boot 成功？ │
      └──────┬──────┘
        Yes / \No
        ↓     ↓
┌──────────┐  ┌──────────────────────────────────┐
│ 继续验证  │  │ 解析 fault_data                   │
│ 总线/日志 │  │ → fault_class → 修复路径表        │
└────┬─────┘  │ → elf_symbol 定位崩溃函数         │
     │        │ → 改代码 → Step 5                  │
     └────────┼──────────────────────────────────┘
              │
              ▼ (最多 5-8 轮)
┌─────────────────────────┐
│ Step 8: 状态报告        │  ← pass / partial / failed after N
└─────────────────────────┘
```
### 5-2 各步详解
#### Step 1 · 定义验收标准（关键！）
> **错误做法**：先写代码，后看效果
> **正确做法**：先定义"怎么算成功"
```python
# 用 todo list 记录验收条件：
- 串口输出 "Gary:BOOT"
- BMS 轮询任务 3 秒内检测到 SOC 值（0-100）
- CAN 总线收到电池电压帧（ID=0x201，data[0-1] = 实际电压值*10）
```
#### Step 2 · 知识检索（RAG-first）
> **禁止**用通用知识替代项目文档
```
❌ 用记忆生成寄存器地址 → 地址可能错
✓ 查 rag-knowledge → 直接命中本项目芯片文档
```
#### Step 3 · 读懂现有代码
> **禁止**重写现有模块
```
❌ 从零实现 Modbus 从站
✓ 找到 Tasks/Comm/modbus_task.c，继承其 HAL 调用模式
```
#### Step 4 · 最小改动
> 遵循开闭原则，不破坏现有接口
```
❌ 在 bms_task.c 加 #ifdef MC / #elif MX_MB_PVT
✓ 在 battery_protocol.c 绑定对应 proto_xxx.c
```
#### Step 5 · 编译验证
> 编译失败 → 不烧录
```
stm32_recompile(code="修改片段")
→ 返回编译错误
→ 修完后重新 compile
→ 确认无错后才进 Step 6
```
#### Step 6 · 烧录 + 验证
> 核心创新在这里
```
stm32_auto_flash_cycle(bin_path="...", wait_for="Gary:BOOT")
  → 烧录成功
  → boot 标记出现 → success
  ↓
  ↓ (失败时)
  → fault_data 结构化返回
  → fault_class = "DACCVIOL"
  → 检查 MMFAR 地址
  → 走 DACCVIOL 修复路径表
  → 改代码 → Step 5
```
#### Step 7 · 下游验证
> "发送返回 OK" ≠ 对方收到正确数据
```
固件通过 UART 发出了 Modbus 响应帧
→ modbus_read 验证寄存器值
→ 确认上位机收到了正确数据
→ 才算端到端验证完成
```
#### Step 8 · 结构化报告
```
## 结果
- **验收条件**：Step 1 定义的内容
- **结果**：pass / partial / failed after 5 attempts
- **证据**：日志行 + 寄存器值 + 总线数据
- **未验证**：CAN 接收侧（无硬件条件）
```
## 六、亮点总结
### 亮点 1：RAG-first 知识管理
- 项目文档（手册/协议/原理图）全部向量化
- AI 每次检索的是**本项目真实配置**，不是通用记忆
### 亮点 2：结构化故障诊断（fault_data）
- 从一行字符串 → 结构化 JSON（含分类/根因/地址/修复建议）
- AI 可基于分类直接走预设修复路径，不再盲猜
### 亮点 3：8 步闭环迭代
- 每次改代码都有硬件验证，不停留在"编译通过"
- 最多 5-8 轮自动重试，上限后停止，不死循环
### 亮点 4：MCP 工具链垂直整合
- 编译/烧录/诊断/知识 全在同一个对话内完成
- 无需切换窗口/终端/调试器
### 亮点 5：Cursor Rules 分层加载
- `alwaysApply` → 基础规范始终生效
- `glob` → 按文件路径精准匹配
- `name` → 按任务类型触发 Agent
- 项目继承 → 子目录覆盖/补充父级事实
### 亮点 6：协议层自动化验证
- Modbus/CAN/I2C 总线操作有工具级验证
- PID 响应有自动分析和建议调参
- 端到端数据链路可验证，不只是固件日志