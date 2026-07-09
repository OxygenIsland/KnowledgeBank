---
title: "[[C 语言基础]]"
type: Permanent
status: done
Creation Date: 2026-07-02 16:22
tags:
---
## 一、C 与 C# 的本质差异
理解这个差异是一切的前提。

| 维度         | C# (Unity)        | C (嵌入式)                        |
| ---------- | ----------------- | ------------------------------ |
| **运行环境**   | .NET 虚拟机 / Mono   | 直接跑在裸机硬件上，无运行时                 |
| **内存管理**   | GC 自动回收垃圾         | **手动管理**，或静态分配（嵌入式常用）          |
| **类型安全**   | 强类型，编译器严格检查       | 弱类型，很多隐式转换，容易踩坑                |
| **面向对象**   | 原生支持 class、继承、接口  | **无**，靠 struct + 函数指针模拟        |
| **异常处理**   | try/catch/finally | **无**，靠返回值和错误码                 |
| **int 大小** | 永远 32-bit         | **依赖平台！** 不同 CPU 可能是 16 或 32 位 |
| **字符串**    | `string` 对象，托管内存  | 字符数组 `char[]`，以 `\0` 结尾        |
| **bool**   | 原生 `bool` 类型      | C99 才有 `_Bool`，嵌入式常用整数代替       |
| **null**   | `null` 关键字        | `NULL` 宏（本质是 `0` 或 `(void*)0`） |

**最关键的心智转变**：C# 里你不用关心"这个变量占几个字节"，C 里**每一个字节都是钱**，嵌入式 RAM 可能只有几 KB，必须精确控制每个变量的大小。

## 二、基本数据类型
### 2.1 整数类型
```c
char    c = 'A';      // 通常 1 字节，存字符或小整数
short   s = 100;      // 通常 2 字节
int     n = 1000;     // 通常 4 字节（ARM Cortex-M 上是 32-bit）
long    l = 100000;   // 通常 4 字节（32-bit 平台）
long long ll = 1e18;  // 通常 8 字节
```


> ⚠️ **嵌入式大坑**：C 标准只规定 `int >= 16 bit`，具体大小**依赖编译器和 CPU 架构**。
> 同一段代码在 8-bit AVR 上 `int` 是 16-bit，在 STM32（ARM 32-bit）上是 32-bit。
> 所以嵌入式**永远用定宽类型**（见第三节），绝不用裸的 `int`。

每种整数都有 **有符号（signed）** 和 **无符号（unsigned）** 之分：
```c
signed   int a = -100;    // 可以是负数，范围 -2147483648 ~ +2147483647
unsigned int b =  100;    // 只能是 0 或正数，范围 0 ~ 4294967295
```
默认不写就是 `signed`。无符号类型用 `unsigned` 前缀，或简写 `uint`（后面会讲 typedef）。
### 2.2 浮点类型
```c
float  f = 3.14f;    // 单精度，4 字节，约 7 位有效数字
double d = 3.14159;  // 双精度，8 字节，约 15 位有效数字
```

> ⚠️ **嵌入式注意**：
> - Cortex-M4（STM32F405）有**硬件浮点单元（FPU）**，float 运算较快
> - Cortex-M0/M3 没有 FPU，float 运算由软件模拟，非常慢
> - 嵌入式能用整数就用整数（比如电压用 mV 单位存 int，而不是 V 存 float）

### 2.3 `void` 类型
```c
void func(void);          // 无参数、无返回值的函数
void *ptr;                // 无类型指针（可以指向任何类型）
```
## 三、定宽整数类型（嵌入式最常用）
这是 `<stdint.h>` 里定义的类型，**嵌入式代码几乎只用这些**，不用裸的 int/short/char：
```c
#include <stdint.h>   // HAL 库已经帮你包含了这个

// 无符号（unsigned）整数
uint8_t   u8  = 255;        // 固定 1 字节，范围 0 ~ 255
uint16_t  u16 = 65535;      // 固定 2 字节，范围 0 ~ 65535
uint32_t  u32 = 4294967295; // 固定 4 字节，范围 0 ~ 4294967295
uint64_t  u64 = ...;        // 固定 8 字节

// 有符号（signed）整数
int8_t    i8  = -128;       // 固定 1 字节，范围 -128 ~ 127
int16_t   i16 = -32768;     // 固定 2 字节，范围 -32768 ~ 32767
int32_t   i32 = -2147483648;// 固定 4 字节
int64_t   i64 = ...;        // 固定 8 字节
```
### 对应项目里的实际用法
```c
// freertos.c 第 1428 行附近：

static uint16_t regnums1 = 28;   // 寄存器数量，最大 65535，2字节够用
uint8_t  comm_status;             // 状态码 0~6，1字节完全够用
uint8_t  i;                       // 循环计数器，最多循环28次，1字节够
static uint8_t first_loop = 1;   // 只需要存 0 或 1，1字节
```

### 如何选择用哪种类型？（经验法则）

| 场景                 | 推荐类型            | 理由                 |
| ------------------ | --------------- | ------------------ |
| 字节操作、缓冲区索引、状态标志    | `uint8_t`       | 最节省内存              |
| 寄存器地址、数量、寄存器值      | `uint16_t`      | Modbus 寄存器是 16-bit |
| 时间戳、大计数、32-bit 寄存器 | `uint32_t`      | ARM 原生字长，操作最快      |
| 需要负数的传感器值（如电流、温度）  | `int16_t`       | 有符号 16-bit         |
| 函数返回状态码            | `int` 或自定义 enum | 够用就行               |
  > [!question]+ 寄存器数量为什么也要用uint16_t？
> Modbus 协议函数参数是 USHORT（uint16_t），使用uint16_t类型保持一致避免隐式转换警告；值本身用 uint8_t 也能跑，但风格不严谨
## 四、C 里没有 bool？— 整数当布尔值
### 4.1 为什么 `first_loop` 能当 bool 用？
```c
static uint8_t first_loop = 1;  // 声明为 uint8_t（无符号1字节整数）
if (first_loop)       // ← 这里把 uint8_t 当 bool 用！
{
    // ...
    first_loop = 0;   // 清零 = false
}
```
**原理**：C 语言从一开始就没有独立的 bool 类型（C99 才通过 `<stdbool.h>` 加入）。C 里的**真假判断规则**非常简单：
```
0         → false（假）
非 0 的值  → true（真）—— 包括 1、-1、255、任何非零值
```
所以任何整数都可以直接放进 `if()` 里用：
```c
uint8_t flag = 1;
if (flag)    { /* 执行 */ }   // flag != 0，为真
if (!flag)   { /* 不执行 */ } // !1 = 0，为假

flag = 0;
if (flag)    { /* 不执行 */ } // flag == 0，为假
if (!flag)   { /* 执行 */ }   // !0 = 1，为真
```
### 4.2 C99 的 `<stdbool.h>`（现代 C 做法）
```c
#include <stdbool.h>

bool flag = true;    // true 本质是 1，false 本质是 0
bool flag = false;

if (flag == true) { ... }
if (flag)         { ... }  // 等价写法
```
HAL 库代码里你会看到两种写法混用，本质一样。

## 五、变量修饰关键字
这四个关键字在嵌入式 C 里非常高频，每个都很重要。
### 5.1 `static` — 三种完全不同的用法
#### 用法 A：修饰局部变量（最常见）
```c
void Read_BMS_Info(void *argument)
{
    static uint8_t first_loop = 1;  // ← static 局部变量
    //
    for(;;) {
        if (first_loop) {
            first_loop = 0;   // 第一次循环后变为 0
        }
    }
}
```

|          | 普通局部变量        | static 局部变量       |
| -------- | ------------- | ----------------- |
| **生命周期** | 函数调用时创建，返回时销毁 | 程序运行期间**永久存在**    |
| **初始化**  | 每次调用都重新初始化    | **只初始化一次**（程序启动时） |
| **存储位置** | 栈（Stack）      | 全局数据区（BSS/Data段）  |
| **作用域**  | 只在函数内可见       | 只在函数内可见           |

`first_loop` 用 `static` 的原因：任务函数 `Read_BMS_Info` 永远不会返回（死循环），但为了逻辑清晰，"只执行一次"的标志必须在循环间保持值，`static` 就是为此而生。

#### 用法 B：修饰全局变量
```c
// freertos.c 里：
static uint8_t BMS_1_PoweronStatus = 0xFF;  // 文件级 static

// 含义：这个变量只在本 .c 文件内可见，其他 .c 文件的代码无法访问它
// 相当于 C# 里的 private（文件级封装）
```

#### 用法 C：修饰函数（用法同全局变量）
```c
static void helper_func(void) { ... }
// 这个函数只在本 .c 文件内可以被调用
```
### 5.2 `volatile` — 告诉编译器"这个变量会被意外改变"
```c
// freertos.c 里：
volatile uint32_t Flag_DataReceived;  // USB 接收标志
volatile uint32_t USB_RECVLen;        // 接收数据长度
```
**为什么需要 `volatile`？**
编译器在优化代码时，会把频繁访问的变量**缓存在 CPU 寄存器里**，不每次都去内存读取，以提高速度。但如果这个变量会被**中断服务程序**或**另一个任务**或**硬件外设**修改，CPU 寄存器里的值就是"过期"的，程序就会出错。
```c
// 没有 volatile 时，编译器可能优化成这样（错误！）：
uint32_t flag = 0;
void task(void) {
    uint32_t cached = flag;   // 编译器缓存到寄存器
    while (!cached) {         // 永远读缓存，永远是 0，死循环！
        do_something();
    }
    // 即使中断把 flag 改成 1，任务也感知不到
}

// 加 volatile 后，编译器每次都去内存读：
volatile uint32_t flag = 0;
void task(void) {
    while (!flag) {    // 每次循环都真正去内存读 flag
        do_something();
    }
    // 中断修改了内存里的 flag，下次循环就能感知到 ✓
}
```

**使用规则**：凡是在**中断和任务之间共享**的变量，必须加 `volatile`。
> C# 里也有 `volatile` 关键字，含义基本相同（用于多线程共享变量）。

### 5.3 `extern` — 声明"这个变量/函数定义在别的文件里"
```c
// freertos.c 里：
extern USHORT usMRegHoldBuf[MB_MASTER_TOTAL_SLAVE_NUM][M_REG_HOLDING_NREGS];
extern uint8_t sys_bin_ver[4];
```

C 语言没有命名空间，每个 .c 文件是独立的"编译单元"。如果变量定义在 `mb_m.c`，想在 `freertos.c` 里用，就需要 `extern` 声明——相当于告诉编译器"这个东西存在，先用着，链接时去找它"。
```
定义（只写一次，分配内存）：
    mb_m.c:       USHORT usMRegHoldBuf[...][...] = {...};
声明（可以写多次，不分配内存）：
    freertos.c:   extern USHORT usMRegHoldBuf[...][...];
    app_task.c:   extern USHORT usMRegHoldBuf[...][...];
```
### 5.4 `const` — 常量（编译后不可修改）
```c
const uint8_t MAX_RETRY = 3;            // 常量，不能修改
const char *msg = "Hello";              // 指向常量字符串的指针

// 对比 #define（预处理器宏）
#define MAX_RETRY 3                     // 宏，编译前文本替换
```

嵌入式里 `const` 变量通常会被编译器放进 **Flash（只读存储器）** 而不是 RAM，节省宝贵的 RAM 空间。

## 六、指针 Pointer
指针是 C 最难、最强大的特性。C# 基本用不到（unsafe 代码除外），但嵌入式 C 里无处不在。
### 6.1 最基本的概念
```c
int  value = 42;      // 普通变量，存储数值 42
int *ptr   = &value;  // 指针变量，存储 value 的【内存地址】
                      // & 是"取地址"运算符
                      // * 在声明时表示"这是一个指针"

printf("%d",  value); // 输出: 42        （变量的值）
printf("%p",  ptr);   // 输出: 0x200001C4（变量的地址，十六进制）
printf("%d", *ptr);   // 输出: 42        （* 在这里是"解引用"，读取地址处的值）

*ptr = 100;           // 通过指针修改 value 的值
printf("%d", value);  // 输出: 100       （value 被改了！）
```

**图示**：
```
内存地址  内存内容
...
0x200001C4:  [ 42 ]  ← value 变量
...
0x200001A0:  [0x200001C4] ← ptr 指针变量（里面存的是 value 的地址）
```
### 6.2 为什么嵌入式大量用指针？
#### 原因一：函数需要修改外部变量
```c
// C 函数参数是"值传递"（传副本），函数内修改不影响外部
void bad_func(int val) {
    val = 100;  // 只改了副本，外部 x 不变
}
void good_func(int *ptr) {   // 传地址
    *ptr = 100;              // 通过地址改原始数据，外部 x 变了
}
int x = 0;
bad_func(x);   // x 还是 0
good_func(&x); // x 变成 100 ✓
```
#### 原因二：操作硬件寄存器（嵌入式核心）
硬件外设的控制寄存器都有固定的内存地址，通过指针直接读写：
```c
// STM32 点亮一个 LED（不用 HAL 的底层做法）
#define GPIOB_ODR  ((volatile uint32_t *)0x40020414)  // GPIOB 输出数据寄存器地址
*GPIOB_ODR |= (1 << 5);   // 把第5位置1 → PB5 输出高电平 → LED亮
*GPIOB_ODR &= ~(1 << 5);  // 把第5位清0 → PB5 输出低电平 → LED灭
```
`0x40020414` 是写死在芯片数据手册里的物理地址，这就是"裸机"的含义。

#### 原因三：避免大数据的内存复制
```c
// 低效（复制整个数组）
void process(uint16_t data[51]) { ... }
process(merged_data);   // 复制 51×2=102 字节到栈上

// 高效（只传8字节地址）
void process(uint16_t *data) { ... }
process(merged_data);   // 只传指针，不复制数据
```
### 6.3 项目里的实际指针用法
```c
// app_task.c 里的 format_conversion 函数签名：
int format_conversion(uint8_t BAT_Index, uint8_t *dst, uint16_t *src)
//                                               ↑               ↑
//                         dst 是指向输出缓冲区的指针    src 是指向寄存器数据的指针
//                         函数直接往 dst 指向的地址写数据，不需要返回值传递
```

```c
// 调用处：
V2format_conversion(1, BMS_SendBuffer, merged_data);
//                     ↑               ↑
//          传入数组名，数组名本身就是第0个元素的地址（自动退化为指针）
```
### 6.4 指针类型修饰
```c
uint8_t       *p1;   // 指向 uint8_t 的指针
const uint8_t *p2;   // 指向【常量】uint8_t 的指针（不能通过 p2 修改值）
uint8_t *const p3;   // 【常量】指针（指针本身不能改变指向，但可以改值）
void          *p4;   // 无类型指针（可以指向任意类型，常用于通用接口）
```
### 6.5 & 的全部含义
#### 含义1：取地址运算符（一元，写在变量前）
```c
int a = 42;
int *p = &a;   // & 读作"取 a 的地址"
               // p 里存的不是 42，而是 a 在内存里的地址，比如 0x20001000

printf("%d",  a);  // 42       ← a 的值
printf("%p", &a);  // 0x20001000 ← a 的地址（%p 是打印地址的格式符）
printf("%p",  p);  // 0x20001000 ← p 里存的就是这个地址
```
#### 含义2：按位与运算符（二元，写在两个值之间）
```c
uint8_t a = 0b10110110;   // 182
uint8_t b = 0b00001111;   // 15
uint8_t c = a & b;        // 按位与，每一位单独做 AND
                          // 结果：0b00000110 = 6

// 嵌入式常用：提取某几位
uint8_t flash = frame[6];
if (flash & (1 << 0)) { /* bit0 是 1，闪光灯0亮 */ }
if (flash & (1 << 1)) { /* bit1 是 1，闪光灯1亮 */ }
```
#### 含义3：C++ 引用声明（写在类型后，声明时）
```c++
// 仅 C++ 有，C 没有这个用法
int a = 42;
int &ref = a;   // ref 是 a 的"别名"，不是独立变量

ref = 100;      // 修改 ref 就是修改 a
printf("%d", a); // 输出 100！

// C# 类比：类似 ref 参数
void Modify(ref int x) { x = 100; }  // C#
void Modify(int &x)    { x = 100; }  // C++（效果相同）
```
### 6.6`*` 的全部含义
#### 含义1：声明指针（写在类型和变量名之间，声明时）
```c
int    *p;     // p 是一个"指向 int 的指针"
uint8_t *buf;  // buf 是一个"指向 uint8_t 的指针"
void   *ptr;   // ptr 是一个"指向任意类型的指针"

// 项目里的例子：
int format_conversion(uint8_t *dst, uint16_t *src)
//                            ↑              ↑
//                   dst 是指针参数       src 是指针参数
```
#### 含义2：解引用运算符（一元，写在指针变量前，使用时）
```c
int a = 42;
int *p = &a;   // p 存了 a 的地址

printf("%d",  p);  // 打印地址值本身（0x20001000）
printf("%d", *p);  // * 读作"p 指向的地址处的值" → 打印 42
                   // 即：去 p 存的地址处，把那里的值取出来

*p = 100;          // 往 p 指向的地址写入 100 → a 变成 100！
printf("%d", a);   // 输出 100
```
**声明时的 `*`** 和 **使用时的 `*`** 读法完全不同：
```c
int *p = &a;   // 声明：p 是"指针"，* 是类型修饰符，读作"指针类型"
*p = 100;      // 使用：* 是解引用，读作"p 指向的值"
```
#### 含义3：乘法运算符（二元，写在两个值之间）
```c
int result = 3 * 4;     // 普通乘法，= 12
uint16_t crc = val * 2; // 就是乘法，没什么特别的
```
#### 最容易混淆的场景：`*` 和 `&` 紧挨在一起
```c
int a = 42;
int *p = &a;

// *p 和 &(*p) 和 a 的关系：
*p   == a        // 42，解引用得到值
&(*p) == &a == p // 地址，对解引用结果再取地址，还是原地址

// 常见组合：
int **pp = &p;   // pp 是"指向指针的指针"
                 // &p 取的是 p 这个指针变量本身的地址
```
## 七、数组与字符串
### 7.1 数组
```c
uint8_t  buf[8]   = {0};          // 8 个 uint8_t，全初始化为 0
uint16_t data[51] = {0};          // 51 个 uint16_t
uint8_t  frame[]  = {0xAA, 0x55}; // 自动推断大小为 2
// 访问（从 0 开始，和 C# 一样）
buf[0] = 0xFF;
buf[7] = 0x01;   // 最后一个合法索引
buf[8] = 0x01;   // ❌ 越界！C 不会报错，会写到相邻内存，严重 bug！
```
> ⚠️ **C 不做越界检查！** C# 数组越界会抛 `IndexOutOfRangeException`，C 会**默默地写错内存**，产生极难调试的 bug。

### 7.2 数组与指针的关系
```c
uint8_t arr[5] = {1, 2, 3, 4, 5};
uint8_t *p = arr;   // arr 数组名 == &arr[0]，可以直接赋给指针
*p       == arr[0] == 1    // 等价
*(p + 1) == arr[1] == 2    // 等价
*(p + 4) == arr[4] == 5    // 等价

// 所以这两个函数调用等价：
func(arr);    // 传数组名
func(&arr[0]); // 传第0个元素的地址
```

### 7.3 字符串（C 没有 string 类型！）
```c
char str1[] = "Hello";         // 字符数组：['H','e','l','l','o','\0']
                               // 注意：自动在末尾加 '\0'（null terminator）
char *str2 = "World";          // 指向字符串常量的指针（不能修改内容）

// 字符串长度
#include <string.h>
strlen(str1);  // 返回 5（不含 '\0'）
sizeof(str1);  // 返回 6（含 '\0'）—— sizeof 是编译时常量，不是函数

// 字符串复制
strcpy(dst, src);              // 复制（不安全，不检查长度）
strncpy(dst, src, sizeof(dst)-1); // 安全版本（指定最大长度）

// 格式化到字符串（类似 C# 的 string.Format）
sprintf(buf, "val=%d", val);
snprintf(buf, sizeof(buf), "val=%d", val);  // 安全版本
```

## 八、结构体 struct
C 里的 `struct` 相当于 C# 里的 `struct`（值类型），是组织多个相关变量的方式，也是 C 模拟"面向对象"的基础手段。
```c
// 定义
typedef struct {
    uint8_t  version;
    uint8_t  emergencyStop;
    uint8_t  relayEnabled;
    uint8_t  FlashLight;
    uint8_t  BackLightEffect;
    uint8_t  lightEffect;
    uint8_t  fanPwm;
} ControlProtocolState;

// 使用（项目里 app_task.c 的真实代码）
ControlProtocolState g_ctrl_state = {
    .version       = 1,   // 指定成员初始化（C99 特性）
    .emergencyStop = 0,
    .relayEnabled  = 0,
    .FlashLight    = 0,
    .lightEffect   = 0,
    .fanPwm        = 0
};

// 访问成员（用 . 运算符）
g_ctrl_state.fanPwm = 50;
uint8_t fan = g_ctrl_state.fanPwm;

// 通过指针访问（用 -> 运算符）
ControlProtocolState *p = &g_ctrl_state;
p->fanPwm = 50;       // 等价于 (*p).fanPwm = 50
```
### 内存布局（对齐）
```c
typedef struct {
    uint8_t  a;   // 1 字节
    // [编译器可能在这里插入 3 字节填充，让 b 对齐到 4 字节边界]
    uint32_t b;   // 4 字节
    uint8_t  c;   // 1 字节
    // [可能再填充 3 字节]
} Example;
// sizeof(Example) 可能是 12，而不是 6 ！

// 如果需要紧凑无填充（网络协议、硬件寄存器映射）：
typedef struct __attribute__((packed)) {
    uint8_t  a;   // 1 字节
    uint32_t b;   // 4 字节（紧跟 a，无填充）
    uint8_t  c;   // 1 字节
} Packed;
// sizeof(Packed) == 6 ✓
```
## 九、枚举 enum
```c
// 定义
typedef enum {
    MB_MRE_NO_ERR    = 0,  // Modbus 通信成功
    MB_MRE_NO_REG    = 1,  // 寄存器越界
    MB_MRE_ILL_ARG   = 2,  // 参数非法
    MB_MRE_REV_DATA  = 3,  // 数据帧错误
    MB_MRE_TIMEDOUT  = 4,  // 超时
    MB_MRE_MASTER_BUSY = 5,// 主站忙
    MB_MRE_EXE_FUN   = 6   // 执行失败
} eMBMasterReqErrCode;

// 使用（项目里的真实用法）
eMBMasterReqErrCode mb1_ret1;
mb1_ret1 = eMBMasterReqReadHoldingRegister(...);

if (mb1_ret1 == MB_MRE_TIMEDOUT) {
    // 处理超时
}
```
> ⚠️ **C 的 enum 是弱类型**：本质上是 `int`，可以和整数互相赋值，编译器不报错。
> C# 的 enum 是强类型，不能隐式和 int 互换。
## 十、typedef — 类型别名
```c
typedef unsigned char  uint8_t;   // 给 unsigned char 起别名 uint8_t
typedef unsigned short uint16_t;  // 给 unsigned short 起别名 uint16_t
typedef unsigned int   uint32_t;  // 给 unsigned int 起别名 uint32_t

// 给结构体起别名（避免每次写 struct xxx）
typedef struct {
    int x;
    int y;
} Point;          // 之后可以直接用 Point，不用 struct Point

Point p = {1, 2}; // ✓

// 给指针类型起别名（嵌入式常用，但也是常见混乱来源）
typedef MB_M_StackTypeDef *pMB_M_StackTypeDef;
// 之后 pMB_M_StackTypeDef 就代表"指向 MB_M_StackTypeDef 的指针"
// 项目里：pMB_M_StackTypeDef pMaster = &mbMasterStack;
```

> [!note]+ 为什么要在定义结构体时使用typedef
> 在 C 语言里，struct 和 typedef 是分开的两件事，通常合并写：
> ```c
> // 拆开看就是这两步：
>// 第一步：定义结构体本身
>struct BatteryProtocol
>{
>    const char *name;
>    void (*read1)(void);
>    ...
>};
>
>// 第二步：给这个结构体类型起一个别名
>typedef struct BatteryProtocol BatteryProtocol_t;
> ```
> // 合并写（你代码里的写法）：
> ```
> 
>typedef struct
>{
 >   const char *name;
 >   void (*read1)(void);
 >   ...
} BatteryProtocol_t;
// 等号左边是类型，等号右边是别名
>```
>不用 `typedef` 的话，每次声明变量都要写 `struct` 关键字
>```
>struct BatteryProtocol proto;          // 没有 typedef，必须写 struct
>BatteryProtocol_t proto;               // 有了 typedef，可以直接用别名
>```
>C++ 不需要这个——C++ 里 `struct BatteryProtocol` 定义后可以直接用 `BatteryProtocol` 作类型名。但 C 语言不行，所以 C 项目里几乎所有结构体都会配一个 `typedef`。

## 十一、函数基础
### 11.1 函数签名
```c
返回类型  函数名(参数类型 参数名, ...) {
    // 函数体
    return 返回值;
}

// 示例：
int format_conversion(uint8_t BAT_Index, uint8_t *dst, uint16_t *src) {
    // ...
    return BMS_SEND_FRAME_LEN;  // 返回打包后的长度
}
  
// 无返回值：
void Set_PWM_DutyCycle(uint8_t fan, uint8_t duty_cycle) {
    // ...
    // 不需要 return（或写 return; 无返回值）
}

// FreeRTOS 任务函数的固定签名：
void Read_BMS_Info(void *argument) {
    // argument 是任务创建时传入的参数，这里没用到，void* 代表任意类型
    for(;;) { ... }  // 必须死循环，永不返回
}
```
### 11.2 函数声明（原型）
```c
// 在头文件或函数使用前声明（告诉编译器这个函数存在）
int format_conversion(uint8_t BAT_Index, uint8_t *dst, uint16_t *src);
  
// 调用（可以在定义之前）
int len = format_conversion(1, buf, data);
  
// 定义（实现，通常在 .c 文件里）
int format_conversion(uint8_t BAT_Index, uint8_t *dst, uint16_t *src) {
    // ...
}
```
### 11.3 函数指针（C 的"委托"）
```c
// C# 里的 delegate / Action / Func
// C 里靠函数指针实现
// 声明函数指针类型
typedef void (*TaskFunction_t)(void *);

// 赋值和调用
TaskFunction_t task = Read_BMS_Info;
task(NULL);   // 等价于 Read_BMS_Info(NULL)

// FreeRTOS 就是这样接受任务函数的：
osThreadNew(Read_BMS_Info, NULL, &attr);
//          ↑ 这里传的就是函数指针
```
## 十二、预处理器指令
C 编译分两步：**预处理 → 编译**。预处理器在编译前对源代码进行文本替换。
### 12.1 `#define` — 宏定义
```c
// 常量宏（编译前文本替换，不占内存，无类型检查）
#define BMS_SEND_FRAME_LEN  54
#define MB1_READ_TIMEOUT_MS 1000
#define PI                  3.14159f
  
// 函数宏（危险，注意加括号）
#define MAX(a, b)  ((a) > (b) ? (a) : (b))  // ← 必须加括号！
// MAX(x+1, y) 展开为 ((x+1) > (y) ? (x+1) : (y)) ✓
// 不加括号的话 MAX(x+1, y) = x+1 > y ? x+1 : y 运算顺序可能出错
  
// 调试日志宏（项目里用到）
#define print_log(...)  printf(__VA_ARGS__)
// ... 和 __VA_ARGS__ 表示可变参数，让 print_log 和 printf 用法完全一致
```
### 12.2 条件编译 — 嵌入式最重要的特性之一
```c
// 根据宏是否定义来决定编译哪段代码
#ifdef MX_MB_PVT           // 如果定义了 MX_MB_PVT
    // PVT 版本的代码
#elif defined(MX_MB_DVT)   // 否则如果定义了 MX_MB_DVT
    // DVT 版本的代码
#else
    // 其他情况
#endif

// 防止头文件被重复包含（每个 .h 文件必有的结构）
#ifndef __MAIN_H           // 如果 __MAIN_H 没有被定义过
#define __MAIN_H           // 那就定义它（标记"已处理"）
    // 头文件内容
#endif                     // 第二次 #include 时，__MAIN_H 已定义，整个文件内容被跳过
```

**这个项目里宏定义在哪里？** 在 Keil 工程设置里（Project → Options → C/C++ → Preprocessor Symbols），编译时传入。这就是同一份代码可以为 DVT/PVT/LIRA_IS_V2 三个硬件板生成不同固件的原因。
  
## 十三、位操作（嵌入式核心技能）
C# 里几乎不用位操作，但嵌入式里**控制硬件寄存器必须用位操作**，因为寄存器的每一个 bit 往往都有独立含义。
### 13.1 六大位运算符
```c
uint8_t a = 0b10110010;  // 二进制字面量（C99 不支持，但 GCC 扩展支持）
uint8_t a = 0xB2;        // 十六进制，等价

// & 按位与（AND）— 清零特定位、提取特定位
0xB2 & 0x0F = 0x02       // 只保留低4位
0b10110010
0b00001111
──────────
0b00000010  = 0x02

// | 按位或（OR）— 置位（把某位设为1）
0x00 | 0x04 = 0x04       // 把 bit2 置1
0b00000000
0b00000100
──────────
0b00000100  = 0x04
  
// ^ 按位异或（XOR）— 翻转特定位
0xFF ^ 0x0F = 0xF0        // 翻转低4位
0b11111111
0b00001111
──────────
0b11110000  = 0xF0

// ~ 按位取反（NOT）— 翻转所有位
~0x0F = 0xF0              // 对于 uint8_t
~(uint8_t)0x0F = 0xF0     // 注意：~ 会提升为 int，要注意类型
  
// << 左移（相当于乘以 2^n）
1 << 3 = 8                // 0b00000001 → 0b00001000

// >> 右移（相当于除以 2^n）
0x80 >> 3 = 0x10          // 0b10000000 → 0b00010000
```
### 13.2 最常见的四种操作模式
```c
uint32_t reg = 0;
uint8_t  n = 5;  // 操作第 n 位（bit 5）

// ① 置位（Set Bit）：把第n位设为1，其他位不变
reg |= (1 << n);
// 原: 0b...0 0000000
// 或: 0b...0 0100000  (1<<5 = 0b00100000)
// 结: 0b...0 0100000

// ② 清位（Clear Bit）：把第n位设为0，其他位不变
reg &= ~(1 << n);
// ~(1<<5) = 0b...1 1011111（除第5位外全是1）
// 与原值AND，只有第5位被清零

// ③ 翻转（Toggle Bit）：
reg ^= (1 << n);

// ④ 读取某一位是否为1：
if (reg & (1 << n)) {   // 结果非零（真）= 该位为1
    // bit5 是 1
}
  
// 项目里的真实例子：
// app_task.c 里，补光灯用按位取值：
// frame[6] = Flash Light；按位取值，闪光灯0占bit0，闪光灯1占bit1
uint8_t flashlight = frame[6];
if (flashlight & (1 << 0)) { /* 闪光灯0 亮 */ }
if (flashlight & (1 << 1)) { /* 闪光灯1 亮 */ }
```

### 13.3 十六进制快速转换技巧
```
0x0 = 0000    0x8 = 1000
0x1 = 0001    0x9 = 1001
0x2 = 0010    0xA = 1010
0x3 = 0011    0xB = 1011
0x4 = 0100    0xC = 1100
0x5 = 0101    0xD = 1101
0x6 = 0110    0xE = 1110
0x7 = 0111    0xF = 1111

例：0xAA = 1010 1010
    0x55 = 0101 0101
    0xFF = 1111 1111
    0x00 = 0000 0000
```

## 十四、内存模型
嵌入式的内存比 PC 小得多，结构也更清晰。STM32F405 为例：
```
内存区域           地址范围           大小    说明
───────────────────────────────────────────────────────────
Flash（程序存储）  0x08000000 ~       1 MB    代码、const 变量、字符串常量
                  0x080FFFFF                  掉电不丢失，只能按扇区擦除
SRAM（运行内存）   0x20000000 ~       192 KB  程序运行时的数据
                  0x2002FFFF
  ├── .data 段                                初始化的全局变量（初始值从Flash复制来）
  ├── .bss 段                                 未初始化的全局变量（启动时清零）
  ├── Heap（堆）  从低地址往高增长              malloc/free 动态内存（嵌入式慎用）
  └── Stack（栈） 从高地址往低增长              局部变量、函数调用帧
```
### 14.1 四种存储类别对照
```c
// ① 全局变量 → .data 或 .bss 段（整个程序期间存活）
uint8_t BMS_SendBuffer[54] = {0};     // .bss（零初始化）
uint8_t BMS_1_PoweronStatus = 0xFF;   // .data（有初始值）

// ② static 局部变量 → 同全局变量一样在 .data/.bss（整个程序期间存活）
void func() {
    static uint8_t first_loop = 1;    // 在 .data 段，不在栈上
}

// ③ 普通局部变量 → 栈（函数返回时自动释放）
void func() {
    uint16_t merged_data[51] = {0};   // 在栈上，51×2=102 字节
    uint8_t  i;                        // 在栈上
}  // ← 函数返回后，merged_data 和 i 的内存自动回收

// ④ 动态分配 → 堆（手动管理）
void func() {
    uint8_t *buf = malloc(100);       // 从堆上分配 100 字节
    if (buf == NULL) { /* 分配失败 */ }
    // ... 使用 buf ...
    free(buf);                         // 必须手动释放！否则内存泄漏
    buf = NULL;                        // 避免野指针
}
```

> ⚠️ **嵌入式普遍不用 `malloc/free`**：
> - RAM 太小，堆碎片化后可能某次 malloc 返回 NULL
> - 堆管理有时间开销
> - 实时系统要求确定性，动态内存分配时间不确定
> - **嵌入式惯例**：所有缓冲区在编译时静态分配（全局/static），大小确定

### 14.2 栈溢出（嵌入式最常见的灾难性 bug）
```c
void dangerous_func() {
    uint8_t big_buf[4096];  // ← 在栈上分配 4KB！
    // STM32 默认任务栈可能只有 512 字节，直接溢出
    // 后果：覆盖相邻内存，程序行为完全不可预测
}

// 正确做法：大缓冲区用全局或 static
static uint8_t big_buf[4096];  // 在 .bss 段，安全
```
freertos.c 里每个任务都明确指定了栈大小：
```c
uint32_t Host_transmitBuffer[4096];  // 4096×4 = 16KB 栈空间
uint32_t Read_BatteryBuffer[512];    //  512×4 = 2KB 栈空间
```
## 十五、类型转换与强制转换
```c
// 隐式转换（自动，可能丢失精度）
uint8_t  a = 300;    // 300 > 255，溢出！a = 44（300 % 256）
int8_t   b = 200;    // 200 > 127，溢出！b = -56（有符号溢出）
float    f = 3 / 2;  // 整数除法！f = 1.0（不是 1.5）
float    g = 3.0 / 2;// 浮点除法，g = 1.5 ✓

// 显式强制转换（Cast）
uint16_t val = 1000;
uint8_t  low = (uint8_t)(val & 0xFF);  // 取低8位：val & 0xFF = 0xE8 = 232
uint8_t  hi  = (uint8_t)(val >> 8);    // 取高8位：1000>>8 = 3

// 项目里的真实用法（format_conversion 里拆16位寄存器为2个8位）：
dst[6] = (uint8_t)(src[18] >> 8);    // 高字节
dst[7] = (uint8_t)(src[18] & 0xFF);  // 低字节
```
  
## 十六、常见坑与嵌入式特有注意事项
### 坑1：整数溢出（无声无息）
```c
uint8_t x = 255;
x++;             // x = 0，不是 256！（0xFF + 1 = 0x100，溢出回 0）
x += 10;         // x = 10（从 0 加 10）

int8_t y = 127;
y++;             // y = -128！（有符号溢出，未定义行为）
```

### 坑2：未初始化的变量
```c
uint8_t buf[10];      // 全局变量：自动清零，buf[0] = 0
void func() {
    uint8_t local[10]; // 局部变量：值是随机的！（栈上的脏数据）
    if (local[0])      // 行为不确定，可能是 0 也可能非 0
}
// 养成习惯：声明时初始化
uint8_t local[10] = {0};  // 全部初始化为 0
```
### 坑3：有符号/无符号混用
```c
int8_t  a = -1;
uint8_t b = 255;
if (a == b) { ... }    // 结果取决于平台！
                        // a 提升为 int: -1
                        // b 提升为 unsigned int: 255（或 unsigned int: 4294967295 如果-1被扩展）
                        // 比较结果可能是 false 也可能是 true
```
### 坑4：除法截断
```c
int a = 7 / 2;    // a = 3，不是 3.5（整数截断）
int b = -7 / 2;   // b = -3（向零截断，不是 -4）
```
### 坑5：宏替换的副作用
```c
#define SQUARE(x)  x * x          // 危险！
SQUARE(1+2) → 1+2 * 1+2 = 1+2+2 = 5  // 期望 9，实际 5

#define SQUARE(x)  ((x) * (x))    // 正确：加括号
SQUARE(1+2) → ((1+2) * (1+2)) = 9 ✓

int i = 3;
SQUARE(i++) → ((i++) * (i++))     // i 被递增两次！未定义行为
// 带副作用的参数不要传给宏，应该用 inline 函数
```
### 坑6：野指针
```c
uint8_t *p;           // 未初始化指针，指向随机地址
*p = 100;             // ❌ 写入随机内存！程序崩溃或数据损坏
uint8_t *q = NULL;    // 初始化为 NULL（0）
if (q != NULL) {      // 使用前判断
    *q = 100;
}

// 释放后置 NULL
free(buf);
buf = NULL;           // 防止继续使用已释放的内存
```

### 嵌入式特有：大端/小端（Endianness）
```c
uint16_t val = 0x1234;
uint8_t *p = (uint8_t *)&val;

// 小端（Little Endian，x86/ARM 默认）：低地址存低字节
p[0] = 0x34;  // 低字节在前
p[1] = 0x12;  // 高字节在后

// 大端（Big Endian，网络字节序，Modbus 用的）：低地址存高字节
p[0] = 0x12;  // 高字节在前
p[1] = 0x34;  // 低字节在后
```

STM32 是小端，但 Modbus 协议规定大端传输，所以 `format_conversion` 里要手动拆字节：
```c
dst[6] = (uint8_t)(src[18] >> 8);    // 先发高字节（Modbus 大端）
dst[7] = (uint8_t)(src[18] & 0xFF);  // 再发低字节
```
## 十七、快速对照表：C# vs C
| 特性               | C# (Unity)                   | C (嵌入式)                                   |
| ---------------- | ---------------------------- | ----------------------------------------- |
| `bool`           | `bool b = true;`             | `uint8_t b = 1;` 或 `#include <stdbool.h>` |
| `string`         | `string s = "hi";`           | `char s[] = "hi";`                        |
| `null`           | `null`                       | `NULL`（宏，值为0）                             |
| 数组               | `int[] arr = new int[5];`    | `int arr[5] = {0};`                       |
| 类                | `class Foo { }`              | `typedef struct { } Foo;`                 |
| 属性               | `public int X { get; set; }` | 直接访问成员或用函数                                |
| `new`            | `Foo f = new Foo();`         | `Foo f; f.x = 0;` 或 `malloc`              |
| 继承               | `: Base`                     | 不支持（靠组合模拟）                                |
| 接口               | `interface IFoo { }`         | 函数指针结构体模拟                                 |
| `foreach`        | `foreach (var x in list)`    | `for (i=0; i<len; i++)`                   |
| 委托/事件            | `Action<int> cb;`            | `void (*cb)(int);`（函数指针）                  |
| `typeof`         | `typeof(int)`                | `sizeof(int)`                             |
| 异常               | `try { } catch { }`          | 不支持，靠返回值                                  |
| `using` 命名空间     | `using UnityEngine;`         | `#include "xxx.h"`                        |
| 泛型               | `List<T>`                    | 不支持（靠 `void*` 或宏模拟）                       |
| 反射               | `Type.GetType()`             | 不支持                                       |
| `Debug.Log()`    | `Debug.Log("msg");`          | `printf("msg\r\n");` 或 `print_log()`      |
| 多线程              | `Task.Run()`                 | `osThreadNew()`（FreeRTOS）                 |
| `Thread.Sleep()` | `await Task.Delay(500);`     | `osDelay(500);`                           |
| 互斥锁              | `lock(obj) { }`              | `osMutexAcquire(mutex, ...);`             |
| `volatile`       | `volatile int x;`（类似）        | `volatile uint32_t x;`                    |

## 附录：项目中出现的关键宏/类型速查
| 名称 | 类型/来源 | 含义 |
|------|---------|------|
| `uint8_t` | `<stdint.h>` | 无符号 8-bit 整数，0~255 |
| `uint16_t` | `<stdint.h>` | 无符号 16-bit 整数，0~65535 |
| `uint32_t` | `<stdint.h>` | 无符号 32-bit 整数 |
| `USHORT` | Modbus 协议栈 typedef | 等同于 `unsigned short`（uint16_t） |
| `eMBMasterReqErrCode` | Modbus 协议栈 enum | Modbus 读写操作的返回错误码 |
| `HAL_StatusTypeDef` | STM32 HAL 库 enum | HAL 函数返回值：OK/ERROR/BUSY/TIMEOUT |
| `GPIO_PinState` | STM32 HAL 库 enum | `GPIO_PIN_SET`(1) / `GPIO_PIN_RESET`(0) |
| `osStatus_t` | FreeRTOS CMSIS 封装 enum | RTOS 函数返回状态 |
| `osMutexId_t` | FreeRTOS | 互斥锁句柄（本质是指针） |
| `osThreadId_t` | FreeRTOS | 任务句柄 |
| `SemaphoreHandle_t` | FreeRTOS | 信号量句柄 |
| `volatile` | C 关键字 | 禁止编译器优化，每次去内存读 |
| `static` | C 关键字 | 局部变量持久化 / 文件级私有 |
| `extern` | C 关键字 | 声明外部定义的变量/函数 |
| `NULL` | `<stddef.h>` 宏 | 空指针，值为 0 |
| `osWaitForever` | FreeRTOS 宏 | 等待超时值：永远等待（0xFFFFFFFF）|
| `__attribute__((packed))` | GCC 扩展 | 结构体紧凑对齐（无填充字节）|
| `taskENTER_CRITICAL()` | FreeRTOS 宏 | 关中断（进入临界区）|
| `taskEXIT_CRITICAL()` | FreeRTOS 宏 | 开中断（退出临界区）|
