---
title: "[[How to configure post-processing effects in URP]]"
type: Literature
status: done
Creation Date: 2023-11-10 14:11
tags:
---
## 在URP 模板场景中使用后期处理
URP 模板的 SampleScene 场景中预先配置了后期处理**Post-process Volume**。
![[Pasted image 20231013200309.png]]
要添加额外的效果，点击 [Add Overrides](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@12.1/manual/VolumeOverrides.html#volume-add-override).
## 在新的 URP 场景中配置后期处理
1. 选择一个摄像机，然后选择 **Post Processing** 复选框。![[Pasted image 20231013200619.png|700]]
2. 在场景中添加一个具有 [Volume](https://docs.unity3d.com/cn/Packages/com.unity.render-pipelines.universal@12.1/manual/Volumes.html) 组件的游戏对象。此指令将添加一个全局卷 (Global Volume)。选择 **GameObject > Volume > Global Volume**。
3. 选择 **Global Volume** 。在 Volume 组件中，单击 Profile 属性右侧的 **New** 按钮创建一个新的配置文件 (Profile)。![[Pasted image 20231013200746.png|750]]
4. 向 Volume 组件添加 Volume Overrides，为 camera 添加后期处理效果。![[Pasted image 20231014102240.png|501]]
5. 可以在 Volume 组件的Overrides中调整后期处理效果设置![[Pasted image 20231014103530.png|700]]