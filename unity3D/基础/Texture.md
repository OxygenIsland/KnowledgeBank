---
title: "[[Texture]]"
type: Literature
status: done
Creation Date: 2024-04-01 20:07
tags:
  - linker-exclude
---
## 1、Texture（纹理）：
- Texture 是所有纹理类型的基类，是一个抽象类，不能直接使用。
- 它定义了一些通用的属性和方法，例如 width、height、filterMode 等。
- 通常情况下，我们使用的是其具体的子类，如Texture2D、RenderTexture等。
## 2、Texture2D（二维纹理）：
- Texture2D 是最常用的纹理类型之一，用于表示2D 图像，例如图片、贴图等。
- 它可以从图片文件、颜色数组等数据源创建，并且可以通过像素级别进行读取和修改。
- Texture2D可以被应用到材质上，用于渲染3D模型或者UI元素。
## 3、RenderTexture （渲染纹理）：
- RenderTexture 是一种特殊类型的纹理，$\color{#FF0000}{用于在渲染过程中捕获场景的输出}$。
- 它通常用于实现多个摄像机的渲染目标、渲染到纹理效果等。
- RenderTexture 可以被设置为摄像机的渲染目标，使得摄像机的渲染结果不直接显示在屏幕上，而是渲染到指定的 RenderTexture 上。
- 
由于 RenderTexture 的特殊性，在某些特殊情况，会比 Texture2D 好用一些，下面举一个例子。
之前做项目的时候遇到了这样一种情况，我将摄像头的视频流渲染到了一张 Texture2D 的纹理上，当我需要拍照时，我需要从这个 Texture2D 上获取一张图片，我是这样做的：
```csharp
// 摄像机视频流纹理
Texture2D _cameraTexture;  

// 复制源纹理的像素数据到新的纹理中 
Texture2D newTexture = new Texture2D(_cameraTexture.width, _cameraTexture.height, _cameraTexture.format, _cameraTexture.mipmapCount > 1); 

newTexture.SetPixels(_cameraTexture.GetPixels()); 
newTexture.Apply(); 
```
当我这样做时，新纹理 newTexture 中并没有复制到视频流中的一帧图片，newTexture 是空白的，我百思不得其解，所以我换了一种思路：
```csharp
Texture2D texture2D = new Texture2D(_cameraTexture.width, _cameraTexture.height, TextureFormat.RGBA32, false);
RenderTexture currentRT = RenderTexture.active;
RenderTexture renderTexture = RenderTexture.GetTemporary(_cameraTexture.width, _cameraTexture.height, 32);
//将源`RenderTexture`的内容复制到临时的`RenderTexture`中。
Graphics.Blit(_cameraTexture, renderTexture);

RenderTexture.active = renderTexture;
texture2D.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
texture2D.Apply();

RenderTexture.active = currentRT;
RenderTexture.ReleaseTemporary(renderTexture);
```
1. `RenderTexture.active` 是一个静态属性，用于获取或设置当前的渲染目标（render target）。
	渲染目标（render target）是指所有的绘制操作将会渲染到的目标纹理。$\color{#FF0000}{这个目标纹理可以是屏幕（即显示器），也可以是一个渲染纹理（RenderTexture）对象。}$ 当渲染操作发生时，所有的渲染结果都会被绘制到当前的渲染目标上。通过 `RenderTexture.active` 属性可以获取或设置当前的渲染目标。当你希望将渲染结果绘制到特定的渲染纹理上时，你可以使用 `RenderTexture.active` 来设置目标纹理，使得后续的绘制操作都会渲染到这个指定的纹理上。在渲染过程中，如果没有显式设置渲染目标，通常渲染操作会默认将结果绘制到屏幕上，即当前显示的窗口或屏幕上。

2. 在 Unity 中，使用 `ReadPixels` 函数从渲染目标（如摄像机渲染到的纹理）中读取像素数据时，需要确保目标纹理是当前激活的渲染目标。这是因为 `ReadPixels` 函数会读取当前渲染目标的像素数据，并且它只能读取当前激活的渲染目标上的像素数据。因此，在调用 `ReadPixels` 函数之前，通常需要将目标纹理设置为当前的渲染目标，以确保 `ReadPixels` 函数能够正确地读取到期望的像素数据。$\color{#FF0000}{ReadPixels方法，通常用来截屏哦}$