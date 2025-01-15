---
title: "[[Camera]]"
type: Literature
status: done
Creation Date: 2023-09-27 12:47
tags:
---
## Main Camera
场景被创建出来时自带的 camera,一个场景可以有多个 camera,但是 Main Camera 只能有一个，即具有"MainCamera"tag 的物体只能有一个。
当添加多个 Camera 时，只能保留一个 Camera 的 Audio Listener，其他相机的 Audio Listener 需要移除因为 Scene 中只能允许一个 Audio Listener 存在
## Clear Flags
整个屏幕总体的背景颜色
- Skybox 天空盒(默认)。
- Solid Color: 纯色。结合下面的 background color 设置背景颜色
- Depth only 仅深度：画中画效果时，小画面摄像机选择该项可清除屏幕空部分信息只保留物体颜色信息。
- Don't clear 不清除任何颜色和深度缓存
## Projection 投射方式：
- Perspective 3D 透视图。物体具有近大远小的效果。(选择 Perspective 时，下面出现的 Field of View: 设置相机视野的远近距离，将镜头拉近或者拉远。)
- Orthography  2D 效果，没有透视感，通常小地图使用。 (选择 Orthography 时，下面出现 Size)
## Clipping Planes
从相机到开始渲染和停止渲染之间的距离，可以把远的东西过滤掉
- Near：绘制的最近点
- Far：绘制的最远点
- Camera 是一个四棱锥，近裁剪面即四棱锥的顶面，远裁剪面即四棱锥的底面。Camera 中所看到的（即游戏屏幕）应该是世界坐标的物体到近裁剪面的投影。
## Viewport Rectangle
设置 Camera Preview 相机画面的窗口大小和位置
- X,Y: 窗口坐标位置 (原点坐标(0,0): 左下角)
- W,H: 窗口的宽和高
用途: 比如设置小窗口。又比如当有两个相机的时候可以分屏使用(左右各一个)
## Depth
相机的渲染顺序。
具有较低深度的摄像机将在较高深度的摄像机之前渲染 
当depth数值大小相同时，谁最后修改谁在上面。
## Culling mask
遮蔽层。通过设置物体的 layer，让相机遮蔽掉不想看到的层中的物体。
默认 everything: 相机可以看到所有的层。
遮蔽方法：