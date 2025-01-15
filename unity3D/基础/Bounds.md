---
title: "[[Bounds]]"
type: Literature
status: done
Creation Date: 2024-04-03 17:53
tags:
---
## 一、Bounds(包围盒)概述
### 1 . 什么是包围盒?
包围盒算法是一种求解离散点集最优包围空间的方法。
基本思想是用体积稍大且特性简单的几何体（称为包围盒）来近似地代替复杂的几何对象。
最常见的包围盒算法有 AABB 包围盒（Axis-aligned bounding box），包围球（Sphere），方向包围盒 OBB（Oriented bounding box），固定方向凸包 FDH（Fixed directions hulls 或 k-DOP）。
### 2 . 包围盒的类型
#### 2.1 AABB 包围盒 (Axis-aligned bounding box)
AABB 是应用最早的包围盒。它被定义为包含该对象，且边平行于坐标轴的最小六面体。故描述一个 AABB，仅需六个标量。AABB 构造比较简单，存储空间小，但紧密性差，尤其对不规则几何形体，冗余空间很大，当对象旋转时，无法对其进行相应的旋转。处理对象是刚性并且是凸的，不适合包含软体变形的复杂的虚拟环境情况。AABB 也是比较简单的一类包围盒。但对于沿斜对角方向放置的瘦长形对象，其紧密性较差。由于 AABB 相交测试的简单性及较好的紧密性，因此得到了广泛的应用，还可以用于软体对象的碰撞检测。

#### 2.2 包围球 (Sphere)
包围球被定义为包含该对象的最小的球体。确定包围球，首先需分别计算组成对象的基本几何元素集合中所有元素的顶点的 x，y，z 坐标的均值以确定包围球的球心，再由球心与三个最大值坐标所确定的点间的距离确定半径 r。包围球的碰撞检测主要是比较两球间半径和与球心距离的大小。

#### 2.3 OBB 方向包围盒 (Oriented bounding box)
OBB 是较为常用的包围盒类型。它是包含该对象且相对于坐标轴方向任意的最小的长方体。OBB 最大特点是它的方向的任意性，这使得它可以根据被包围对象的形状特点尽可能紧密的包围对象，但同时也使得它的相交测试变得复杂。OBB 包围盒比 AABB 包围盒和包围球更加紧密地逼近物体，能比较显著地减少包围体的个数，从而避免了大量包围体之间的相交检测。但 OBB 之间的相交检测比 AABB 或包围球体之间的相交检测更费时。

#### 2.4 FDH 固定方向凸包 (Fixed directions hulls 或 k-DOP)
FDH（k-DOP）是一种特殊的凸包，继承了 AABB 简单性的特点，但其要具备良好的空间紧密度，必须使用足够多的固定方向。被定义为包含该对象且它的所有面的法向量都取自一个固定的方向（k 个向量）集合的凸包。FDH 比其他包围体更紧密地包围原物体，创建的层次树也就有更少的节点，求交检测时就会减少更多的冗余计算，但相互间的求交运算较为复杂。

#### 2 .5 包围盒选择
任何实时三维交互式程序，如果没有碰撞检测，都是没有价值，甚至无法使用的。游戏中最常用的碰撞检测技术莫过于包围盒（bounding volume）碰撞检测。对于以 60 pfs 运行的游戏来说，处理每一帧数据的时间只有 0.0167 s 左右，对于不同的游戏，碰撞检测大概需要占 10～30%的时间，也就是说，所有碰撞检测必须在 0.002～0.005 s 内完成，非常巨大的挑战。
因此，任何包围盒都应该满足以下特性：
1. 快速的碰撞检测；
2. 能紧密覆盖所包围的对象；
3. 包围盒应该非常容易计算；
4. 能方便的旋转和变换坐标；
5. 低内存占用。
最常见的包围盒有：Sphere，AABB，OBB 等，外加一个比较特殊的 frustum。Sphere 能很好的满足 1，3，4，5 条，但通常包含了太多无用的空间，容易导致错误的碰撞结果。AABB 应该是 sphere 与 obb 之间的解决方案，同时兼顾了效率和空间覆盖范围。OBB 是三者中精度最高的，但检测代价也是最高的。
最终使用哪一种包围盒，是一个非常痛苦的过程，我们需要在效率和精度之间做出权衡取舍。前几天刚好完成了基本的碰撞检测函数，以下是我的一些测试数据，在一定程度上可以作为参考。纯 C #代码实现 ，没有任何 GPU 加速，单线程在 Q 6600上运行。

AABB 包围盒（Axis-aligned bounding box）：100 万次测试，1000 次碰撞，耗时 0.014 s。
包围球（Sphere）：100 万次测试，大约有 16000 次碰撞，耗时 0.016 s。
OBB 方向包围盒（Oriented bounding box)：使用传统的 separate axis 算法，100 万次测试，30 万次碰撞，耗时 0.160 s 左右。对于没有碰撞的情况，几乎在前 6 条轴的检测中，就能结束检测，也就是说大约 50 万次（50%）测试都在检测第七条轴之前结束。
Vertical-agliened OBB：普通 OBB 的特殊版本，只能绕 Y 轴旋转。100 w 次测试，同样 30 万次碰撞，耗时 0.08 s，几乎比普通 OBB 快了一倍。
Frustum-AABB：使用<< Optimized View Frustum Culling Algorithms for Bounding Boxes >>中的算法，100 w 次测试，6 万次碰撞，耗时 0.096 s。目前我计算 n-vertex 和 p-vertex 的方法是瓶颈，大约 0.016 s 的时间花在计算这两个点上。相比 XNA 中的 BoundingFrustum. Intersects，同样的测试需要0.5s 左右。
(以上均为对随机数据的测试，因此不同包围盒之间的实际碰撞次数并没有可比性, 也不代表不同类型间的精度)
显然，AABB 是性价比最高的，OBB 虽然有较高精度，但相对其计算代价来说，并不划算，可以考虑用多个 AABB 来近似 OBB，或者使用代价相对较低的 Vertical-agliened OBB。Sphere 看起来简单，但计算涉及到开方（虽然 Math. Sqrt 会直接编译为 fsqrt 指令)，因此仍然没有 AABB 快（只需要6条逻辑比较指令）
## 二、Unity 中的 Bounds
### 1.Bounds结构体
unity api 对 Bounds 的解释：
>An axis-aligned bounding box, or AABB for short, is a box aligned with coordinate axes and fully enclosing some object. Because the box is never rotated with respect to the axes, it can be defined by just its center and extents, or alternatively by min and max points.

Unity 用 Bounds 这个结构体 struct 来描述 AABB 包围盒，获取一个物体 AABB 包围盒的 API 有三种：Render，Collider，Mesh。
- Render：`GetComponent<Renderer>(). Bounds`  —  世界坐标
- Collider：`GetComponent<Collider>(). Bounds`  —  世界坐标
- Mesh：`GetComponent<MeshFilter>(). Bounds`  —  本地坐标
把 Mesh. Bounds 本地坐标换算成世界坐标 bounds：
```csharp
var centerPoint = transform.TransformPoint(bounds.center);
Bounds newBounds = new Bounds(centerPoint, bounds.size);
```
注意：不管是2D 还是3D 碰撞以及精灵和都是有 `bounds` 属性的。  
总结：幸亏有了这个结构体，在实际开发中适当的使用包围盒会省去很多麻烦，做为结构体他和 `Vector3` 一样是不允许为空的。在一些属性中他是只读的。
#### 1 .1 Public Attribute（公共属性）
Center：边界盒的中心（世界坐标）；
Extents：边界框的范围，总是 size 的一半；
Max：（世界坐标）边界盒的最大点，这个值总是等于 center+extents；
Min：（世界坐标）边界盒的最小点，这个值总是等于 center-extents；
Size：边界盒的总大小。
我们不能直接修改 Bounds 结构体里头的 center 和 size 属性都不能直接设置。
我们通过画线的方式分别看一下各个参数在预制体上的位置。
```csharp
Bounds bounds = this.GetComponent<Collider>().bounds;
Debug.DrawLine(bounds.center, bounds.center + bounds.extents, Color.red);
```
![[Pasted image 20240403181841.png|116]]我们可以看到这个向量的长度是从中心点到右上角的长度。  
由于 `extents` 是 `size` 的一半，所以我们这样画 `size`。
```csharp
//得到左下角的位置
Vector3 p1 = bounds.center - bounds.extents;
Debug.DrawLine(p1, p1 + bounds.size, Color.green);
```
![[Pasted image 20240403181929.png|134]]我们可以看到 `size` 的长度刚好是从左下角到右上角的长度。  
然后我们分别画出最小值和最大值和中心点的连线。
```csharp
Debug.DrawLine(bounds.center,  bounds.min, Color.gray);
Debug.DrawLine(bounds.center, bounds.max, Color.cyan);
```
![[Pasted image 20240403182220.png|155]] 由此可以看出最小值在左下角，最大值在右上角。
#### 1 .2 Public Functions（公共函数）
Encapsulate：重新计算最大最小点；
Contains：可判断点是否包含在边界框内（世界坐标）如我们需判断你是否点击了某个精灵则可以用 Contains ()；
SetMinMax：设置边界盒的最小最大值；
SqrDistance：点和该边界盒之间的最小平方距离；
IntersectRay：射线与改边界盒相交吗？
Intersects：与另一个边界相交吗？比如我们需要判断两个精灵是否有重叠在一起则就可以使用 Intersects ()。
## 三、旋转对 Bounds 的影响
我们对上面的小方块旋转：
![[Pasted image 20240403182422.png|213]]
旋转之后我们发现这个**最小值**和**最大值**不再是小方块的**左下角**和**右上角**。  
换言之**他并不是和自身的坐标轴对齐**。  
于是，我尝试着画出这个小方块的 Bounds：
```csharp
//后左下角
Vector3 backBottomLeft = bounds.min;
///后右下角
Vector3 backBottomRight = backBottomLeft + new Vector3(bounds.size.x, 0, 0);
///前左下角
Vector3 forwardBottomLeft = backBottomLeft + new Vector3(0, 0, bounds.size.z);
///前右下角
Vector3 forwardBottomRight = backBottomLeft + new Vector3(bounds.size.x, 0, bounds.size.z);
///后右上角
Vector3 backTopRight = backBottomLeft + new Vector3(bounds.size.x, bounds.size.y, 0);
///前左上角
Vector3 forwardTopLeft = backBottomLeft + new Vector3(0, bounds.size.y, bounds.size.z);
///后左上角
Vector3 backTopLeft = backBottomLeft + new Vector3(0, bounds.size.y, 0);
///前右上角
Vector3 forwardTopRight = bounds.max;

Debug.DrawLine(bounds.min, backBottomRight, Color.red);
Debug.DrawLine(backBottomRight, forwardBottomRight, Color.red);
Debug.DrawLine(forwardBottomRight, forwardBottomLeft, Color.red);
Debug.DrawLine(forwardBottomLeft, bounds.min, Color.red);

Debug.DrawLine(bounds.min, backTopLeft, Color.red);
Debug.DrawLine(backBottomRight, backTopRight, Color.red);
Debug.DrawLine(forwardBottomRight, bounds.max, Color.red);
Debug.DrawLine(forwardBottomLeft, forwardTopLeft, Color.red);

Debug.DrawLine(backTopRight, backTopLeft, Color.red);
Debug.DrawLine(backTopLeft, forwardTopLeft, Color.red);
Debug.DrawLine(forwardTopLeft, bounds.max, Color.red);
Debug.DrawLine(bounds.max, backTopRight, Color.red);

```
运行结果如下：  
当小方块完全==不做旋转时，本地坐标轴和世界坐标轴重合==
![[Pasted image 20240403182527.png|196]]
==旋转45度之后==，
![[Pasted image 20240403182548.png|210]]
==注：红框是我们画出的小方块的 Bounds，==  
我们发现小方块的**Bounds没有随着小方块旋转，但是它仍然完全包裹着小方块**。  
即是：**它是与世界坐标轴对齐，完全包围的对象是它自身的预制体**。
## 四、Bounds 和碰撞器 Collider 的区别
碰撞器 Collider 的方框始终跟着模型旋转移动，缩放跟着模型的，只要模型不缩放它也不缩放。
属于 obb 包围盒：他是有向的；检测精度较好。
Bounds 跟随模型移动，而不会跟模型着旋转，而是随着模型旋转而缩放变大变小，始终包裹模型。
属于 aabb 包围盒：他是无向的；检测精度较差。
## 五、相关方法
### 1 .多物体 Bounds（Encapsulate）
计算多物体 Bounds，则要遍历所有子物体，然后调用 Encapsulate 方法来计算。
```csharp
Bounds bounds;
Renderer[] renderers = model.GetComponentsInChildren<Renderer>();
for (int i = 0; i < renderers.Length; i++)
{
    bounds.Encapsulate(renderers[i].bounds);
}
```
![[Pasted image 20240403182844.png|500]]
### 2.计算包围盒的八个顶点
```csharp
center = bounds.center;
ext = bounds.extents;
 
float deltaX = Mathf.Abs(ext.x);
float deltaY = Mathf.Abs(ext.y);
float deltaZ = Mathf.Abs(ext.z);
 
#region 获取AABB包围盒顶点
points = new Vector3[8];
points[0] = center + new Vector3(-deltaX, deltaY, -deltaZ);        // 上前左（相对于中心点）
points[1] = center + new Vector3(deltaX, deltaY, -deltaZ);         // 上前右
points[2] = center + new Vector3(deltaX, deltaY, deltaZ);          // 上后右
points[3] = center + new Vector3(-deltaX, deltaY, deltaZ);         // 上后左
 
points[4] = center + new Vector3(-deltaX, -deltaY, -deltaZ);       // 下前左
points[5] = center + new Vector3(deltaX, -deltaY, -deltaZ);        // 下前右
points[6] = center + new Vector3(deltaX, -deltaY, deltaZ);         // 下后右
points[7] = center + new Vector3(-deltaX, -deltaY, deltaZ);        // 下后左
#endregion
```
![[Pasted image 20240403182941.png|389]]
### 3.绘制 bounds 方框
```csharp
/// <summary> 绘制Bounds方框 </summary>
/// <param name="bounds"></param>
/// <param name="color"></param>
/// <param name="offsetSize"></param>
/// <param name="duration"></param>
public static void DrawBoundBoxLine(Bounds bounds, Color color = default(Color), float offsetSize = 1f, float duration = 0.1f)
{
    //先计算出包围盒8个点
    Vector3[] points = new Vector3[8];
    var width_x = bounds.size.x * offsetSize;
    var hight_y = bounds.size.y * offsetSize;
    var length_z = bounds.size.z * offsetSize;

    var LeftBottomPoint = bounds.min;
    var rightUpPoint = bounds.max;
    var centerPoint = bounds.center;
    var topPoint = new Vector3(centerPoint.x, centerPoint.y + hight_y / 2, centerPoint.z);
    var bottomPoint = new Vector3(centerPoint.x, centerPoint.y - hight_y * 0.5f, centerPoint.z);

    points[0] = LeftBottomPoint + Vector3.right * width_x;
    points[1] = LeftBottomPoint + Vector3.up * hight_y;
    points[2] = LeftBottomPoint + Vector3.forward * length_z;

    points[3] = rightUpPoint - Vector3.right * width_x;
    points[4] = rightUpPoint - Vector3.up * hight_y;
    points[5] = rightUpPoint - Vector3.forward * length_z;

    points[6] = LeftBottomPoint;
    points[7] = rightUpPoint;

    Debug.DrawLine(LeftBottomPoint, points[0], color, duration);
    Debug.DrawLine(LeftBottomPoint, points[1], color, duration);
    Debug.DrawLine(LeftBottomPoint, points[2], color, duration);

    Debug.DrawLine(rightUpPoint, points[3], color, duration);
    Debug.DrawLine(rightUpPoint, points[4], color, duration);
    Debug.DrawLine(rightUpPoint, points[5], color, duration);

    Debug.DrawLine(points[1], points[3], color, duration);
    Debug.DrawLine(points[2], points[4], color, duration);
    Debug.DrawLine(points[0], points[5], color, duration);

    Debug.DrawLine(points[2], points[3], color, duration);
    Debug.DrawLine(points[0], points[4], color, duration);
    Debug.DrawLine(points[1], points[5], color, duration);
}
```
### 4.绘制碰撞器方框
#### 4.1方法一
```csharp
/// <summary> 绘制boxCollider的绿色方框 </summary>
/// <param name="color"></param>
void DrawGizmosOnRunTime(Color color)
{
    var boxCollider = GetComponent<BoxCollider>();
    Gizmos.color = color;
    Matrix4x4 rotationMatrix = Matrix4x4.TRS(boxCollider.transform.position, boxCollider.transform.rotation, boxCollider.transform.lossyScale);
    Gizmos.matrix = rotationMatrix;
    Gizmos.DrawWireCube(boxCollider.center, boxCollider.size);
}
void OnDrawGizmos()
{
    DrawGizmosOnRunTime(Color.red);
}
```
#### 4.2方法二
```csharp
/// <summary> 绘制boxCollider的绿色方框 </summary>
/// <param name="boxCollider"></param>
/// <param name="color"></param>
/// <param name="offsetSize"></param>
public static void DrawOnGameViewRuntime(BoxCollider boxCollider, Color color = default(Color), float offsetSize = 1f)
{  
    float width = 0.1f;
    Vector3 rightDir = boxCollider.transform.right.normalized;
    Vector3 forwardDir = boxCollider.transform.forward.normalized;
    Vector3 upDir = boxCollider.transform.up.normalized;
    Vector3 center = boxCollider.transform.position + boxCollider.center;
    Vector3 size = boxCollider.size * offsetSize;
    size.x *= boxCollider.transform.lossyScale.x;
    size.y *= boxCollider.transform.lossyScale.y;
    size.z *= boxCollider.transform.lossyScale.z;

    Debug.DrawLine(center + upDir * size.y / 2f + rightDir * size.x / 2f + forwardDir * size.z / 2f, center + upDir * size.y / 2f - rightDir * size.x / 2f + forwardDir * size.z / 2f, color);
    Debug.DrawLine(center - upDir * size.y / 2f + rightDir * size.x / 2f + forwardDir * size.z / 2f, center - upDir * size.y / 2f - rightDir * size.x / 2f + forwardDir * size.z / 2f, color);
    Debug.DrawLine(center + upDir * size.y / 2f + rightDir * size.x / 2f + forwardDir * size.z / 2f, center - upDir * size.y / 2f + rightDir * size.x / 2f + forwardDir * size.z / 2f, color);
    Debug.DrawLine(center + upDir * size.y / 2f - rightDir * size.x / 2f + forwardDir * size.z / 2f, center - upDir * size.y / 2f - rightDir * size.x / 2f + forwardDir * size.z / 2f, color);
    Debug.DrawLine(center + upDir * size.y / 2f + rightDir * size.x / 2f - forwardDir * size.z / 2f, center + upDir * size.y / 2f - rightDir * size.x / 2f - forwardDir * size.z / 2f, color);
    Debug.DrawLine(center - upDir * size.y / 2f + rightDir * size.x / 2f - forwardDir * size.z / 2f, center - upDir * size.y / 2f - rightDir * size.x / 2f - forwardDir * size.z / 2f, color);
    Debug.DrawLine(center + upDir * size.y / 2f + rightDir * size.x / 2f - forwardDir * size.z / 2f, center - upDir * size.y / 2f + rightDir * size.x / 2f - forwardDir * size.z / 2f, color);
    Debug.DrawLine(center + upDir * size.y / 2f - rightDir * size.x / 2f - forwardDir * size.z / 2f, center - upDir * size.y / 2f - rightDir * size.x / 2f - forwardDir * size.z / 2f, color);
    Debug.DrawLine(center + upDir * size.y / 2f + rightDir * size.x / 2f + forwardDir * size.z / 2f, center + upDir * size.y / 2f + rightDir * size.x / 2f - forwardDir * size.z / 2f, color);
    Debug.DrawLine(center - upDir * size.y / 2f + rightDir * size.x / 2f + forwardDir * size.z / 2f, center - upDir * size.y / 2f + rightDir * size.x / 2f - forwardDir * size.z / 2f, color);
    Debug.DrawLine(center + upDir * size.y / 2f - rightDir * size.x / 2f + forwardDir * size.z / 2f, center + upDir * size.y / 2f - rightDir * size.x / 2f - forwardDir * size.z / 2f, color);
    Debug.DrawLine(center - upDir * size.y / 2f - rightDir * size.x / 2f + forwardDir * size.z / 2f, center - upDir * size.y / 2f - rightDir * size.x / 2f - forwardDir * size.z / 2f, color);
}
```
### 5.求两个包围盒之间的距离
```csharp
// Distance between two ClosestPointOnBounds
// this is needed in cases where entites are really big. in those cases,
// we can't just move to entity.transform.position, because it will be
// unreachable. instead we have to go the closest point on the boundary.
//
// Vector3.Distance(a.transform.position, b.transform.position):
//    _____        _____
//   |     |      |     |
//   |  x==|======|==x  |
//   |_____|      |_____|
//
//
// Utils.ClosestDistance(a.collider, b.collider):
//    _____        _____
//   |     |      |     |
//   |     |x====x|     |
//   |_____|      |_____|
//
public static float ClosestDistance(Collider a, Collider b)
{
    return Vector3.Distance(a.ClosestPointOnBounds(b.transform.position),
                            b.ClosestPointOnBounds(a.transform.position));
}
```
### 6.计算所有包围盒的中心点
计算出多个 Bounds 的中心点。
```csharp
[MenuItem ("MyMenu/Do Test")]
static void Test () 
{
	Transform parent = Selection.activeGameObject.transform;
	Vector3 postion = parent.position;
	Quaternion rotation = parent.rotation;
	Vector3 scale = parent.localScale;
	parent.position = Vector3.zero;
	parent.rotation = Quaternion.Euler(Vector3.zero);
	parent.localScale = Vector3.one;

	Vector3 center = Vector3.zero;
	Renderer[] renders = parent.GetComponentsInChildren<Renderer>();
	foreach (Renderer child in renders)
	{
		center += child.bounds.center;   
	}
	center /= parent.GetComponentsInChildren<Transform>().Length; 
	Bounds bounds = new Bounds(center,Vector3.zero);
	foreach (Renderer child in renders)
	{
		bounds.Encapsulate(child.bounds);   
	}

	parent.position = postion;
	parent.rotation = rotation;
	parent.localScale = scale;

	foreach(Transform t in parent)
	{
		t.position = t.position -  bounds.center;
	}
	parent.transform.position = bounds.center + parent.position;
}

```