---
title: "[[UniRx]]"
type: Permanent
status: done
Creation Date: 2025-08-09 16:52
tags:
---
在Unity游戏开发中，响应式编程 (Reactive Programming) 是一种强大的编程范式，它提供了一种优雅的方式来处理异步事件和数据流。通过采用响应式编程，开发者可以编写出更简洁、可读性更高、更易于维护的代码，尤其在处理复杂的用户输入、UI事件和游戏逻辑时优势显著。

## 什么是响应式编程？

从根本上说，响应式编程是一种面向**数据流 (Data Streams)** 和**变化传播 (Propagation of Change)** 的编程范式。这意味着程序会“响应”数据的变化。一个简单直白的理解是：“当某个值发生变化时，与之相关的某些事情会自动发生。”[1](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHU9kq0S5z7PXe99lsDsRqfZln6Zb5QfUrR_SKzr97zcX6zUnKG_Hedht5wJ6GKKBWid_nhFHO30YOkS_z5hGuqSpG8GwDpP9ULo4ZVA-FSP5f4m_2GnyuCC0yCrG8hC9U4yZlCqfymdG1Nc8d8ejGeewiK9l4ivOxRC0MCTsO0e04vNYUGLHmsZsyRsFjTMx0_-C0%3D)

这个范式主要受到**观察者模式 (Observer Pattern)**、**迭代器模式 (Iterator Pattern)** 和**函数式编程 (Functional Programming)** 的启发。[2](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHRQj26OW7HxyBibVQBcQ2sFo0Z58IMwX6eG4mQv34sYSOpADK4dtPTNKb8MusjvtE5jiEvPV_uZ1qSUJU7hfG0HdbwpEH25ZeTIa_-3nMW-6hLU1CV04qFoLUyfRSd1jgU7Z91GnEbDkabAyEnvV_EuX4T4OFpFP8C2ZDwCXhofiGaXcGd7_s%3D) 其核心思想是将各种随时间推移而产生的数据或事件——例如鼠标点击、网络响应、变量值的改变——都看作是可以被观察的“流”。然后，你可以使用一系列丰富的操作符对这些流进行组合、过滤、转换和处理。

## 核心原理

响应式编程建立在几个核心概念之上：
- **可观察对象 (Observable):** 代表一个可被“订阅”的异步数据流。它会随着时间的推移向其订阅者推送（emit）数据项，直到流完成或发生错误。在Unity中，玩家的输入、游戏对象的碰撞事件、计时器等都可以被视为可观察对象。
- **观察者 (Observer):** 也称为订阅者 (Subscriber)，它订阅一个可观察对象，并对流推送的数据做出反应。观察者通常有三个关键方法来处理流的通知：
    - OnNext(): 处理流中推送的每一个数据项。
    - OnCompleted(): 当流成功结束时被调用。
    - OnError(): 当流中发生错误时被调用。
- **操作符 (Operators):** 这是响应式编程的精髓所在。操作符是纯函数，可以对一个或多个数据流进行处理，并返回一个新的数据流，而不会改变原始流。这使得你可以像链式调用一样组合各种操作，以声明式的方式构建复杂的逻辑。常见的操作符包括 Where (过滤)、Select (转换)、Merge (合并)、Throttle (节流)等。
    

简单来说，其工作流程可以概括为：**创建一个数据流 (Observable)，通过一系列操作符 (Operators) 对其进行转换和过滤，最后由观察者 (Observer) 订阅并消费最终结果。**

## UniRx：Unity中的响应式编程利器

虽然响应式编程是一个通用的概念，但在Unity中，它主要是通过一个名为 **UniRx (Reactive Extensions for Unity)** 的第三方库来实现的。UniRx是.NET响应式扩展 (Rx.NET) 的一个专为Unity优化的重制版，它解决了原版在Unity特定环境（如IL2CPP下的iOS平台）中的兼容性问题，并提供了许多针对Unity的实用功能。[3](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQGoO165aJwYQj1F2bHS5bL8zqGNeRs__MJEElvQWVM4TUqI3fhvoXGMypePha6sUuQw2xGsDLe97aPU3EwQjQJGUtiybWHy_JWjFFhMpEQTdwxjjDTbOnaXk-pGATcYLb1aQJg%3D) 
**为什么在Unity中使用UniRx？**

传统的Unity开发严重依赖回调函数和协程来处理异步任务。但这两种方式都有其局限性：[4](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHPoQia4Q-1g4ojTg19HbetEuH5BQe3lvKxtSvnXCuYGMQlPfCOnCNTzl-kBBoyCMLk5YWz53rhsZeLc7OI6_s5oWieetoYpVX4p7pctXS_FmD3lyxg8erzH2zi6VczxMyJcvF-JHEOrjJN21UT0YJK5XThpFA-oRQyZTjSzQ%3D%3D)
- **回调地狱 (Callback Hell):** 当多个异步操作相互依赖时，代码会变得层层嵌套，难以阅读和维护。
- **协程的局限性:**
    - 协程无法直接返回值，通常需要借助回调函数。[3](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQGoO165aJwYQj1F2bHS5bL8zqGNeRs__MJEElvQWVM4TUqI3fhvoXGMypePha6sUuQw2xGsDLe97aPU3EwQjQJGUtiybWHy_JWjFFhMpEQTdwxjjDTbOnaXk-pGATcYLb1aQJg%3D)
    - 异常处理比较困难，try-catch 无法直接包围 yield return 语句。[3](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQGoO165aJwYQj1F2bHS5bL8zqGNeRs__MJEElvQWVM4TUqI3fhvoXGMypePha6sUuQw2xGsDLe97aPU3EwQjQJGUtiybWHy_JWjFFhMpEQTdwxjjDTbOnaXk-pGATcYLb1aQJg%3D)[4](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHPoQia4Q-1g4ojTg19HbetEuH5BQe3lvKxtSvnXCuYGMQlPfCOnCNTzl-kBBoyCMLk5YWz53rhsZeLc7OI6_s5oWieetoYpVX4p7pctXS_FmD3lyxg8erzH2zi6VczxMyJcvF-JHEOrjJN21UT0YJK5XThpFA-oRQyZTjSzQ%3D%3D)
    - 组合多个协程的逻辑会变得复杂。
        
UniRx通过将事件和异步操作转换为数据流，极大地简化了这些场景，带来了诸多好处：

- **代码解耦:** 通过将事件源和处理逻辑分离，降低了代码的耦合度，使系统更加灵活。[5](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQEIxifIpZCiIJGxj6FPiLTnkbOzeyOh3h1gy9odsc5jpjknmJXJ0apxZ3DJKzQxt34omEsDAcZ2j4Y-YbSLOwRtQwIu-v2MTtrGjX51JCAwXSV8DuXcub_f2cTW1hffmKb4XLnRVTpSn0aJeLV1pdlh6fTqAf8W)
- **代码简洁可读:** 链式的操作符使得复杂的逻辑可以被清晰地表达出来，代码更关注“做什么”而非“怎么做”。[1](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHU9kq0S5z7PXe99lsDsRqfZln6Zb5QfUrR_SKzr97zcX6zUnKG_Hedht5wJ6GKKBWid_nhFHO30YOkS_z5hGuqSpG8GwDpP9ULo4ZVA-FSP5f4m_2GnyuCC0yCrG8hC9U4yZlCqfymdG1Nc8d8ejGeewiK9l4ivOxRC0MCTsO0e04vNYUGLHmsZsyRsFjTMx0_-C0%3D)
- **简化异步处理:** 无论是处理UI点击、网络请求还是游戏内的计时事件，都可以统一为数据流进行操作。[4](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHPoQia4Q-1g4ojTg19HbetEuH5BQe3lvKxtSvnXCuYGMQlPfCOnCNTzl-kBBoyCMLk5YWz53rhsZeLc7OI6_s5oWieetoYpVX4p7pctXS_FmD3lyxg8erzH2zi6VczxMyJcvF-JHEOrjJN21UT0YJK5XThpFA-oRQyZTjSzQ%3D%3D)
- **易于测试:** 由于大部分逻辑是纯函数式的数据转换，使得单元测试变得更加容易。[5](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQEIxifIpZCiIJGxj6FPiLTnkbOzeyOh3h1gy9odsc5jpjknmJXJ0apxZ3DJKzQxt34omEsDAcZ2j4Y-YbSLOwRtQwIu-v2MTtrGjX51JCAwXSV8DuXcub_f2cTW1hffmKb4XLnRVTpSn0aJeLV1pdlh6fTqAf8W)

## UniRx的核心组件与应用示例

UniRx为Unity开发者提供了丰富的工具，其中最常用的包括：

- **ReactiveProperty:** 这是一个响应式属性。当它的值发生改变时，会自动通知所有的订阅者。这对于实现MVVM (Model-View-ViewModel) 模式或同步UI和游戏数据非常有用。[6](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQF8_Q8zv0XYW_lGjRaRTR3HCyQyrAt_tyqXDWnOWLhSZvNBgIt0zPgnTNllPaadVTBZn-FTyuvoboUoYzhj9vvMd-PKpO_ETXPwEKkSyEwH2PxY2D6wxm1lzc2MHlkkIGQQutl-vpCQ9fuvjJrjwcZAhrlHzHKaH-H7TxeW3Zo_cxD9PGmwEwbhhfL_CXFBIZyhWN-M9Vz0fvk%3D)
    - **示例：** 玩家生命值变化时自动更新UI。
```csharp
// 在玩家数据脚本中
public ReactiveProperty<int> Health = new ReactiveProperty<int>(100);
// 在UI脚本的Start方法中
playerData.Health
    .Subscribe(newHealth => {
        healthBar.fillAmount = newHealth / 100f;
        healthText.text = newHealth.ToString();
    })
    .AddTo(this); // 确保在GameObject销毁时取消订阅
```
- **ReactiveCommand:** 用于处理命令式的操作，通常与用户输入（如按钮点击）绑定。它可以包含一个执行条件，只有在满足条件时命令才能被触发。[6](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQF8_Q8zv0XYW_lGjRaRTR3HCyQyrAt_tyqXDWnOWLhSZvNBgIt0zPgnTNllPaadVTBZn-FTyuvoboUoYzhj9vvMd-PKpO_ETXPwEKkSyEwH2PxY2D6wxm1lzc2MHlkkIGQQutl-vpCQ9fuvjJrjwcZAhrlHzHKaH-H7TxeW3Zo_cxD9PGmwEwbhhfL_CXFBIZyhWN-M9Vz0fvk%3D) 
	- **示例：** 玩家只有在拥有足够魔法值时才能释放技能。
```csharp
public ReactiveProperty<int> Mana = new ReactiveProperty<int>(100);
public ReactiveCommand CastSpellCommand;

void Start() {
    // 命令的执行条件是魔法值大于20
    CastSpellCommand = Mana.Select(mana => mana > 20).ToReactiveCommand();

    // 订阅命令的执行
    CastSpellCommand.Subscribe(_ => {
        Mana.Value -= 20;
        // 执行技能逻辑...
    });

    // 将UI按钮的点击事件绑定到命令
    castButton.OnClickAsObservable().Subscribe(_ => CastSpellCommand.Execute());
}
```
- **将Unity事件转换为Observable:** UniRx可以将Unity的生命周期函数、UI事件、碰撞事件等轻松转换为可观察的数据流。
	- **示例：** 实现三连击检测。传统方法需要用变量记录点击次数和时间，代码繁琐。使用UniRx则非常直观：
```csharp
// 检测鼠标在0.25秒内的连续点击
Observable.EveryUpdate()
    .Where(_ => Input.GetMouseButtonDown(0))
    .Buffer(TimeSpan.FromSeconds(0.25)) // 将0.25秒内的点击打包成一个列表
    .Where(clicks => clicks.Count >= 3) // 筛选出点击次数大于等于3的
    .Subscribe(_ => {
        Debug.Log("Triple Click Detected!");
    })
    .AddTo(this);
```