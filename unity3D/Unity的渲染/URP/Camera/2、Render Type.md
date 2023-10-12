通用渲染管线 (Universal Render Pipeline, URP) 中有两种类型的摄像机：
- [[2、Render Type#Base Camera|基础摄像机 (Base Camera)]] 是一种渲染到渲染目标（屏幕或[渲染纹理](https://docs.unity3d.com/Manual/class-RenderTexture.html)）的通用摄像机。
- [[#Overlay Camera|叠加摄像机 (Overlay Camera)]] 渲染在另一个摄像机的输出之上。基础摄像机的输出可以和一个或多个叠加摄像机的输出结合起来。这种技术称为[[2、Render Type#Camera stacking|摄像机堆叠 (Camera stacking)]]。
使用摄像机的 **Render Type** 属性可使摄像机成为基础摄像机或叠加摄像机。
可通过设置摄像机的 Universal Additional Camera Data 组件的 renderType 属性，在脚本中更改摄像机的类型，如下所示：
```csharp
var cameraData = camera.GetUniversalAdditionalCameraData();
cameraData.renderType = CameraRenderType.Base;
```
## Base Camera
URP 中默认的摄像机类型是基础摄像机。基础摄像机是一种渲染到特定渲染目标的通用摄像机。
要在 URP 中渲染任何内容，场景中必须至少有一个基础摄像机。==在一个场景中可以有多个 baseCamera，但是不同 baseCamera 的图层之间不能融合，只会根据优先级进行覆盖。想要将多视角的画面融合在一起的话需要使用 Camera Stacking==
## Overlay Camera
叠加摄像机将其视图渲染在另一个摄像机的输出之上。叠加摄像机可用于创建诸如 2 D UI 中的 3 D 对象或车辆中的驾驶舱之类的效果。
必须通过摄像机堆叠系统将叠加摄像机与一个或多个基础摄像机结合使用。不能单独使用叠加摄像机。不在摄像机堆叠中的叠加摄像机不会执行其渲染循环的任何步骤。
## Camera stacking
摄像机堆叠允许将多个摄像机的结果合成在一起。摄像机堆叠由一个基础 (Base) 摄像机和任意数量的额外叠加 (Overlay) 摄像机组成。当摄像机堆叠中的多个摄像机渲染到同一个渲染目标时，Unity 会为摄像机堆叠中的每个摄像机绘制渲染目标中的每个像素。此外，如果多个 Base camera 或 camera stack 渲染到同一渲染目标的同一区域，则 Unity 会再次在重叠区域中绘制所有像素，渲染次数与每个 Base camera 或 camera stack 所需的渲染次数相同。必须小心操作，确保摄像机的顺序不会导致过度绘制。
### 使用叠加摄像机的叠加效果：
![[Pasted image 20230731212118.png]]
Scene 中的布局，五辆汽车并没有放在一起，但是在 Game 视图中观看的时候，如下图所示：
![[Pasted image 20230731212153.png]]
单独看一下两个相机的视图：
- Base:
![[Pasted image 20230731212220.png]]
- Overlay ![[Pasted image 20230731212251.png]] 必须通过 camera stack 系统将 overlay camera 与一个或多个 base camera 结合使用。不能单独使用叠加摄像机。不在摄像机堆叠中的叠加摄像机不会执行其渲染循环的任何步骤。
可点击 Stack 下方的+号添加其他的 Overlay 相机，-号删除，选中上下拖动调整渲染顺序。
![[Pasted image 20230731212429.png]]
- 注意：Base 类型的摄像机是最先渲染的，所以在最下层，然后再到 Stack 里面的 Overlay 摄像机，按照 Stack 里面从上到下的顺序，最上面的相机最先开始渲染。
## Rendering to a Render Texture
在通用渲染管线 (Universal Render Pipeline, URP) 中，摄像机可以渲染到屏幕或渲染到 Render Texture。默认设置为渲染到屏幕，这也是最常见的用例，但渲染到渲染纹理可以创建 CCTV 摄像机监控器等效果。

如果有一个摄像机渲染到渲染纹理，必须有另一个摄像机随后将该渲染纹理渲染到屏幕。在 URP 中，所有渲染到 Render Texture 的摄像机将在所有渲染到屏幕的摄像机之前执行它们的渲染循环。这样可以确保渲染纹理已准备好渲染到屏幕。
### 渲染到 Render Texture 后再将该 Render Texture渲染到屏幕
![在 URP 中渲染到渲染纹理](https://docs.unity3d.com/cn/Packages/com.unity.render-pipelines.universal@12.1/manual/images/camera-inspector-output-target.png)

在项目中使用 **Assets** > **Create** > **Render Texture** 创建一个渲染纹理资源。在场景中创建一个 Quad。在项目中创建一个 Material，然后选择该 Material。在 Inspector 中，将渲染纹理拖到材质的 **Base Map** 字段中。在 Scene 视图中，将材质拖到 Quad 上。在场景中创建一个摄像机。此摄像机的 **Render Mode** 默认为 **Base**，因此是一个基础摄像机 (Base Camera)。选择该基础摄像机。在 Inspector 中，滚动到 Output 部分。将摄像机的 **Output Target** 设置为 **Texture**，然后将渲染纹理拖到 **Texture** 字段上。在场景中创建另一个摄像机。此摄像机的 **Render Mode** 默认为 **Base**，因此是一个基础摄像机。将四边形放置在新基础摄像机的视图中。
