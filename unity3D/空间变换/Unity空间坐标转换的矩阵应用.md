---
title: "[[Unity空间坐标转换的矩阵应用]]"
type: Literature
status: done
Creation Date: 2024-05-27 09:43
tags:
---
>本文主要介绍通过矩阵的方式实现对象的空间变换，主要涉及的变换形式为世界空间转相对空间中的矩阵实现过程
实际开发中，`Unity` 已经为开发者封装好一些坐标转换的方法，使用起来是比较方便的，但是对于理解而言就比较复杂了，所以下面的介绍会基于模拟的方式来了解 `Unity` 的矩阵坐标变换过程

### 一、通过向量进行空间变换
创建两个空物体分别命名为`centerPos`与`targetPos`
接下来所执行的操作，可以理解为求 `targetPos` 相对于 `centerPos` 的本地坐标系下的坐标，即此时 `centerPos` 为坐标原点，来求出 `targetPos` 在该坐标系下的坐标位置
为了便于观察，通过 Gizmos 绘制出 `centerPos` 的本地坐标系，同时标识出两者的位置关系，如图所示：
![[Pasted image 20240526140431.png]]
为了便于后续矩阵的理解，先通过常规的方式来计算得到 `targetPos` 相对于 `centerPos` 的本地坐标位置，实现过程很简单，分为两步来描述： 
- 得到从`centerPos`指向`targetPos`的向量
- 计算该向量在`centerPos`坐标系下各个轴的投影

得到一个向量可以通过终止坐标点减去起始坐标点获取，而投影就更简单了，只需要与`centerPos`本地坐标系的各个轴的向量做一个点积即可,经过计算就可以得到转换坐标系后的坐标位置，代码为：

```csharp
    public Vector3 GetTargetRelatPos(Transform targetPos , Transform centerPos)
    {
        Vector3 result=new Vector3(0,0,0);
        Vector3 v3 = targetPos.position - centerPos.position;
        result.x = Vector3.Dot(v3 , centerPos.right);
        result.y = Vector3.Dot(v3 , centerPos.up);
        result.z = Vector3.Dot(v3 , centerPos.forward);
        return result;
    }
```

直接通过代码解释比较抽象，而这部分恰巧又与后面坐标转换矩阵的内容相关，所以这里来将其可视化一下：
![[Pasted image 20240526183254.png|500]]
图中各个对象的信息为：
- 绿色小球：中心点`centerPos`与目标点`targetPos`
- 红、绿、蓝三条辅助线：`centerPos`的本地坐标系的三个轴
- 黄色辅助线：从`centerPos`指向`targetPos`的向量
- 白色辅助线：代表向量投影坐标轴的垂线
- 白色小球：代表向量在各个轴上的投影点

绘制的代码为，可以在项目中实际操作一下，转换角度来理解：
```csharp
    public void OnDrawGizmos()
    {
        //绿色小球绘制
        Gizmos.color = Color.green;
        Gizmos.DrawSphere(centerPos.position, 0.1f);
        Gizmos.DrawSphere(targetPos.position, 0.1f);
        //坐标辅助线绘制
        Gizmos.color=Color.red;
        Gizmos.DrawLine(centerPos.position, centerPos.position+centerPos.right*10);  
        Gizmos.color=Color.green;
        Gizmos.DrawLine(centerPos.position, centerPos.position+centerPos.up*10);  
        Gizmos.color=Color.blue;
        Gizmos.DrawLine(centerPos.position, centerPos.position+centerPos.forward*10);
        //向量绘制
        Gizmos.color = Color.yellow;
        Gizmos.DrawLine(centerPos.position, targetPos.position);
​
        Vector3 v3 = GetTargetRelatPos(targetPos,centerPos);
        //垂线绘制
        Gizmos.color = Color.white;
        Gizmos.DrawLine(targetPos.position, centerPos.position+ v3.x * centerPos.right); 
        Gizmos.DrawLine(targetPos.position, centerPos.position+ v3.y * centerPos.up);
        Gizmos.DrawLine(targetPos.position, centerPos.position+ v3.z * centerPos.forward);
        //小球绘制
        Gizmos.DrawSphere(centerPos.position + v3.x * centerPos.right, 0.1f);
        Gizmos.DrawSphere(centerPos.position + v3.y * centerPos.up, 0.1f);
        Gizmos.DrawSphere(centerPos.position + v3.z * centerPos.forward, 0.1f);
    }
```

通过对上面的代码的解析，可以看出影响物体坐标转换的关键因素在于参考点 `centerPos` 的坐标位置与其旋转关系，这里通过一个动图来简单的解释一下：![[c438da68-6dc8-11ec-9b9f-02506b937437.mp4]]
通过图中演示坐标系初始位置、旋转、缩放三个维度变化对于最终结果的影响可以看出，坐标系初始位置的变化会引起向量的模的变化，而旋转则会改变向量在各个坐标轴的分量，即局部空间下的向量方向的改变，那么我们很容易就总结出：
- 影响物体局部坐标的关键因素在于初始点的位置与其方向，这里的方向可以拆分为三个坐标轴 `right`、`up`、`forward`，而缩放则不会引起坐标转换过程中位置的变化
### 二、使用空间变换矩阵
同样对于上面的一个案例，通过矩阵的方式来计算得到 `targetPos` 相对于 `centerPos` 坐标系的局部坐标，==为了便于理解，我们先排除缩放的影响，默认 `centerPos` 的缩放为（1，1，1）==，则可以通过下面几种方式完成计算：
```csharp
    //第一种：
    public Vector3 GetTargetRelatPosFirst(Transform targetPos, Transform centerPos)
    {      
        return centerPos.InverseTransformPoint(targetPos.position);
    }
    //第二种：
    public Vector3 GetTargetRelatPosSencond(Transform targetPos, Transform centerPos)
    {       
        Matrix4x4 m4 = centerPos.worldToLocalMatrix;
        return m4.MultiplyPoint3x4(targetPos.position);
    }
    //第三种：
    public Vector3 GetTargetRelatPosThird(Transform targetPos, Transform centerPos)
    {
        Vector4 v4 = new Vector4(targetPos.position.x, targetPos.position.y, targetPos.position.z, 1);
        return centerPos.worldToLocalMatrix * v4;
    }
    
```

几种方式的实现过程大致相同，都是基于矩阵乘法的坐标转换，不过第一种与第二种是`Unity`官方对矩阵与三维向量乘法的一个进一步封装，而第三种的实现过程相对完整，这里就根据第二种的计算方法来理解，大概可以分为下面几个环节：

### 1、齐次坐标转换：
通过第三种解决方案的代码可以看到，会将`targetPos`的`Position`从`Vector3`变换为`Vector4`，并对最后的一维补充为1。通过高中数学知识可以了解到，向量可以转换成为矩阵，而对于矩阵的乘法而言，第一个矩阵的列数必须与第二个矩阵的行数相同，所以这里为了可以进行计算，需要将三维向量转换为四维

但是最后一个1并不是单纯的补位，在矩阵的乘法中也有着重要的计算意义，比如说，如果我们不手动将`Vector3`变换为`Vector4`，`Unity`也会默认帮我们处理变换，但是最后补充的就是数字0，然后你就会惊奇的发现计算的结果与实际结果有一定的偏差
[[]]
这里是==齐次坐标转换规则==的原因，一般来说，在坐标转换矩阵中，会将对象的坐标运算从笛卡尔坐标空间转换到齐次坐标空间内。而 [[空间和变换#1 .2 四维空间|在齐次坐标空间内0代表向量，而1代表的是坐标点]]，而由于我们通过转换的矩阵是直接通过目标点 `targetPos` 的世界坐标来计算的，而不像我们初始实现的那样，通过 `centerPos` 到 `targetPos` 的向量来执行计算，所以这里要补充的是1，代表该 `vector3` 表示的是 `targetPos` 的世界坐标

由于该位是1，就会在后续的矩阵乘法计算中加上偏移量，也就是 `centerPos` 的世界坐标点，代表的其相对于世界坐标（0，0，0）的偏移量，有点难以理解，但是到后面的矩阵计算时就会一目了然了
### 2、理解 TRS 矩阵
`TRS`矩阵，也就是由`Translate`、`Rotate`、`Scale`组合而成的矩阵，并且矩阵的变换顺序为先`Scale`，然后`Rotate`，最后再进行`Translate`的操作，这样的执行顺序是为了避免由于位移与旋转的影响而产生缩放的形变问题，所以先执行缩放的操作，而`TRS`的执行顺序可以理解为：
- T(R(Sp)))
 TRS 矩阵用于从本地坐标系到世界坐标系的变换，可以将一个向量变换到世界坐标系中的指定的位置
要完成 TRS 矩阵的生成转发，首先要理解 `TRS` 矩阵所构成的位置、旋转、缩放分别对应的基本矩阵，所以这里首先拆解一下各个矩阵：

#### **Translate：**
基于单位矩阵进行变化，位置信息会被记录在4x4矩阵的 `m01`、`m02`、`m03` 位置，在 `Unity` 中可以通过 `Matrix4x4.Translate()` 打印出位置矩阵。这里通过设置物体坐标位置（1，2，3）并通过 `Debug.Log(Matrix4x4.Translate(centerPos.position));` 打印出 `centerPos` 对应的位置矩阵，结果如图所示：
![[Pasted image 20240526190225.png|500]]
即 `Translate` 的矩阵表示为：
$$\left[
\begin{matrix}
1 & 0 & 0 & T_x\\
0 & 1 & 0 & T_y \\
0 & 0 & 1 & T_z\\
0 & 0 & 0 & 1
\end{matrix}
\right]
$$

#### **Rotate：**
旋转矩阵本身需要3x3矩阵，该矩阵记录了对象本地坐标的三个坐标轴的单位向量，即 `centerPos.Right` 和 `centerPos.Up` 以及 `centerPos.Forward` 三个坐标轴的向量，为 `centerPos` 设置一定的旋转量，并打印出结果，实施打印的代码为：

```csharp
        Debug.Log(Matrix4x4.Rotate(centerPos.rotation));
        Debug.Log(centerPos.right);
        Debug.Log(centerPos.up);
        Debug.Log(centerPos.forward);
```

打印结果，如图：
![[Pasted image 20240526190903.png|500]]
可以看出矩阵数值与对象的局部坐标轴的单位向量相互对应,即对象的旋转矩阵表示为：
$$\left[
\begin{matrix}
R_x & U_x & F_x & 0\\
R_y & U_y & F_y & 0 \\
R_z & U_z & F_z & 0\\
0   &   0 &   0 & 1
\end{matrix}
\right]
$$
#### **Scale：**
关于剩下的缩放的矩阵，最简单的想法是可以通过剩下的`m30`、`m31`、`m32`来记录，但是事实并不是如此，为了方便位移旋转与缩放的组合计算得到最后`TRS`矩阵，需要进行矩阵的乘法计算，同时缩放的三个分量分别对应旋转的三个坐标轴分量，为了在乘法将缩放与旋转结合起来，就必须使缩放矩阵与旋转矩阵相似，使其分量可以产生乘法计算

同样是基于3x3的矩阵来，设置 `centerPos` 的缩放为（2，3，4），并通过 `Debug.Log(Matrix4x4.Scale(centerPos.localScale));` 打印出对应的缩放矩阵，如图所示：
![[Pasted image 20240526191328.png|475]] 
则可以推断出来缩放的矩阵为：
$$\left[
\begin{matrix}
S_x & 0   & 0   & 0\\
0   & S_y & 0   & 0\\
0   & 0   & S_z & 0\\
0   & 0   & 0   & 1
\end{matrix}
\right]
$$

--------
得到对象的位移、旋转、缩放矩阵后，可以进行乘法计算得到对象的 `TRS` 矩阵，当然也可以直接通过 `Unity` 的封装的方法 `TRS(Vector3 pos, Quaternion q, Vector3 s)` 来直接得到对象的 `TRS` 矩阵，两种方式的代码示例：
```csharp
        Matrix4x4 trsOne=Matrix4x4.TRS(centerPos.position, centerPos.rotation, centerPos.localScale);
        Matrix4x4 trsTwo = Matrix4x4.Translate(centerPos.position) * Matrix4x4.Rotate(centerPos.rotation) * Matrix4x4.Scale(centerPos.localScale);    
```

根据上面的代码，以及每个乘法元素对应的矩阵结构来执行乘法的计算，通过矩阵的乘法来计算得到最后的矩阵，乘法的公式构成即 `Translate`、`Roate`、`Scale` 三个对应的基本转换矩阵，示例如下：
$$\left[
\begin{matrix}
1 & 0 & 0 & T_x\\
0 & 1 & 0 & T_y \\
0 & 0 & 1 & T_z\\
0 & 0 & 0 & 1
\end{matrix}
\right]
*
\left[
\begin{matrix}
R_x & U_x & F_x & 0\\
R_y & U_y & F_y & 0 \\
R_z & U_z & F_z & 0\\
0   &   0 &   0 & 1
\end{matrix}
\right]
*
\left[
\begin{matrix}
S_x & 0   & 0   & 0\\
0   & S_x & 0   & 0\\
0   & 0   & S_x & 0\\
0   & 0   & 0   & 1
\end{matrix}
\right]
$$
经过矩阵的乘法运算得到结果就是对象的 `TRS` 矩阵，其具体结构为：
$$\left[
\begin{matrix}
R_xS_x & U_xS_y & F_xS_z & T_x\\
R_yS_x & U_yS_y & F_yS_z & T_y\\
R_zS_x & U_zS_y & F_zS_z & T_z\\
0   & 0   & 0   & 1
\end{matrix}
\right]
$$
通过计算过程与结果来看，`Unity` 中的 `TRS` 矩阵是以列为主导的，前三行的前三列分别代表对象的坐标轴的单位向量与各个方向缩放的乘积，而剩下第四行用来表示位置信息

同时需要**注意**的是，虽然整个乘法过程看起来像是先旋转，但是要明白的是 `Unity` 对于矩阵与向量的乘法是右乘，而且矩阵乘法的先后顺序不影响计算结果，所以我们可以反向理解该乘法过程为：
- `Translate` 乘 （`Rotate` 乘 （`Scale` 乘 `Vector4`）））
### 3、世界转局部的转换矩阵
**worldToLocalMatrix**用于从世界坐标系到局部坐标系的变换，
#### **矩阵推导：**
在前面已经描述了一些实现方法，这里主要是来说明一下矩阵变换的过程，`Unity` 中默认提供给我们的是 `worldToLocalMatrix` 这个空间转换矩阵，如果我们通过改变对象的位移、旋转、缩放，就会发现其生成的变换矩阵与 `TRS` 类似，但是又有不同，简单示例：当我们只修改物体的旋转量后，可以发现得到的矩阵是行主导的，如图所示：
![[Pasted image 20240526193122.png|500]]
那这里就是对于旋转矩阵做了一个转置操作，即旋转对应的矩阵为旋转矩阵的转置矩阵，用代码表示为`Matrix4x4.Transpose(Matrix4x4.Rotate(centerPos.rotation))`，矩阵为：
$$\left[
\begin{matrix}
R_x & R_y & R_z & 0\\
U_x & U_y & U_z & 0 \\
F_x & F_y & F_z & 0\\
0 & 0 & 0 & 1
\end{matrix}
\right]
$$
对于位移，同样单独修改 `centerPos` 的坐标为（2，3，4），可以观察到打印出的矩阵为位置矩阵的反矩阵，即 `Matrix4x4.Translate(centerPos.position).inverse`，打印的结果如图：
![[Pasted image 20240526193424.png|500]]
所以 Translate 对应的矩阵为：
$$\left[
\begin{matrix}
1 & 0 & 0 & -T_x\\
0 & 1 & 0 & -T_y \\
0 & 0 & 1 & -T_z\\
0 & 0 & 0 & 1
\end{matrix}
\right]
$$
最后一步就是对于 `Scale` 执行修改，并观察结果，先说结论，`Scale` 与 `Translate` 相同，同样是进行了逆矩阵的操作，但是由于直接观察结果难以察觉到矩阵与逆矩阵的操作，所以我们直接通过打印两个矩阵进行数据对比：

```csharp
        Debug.Log(centerPos.worldToLocalMatrix);
        Debug.Log(Matrix4x4.Scale(centerPos.localScale).inverse);
```

执行代码，就会发现两个日志的结果相同，证明了世界坐标转局部坐标通过缩放的逆矩阵来实现，则缩放的矩阵为：
$$\left[
\begin{matrix}
\frac{1}{S_x} & 0   & 0   & 0\\
0   & \frac{1}{S_y} & 0   & 0\\
0   & 0   & \frac{1}{S_z} & 0\\
0   & 0   & 0   & 1
\end{matrix}
\right]
$$
得到 `Translate`、`Rotate`、`Scale` 的变换矩阵后，就可以对其执行乘法操作，但是与 `TRS` 不同的是，该矩阵的顺序为 `SRT`，代码为：
```csharp
    Matrix4x4.Scale(centerPos.localScale).inverse * Matrix4x4.Transpose(Matrix4x4.Rotate(centerPos.rotation)) * Matrix4x4.Translate(centerPos.position).inverse;   
    
```

根据矩阵的乘法，我们当然也可以得到最后的计算结果：
![[Pasted image 20240526194039.png|500]]
#### **消除缩放的影响：**
我们前面说到，对象的空间坐标转换，往往是刚体的转换，即位置与旋转，但是直接使用`worldToLocalMatrix`的话，对象的缩放会对转换的结果产生影响，所以这里需要消除缩放对于空间转换的影响，直接对`worldToLocalMatrix`乘上缩放的矩阵，这样就可以将公式内的缩放的逆矩阵转换为单位矩阵：

```csharp
    public Vector3 GetTargetRelatPosFirst(Transform targetPos, Transform centerPos)
    {       
        Matrix4x4 m4 = centerPos.worldToLocalMatrix*Matrix4x4.Scale(centerPos.localScale);
        return m4.MultiplyPoint3x4(targetPos.position);
    }
```

### 总结

掌握好矩阵的计算，可以很好的理解到空间`Translate`、`Rotate`、`Scale`的变换的过程，虽然不理解矩阵也可以通过向量或者四元数来完成所有操作，但是在执行复杂的变换操作时相对就比较难以理解，所以学习认识矩阵还是有一定的帮助的