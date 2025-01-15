---
title: "[[6、lamda表达式]]"
type: Literature
status: done
Creation Date: 2023-09-27 12:47
tags:
---
lambda 表达式简化了[[委托#匿名委托|匿名委托]]的使用，让你让代码更加简洁，优雅。
所有的 lambda 表达式都是用新的 lambda 运算符 " => ",可以叫他，“转到”或者 “成为”。运算符将表达式分为两部分，左边指定输入参数，右边是 lambda 的主体。
以下示例使用带有方法语法的 [[LINQ|LINQ]] 功能来演示 lambda 表达式的用法：
```c#
//这段代码的功能是找出字符串数组中以字母"a"开头的字符串中最短的字符串的长度。
//首先，声明了一个字符串数组 `words`，其中包含了三个字符串元素："bot"，"apple"，"apricot"。
//然后，使用 LINQ 的 `Where` 方法来筛选出以字母"a"开头的字符串。在这里，使用了一个 lambda 表达式 `w => w.StartsWith("a")` 作为筛选的条件。这个 lambda 表达式的意思是对于数组中的每个字符串 `w`，判断它是否以字母"a"开头。如果是，则该字符串会被保留下来。
//接下来，使用 `Min` 方法来找出保留下来的字符串中最短的字符串的长度。同样地，使用了一个 lambda 表达式 `w => w.Length` 来表示取字符串的长度。
string[] words = { "bot", "apple", "apricot" };
int minimalLength = words.Where(w => w.StartsWith("a")).Min(w => w.Length);

Console.WriteLine(minimalLength);   // output: 5
//使用LINQ的`Aggregate`方法来对数组中的元素进行累积操作。在这里，使用了两个参数。第一个参数是初始值，设置为1，表示累积的初始值为1。第二个参数是一个lambda表达式`(interim, next) => interim * next`，表示对每个元素进行累积操作的规则。这个lambda表达式接受两个参数：`interim`表示当前累积的结果，`next`表示数组中的下一个元素。lambda表达式的逻辑是将当前累积的结果乘以下一个元素，得到新的累积结果。
int[] numbers = { 4, 7, 10 };
int product = numbers.Aggregate(1, (interim, next) => interim * next);
Console.WriteLine(product);   // output: 280
```
lambda 表达式的输入参数在编译时是强类型。当编译器可以推断输入参数的类型时，如前面的示例所示，可以省略类型声明。如果需要指定输入参数的类型，则必须对每个参数执行类型声明，如以下示例所示：
```c#
int[] numbers = { 4, 7, 10 };
int product = numbers.Aggregate(1, (int interim, int next) => interim * next);
Console.WriteLine(product);   // output: 280
```
以下示例显示如何在没有输入参数的情况下定义 lambda 表达式：
```c#
Func<string> greet = () => "Hello, World!";
Console.WriteLine(greet());
```
## lamda 表达式表示属性的“get”访问器
在 C# 中，=> 符号通常用于定义属性的 "get" 访问器，而不是 "set" 访问器。属性的 "get" 访问器用于获取属性的值，而属性的 "set" 访问器用于设置属性的值。这两者通常使用不同的语法。
```csharp
private SomeType _someField; // 用于存储属性的私有字段
public SomeType SomeProperty
{
    get
    {
        // 返回属性的值
        return _someField;
    }
    set
    {
        // 设置属性的值
        _someField = value;
    }
}
```
在上面的示例中，SomeProperty 属性具有 "get" 和 "set" 访问器，分别用于获取和设置属性的值。如果你只想定义一个 "get" 访问器，你可以使用 => 简写，如下所示：
```csharp
public SomeType SomeProperty => _someField;
```
这种写法会自动为属性创建一个只读属性，只能获取其值，不能设置。在这里，=> 用于定义 "get" 访问器的逻辑。
