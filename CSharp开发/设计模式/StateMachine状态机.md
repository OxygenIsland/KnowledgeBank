---
title: "[[StateMachine状态机]]"
type: Literature
status: done
Creation Date: 2024-04-08 09:37
tags:
---
最近在工作中用到了状态机，所以对这种模式有点感兴趣，状态机当然可以自己写脚本来完成，但是看到了一个 stateless 的库，应该写的会比较完整，所以简单学习一下
## 1、Stateless 的使用
用起来也挺简单的，以打电话这个事情为例，针对打电话的种种动作和状态做成一个状态机。需要先定义一些状态和事件/触发器，电话有拨号、接通、留言等事件，有响铃、挂起、挂断等事件：
```csharp
//代码来自官方示例，可以在官方github库上找到，略有修改以完整展示功能。
enum Trigger
{
    CallDialed,
    CallConnected,
    LeftMessage,
    PlacedOnHold,
    TakenOffHold,
    PhoneHurledAgainstWall,
    MuteMicrophone,
    UnmuteMicrophone,
    SetVolume
}

enum State
{
    OffHook,
    Ringing,
    Connected,
    OnHold,
    PhoneDestroyed
}
```
然后创建一个状态机，并且通过提供委托来初始化状态和更新状态：
```csharp
_machine = new StateMachine<State, Trigger>(() => _state, s => _state = s);
```
配置状态机的行为：
```csharp
//使用Permit指示发生某个事件后，从一个状态变换到另外一个状态。
_machine.Configure(State.OffHook)  //配置状态机的 `OffHook` 状态。
		.Permit(Trigger.CallDialed, State.Ringing);

//设置一个带参数的事件，这个事件是CallDialed的类型
var _setCalleeTrigger = _machine.SetTriggerParameters<string>(Trigger.CallDialed);
_machine.Configure(State.Ringing)
    //允许重新进入当前的状态，这个过程会触发进入和退出动作
    .PermitReentry(Trigger.Ringing)
    //使用OnEntryFrom指示在触发这个状态的时候，运行某个动作，这里指定的是一个带参数的事件
    .OnEntryFrom(_setCalleeTrigger, callee => OnDialed(callee), "Caller number to call")
    .Permit(Trigger.CallConnected, State.Connected);

_machine.Configure(State.OnHold)
    //定义子状态
    .SubstateOf(State.Connected)
    .Permit(Trigger.TakenOffHold, State.Connected)
    .Permit(Trigger.PhoneHurledAgainstWall, State.PhoneDestroyed);

_machine.Configure(State.Connected)
    //进入状态的时候执行动作
    .OnEntry(t => StartCallTimer())
    //离开状态执行动作
    .OnExit(t => StopCallTimer())
    //状态不变化，但是响应某种事件，和PermitReentry不同，它不会触发进入和退出的动作
    .InternalTransition(Trigger.MuteMicrophone, t => OnMute())
    .InternalTransition(Trigger.UnmuteMicrophone, t => OnUnmute())
    .InternalTransition<int>(_setVolumeTrigger, (volume, t) => OnSetVolume(volume))
    .Permit(Trigger.LeftMessage, State.OffHook)
    .Permit(Trigger.PlacedOnHold, State.OnHold)
    //指定在发生同一种事件的时候，根据事件的参数不同而决定进入不同的状态。
    //允许在 `Connected` 状态时触发 `_setCalleeTrigger` 事件，但是只有当 `callee` 参数为空或只包含空白字符时才会将状态机保持在 `Connected` 状态。
    .PermitIf(_setCalleeTrigger, State.Connected, callee => string.IsNullOrWhiteSpace(callee))
    .PermitIf(_setCalleeTrigger, State.Connected, callee => !string.IsNullOrWhiteSpace(callee))
    //如果没有定义这个事件而发生了这个事件，会弹出异常。通过指定忽略某一类事件，可以避免这个情况。
    .Ignore(Trigger.CallDialled);

//当然也可以使用这个来避免弹出上面说的异常
//OnUnhandledTrigger方法用于指定在状态机接收到无法处理的触发器时执行的操作。这是一种处理状态机未预期的输入的方式。在你的代码中，通过传递一个 lambda 表达式给 `OnUnhandledTrigger` 方法，你可以定义在发生未处理触发器时应该执行的逻辑。
_machine.OnUnhandledTrigger((state, trigger) => { });

//可以使用异步调用，但是必须要在触发事件的时候，使用FireAsync
//通过 `OnEntryAsync` 方法配置的异步操作，是为了在状态机进入特定状态时执行异步的逻辑。而在触发事件时，你需要使用 `FireAsync` 方法来异步地触发状态机的状态转换。
_machine.Configure(State.PhoneDestroyed)
    .OnEntryAsync(async () => await SendEmailToAssignee());


```
配置好了各状态之间的转换，下面就是触发事件了。
```csharp
public void Dialed(string callee)
{
    //有参数的触发
    _machine.Fire(_setCalleeTrigger, callee);
}
public void Connected()
{
    //无参数的触发
    _machine.Fire(Trigger.CallConnected);
}
public async Task PhoneDestroy()
{
    //异步触发
    await _machine.FireAsync(Trigger.PhoneDestroyed);
}
public string ToDotGraph()
{
    //导出DOT GRAPH
    return UmlDotGraph.Format(_machine.GetInfo());
}
```
外部调用很简洁：
```csharp
phoneCall.Dialed("Prameela");
phoneCall.Connected();
phoneCall.SetVolume(2);
phoneCall.Hold();
```
## 2、自定义状态机
### 2.1、状态机接口对象
```csharp
/// <summary>
/// 状态对象
/// </summary>
public interface IStateObject
{
    /// <summary>
    /// 进入状态
    /// </summary>
    void EnterState();
    /// <summary>
    /// 离开状态
    /// </summary>
    void ExitState();
    /// <summary>
    /// 更新状态
    /// </summary>
    void UpdateState();
}
```
### 2.2、状态机核心逻辑
```csharp
/// <summary>
/// 状态机
/// </summary>
public class StateMachine
{
    /// <summary>
    /// 运行 Update 时间间隔 毫秒
    /// </summary>
    public int RunInterval = 500;
    /// <summary>
    /// 当前状态
    /// </summary>
    private string CurrentState;
    /// <summary>
    /// 字典存放当前所有对象
    /// </summary>
    private Dictionary<string, IStateObject> Dic = new();
    /// <summary>
    /// 当前的线程对象
    /// </summary>
    private Thread thread;
    /// <summary>
    /// 是否已经在运行
    /// </summary>
    private bool IsRun = false;
    public StateMachine(int runInterval = 500)
    {
        this.RunInterval = runInterval;
    }
    /// <summary>
    /// 注册一个状态对象
    /// </summary>
    /// <param name="stateObject"></param>
    /// <param name="istateObject"></param>
    public void Register(string stateObject, IStateObject istateObject)
    {
        Dic.TryAdd(stateObject, istateObject);
    }
    /// <summary>
    /// 注册一个状态对象
    /// </summary>
    /// <param name="stateObject"></param>
    /// <param name="istateObject"></param>
    public void Register(Dictionary<string, IStateObject> stateObjects)
    {
        if (stateObjects?.Any() == true)
        {
            foreach (var item in stateObjects)
            {
                Dic.TryAdd(item.Key, item.Value);
            }
        }
    }
    /// <summary>
    /// 设置当前状态
    /// </summary>
    /// <param name="stateObject"></param>
    public void SetState(string stateObject)
    {
        if (CurrentState != stateObject)
        {
            if (CurrentState != null && Dic.TryGetValue(CurrentState, out var oldObj))
            {
                oldObj.ExitState();
            }
            CurrentState = stateObject;
            if (CurrentState != null && Dic.TryGetValue(CurrentState, out var newObj))
            {
                newObj.EnterState();
            }
        }
    }
    /// <summary>
    /// 自己启动服务
    /// </summary>
    public void Start()
    {
        if (!IsRun)
        {
            IsRun = true;
            // 创建一个新的后台线程，并指定线程执行的方法为 Run
            thread = new Thread(new ThreadStart(Run));
            // 将线程设置为后台线程，是指在应用程序的主线程（通常是前台线程）结束时，后台线程会自动终止，而不会等待后台线程完成。与之相对的是 "前台线程"，前台线程会等待所有其他非后台线程执行完毕后，应用程序才会退出。
            thread.IsBackground = true;
            thread.Start();
            Console.WriteLine("状态机启动");
        }
    }
    /// <summary>
    /// 自己停止服务
    /// </summary>
    public void Close()
    {
        if (IsRun)
        {
            //最后一个状态直接退出
            if (CurrentState != null && Dic.TryGetValue(CurrentState, out var oldObj))
            {
                oldObj.ExitState();
            }
            IsRun = false;
            try
            {
                thread.Interrupt();
            }
            catch (Exception)
            {
            }
            Thread.Sleep(50);
            thread = null;
            Console.WriteLine("状态机关闭");
        }
    }
    /// <summary>
    /// 线程执行的任务
    /// </summary>
    private void Run()
    {
        try
        {
            while (IsRun)
            {
                Updata();
                // 使用 SpinWait.SpinUntil 方法进行线程自旋，等待指定的时间间隔
                SpinWait.SpinUntil(() => !IsRun, RunInterval);
            }
        }
        catch (Exception) { };
    }
    /// <summary>
    /// 更新数据
    /// </summary>
    public void Updata()
    {
        if (CurrentState != null && Dic.TryGetValue(CurrentState, out var objobj))
        {
            objobj.UpdateState();
        }
    }
}
```
### 2.3、定义状态对象
```csharp
/// <summary>
/// 一只猫
/// </summary>
public class Cat : IStateObject 
{
    public void EnterState()
    {
        Console.WriteLine("小猫进来了");
    }
    public void ExitState()
    {
        Console.WriteLine("小猫出去了");
    }
    public void UpdateState()
    {
        Console.WriteLine("小猫在玩逗猫棒!");
    }
}

/// <summary>
/// 一只狗
/// </summary>
public class Dog : IStateObject 
{
    public void EnterState()
    {
        Console.WriteLine("小狗进来了");
    }
    public void ExitState()
    {
        Console.WriteLine("小狗出去了");
    }
    public void UpdateState()
    {
        Console.WriteLine("小狗在玩耍!");
    }
}
```
### 2.4、测试代码
```csharp
static void Main(string[] args)
{
    StateMachine stateMachine = new StateMachine(1500);
    //状态机
    //根据当前的不同的状态，做出不同的事件操作
    stateMachine.Register(nameof(Cat), new Cat());
    stateMachine.Register(nameof(Dog), new Dog());
    //启动状态机
    stateMachine.Start();
    //开始执行状态机
    //设置当前状态
    stateMachine.SetState(nameof(Cat));
    Thread.Sleep(2000);
    stateMachine.SetState(nameof(Dog));
    Thread.Sleep(2000);
    stateMachine.SetState(nameof(Cat));
    Thread.Sleep(2000);
    //状态机停止
    stateMachine.Close();
    Console.WriteLine("状态机执行完毕!");
    Console.ReadLine();
}
```
![[Pasted image 20231231215058.png|650]]