---
title: "[[C++ 快速入门笔记]]"
type: Permanent
status: ing
Creation Date: 2026-06-20 11:26
tags:
---
  
## 1. 整体认知:C++ 和 C# 的核心差异

| 维度              | C# / Unity                     | C++                                                           |
| --------------- | ------------------------------ | ------------------------------------------------------------- |
| 编译方式            | 编译成 IL,运行在 CLR/Mono/IL2CPP 上   | 直接编译成机器码(原生代码)                                                |
| 内存管理            | 有 GC,自动回收                      | **没有 GC**,默认手动 `new`/`delete`,现代 C++ 用智能指针辅助                  |
| 基类              | 万物继承自 `object`                 | **没有统一基类**,类之间默认互不相关                                          |
| 指针              | 默认隐藏(对象都是引用类型),`unsafe` 才能用指针  | **指针是一等公民**,无处不在                                              |
| 值类型/引用类型        | `struct` 值类型,`class` 引用类型,泾渭分明 | `struct`/`class` 几乎等价(默认访问权限不同而已),是否"传值"取决于你怎么写(直接用 vs 指针/引用) |
| 头文件             | 没有,一个 `.cs` 文件即声明即实现           | **声明(`.h`)和实现(`.cpp`)通常分离**                                   |
| 编译单元            | 项目整体编译                         | 每个 `.cpp` 独立编译成 `.o`,最后链接(linker)成一个程序                        |
| 命名空间            | `namespace` + 项目自动管理           | `namespace`,但头文件容易污染全局,需要 `using` 小心使用                        |
| 接口              | `interface` 关键字                | 用**纯虚函数**模拟接口                                                 |
| 包管理             | NuGet                          | 没有统一标准,常用 vcpkg / conan,很多项目直接拷源码                             |
| 反射/特性 Attribute | 原生支持                           | 标准 C++ 不支持反射,UE 用宏 + 代码生成器(UHT)模拟                             |

**一句话总结**:C++ 把 C# 帮你藏起来的"内存"和"指针"全部暴露给你,代价是更复杂,好处是性能和控制力极致。

## 2. 基本程序结构与编译流程

### 2.1 Hello World
  
```cpp
#include <iostream>   // 类似 using System; 但这是"文本包含"不是模块导入
int main()            // C++ 程序入口固定叫 main,不在类里面
{
    std::cout << "Hello, World!" << std::endl;
    return 0;          // 返回给操作系统的退出码,0 表示成功
}
```
对比 C#:
```csharp
using System;
class Program {
    static void Main() {
        Console.WriteLine("Hello, World!");
    }
}
```

要点:
- `#include` 是**预处理指令**,在编译前把目标文件的内容**原样粘贴**进来(不是 import 模块这种语义)。
- `main` 函数必须存在且唯一,是程序唯一入口,不需要包在类里。
- `std::cout` 是标准输出流,`<<` 是被重载过的"插入"运算符。`std::endl` 换行并刷新缓冲区。
- `std` 是标准库的命名空间(类似 `System`)。
### 2.2 头文件 / 源文件分离(C++ 特有,务必理解)

C++ 工程通常拆成:
- **`.h` / `.hpp`(头文件)**:只写"声明"——类型定义、函数签名、类的成员声明。
- **`.cpp`(源文件)**:写"实现"——函数体的具体代码。
```cpp
// Math.h —— 声明
#pragma once   // 防止同一个头文件被重复 include(现代写法,等价于老式的 #ifndef include guard)
int Add(int a, int b);   // 只声明,不写函数体
```

```cpp
// Math.cpp —— 实现
#include "Math.h"
int Add(int a, int b) {
    return a + b;
}
```

```cpp
// main.cpp —— 使用
#include "Math.h"
#include <iostream>

int main() {
    std::cout << Add(1, 2) << std::endl;
}
```

为什么要这样分?因为 C++ 是**逐个 `.cpp` 文件独立编译**的(每个 `.cpp` 叫一个"编译单元"),编译器看到 `Add(1,2)` 这行代码时,只需要知道"有这么个函数,长这样"就能编译通过,不需要知道具体实现。等到**链接(link)**阶段,链接器才会去别的 `.o` 文件里找 `Add` 函数的真正实现并拼起来。
  
这也是为什么改了 `.h` 文件通常要重新编译很多文件,而只改 `.cpp` 的实现一般只需重新编译那一个文件——这是 C++ 编译慢的根源之一,也是为什么大型 C++ 项目特别在意"减少头文件依赖"。

### 2.3 编译流程四步走

```
源码(.cpp/.h)
   │  预处理(展开 #include / #define / #if)
   ▼
预处理后的源码
   │  编译(翻译成汇编/目标代码,做语法检查、类型检查)
   ▼
目标文件(.o / .obj) ——— 每个 .cpp 一个
   │  链接(把所有 .o 和库文件拼成一个可执行文件,解析跨文件的函数调用)
   ▼
可执行文件(.exe / 无后缀)
```

常见报错对应阶段:
- **编译错误(compile error)**:语法错、类型不对——通常是某个 `.cpp` 自己的问题。
- **链接错误(link error,如 `undefined reference`)**:声明了但没实现,或者忘了把对应 `.cpp`/库加入编译。这是新手最容易懵的报错类型,本质是"找不到函数的具体代码"。

## 3. 基础语法:变量、类型、运算符、控制流

### 3.1 基本数据类型

```cpp
int    a = 10;          // 整型,通常 4 字节(和平台/编译器相关,不像 C# int 强制 4 字节)
short  b = 1;            // 短整型,通常 2 字节
long   c = 100L;         // 长整型
long long d = 100LL;     // 长长整型,至少 8 字节,等价于 C# 的 long
float  e = 1.5f;         // 单精度浮点,4 字节,等价 C# float
double f = 1.5;          // 双精度浮点,8 字节,等价 C# double
char   g = 'A';          // 单字符,1 字节,等价 C# char(但 C++ char 本质就是个小整数)
bool   h = true;         // 布尔
wchar_t  wc = L'你';      // 宽字符(平台相关,不推荐,UE 多用 TCHAR)
unsigned int  ui = 10u;  // 无符号整型,没有 C# 那种统一的 uint 写法,但概念一样
size_t  sz = 100;        // 无符号整数类型,专门用来表示"大小/索引",sizeof 的返回类型
```

  
⚠️ **类型大小不是语言标准死规定的**,而是和平台/编译器相关(C# 的 `int` 永远是 4 字节,C++ 不是这样保证的,只保证大小关系 `short <= int <= long <= long long`)。需要确定大小时用 `<cstdint>` 里的 `int32_t`、`uint64_t` 等。

```cpp
#include <cstdint>
int32_t x = 5;   // 明确 4 字节有符号整数
uint8_t y = 255; // 明确 1 字节无符号整数,常用来表示字节
```

### 3.2 `auto`(类型推导,类似 C# 的 `var`)

```cpp
auto x = 10;        // 推导为 int
auto y = 3.14;       // 推导为 double
auto name = std::string("Tom"); // 推导为 std::string
```

### 3.3 `const` 和 `constexpr`

```cpp
const int MaxHP = 100;          // 运行期常量,类似 C# 的 readonly,值不能改
constexpr int MaxMP = 50;       // 编译期常量,必须在编译时就能算出来,类似 C# 的 const
```

区别:`const` 只保证"之后不能改",值可以在运行时才确定;`constexpr` 强制要求编译期就能算出来,常用于数组大小等场景。日常写代码,优先用 `const`,需要编译期常量(如模板参数、数组维度)用 `constexpr`。

### 3.4 运算符

和 C# 几乎一致:`+ - * / % ++ -- == != < > <= >= && || ! & | ^ ~ << >>` 都通用。

需要特别注意的几个:

- `/`:整数除法是**截断**而不是四舍五入,`7 / 2 == 3`(和 C# 一致)。

- `%`:取模,负数取模结果是实现定义/向零截断(C++11 起标准化为向零截断,和 C# 一致)。

- 没有 `??`(空合并运算符)、没有 `?.`(空条件运算符)——因为 C++ 的"空"概念用指针的 `nullptr` 表达,语义不完全一样。

- 三元运算符 `?:` 和 C# 一样。
### 3.5 控制流

```cpp
// if / else,和 C# 完全一样
if (hp <= 0) {
    // ...
} else if (hp < 20) {
    // ...
} else {
    // ...
}

// switch,和 C# 类似,但 C++ 默认会"穿透"(fall-through),需要手动写 break

switch (state) {
    case 0:
        DoA();
        break;          // 忘记写 break 会继续执行下一个 case!这是经典坑
    case 1:
        DoB();
        break;
    default:
        DoDefault();
}

// for 循环
for (int i = 0; i < 10; i++) {
    // ...
}

// 基于范围的 for(C++11 起),等价于 C# 的 foreach

std::vector<int> nums = {1, 2, 3};

for (int n : nums) {
    std::cout << n << std::endl;
}

for (auto& n : nums) {   // 加 & 表示引用,可以修改原元素,且避免拷贝
    n *= 2;
}

for (const auto& n : nums) { // 只读访问大对象时的推荐写法,避免拷贝又防止误改
    std::cout << n << std::endl;
}

// while / do-while,和 C# 一致
while (hp > 0) { /* ... */ }

do { /* ... */ } while (hp > 0);

```

## 4. 函数

### 4.1 基本定义

```cpp
int Add(int a, int b) {
    return a + b;
}

void PrintHello() {   // void 表示无返回值,和 C# 一致
    std::cout << "Hello" << std::endl;
}
```

### 4.2 默认参数

```cpp
void Heal(int amount, bool isMagic = false) {
    // ...
}

Heal(10);             // isMagic 用默认值 false
Heal(10, true);
```

(注意:C++ 没有 C# 的**具名实参**`Heal(amount: 10)`这种写法标准里不支持,只能按位置传。)

### 4.3 函数重载(Overload)

```cpp

int Add(int a, int b) { return a + b; }

double Add(double a, double b) { return a + b; }

```

和 C# 一样按参数类型/个数区分,编译期决定调用哪个(静态多态)。

### 4.4 传值 / 传引用 / 传指针(C++ 函数参数的三种方式,非常重要)


```cpp

void ModifyByValue(int x)      { x = 100; }     // 拷贝一份,不影响外面的变量

void ModifyByRef(int& x)       { x = 100; }     // 引用,直接改外面的变量(类似 C# 的 ref)

void ModifyByPointer(int* x)   { *x = 100; }    // 指针,通过地址改外面的变量,需要解引用

int main() {
    int a = 1;
    ModifyByValue(a);    // a 仍然是 1
    ModifyByRef(a);       // a 变成 100
    ModifyByPointer(&a);  // a 变成 100,注意要传地址 &a
}

```

对应 C# 心智模型:

- `void Foo(int x)` ≈ C# 默认传值
- `void Foo(int& x)` ≈ C# 的 `ref int x`(但 C++ 调用端不需要写特殊语法)
- `void Foo(const int& x)`:常用于**大对象只读传参**,既避免拷贝开销,又防止被修改,这是 C++ 里非常地道的写法,C# 里没有直接对应(`in` 参数算是接近)。

### 4.5 `inline` 函数

```cpp

inline int Square(int x) { return x * x; }

```

建议编译器把函数体直接"内联"展开到调用处,省去函数调用开销,常用于头文件里的小函数(也是为了避免多个 `.cpp` 包含同一头文件时产生"重复定义"链接错误)。

## 5. 数组与字符串

### 5.1 C 风格数组(原始,了解原理用)

```cpp
int arr[5];                       // 未初始化,值不确定
int arr2[5] = {1, 2, 3};           // 后面补 0 → {1,2,3,0,0}
int arr3[] = {1, 2, 3, 4};         // 编译器自动推断大小为 4

std::cout << arr3[0];               // 10
std::cout << sizeof(arr3);          // 字节数,如 16(4个int * 4字节),不是元素个数!
std::cout << sizeof(arr3) / sizeof(arr3[0]); // 老式获取元素个数的写法
```

⚠️ C 风格数组**不知道自己的长度**(传给函数时会"退化"成指针,长度信息丢失),也没有边界检查,越界访问是未定义行为(不会像 C# 抛 `IndexOutOfRangeException`,而是直接读写了不该读写的内存)。

### 5.2 `std::array`(C++11,固定大小,推荐替代 C 风格数组)

```cpp
#include <array>
std::array<int, 5> arr = {1, 2, 3, 4, 5};
arr.size();         // 5,知道自己的长度
arr.at(0);          // 带边界检查的访问,越界会抛异常
arr[0];              // 不带边界检查,更快
```
### 5.3 `std::vector`(动态数组,等价 C# 的 `List<T>`,最常用)

```cpp
#include <vector>
std::vector<int> v;          // 空动态数组
v.push_back(1);                // 尾部添加,等价 List.Add
v.push_back(2);
v.size();                      // 当前元素个数
v[0];                          // 索引访问
v.pop_back();                   // 移除最后一个元素
v.empty();                      // 是否为空
std::vector<int> v2 = {1, 2, 3}; // 列表初始化
for (int x : v2) { /* ... */ }    // 范围 for 遍历
```

### 5.4 字符串

```cpp
// C 风格字符串:本质是 char 数组,以 '\0' 结尾
const char* s1 = "Hello";
// std::string —— 推荐使用,等价 C# 的 string,但是可变的(类似 StringBuilder + string 的结合体)
#include <string>
std::string s2 = "Hello";
s2 += " World";                  // 拼接
s2.length();                      // 长度
s2.substr(0, 5);                  // 子串,Hello
s2.find("World");                 // 查找,返回索引,找不到返回 std::string::npos
s2[0];                            // 索引访问字符
s2 == "Hello World";              // 比较,已重载 ==,可以直接比较内容(不像裸指针比较地址)
// std::string 和 C# string 的关键区别:std::string 是可变的(mutable),
// 而 C# string 是不可变的(immutable)。s2 += "xxx" 真的在原地修改了内容(必要时重新分配内存)。
```

字符串拼接 / 格式化:

```cpp
#include <sstream>
std::ostringstream oss;
oss << "HP: " << 100 << ", MP: " << 50;
std::string result = oss.str();

// C++20 起有更接近 C# string.Format / interpolation 的 std::format

#include <format>
std::string s = std::format("HP: {}, MP: {}", 100, 50);

```

## 6. 结构体与类
### 6.1 `struct` vs `class`

C++ 里 `struct` 和 `class` 几乎一样,**唯一区别是默认访问权限**:
- `struct` 默认成员是 `public`
- `class` 默认成员是 `private`

```cpp
struct Point {       // 默认 public
    int x;
    int y;
};

class Point2 {        // 默认 private
    int x;            // 类外访问不了
    int y;
    
public:
    void Set(int nx, int ny) { x = nx; y = ny; }
};
```

约定俗成:**`struct` 用于纯数据聚合(POD,没什么行为的数据包)**,**`class` 用于有行为、需要封装的对象**。这和 C# 里 `struct`(值类型)/`class`(引用类型)的语义区分**完全不同**,不要混淆!

### 6.2 类的基本写法(声明在 .h,实现在 .cpp 是惯例)

```cpp
// Player.h
class Player {
public:
    Player(int hp, int mp);     // 构造函数声明
    ~Player();                   // 析构函数声明
    void TakeDamage(int amount);
    int GetHP() const;           // const 成员函数:承诺不修改成员变量
private:
    int m_HP;                    // 成员变量,m_ 前缀是常见命名习惯(非强制)
    int m_MP;
};

```

```cpp
// Player.cpp
#include "Player.h"

Player::Player(int hp, int mp) : m_HP(hp), m_MP(mp) {  // 初始化列表,见下文
    // 构造函数体
}

Player::~Player() {
    // 析构函数体,对象销毁时自动调用,常用于释放资源
}

void Player::TakeDamage(int amount) {
    m_HP -= amount;
}

int Player::GetHP() const {
    return m_HP;
}

```

`类名::函数名` 这种 `::` 叫**作用域解析运算符**,表示"这个函数是属于 `Player` 类的"。

### 6.3 构造函数初始化列表

```cpp
class Player {
public:
    Player(int hp, int mp) : m_HP(hp), m_MP(mp) {}  // 推荐写法
    // 等价但不推荐:
    // Player(int hp, int mp) { m_HP = hp; m_MP = mp; }
private:
    int m_HP;
    int m_MP;
};
```

初始化列表是在"构造"阶段直接初始化成员,而函数体里赋值是先默认构造再赋值,多一次开销(对于复杂类型如 `const` 成员、引用成员、没有默认构造函数的成员,**只能**用初始化列表)。

### 6.4 访问控制

```cpp
class Foo {
public:                    // 任何地方都能访问
    int a;
protected:                 // 自己和子类能访问
    int b;
private:                   // 只有自己能访问(默认)
    int c;
};
```
和 C# 的 `public`/`protected`/`private` 语义一致,只是 C++ 没有 `internal`。

### 6.5 静态成员

```cpp
class Player {
public:
    static int s_TotalCount;          // 声明
    Player() { s_TotalCount++; }
};
int Player::s_TotalCount = 0;          // 静态成员变量必须在类外定义(C++17 起可用 inline 解决)
```

等价 C# 的 `static` 字段,所有实例共享。

### 6.6 `this` 指针

```cpp
class Player {
public:
    void SetHP(int hp) {
        this->m_HP = hp;   // this 是指向当前对象的指针,等价 C# 的 this(但 C++ 是指针,需要 -> 访问)
    }
private:
    int m_HP;
};
```
### 6.7 拷贝构造函数 / 赋值运算符(C++ 特有的坑点)

```cpp
class Player {
public:
    Player(const Player& other) {       // 拷贝构造:用另一个对象初始化新对象时调用
        m_HP = other.m_HP;
    }
    Player& operator=(const Player& other) {  // 拷贝赋值:已存在的对象被赋值时调用
        if (this != &other) {
            m_HP = other.m_HP;
        }
        return *this;
    }
private:
    int m_HP;
};

```

如果你不写,编译器会自动生成一个"逐成员拷贝"的版本——**这对包含裸指针的类是危险的**,会导致"浅拷贝"(两个对象的指针指向同一块内存,析构时被 `delete` 两次,崩溃)。这是 C++ 里经典的"三/五法则"问题(Rule of Three/Five),也是智能指针存在的重要理由之一。
  
## 7. 面向对象:继承与多态
### 7.1 继承

```cpp
class Animal {
public:
    void Eat() { std::cout << "eating" << std::endl; }
};

class Dog : public Animal {    // 公有继承,等价 C# 的 class Dog : Animal
public:
    void Bark() { std::cout << "woof" << std::endl; }
};

Dog d;
d.Eat();    // 继承自 Animal
d.Bark();
```
⚠️ C++ 继承可以指定 `public` / `protected` / `private` 继承方式,**日常 99% 场景用 `public` 继承即可**,效果等同 C# 的继承。其他两种是 C++ 特有的小众用法,初学不用深究。

### 7.2 虚函数与多态(对应 C# 的 `virtual`/`override`)
```cpp
class Animal {
public:
    virtual void Speak() {                 // virtual 声明这是个"可以被子类重写"的函数
        std::cout << "..." << std::endl;
    }
    virtual ~Animal() {}                    // 基类析构函数几乎总是要写成 virtual!见下方说明
};

class Dog : public Animal {
public:
    void Speak() override {                 // override 关键字(C++11),编译器帮你检查签名是否真的重写了
        std::cout << "Woof" << std::endl;
    }
};

void MakeSpeak(Animal* a) {
    a->Speak();   // 多态:运行时根据实际对象类型调用 Dog::Speak 还是 Animal::Speak
}

Dog d;
MakeSpeak(&d);    // 输出 Woof
```

**为什么基类析构函数要写 `virtual`?**
```cpp
Animal* a = new Dog();
delete a;   // 如果 Animal 的析构函数不是 virtual,这里只会调用 Animal 的析构函数,
            // Dog 自己的析构函数不会被调用 → 资源泄漏!
```

这是 C++ 面向对象一个**极其经典的坑**,C# 里完全不用考虑这个问题(C# 的 GC 自动处理)。**只要一个类可能被继承且通过基类指针删除, 析构函数必须是 `virtual`。**

### 7.3 纯虚函数 = 接口 / 抽象类

```cpp
class IShape {            // 约定:接口类常以 I 开头(非强制,纯习惯)
public:
    virtual double GetArea() const = 0;   // "= 0" 表示纯虚函数,没有实现
    virtual ~IShape() {}
};

// IShape 不能被实例化(IShape s; 会编译报错),只能被继承
class Circle : public IShape {
public:
    Circle(double r) : m_Radius(r) {}
    double GetArea() const override { return 3.14159 * m_Radius * m_Radius; }
private:
    double m_Radius;
};

```

对应 C# 的 `interface IShape { double GetArea(); }`。C++ 没有专门的 `interface` 关键字,**纯虚函数 + 抽象类就是 C++ 模拟接口的标准方式**。C++ 还支持**多继承**(可以同时继承多个类/抽象类),C# 只支持单继承+多接口——C++ 多继承功能更强但也更容易踩坑(经典的"菱形继承"问题),初学阶段不建议主动设计多继承。

### 7.4 `final` 关键字
```cpp
class Dog final : public Animal { ... };  // 禁止 Dog 再被继承
class Cat : public Animal {
    void Speak() final override { ... }   // 禁止子类再重写 Speak
};
```

等价 C# 的 `sealed`。

## 8. 模板(对标 C# 泛型)
```cpp
// 函数模板
template<typename T>
T Max(T a, T b) {
    return a > b ? a : b;
}
Max(1, 2);          // T 自动推导为 int
Max(1.5, 2.5);       // T 自动推导为 double
Max<double>(1, 2.5); // 也可以显式指定 T

// 类模板
template<typename T>
class Box {
public:
    Box(T value) : m_Value(value) {}
    T GetValue() const { return m_Value; }
private:
    T m_Value;
};
Box<int> b1(10);
Box<std::string> b2("hello");
```

C++ 模板 vs C# 泛型 关键区别:
- **C# 泛型**是运行时机制(虽然值类型会做特化),一套 IL 代码,运行时按类型实例化。
- **C++ 模板**是**编译期**机制:`Max<int>` 和 `Max<double>` 在编译后是**两份完全独立的机器码**(称为"模板实例化"),这带来更好的性能(没有装箱/拆箱、没有运行时类型检查开销),代价是编译变慢、生成的二进制变大("代码膨胀")、报错信息有时非常冗长难懂。
- C++ 模板比 C# 泛型功能强得多(可以做编译期计算、特化、可变参数模板等,这是"模板元编程"领域),但学习曲线也陡得多。初学阶段会用 `vector<T>`、写简单的 `template<typename T>` 函数/类即可,不需要深入元编程。

## 9. Lambda 表达式
```cpp
[capture](parameters) -> return_type {
    body
};

auto add = [](int a, int b) { return a + b; };
std::cout << add(1, 2);   // 3
// 捕获外部变量
int x = 10;
auto printX = [x]() { std::cout << x; };        // 按值捕获:lambda 内部是 x 的一份拷贝
auto addX   = [&x]() { x += 1; };                  // 按引用捕获:可以修改外部的 x
auto captureAll = [=]() { /* 按值捕获所有外部变量 */ };
auto captureAllRef = [&]() { /* 按引用捕获所有外部变量 */ };

// 常配合 algorithm 使用
std::vector<int> v = {1, 2, 3};
std::for_each(v.begin(), v.end(), [](int x) { std::cout << x << " "; });

```

对比 C#:
```csharp
Func<int,int,int> add = (a, b) => a + b;
// C# 的 lambda 闭包默认按引用捕获外部变量(且是隐式的),
// C++ 必须显式声明捕获方式([x] 还是 [&x]),这是 C++ 更"显式可控"的体现。
```

## 10. 命名空间
```cpp
namespace MyGame {
    class Player { /* ... */ };
    namespace Utils {
        void Log(const std::string& msg);
    }
}
// 使用
MyGame::Player p;
MyGame::Utils::Log("hello");
using namespace MyGame;  // 引入整个命名空间,之后可以直接写 Player p; (不推荐在头文件里这样用)
using MyGame::Player;     // 只引入一个名字,更安全的折中写法
```

等价 C# 的 `namespace` + `using`。⚠️ **绝对不要在头文件(`.h`)里写 `using namespace xxx;`**——头文件会被很多 `.cpp` 包含,这会把命名空间"泄漏"到所有包含它的文件里,容易引发命名冲突,这是 C++ 圈子里非常公认的规范。

## 11. 运算符重载
C++ 允许自定义类型重写运算符的行为(C# 也支持,语法略有不同)。
```cpp
struct Vector2 {
    float x, y;
    Vector2 operator+(const Vector2& other) const {     // 重载 +
        return { x + other.x, y + other.y };
    }
    bool operator==(const Vector2& other) const {        // 重载 ==
        return x == other.x && y == other.y;
    }
};

Vector2 a{1, 2}, b{3, 4};
Vector2 c = a + b;     // 调用 operator+
bool eq = (a == b);
```
和 Unity 里 `Vector3` 重载 `+`/`-`/`*` 的思路完全一致,只是 C++ 语法是 `operator+`,C# 是 `public static Vector3 operator +(...)`。
  
## 12. 异常处理

```cpp
#include <stdexcept>
double Divide(double a, double b) {
    if (b == 0) {
        throw std::runtime_error("division by zero");  // 抛出异常
    }
    return a / b;
}

try {
    Divide(1, 0);
} catch (const std::runtime_error& e) {
    std::cout << "Error: " << e.what() << std::endl;
} catch (...) {                 // 捕获所有类型异常("万能 catch")
    std::cout << "Unknown error" << std::endl;
}
```

语法和 C# 的 `try/catch/throw` 很像,但**实践中 C++ 业界对异常的使用比 C# 保守得多**:很多游戏引擎(包括 Unreal Engine 默认配置)会直接**关闭异常**(因为异常处理有性能开销且不适合实时系统),转而用返回错误码、`std::optional`、断言(`assert`)等方式处理错误。学 UE 的话,养成"少依赖异常"的习惯会更顺畅。

## 13. 移动语义与右值引用(进阶难点)

这是 C++11 引入的、C# 完全没有对应概念的特性,初学可以先了解原理,不必强求精通。
### 13.1 左值与右值(简化理解)
- **左值(lvalue)**:有名字、可以取地址的东西,比如变量 `a`。

- **右值(rvalue)**:临时的、没有名字的值,比如 `10`、`a + b` 的结果、函数返回的临时对象。

### 13.2 为什么需要"移动"

```cpp
std::vector<int> CreateBigVector() {
    std::vector<int> v(1000000, 1);  // 一百万个元素
    return v;   // 如果是"拷贝"返回,意味着复制一百万个元素,代价巨大
}

std::vector<int> result = CreateBigVector();
```
传统做法(没有移动语义)需要**整体拷贝**这个巨大的 vector。移动语义允许直接把临时对象内部的资源(比如堆内存指针)"偷"过来,而不是复制内容——只是改了几个指针的指向,代价几乎是 O(1)。
```cpp
class Buffer {
public:
    Buffer(Buffer&& other) noexcept {       // 移动构造函数,&& 表示"右值引用"
        m_Data = other.m_Data;               // 直接"偷"走资源指针
        other.m_Data = nullptr;               // 把原对象置空,防止它析构时把资源也释放了
    }
private:
    int* m_Data;
};

std::vector<int> v1 = {1,2,3};
std::vector<int> v2 = std::move(v1);   // std::move 把 v1"变成"右值,触发移动而不是拷贝
                                          // 之后 v1 处于"被掏空"状态,不应再使用其内容
```
简化理解:**`std::move` 不是真的移动什么东西,它只是把一个左值"伪装"成右值,告诉编译器"这个对象我不要了,你可以随便拿走它的资源"。** 现代 C++ 标准库(`vector`、`string`、`unique_ptr` 等)都内置了移动语义,日常使用容器/智能指针时,你已经在享受移动语义带来的性能红利,不需要每次都自己手写。

## 14. 现代 C++(C++11/14/17/20)特性速览
C++ 标准每隔几年更新一次,"现代 C++"通常指 C++11 及以后,写法上已经和早期 C++98 的"裸指针+手动管理"风格有很大差距,日常学习/工作建议直接以现代写法为准。

| 特性                             | 引入版本  | 一句话说明                                |
| ------------------------------ | ----- | ------------------------------------ |
| `auto` 类型推导                    | C++11 | 类似 C# 的 `var`                        |
| 基于范围的 for                      | C++11 | 类似 C# 的 `foreach`                    |
| 智能指针 `unique_ptr`/`shared_ptr` | C++11 | 自动内存管理                               |
| Lambda 表达式                     | C++11 | 匿名函数                                 |
| `nullptr`                      | C++11 | 代替 `NULL`/`0` 表示空指针,类型更安全            |
| 右值引用 / 移动语义                    | C++11 | 避免不必要的拷贝,见第 18 节                     |
| `override` / `final`           | C++11 | 显式标记重写/禁止继承                          |
| 统一初始化 `{}`                     | C++11 | `int x{5};`、`Player p{100, 50};`     |
| `nullptr_t`、强类型枚举 `enum class` | C++11 | 见下方说明                                |
| 泛型 Lambda(`auto` 参数)           | C++14 | `[](auto a, auto b){ return a+b; }`  |
| 结构化绑定 `auto [a,b] = pair`      | C++17 | 拆包,类似元组解构                            |
| `std::optional<T>`             | C++17 | 表示"可能没有值",类似 C# 的 `Nullable<T>`/可空引用 |
| `if constexpr`                 | C++17 | 编译期条件分支(模板元编程常用)                     |
| 概念约束 `concepts`                | C++20 | 给模板参数加约束,报错更友好,接近 C# 泛型约束 `where`    |
| 协程 `co_await`                  | C++20 | 类似 C# 的 `async`/`await`,但更底层、更灵活也更复杂 |
| 模块 `import`                    | C++20 | 试图替代 `#include`,提升编译速度,目前生态还在过渡中     |
| 范围库 `<ranges>`                 | C++20 | 接近 C# LINQ 的链式写法                     |

### 14.1 `enum class`(强类型枚举,推荐替代传统 `enum`)
```cpp
enum class Color { Red, Green, Blue };   // C++11 起推荐写法
Color c = Color::Red;                      // 必须带上枚举名前缀,不会和其他枚举值混淆
// int x = c;                                 // 编译错误!不会隐式转 int,比传统 enum 更安全
enum OldColor { OldRed, OldGreen };        // 传统写法,值会污染外层作用域,且能隐式转 int(不推荐)
```
### 14.2 `std::optional`
```cpp
#include <optional>
std::optional<int> FindUserAge(const std::string& name) {
    if (name == "Tom") return 25;
    return std::nullopt;     // 表示"没找到"
}
auto age = FindUserAge("Tom");
if (age.has_value()) {
    std::cout << age.value();
}
if (age) {                    // optional 可以直接当 bool 用
    std::cout << *age;          // 也可以用 * 取值
}
```

## 15. 常见陷阱(从 C# 来的人最容易踩的坑)

1. **忘记 `delete`** → 内存泄漏。建议:学完基础后尽快切换到智能指针,几乎不再手写裸 `new`/`delete`。
2. **基类析构函数忘记写 `virtual`** → 多态删除时子类资源没释放。规则: **只要类可能被继承,析构函数默认写成 `virtual`。**
3. **悬空指针**:对象已经销毁,指针还在用。
4. **switch 忘记写 `break`** → 穿透到下一个 case。
5. **数组越界不报错**:`arr[10]` 在一个长度为 5 的数组上不会抛异常,而是读写了不属于这个数组的内存,行为未定义,可能"看起来正常运行"但悄悄破坏了别的数据,排查起来很痛苦。
6. **== 比较裸指针时比较的是地址,不是内容**:`const char* a = "abc"; const char* b = "abc"; a == b;` 结果不一定是 `true`(取决于编译器是否做了字符串常量合并),要比较内容应该用 `strcmp` 或者直接用 `std::string`。
7. **拷贝构造/赋值运算符没有正确处理裸指针成员** → 浅拷贝导致重复释放崩溃。
8. **整数除法截断**:`5 / 2` 结果是 `2` 不是 `2.5`,需要至少一个操作数是浮点数:`5.0 / 2`。
9. **头文件忘记加 `#pragma once`(或 include guard)** → 重复包含导致"重复定义"编译错误。
10. **在头文件里写 `using namespace std;`** → 命名污染,养成只在 `.cpp` 里这样写、或者干脆都加 `std::` 前缀的习惯。
11. **把 `vector` 等容器按值传给函数却没意识到在拷贝整个容器** → 大容器作为函数参数,记得用 `const std::vector<T>&` 传引用,避免无谓拷贝(等价 C# 里大 struct 传参考虑 `in`/`ref` 的思路,但 C++ 默认是值语义,更容易"无意中"产生整体拷贝)。