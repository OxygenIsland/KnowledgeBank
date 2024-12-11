## 1 、RectTransform —— UI 元素必备组件
### 1 .1 Transform —— 3D
>前言：在了解 RectTransform 组件前，我们有必要先来了解下 Transform 组件

在 Unity 中，Transform 是 3 D 物体必备的基本组件，该组件记录并表示了，一个 3D 物体在三维空间中的位置、旋转和缩放三种属性
- 调整位置，只需修改 Position，即可改变对象出现的位置
- 调整旋转，只需修改 Rotation，即可改变对象朝向
- 调整缩放，只需修改 Scale，即可改变对象大小

### 1 .2 RectTransform —— 2D 矩形
然而，UI 元素所在的是一个二维平面上，直接对应的是我们的显示器 /手机显示屏。我们的显示器、手机屏幕有着不同的大小、不同的品牌，不同的分辨率，不同的屏幕比例等等…
那么就出现了一个相当复杂的问题，这么多不不同同的不同，我们开发者该咋办？我们怎么保证，一个按钮的位置，显示在不同手机屏幕的左下角？直接给 UI 元素，设置一个固定的二维坐标，那么在 720\*480 的屏幕上是一个位置。在 1920\*1080 屏幕上，又是另一个位置了，肯定不是左下角，还差的很远
![[Pasted image 20240522190407.png|475]]
于是， Unity 为了解决掉这个让人头疼的问题，就有了 RectTransform 组件
> **配合 `Canvas` 画布组件，从而达到**  
> **专门治理解决， UI 在不同屏幕上的各种疑难杂症**

**该组件记录并表示了，一个 `2D UI元素` 在屏幕中的 `位置` 、 `旋转` 和 `缩放` 三种属性**

==RectTransform 继承自 Transform，对比 Transform，它增加了2个新的属性，分别是：Anchor（锚点） 和 Pivot（轴心点） ==

### 1 .3 Difference —— 区别
- Transform：记录并表示，一个 3D 物体在三维空间中的位置、旋转和缩放三种属性
- RectTransform：记录并表示，一个 2 D UI 元素在屏幕中的位置、旋转和缩放三种属性
- Rect：表示 2D 矩形，常用来处理表示 2 维矩形，设置 x、y 位置和宽度、高度。( 你可以理解为用来描述一个矩阵的长宽 )
## 2 、Anchor —— 锚点
**什么是锚点?**
**`Anchors` （锚点）其实说白了就是：4个点。**
![[Pasted image 20240522191142.png|315]]
**在 RectTransform 组件上，`锚点 Anchors` 有 2个值 `Min 和 Max`**
> **`Min 和 Max` 的值是经过 `归一化` 的，也就是 `X 或 Y 的值在0-1` 之间**

由平面中的 2个坐标点，就可以确定4个点的位置，而这两个点，就是 Min(x,y) 和 Max(x,y)
![[Pasted image 20240522191359.png|425]] ![[20190415235634115.gif|675]]
==**锚点可以重合在一起**==
![[Pasted image 20240522191601.png|203]]
>**这种情况下，`无论父物体如何改变大小，子物体的大小永远不变`**  
> **`为什么？？？`**  
> **先不急，我们需要先去认识一下另外一个属性，`轴心点`**

## 3、Pivot —— 轴心点
> **UI 元素的轴心点，它依旧是一个二维坐标点**

**一般创建一个 UI 元素，默认轴心 `Pivot (0.5,0.5)` 在 UI 元素的 `正中心`，轴心点的 `原点(0,0)`，在当前 UI 元素的左下角**
![[Pasted image 20240522191754.png|475]]
==UI 元素的旋转和缩放是围绕 Pivot 进行的==
**轴心点的坐标不同，会造成 UI 的 `缩放` / `旋转` 效果不同，以及与父物体形成的 UI 适应问题**
![[20190415235634115 1.gif|500]]
## 4、AnchorPresets —— 快速锚点预设(设置)面板
**该面板上的功能按钮一共分 三类**
> 1. **九宫定位按钮 [九个]**
> 2. **缩放(弹性)定位按钮 [七个]**
> 3. **辅助操作按钮 [八个]**
![[Pasted image 20240522192100.png|500]]
![[Pasted image 20240522192311.png|500]]

## 5 、Other Rect attributes —— 其他 Rect 属性
通过锚点预设面板修改 UI 元素的 RectTransform 过程中，你会发现不同的设置，会出现不同的属性。并且左右属性不会同时出现。有 Pos X 没 Left 类似于这样
>Pos X —— Left
>Pos Y —— Top
>Width —— Right
>Height —— Bottom

![[20190415235634115 2.gif|500]]
### 5.1 Posx、Pos Y —— 锚点到轴心
|  **属性名**   | **意义**                          |
| :--------: | :------------------------------ |
| **Pos X**  | **`Anchors` X 到 `Pivot` Y 的距离** |
| **Pos Y**  | **`Anchors` Y 到 `Pivot` Y 的距离** |
| **Width**  | **`UI 元素宽度`**                   |
| **Height** | **`UI 元素高度`**                   |
![[Pasted image 20240522192752.png|500]]
==**重点：解释下 Pos X 、Pos Y 与 Width、Height 的出现时机，与原理**==

1. 当 Min X 与 Max X 值相等时，两个 X 锚点重合 —— 两个 X 锚点到轴心 Pivot 的距离相等。如上图： Pos X 值为 358，就表示 Min X 与 Max X 到 Pivot 的距离两者都是 358
2. 此时改变 UI 元素的宽度 Width，以及改变轴心 Pivot X，Pos X 值也会实时被计算出来，但 Min X 与 Max X 到 Pivot 的距离值还是一样的
结论：当锚点 Min X 与 Max X 值相等时，Pos X 一个属性值，就能表示两个 X 锚点与轴心的距离

![[Pasted image 20240522193125.png|500]]
此时代表 X 方向的尺寸会受到 Parent 的尺寸影响，在 X 方向 Image 实际的 Width 是由 Left 和 Right 来控制。Image 的 Higth 则是固定的
![[20190331162805552.gif|500]]

![[Pasted image 20240523095134.png|550]] ![[20190331162805552 1.gif|550]]

![[Pasted image 20240523095319.png|475]] 
此时代表 X，Y 方向的尺寸都会受到 Parent 的尺寸影响。
![[20190331162805552 2.gif|500]]
代码设置锚点
```csharp
RectTransform
1.top
GetComponent<RectTransform>().offsetMax = new Vector2(GetComponent<RectTransform>().offsetMax.x, top);
2.bottom
GetComponent<RectTransform>().offsetMin = new Vector2(GetComponent<RectTransform>().offsetMin.x, bottom);
3.width，height
GetComponent<RectTransform>().sizeDelta = new Vector2(width, height);
4.pos
GetComponent<RectTransform>().anchoredPosition3D = new Vector3(posx,posy,posz);
GetComponent<RectTransform>().anchoredPosition = new Vector2(posx,posy);
```
### 5.2 Position —— PosX、PosY 与 Left、Top、Right、Bottom 数值显示与 anchoredPosition
在 UGUI 中 Pos X 与 Pos Y 分别表示 UI**轴心点**到**锚点**的水平与方向距离。==Position 值的显示只和 UI 自身**锚点**及**轴心点**的位置有关系。==  
#### anchoredPosition 与 position 的区别：
##### 区别和联系
对于 UGUI 元素来说，RectTransform.anchoredPosition (Vector2) 是相对于anchor来设置的位置。RectTransform.position （Vector3) 是三维坐标（in world space），是相对于世界原点的。
##### 举例说明
已知 e.Position 是触摸或点击事件提供的屏幕坐标（Vector2)，Canvas 设置为 Screen Space - Overlay。如果屏幕是 [iPhone7](https://www.baidu.com/s?wd=iPhone7&tn=24004469_oem_dg&rsv_dl=gh_pl_sl_csd) 的大小 667x375，那么点在[最右](https://www.baidu.com/s?wd=%E6%9C%80%E5%8F%B3&tn=24004469_oem_dg&rsv_dl=gh_pl_sl_csd)下角的时候，e.Position 的值就是(667, 375)。如果把按钮的 RectTransform.position 赋值为 e.Position，就能把这个按钮放在屏幕右下角 (667, 375)位置。如果把按钮的 RectTransform.anchoredPosition 赋值为 e.Position，那么按钮会在哪里取决于 anchor 的位置（参见下图）：

![|500](https://i-blog.csdnimg.cn/blog_migrate/888acdc7681f4d4c07cd474bd2980e36.png)

1. 如果 anchor 在左上角(0, 0)，那么相对 anchor 设置坐标为 (0, 0) + (667, 375) = (667, 375)
2. 如果anchor在右下角(667, 375)，那么相对 anchor 设置坐标为 (667, 375) + (667, 375) = (1334, 750)，设置到屏幕外了。
3. 其他情况类推。

问题：RectTransform.position 是世界坐标下的 Vector3， e.Position 是屏幕坐标下的 Vector2，为什么从 Vector2 隐式类型转换为 Vector3 后坐标正好是对的？

可能的解释：隐式类型转换时，z = 0。因为 Canvas 是使用 Screen Space - Overlay 模式，元素是绘制在场景之上的，也就是最顶层，z 的数值应该是失效的，只要 x, y 坐标值是对的，元素就会显示在正确的位置。如果有覆盖的问题，可能要设置渲染次序而不是 z 值了。

##### 总结
==position 的原点是 Canvas 屏幕空间的原点, anchoredPosition 的原点是元素本身的 anchor。==
#### **UI 的锚点和轴心点都在正中间**  
这种情况下，锚点和轴心点重合 Pos X 和 Pos Y 显示的数值为0
![[Pasted image 20240523100043.png|500]]
#### **UI 的锚点或轴心点不在中心(.AnchorMin 和 AnchorMax 重合)**  
这个时候，在 Pos X 和 Pos Y 显示的数值实际是 anchoredPosition,这种情况 UI 的 LocalPosition 和 anchoredPosition 并不相等
![[Pasted image 20240523100432.png|500]]
#### **AnchorMin 和 AnchorMax 不重合**
Pos X 和 Pos Y 消失取而代之的的是 Left，Top，Right,Bottom,分别代表这个**UI 矩形边框距离其四个锚点组成的边框的向量距离**，此时与轴心点没有关系
![[20190331162805552 3.gif|500]]
此时 anchoredPosition 的值等于轴心点坐标-锚框坐标

## 6、RectTransformAPI 属性解析
### AnchoredPosition —— UI 坐标
对于 UGUI 元素来说，RectTransform. AnchoredPosition (Vector 2) 是相对锚点来设置的位置。换句话就是轴心点与锚点的向量，即 UI 坐标。它根据 AnchorMin 和 AnchorMax 是否重合要分别计算。
1. 重合，anchoredPosition 就是表示锚点到 Pivot 的位置也就是 Inspector 面板 PosX、PosY 的值
2. 不重合，轴心点坐标-锚框坐标
AnchoredPosition 的作用就是修改 UI 对象的二维坐标位置
![[Pasted image 20240523101138.png|475]]

### anchoredPosition3D —— UI坐标系的3D坐标
anchoredPosition 3D 与 anchoredPosition 表示同一位置的坐标，区别在于前者是三维向量，后者是二维向量
### anchorMax、anchorMin —— 锚点矩形
Anchors 的 Min 和 Max 分别是归一化的位置值(从0到1)，表示占父 RectTransform 的百分比
![[Pasted image 20240523101402.png|500]]
### offsetMax、offsetMin —— 偏移量
offsetMax 为当前矩形右上角相对于锚点右上角的偏移。
offsetMin 为当前矩形左下角相对于锚点左下角的偏移。
![[Pasted image 20240523101430.png|484]]
这个值在使用代码控制 RectTransform 时很有用，比如在制作 UI 时，其中有个 RectTransform 采用的是“绝对定位”，运行时需要用代码来将其设置为全拉伸，那么对该 RectTransform 执行如下操作就可以实现：
```csharp
	rectTransform.anchorMin = Vector2.zero;
	rectTransform.anchorMax = Vector2.one;
	rectTransform.offsetMin = Vector2.zero;
	rectTransform.offsetMax = Vector2.zero;
```
### Rect —— 矩形类
如果想要获取一个 RectTransform 的矩形信息，应该使用 rectTransform. Rect 属性。Rect 属性同样是一个计算出来的值，但是它表示的是该 rectTransform 对应的矩形的相关信息。其中前两个参数分别代表矩形左下角相对于锚点的 x 和 y 坐标，后两个参数分别代表举行的宽度和高度。

### SizeDelta —— UI 坐标
SizeDelta 是 offsetMax-offsetMin 的结果。在锚点全部重合的情况下，它的值就是面板上的（Width，Height）。在锚点完全不重合的情况下，它是相对于父矩形的尺寸。
一个常见的错误是，当 RectTransform 的锚点并非全部重合时，使用 sizeDelta 作为这个 RectTransform 的尺寸。此时拿到的结果一般来说并非预期的结果。
![[Pasted image 20240523101631.png|500]]
### sizeDelta —— 动态改变 RectTransform
在代码中动态改变 RectTransform 大小的方法如下所示：
 
1：直接对 sizeDelta 属性进行赋值，其中 X 和 Y 可以对应理解成 width 和 height。SizeDelta 的具体含义：若 achors 是一个点的话则代表宽高，否则为到锚点的距离
```csharp
var rt = gameObject. GetComponent<RectTransform>();
Rt. SizeDelta = new Vector 2 (100, 30);
```
 2：使用 SetSizeWithCurrentAnchors 函数来进行设定，其中 Horizontal 和 Vertical 分别对应宽和高。此函数受当前锚点和中心点的影响。
```csharp
var rt = gameObject. GetComponent<RectTransform>();
Rt.SetSizeWithCurrentAnchors (RectTransform. Axis. Horizontal, 100);
Rt.SetSizeWithCurrentAnchors (RectTransform. Axis. Vertical, 30);
```
3：使用 SetInsetAndSizeFromParentEdge 函数来进行设定。此函数不受锚点和中心的影响，其中第一个参数代表对齐方式，第二个参数为距离边界的距离，第三个参数为宽度。
```csharp
 var rt = gameObject. GetComponent<RectTransform>();
Rt.SetInsetAndSizeFromParentEdge (RectTransform. Edge. Right, 0, 100);
Rt.SetInsetAndSizeFromParentEdge (RectTransform. Edge. Bottom, 0, 30);
```


