---
title: "[[1、Universal Additional Camera Data 组件]]"
type: Literature
status: done
Creation Date: 2023-11-10 14:11
tags:
---
Universal Additional Camera Data 组件是通用渲染管线 (URP) 用于内部数据存储的组件。

在 URP 中，具有 Camera 组件的游戏对象还必须具有 Universal Additional Camera Data 组件。如果项目使用 URP，Unity 会在您创建摄像机游戏对象时自动添加 Universal Additional Camera Data 组件。不能从摄像机游戏对象上移除 Universal Additional Camera Data 组件。

如果不使用脚本来控制和自定义 URP，则无需对 Universal Additiona Camera Data 组件执行任何操作。

如果要使用脚本来控制和自定义 URP，则可以在如下所示的脚本中访问摄像机的 Universal Additional Camera Data 组件：
```csharp
var cameraData = camera.GetUniversalAdditionalCameraData();
```
