## 1.1. Graphics APIs
There are currently two dominant paradigms for graphics and user-interface APIs. 两种主流模式的 API：
The first is the integrated approach（集成方法）, exemplified by Java, where the graphics and userinterface toolkits（用户界面工具包） are integrated and portable packages that are fully standardized and supported as part of the language. 
The second is represented by Direct3D and OpenGL, where the drawing commands（绘制命令） are part of a software library tied to a language such as C++, and the user-interface software is an independent entity that might vary from system to system. In this latter approach, it is problematic to write portable code, although for simple programs it may be possible to use a portable library layer to encapsulate the system specific user-interface code. 
## 1.2. Graphics Pipeline
Every desktop computer today has a powerful 3D graphics pipeline. 
渲染管线是 => a special software/hardware subsystem that efficiently draws 3D primitives (三维基元) in perspective. 
The basic operations in the pipeline map the 3D vertex locations to 2D screen positions and shade the triangles so that they both look realistic and appear in proper back-to-front order. 目前这个 proper back-to-front order 是通过 z-buffer 来实现的。

It turns out that the geometric manipulation used in the graphics pipeline can be accomplished almost entirely in a 4D coordinate space composed of three traditional geometric coordinates and a fourth homogeneous coordinate that helps with perspective viewing. 
渲染管线中使用到的几何操作可以在一个 4 D coordinate space 中完成，也就是 #TODO齐次坐标系 ?？中完成。空间中的 4 维坐标使用 4 × 4
Matrices and 4-vectors 来处理

The speed at which images can be generated depends strongly on the number of triangles being drawn.
当应用的交互性比视觉性重要时，要 minimize the number of triangles used to represent a model。
In addition, if the model is viewed in the distance, fewer triangles are needed than when the model is viewed from a closer distance.
This suggests that it is useful to represent a model with a varying level of detail(==LOD==).
## 1.3 Numerical Issues 数学问题
Many graphics programs are really just 3D numerical codes（三维的数学表达式）. 所以，接下来我们了解一些基本的数学知识
1. 3 个特殊值
	- Infinity ($\infty$)
	- Minus infinity ($-\infty$)
	- Not a number (NaN) This is an invalid number that arises from an operation with undefined consequences, such as zero divided by zero.
下面是一些简单的运算法则，其中 a 是一个正实数：
![[Pasted image 20240423213940.png|233]]   ![[Pasted image 20240423214021.png|206]]   ![[Pasted image 20240423214442.png|229]]
其中，涉及到 NaN 的表达式要遵循以下规则：
- Any arithmetic expression that includes NaN results in NaN.
- Any Boolean expression involving NaN is false.
## 1.4 Designing and Coding Graphics Programs
### 1.4.1 Class Design
A key part of any graphics program is to have good classes or routines for geometric entities such as vectors and matrices, as well as graphics entities such as RGB colors and images. 
This implies that some basic classes to be written include:
- **vector 2**
- **vector 3**
- **hvector**  A homogeneous vector with four components (see Chapter 7).
- **rgb**  An RGB color that stores three components. 
- **transform**  A 4 × 4 matrix for transformations.
- **image**  A 2D array of RGB pixels with an output operation.
### 1.4.2 Float 和 Double
