---
title: "[[unity中多线程的应用]]"
type: Reference
status: done
Creation Date: 2025-04-22 15:45
tags:
---
为了保证数据安全，Unity核心的游戏逻辑全部都是在一个线程里完成，也就是我们常说的Unity主线程，而且unity支持多线程的使用，可以使用C#的Thread类来创建和管理线程，需要注意的是，只有在主线程（也称为渲染线程）中，才可以访问Unity对象，比如gameobject、transform等属性。

Unity 的核心逻辑（包括场景管理、脚本生命周期函数、输入处理、渲染调度、物理系统、UI系统等）均在单一主线程中完成，称为 ​**​主循环​**​ 或 ​**​帧循环**，所有挂载到 `GameObject` 的脚本，其生命周期函数由 Unity 引擎通过 ​**​反射​**​ 在主线程中按固定顺序调用

### Unity 中的多线程支持
Unity ​**​支持多线程​**​，但有严格限制：
#### 可安全在子线程中使用的功能
1. ​**​数学计算​**​：向量运算、矩阵运算等
2. ​**​路径计算​**​：`NavMesh` 路径计算
3. ​**​网络请求​**​：`UnityWebRequest` 的部分操作
4. ​**​文件 I/O​**​：文件读写（但要注意资源路径问题）
5. ​**​自定义算法​**​：游戏逻辑中的复杂计算
### Unity 的多线程工具
#### ​1. **​C# 原生多线程​**​：`Thread`, `ThreadPool`
```csharp
void Start() {
    // 启动新线程
    Thread thread = new Thread(DoBackgroundWork);
    thread.Start();
}

void DoBackgroundWork() {
    // 这里可以执行非Unity API的操作
    Debug.Log("This will cause error!"); // ❌ 不能在子线程调用Unity API
    
    // 正确的做法是将结果传回主线程处理
    float result = PerformComplexCalculation();
    
    MainDispatcher.RunOnMainThread(() => {
        // ✅ 在主线程更新UI或游戏对象
        textComponent.text = $"Result: {result}";
    });
}
```

```csharp
void CalculateInBackground() {
    ThreadPool.QueueUserWorkItem(state => {
        Vector3[] path = CalculatePath();
        
        // 通过主线程调度器返回结果
        UnityMainThreadDispatcher.Instance.Enqueue(() => {
            DrawPath(path);
        });
    });
}
```

#### 2. ​**​Job System​**​（推荐）：
- 基于 Burst 编译器的高性能多线程方案
- 通过 `IJob` 接口实现
```csharp
struct CalculationJob : IJob {
    public NativeArray<float> input;
    public NativeArray<float> output;
    
    public void Execute() {
        for(int i = 0; i < input.Length; i++) {
            output[i] = input[i] * 2f;
        }
    }
}

void Start() {
    NativeArray<float> input = new NativeArray<float>(100, Allocator.TempJob);
    NativeArray<float> output = new NativeArray<float>(100, Allocator.TempJob);
    
    // 填充输入数据...
    
    var job = new CalculationJob {
        input = input,
        output = output
    };
    
    JobHandle handle = job.Schedule();
    handle.Complete(); // 等待作业完成
    
    // 使用结果...
    
    input.Dispose();
    output.Dispose();
}
```
#### 3. ​**​UniTask​**​（第三方库）：
##### 3.1 ​**​UniTask 的多线程支持**
UniTask 提供了与 C# 原生的 `Task` 类似的机制，允许通过以下方式实现多线程编程：
- ​**​`UniTask.Run`​**​：在​**​线程池​**​中执行代码块，避免阻塞主线程。
```csharp
await UniTask.Run(() => {
    // 在子线程执行耗时操作（如计算、IO）
    HeavyCalculation();
});
```
- ​**​`UniTask.SwitchToThreadPool`​**​：显式切换到线程池上下文。
```csharp
await UniTask.SwitchToThreadPool();
// 后续代码在线程池执行
```
##### 3.2. ​**​与 Unity 主线程的交互**
Unity 的 API ​**​必须​**​在主线程调用（如 `GameObject`、`Transform` 等）。UniTask 提供了以下方法切换回主线程：
- ​**​`UniTask.SwitchToMainThread`​**​：回到主线程上下文。
```csharp
await UniTask.Run(() => {
    // 子线程执行耗时操作
}).ContinueWith(() => {
    // 自动切换回主线程
    transform.position = new Vector3(0, 0, 0); // 安全操作
});

// 或者显式切换上下文
await UniTask.SwitchToThreadPool(); // 切换到线程池
// 执行子线程任务...
await UniTask.SwitchToMainThread(); // 切换回主线程
transform.position = Vector3.zero; // 安全操作
```
##### 3.3 ​**​注意事项​**​
- ​**​线程安全​**​：在子线程中避免操作 Unity 对象或共享数据。
- ​**​性能开销​**​：频繁的线程切换可能抵消多线程带来的性能优势。
- ​**​`UniTaskConfig`​**​：可通过配置调整线程池行为（如 `ThreadPoolMinSize`）。
### 主线程与子线程交互的最佳实践
#### ​**​1. 使用主线程调度器​**​：
MainDispatcher 是一个 DW中自定义的一个 工具类，用于在主线程上调度和执行动作(Action)，支持延迟执行和线程安全操作。
```csharp
namespace Lenovo.XR.StARstudio.PluginsInstance.ARPackage.Tool
{
    public class MainDispatcher : MonoBehaviour
    {
        public class MainActionNode
        {
            public Action mAction; //要执行的动作
            public long targetTime;  //目标执行时间(毫秒级时间戳)
            public bool needRemove = false;  //标记是否需要移除
        }
        //将 `action` 委托包装成一个线程池任务，由系统自动分配后台线程执行。
        public static void RunAsync(Action action)
        {
            ThreadPool.QueueUserWorkItem(o => action());
        }

		//- `state`：任意类型的对象参数（可传递值类型或引用类型）
		//- `action`：必须接受 `object` 类型参数的委托
        public static void RunAsync(Action<object> action, object state)
        {
            ThreadPool.QueueUserWorkItem(o => action(o), state);
        }

        public static void RunOnMainThread(Action action,bool canRepeatable = true)
        {
            RunOnMainThread(action, 0f, canRepeatable);
        }

        public static void RunOnMainThread(Action action, float delayTime, bool canRepeatable = true)
        {
            lock (_actions)
            {
                if (!canRepeatable)
                {
                    foreach (var existingAction in _actions)
                    {
                        if (existingAction.mAction == action)
                        {
                            // 如果不允许重复并且动作已经存在，则不添加
                            //Log.Warn("MainDispatcher action queue is Repeatable, and ignore new request  : ");
                            return;
                        }
                    }
                }

                MainActionNode mNode = new MainActionNode();
                mNode.mAction = action;
                if(delayTime <= 0)
                {
                    mNode.targetTime = 0;
                }
                else
                {
                    mNode.targetTime = DateTime.Now.Ticks / 10000 + (long)(delayTime * 1000f);
                }
                if(_actions.Count < 20)
                {
                    _actions.Add(mNode);
                    _queued = true;
                }
                else
                {
                    if(_actions.Count > 50)
                    {
                        Log.Error("MainDispatcher action queue is full, and ignore all action : " + _actions.Count);
                        _actions.Clear();
                        return;
                    }
                    Log.Warn("MainDispatcher action queue is crowded, please check the action queue : " + _actions.Count);
                }
            }
        }

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void Initialize()
        {
            if (_instance == null)
            {
                Debug.LogWarning("MainDispatcher BeforeSceneLoad");
                _instance = new GameObject("MainDispatcher").AddComponent<MainDispatcher>();
                DontDestroyOnLoad(_instance.gameObject);
            }
        }
        private void Update()
        {
            if (_queued)
            {
                lock (_actions)
                {
                    for (int i= 0;i< _actions.Count;i++)
                    {
                        try
                        {
                            if ((_actions[i].targetTime == 0 || (DateTime.Now.Ticks / 10000 - _actions[i].targetTime) > 0) && !_actions[i].needRemove)
                            {
                                _actions[i].mAction();
                                _actions[i].needRemove = true;
                            }
                        }
                        catch (Exception e)
                        {
                            Debug.LogError("An exception occurred while dispatching an action on the main thread: " + e);
                        }
                    }
                    for(int i = _actions.Count -1;i >= 0; i--)
                    {
                        if (_actions[i].needRemove)
                        {
                            _actions.Remove(_actions[i]);
                        }
                    }
                    if(_actions.Count <= 0)
                    {
                        _queued = false;
                    }
                }
            }
        }

        static MainDispatcher _instance;
        static volatile bool _queued = false;
        static List<MainActionNode> _actions = new List<MainActionNode>(20);
    }
}
```

```csharp
// 在子线程中
MainDispatcher.RunOnMainThread(() => {
    // 这里可以安全调用Unity API
});
```
#### 2. ​**​使用 `UnityMainThreadDispatcher`​**​（常见第三方方案）
`UnityMainThreadDispatcher` 是专为 Unity 设计的开源工具，主要用于解决多线程环境下调用 Unity API 的限制问题。通过将非主线程的操作调度到主线程执行，它实现了线程安全且便捷的跨线程交互
**核心功能与优势​**​：
- ​**​线程安全调度​**​：提供 `Enqueue` 方法将 `Action` 或协程（`IEnumerator`）加入主线程执行队列，避免直接操作 Unity API 导致的线程冲突
- ​**​协程支持​**​：可直接调度协程到主线程，支持异步逻辑的分帧处理，例如网络请求完成后更新 UI
- ​**​轻量级集成​**​：无需额外依赖，仅需将预制体或脚本添加到场景即可使用
```csharp
// 子线程中执行耗时操作后更新UI
ThreadPool.QueueUserWorkItem(_ => {
    var data = DownloadData();
    UnityMainThreadDispatcher.Instance().Enqueue(() => {
        textComponent.text = data; // 主线程安全操作
    });
});
```

#### 3. ​**​使用 `PlayerLoop` 注入​**​（高级用法）
#### 4. 共享数据加锁
```csharp
private object _lock = new object();
private List<string> _results = new List<string>();

void ProcessInThread() {
    lock(_lock) {
        _results.Add("new data");
    }
}

void Update() {
    lock(_lock) {
        foreach(var r in _results) {
            // 处理结果
        }
        _results.Clear();
    }
}
```
### 应用案例
#### 1. 分帧加载大量资源
```csharp
IEnumerator LoadAssetsAsync() {
    List<string> paths = GetResourcePaths();
    
    foreach(var path in paths) {
        bool done = false;
        ThreadPool.QueueUserWorkItem(_ => {
            var asset = LoadAssetFromDisk(path); // 自定义加载方法
            MainDispatcher.RunOnMainThread(() => {
                InstantiatePrefab(asset);
                done = true;
            });
        });
        
        while(!done) {
            yield return null;
        }
    }
}
```
#### 2. 实时数据处理（如网络游戏）
```csharp
void Update() {
    if(_networkQueue.Count > 0) {
        lock(_networkQueue) {
            var packet = _networkQueue.Dequeue();
            ProcessPacket(packet);
        }
    }
}

// 网络线程
void NetworkThread() {
    while(true) {
        var packet = ReceiveNetworkPacket();
        lock(_networkQueue) {
            _networkQueue.Enqueue(packet);
        }
    }
}
```
#### 3. 地形生成
```csharp
IEnumerator GenerateTerrain() {
    TerrainData data = new TerrainData();
    
    // 使用Job System生成高度图
    var heightJob = new GenerateHeightMapJob {
        // 设置参数...
    };
    JobHandle handle = heightJob.Schedule();
    
    while(!handle.IsCompleted) {
        yield return null;
    }
    handle.Complete();
    
    // 在主线程应用生成的地形
    terrain.terrainData = data;
}
```