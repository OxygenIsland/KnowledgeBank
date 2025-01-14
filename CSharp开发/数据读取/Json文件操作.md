---
title: "[[Json文件操作]]"
type: Literature
status: done
Creation Date: 2024-02-03 23:50
tags:
---
## 1、Deserialize
该方法通常用于将整个 JSON 字符串转换为一个 .NET 对象。如果想转换 JSON 字符串中的某一段，可以首先将整个字符串解析为一个包含多个属性的 .NET 对象，然后从该对象中提取所需的属性。
例如，假设你有以下 JSON 字符串：
```csharp
{
    "name": "John",
    "age": 30,
    "address": {
        "street": "123 Main St",
        "city": "New York"
    }
}
```
如果想获取 "address" 字段的内容，可以首先将整个 JSON 字符串解析为一个 .NET 对象，然后从该对象中提取 "address" 属性的值：
```csharp
using Newtonsoft.Json;
using System;

public class Person
{
    public string Name { get; set; }
    public int Age { get; set; }
    public Address Address { get; set; }
}
public class Address
{
    public string Street { get; set; }
    public string City { get; set; }
}
class Program
{
    static void Main()
    {
        string json = "{\"name\":\"John\",\"age\":30,\"address\":{\"street\":\"123 Main St\",\"city\":\"New York\"}}";
        Person person = JsonConvert.DeserializeObject<Person>(json);
        // 获取 address 字段的内容
        Address address = person.Address;
        Console.WriteLine($"Street: {address.Street}, City: {address.City}");
    }
}
```
如果调用 JsonConvert. DeserializeObject 后返回的结果是 null，通常有以下几种可能性和排查步骤：

- **JSON 字符串格式错误：** 首先确保 JSON 字符串的格式是正确的，没有额外或错误的字符，并且所有的引号都正确嵌套。JSON 在语法上非常严格，任何不符合规范的字符都会导致解析失败。
- **目标类型不匹配：** 确保你传递给 JsonConvert. DeserializeObject 的目标类型与 JSON 数据的结构相匹配。如果目标类型与 JSON 结构不匹配，那么解析过程可能无法将数据映射到该类型，导致返回 null。
- **JSON 字段名与目标类属性不匹配：** 如果 JSON 数据的字段名与目标类的属性名不匹配，解析器可能无法正确映射数据。可以 $\color{#FF0000}{使用属性标签（例如[JsonProperty]）来显式指定字段名与属性名的映射关系}$ 
### JsonProperty
假设有一个 JSON 数据如下：
```csharp
{
    "user_name": "john_doe",
    "user_age": 30
}
```
你希望将这个 JSON 数据映射到一个 C# 类型 `User` 中：
```csharp
public class User
{
    // 使用 JsonProperty 特性指定字段名与属性名的映射关系
    [JsonProperty("user_name")]
    public string UserName { get; set; }
    [JsonProperty("user_age")]
    public int UserAge { get; set; }
}
```
在上面的示例中，我们在 `User` 类型的属性上使用了 `JsonProperty` 特性指定了 JSON 数据中的字段名。这样，当你使用 `JsonConvert.DeserializeObject`  将 JSON 数据解析到 User 对象时，Json.NET 将会根据特性中指定的字段名来进行映射。使用这种方式，即使 JSON 数据的字段名与 C# 类型属性名不匹配，也能够正确地进行数据映射。
## 2、Serialize
Json 的格式跟在代码设置的自定义类的格式一定要一一对应，错一个字母都不行，还区分大小写。
首先，我们先写一个字段类 Person，类里面有 string 类型的“Name”和 int 类型的“Grade”，然后写一个"Data”数据类，里面存放的使我们的字段类 Person 数组：
```csharp
[System.Serializable]
class Person
{
    public string Name;
    public int Grade;
}
[System.Serializable]
class Data
{
    public Person[] Person;
}
```
生成 Json 数据，将 Json 数据保存到文件中：
```csharp
using System.IO;
using UnityEngine;
public class Demo5 : MonoBehaviour
{
    void Start()
    {
        WriteData();
    }
    //写数据
    public void WriteData()
    {
        //新建一个数据类
        Data m_Data = new Data();
        //新建一个字段类 进行赋值
        m_Data.Person = new Person[5];
        for (int i = 0; i < 5; i++)
        {
            Person m_Person = new Person();
            m_Person.Name = "User" + i;
            m_Person.Grade = i + 50;
            m_Data.Person[i] = m_Person;
        }
        //将数据转成json
        string js = JsonUtility.ToJson(m_Data);
        //获取到项目路径
        string fileUrl = Application.streamingAssetsPath + "\\jsonInfo.txt";
        //打开或者新建文档
        using (StreamWriter sw =new StreamWriter(fileUrl))
        {
            //保存数据
            sw.WriteLine(js);
            //关闭文档
            sw.Close();
            sw.Dispose();
        }
    }
}
```