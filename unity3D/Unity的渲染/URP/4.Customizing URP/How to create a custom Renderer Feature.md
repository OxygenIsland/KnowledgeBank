- The **Scriptable Render Pipeline Settings** property refers to a URP asset (**Project Settings** > **Graphics** > **Scriptable Render Pipeline Settings**).
创建示例场景和游戏对象。
创建可编写脚本的渲染器功能，并将其添加到通用渲染器中。
创建可编写脚本的渲染过程并将其排入队列。
在 Execute 方法中实现渲染命令。
实现特定于示例的材质和渲染代码。
更改渲染过程的顺序
此示例的完整代码
## Create example Scene and GameObjects
1. Create a plane.
2. Create a new Material and assign it the `Universal Render Pipeline/Lit` shader. Set the base color to grey (for example, `#6A6A6A`). Call the Material `Plane`.
3. Create a Point Light and place it above the plane.
Your Scene should look like the following illustration:
![[Pasted image 20231109212022.png|725]]
## Create a scriptable Renderer Feature and add it to the Universal Renderer
This part shows how to create a scriptable Renderer Feature and implement the methods that let you configure and inject `ScriptableRenderPass` instances into the scriptable Renderer.
1. Create a new C# script. Call the script `LensFlareRendererFeature.cs`.
2. Open the script, remove all the code from the `LensFlareRendererFeature` class that Unity created. Add the following `using` directive.
```csharp
using UnityEngine.Rendering.Universal;
```
3. The `LensFlareRendererFeature` class must inherit from the `ScriptableRendererFeature` class.
```csharp
public class LensFlareRendererFeature : ScriptableRendererFeature
```
4. The class must implement the following methods:
    - `Create`: Unity calls this method on the following events:
        - When the Renderer Feature loads the first time.
        - When you enable or disable the Renderer Feature.
        - When you change a property in the inspector of the Renderer Feature.
    - `AddRenderPasses`: Unity calls this method every frame, once for each Camera. This method lets you inject `ScriptableRenderPass` instances into the scriptable Renderer.
Now you have the custom `LensFlareRendererFeature` Renderer Feature with its main methods.
Below is the complete code for this part.
```csharp
using UnityEngine; 
using UnityEngine.Rendering; 
using UnityEngine.Rendering.Universal; 
public class LensFlareRendererFeature : ScriptableRendererFeature 
{ 
	public override void Create() 
	{ 
	} 
	public override void AddRenderPasses(ScriptableRenderer renderer, ref RenderingData renderingData) 
	{ 
	} 
}
```
[[4.URP Renderer Feature#How to add a Renderer Feature| Add the Renderer Feature you created to the the Universal Renderer asset.]]
![[Pasted image 20231109213349.png|478]]
Add the Lens Flare Renderer Feature to the Universal Renderer.
## Create and enqueue the scriptable Render Pass
This part shows how to create a scriptable Render Pass and and enqueue its instance into the scriptable Renderer.
1. In the `LensFlareRendererFeature` class, declare the `LensFlarePass` class that inherits from `ScriptableRenderPass`.
```csharp
using UnityEngine; 
using UnityEngine.Rendering; 
using UnityEngine.Rendering.Universal; 
public class LensFlareRendererFeature : ScriptableRendererFeature 
{ 
	class LensFlarePass : ScriptableRenderPass 
	{ 
		//Unity runs the `Execute` method every frame. In this method, you can implement your custom rendering functionality.
		public override void Execute(ScriptableRenderContext context, ref RenderingData renderingData)
		{ 
			Debug.Log(message: "The Execute() method runs."); 
		} 
	} 
	private LensFlarePass _lensFlarePass; 
	public override void Create() 
	{ 
		_lensFlarePass = new LensFlarePass(); 
	} 
	public override void AddRenderPasses(ScriptableRenderer renderer, ref RenderingData renderingData) 
	{ renderer.EnqueuePass(_lensFlarePass); 
	} 
}
```
Now your custom `LensFlareRendererFeature` Renderer Feature is executing the `Execute` method inside the custom `LensFlarePass` pass.
## Implement rendering commands in the Execute method
