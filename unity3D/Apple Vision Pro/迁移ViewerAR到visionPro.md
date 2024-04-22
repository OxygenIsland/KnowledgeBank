## 开发环境配置
硬件
- [[1. visionOS Platform Overview#1.1 vision​OS Modes|Apple Silicon Mac]]
软件
- Unity 2022.3（LTS）或更高的 unity 版本
- Xcode 15 beta 2
- visionOS build support
- unity PolySpatial

## feature use
- ViewerAR 应该在 Full Space 模式下以一个 Immersive (MR) content 的形式进行显示（如何配置）
- viewerAR 中的 3 D 内容应该通过  [[1. visionOS Platform Overview#1.2.1 Volumes|Volumes]] 进行显示和放置

## Problem
1. 跟随用户的操作界面 UI (应该放置到一个 unbound volumes 中)
2. 交互方式需要更改，利用手势追踪去与 UI 交互（以前的焦点交互还可以响应吗）
	1. 统一使用 polySpatial UI Raycaster 与 UI 界面进行交互
	2. 写一个跟随脚本和固定脚本
3. 模型识别、图片识别、特征识别是否还支持？通过 ARKit 是否可以拿到图像
4. 在 visionOS 平台下不支持的插件
	- 3DWebview
## TODO LIST
1. Unity 打包成功，xcode 模拟器运行
2. 如何打包一个 unbound volumes 应用 (UI 界面放置在 space 中跟随用户)
3. 更新 shader，UI 显示异常
4.  [[Input#Head Tracking|获取头部位置]]


## ERROR
### 升级 unity2022 遇到的问题
1.ILRuntime.Runtime.Intepreter.RegisterFrameInfo' has an extra field 'ManagedStack' of type 'ILRuntime.Other.UncheckedList `1[System.Object]' in the player and thus can't be serialized  UnityEngine.GUIUtility:ProcessEvent (int,intptr,bool&)
![[038be6fc9627add5c7b2a3c14516c83.png|500]]
I have resolved this issue by deleting 'Library/Bee' and 'Library/BuildPlayerData' folders before run build script.  
(in Unity 2022.1.14)
使用 V 2.0.2 版本的 ILRuntime 没有出现该错误
### visionOS 平台遇到的问题
