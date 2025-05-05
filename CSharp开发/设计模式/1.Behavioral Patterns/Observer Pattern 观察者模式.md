---
title: "[[Observer Pattern 观察者模式]]"
type: Reference
status: done
Creation Date: 2025-05-05 16:28
tags:
  - 设计模式
---
## Definition
Define a one-to-many dependency between objects so that when one object changes state, all its dependents are notified and updated automatically.  
定义对象间一种一对多的依赖关系，使得每当一个对象改变状态，则所有依赖于它的对象都会得到通知并被自动更新。
![[Pasted image 20250505171911.png|500]]
## Participants
Subject类，可翻译为主题或抽象通知者，一般用一个抽象类或者一个接口实现。它把所有对观察者对象的引用保存在一个聚集里，每个主题都可以有任何数量的观察者。抽象主题提供一个接口，可以增加和删除观察者
```csharp
abstract class Subject
{
    private IList<Observer> observers = new List<Observer>（）;
    //增加观察者
    public void Attach（Observer observer）
    {
        observers.Add（observer）;
    }
    //移除观察者
    public void Detach（Observer observer）
    {
        observers.Remove（observer）;
    }
    //通知
    public void Notify（）
    {
        foreach（Observer o in observers）
        {
            o.Update（）;
        }
    }
}
```
Observer类，抽象观察者，为所有的具体观察者定义一个接口，在得到主题的通知时更新自己。这个接口叫做更新接口。抽象观察者一般用一个抽象类或者一个接口实现。更新接口通常包含一个Update（）方法，这个方法叫做更新方法。
```csharp
abstract class Observer
{
    public abstract void Update（）;
}
```
ConcreteSubject类，叫做具体主题或具体通知者，将有关状态存入具体观察者对象；在具体主题的内部状态改变时，给所有登记过的观察者发出通知。具体主题角色通常用一个具体子类实现。
```csharp
class ConcreteSubject : Subject
{
    private string subjectState;
        //具体被观察者状态
    public string SubjectState
    {
        get { return subjectState; }
        set { subjectState = value; }
    }
}
```
ConcreteObserver类，具体观察者，实现抽象观察者角色所要求的更新接口，以便使本身的状态与主题的状态相协调。具体观察者角色可以保存一个指向具体主题对象的引用。具体观察者角色通常用一个具体子类实现。
```csharp
class ConcreteObserver : Observer
{
    private string name;
    private string observerState;
    private ConcreteSubject subject;

    public ConcreteObserver（ConcreteSubject subject，string name）
    {
        this.subject = subject;
        this.name = name;
    }

    public override void Update（）
    {
        observerState = subject.SubjectState;
        Console.WriteLine（"观察者{0}的新状态是{1}"，name，observerState）;
    }
    
    public ConcreteSubject Subject
    {
        get { return subject; }
        set { subject = value; }
    }
}
```
客户端代码
```csharp
static void Main（string[] args）
{
    ConcreteSubject s = new ConcreteSubject（）;

    s.Attach（new ConcreteObserver（s，"X"））;
    s.Attach（new ConcreteObserver（s，"Y"））;
    s.Attach（new ConcreteObserver（s，"Z"））;

    s.SubjectState = "ABC";
    s.Notify（）;

    Console.Read（）;
}
```
观察者模式所做的工作其实就是在解除耦合。让耦合的双方都依赖于抽象，而不是依赖于具体。从而使得各自的变化都不会影响另一边的变化。
## 观察者模式的不足
‘抽象通知者’还是依赖‘抽象观察者’，也就是说，万一没有了抽象观察者这样的接口，我这通知的功能就完不成了。另外就是每个具体观察者，它不一定是‘Uodate’的方法要调用。
如果通知者和观察者之间根本就互相不知道，由客户端来决定通知谁，那就好了。这就是我们接下来要讲的实践委托
## 事件委托实现
![[Pasted image 20250505175512.png|500]]

![[Pasted image 20250505175600.png|500]]

![[Pasted image 20250505175625.png|500]]
委托就是一种引用方法的类型。一旦为委托分配了方法，委托将与该方法具有完全相同的行为。委托方法的使用可以像其他任何方法一样，具有参数和返回值。委托可以看作是对函数的抽象，是函数的‘类’，委托的实例将代表一个具体的函数。

delegate void EventHandler（），可以理解为声明了一个特殊的‘类’。而‘public event EventHandler Update;’可以理解为声明了一个‘类’的变量，也就是一个事件委托变量叫‘更新’。”

一个委托可以搭载多个方法，所有方法被依次唤起。更重要的是，它可以使得委托对象所搭载的方法并不需要属于同一个类
 ，这样就使得，本来是在‘老板’类中的增加和减少的抽象观察者集合以及通知时遍历的抽象观察者都不必要了。转到客户端来让委托搭载多个方法，这就解决了本来与抽象观察者的耦合问题。
 