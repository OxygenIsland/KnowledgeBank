---
title: "[[Shallow Copy and Deep Copy]]"
type: Reference
status: done
Creation Date: 2025-05-02 13:45
tags:
---
在面向对象编程中，​**​浅拷贝（Shallow Copy）​**​和​**​深拷贝（Deep Copy）​**​是两种关键的对象复制策略，它们的核心差异在于如何处理对象内部的引用类型数据。

## **一、概念对比​**​

| |浅拷贝（Shallow Copy）|深拷贝（Deep Copy）|
|---|---|---|
|​**​定义​**​|仅复制对象的顶层值类型字段和引用地址|递归复制对象及其所有引用对象的完整数据|
|​**​引用类型处理​**​|副本与原对象共享同一引用对象（指针指向同一内存）|创建引用对象的全新副本（生成独立内存空间）|
|​**​内存消耗​**​|低（仅复制地址）|高（复制全部引用链对象）|
|​**​性能​**​|快（直接内存复制）|慢（需递归处理引用对象）|
|​**​典型实现​**​|`MemberwiseClone()`（C#）|手动递归克隆、序列化/反序列化、第三方工具库|

## ​**​二、代码示例​**​
### 场景：包含引用类型的对象
```csharp
public class Employee {
    public int Id;          // 值类型
    public List<string> Skills = new List<string>(); // 引用类型
}
```
### 1. 浅拷贝实现
```csharp
public Employee ShallowCopy() {
    return (Employee)this.MemberwiseClone(); // 仅复制Skills列表的引用
}
```
### 2. 深拷贝实现
```csharp
public Employee DeepCopy() {
    var copy = (Employee)this.MemberwiseClone();
    copy.Skills = new List<string>(this.Skills); // 创建新列表
    return copy;
}
```
### 测试结果
```csharp
var original = new Employee { Id = 1, Skills = { "C#", "SQL" } };

// 浅拷贝测试
var shallowCopy = original.ShallowCopy();
shallowCopy.Skills.Add("Python");
Console.WriteLine(original.Skills.Count); // 输出 3（原对象被修改！）

// 深拷贝测试
var deepCopy = original.DeepCopy();
deepCopy.Skills.Remove("SQL");
Console.WriteLine(original.Skills.Count); // 仍输出 3（原对象不受影响）
```
### **三、内存结构示意图​**​

```
浅拷贝：
┌───────────┐       ┌────────────┐
│ 原对象     │       │ 副本        │
├─────┬─────┤       ├──────┬─────┤
│ Id=1│ ●───┼──────►│List A│[C#,SQL]
└─────┴─────┘       └──────┴─────┘

深拷贝：
┌───────────┐       ┌────────────┐
│ 原对象     │       │ 副本        │
├─────┬─────┤       ├──────┬─────┤
│ Id=1│ ●──┼─────┐  │ Id=1 │ ●   │
└─────┴─────┘    │  └──────┴─────┘
                 ▼         │
              ┌──────┐     ▼
              │List A│   ┌───────┐
              └──────┘   │List B │
                         └───────┘
```
### **四、使用场景选择​**​
#### ✅ 适合浅拷贝的情况
1. 对象​**​仅包含值类型字段​**​（如坐标点`Point`结构）
2. 引用字段是​**​不可变对象​**​（如`string`, `DateTime`）
3. ​**​明确需要共享引用​**​的场景（如缓存对象的轻量级副本）
#### 🛑 必须使用深拷贝的情况
1. 引用对象​**​需要独立修改​**​（如游戏存档副本）
2. 存在​**​多层嵌套引用​**​（如树形菜单结构）
3. 对象包含​**​线程不安全​**​的引用类型（如`Dictionary`）
### **五、深拷贝实现方案**

|方法|优点|缺点|
|---|---|---|
|​**​手动递归克隆​**​|完全可控，性能优化空间大|代码量大，维护成本高|
|​**​序列化/反序列化​**​|实现简单（JSON/二进制）|性能差，需处理序列化特性|
|​**​表达式树（C#）​**​|动态生成高效拷贝代码|实现复杂度高|
|​**​第三方库​**​|快速集成（如AutoMapper）|依赖外部包，可能存在兼容问题|
#### 示例：通过序列化实现深拷贝
```csharp
using System.Runtime.Serialization.Formatters.Binary;
using System.IO;

public static T DeepCopy<T>(T obj) {
    using (var ms = new MemoryStream()) {
        var formatter = new BinaryFormatter();
        formatter.Serialize(ms, obj);
        ms.Position = 0;
        return (T)formatter.Deserialize(ms);
    }
}
// 注意：.NET Core 中 BinaryFormatter 已过时，建议改用 System.Text.Json 或 Newtonsoft.Json
```