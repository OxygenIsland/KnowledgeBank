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
3. 模型识别、图片识别、特征识别是否还支持？通过 ARKit 是否可以拿到图像
4. 在 visionOS 平台下不支持的插件
	- 3DWebview
	- 
 