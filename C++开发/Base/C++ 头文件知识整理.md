> 面向 C++ 初学者的头文件系统性笔记。从**是什么 → 为什么 → 怎么做**三角度梳理,
> 每节都配有可运行的最小示例。读完应能独立处理 90% 的头文件相关问题。
---
## 一、是什么(What)
### 1.1 头文件的定义
**头文件(`.h` / `.hpp`)** 是 C++ 中**仅含声明、不含(或极少含)实现**的源代码文件。
```cpp
// math_utils.h —— 一个典型头文件
#pragma once

int add(int a, int b);              // 函数声明
double pi = 3.14159;                // ❌ 错误:不要在头文件定义全局变量(后面解释)

struct Point {                      // 类型定义可以放在头文件
    double x, y;
};

class Circle {
public:
    Circle(double r);
    double area() const;
private:
    double radius_;
};
```

### 1.2 头文件 vs 源文件

| 文件类型 | 后缀 | 内容 | 编译产物 |
|---|---|---|---|
| 头文件 | `.h` / `.hpp` | 声明(declaration) | 不直接编译 |
| 源文件 | `.cpp` / `.cc` | 定义(definition) + 实现 | 编译为 `.o` |

**关键规则**:C++ 中**任何变量、函数都只能被定义一次,但可以声明多次**。头文件放声明,源文件放定义。
```cpp
// math_utils.h —— 声明
int add(int a, int b);

// math_utils.cpp —— 定义
#include "math_utils.h"
int add(int a, int b) { return a + b; }
```
### 1.3 `.h` vs `.hpp` 的区别
- `.h`:历史遗留,C/C++ 通用约定(很多 C 库也是 `.h`)
- `.hpp`:明确表示「C++ 专属头文件」,内部可用模板、命名空间等 C++ 特性

**业界没有强制规范**,但现代 C++ 项目倾向于:
- 纯 C 接口 → `.h`
- 用了模板 / 类 / C++ 特性 → `.hpp` 或仍用 `.h`

Boost 全部用 `.hpp`,Google Abseil 几乎都用 `.h`,你看到哪种都行,选一种保持一致。
### 1.4 编译模型:C++ 怎么用头文件
```
┌──────────────┐    ┌──────────────┐
│ foo.h        │    │ bar.h        │
│ (声明)       │    │ (声明)       │
└──────┬───────┘    └──────┬───────┘
       │                   │
       │  #include "foo.h" │
       ▼                   ▼
┌─────────────────────────────────┐
│ main.cpp  (编译器看到的实际内容) │
│   - foo.h 的所有声明             │
│   - bar.h 的所有声明             │
│   - main.cpp 自己的代码          │
└──────────────┬──────────────────┘
               │
               ▼ 编译
        ┌────────────┐
        │ main.o     │ (目标文件)
        └─────┬──────┘
              │ 链接(把 main.o 和 foo.o、bar.o 拼起来)
              ▼
        ┌────────────┐
        │ main.exe   │
        └────────────┘
```
**头文件不是被「编译」的,而是在编译源文件时被「文本粘贴」进去**。这是理解所有头文件问题的基石。

---

## 二、为什么(Why)
### 2.1 为什么需要头文件?
**核心答案:为了让编译器在不看到完整实现的情况下,也能正确生成调用代码。**
考虑两个文件:
```cpp
// add.cpp
int add(int a, int b) { return a + b; }

// main.cpp —— 这里只看到声明
int add(int, int);  // 编译器只关心:返回 int、需要两个 int
int main() { return add(1, 2); }
```
编译器在编译 `main.cpp` 时,**根本不需要知道 `add` 是怎么实现的**——它只需要知道:
- 返回类型是什么
- 参数是什么
- 函数名是什么

这样编译器就能:
1. **类型检查**:`add(1, 2)` 是否参数类型匹配
2. **生成调用代码**:按调用约定把参数压栈、call 到函数地址

**链接器**(linker)负责在最后把所有 `.o` 拼起来,真正把 `main.o` 里 `call add` 的地址替换成 `add.o` 里 `add` 函数的真实地址。
### 2.2 没有头文件会怎样?
假设只有一个 `add.cpp`,里面把声明和定义都写了:
```cpp
// add.cpp
int add(int a, int b) { return a + b; }
int main() { return add(1, 2); }
```
能跑。但**只要你想把 `add` 给别的文件用**——比如 `main.cpp` 想调用 `add`——就必须有人告诉 `main.cpp`:`add` 长什么样。**头文件就是干这个的**。
### 2.3 为什么会出现重复定义错误?
**没有 `#pragma once` 也没有 include guard**,会发生这个经典问题:
```cpp
// common.h —— 愚蠢的写法
int global_var = 42;  // 全局变量定义

// a.cpp
#include "common.h"

// b.cpp
#include "common.h"

// main.cpp
#include "a.cpp"   // ❌ 实际项目中不会,但原理一样
#include "b.cpp"   // ❌
```
最终 `main.cpp` 里 `global_var` 被定义了两次 → **链接错误 `multiple definition of 'global_var'`**。
**根本原因**:头文件是「文本粘贴」。同一份声明被多文件 include 时,声明没问题(声明可以重复),但**定义只能有一份**,于是冲突。

解决:
```cpp
// common.h —— 正确写法
#pragma once
extern int global_var;  // 声明:告诉编译器「别处有定义」
```

### 2.4 为什么 C# 没这些问题?
C# 在头文件问题上比 C++ 简单得多:

| 维度 | C++ | C# |
|---|---|---|
| 类型前向引用 | ❌ 不允许,必须先声明 | ✅ 任意顺序 |
| 多文件共享类型 | 手动 `#include` | 自动 |
| 接口与实现分离 | 头/源文件分开 | 类内部 partial |
| 编译单元 | 单个 `.cpp` | 单个 `.cs` 但跨文件可见 |

C# 编译器做**两遍扫描**,持有完整类型信息;C++ 沿用 C 的**单遍声明式编译**,出于性能与历史包袱。但代价就是你得手动管理头文件。
### 2.5 为什么头文件对编译速度影响巨大?
```
a.h 被 1000 个 .cpp #include
↓
修改 a.h
↓
所有 1000 个 .cpp 全部重新编译
```
这就是 **PCH(预编译头文件)、forward declaration、拆 header** 这些优化手段存在的根本原因——**减少头文件的传播半径**。

---

## 三、怎么做(How)
### 3.1 必须掌握的四个基本功
#### ① Include Guard / `#pragma once`
**每个头文件的第一行,二选一**:
```cpp
// 方式 1:#pragma once(现代推荐,99% 的编译器支持)
#pragma once

// 方式 2:传统 include guard(老项目、跨编译器兼容时用)
#ifndef ROBOT_LOGGING_LOG_PROPERTY_H
#define ROBOT_LOGGING_LOG_PROPERTY_H
// ... 内容 ...
#endif
```
为什么需要?因为头文件会被多个 `.cpp` 包含,需要防止同一个文件被展开多次。
#### ② 声明 vs 定义
```cpp
// 声明(declaration)——告诉编译器「有这个东西」
int add(int a, int b);
void foo();
class Bar;        // 前置声明
extern int g_x;   // 变量的声明

// 定义(definition)——给出具体内容
int add(int a, int b) { return a + b; }  // 函数体
void foo() { /* ... */ }                 // 函数体
class Bar { /* ... */ };                 // 类定义
int g_x = 42;                            // 变量定义
```
**记住**:
- 函数/类:**声明可以多次,定义只能一次**(整个程序范围内)
- `inline` 函数 / `constexpr` 函数 / `template` 函数:可以在头文件多次定义(ODR 例外)
#### ③ `#include` 的两种形式
```cpp
#include <iostream>       // 尖括号:系统/标准库头文件
#include "robot_logging/log_event.h"  // 引号:项目内自定义头文件
```
路径搜索:
- `<...>`:编译器配置的系统 include 路径
- `"..."`:先在当前文件所在目录找,再查系统路径(通常)
#### ④ 头文件放什么、不放什么

| 放头文件                | 不放头文件                     |
| ------------------- | ------------------------- |
| 类/结构体定义             | 函数实现(非 inline)            |
| 模板/内联函数             | 全局变量定义                    |
| 枚举、typedef、using    | 大量静态常量(除非 `inline const`) |
| 公开常量(`constexpr`)   | 仅 `.cpp` 内部用的辅助函数         |
| 其他需要的头文件 `#include` | 实现细节的 `#include`          |

### 3.2 前置声明(Forward Declaration)
**场景**:A 只想用 B 的指针/引用,不需要看到 B 的内部。
```cpp
// log_event.h
#pragma once
#include <string>
#include <vector>

namespace robot_logging {

struct LogProperty;   // 前置声明:告诉编译器「这是个 struct,叫这个名字」
struct Breadcrumb;    // 同上

struct LogEvent {
    std::vector<LogProperty> Properties;  // ✅ OK,std::vector 内部按指针实现
    // LogProperty value;               // ❌ 错误,需要完整定义
};

} // namespace robot_logging
```

**限制**:
- ✅ 可以用于:**指针、引用、`std::vector<T>`、`std::unique_ptr<T>` 等只持有指针的容器**
- ❌ 不可以用于:**值成员、继承、需要 `sizeof(T)` 的场景**
**为什么 `std::vector<T>` 可以?** 因为标准保证 `vector<T>` 内部存的是 `T*` + 大小/容量指针,实现里只用到 `T*` 的大小,不依赖 `T` 的完整定义。

### 3.3 头文件拆分原则
**不是「一个类一个文件」的机械做法,而是按「复用边界 + 编译依赖」拆**。

#### 决策树
```
这个类型会被谁用?
├─ 只有当前 .cpp 用 → 直接放 .cpp,别进头文件
├─ 多个类型间互相依赖 → 各自一个头文件 + 互相 #include
├─ 多个类型单向依赖 → 可以合并一个共头文件(co-header)
└─ 对外暴露的稳定 API → 必须独立头文件
```

#### 真实项目举例
**方式 A:每类型一文件**(Boost / Abseil)
```
include/robot_logging/
├── log_level.h
├── log_property.h
├── breadcrumb.h
├── log_event.h       # #include "log_property.h" 等
└── logger.h
```

**方式 B:相关类型共头文件**(很多中型项目)
```
include/robot_logging/
├── log_types.h       # LogLevel + LogProperty + Breadcrumb
├── log_event.h       # #include "log_types.h"
└── logger.h
```

**方式 C:分层 + fwd.h**(Spdlog / 大型库)
```
include/robot_logging/
├── fwd.h             # 所有类型的前置声明
├── types/
│   ├── log_event.h
│   └── log_property.h
├── sinks/
│   └── console_sink.h
└── logger.h
```

### 3.4 头文件包含的最佳实践
#### ① IWYU(Include What You Use)
**每个头文件必须自己 include 它直接用到的所有东西**,不要依赖「间接包含」。
```cpp
// ❌ 错误:依赖间接包含
// foo.h 用了 std::string,但没 #include <string>
// 而是依赖某个 #include "foo.h" 的文件先 #include 了 <string>

// ✅ 正确
// foo.h
#pragma once
#include <string>  // 自己用到,自己 include
```

#### ② 避免循环依赖
```cpp
// ❌ 错误
// a.h
#include "b.h"  // a 包含 b
class A { B* b_; };

// b.h
#include "a.h"  // b 又包含 a → 循环!
class B { A* a_; };
```

修复:
```cpp
// a.h
#pragma once
#include "b.h"        // A 用到 B 的完整定义(假设需要)
class A { B b_; };

// b.h
#pragma once
class A;              // ✅ 只前置声明
class B { A* a_; };    // B 只用到 A 的指针
```

#### ③ 用前向声明替代不必要的 include
```cpp
// ❌ 慢:任何用到 Sink 的地方都要重编 vector 和 memory
#include <memory>
#include <vector>
class Sink { /* ... */ };

// ✅ 快:用户只需要 Sink 指针时
class Sink;  // 前置声明就够了
```

### 3.5 处理重复 include 的几种姿势
#### ① `#pragma once`(推荐)
```cpp
#pragma once
```

#### ② Include Guard
```cpp
#ifndef PROJECT_MODULE_FILENAME_H
#define PROJECT_MODULE_FILENAME_H
// 内容
#endif
```

宏命名要保证全局唯一(用项目前缀),避免和其他库冲突。

#### ③ `#pragma once` vs include guard

| 特性 | `#pragma once` | include guard |
|---|---|---|
| 简洁 | ✅ | ❌ |
| 标准支持 | 大部分编译器,非 C++ 标准 | ✅ C++ 标准 |
| 抗「同路径不同文件」问题 | ❌(可能误判) | ✅ |
| 跨平台稳妥 | 99% 场景 OK | ✅ 100% OK |

**实际建议**:新项目直接 `#pragma once`,兼容老项目时两者都加。

### 3.6 常见错误与诊断

| 错误 | 原因 | 修复 |
|---|---|---|
| `Use of undeclared identifier 'Foo'` | 没 include 或没前置声明 | 加 `#include "foo.h"` 或 `class Foo;` |
| `Multiple definition of 'X'` | 头文件里写了非 inline 定义 | 用 `extern` 声明 / 把定义挪到 `.cpp` |
| `Redefinition of 'class X'` | 没 include guard | 加 `#pragma once` |
| `Incomplete type 'Foo'` | 用值成员但只有前置声明 | 改成指针 / include 完整头文件 |
| `X does not name a type` | 同上,且常因 include 顺序问题 | 检查 include 顺序,改用前置声明 |

### 3.7 进阶话题(了解即可)

- **PIMPL**:`unique_ptr<Impl>` 隐藏实现,加速编译、保留 ABI
- **预编译头文件(PCH)**:把不常改的大头(如 `<windows.h>`)预编译
- **C++20 Modules**:`import std;` —— 头文件体系的潜在继任者(目前生态不成熟)
- **Unity Build / Jumbo Build**:CMake 可配置,把多个 `.cpp` 合并编译加速

---

## 四、本项目实践建议(`robot_logging`)

基于你当前的目录结构(`/Users/albert/Downloads/cpp_practice/robot_logging/`),推荐如下整理:

```
include/robot_logging/
├── log_level.h          # 不动:enum + 工具函数
├── log_property.h       # 新建:从 log_event.h 抽出 LogProperty
├── breadcrumb.h         # 不动
├── log_event.h          # 改为 #include "log_property.h" "breadcrumb.h",删除本地定义
├── i_log_event_sink.h   # 不动
└── logger.h             # 不动
```

按这个布局调整后,你前面遇到的「`LogProperty` 未声明」错误会自然消失,而且未来加 sink、filter、enricher 时,各组件可以**按需 include**,不必被迫拉入全部依赖。

---

## 五、一页速查表

```cpp
// ✅ 标准头文件模板
#pragma once                                // 1. 防重复
#include <必要的系统头>                      // 2. 自给自足
#include "必要的项目头"                      // 3. 不依赖间接包含

namespace project {                         // 4. 包到命名空间

// 5. 前置声明(只用到指针/引用时)
class Foo;
struct Bar;

// 6. 类型定义
class MyClass {
    Bar* bar_;                              // 用指针 → 只需前置声明
    // Bar bar_;                           // 用值 → 需要完整定义
public:
    MyClass();
    void doSomething(const Foo& f);         // 参数引用 → 只需前置声明
};

// 7. inline / template 函数(可以放在头文件)
inline int square(int x) { return x * x; }
template<typename T>
T clamp(T v, T lo, T hi) { return v < lo ? lo : (v > hi ? hi : v); }

} // namespace project
```