---
title: "[[2、Pipeline]]"
type: Literature
status: done
Creation Date: 2024-07-04 14:52
tags:
---
## Pipeline in Detail

Two **major** points of the pipeline will be explained below, which **weren’t** totally wrong explained [here in book I](http://simonschreibt.de/gat/renderhell-book1), but might not be clear enough:
1. **Not** everything is done by the “tiny” GPU cores!  
2. There can be **several parallel** running pipelines!
## 1 . Not everything is done by the “tiny” GPU cores!
In the pipeline example above it might seem like every pipeline stage is done by the GPU Cores – This is **NOT** the case! In fact, most of the stuff is **not** done by them. In the new section in [[1、Verview#1 . Copy the data into system memory for fast access|1. Copy the data into system memory for fast access]] you already saw that several components are necessary to just bring the data to a core. So what work do the cores actually do?
Let’s observe one:
![[gpu_core_exhibitionist_01.webm]]
A core can receive commands and data. Then it executes the command by calculating the data in a floating point unit (FP UNIT) **or** an integer unit (INT UNIT). So you could say: A core can calculate pixels and vertices (maybe also other calculations like physics but let’s focus on graphic rendering).

Other important stuff like distribute the render-tasks, calculate tessellation（曲面细分）, culling and preparing the fragments for the pixel shader, depth testing and writing pixels into the frame buffer are **NOT** done by the cores. This work is done by special, **not** programmable hardware blocks which are also placed in the GPU.

Ok, after we know that now, let’s move on to the next major point I have to clear out:
## 2 . There can be several parallel running pipelines!
First, I’ll give you a short example what I mean with that headline. If you’re still thirsty after this, I’ll take you into an even **more** detailed explanation.
But first, let’s recap: If we would only have **one** GPU Core, what could we calculate with it?
![[Pasted image 20240704153112.png|500]]
Correct: Nothing! Because the core needs someone who assigns him some work. This is done by a Streaming Multiprocessor **（SM，流处理器簇）** which can handle a stream of vertices/pixels which belong to **one** shader. OK, with that and one core we could calculate one vertex/pixel at a time:
![[Pasted image 20240704153347.png|500]]
当然了，如果我们增加 Core 的数量，就可以在同一时刻计算多个顶点/像素了，但前提是这些顶点和像素都必须属于同一个着色器！
![[Pasted image 20240704153426.png|500]]
This was already explained in my first attempt of explaining the pipeline! But now it gets interesting: What if we would add **another** Streaming Multiprocessor which cares about half of the cores?
![[Pasted image 20240704154012.png|500]]
Now we can not only calculate vertices/pixels in parallel, we can also take care about **2 shader streams** at the same time! This means, we can for example run two different pixel shaders at the same time or run a vertex shader AND a pixel shader at the same time!

This rough example shall just give you a glimpse about that several different hardware blocks are involved and they all work in parallel so the pipeline is more flexible than I described in my first attempt.

Anyone still thirsty? Then let’s get into more detail!
## 3 . In-Depth look into the pipeline stages
### 3.1 Overview
First of all: Why do we need a flexible/parallel pipeline? The reason is, that you can’t foresee, what workload you’ll have. Especially with tessellation it might be, that there are suddenly 100.000 more polygons on the screen than one frame before. Therefore you need a flexible pipeline which handles totally different workloads.

**DON’T WORRY!**

Please don’t be afraid by looking at the two following images (like I am when i read a Wikipedia article and see formulas between the text)! Yes, this stuff isn’t easy and even complex charts only show what a programmer needs to know and hide a lot of the “real” complexity. I only show it to give you a rough understand **how** complicated this stuff is. :)

The following image shows a GPU. I have no idea about what is what, but it’s kind of beautiful, isn’t it?
![[Pasted image 20240704160723.png|500]]
And here’s an image from Christoph Kubisch’ Article “Life of a triangle”. It shows parts of the work which is happening on a GPU in structured graphics.
![[Pasted image 20240704160830.png|1025]]
I hope you’ve a rough idea about the complexity now and will realize how much the explanations below are simplified. Let’s now have a detailed look on the whole pipeline.

### 3.2 Application Stage
It starts with the application or a game telling the driver (驱动程序) that it wants something rendered.
![[pipeline_application_stage_01.webm]]
### 3.3 Driver Stage
The driver receives the commands from the application and puts them into a [[1、Verview#5 . Command Buffer|command buffer]]. After a while (or when the programmer forces it), the commands are send to the GPU.
![[pipeline_driver_stage_01.webm]]
### 3.4 Read commands
Now we’re **on the graphic card**! The **Host Interface** reads commands to make them available for further use.
![[pipeline_readcommands_stage_01.webm]] 
### 3.5 Data Fetch
Some of the commands sent to the GPU can contain data or are instructions to copy data. The GPU typically has a dedicated（专用的） engine to deal with copying data from RAM to VRAM and vice versa (反之亦然). This data could be anything filling vertex buffers, textures or other shader parameter buffers. Our frame would typically start with some camera matrices being sent.
![[pipeline_datafetch_stage_01.webm]]
**Important:**
1. I symbolize the data as geometries but in fact we’re talking just about vertex-lists (vertex buffer). For a long time the rendering process doesn’t care about the final model. Instead, most of the time, only single vertices/pixels are worked with.
2. Textures **only** get copied, if they’re not **already** in the VRAM on the graphic card!
3. If vertex buffer are used a lot, they can stay in the VRAM like textures and don’t have to be copied with every draw call
4. Vertex buffers **may** stay in the RAM (not VRAM) if they change a lot. Then the GPU can read the data directly from RAM to its Caches.

Now that all ingredients (原料) are ready the Gigathread Engine comes into play, it creates a thread for every vertex/pixel and bundles them into a package. NVIDIA calls such a package: **Thread Block**. Additional threads may also be created for vertices after tessellation (曲面细分) or for geometry shaders (几何着色器). Thread blocks are then distributed to the **Streaming Multiprocessors**. ![[pipeline_workdistribution_01.webm]]
### 3.6 Vertex Fetch
A Streaming Multiprocessor is a collection of different hardware units and one of them is the **Polymorph Engine**(几何处理引擎). For the sake of simplicity I present them like separate (分离的) guys. The Polymorph Engine gets the needed data and copies it into caches so cores can work faster. Why it is useful to copy data into caches was explained [[1、Verview#1 . Copy the data into system memory for fast access|here]]. ![[pipeline_vertexfetch_01.webm]]
### 3.7 Shader Execution
==The main purpose of the Streaming Multiprocessor is executing program code written by the application developer, also called shaders. ==There is multiple types of shaders but each kind can run on any of these Streaming Multiprocesors and they all follow the same execution logic.

The Streaming Multiprocessor now takes his big Thread Block which he received from the Gigathread Engine (千兆线程引擎) and separates it into smaller chunks（块） of work. He splits the Thread Block into heaps of 32 Threads. Such a smaller heap is called: **Warp**. In total, a Maxwell Streaming Multiprocessor can “hold” 64 of such warps. In my example and Maxwell GPUs there are 32 dedicated cores to work on the 32 Threads. ![[pipeline_workdistribution_02.webm]]
One Warp is then taken to be worked on. At this point the hardware should have all necessary data loaded into the registers so that the cores can work with it. We simplify the illustration here a bit: Maxwell’s Streaming Processor for example has 4 warp schedulers（调度器）, which each would let one warp work and manage a subset of the Streaming Multiprocessor’s warps. ![[pipeline_workdistribution_03.webm]]
The actual work begins now. The cores itself never see the whole shader-code but only **one** command of it at the time. They do their work and then the next command is given to them by the Streaming Multiprocessor. All cores execute the same command but on different data (vertices/pixels). It’s **not** possible that some cores work on command A and some on command B at the same time. This method is called **lock-step**. ![[pipeline_workdistribution_04.webm]]
This lock-step method gets important if you have an IF-statement in your shader code which executes either **one** code block **or** another.
![[pipeline_workdistribution_05.webm]]This IF-Statement makes **some** of our cores execute the left code and some the right code. It can’t be done at the same time (like explained above). First one code-side would be executed and some cores would be “sleeping” and **then** the other side is executed afterwards. [Kayvon explains this here at 43:58 “What about conditional execution?”](http://scs.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=11e89f91-6ae0-44bc-bfc7-cea41b1af542).
GPU 中的 IF 条件不同于 CPU。在 CPU 中，IF 条件只会执行一条分支；而在 GPU 中，IF 条件很有可能两条分支都执行。可以参考知乎上的回答 [《Shader中的条件分支能否节省shader的性能？》](https://www.zhihu.com/question/329084698/answer/717914074)。

In my example 16 pixels/vertices would be worked on but it’s of course possible to have IF-statements where only ONE pixel/vertex is calculated and the other 31 cores get masked out. The same applies to loops, if only one core has to stay in the loop long, all the others become idle. This phenomenon is also called “divergent threads” **（分歧线程）** and should be minimized. Ideally all threads in the warp hit the same side of the IF-condition, because then we can entirely jump over the non-active side. ![[pipeline_workdistribution_06.webm]] But why can the Streaming Processor hold 64 warps, when the cores can only work on very few at a time?? This is because sometimes you can’t progress because you have to wait for some data. For example we need to calculate the lighting with the normal from our normal map texture. Even if the normal was in the cache it takes a while to access it, and if it wasn’t it can take a good while. Pro’s call this **Memory Stall** （内存延迟）and this is greatly [explained by Kayvon](http://scs.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=11e89f91-6ae0-44bc-bfc7-cea41b1af542). Instead of doing nothing, the current warp will just be exchanged with one, where the necessary data is ready for use: ![[pipeline_workdistribution_07.webm]]
The explanation above was a bit simplified. Modern GPU architecture doesn’t _only_ allow a Streaming Processor working at **one** Warp at the time. Look for example [at this image](http://images.bit-tech.net/content_images/2014/02/nvidia-geforce-gtx-750-ti-review/gtx750ti-10b.jpg) showing a Streaming Processor (SMM) based on Maxwell architecture: **One** Streaming Processor has access to **four** Warp schedulers, each controlling 32 Cores. This makes him able to work on four Warps completely **parallel**. The book keeping for the work state of multiple threads is kept independently and is reflected by how many Threads the SM can hold in parallel, as noted on top.
There is more than just waiting for memory that allows us to switch active scheduling as [Guohui Wang](http://www.ece.rice.edu/~gw2/) noted:

> Since more than 4 Warps can run in parallel in Maxwell. Each warp scheduler can perform dual-issuing instruction in one clock clock to a warp, in this sense, every clock cycle we have up to 4 warps get their new instructions to work on (suppose at least 4 warps are ready by far). However, we also have instruction-level parallelism. That means when 4 warps are executing instructions (typically with 10-20 cycle latency), the next batch of 4 warps can accept new instructions in the next clock cycle. Therefore, it is possible to have more than 4 warps running in parallel if the resources are available. Actually, in one of the CUDA optimization video in GTC2013, more than 30 active warps are recommended to keep the pipeline fully occupied in a general case. You may want to revise the wording here to indicate that there will be multiple (more than 4) warps running in parallel, to avoid any potential confusion that people may think 4 scheduler could only hold 4 parallel warps.  
> – Guohui Wang
![[Pasted image 20240704161834.png|475]]

But what are our threads actually working on? For example a **Vertex Shader**!
### 3.8 Vertex Shader

The vertex shader takes care of **one** vertex and modifies it how the programmer wants. Unlike normal software (e.g. Mail-Program) where you run **one** instance of the program and hand over a lot data which get taken care of (e.g. handling all the Mails), you run **one** instance of a vertex shader program **for every** vertex which then runs in in one thread managed by the Streaming Multiprocessor.

Our vertex shader transforms vertices or its parameters (pos, color, uv) like you want: ![[pipeline_vertex_shader_01.webm]]
Some stages are only executed when **Tessellation** is used. Click the link below, if you want to see what happens when Tessellation gets into the game.
### 3.9 Patch Assembly

Until here we only saw **single** vertices. Sure, they came in a specific order send by a programmer but we treated them independently and not as a group. The following sections deal with steps that are **only** done when tessellation shaders are being used. The first of such steps creates patches（面片） from the individual vertices. That way（这样） it is possible to subdivide them and add geometric detail. How many vertices make a patch is defined by the programmer, the maximum is, guess what, 32 vertices.

In OpenGL is this stage called Patch/Primitive Assembly and in DirectX only Patch Assembly (Primitive Assembly comes later). More detailled information about patch/primitive assembly [can be found in [a57]]( http://www.lighthouse3d.com/tutorials/glsl-core-tutorial/primitive-assembly/ ).
![[pipeline_patch_assembly_01.webm]]
### 3.10 Hull Shader
The Hull shader takes all the vertices which belong to the just created patch and calculates a tessellation factor e.g. dependent on the distance to the camera. As the hardware can only tessellate three basic shapes (quad, triangle or a series of lines), the shader code also contains which shape is being used by the tessellator. As a result there is not just a single tessellation factor, but they are computed for each outer side and also a special “inner” side of the shape. To be able to create meaningful geometry later, the Hull Shader also computes the input values for the Domain Shader, which takes care of the positions. ![[pipeline_hull_shader_01.webm]]
### 3.11 Tessellation
Now we know in which shape and how much we want to subdivide the patch – the Polymorph Engine takes this information and does the actual work. Out of this arrive a lot new vertices. These are sent back to the Gigathread Engine to be distributed across the GPU and are handled by the Domain Shader. More information about the shader stages can be found [here [a55]]( http://www.highperformancegraphics.org/previous/www_2010/media/Hot3D/HPG2010_Hot3D_NVIDIA.pdf ) and [here [a79]]( http://www.hotchips.org/wp-content/uploads/hc_archives/hc22/HC22.23.110-1-Wittenbrink-Fermi-GF100.pdf ).
![[pipeline_tesselation_01.webm]]
Here you can find Detailed articles about [Triangle Tesselation](http://prideout.net/blog/?p=48) and [Quad Tesselation](http://prideout.net/blog/?p=49).

You might ask why not directly put the geometry detail into the model. There are two reasons for this. First, you might remember how accessing memory is slow compared to just doing calculations. So instead of having to fetch all those additional vertices with all their attributes (position, normal, uv…), it is better to generate them from less data (patch corner vertices + displacement logic or textures, which support mipmaps, compression…). Second, with tessellation you’re able to adjust the detail depending on the distance to the camera – so you’re very flexible. Otherwise we may compute tons of vertices, that belong to triangles that are not even visible in the end (too small or not in view).

### 3.12 Domain Shader

Now the final position for the generated tessellation vertices are calculated. If the programmer wanted to use a displacement map（置换贴图）, it is applied here. The input of the Domain Shader are the outputs of the Hull Shader (for example the patch vertices) as well as a barycentric coordinate（重心坐标） from the tessellator. With the coordinate and the patch vertices you can compute a new position of the vertex, and you can then apply the displacement to it. Similar to a vertex shader, the Domain Shader computes the data passed to the next shader stages, which can be either the Geometry Shader if active, or the Fragment Shader.
![[pipeline_domain_shader01.webm]]
### 3.13 Primitive Assembly

Towards the end of the geometry pipeline we gather the vertices that assemble our primitive（图元）: a triangle, line or point. The vertices either came from the vertex shader, or if tessellation was active from the domain shader.

What mode (triangle, line or point) we are in was defined in the application for this drawcall. Normally we would just pass the primitive for final processing and rasterzation（光栅化）, but there is an optional stage that makes use of this information, the Geometry Shader. ![[pipeline_primitive_assembly_01.webm]]
### 3.14 Geometry Shader

The Geometry Shader works on the final primitives. Similar to the Hull Shader it gets the primitive’s vertices as input. It can modify those vertices and even generate a few new ones. It can also change the actual primitive mode. For example turn a point into two triangles, or the three visible sides of a cube.

However it is not really good for creating lots of new vertices or triangles, tessellation is best left to the tessellation shaders. Its purpose is rather（相当、十分） special given（过去分词：“被给予/被提供/被设定好的”） it’s the last stage prior to（意思是 **"before"**，但它比 before **更正式、更书面**） preparing the primitive for rasterization. For example it plays a key-role in current [voxelization techniques](https://research.nvidia.com/publication/interactive-indirect-illumination-using-voxel-cone-tracing).

[Here](https://open.gl/geometry) you can find good examples how to program & use geometry shaders. And [this](http://www.lighthouse3d.com/tutorials/glsl-core-tutorial/pipeline33/) is a great overview about the openGL pipeline.
![[pipeline_geometry_shader01.webm]]
### 3.15 Viewport Transform & Clipping

Until here the programmers seem to use a quadratic（二次的） space for all the operations (i guess it’s easier/faster that way) but now this needs to be fit to the actual resolution of your monitor (or window where the game is rendered into). More info about this you can find [here](http://cg.informatik.uni-freiburg.de/course_notes/graphics_01_pipeline.pdf) in the “Viewport Transform / Screen Mapping” Section.
![[pipeline_screenmapping01.webm]] Also triangles get cut if they overlap a certain security-border (Guard Band) of the scene (this is called: Guard Band Clipping and you find more infos [here](http://www.byteboss.com/288180.ppt) and [here](http://developer.download.nvidia.com/assets/gamedev/docs/Guard_Band_Clipping.pdf)). The clipping is done because the Rastizer can only deal with triangles **within** the area it’s working on:
![[pipeline_clipping01.webm]]
### 3.16 Triangles Journey

This is not really a separate step in the pipeline but I found it very interesting so that it gets its own section.

At this point we know the exact position, shading, etc. of several vertices which form triangles. These triangles need to be “painted” and before we can do that, someone has to find out which pixels of the screen are covered by the triangles. This is done by so called rasterizers. It’s important to know, that there are **several** available **AND** several of them can work at the **same** triangle if its big enough. Else it would mean that only **one** rasterizer is working when you have big triangles on screen and the others would have some vacation.

Therefore every rasterizer has the responsibility for certain parts of the screen. And if a triangle belongs to such a responsibility area (the bounding box of the triangle is taken to measure this), it is send to this rasterizer so that he can work on it. ![[pipeline_triangle_journey01.webm]]
### 3.17 Rasterizing

The rasterizer（光栅化器） receives the triangles he’s responsible for and first does a quick check if the triangle even faces forward. If not, it’s thrown away (backface culling). If the triangle is “valid”, the rasterizer creates pre-pixels/fragments by calculating the edges which connect the vertices (edge setup) and so seeing which pixels quads (2×2 pixels) belong to the triangle.
![[pipeline_rasterizing01.webm]] If you’re really into rasterizing and micro-triangles, you definitely should [check out this presentation](http://attila.ac.upc.edu/wiki/images/9/95/CGI10_microtriangles_presentation.pdf). And [this article](http://www.lighthouse3d.com/tutorials/glsl-tutorial/rasterization-and-interpolation/) gives a good overview about it.
After the pre-pixels/fragments are created, there’s a check if they would be even visible (or hidden by already rendered stuff):

> Pixels produced by the rasterizer are sent to the Z-cull unit. The Z-cull unit takes a pixel tile and compares the depth of pixels in the tile with existing pixels in the framebuffer. Pixel tiles that lie entirely behind framebuffer pixels are culled from the pipeline, eliminating the need for further pixel shading work.  
> – [NVIDIA GF100 Whitepaper](http://www.hardwarebg.com/b4k/files/nvidia_gf100_whitepaper.pdf)

### 3.18 Pixel Shader/Fragment Shader

Fragment Shader 和 Pixel Shader指的是同一个可编程阶段，只是“学名”和“俗名”不同。

After the pre-pixels/fragments are generated they can be “filled”. For every pre-pixel/fragment a new thread is generated and again distributed to all the available cores (like it was done with all the vertices).

“Again we batch up 32 pixel threads, or better say 8 times 2×2 pixel quads, which is the smallest unit we will always work with in pixel shaders.” ![[pipeline_workdistribution_03 1.webm]]
When the cores are done with their work, they write the results into the registers from where they are taken and put into the caches for the last step: Raster Output (ROP).

### 3.19 Raster Output

The final step is done by the so called “Raster Output” Units which move the final pixel data (just got from the pixel shader) from L2 cache into the framebuffer which lays around in the VRAM. The GF100 as an example has 48 such ROPs and I interpret the dataflow (from L2 cache to VRAM) based on that they are placed really near to each other:

> “[…] L2 cache, and ROP group are closely coupled […]”  
> – [NVIDIA GF 100 Whitepaper](http://www.hardwarebg.com/b4k/files/nvidia_gf100_whitepaper.pdf)

Besides of just moving pixel data, the ROPs also take care of pixel blending, coverage information for anti aliasing and “atomic operations（原子操作）”.
![[pipeline_rop_01.webm]] What a ride, it took a long time to bring all the information together so I hope you found this book useful.