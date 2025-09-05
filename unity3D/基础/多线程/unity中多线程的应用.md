---
title: "[[unity中多线程的应用]]"
type: Reference
status: done
Creation Date: 2025-04-22 15:45
tags:
---
为了保证数据安全，Unity核心的游戏逻辑全部都是在一个线程里完成，也就是我们常说的Unity主线程，而且unity支持多线程的使用，可以使用C#的Thread类来创建和管理线程，需要注意的是，只有在主线程（也称为渲染线程）中，才可以访问Unity对象，比如gameobject、transform等属性。

Unity 的核心逻辑（包括场景管理、脚本生命周期函数、输入处理、渲染调度、物理系统、UI系统等）均在单一主线程中完成，称为 ​**​主循环​**​ 或 ​**​帧循环**，所有挂载到 `GameObject` 的脚本，其生命周期函数由 Unity 引擎通过 ​**​反射​**​ 在主线程中按固定顺序调用

## Unity 中的多线程支持
Unity ​**​支持多线程​**​，但有严格限制：
可安全在子线程中使用的功能
1. ​**​数学计算​**​：向量运算、矩阵运算等
2. ​**​路径计算​**​：`NavMesh` 路径计算
3. ​**​网络请求​**​：`UnityWebRequest` 的部分操作
4. ​**​文件 I/O​**​：文件读写（但要注意资源路径问题）
5. ​**​自定义算法​**​：游戏逻辑中的复杂计算
## Unity 的多线程工具
### ​1. **​C# 原生多线程​**​：`Thread`, `ThreadPool`
这是 .NET 中最基本、最底层的多线程实现方式。它直接对应一个操作系统的线程。当你创建一个 Thread 实例并启动它时，操作系统会分配一个全新的线程来执行你指定的代码。
**核心理念**：手动创建和管理一个完全独立的执行线程，该线程与 Unity 的主线程并行运行。

**适用场景**：
- 执行一个长期运行、独立的后台任务，例如监听网络端口、处理一个持续的数据流等。
- 需要对线程有精细控制的场景，如设置线程优先级、命名线程以便调试等。
- 在不涉及 Unity API 调用的纯 C# 计算密集型任务中。
    
**规范流程**：
1. **创建线程**：实例化一个 Thread 对象，并将要执行的方法（通常是一个无参数、无返回值的方法）作为构造函数的参数传入。
    - 可以使用 ThreadStart 委托或更简洁的 Lambda 表达式。
2. **（可选）配置线程**：可以设置线程的属性，例如 Name (方便调试) 和 IsBackground。
    - **极其重要**：在 Unity 中，手动创建的线程**必须**设置为后台线程 (IsBackground = true)。否则，当主程序（Unity 编辑器或构建的游戏）退出时，如果这个前台线程仍在运行，整个进程将无法正常关闭。
3. **启动线程**：调用线程实例的 Start() 方法。此时，新线程开始执行你在步骤1中指定的代码。
4. **线程通信与同步**：
    - 由于新线程不能直接访问 Unity 的 API（如 GameObject.Find, transform.position），任何需要与 Unity 主线程交互的数据都必须通过线程安全的方式传递。
    - 通常的做法是：在后台线程中计算数据，然后将结果存储在一个共享的、线程安全的变量中。在主线程的 Update 方法里，检查这个变量，并将结果应用到 Unity 场景中。
    - 可以使用 lock、Mutex、Semaphore 等 [[同步原语|同步原语]] 来保证对共享数据的安全访问。
5. **（可选）等待线程结束**：如果主线程需要等待后台线程执行完毕，可以调用 thread.Join()。但这会阻塞主线程，所以在 Unity 的 Update 中要慎用。
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
### 2. ​**​Task**​:
Task 是 .NET 4.x 引入的任务并行库 (TPL) 的核心部分。它比 Thread 更高级，是一个对“工作单元”的抽象。Task 不一定直接对应一个线程，它由 ThreadPool (线程池) 来管理和执行，这减少了频繁创建和销毁线程带来的开销。

async/await 语法实际上就是建立在 Task 之上的。

**核心理念**：将工作封装成一个“任务”，交给线程池去高效地调度执行，并提供了更方便的方式来处理任务的结果、异常和连续执行。

**适用场景**：
- 执行中短期的后台计算，特别是当有大量此类任务时，使用线程池可以获得更好的性能。
- 需要链式调用多个异步操作（例如，一个操作完成后接着执行另一个）。
- 与 async/await 结合，编写更结构化的异步代码（尽管在 Unity 中，UniTask 是更好的选择）。

**规范流程**：

1. **启动任务**：最常用的方式是使用 Task.Run()，它会自动从线程池中获取一个线程来执行你提供的 Lambda 表达式。
```csharp
    Task<int> task = Task.Run(() => {
        // ... 在后台线程执行的代码 ...
        return 123; // 返回结果
    });
```
2. **处理任务结果**：
    - **轮询检查**：可以在主线程的 Update 中检查任务的 IsCompleted 属性。任务完成后，通过 task.Result 获取返回值。**注意**：在任务完成前访问 task.Result 会阻塞主线程。
    - **使用回调（ContinueWith）**：可以为任务附加一个延续任务。ContinueWith 会在原任务完成后自动执行。
  ```csharp
        task.ContinueWith(t => {
            int result = t.Result;
            // 注意：ContinueWith 的代码默认也在后台线程执行！
            // 需要手动调度回主线程。
        });
    ```
        
3. **调度回主线程**：这是在 Unity 中使用 Task 的关键和难点。由于 ContinueWith 或 await task 之后的代码默认在后台线程，你必须自己实现将逻辑调度回主线程的机制。常见的模式是创建一个主线程任务调度器。
    - UniTask 库已经完美地解决了这个问题，这也是为什么推荐使用 UniTask 的核心原因之一。
### 3. ​**​Job System​**​（推荐）：
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
### 4. ​**​UniTask​**​（第三方库）：
从 Unity 2017 开始，Unity 支持了现代 C# 的 async/await 异步编程模型。[4](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHJ8QisNcMKi7wn1DE55AbzSRnKn30M1ZmRFXc5WQM2GNSHL8gAeRaJuxFdF8zPHONWNfJLuLuXusiFPmwhZmU_2F3YAkvMs5uze_wmszfJzAVf7pVy6xmuyYGCkggp33u2IGav7QJ9KTSdExwjQHH5zOo2-8FDMgGQV8-FC48DL5gz_vuO_T-goDOyEg%3D%3D) 这种方式相比协程，语法更简洁，支持返回值和 try/catch 异常处理，并且可以真正地在后台线程中运行任务。[4](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHJ8QisNcMKi7wn1DE55AbzSRnKn30M1ZmRFXc5WQM2GNSHL8gAeRaJuxFdF8zPHONWNfJLuLuXusiFPmwhZmU_2F3YAkvMs5uze_wmszfJzAVf7pVy6xmuyYGCkggp33u2IGav7QJ9KTSdExwjQHH5zOo2-8FDMgGQV8-FC48DL5gz_vuO_T-goDOyEg%3D%3D) 

[[UniTask入门|UniTask]] 是一个专为 Unity 优化的第三方开源库，它提供了比原生 Task 更高的性能和更低的内存分配（甚至是零分配），并完美集成了 Unity 的生命周期和异步操作，是目前在 Unity 中使用 async/await 的主流选择。[5](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQEiYWMdzEUctVHqsRbbEohF_q6NuUASpy7KWVkssEfaBimQ9K3JNafSBaxrd4xQt14IslOSKenbqjOHjckGIvXyIxCZhFKOhI74U3MeoAlhgXfcgubpsj_0Dsln_BBN3uWzc2J-Br703CgVVQ%3D%3D)[6](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHBPqtlpdqpy2mO9TSoUK00a4chFxxSIoBRv8GwX0oJ62c9kttsQDCACUmBUOtb9sASB4tDbeBGZPdG_VArkwG1PisCOrSxft8vFAI1hwHDvN6aFgm4TWd0ZDZ2XLixM7W0) 

**核心理念**：使用 async/await 语法糖来编写易于读写的非阻塞代码，可以将计算密集型任务切换到后台线程，完成后再切回主线程更新 Unity 对象。

**适用场景**：
- 网络请求、文件读写等 I/O 密集型操作。[2](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHsCuJHNAjrkHKm_2V_DYu926tMaMH9dOfFfleVeAhIadxQOORGs_O88T77sPII65wXVlO6hpkEHfCD4vnyBYnAI3uyVj51oNY4N6NAVOrTCQo5Ki4LTLMNOZqh_vpRGAS3_rJK4zWytvURNIRE7fKfOCNcaiZAmcYq3XAQXQJhiaKzTF5qOAqdwgIvsCundriCvNyOkrYYPg%3D%3D) 
- 需要返回值的异步任务。[4](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHJ8QisNcMKi7wn1DE55AbzSRnKn30M1ZmRFXc5WQM2GNSHL8gAeRaJuxFdF8zPHONWNfJLuLuXusiFPmwhZmU_2F3YAkvMs5uze_wmszfJzAVf7pVy6xmuyYGCkggp33u2IGav7QJ9KTSdExwjQHH5zOo2-8FDMgGQV8-FC48DL5gz_vuO_T-goDOyEg%3D%3D) 
- 需要复杂异常处理的异步逻辑。[4](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHJ8QisNcMKi7wn1DE55AbzSRnKn30M1ZmRFXc5WQM2GNSHL8gAeRaJuxFdF8zPHONWNfJLuLuXusiFPmwhZmU_2F3YAkvMs5uze_wmszfJzAVf7pVy6xmuyYGCkggp33u2IGav7QJ9KTSdExwjQHH5zOo2-8FDMgGQV8-FC48DL5gz_vuO_T-goDOyEg%3D%3D) 
- 替代大部分协程的使用场景，编写更现代、更可控的代码。[7](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQGmD5xKkk8MXNNpX3ns_0n86e42CbICYJVZCKE0tR5h7-HCwGk8iWwf27o9DBKN53POz-O7GrPELOjDunRYT5rwIdrFZlZ2i1WI3U0EkalQ4EciGM-RNYbwBPXtp9d3RmGVnPTIxEOSg4orCONHiqmsZvOupgM%3D) 
    
**规范流程** (以 UniTask 为例):
1. **安装 UniTask**：通过 Unity Package Manager 从 Git URL 或 OpenUPM 安装 UniTask。[8](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQEtP8cVlqxpxjnx6cWFUuKWNpYPirRV0qeO8ObUf2BlOxg6aNu_kroLFRz9avGaPS3F-IYUUmRgEL7AcUemc_654h3LYHtqb47EMlaPMX0nH1irInuPCj0%3D) 
2. **定义异步方法**：使用 async 关键字修饰方法，返回类型为 UniTask (无返回值) 或 UniTask\<T> (有返回值)。
3. **使用 await 等待** ：在异步方法内部，使用 await 关键字等待一个异步操作完成。UniTask 提供了丰富的可等待操作：
    - await UniTask.Delay(TimeSpan.FromSeconds(t));：替代 WaitForSeconds。
    - await UniTask.Yield(); 或 await UniTask.NextFrame();：替代 yield return null。
    - await SceneManager.LoadSceneAsync(sceneName);：可直接等待 Unity 的原生异步操作。
    - await UniTask.SwitchToThreadPool();：将后续代码切换到后台线程执行。
    - await UniTask.SwitchToMainThread();：将后续代码切换回主线程执行。
4. **处理生命周期和取消**：可以通过 CancellationToken 来取消一个正在进行的异步任务，这对于管理长时间运行的操作非常有用。[6](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHBPqtlpdqpy2mO9TSoUK00a4chFxxSIoBRv8GwX0oJ62c9kttsQDCACUmBUOtb9sASB4tDbeBGZPdG_VArkwG1PisCOrSxft8vFAI1hwHDvN6aFgm4TWd0ZDZ2XLixM7W0) 
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