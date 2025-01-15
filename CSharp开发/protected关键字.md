---
title: "[[protected关键字]]"
type: Literature
status: done
Creation Date: 2024-04-08 09:37
tags:
---
受保护成员在其所在的类中可由派生类实例访问。
只有在通过派生类类型进行访问时，**基类的受保护成员在派生类中才是可访问的**。以下面的代码段为例：
```csharp
class A
{
    protected int x = 123;
}
class B : A
{
    static void Main()
    {
        var a = new A();
        var b = new B();
        // Error CS1540, because x can only be accessed by
        // classes derived from A.
        // a.x = 10;
        // OK, because this class derives from A.
        b.x = 10;
    }
}
```
语句 a.x = 10 生成错误，因为它是在静态方法 Main 中生成的，而不是类 B 的实例。无法保护结构成员，因为无法继承结构。
在此示例中，DerivedPoint 类是从 Point 派生的。因此，可以从派生类直接访问基类的受保护成员。
```csharp
class Point
{
    protected int x;
    protected int y;
}
class DerivedPoint: Point
{
    static void Main()
    {
        var dpoint = new DerivedPoint();
        // Direct access to protected members.
        dpoint.x = 10;
        dpoint.y = 15;
        Console.WriteLine($"x = {dpoint.x}, y = {dpoint.y}");
    }
}
// Output: x = 10, y = 15
```