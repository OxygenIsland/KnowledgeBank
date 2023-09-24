## stack 摄像机堆叠
摄像机堆叠允许将多个摄像机的结果合成在一起。摄像机堆叠由一个基础 (Base) 摄像机和任意数量的额外叠加 (Overlay) 摄像机组成。当摄像机堆叠中的多个摄像机渲染到同一个渲染目标时，Unity 会为摄像机堆叠中的每个摄像机绘制渲染目标中的每个像素。此外，如果多个 Base camera 或 camera stack 渲染到同一渲染目标的同一区域，则 Unity 会再次在重叠区域中绘制所有像素，渲染次数与每个 Base camera 或 camera stack所需的渲染次数相同。必须小心操作，确保摄像机的顺序不会导致过度绘制。

URP 中有两种类型的摄像机：
- 基础摄像机（Base Camera）是一种渲染到渲染目标（屏幕或渲染纹理）的通用摄像机。
- 叠加摄像机（Overlay Camera）渲染在另一个摄像机的输出之上。基础摄像机的输出可以和一个或多个叠加摄像机的输出结合起来。这种技术称为摄像机堆叠 (Camera stacking)。使用叠加摄像机可以做分层渲染、渲染层级调整、内景外景融合等等比较实用的功能。
![[Pasted image 20230731211934.png]]
代码中动态修改摄像机类型：
```c#
var cameraData = camera.GetUniversalAdditionalCameraData();
cameraData.renderType = CameraRenderType.Base;
```
### 使用叠加摄像机的叠加效果：
![[Pasted image 20230731212118.png]]
Scene 中的布局，五辆汽车并没有放在一起，但是在 Game 视图中观看的时候，如下图所示：
![[Pasted image 20230731212153.png]]
单独看一下两个相机的视图：
- Base:
- ![[Pasted image 20230731212220.png]]
- Overlay
- ![[Pasted image 20230731212251.png]] 必须通过 camera stack 系统将 overlay camera 与一个或多个 base camera结合使用。不能单独使用叠加摄像机。不在摄像机堆叠中的叠加摄像机不会执行其渲染循环的任何步骤。
可点击 Stack 下方的+号添加其他的 Overlay 相机，-号删除，选中上下拖动调整渲染顺序。
![[Pasted image 20230731212429.png]]
- 注意：Base 类型的摄像机是最先渲染的，所以在最下层，然后再到 Stack 里面的 Overlay 摄像机，按照 Stack 里面从上到下的顺序，最上面的相机最先开始渲染。

