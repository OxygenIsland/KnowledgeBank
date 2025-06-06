当代GPU被设计成可以执行大规模的并行操作，这有益于图形应用，因为在渲染管线中，不论是顶点着色器还是像素着色器，它们都可以独立进行。然而对于一些非图形应用也可以受益于GPU并行架构所提供的大量计算能力。比如说我们有个应用可以把两个excel里的N个值相加，如果N很大，那么是不是可以利用GPU来进行这些相加计算，来提升速度。像这样的非图形应用使用GPU的情况，我们称之为**GPGPU**（General Purpose GPU）编程。

对于GPGPU编程而言，用户通常需要将GPU计算后的结果返回到CPU中。例如前面的例子中，我们要在CPU中读取到GPU计算后值，以便可以将结果写入到新的excel中。这就涉及到将数据从GPU显存（Video Memory）中拷贝到CPU系统内存（System Memory）中的操作，该操作非常的**慢**。但是相比使用GPU来计算所提升的运行速度而言，可以忽略此问题。下图展示了CPU和RAM、GPU和VRAM、CPU和GPU之间的相对内存带宽速度（图中的数字只是说明性的数字，以显示带宽之间的数量级差异），可以发现瓶颈在于CPU和GPU之间的内存传输。
![[Pasted image 20250606153342.png|330]]
要实现GPGPU编程，我们就需要一个方法来访问GPU从而实现数据并行算法，这里就需要使用到Compute Shader（后面简称为CS）。CS属于图形API中的一种可编程着色器，它独立于渲染管线之外，但是可以对GPU资源（存放在显存中）进行读取和写入操作。==本质上来说，CS允许我们访问GPU来实现数据并行算法，而不需要绘制任何东西。==

当然了，CS除了适用于非图形应用的GPGPU编程外，我们也可以用它实现很多图形应用中的效果，例如剔除，模糊等。由于CS可以直接读写GPU资源，使得我们能够将CS的输出直接绑定到渲染管线上。因此对于图形应用，我们通常使用GPU的计算结果作为渲染管道的输入，因此不需要将结果从GPU传输到CPU。例如我们要实现一个模糊效果，可以先用CS模糊一个Texture，然后模糊后的Texture可以直接作为Fragment Shader的输入。

CS本质上是显卡以及图形API的产物，Unity引擎在Direct3D API的基础上对其进行了一层的封装。Unity ComputeShader是一种用于进行通用并行计算的特殊类型的Shader，用于在GPU上执行高性能通用计算。通过使用ComputeShader，开发人员可以利用GPU的并行计算能力来加速复杂的计算任务，如图像处理、物理模拟和数据处理等。通过利用ComputeShader，开发人员可以充分发挥GPU的潜力，提高应用程序的性能和效率。

## 1. 使用ComputeShader的步骤
在Project中右键，即可创建出一个CS文件：
![[Pasted image 20250606154428.png|500]]
生成的文件属于一种 Asset 文件，并且都是以 **.compute 作为文件后缀**的。我们来看下里面的默认内容：
```csharp
#pragma kernel CSMain

RWTexture2D<float4> Result;

[numthreads(8,8,1)]
void CSMain (uint3 id : SV_DispatchThreadID)
{
    Result[id.xy] = float4(id.x & id.y, (id.x & 15)/15.0, (id.y & 15)/15.0, 0.0);
}
```
### 2.1 kernel
`#pragma kernel CSMain`这一行即把一个名为CSMain的函数声明为内核，或者称之为核函数。这个核函数就是最终会在GPU中被执行。一个CS中**至少要有一个kernel才能够被唤起**。声明方法即为：`#pragma kernel functionName`
我们也可用它在一个CS里声明多个内核，此外我们还可以再该指令后面定义一些预处理的宏命令，如下：
```csharp
#pragma kernel KernelOne SOME_DEFINE DEFINE_WITH_VALUE=1337  
#pragma kernel KernelTwo OTHER_DEFINE
```
我们不能把注释写在该命令后面，而应该**换行写注释**，例如下面写法会造成编译的报错：
`#pragma kernel functionName // 一些注释`
### 2.2 RWTexture2D
````csharp
RWTexture2D<float4> Result;
````
RWTexture2D中，RW其实是**Read**和**Write**的意思，Texture2D就是二维纹理，因此它的意思就是**一个可以被CS读写的二维纹理**。如果我们只想读不想写，那么可以使用Texture2D的类型。

我们知道纹理是由一个个像素组成的，每个像素都有它的下标，因此我们就可以通过像素的下标来访问它们，例如：Result\[uint2(0,0)]。

同样的每个像素会有它的一个对应值，也就是我们要读取或者要写入的值。这个值的类型就被写在了<>当中，通常对应的是一个rgba的值，因此是float4类型。通常情况下，我们会在CS中处理好纹理，然后在Fragment Shader中来对处理后的纹理进行采样。

这样我们就大致理解这行代码的意思了，声明了一个名为Result的可读写二维纹理，其中每个像素的值为float4。

在CS中可读写的类型除了**RWTexture**以外还有**RWBuffer**和**RWStructuredBuffer**，后面会介绍。
### 2.3 numthreads
然后是下面一句（很重要！）：
```csharp
[numthreads(8,8,1)]
```

又是num，又是thread的，肯定和线程数量有关。没错，它就是定义**一个线程组（Thread Group）中可以被执行的线程（Thread）总数量。**

我们先来看看什么是线程组。在GPU编程中，我们可以将所有要执行的线程划分成一个个线程组，一个线程组在单个流多处理器（Stream Multiprocessor，简称SM）上被执行。如果我们的GPU架构有16个SM，那么至少需要16个线程组来保证所有SM有事可做。为了更好的利用GPU，每个SM至少需要两个线程组，因为SM可以切换到处理不同组中的线程来隐藏线程阻塞（如果着色器需要等待Texture处理的结果才能继续执行下一条指令，就会出现阻塞）。

每个线程组都有一个各自的共享内存（Shared Memory），该组中的所有线程都可以访问该组对应的共享内存，但是不能访问别的组对应的共享内存。因此线程同步操作可以在线程组中的线程之间进行，不同的线程组则不能进行同步操作。

每个线程组中又是由n个线程组成的，线程组中的线程数量就是通过numthreads来定义的，格式如下：

```cpp
numthreads(tX, tY, tZ)
```

> 注：X，Y，Z前加个t方便和后续线程组的X，Y，Z进行区分。

其中 tX、tY、 tZ 的值即线程的总数量，例如 numthreads(4, 4, 1) 和 numthreads(16, 1, 1) 都代表着有16个线程。那么为什么不直接使用 numthreads(num) 这种形式定义，而非要分成tX，tY，tZ这种三维的形式呢？看到后面自然就懂其中的奥秘了。

**每个核函数前面我们都需要定义numthreads**，否则编译会报错。

其中tX，tY，tZ三个值也并不是也可随便乱填的，它们在不同的版本里有如下的约束：

|Compute Shader 版本|tZ的最大取值|最大线程数量（tX*tY*tZ）|
|---|---|---|
|cs_4_x|1|768|
|cs_5_0|64|1024|

如果是NVIDIA的显卡，线程组中的线程又会被划分成一个个**Warp**，每个Warp由32个线程组成，一个Warp通过SM来调度。在SIMD32下，当SM操控一个Warp执行一个指令，意味着有32个线程同时执行相同的指令。假如我们使用numthreads设置每个线程组只有10个线程，但是由于SM每次调度一个Warp就会执行32个线程，这就会造成有22个线程是不干活的（静默状态），从而在性能上无法达到最优。因此针对NVIDIA的显卡，我们应该将线程组中的线程数设置为32的倍数来达到最佳性能。如果是AMD显卡的话，线程组中的线程则是被划分成一个个由64个线程组成**Wavefront**，那么线程组中的线程数应该设置为64的倍数。因此**建议numthreads值设为64的倍数**，这样可以同时顾及到两大主流的显卡。

在[Direct3D12](https://zhida.zhihu.com/search?content_id=169975694&content_type=Article&match_order=1&q=Direct3D12&zhida_source=entity)中，可以通过**ID3D12GraphicsCommandList::Dispatch(gX,gY,gZ)** 方法创建gX*gY*gZ个**线程组**。**注意顺序，先numthreads定义好每个核函数对应线程组里线程的数量（tX*tY*tZ），再用Dispatch定义用多少线程组(gX*gY*gZ)来处理这个核函数**。

gX，gY，gZ在不同的版本里有如下的约束：

|Compute Shader 版本|gX和gY的最大取值|gZ的最大取值|
|---|---|---|
|cs_4_x|65535|1|
|cs_5_0|65535|65535|

接着我们用一张示意图来看看线程与线程组的结构，如下图：
![[Pasted image 20250606160612.png|500]]
上半部分代表的是线程组结构，下半部分代表的是单个线程组里的线程结构。因为他们都是由(X,Y,Z)来定义数量的，因此就像一个三维数组，下标都是从0开始。我们可以把它们看做是表格一样：**有Z个一样的表格，每个表格有X列和Y行**。例如线程组中的(2,1,0)，就是第1个表格的第2行第3列对应的线程组，下半部分的线程也是同理。

搞清楚结构，我们就可以很好的理解下面这些与单个线程有关的参数含义：

|参数|值类型|含义|计算公式|
|---|---|---|---|
|SV_GroupID|int3|当前线程所在的线程组的ID，取值范围为(0,0,0)到(gX-1,gY-1,gZ-1)。|无|
|SV_GroupThreadID|int3|当前线程在所在线程组内的ID，取值范围为(0,0,0)到(tX-1,tY-1,tZ-1)。|无|
|SV_DispatchThreadID|int3|当前线程在所有线程组中的所有线程里的ID，取值范围为(0,0,0)到(gX*tX-1, gY*tY-1, gZ*tZ-1)。|假设该线程的SV_GroupID=(a, b, c)，SV_GroupThreadID=(i, j, k) 那么SV_DispatchThreadID=(a*tX+i, b*tY+j, c*tZ+k)|
|SV_GroupIndex|int|当前线程在所在线程组内的下标，取值范围为0到tX*tY*tZ-1。|假设该线程的SV_GroupThreadID=(i, j, k) 那么SV_GroupIndex=k*tX*tY+j*tX+i|

这里需要注意的是，不管是group还是thread，它们的**顺序都是先X再Y最后Z**，用表格的理解就是先行(X)再列(Y)然后下一个表(Z)，例如我们tX=5，tY=6那么第1个thread的SV_GroupThreadID=(0,0,0)，第2个的SV_GroupThreadID=(1,0,0)，第6个的SV_GroupThreadID=(0,1,0)，第30个的SV_GroupThreadID=(4,5,0)，第31个的SV_GroupThreadID=(0,0,1)。group同理，搞清顺序后，SV_GroupIndex的计算公式就很好理解了。

再举个例子，比如SV_GroupID为(0,0,0)和(1,0,0)的两个group，它们内部的第1个thread的SV_GroupThreadID都为(0,0,0)且SV_GroupIndex都为0，但是前者的SV_DispatchThreadID=(0,0,0)而后者的SV_DispatchThreadID=(tX,0,0)。

好好理解下，它们在核函数里非常的重要。
> [!note]+ note
> 其实就是一个线程的排序问题，为每一个线程排一个座位号，靠座位号来进行区分和索引
### 2.4 核函数
```cpp
void CSMain (uint3 id : SV_DispatchThreadID)
{
    Result[id.xy] = float4(id.x & id.y, (id.x & 15)/15.0, (id.y & 15)/15.0, 0.0);
}
```

最后就是我们声明的核函数了（其实就是Compute Shader函数体），其中参数SV_DispatchThreadID的含义上面已经介绍过了，除了这个参数以外，我们前面提到的几个参数都可以被传入到核函数当中，根据实际需求做取舍即可，完整如下：

```cpp
void KernelFunction(uint3 groupId : SV_GroupID,
    uint3 groupThreadId : SV_GroupThreadID,
    uint3 dispatchThreadId : SV_DispatchThreadID,
    uint groupIndex : SV_GroupIndex)
{
    
}
```

Unity默认的核函数体内执行的代码就是为我们Texture中下标为 id.xy 的像素赋值一个颜色，这里也就是最牛逼的地方。

举个例子，以往我们想要给一个 x*y 分辨率的Texture每个像素进行赋值，单线程的情况下，我们的代码往往如下：

```cpp
for (int i = 0; i < x; i++)
    for (int j = 0; j < y; j++)
        Result[uint2(x, y)] = float4(a, b, c, d);
```

两个循环，像素一个个的慢慢赋值。那么如果我们要每帧给很多张2048*2048的图片进行操作，可想而知会卡死你。

如果使用多线程，为了避免不同的线程对同一个像素进行操作，我们往往使用分段操作的方法，如下，四个线程进行处理：

```csharp
void Thread1()
{
    for (int i = 0; i < x/2; i++)
        for (int j = 0; j < y/2; j++)
            Result[uint2(x, y)] = float4(a, b, c, d);
}

void Thread2()
{
    for (int i = 0; i < x/2; i++)
        for (int j = y/2; j < y; j++)
            Result[uint2(x, y)] = float4(a, b, c, d);
}

void Thread3()
{
    for (int i = x/2; i < x; i++)
        for (int j = 0; j < y/2; j++)
            Result[uint2(x, y)] = float4(a, b, c, d);
}

void Thread4()
{
    for (int i = x/2; i < x; i++)
        for (int j = y/2; j < y; j++)
            Result[uint2(x, y)] = float4(a, b, c, d);
}
```

这么写不是很蠢么，如果有更多的线程，分成更多段，不就一堆重复的代码。但是如果我们能知道每个线程的开始和结束下标，不就可以把这些代码统一起来了么，如下：

```cpp
void Thread(int start, int end)
{
    for (int i = start; i < end; i++)
        for (int j = start; j < end; j++)
            Result[uint2(x, y)] = float4(a, b, c, d);
}
```

那我要是可以开出很多很多的线程是不是就可以一个线程处理一个像素了？

```cpp
void Thread(int x, int y)
{
    Result[uint2(x, y)] = float4(a, b, c, d);
}
```

用CPU我们做不到这样，但是用GPU，用CS我们就可以，实际上，前面默认的CS的代码里，核函数的内容就是这样的。

接下来我们来看看CS的妙处，**看 id.xy 的值**。id 的类型为SV_DispatchThreadID，我们先来回忆下SV_DispatchThreadID的计算公式：

> 假设该线程的SV_GroupID=(a, b, c)，SV_GroupThreadID=(i, j, k) 那么SV_DispatchThreadID=(a*tX+i, b*tY+j, c*tZ+k)

首先前面我们使用了[numthreads(8,8,1)]，即tX=8，tY=8，tZ=1 ，且 i 和 j 的取值范围为0到7，而k=0。那么我们线程组(0,0,0)中所有线程的 SV_DispatchThreadID.xy 也就是 id.xy 的取值范围即为 (0,0) 到 (7, 7)，线程组(1,0,0)中它的取值范围为 (8,0) 到 (15, 7)，...，线程组(0,1,0)中它的取值范围为 (0,8) 到 (7, 15)，...，线程组(a,b,0)中它的取值范围为(a*8, b*8, 0)到(a*8+7, b*8+7, 0)。

我们用示意图来看下，假设下图每个网格里包含了64个像素：
![[Pasted image 20250606163310.png|500]]
也就是说我们每个线程组会有64个线程同步处理64个像素，并且不同的线程组里的线程不会重复处理同一个像素，若要处理分辨率为 1024\*1024 的图，我们只需要dispatch(1024/8, 1024/8, 1)个线程组。

这样就实现了成百上千个线程同时处理一个像素了，若用CPU的方式这是不可能的。是不是很妙？

而且我们可以发现numthreads中设置的值是很值得推敲的，例如我们有4\*4的矩阵要处理，那么设置numthreads(4,4,1)，那么每个线程的SV_GroupThreadID.xy的值不正好可以和矩阵中每项的下标对应上么。

那么我们在Unity中怎么调用核函数，又怎么dispatch线程组以及使用的RWTexture又怎么来呢？这里就要回到我们C#的部分了。
## 2. C#部分
以往的Vertex & Fragment shader我们都是给它关联到Material上来使用的，但是CS不一样，它是**由c#来驱动**的。先新建一个monobehaviour脚本，Unity为我们提供了一个**ComputeShader**的类型用来引用我们前面生成的 .compute 文件：
```csharp
public ComputeShader computeShader;
```
![[Pasted image 20250606165143.png|345]]
此外我们再关联一个Material，因为CS处理后的纹理，依旧要经过FragmentShader采样后来显示。
```text
public Material material;
```
这个Material我们使用一个Unlit Shader，并且纹理不用设置，如下：
![[Pasted image 20250606165223.png|343]]
然后关联到我们的脚本上，并且随便建个Cube也关联上这Material。

接着我们可以将Unity中的**RenderTexture**赋值到CS中的RWTexture2D上，但是需要注意因为我们是多线程处理像素，并且这个处理过程是**无序**的，因此我们要将RenderTexture的**enableRandomWrite**属性设置为true，代码如下：

```csharp
RenderTexture mRenderTexture = new RenderTexture(256, 256, 16);
mRenderTexture.enableRandomWrite = true;
mRenderTexture.Create();
```

我们创建了一个分辨率为256\*256的RenderTexture，首先我们要把它赋值给我们的Material，这样我们的Cube就会显示出它。然后要把它赋值给我们CS中的Result变量，代码如下：

```csharp
material.mainTexture = mRenderTexture;
computeShader.SetTexture(kernelIndex, "Result", mRenderTexture);
```

这里有一个kernelIndex变量，即核函数下标，我们可以利用FindKernel来找到我们声明的核函数的下标：

```csharp
int kernelIndex = computeShader.FindKernel("CSMain");
```

这样在我们Fragment Shader采样的时候，采样的就是CS处理过后的纹理：

```csharp
fixed4 frag (v2f i) : SV_Target
{
    // _MainTex 就是被处理后的 RenderTexture
    fixed4 col = tex2D(_MainTex, i.uv);
    return col;
}
```

> 注：此时没有将CS的处理结果从GPU回读到CPU的操作，因为处理结果直接输入到渲染管线中由Fragment Shader进行处理了。

最后就是开线程组和调用我们的核函数了，C#的ComputeShader类提供了Dispatch方法为我们一步到位：

```csharp
computeShader.Dispatch(kernelIndex, 256 / 8, 256 / 8, 1);
```

为什么是256/8，前面已经解释过了。来看看效果：
![[Pasted image 20250606165945.png|360]]
上图就是我们Unity默认生成的CS代码所能带来的效果，我们也可试下用它处理2048*2048的Texture，也是非常快的。

接下来我们再来看看粒子效果的例子：

首先一个粒子通常拥有颜色和位置两个属性，并且我们肯定是要在CS里去处理这两个属性的，那么我们就可以在CS创建一个struct来存储：

```cpp
struct ParticleData {
	float3 pos;
	float4 color;
};
```

接着，这个粒子肯定是很多很多的，我们就需要一个像List一样的东西来存储它们，HLSL为我们提供了RWStructuredBuffer类型。
## RWStructuredBuffer
它是一个可读写的buffer，并且我们可以指定buffer中的数据类型为我们**自定义**的struct类型，不用再局限于int，float这类的基本类型。因此我们可以这么定义我们的粒子数据：

```cpp
RWStructuredBuffer<ParticleData> ParticleBuffer;
```
为了有动效，我们可以再添加一个时间相关值，我们可以根据时间来修改粒子的位置和颜色：

```cpp
float Time;
```

接着就是怎么在核函数里修改我们的粒子信息了，要修改某个粒子，我们肯定要知道粒子在buffer中的下标，并且这个下标在不同的线程中不能重复，否则就可能导致多个线程修改同一个粒子了。

根据前面的介绍，我们知道一个线程组中SV_GroupIndex是唯一的，但是在不同线程组中并不是，例如每个线程组内有1000个线程，那么SV_GroupID都是0到999。那么我们可以根据SV_GroupID把它叠加上去，例如SV_GroupID=(0,0,0)时是0-999，SV_GroupID=(1,0,0)是1000-1999等等，为了方便我们的线程组就可以是(X,1,1)格式。然后我们就可以根据Time和Index随便的摆布下粒子，CS完整代码：

```glsl
#pragma kernel UpdateParticle

struct ParticleData {
	float3 pos;
	float4 color;
};

RWStructuredBuffer<ParticleData> ParticleBuffer;

float Time;

[numthreads(10, 10, 10)]
void UpdateParticle(uint3 gid : SV_GroupID, uint index : SV_GroupIndex)
{
	int pindex = gid.x * 1000 + index;
	
	float x = sin(index);
	float y = sin(index * 1.2f);
	float3 forward = float3(x, y, -sqrt(1 - x * x - y * y));
	ParticleBuffer[pindex].color = float4(forward.x, forward.y, cos(index) * 0.5f + 0.5, 1);
	if (Time > gid.x)
		ParticleBuffer[pindex].pos += forward * 0.005f;
}
```

接下来我们要在C#里给粒子初始化并且传递给CS。我们要传递粒子数据，也就是说要给前面的RWStructuredBuffer\<ParticleData>赋值，Unity为我们提供了**ComputeBuffer类来与RWStructuredBuffer或StructuredBuffer相对应**。

## ComputeBuffer

在CS中经常需要将我们一些CPU种自定义的Struct数据读写到显存中，ComputeBuffer就是为这种情况而生的。我们可以在C#里创建并填充它，然后传递到CS或者其他Shader中使用。通常我们用下面方法来创建它：

```csharp
ComputeBuffer buffer = new ComputeBuffer(int count, int stride)
```

其中count代表我们buffer中元素的数量，而stride指的是每个元素占用的空间（字节），例如我们传递10个float的类型，那么count=10，stride=4。需要注意的是**ComputeBuffer中的stride大小必须和RWStructuredBuffer中每个元素的大小一致**。

声明完成后我们可以使用SetData方法来填充，参数为自定义的struct数组：

```csharp
buffer.SetData(T[]);
```

最后我们可以使用ComputeShader类中的SetBuffer方法来把它传递到CS中：

```csharp
public void SetBuffer(int kernelIndex, string name, ComputeBuffer buffer)
```

记得用完后把它Release()掉。
在C#中我们定义一个一样的Struct，这样才能保证和CS中的大小一致：

```csharp
public struct ParticleData
{
    public Vector3 pos;//等价于float3
    public Color color;//等价于float4
}
```

然后我们在Start方法中声明我们的ComputeBuffer，并且找到我们的核函数：

```csharp
void Start()
{
    //struct中一共7个float，size=28
    mParticleDataBuffer = new ComputeBuffer(mParticleCount, 28);
    ParticleData[] particleDatas = new ParticleData[mParticleCount];
    mParticleDataBuffer.SetData(particleDatas);
    kernelId = computeShader.FindKernel("UpdateParticle");
}
```

由于我们想要我们的粒子是运动的，即每帧要修改粒子的信息。因此我们在Update方法里去传递Buffer和Dispatch：

```csharp
void Update()
{
    computeShader.SetBuffer(kernelId, "ParticleBuffer", mParticleDataBuffer);
    computeShader.SetFloat("Time", Time.time);
    computeShader.Dispatch(kernelId,mParticleCount/1000,1,1);
}
```

到这里我们的粒子位置和颜色的操作都已经完成了，但是这些数据并不能在Unity里显示出粒子，我们还需要Vertex & FragmentShader的帮忙，我们新建一个UnlitShader，修改下里面的代码如下：

```glsl
Shader "Unlit/ParticleShader"
{
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        LOD 100

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            
            #include "UnityCG.cginc"

            struct v2f
            {
                float4 col : COLOR0;
                float4 vertex : SV_POSITION;
            };
            
            struct particleData
            {
		float3 pos;
		float4 color;
            };

            StructuredBuffer<particleData> _particleDataBuffer;
            
            v2f vert (uint id : SV_VertexID)
            {
                v2f o;
                o.vertex = UnityObjectToClipPos(float4(_particleDataBuffer[id].pos, 0));
                o.col = _particleDataBuffer[id].color;
                return o;
            }

            fixed4 frag (v2f i) : SV_Target
            {
                return i.col;
            }
            ENDCG
        }
    }
}
```

前面我们说了ComputeBuffer也可以传递到普通的Shader中，因此我们在Shader中也创建一个结构一样的Struct，然后利用StructuredBuffer\<T>来接收。

**SV_VertexID：**在VertexShader中用它来作为传递进来的参数，代表顶点的下标。我们有多少个粒子即有多少个顶点。顶点数据使用我们在CS中处理过的buffer。

最后我们在C#中关联一个带有上面shader的material，然后将粒子数据传递过去，最终绘制出来。完整代码如下：

```csharp
public class ParticleEffect : MonoBehaviour
{
    public ComputeShader computeShader;
    public Material material;
    
    ComputeBuffer mParticleDataBuffer;
    const int mParticleCount = 20000;
    int kernelId;
    
    struct ParticleData
    {
        public Vector3 pos;
        public Color color;
    }

    void Start()
    {
        //struct中一共7个float，size=28
        mParticleDataBuffer = new ComputeBuffer(mParticleCount, 28);
        ParticleData[] particleDatas = new ParticleData[mParticleCount];
        mParticleDataBuffer.SetData(particleDatas);
        kernelId = computeShader.FindKernel("UpdateParticle");
    }

    void Update()
    {
        computeShader.SetBuffer(kernelId, "ParticleBuffer", mParticleDataBuffer);
        computeShader.SetFloat("Time", Time.time);
        computeShader.Dispatch(kernelId,mParticleCount/1000,1,1);
        material.SetBuffer("_particleDataBuffer", mParticleDataBuffer);
    }

    void OnRenderObject()
    {
        material.SetPass(0);
        Graphics.DrawProceduralNow(MeshTopology.Points, mParticleCount);
    }

    void OnDestroy()
    {
        mParticleDataBuffer.Release();
        mParticleDataBuffer = null;
    }
}
```

**material.SetBuffer**：传递ComputeBuffer到我们的shader当中。

**OnRenderObject**：该方法里我们可以自定义绘制几何。

**DrawProceduralNow**：我们可以用该方法绘制几何，第一个参数是拓扑结构，第二个参数数顶点数。
最终得到的效果如下：
![[a3b48644-01cf-11ec-9224-ea60cd877544.mp4]]
## ComputeBufferType

在例子中，我们new一个ComputeBuffer的时候并没有使用到[ComputeBufferType](https://link.zhihu.com/?target=https%3A//docs.unity3d.com/ScriptReference/ComputeBufferType.html)的参数，默认使用了ComputeBufferType.Default。实际上我们的ComputeBuffer可以有多种不同的类型对应[HLSL中不同的Buffer](https://link.zhihu.com/?target=https%3A//docs.microsoft.com/en-us/windows/win32/direct3d11/direct3d-11-advanced-stages-cs-resources)，来在不同的场景下使用，一共有如下几种类型：

|   |   |
|---|---|
|Default|ComputeBuffer的默认类型，对应HLSL shader中的StructuredBuffer或RWStructuredBuffer，常用于自定义Struct的Buffer传递。|
|Raw|Byte Address Buffer，把里面的内容（byte）做偏移，可用于寻址。它对应HLSL shader中的ByteAddressBuffer或RWByteAddressBuffer，用于着色器访问的底层DX11格式为无类型的R32。|
|Append|Append and Consume Buffer，允许我们像处理Stack一样处理Buffer，例如动态添加和删除元素。它对应HLSL shader中的AppendStructuredBuffer或ConsumeStructuredBuffer。|
|Counter|用作计数器，可以为RWStructuredBuffer添加一个计数器，然后在ComputeShader中使用IncrementCounter或DecrementCounter方法来增加或减少计数器的值。由于Metal和Vulkan平台没有原生的计数器，因此我们需要一个额外的小buffer用来做计数器。|
|Constant|constant buffer (uniform buffer)，该buffer可以被当做Shader.SetConstantBuffer和Material.SetConstantBuffer中的参数。如果想要绑定一个structured buffer那么还需要添加ComputeBufferType.Structured，但是在有些平台（例如DX11）不支持一个buffer即是constant又是structured的。|
|Structured|如果没有使用其他的ComputeBufferType那么等价于Default。|
|IndirectArguments|被用作 Graphics.DrawProceduralIndirect，ComputeShader.DispatchIndirect或Graphics.DrawMeshInstancedIndirect这些方法的参数。buffer大小至少要12字节，DX11底层UAV为R32_UINT，SRV为无类型的R32。|

举个例子，在做GPU剔除的时候经常会使用到Append的Buffer（例如后面介绍的用CS实现视椎剔除），C#中的声明如下：

```csharp
var buffer = new ComputeBuffer(count, sizeof(float), ComputeBufferType.Append);
```

注：Default，Append，Counter，Structured对应的Buffer每个元素的大小，也就是stride的值应该是4的倍数且小于2048。

上述ComputeBuffer可以对应CS中的AppendStructuredBuffer，然后我们可以在CS里使用Append方法为Buffer添加元素，例如：

```glsl
AppendStructuredBuffer<float> result;

[numthreads(640, 1, 1)]
void ViewPortCulling(uint3 id : SV_DispatchThreadID)
{
    if(满足一些自定义条件)
        result.Append(value);
}
```

那么我们的buffer中到底有多少个元素呢？计数器可以帮助我们得到这个结果。

在C#中，我们可以先使用ComputeBuffer.SetCounterValue方法来初始化计数器的值，例如：

```csharp
buffer.SetCounterValue(0);//计数器值为0
```

随着AppendStructuredBuffer.Append方法，我们计数器的值会自动的++。当CS处理完成后，我们可以使用ComputeBuffer.CopyCount方法来获取计数器的值，如下：

```csharp
public static void CopyCount(ComputeBuffer src, ComputeBuffer dst, int dstOffsetBytes);
```

Append，Consume或者Counter的buffer会维护一个计数器来存储buffer中的元素数量，该方法可以把src中的计数器的值拷贝到dst中，dstOffsetBytes为在dst中的偏移。在DX11平台dst的类型必须为Raw或者IndirectArguments，而在其他平台可以是任意类型。

因此获取buffer中元素数量的代码如下：

```csharp
uint[] countBufferData = new uint[1] { 0 };
var countBuffer = new ComputeBuffer(1, sizeof(uint), ComputeBufferType.IndirectArguments);
ComputeBuffer.CopyCount(buffer, countBuffer, 0);
countBuffer.GetData(countBufferData);
//buffer中的元素数量即为：countBufferData[0]
```

---
## UAV（Unordered Access view）

通常我们Shader中使用的资源被称作为**SRV（Shader resource view）**，例如Texure2D，它是**只读**的。但是在Compute Shader中，我们往往需要对Texture进行写入的操作，因此SRV不能满足我们的需求，而应该使用一种新的类型来绑定我们的资源，即UAV。它允许来自多个线程临时的无序读/写操作，这意味着该资源类型可以由多个线程同时读/写，而不会产生内存冲突。

前面我们提到了RWTexture，RWStructuredBuffer这些类型都属于UAV的数据类型，并且它们**支持在读取的同时写入**。它们只能在Fragment Shader和Compute Shader中被使用（绑定）。

如果我们的RenderTexture不设置enableRandomWrite，或者我们传递一个Texture给RWTexture，那么运行时就会报错：

> the texture wasn't created with the UAV usage flag set!

  

## groupshared

我们可以通过Dispatch操作执行很多的线程组，每个线程组都有一块属于它们自己的内存空间，我们称之为（组内）共享内存或线程本地存储。线程组内的所有线程都可以对当前线程组的共享内存进行访问，但是没法访问别的线程组的共享内存。

通过groupshared关键字声明的变量会被存放在共享内存中，例如：

```cpp
groupshared float4 vec;
```

每个线程组都会有自己对应的vec变量，当前线程组对vec的修改不会影响到别的线程组的vec值。

Direct3D 11以来，共享内存支持的最大大小为32kb（之前的版本是16kb），并且单个线程最多支持对共享内存进行256byte的写入操作。

线程访问共享内存的速度非常的快，可以认为与硬件缓存一样快。我们常用它来缓存像素值，来避免不同线程之间重复采样的操作（采样是一个比较耗时的操作），例如：

```cpp
Texture2D input;
groupshared float4 cache[256];

[numthreads(256, 1, 1)]
void CS(int3 groupThreadID : SV_GroupThreadID, int3 dispatchThreadID : SV_DispatchThreadID)
{
    cache[groupThreadID.x] = input[dispatchThreadID.xy];

    GroupMemoryBarrierWithGroupSync();

    float4 left = cache[groupThreadID.x - 1];
    float4 right = cache[groupThreadID.x + 1];
    ......
}
```

其中**GroupMemoryBarrierWithGroupSync**起到组内线程同步的作用。该函数会阻塞线程组中所有线程的执行，直到所有共享内存的访问完成并且线程组中的所有线程都执行到此调用。这样就避免了当我们在读取共享内存的时候，它却还没有写入完成的问题。

  

## 移动端支持问题

我们可以运行时调用 **SystemInfo.supportsComputeShaders** 来判断当前的机型是否支持CS。其中OpenGL ES 从 3.1 版本才开始支持CS，而使用Vulkan的Android平台以及使用Metal的IOS平台都支持CS。

然而有些Android手机即使支持CS，但是对RWStructuredBuffer的支持并不友好。例如在某些OpenGL ES 3.1的手机上，只支持Fragment Shader内访问StructuredBuffer。

在普通的shader中要支持CS，shader model最低要求为4.5，即：

```text
#pragma target 4.5
```
## Shader.PropertyToID

在CS中定义的变量依旧可以通过 Shader.PropertyToID("name") 的方式来获得唯一id。这样当我们要频繁利用 ComputeShader.SetBuffer 对一些相同变量进行赋值的时候，就可以把这些id事先缓存起来，避免造成GC。

```csharp
int grassMatrixBufferId;
void Start() {
    grassMatrixBufferId = Shader.PropertyToID("grassMatrixBuffer");
}
void Update() {
    compute.SetBuffer(kernel, grassMatrixBufferId, grassMatrixBuffer);
    
    // dont use it
    //compute.SetBuffer(kernel, "grassMatrixBuffer", grassMatrixBuffer);
}
```

  

## 全局变量或常量？

假如我们要实现一个需求，在CS中判断某个顶点是否在一个固定大小的包围盒内，那么按照以往C#的写法，我们可能如下定义包围盒大小：

```glsl
#pragma kernel CSMain

float3 boxSize1 = float3(1.0f, 1.0f, 1.0f); // 方法1
const float3 boxSize2 = float3(2.0f, 2.0f, 2.0f); // 方法2
static float3 boxSize3 = float3(3.0f, 3.0f, 3.0f); // 方法3

[numthreads(8,8,1)]
void CSMain (uint3 id : SV_DispatchThreadID)
{
    // 做判断
}
```

经过测试，其中方法1和方法2的定义，在CSMain里读取到的值都为 float3(0.0f,0.0f,0.0f) ，只有方法3才是最开始定义的值。

  

## Shader variants and keywords

CS同样支持[shader变体](https://link.zhihu.com/?target=https%3A//docs.unity3d.com/2020.3/Documentation/Manual/SL-MultipleProgramVariants.html)，用法和普通的shader变体基本相似，示例如下：

```glsl
#pragma kernel CSMain
#pragma multi_compile __ COLOR_WHITE COLOR_BLACK

RWTexture2D<float4> Result;

[numthreads(8,8,1)]
void CSMain (uint3 id : SV_DispatchThreadID)
{
#if defined(COLOR_WHITE)
	Result[id.xy] = float4(1.0, 1.0, 1.0, 1.0);
#elif defined(COLOR_BLACK)
	Result[id.xy] = float4(0.0, 0.0, 0.0, 1.0);
#else
	Result[id.xy] = float4(id.x & id.y, (id.x & 15) / 15.0, (id.y & 15) / 15.0, 0.0);
#endif
}
```

然后我们就可以在C#端启用或禁用某个变体了：

- #pragma multi_compile 声明的全局变体可以使用Shader.EnableKeyword/Shader.DisableKeyword或者ComputeShader.EnableKeyword/ComputeShader.DisableKeyword
- #pragma multi_compile_local 声明的局部变体可以使用ComputeShader.EnableKeyword/ComputeShader.DisableKeyword

示例如下：

```csharp
public class DrawParticle : MonoBehaviour
{
    public ComputeShader computeShader;

    void Start() {
        ......
        computeShader.EnableKeyword("COLOR_WHITE");
    }
}
```
