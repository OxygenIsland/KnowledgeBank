左手坐标系、右手坐标系：
3d 坐标系存在两种完全不同的坐标系，左手坐标系和右手坐标系。如果属于相同的坐标系，可以通过旋转来重合，否则是不可以重合的。两个坐标系之间没有好坏，只是应用与不同的场景。计算机中使用左手坐标系，线性代数中使用右手坐标系。==Unity 是左手坐标系==

1、**世界坐标系**：是一个特殊的坐标系，它建立了描述其他坐标系所需要的参考框架，另一方面说，能用时间坐标系描述其他坐标系的位置，而不能用更大的坐标系来描述世界坐标系。

2、**物体坐标系**：特定物体相关联的坐标系。当物体位移或改变方向时，和该物体相关的坐标系也随之移动和改变方向。比如告诉你“向前走一步”，则是向你的物体坐标系发指令。“前”、“后”、“左”、“右”这样的概念只有物体坐标系才有意义。“向左转”是物体坐标系，“向东”则是世界坐标系。有时物体坐标系也称作**模型坐标系**，模型顶点的坐标都是在模型坐标系中描述的。

3、**摄像机坐标系**：观察者密切相关的坐标系。摄像机坐标系被看作是一种特殊的物体坐标系，该物体坐标系定义摄像机的屏幕可视区域。在摄像机坐标系中，摄像机在原点，x 轴向右，z 轴向前，y 轴向上。一个摄像机坐标系如下图所示。关于摄像机坐标系的轴向约定可能不同。许多图形学书中习惯用右手坐标系，z 轴向外，即从屏幕指向读者。2D 屏幕上显示的内容就是3D 摄像机坐标系通过投影转换呈现的。

![[Pasted image 20240526203346.png|423]]

4、**惯性坐标系**：为了简化世界坐标系到物体坐标系之间的转换，才有了惯性坐标系。惯性坐标系的原点和物体坐标系的原点重合，但惯性坐标系的轴平行于世界坐标系轴。所以从物体坐标系转换为惯性坐标系只需要旋转，从惯性坐标系到世界坐标系只需要平移。
![[Pasted image 20240526203419.png|347]]、
5、**嵌套坐标系**：3D 虚拟世界中每个物体都有自己的坐标系———-自己的原点和坐标轴。每个模型都有自己的原点和坐标轴，模型的子物体就是在这个嵌套坐标系中。


**屏幕坐标系：** 以像素来定义的，以屏幕的左下角为（0，0）点，右上角为（Screen.width，Screen.height），Z 的位置是以相机的世界单位来衡量的。注：鼠标位置坐标属于屏幕坐标，Input.mousePosition 可以获得该位置坐标，手指触摸屏幕也为屏幕坐标，Input.GetTouch(0).position 可以获得单个手指触摸屏幕坐标。

**绘制 GUI 界面的坐标系：** 这个坐标系与屏幕坐标系相似，不同的是该坐标系以屏幕的左上角为（0，0）点，右下角为（Screen.width，Screen.height）。

**视口坐标系：** 视口坐标是标准的相对于相机的。相机的左下角为（0，0）点，右上角为（1，1）点，Z 的位置是以相机的世界单位来衡量的。
一些坐标转换：
- 世界坐标→屏幕坐标：camera.WorldToScreenPoint(transform.position);这样可以将世界坐标转换为屏幕坐标。其中 camera 为场景中的 camera 对象。
- 屏幕坐标→视口坐标：camera.ScreenToViewportPoint(Input.GetTouch(0).position);这样可以将屏幕坐标转换为视口坐标。其中 camera 为场景中的 camera 对象。
- 视口坐标→屏幕坐标：camera.ViewportToScreenPoint();
- 视口坐标→世界坐标：camera.ViewportToWorldPoint();
```csharp
using UnityEngine;
using System.Collections;
public class Position : MonoBehaviour
{
    //场景的相机，拖放进来        
    public Camera camera;
    //场景的物体        
    private GameObject obj;
    void Start()
    {
        //初始化        
        obj = GameObject.Find("Plane");
    }
    void Update()
    {
        if (Input.GetMouseButtonDown(0))
        {
            print("世界坐标" + obj.transform.position);
            print("屏幕坐标" + Input.mousePosition);
            print("Plane 世界坐标→屏幕坐标" + camera.WorldToScreenPoint(obj.transform.position));
            print("鼠标屏幕坐标→视口坐标" + camera.ScreenToViewportPoint(Input.mousePosition));
            print("Plane 世界坐标→视口坐标" + camera.WorldToViewportPoint(obj.transform.position));
        }
    }
}
```