## overview
Unity 在每一帧中,渲染每个 active camera之前会引发一个 `beginCameraRendering` 事件。如果摄像机处于inactive状态（例如，摄像机游戏对象上的 **Camera** 组件复选框被清除），Unity 不会引发此摄像机的 `beginCameraRendering` 事件。

当您订阅此事件的方法时，您可以在 Unity 渲染摄像机之前执行自定义逻辑。自定义逻辑的示例包括渲染额外的摄像机以渲染纹理，并将这些纹理用于平面反射或监控摄像机视图等效果。

[RenderPipelineManager](https://docs.unity3d.com/ScriptReference/Rendering.RenderPipelineManager.html) 类中的其他事件提供了更多自定义 URP 的方法。您也可以将本文所述的原则应用于这些事件。
## example
This example demonstrates how to subscribe a method to the `beginCameraRendering` event.
1. 在场景中，创建一个立方体。将这个立方体命名为“Example Cube”。
2. 在项目中，创建一个 C# 脚本。将这个脚本命名为 `URPCallbackExample`。
3. 将以下代码复制并粘贴到这个脚本中。
```csharp
using UnityEngine; using UnityEngine.Rendering; public class URPCallbackExample : MonoBehaviour 
{ 
	private void OnEnable() 
	{ 
	// Add WriteLogMessage as a delegate of the RenderPipelineManager.beginCameraRendering event 
	RenderPipelineManager.beginCameraRendering += WriteLogMessage; 
	} 
	private void OnDisable() 
	{
	 RenderPipelineManager.beginCameraRendering -= WriteLogMessage; 
	} 
	 // When this method is a delegate of RenderPipeline.beginCameraRendering event, Unity calls this method every time it raises the beginCameraRendering event 
	void WriteLogMessage(ScriptableRenderContext context, Camera camera) 
	{
	Debug.Log($"Beginning rendering the camera: {camera.name}"); 
	} 
}
```
当您订阅某个事件时，您的处理程序方法（在此例中为 `WriteLogMessage`）必须接受事件委托中定义的参数。在此示例中，事件委托是 `RenderPipeline.BeginCameraRendering`，它需要以下参数：`<ScriptableRenderContext, Camera>`。
4. 将 `URPCallbackExample` 脚本附加到 Example Cube。
5. 选择 **Play**。每次 Unity 引发 `beginCameraRendering` 事件时，Unity 都会在 Console 窗口中打印来自脚本的消息。
![[Pasted image 20231109211504.png|575]]
6. 要调用 `OnDisable()` 方法：在运行模式下，选择 Example Cube，并清除脚本组件标题旁边的复选框。Unity 会从 `RenderPipelineManager.beginCameraRendering` 事件中取消订阅 `WriteLogMessage`，并停止在 Console 窗口中打印消息。
![[Pasted image 20231109211548.png|481]]
