---
title: "[[ErrorOr]]"
type: Permanent
status: done
Creation Date: 2025-08-09 12:38
tags:
  - UnityPlugin
---
### ErrorOr 是什么？—— 一个优雅的错误处理“容器”
从本质上讲，ErrorOr 是一个 C# 库，它提供了一个名为 ErrorOr\<T> 的泛型结构体。你可以把它想象成一个特殊的、智能的“盒子”或“容器”。这个盒子在任何时候，都只处于两种状态之一：
1. **成功状态**: 盒子里装着一个你期望的、类型为 T 的成功值 (例如，一个 PlayerData 对象，一个 Texture2D，或者一个表示成功的 Success 标记)。
2. **失败状态**: 盒子里装着一个或多个 Error 对象，详细描述了哪里出了问题。
    
它设计的核心目标，是用来**替代**那些在软件开发中普遍存在但又问题多多的传统错误处理方式。

#### 它解决了什么痛点？

在没有 ErrorOr 的世界里，我们通常这样处理错误：

1. **返回 null**:
    - **问题**: 这是“空引用异常” (NullReferenceException) 的万恶之源。调用者很容易忘记检查 null，导致程序在不经意间崩溃。返回 null 也没有提供任何关于“为什么失败”的上下文信息。
2. **抛出异常 (throw new Exception())**:
    - **问题**: 异常的性能开销很大，而且它会粗暴地中断程序的正常控制流。它更适合处理真正**意外的、无法恢复的**系统级故障（比如栈溢出），而不适合处理**可预期的、业务逻辑上的**失败（比如“用户名已存在”、“文件未找到”）。
3. **返回错误码 (如 int 或 enum)**:
    - **问题**: 调用者需要去查阅文档才能明白 -1 或 ErrorCode.ConnectionFailed 代表什么。这种方式通常需要通过 out 参数来返回成功值，使得函数签名变得笨拙，而且容易造成“魔法数字”满天飞。

ErrorOr 通过提供一个统一、明确且信息丰富的返回类型，优雅地解决了以上所有问题。

### ErrorOr 在 Unity 中的关键作用
在 Unity 开发中，充满了各种可能失败的操作。ErrorOr 在这些场景下能发挥巨大威力，让你的代码更健壮、更清晰、更易于维护。
#### 1. 异步操作与网络请求 (Web Requests)
这是 ErrorOr 在 Unity 中最核心的应用场景之一。使用 UnityWebRequest 或 HttpClient 时，失败是常态。
**传统方式 (问题重重):**
```csharp
async Task<PlayerData> LoadPlayerDataFromServer(string id)
{
    // ... 发送请求 ...
    if (request.result != UnityWebRequest.Result.Success)
    {
        Debug.LogError("Network error: " + request.error); // 底层直接打印日志
        return null; // 返回 null，UI 层不知道具体原因
    }
    // ...
    return JsonConvert.DeserializeObject<PlayerData>(request.downloadHandler.text);
}
// 调用方：
var data = await LoadPlayerDataFromServer("p1");
if (data == null) {
    // 为什么是 null？是网络断了？还是服务器404？还是JSON解析错了？不知道！
}
```
使用 ErrorOr (清晰、可控):
```csharp
async Task<ErrorOr<PlayerData>> LoadPlayerDataFromServer(string id)
{
    // ... 发送请求 ...
    if (request.result != UnityWebRequest.Result.Success)
    {
        // 返回结构化的错误
        return Error.Network("API.RequestFailed", request.error); 
    }
    try
    {
        var data = JsonConvert.DeserializeObject<PlayerData>(request.downloadHandler.text);
        return data; // 返回成功值
    }
    catch (JsonException ex)
    {
        // 返回另一种明确的错误
        return Error.Validation("API.Response.InvalidJson", ex.Message);
    }
}
// 调用方：
var result = await LoadPlayerDataFromServer("p1");
result.Match(
    onValue: data => uiManager.ShowPlayerData(data),
    onError: errors => uiManager.ShowErrorPopup(errors[0]) // UI层根据错误类型显示不同提示
);
```
#### 2. 资源加载 (Addressables / Resources)

加载资源是一个典型的可能失败的操作（资源不存在、网络问题导致加载失败等）。

**传统方式:**
```csharp  
Addressables.LoadAssetAsync<GameObject>("MyPrefab").Completed += handle => {  
	if (handle.Status != AsyncOperationStatus.Succeeded)  
	{  
		Debug.LogError("Prefab not found!");  
		// 然后呢？游戏可能就卡在这里了，或者某个对象无法生成  
	}  
	else
	{  
		Instantiate(handle.Result);  
	}  
};
````
**使用 `ErrorOr` (封装异步逻辑):**
```csharp
public async Task<ErrorOr<T>> LoadAddressableAsset<T>(string key)
{
    var handle = Addressables.LoadAssetAsync<T>(key);
    await handle.Task;
    if (handle.Status == AsyncOperationStatus.Succeeded)
    {
        return handle.Result;
    }
    return Error.NotFound("Addressables.AssetNotFound", $"Asset with key '{key}' failed to load.");
}
// 调用方：
var prefabResult = await LoadAddressableAsset<GameObject>("MyPrefab");
prefabResult.Match(
    onValue: prefab => Instantiate(prefab),
    onError: _ => Debug.LogError("Cannot instantiate player, prefab is missing!")
);
````

#### 3. 游戏存档与读档 (File I/O)

保存游戏可能因为磁盘已满、没有写入权限而失败。

**传统方式 (void):**  
void SaveGame() 在内部用 try-catch 打印日志，调用者无法得知保存是否成功，也就无法给玩家“保存成功”的提示。

**使用 ErrorOr (ErrorOr\<Success>):**  
ErrorOr\<Success> SaveGame() 会明确返回成功或失败。UI层调用后，可以通过 Match 来决定是显示“保存成功！”还是“保存失败，磁盘空间不足！”。

#### 4. 复杂的业务逻辑（如合成系统、技能释放）
在游戏中，很多操作都有前置条件。
**传统方式:**
```csharp
bool CanCraft(Recipe recipe)
{
    if (!inventory.HasItem(recipe.itemA)) return false;
    if (!inventory.HasItem(recipe.itemB)) return false;
    return true;
}
```
false 并没有告诉你到底是缺材料A还是缺材料B。
**使用 ErrorOr:**
```csharp
ErrorOr<Success> CanCraft(Recipe recipe)
{
    var errors = new List<Error>();
    if (!inventory.HasItem(recipe.itemA)) 
        errors.Add(Error.Validation("Crafting.MissingItem", "缺少木材"));
    if (!inventory.HasItem(recipe.itemB))
        errors.Add(Error.Validation("Crafting.MissingItem", "缺少铁矿"));

    if (errors.Count > 0)
        return errors; // 一次性返回所有缺失的材料

    return Result.Success;
}
```
UI层拿到这个包含两个 Error 的列表后，可以将“木材”和“铁矿”两个UI元素都标红，用户体验极佳。
#### 5. 增强调试体验
这是 ErrorOr 一个被低估但极其强大的优点。通过精心设计 Error.ToString()，你可以让错误日志直接链接到代码。
```csharp
// Error.ToString() 的实现
public override string ToString()
{
#if UNITY_EDITOR
    // 在Unity编辑器中，输出可点击的超链接！
    return $"[Error] Code: {Code}, Desc: \"{Description}\"\nAt: <a href=\"{SourceFilePath}\" line=\"{SourceLineNumber}\">{SourceFilePath}:{SourceLineNumber}</a>";
#else
    return base.ToString();
#endif
}
```

当你在Unity控制台看到这个错误日志时，可以直接点击它，VS Code或Rider就会立刻跳转到创建这个 Error 的那一行代码，调试效率瞬间翻倍！

### 总结：ErrorOr 为 Unity 开发带来的价值

- **代码清晰性与可读性**: 函数签名 ErrorOr\<T> Func() 清晰地宣告“此操作可能失败”，迫使调用者正视这一点。
- **强制错误处理**: Match 模式从机制上杜绝了忘记处理失败路径的可能，让代码更健壮。
- **丰富的错误上下文**: 不再是简单的null或false，而是结构化的、包含详细信息的错误对象。
- **优雅的解耦**: 将“执行操作”的逻辑与“处理结果”的逻辑（如更新UI、记日志）彻底分开，符合单一职责原则。
- **提升调试效率**: 可点击的错误日志是Unity开发者的福音。
- **对异步友好的流程控制**: async/await 与 ErrorOr 结合，能以同步代码的形式编写出清晰、强大的异步错误处理流程。
    

总而言之，ErrorOr 不仅仅是一个工具库，它更是一种先进的、现代化的编程思想。在复杂的Unity项目中引入它，是对项目代码质量和长期可维护性的一次巨大投资。