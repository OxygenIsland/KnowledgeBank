---
title: "[[Fixing Performance Problems]]"
type: Reference
status: ing
Creation Date: 2025-04-23 16:12
tags:
---
## The causes of poorly-performing code
**核心原则​**​  
当我们确认游戏性能问题源于代码时，必须审慎选择优化策略。表面上看，优化高负荷函数似乎是首选方案，但该函数可能本身已处于最优状态——其高成本是算法特性决定的固有开销。相比之下，修改一个被数百个游戏对象频繁调用的脚本中的微小低效，反而可能带来更显著的性能提升。

当代码性能低下时，本质原因是它在运行时给CPU造成了过重负担。以下是可能的原因：
### Move code out of loops when possible
```csharp
void Update() 
{
    for(int i = 0; i < myArray.Length; i++) 
    {
        if (exampleBool) 
        {
            ExampleFunction(myArray[i]);
        }
    }
}

//优化后
void Update() 
{
    if (exampleBool)
    {
        for(int i = 0; i < myArray.Length; i++)
        {
            ExampleFunction(myArray[i]);
        }
    }
}
```
### Only run code when things change
基本原则，不举例子
### Run code every \[x] frames
```csharp
private int interval = 3;
void Update()
{
    if(interval > 0 && Time.frameCount % interval == 0)
    {
        ExampleExpensiveFunction();
    }
    //交替执行,也可以改用`Coroutine`或`InvokeRepeating`实现更精确的时间间隔控制
    else if(Time.frameCount % 2 == 1)
    {
        AnotherExampleExpensiveFunction();
    }
}
```
### Use caching
```csharp
void Update()
{
	Renderer myRenderer = GetComponent<Renderer>();
    ExampleFunction(myRenderer);
}
//优化后
private Renderer myRenderer;
void Start()
{
    myRenderer = GetComponent<Renderer>();
}

void Update()
{
    ExampleFunction(myRenderer);
}
```
### Use the right data structure
**数据结构的选择会显著影响代码性能表现。​**​  
没有任何一种数据结构能完美适用于所有场景，因此要为游戏中的每个具体任务选择最合适的数据结构。
对于初学者，建议从​**​大O表示法(Big O Notation)​**​开始学习。这种算法复杂度分析方法能帮助我们比较不同数据结构的效率。[这篇指南](https://robbell.io/2009/06/a-beginners-guide-to-big-o-notation)提供了清晰易懂的入门讲解。同时也可以参考一下[MSDN的C#集合与数据结构指南](https://learn.microsoft.com/en-us/dotnet/standard/collections/?redirectedfrom=MSDN)

## Minimize the impact of garbage collection
**垃圾回收（Garbage Collection）是Unity内存管理机制的重要组成部分​**​。我们代码使用内存的方式直接决定了垃圾回收的频率及其对CPU的性能开销。
### Use object pooling
通常来说，实例化(Instantiate)和销毁(Destroy)游戏对象的性能开销，要远高于简单地停用(Deactivate)和重新激活(Reactivate)现有对象。特别是当对象包含初始化代码时（例如在Awake()或Start()函数中调用GetComponent()等操作），这种性能差异会更加显著。

在需要频繁生成和销毁同类对象的场景中（例如射击游戏中的子弹系统），采用对象池化(Object Pooling)技术可以带来显著的性能优化。该技术的核心思想是：预先创建对象集合，通过暂时停用不再需要的对象（而非销毁），在需要时重新激活并回收利用这些对象。
## Avoiding expensive calls to the Unity API
有时我们的代码对其他函数或API的调用可能产生意外高昂的性能开销。这种情况可能由多种因素导致：看似简单的变量访问，实际上可能是包含额外逻辑的访问器(accessor)——这些访问器可能执行附加代码、触发事件或引发托管代码与引擎代码之间的交互。
### SendMessage()
`SendMessage()`与`BroadcastMessage()`,这两个函数具有极高的灵活性，对项目结构要求极低，能够快速实现消息传递功能。
方法签名差异：
- `SendMessage(string methodName)`：仅在当前GameObject上查找
- `BroadcastMessage(string methodName)`：会向下搜索所有子对象

特别适合用于：
- 原型开发(Prototyping)
- 初学者脚本编写(Beginner-level scripting)
但它们的调用成本极其昂贵，这是因为：
1. 基于反射(Reflection)机制实现
2. 反射指代码在运行时（而非编译时）自我检查并决策的过程
3. 使用反射的代码会给CPU带来远高于常规代码的运算负担
推荐方案：
- ​**​明确目标组件时**，直接调用
- **​不明确目标组件时**，使用事件Event、委托Delegates
### Find()
`Find()`及相关函数功能强大但执行成本高昂。这些函数需要Unity遍历内存中的每个游戏对象(GameObject)和组件(Component)。这意味着：
- 在小型简单项目中影响尚不明显
- 随着项目复杂度提升，其性能开销会显著增加
所以我们需要：
1. ​**​控制调用频率​**​  
    应尽量减少`Find()`类函数的使用次数
    
2. ​**​结果缓存机制​**​  
    必须使用时，务必缓存查找结果供重复使用
    
或者采用替代方案：

| 优化方案   | 具体实施方式                     | 优势说明      |
| ------ | -------------------------- | --------- |
| 检视器赋值  | 通过Inspector面板直接拖拽引用        | 完全避免运行时查找 |
| 引用管理脚本 | 创建专用脚本集中管理常用对象引用           | 统一维护查找资源  |
| 层级查询优化 | 使用`transform.Find()`限定搜索范围 | 缩小遍历范围    |

### Transform()
Setting the position or rotation of a transform causes an internal **OnTransformChanged** event to propagate(传播) to all of that transform's children. This means that it's relatively expensive to set a transform's position and rotation values, especially in transforms that have many children.​
**减少属性设置次数​**​：避免在`Update()`中多次单独设置x/z轴位置。建议：
```csharp
Pose newPose = new Pose(new Vector3(1, 2, 3), Quaternion.Euler(0, 45, 0));
transform.SetPositionAndRotation(newPose.position, newPose.rotation); // 一次性设置    
```
此方式仅触发一次`OnTransformChanged`事件。

**​position vs localPosition**
​**​`Transform.position`​**:
- 每次调用时动态计算世界坐标，消耗CPU资源。
- 频繁使用时建议缓存（如`Vector3 cachedPos = transform.position;`）。
**​`Transform.localPosition`​**​：
- 直接返回Transform中存储的局部坐标值，无额外计算。
- 若场景允许，优先使用`localPosition`替代`position`以提升性能。
### Update()
`Update()`、`LateUpdate()` 等事件函数看似简单，但每次调用时都存在隐藏开销：
1. ​**​跨层通信​**​：每次调用需在引擎代码（原生层）和管理代码（托管层）间进行通信。
2. ​**​安全检查​**​：Unity在调用前会执行多项检查，例如：
    - 确认`GameObject`处于有效状态
    - 验证对象未被销毁等。

虽然单次调用的开销不大，但当游戏中存在​**​数千个活跃的`MonoBehaviour`脚本​**​时，这些开销会显著累积。

即使`Update()`函数体为空：
- 安全检查仍会执行
- 原生层调用依然发生
- ​**​CPU时间被无意义消耗​**

### Vector2 and Vector3
向量运算（Vector2/Vector3）相比浮点数(float)或整数(int)运算会生成更多CPU指令。虽然单次计算耗时差异微小，但在大规模使用时可能显著影响性能。
#### ​**​关键性能问题​**​
1. ​**​运算复杂度对比​**

| 运算类型    | CPU指令复杂度 | 典型场景       |
| ------- | -------- | ---------- |
| 整数/浮点运算 | 低        | 简单数值计算     |
| 向量运算    | 高        | 坐标变换、物理模拟等 |
 
2. ​**​高频调用场景​**​
    - 在`Update()`的嵌套循环中
    - 对大量游戏对象频繁进行向量运算时

#### ​**​平方根计算的性能陷阱​**​
以下操作涉及​**​昂贵的平方根计算​**​：

```csharp
Vector2.magnitude    // 计算二维向量长度（含平方根）
Vector3.magnitude    // 计算三维向量长度（含平方根）
Vector2.Distance()   // 底层调用magnitude
Vector3.Distance()   // 底层调用magnitude
```
✅ ​**​优化方案​**​：  
使用`.sqrMagnitude`替代（避免平方根计算）：
```csharp
// 比较距离时（只需比较平方值即可）
if (vectorA.sqrMagnitude < vectorB.sqrMagnitude) 
{
    // 更高效的距离比较
}
```
### Camera.main
#### **📌 核心概念​**​
`Camera.main` 是Unity提供的一个便捷API，用于获取场景中​**​第一个启用且标记为"Main Camera"的相机组件引用​**​。
⚠ ​**​重要提示​**​：  
虽然`Camera.main`看起来像是一个变量，但实际上它是一个​**​访问器（accessor）​**​，底层会调用类似`Find()`的内部函数，遍历所有`GameObject`和`Component`，​**​性能开销较高​**​。
#### ​**​❌ 问题分析​**​
1. ​**​底层机制​**​
    - 每次调用`Camera.main`时，Unity都会在内存中​**​搜索所有GameObject​**​，检查是否有​**​启用且标记为"Main Camera"的相机​**​。
    - 这个过程类似于`GameObject.Find()`，​**​性能消耗大​**​，尤其是在复杂场景中。
2. ​**​高频调用影响​**​
    - 如果在`Update()`等每帧执行的函数中调用`Camera.main`，会导致​**​不必要的性能损耗​**​。
## Culling
Unity contains code that checks whether objects are within the frustum of a camera. If they are not within the frustum of a camera, code related to rendering these objects does not run. The term for this is **frustum culling(视锥体剔除)**.

We can take a similar approach to the code in our scripts. If we have a code that relates to the visual state of an object, we may not need to execute this code when the object cannot be seen by the player. In a complex Scene with many objects, this can result in considerable performance savings.

```csharp
private Renderer myRenderer;
void Start()
{
	myRenderer = GetComponent<Renderer>();
}

void Update()
{
	UpdateTransformPosition();
	if(myRenderer.isVisible)
	{
		UpdateAnimations();
	}
}
```

### **游戏对象可见性优化方案（中文翻译）​**​
#### ​**​📌 核心概念​**​
在游戏开发中，当玩家​**​无法看到某些对象​**​时，可以通过多种方式​**​禁用相关代码逻辑​**​以提升性能。具体实现方法需根据游戏需求灵活选择。
#### ​**​🔧 实现方案​**​
1. ​**​手动禁用（确定不可见时）​**​
    - ​**​适用场景​**​：明确知道某些对象在特定游戏阶段不可见（如过场动画中的背景物体）
    - ​**​实现方式​**​：
```csharp
gameObject.SetActive(false);  // 直接禁用整个对象
enabled = false;              // 或禁用特定组件
```
2. ​**​自动计算可见性（不确定时）​**​

| 方法           | 技术实现                                          | 特点           |
| ------------ | --------------------------------------------- | ------------ |
| ​**​粗略计算​**​ | 检查对象是否在玩家后方（如通过`Vector3.Dot`计算朝向）             | 计算量小但不够精确    |
| ​**​引擎回调​**​ | 使用`OnBecameVisible()`/`OnBecameInvisible()`函数 | 依赖渲染管线，有1帧延迟 |
| ​**​精确检测​**​ | 执行射线检测（Raycast）或视锥体测试                         | 结果精准但性能开销大   |

## Level of detail
*Level of detail*, is another common rendering optimization technique. Objects nearest to the player are rendered at full fidelity(保真度) using detailed meshes and textures. Distant objects use less detailed meshes and textures. A similar approach can be used with our code. For example, we may have an enemy with an AI script that determines its behavior. Part of this behavior may involve costly operations for determining what it can see and hear, and how it should react to this input. We could use a level of detail system to enable and disable these expensive operations based on the enemy's distance from the player. In a Scene with many of these enemies, we could make a considerable performance saving if only the nearest enemies are performing the most expensive operations.
```csharp
// 敌人AI控制脚本
void Update() 
{
    float distanceToPlayer = Vector3.Distance(transform.position, player.position);
    // LOD分级逻辑
    if(distanceToPlayer < 10f) // 近距离
    {
        UpdateHighPrecisionSensory(); // 高精度视觉/听觉检测
        UpdateComplexDecisionMaking(); // 复杂行为决策
    }
    else if(distanceToPlayer < 30f) // 中距离
    {
        UpdateBasicSensory(); // 基础感知检测
    }
    // 远距离不执行AI计算
}
```
Unity's [CullingGroup](https://docs.unity3d.com/Manual/CullingGroupAPI.html) API allows us to hook into Unity's LOD system to optimize our code. The Manual page for the CullingGroup API contains several examples of how this might be used in our game. As ever, we should test, profile and find the right solution for our game.