---
title: "[[unity中的坐标系]]"
type: Literature
status: done
Creation Date: 2024-05-27 09:43
tags:
---
##   世界坐标系
世界坐标系是一个特殊的坐标系，它建立了描述其他坐标系所需要的参考框架，另一方面说，能用时间坐标系描述其他坐标系的位置，而不能用更大的坐标系来描述世界坐标系。该坐标系分为左手坐标系和右手坐标系，其中如图所示。两个坐标系之间没有好坏，只是应用与不同的场景。计算机中使用左手坐标系，线性代数中使用右手坐标系。==Unity 是左手坐标系==
![[Pasted image 20240530175935.png|500]]
Unity中一个物体的坐标信息，通过Transform.position来存储，它是一个[Vector3](https://so.csdn.net/so/search?q=Vector3&spm=1001.2101.3001.7020)变量，是一个三维向量，存储了XYZ的信息。
![[Pasted image 20240530180008.png|362]]
在 Unity 中，可通过 Transform.forward 来表示正方向，Vector3.forward 也可以表示正方向，这两者的区别在于：**Vector3.forward 的值永远是(0,0,1)，而 transform.forward 的值则是根据当前物体的自身坐标系 Z 轴，不一定等于(0,0,1)**
## 局部坐标系
特定物体相关联的坐标系。当物体位移或改变方向时，和该物体相关的坐标系也随之移动和改变方向。比如告诉你“向前走一步”，则是向你的物体坐标系发指令。“前”、“后”、“左”、“右”这样的概念只有物体坐标系才有意义。“向左转”是物体坐标系，“向东”则是世界坐标系。有时物体坐标系也称作**模型坐标系**，模型顶点的坐标都是在模型坐标系中描述的。
## 摄像机坐标系
观察者密切相关的坐标系。摄像机坐标系被看作是一种特殊的物体坐标系，该物体坐标系定义摄像机的屏幕可视区域。在摄像机坐标系中，摄像机在原点，x 轴向右，z 轴向前，y 轴向上。一个摄像机坐标系如下图所示。关于摄像机坐标系的轴向约定可能不同。许多图形学书中习惯用右手坐标系，z 轴向外，即从屏幕指向读者。2 D 屏幕上显示的内容就是 3 D 摄像机坐标系通过投影转换呈现的。

![[Pasted image 20240526203346.png|423]]

## 屏幕坐标系
以像素来定义的，以屏幕的左下角为（0，0）点，右上角为（Screen.width，Screen.height），Z 的位置是以相机的世界单位来衡量的。
注：鼠标位置坐标属于屏幕坐标，Input.mousePosition 可以获得该位置坐标，手指触摸屏幕也为屏幕坐标，Input.GetTouch(0).position 可以获得单个手指触摸屏幕坐标。
现在我运行下面这行代码就是得出我当前游戏视窗的屏幕分辨率。
```csharp
    void Start()
    {
        Debug.Log("当前窗口的分辨率为：" + Screen.width + "X" + Screen.height);
        Debug.Log("当前屏幕的分辨率为：" + Screen.currentResolution);
    }
```
![[Pasted image 20240530180200.png|500]]
鼠标位置坐标就是属于屏幕坐标系，通过屏幕坐标和世界坐标互转，可得到鼠标在 Unity3D 中的实际交互位置，然后就可以通过逻辑做出反馈。
## 视口坐标系
视口坐标是标准的相对于相机的。相机的左下角为（0，0）点，右上角为（1，1）点，Z 的位置是以相机的世界单位来衡量的。
该坐标系计算方式和屏幕坐标系类似，只不过把其参数标准化了，更加适用于比例计算。
![[Pasted image 20240530180314.png|500]]
这里不管是视口坐标还是屏幕坐标，其z值还是有的，是表示深度的。
## GUI 坐标系
这个坐标系与屏幕坐标系相似，不同的是该坐标系以屏幕的左上角为（0，0）点，右下角为（Screen.width，Screen.height）。

## 坐标系的相互转换
### 1.世界坐标和屏幕坐标的相互转换
Unity 中采用多种坐标系就是为了在不同的情况下使用不同的坐标更加方面。既然采用了多种坐标那么就必定会提供相关的转换方法，下面就简要总结一下上述坐标的相互转换。  
其实这些坐标系看起来眼花缭乱，很多的样子，实际深究起来也就一个世界转屏幕（或屏幕转世界）值得探讨，其他的都很容易实现。

屏幕坐标转世界坐标  
```csharp
Camera.ScreenToWorldPoint(Vector3 Pos);
//其中 camera 为场景中的 camera 对象。
```
世界坐标转屏幕坐标
```csharp
//其中 camera 为场景中的 camera 对象。
Camera.WorldToScreenPoint(Vector3 Pos);
```
这些转换一般应用于想要通过鼠标来操作世界物体，比如物体跟随鼠标移动…
**案例演示--物体跟随鼠标移动，xyz 都移动**
![[a4dd10b29f4441a78b8bfeba1fb2df40.gif|500]]
可能你看这段代码的时候不理解，比如感觉明明直接用下面这句话，就可以啦，为什么要大费周章呢？看到这里你应该去试一下再往下看
```csharp
Camera.main.WorldToScreenPoint(Input.mousePosition);
```
若直接使用上面那句话，那么世界坐标会缺少 Z 值，所以转换之后的坐标一定是错误的  
所以我们要通过巧妙的方式弥补这个 Bug，代码如下。
```csharp
    void Update()
    {
        // 首先将要操纵的物体的世界坐标转为屏幕坐标
        Vector3 screenPos = Camera.main.WorldToScreenPoint(transform.position);
        // 然后获取鼠标的屏幕坐标
        Vector3 mousePos = Input.mousePosition;
        // 然后将已经转换好的物体的屏幕坐标的Z值赋给缺失z值的鼠标屏幕坐标
        mousePos.z = screenPos.z;
        // 然后将已经完整的鼠标屏幕坐标转成世界坐标
        Vector3 worldPos = Camera.main.ScreenToWorldPoint(mousePos);
        // 最后每帧修改物体世界坐标位置
        transform.position = worldPos;
    }

```
### 2.世界坐标和视口坐标的相互转换
世界坐标转视口坐标
```csharp
//其中 camera 为场景中的 camera 对象。
Camera.WorldToViewportPoint(Vector3 Pos)
```
视口坐标转世界坐标
```csharp
//其中 camera 为场景中的 camera 对象。
Camera.ViewportToWorldPoint(Vector3 Pos);
```
这个原理和上一个差不多，因为屏幕和视口是可以相互转换的，所以把上面的转换函数换成下面的也是成立的，前提是最后用视口转世界坐标时，要把鼠标位置屏幕坐标先转成视口再使用，听不懂的话，我简单改一下，把代码贴出来，动态示意图就不放了，因为是一样的效果。
```csharp
        // 首先将要操纵的物体的世界坐标转为视口做坐标
        Vector3 screenPos = Camera.main.WorldToViewportPoint(transform.position);
        // 然后获取鼠标的屏幕坐标
        Vector3 mousePos = Input.mousePosition;
        // 然后将已经转换好的物体的屏幕坐标的Z值赋给缺失z值的鼠标屏幕坐标
        mousePos.z = screenPos.z;
        // 将屏幕坐标转为视口坐标
        mousePos = Camera.main.ScreenToViewportPoint(mousePos);
        // 然后将已经完整的视口坐标转成世界坐标
        Vector3 worldPos = Camera.main.ViewportToWorldPoint(mousePos);
        // 最后每帧修改物体世界坐标位置
        transform.position = worldPos;
```
### 3.屏幕坐标和视口坐标的相互转换
屏幕坐标转视口坐标
```csharp
//其中 camera 为场景中的 camera 对象。
Camera.ScreenToViewportPoint(Vector3 Pos);
```
视口坐标转屏幕坐标
```csharp
//其中 camera 为场景中的 camera 对象。
Camera.ViewportToScreenPoint(Vector3 Pos);
```
### 4.世界坐标和局部坐标的相互转换
世界坐标转局部坐标
```csharp
transform.InverseTransformPoint(Vector3 Pos);
transform.worldToLocalMatrix
```
局部坐标转世界坐标
```csharp
transform.TransformPoint(Vector3 Pos);
transform.localToworldMatrix
```
## 坐标系混淆
大家在使用坐标系的时候，可能听过很多很多别称，对于新手来说，很容易对一些较为生僻的叫法产生疑惑，这里给大家梳理一下。

- 世界坐标、全局坐标、左手坐标、绝对坐标
- 局部坐标、自身坐标、物体坐标、本地坐标、相对坐标
- 屏幕坐标、像素坐标
- 视口坐标、视窗坐标
- GUI 坐标、UI 坐标

