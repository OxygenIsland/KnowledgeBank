## 1、onPreRender
In the Built-in Render Pipeline, Unity calls this `onPreRender` before any Camera begins rendering. To execute custom code at this point, create callbacks that match the signature of [CameraCallback](https://docs-alpha.unity3d.com/cn/2023.2/ScriptReference/Camera.CameraCallback.html), and add them to this delegate.

For similar functionality that applies only to a single Camera and requires your script to be on the same GameObject, see [MonoBehaviour.OnPreRender](https://docs-alpha.unity3d.com/cn/2023.2/ScriptReference/MonoBehaviour.OnPreRender.html).  
  
If you're using a Scriptable Render Pipeline, for example the Universal Render Pipeline, use [RenderPipelineManager](https://docs-alpha.unity3d.com/cn/2023.2/ScriptReference/Rendering.RenderPipelineManager.html) instead.  
  
Unity calls `onPreRender` after the Camera performs its culling operation. This means that if you make a change that affects what the Camera sees, the change will take effect from the next frame. To make a change to what the Camera sees in the current frame, use [Camera.onPreCull](https://docs-alpha.unity3d.com/cn/2023.2/ScriptReference/Camera-onPreCull.html).

```csharp
using UnityEngine;  
  
public class CameraCallbackExample : MonoBehaviour
{
    // Add your callback to the delegate's invocation list
    void Start()
    {
        Camera.onPreRender += OnPreRenderCallback;
    }  
    // Unity calls the methods in this delegate's invocation list before rendering any camera
    void OnPreRenderCallback(Camera cam)
    {
        [Debug.Log]("Camera callback: Camera name is " + cam.name);  
        // Unity calls this for every active [Camera](https://docs-alpha.unity3d.com/cn/2023.2/ScriptReference/Camera.html).
        // If you're only interested in a particular [Camera](https://docs-alpha.unity3d.com/cn/2023.2/ScriptReference/Camera.html),
        // check whether the [Camera](https://docs-alpha.unity3d.com/cn/2023.2/ScriptReference/Camera.html) is the one you're interested in
        if (cam == Camera.main)
        {
            // Put your custom code here
        }
    }  
    // Remove your callback from the delegate's invocation list
    void OnDestroy()
    {
        Camera.onPreRender -= OnPreRenderCallback;
    }
}
```