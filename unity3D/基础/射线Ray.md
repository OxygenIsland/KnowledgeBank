---
title: "[[射线Ray]]"
type: Literature
status: done
Creation Date: 2024-04-28 09:48
tags:
---
unity 从 Main Camera 的 near clipping plane 的一个点，（鼠标坐标确定下 x,y）以锥角的方向形成了一条射线，而不是从相机的位置。摄像机提供了两种方法， ScreenPointToRay 和 ViewportPointToRay 。
- ScreenPointToRay 需要提供一个像素位置，取决于屏幕分辨率
- ViewportPointToRay 接受 0.. 1 范围内的归一化坐标 ( 0 代表左下角 1 代表右上角)
```c#
Ray ray = Camera. Main. ScreenPointToRay (Input. MousePosition);
```
Ray 即射线，需要两个属性，原点&方向。
- 原点：游戏屏幕上的鼠标的坐标（x, y），加上近裁剪面的 z 坐标形成的（x, y,z）
- 方向：即正交 Camera 的四棱锥锥角方向，可以理解物体平面与近裁剪面是平行的，形成一个小的四棱锥。
```c#
if (Input.GetMouseButton(1))//判断鼠标右键是否被单击
{
    // 创建一条点击位置为光标位置的射线
    Ray rays = Camera.main.ScreenPointToRay(Input.mousePosition);
    // 只检测12层的obj
    LayerMask layer = 1 << 12;
            
    //将射线以黄色的表示出来
    Debug.DrawRay(rays.origin, rays.direction * 100, Color.yellow);
    //创建一个RayCast变量用于存储返回信息
    RaycastHit hit;
    //将创建的射线投射出去并将反馈信息存储到hit中
    if (Physics.Raycast(rays, out hit, Mathf.Infinity,layer))
    {
        //获取被射线碰到的对象transfrom变量
        currentObject = hit.transform;
    }
    Debug.Log(currentObject.name);
}
```
$\color{#FF0000}{Question:}$  当场景中存在多个相机时，射线检测会出现检测不准的现象，不能检测到鼠标点击的物体，此时应该将 Hierarchy 面板中，从上到下出现的第一个相机的 tag 设置为 Main Camera，就解决了问题，具体原因还不清楚