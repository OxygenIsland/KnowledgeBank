---
title: "[[3、Clearing, rendering order and overdraw]]"
type: Literature
status: done
Creation Date: 2023-11-10 14:11
tags:
---
## 1、Clering
在 Unity 中，URP（Universal Render Pipeline）相机中的 Clearing（清除）是指相机在渲染新的帧之前如何处理场景中的现有内容。Clearing 主要包括清除颜色缓冲区（Clear Color Buffer）、深度缓冲区（Clear Depth Buffer）和模板缓冲区（Clear Stencil Buffer）等操作。

具体来说，清除通常发生在渲染每一帧之前，以确保在绘制新的场景之前，旧的渲染结果被清除，从而获得干净的画布。以下是 Clearing 的一些重要概念：

1. **Clear Color Buffer**：这是屏幕上的颜色缓冲区，它存储了像素的颜色信息。在渲染新的帧之前，通常需要将颜色缓冲区清除为背景颜色或其他默认颜色。
2. **Clear Depth Buffer**：深度缓冲区用于存储像素的深度信息，用于确定哪些像素在前面，哪些在后面。在渲染新帧之前，通常需要将深度缓冲区清除为最大深度值，表示没有像素被绘制。
3. **Clear Stencil Buffer**：模板缓冲区通常用于实现一些高级的渲染效果，如遮罩。在渲染新帧之前，你也可以选择清除模板缓冲区。

URP 相机的 Clearing 选项允许你定义在渲染新的帧之前如何执行上述清除操作。你可以选择是否清除颜色缓冲区、深度缓冲区和模板缓冲区，以及使用哪种颜色来清除颜色缓冲区。这允许你控制渲染的输出，以满足特定的需求和效果。
### 1.1 Base Camera
Color Buffer
在**Background Type**中进行设置
- Skybox，在渲染循环开始时，将颜色缓冲区清除为天空盒
- Solid Color，在渲染循环开始时，将颜色缓冲区清除为纯色
- Uninitialized，使用未初始化的颜色缓冲区。
	Uninitialized 的颜色缓冲区的内容因平台而异。在某些平台上，Uninitialized 的颜色缓冲区将包含来自前一帧的数据。在其他平台上，Uninitialized 的颜色缓冲区将包含未初始化的内存。仅当摄像机绘制到颜色缓冲区中的每个像素，且不希望产生不必要清除操作的成本时，才应选择使用未初始化的颜色缓冲区。
Depth Buffer
	base camera 在每个渲染循环开始时清除其深度缓冲区。
### 1.2 Overlay Camera
Color Buffer
在渲染循环开始时，Overlay Camera接收一个颜色缓冲区，该缓冲区包含来自摄像机堆叠中先前摄像机的颜色数据。颜色缓冲区的内容不会清除。
Depth Buffer
勾选**Clear Depth**属性可以设置
在渲染循环开始时，Overlay Camera接收一个深度缓冲区，该缓冲区包含来自摄像机堆叠中先前摄像机的深度数据。
当 **Clear Depth** 设置为 true 时，Overlay Camera会清除深度缓冲区，并将其视图绘制到所有现有颜色数据之上的颜色缓冲区。当 **Clear Depth** 设置为 false 时，叠加摄像机会在将其视图绘制到颜色缓冲区之前针对深度缓冲区进行测试。
## 2、Camera clearing and rendering order
如果 URP 场景包含多个摄像机，Unity 每帧执行一次以下操作：
1. Unity 获取场景中所有激活的 base camera的列表。
2. Unity 将激活的 base camera 组织成 2 组：一组摄像机[[2、Render Type#Rendering to a Render Texture|将其视图渲染到渲染纹理]] ，另一组摄像机将其视图渲染到屏幕。
3. Unity 按照 **Priority** 顺序对渲染到渲染纹理的 base camera进行排序，因此具有更高 **Priority** 值的摄像机将最后绘制。
4. 对于渲染到渲染纹理的每个 base camera，Unity 执行以下步骤：
    1. 剔除基础摄像机
    2. 将基础摄像机渲染到渲染纹理
    3. 对于基础摄像机的 [[2、Render Type#Camera stacking|Camera stacking]] 中的每个 overlay camera，按照在摄像机堆叠中定义的顺序：
        1. 剔除 overlay camera
        2. 将 overlay camera渲染到渲染纹理
5. Unity 按照 **Priority** 顺序对渲染到屏幕的基础摄像机进行排序，因此具有更高 **Priority** 值的摄像机将最后绘制。
6. 对于渲染到屏幕的每个基础摄像机，Unity 执行以下步骤：
    1. 剔除 base camera
    2. 将 base camera渲染到屏幕
    3. 对于 base camera 的摄像机堆叠中的每个 base camera，按照在摄像机堆叠中定义的顺序：
        1. 剔除 overlay camera
        2. 将 overlay camera渲染到屏幕

由于 overlay camera 出现在多个摄像机堆叠中，或者由于 overlay camera多次出现在同一个摄像机堆叠中，因此 Unity 可以在一帧内多次渲染叠加摄像机的视图。发生这种情况时，Unity 不会重用剔除或渲染操作的任何元素，而是按照上面详述的顺序完全重复这些操作。
## 过度绘制

URP 在摄像机内执行多项优化，包括优化渲染顺序以减少过度绘制。但是，使用摄像机堆叠时，实际上会定义这些摄像机的渲染顺序。因此，必须小心操作，确保摄像机的顺序不会导致过度绘制。

当摄像机堆叠中的多个摄像机渲染到同一个渲染目标时，Unity 会为摄像机堆叠中的每个摄像机绘制渲染目标中的每个像素。此外，如果多个基础摄像机或摄像机堆叠渲染到同一渲染目标的同一区域，则 Unity 会再次在重叠区域中绘制所有像素，渲染次数与每个基础摄像机或摄像机堆叠所需的渲染次数相同。

