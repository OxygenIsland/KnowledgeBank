通用渲染管线 (Universal Render Pipeline, URP) 使用 Volume 框架。Volume 可以根据摄像机相对于每个 Volume的位置来覆盖或扩展场景属性。
URP 为 Volume 实现了专用的游戏对象：**Global Volume**、**Box Volume**、**Sphere Volume**、**Convex Mesh Volume**。
![[Pasted image 20231014103852.png|587]]
可以将 **Volume** 组件添加到任何游戏对象。一个场景可以包含多个带有 Volume 组件的游戏对象。可以将多个 Volume 组件添加到一个游戏对象。

Volume 组件引用一个包含场景属性的 [[Volume#Volume Profiles|Volume Profile]] 。包含每个属性的默认值，并在默认情况下隐藏它们。使用 [[Volume#Volume Overrides|Volume Override]] 可以更改或扩展配置文件中的默认属性。

在运行时，URP 查找附加到场景内活动游戏对象的所有已启用的 Volume 组件，并确定每个体积对最终场景设置的贡献。URP 使用摄像机位置以及 Volume 组件属性来计算此贡献。URP 会插入所有具有非零贡献的体积的值，从而计算最终属性值。
## Volume 组件属性
- **Mode**
  Global：Volume 无边界，并允许 Volume影响场景中的每个摄像机。  
  Local：为 Volume 指定边界，Volume 仅影响边界内的摄像机。向Volume 的游戏对象添加碰撞体，并使用该碰撞体设置边界。如果摄像机在碰撞体的边界以内，则Volume会影响摄像机。
- **Blend Distance**
   距 URP 开始混合的体积碰撞体最远的距离。值为 0 表示 URP 在进入时立即应用 Volume 的 Override。仅当从 **Mode** 下拉选单中选择 **Local** 时，才显示此属性。
- **Weight**
   Volume 对场景的影响程度。URP 会用此参数乘以 摄像机位置和Blend Distance计算出的值。
- **Priority**
   URP 使用此值来确定当多个 Volume对场景具有相同的影响程度时使用哪个 Volume。URP 首先使用具有更高优先级的 Volume。
- [[Volume#Volume Profiles|Profiles]]
   这是一个配置文件资源，其中包含的 Volume 组件存储了 URP 用于处理此 Volume 的属性。
## Volume Profiles
**Profile** 字段存储了一个 Volume 配置文件资源，此资源包含 URP 用于渲染场景的属性。可以编辑此体积配置文件，或为 **Profile** 字段分配不同的 Volume Profiles。还可以分别单击 **New** 和 **Clone** 按钮来创建体积配置文件或克隆当前的 Volume Profiles。
## Local Volumes
在此示例中，URP 在摄像机位于某个盒型碰撞体内时应用post-processing effects。
1. 在场景中，创建一个新的盒体 (**GameObject > Volume > Box Volume**)。
2. 选择该盒体。在 Inspector 中的 **Volume** 组件下的 **Profile** 字段中，单击 **New**。![[Pasted image 20231014111115.png|675]]
   Unity 会创建新的体积配置文件，并将 **Add Override** 按钮添加到 Volume 组件。![[Pasted image 20231014111310.png|610]]
3. 如果场景中有其他 Volume，更改 Priority 属性的值，确保来自该 Volume 的 Override 具有 更高的优先级。![[Pasted image 20231014111459.png|738]]
4. 单击 [Add Override](https://docs.unity3d.com/cn/Packages/com.unity.render-pipelines.universal@12.1/manual/VolumeOverrides.html#volume-add-override)。在 Volume Overrides 对话框中，选择一个后期处理效果。
5. 在 Collider 组件中，调整 Size 和 Center 属性，使碰撞体占据您希望局部后期处理效果所在的体积。![[Pasted image 20231014111629.png|560]]
6. 确保选中 **Is Trigger** 复选框。当摄像机位于体积的盒型碰撞体的边界以内时，URP 会使用盒体的 Volume Override。
## Volume Overrides
使用 Volume Overrides 可以更改或扩展配置文件 (Volume Profile)中的默认属性。URP 将后期处理效果实现为 Volume Overrides。下图显示了 URP 模板 SampleScene 中的渐晕 (Vignette) 后期处理效果。![[Pasted image 20231014112136.png|550]]
在 Volume Overrides 中，每个属性左侧的复选框可用于启用或禁用特定属性。如果禁用某个属性，URP 将改用该属性在 Volume component中的默认值。要启用或禁用所有属性，请使用属性列表上方的 **All** 或 **None** 快捷方式。
