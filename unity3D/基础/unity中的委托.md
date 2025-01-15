---
title: "[[unity中的委托]]"
type: Literature
status: done
Creation Date: 2024-05-30 18:33
tags:
---
## 1. UnityAction
UnityAction 是 Unity 对 CSharp 中 [[delegate委托#4. Action|Action]] 的再封装，是更适合再 Unity 中使用的一种泛型委托，用法和 Action 一样
需要包含头文件 `using UnityEngine.Events;`
```csharp
private void UnityActionTest()
{
    UnityAction action;   // 无参的Action
    action = () => Debug.Log("action use once");
    action += () => Debug.Log("action use twice");
    action();

    UnityAction<int, string> action2;   // 有多个参数的Action
    action2 = (a, b) => Debug.Log("name: " + b + "\tage: " + a.ToString());
    action2 += (a, b) => Debug.Log("name: " + b + "\tage: " + (a + 1).ToString());
    action2(18, "Ousun");
}
```
输出结果：
![[Pasted image 20230820173245.png]]
## 2. UnityEvent
UnityEvent 对标 CSharp 中的关键字 [[delegate委托#3. Event 事件|event]]，是 event 的一个封装，用于将 event 暴露到 Inspector 面板。
UnityEvent 可以在面板中添加监听事件，也可以在代码中添加监听事件或 UnityAction
`public UnityEvent<int, string> myEvent;`
UGUI 中的 Buttom 点击事件，就继承自 UnityEvent，可以将 UnityEvent 显示在监视器面板中
![[Pasted image 20230820173358.png]]
在代码中调用 event，**只能使用 Invoke 方法调用**，同时，**UnityEvent 内添加的方法可以是 UnityAction**
用 AddListener 和 RemoveListener 分别为事件添加和移除方法
```csharp
public UnityEvent<int, string> myEvent;
private void UnityEventTest()
{
    myEvent.AddListener((a, b) => 
    { 
    	Debug.Log("name: " + b + "\tage: " + a.ToString()); 
    });
    myEvent.AddListener((a, b) =>
    {
    	Debug.Log("name: " + b + "\tage: " + (a + 1).ToString());
    });
    myEvent.Invoke(18, "Ousun");
}
```
输出结果：
![[Pasted image 20230820173513.png]]
配合监视器面板使用，监视器如下：
![[Pasted image 20230820174121.png]]
添加的相关函数如下：
```csharp
public void InspectorEvent(int a, string b)
{
	Debug.Log("InspectorEvent is called");
}
public void InspectorEvent2(int a, string b)
{
	Debug.Log("InspectorEvent2 is called");
}
```
再次调用上面的 `UnityEventTest()` 函数，输出结果如下：
![[Pasted image 20230820174208.png]]
## 3.回调函数
>其实，回调函数也是一种 delegate 类型。比普通的 delegate 多了一个执行顺序，回调函数是 delegate 的近一步的形式。

将函数作为参数传到另一个函数里面，当哪个函数执行完之后，再执行传进去的这个参数。
这个过程就叫做回调：也就是主函数执行完，回头再调用传进来的那个函数。
### 3.1回调函数的作用
回调函数的作用通常来说就是完成某个动作之后可以立马进行另一个动作，但你不确定那个动作具体会干什么，你可以根据不同的需求来进行不同的改变。
通俗的例子：
你到一个商店买东西，刚好你要的东西没有货，于是你在店员那里留下了你的电话。过了几天店里有货了，店员就打了你的电话，然后你接到电话后就到店里去取了货。在这个例子里，你的电话号码就叫回调函数，你把电话留给店员就叫登记回调函数，店里后来有货了叫做触发了回调关联的事件，店员给你打电话叫做调用回调函数，你到店里去取货叫做响应回调事件。
### 3.2回调函数的定义
定义一个回调函数类：
```c#
using UnityEngine;
// 定义一个回调函数类
// 类里有一个求和方法，要求在求和结束后需要将结果显示出来
public class CallbackExample : MonoBehaviour
{
    public delegate void callback(int a);
    public void AddNum(int a, int b, callback call)
    {
        int count = a + b;
        call(count);
    }
}
```
定义一个测试类，去调用回调函数：
```c#
using UnityEngine;
// 在这个类里面调用上个类的求和方法
// 根据要求，添加显示方法，将求和之后的数据显示出来
public class Test : MonoBehaviour
{
    public int x;
    public int y;
    CallbackExample ex = new CallbackExample();
    public void Start()
    {
        ex.AddNum(x, y, Show);
    }
    void Show(int z)
    {
        print(z);
    }
}
```
测试结果：
![[Pasted image 20230727230642.png]]
回调函数的特点：
**在一个类里面定义回调函数，而在另一个类里面才有具体的实现方法。** 这样当你想修改求和之后的动作时，就可以直接在测试类中进行修改，而不用再到 Callback 类里面修改。

