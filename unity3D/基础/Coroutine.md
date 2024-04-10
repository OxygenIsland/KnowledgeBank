协程在**Unity**中是一个很重要的概念，我们知道，在使用 Unity 进行游戏开发时，**一般（注意是一般）不考虑多线程**，因为在 `Unity` 中，只能在主线程中获取物体的组件、方法、对象，如果脱离这些，`Unity` 的很多功能无法实现，那么多线程的存在与否意义就不大了。
如何处理一些在主任务之外的需求呢，Unity 给我们提供了协程这种方式

**线程与协程有什么区别呢：**
- 两者在内存的使用上是相同的，共享堆，不共享栈
- **线程是并行（对于多核CPU）的**，**协程是串行的**，同一时间只能执行一个协程，线程则是并发的，可以同时有多个线程在运行。

## 1.什么是协程
协程，从字面意义上理解就是协助程序的意思，**我们在主任务进行的同时，需要一些分支任务配合工作**来达到最终的效果
稍微形象的解释一下，想象一下，在进行主任务的过程中我们需要一个对资源消耗极大的操作时候，如果在一帧中实现这样的操作，游戏就会变得十分卡顿，这个时候，我们就可以通过协程，$\color{#FF0000}{在一定帧内完成该工作的处理}$，同时不影响主任务的进行。
## 2.协程的原理
协程不是线程，协程依旧是在主线程中进行
协程是通过[[迭代器]]来实现功能的，通过关键字 [[迭代器#^c7ba43|IEnumerator]]  来定义一个迭代方法，注意使用的是 `IEnumerator`，而不是 `IEnumerable`：

两者之间的区别：
- **`IEnumerator`：是一个实现迭代器功能的接口**
- `IEnumerable`：是在 `IEnumerator` 基础上的一个封装接口，有一个 [[迭代器#^c7ba43|GetEnumerator()]]  方法返回 `IEnumerator` 
在迭代器中（其实就是协程代码中），最关键的是 `yield` 的使用，这是实现我们协程功能的主要途径，通过该关键方法，可以使得协程的运行暂停、记录下一次启动的时间与位置等等。
当协程中使用了 yield 语句，例如 `yield return new WaitForSeconds(3f);`，Unity 会创建一个用于等待的 [[#CustomYieldInstruction ]] 对象，并在每一帧调用它的 keepWaiting 属性来检查是否满足等待条件。如果 keepWaiting 返回 true，则继续等待；如果返回 false，则协程继续执行。

协程函数与普通函数的区别：

|操作|协程函数|普通函数|
|---|---|---|
|返回值|可分步返回多次|只能返回一次|
|获取返回值的方式|调用后执行MoveNext()，通过Current属性获取当前返回值;|调用函数;|
|返回顺序|根据实际情况交错返回|根据调用顺序返回|

## 3.协程的使用
首先通过一个迭代器定义一个返回值为 IEnumerator 的方法，然后再程序中通过 StartCoroutine 来开启一个协程即可：在正式开始代码之前，需要了解 StartCoroutine 的两种重载方式：
```csharp
StartCoroutine（string methodName）//没有参数的情况，直接通过方法名（字符串形式）来开启协程
StartCoroutine（IEnumerator routine）//通过方法形式调用
StartCoroutine（string methodName，object values) //带参数的通过方法名进行调用
//协程开启的方式主要是上面的三种形式，如果你还是不理解，可以查看下面代码：
 	//通过迭代器定义一个方法
 	IEnumerator Demo(int i)
    {
        //代码块
        yield return 0; 
		//代码块
    }
    //在程序种调用协程
    public void Test()
    {
        //第一种与第二种调用方式,通过方法名与参数调用
        StartCoroutine("Demo", 1);
        //第三种调用方式， 通过调用方法直接调用
        StartCoroutine(Demo(1));
    }
```
在一个协程开始后，同样会对应一个结束协程的方法 StopCoroutine 与 StopAllCoroutines 两种方式，但是需要注意的是，两者的使用需要遵循一定的规则，在介绍规则之前，同样介绍一下关于 StopCoroutine 重载：
```csharp
StopCoroutine (string methodName)//通过方法名（字符串）来进行
StopCoroutine (IEnumerator routine)//通过方法形式来调用
StopCoroutine (Coroutine routine)//通过指定的协程来关闭
```
## 4.关于 yield
要想理解协程，就要理解 yield
yield 也是脚本生命周期的一些执行方法，不同的 yield 的方法处于生命周期的不同位置，可以通过下图查看：
![[Pasted image 20230820114126.png|825]]
通过这张图可以看出大部分 yield 位于 `Update` 与 `LateUpdate` 之间，而一些特殊的则分布在其他位置，这些 `yield` 代表什么意思呢，又为啥位于这个位置呢？

首先解释一下位于 Update 与 LateUpdate 之间这些 yield 的含义：
```csharp
yield return null; 暂停协程等待下一帧继续执行
yield return 0或其他数字; 暂停协程等待下一帧继续执行
yield return new WairForSeconds(时间); 等待规定时间后继续执行

yield return StartCoroutine("协程方法名");开启一个协程（嵌套协程)!
```
在了解这些 yield 的方法后，可以通过下面的代码来理解其执行顺序：
```csharp
void Update()
    {
        Debug.Log("001");
        StartCoroutine("Demo");
        Debug.Log("003");
    }
    private void LateUpdate()//lateupdate函数要等所有脚本的update函数执行完才能执行
    {
        Debug.Log("005");
    }
    IEnumerator Demo()
    {
        Debug.Log("002");
        yield return 0;
        Debug.Log("004");
    }
```
将上面的脚本挂载到物体上，运行游戏场景，来查看打印的日志，可以看到下面的日志记录：  
日志记录：
![[Pasted image 20230820114453.png|475]]
可以很清晰的看出，协程虽然是在 Update 中开启，但是关于  **yield return null 后面的代码会在下一帧运行，并且是在 Update 执行完之后才开始执行，并且在 LateUpdate 之前执行**

---

接下来看几个特殊的 yield，他们是用在一些特殊的区域，一般不会有机会去使用，但是对于某些特殊情况的应对会很方便
```csharp
yield return GameObject; 当游戏对象被获取到之后执行
yield return new WaitForFixedUpdate()：等到下一个固定帧数更新
yield return new WaitForEndOfFrame():等到所有相机画面被渲染完毕后更新
yield break; 跳出协程对应方法，其后面的代码不会被执行
```
通过上面的一些**yield**一些用法以及其在脚本生命周期中的位置，我们也可以看到关于**协程不是线程**的概念的具体的解释，所有的这些方法都是在主线程中进行的，只是有别于我们正常使用的 Update 与 LateUpdate 这些可视的方法
###  CustomYieldInstruction  
这是 Unity 中用于自定义协程等待的基类。通过继承 `CustomYieldInstruction`，可以创建自定义的等待条件，使得协程可以等待这些条件的满足。
```csharp
using System;
using UnityEngine;
public class WaitForSecondsWithCallback : CustomYieldInstruction
{
    private float duration;
    private float elapsedTime;
    private Action callback;
    public override bool keepWaiting => elapsedTime < duration;

    public WaitForSecondsWithCallback(float seconds, Action callback)
    {
        duration = seconds;
        this.callback = callback;
    }

    public void Update()
    {
        elapsedTime += Time.deltaTime;

        if (!keepWaiting)
        {
            // 执行回调函数
            callback?.Invoke();
        }
    }
}
```

```csharp
using UnityEngine;

public class CoroutineExample : MonoBehaviour
{
    private void Start()
    {
        StartCoroutine(MyCoroutine());
    }
    private System.Collections.IEnumerator MyCoroutine()
    {
        Debug.Log("Coroutine started");
        // 等待 3 秒并执行回调
        yield return new WaitForSecondsWithCallback(3f, () => Debug.Log("Callback executed"));

        Debug.Log("Coroutine finished");
    }
}

```
## 5.协程几个小用法
### 5 .1将一个复杂程序分帧执行
如果一个复杂的函数对于一帧的性能需求很大，我们就可以通过**yield return null**将步骤拆除，从而将性能压力分摊开来，最终获取一个流畅的过程，这就是一个简单的应用。

举一个案例，如果**某一时刻需要使用 Update**读取一个**列表**，这样一般需要一个**循环去遍历列表**，这样每帧的代码执行量就比较大，就可以将这样的执行放置到协程中来处理：
```csharp
public class Test : MonoBehaviour
{
    public List<int> nums = new List<int> { 1, 2, 3, 4, 5, 6 };
    private void Update()
    {
        if(Input.GetKeyDown(KeyCode.Space))
        {
            StartCoroutine(PrintNum(nums));
        }
    }
	// 通过协程分帧处理!!!!！
    IEnumerator PrintNum(List<int> nums)
    {
        foreach(int i in nums)
        {
            Debug.Log(i);
            yield return null;
        }
    }
}
```
上面只是列举了一个小小的案例，在实际工作中会有一些很消耗性能的操作的时候，就可以通过这样的方式来进行性能消耗的分消.

### 5 .2 [[11、延迟调用和周期性调用#使用协程来实现延时|延时调用]]和[[11、延迟调用和周期性调用#使用协程来实现周期性调用|周期性调用]]
### 5 .3异步加载等功能
只要一说到**异步**，就必定离不开**协程**，因为在异步加载过程中可能会影响到其他任务的进程，这个时候就需要通过协程将这些可能被影响的任务**剥离**出来。

常见的异步操作有：
- AB包资源的异步加载
- Reaources资源的异步加载
- 场景的异步加载
### 5.4用协程来实现接口调用
1. **编写接口和接口方法**：首先，您需要定义接口以及接口中的方法。这是您的接口协议，规定了应该实现的操作。
```csharp
public interface IMyApi
{
    IEnumerator GetDataFromServer(string url, Action<string> callback);
}
```
2. **编写实现接口的类**：创建一个类，实现您的接口，并提供方法的具体实现。在方法内部，使用 Unity 的协程来执行异步操作。
```csharp
public class MyApi : IMyApi
{
    public IEnumerator GetDataFromServer(string url, Action<string> callback)
    {
        using (UnityWebRequest webRequest = UnityWebRequest.Get(url))
        {
            yield return webRequest.SendWebRequest();

            if (webRequest.result == UnityWebRequest.Result.Success)
            {
                string data = webRequest.downloadHandler.text;
                callback(data);
            }
            else
            {
                Debug.LogError("Error: " + webRequest.error);
            }
        }
    }
}
```
3. **在 MonoBehaviours 中使用协程**：在需要调用接口的 MonoBehaviours 中，使用 `StartCoroutine` 来调用接口的方法。在回调中处理数据。
```csharp
public class MyMonoBehaviour : MonoBehaviour
{
    private IMyApi myApi = new MyApi();

    private void Start()
    {
        StartCoroutine(GetDataAndProcess());
    }

    private IEnumerator GetDataAndProcess()
    {
        string url = "https://api.example.com/data";

        yield return myApi.GetDataFromServer(url, data =>
        {
            // Process the data
            Debug.Log(data);
        });
    }
}
```
在这个示例中，`GetDataAndProcess` 协程首先调用 `GetDataFromServer`，然后在接口的回调中处理获取的数据。这使您能够在 Unity 中执行异步操作而不会阻塞主线程。