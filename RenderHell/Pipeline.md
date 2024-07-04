## Pipeline in Detail
Most of the constructive feedback I received about this article was “Nice explanation, but your pipeline is 6 years old!”. I wasn’t sure what that exactly meant until [Christoph Kubisch](https://twitter.com/pixeljetstream) joined my fight in the Render Hell. He is a Developer Technology Engineer working for [NVIDIA](http://www.nvidia.com/) and whatever question I had, [he answered it](https://developer.nvidia.com/content/life-triangle-nvidias-logical-pipeline). And believe me, I had a lot! 😀

Two **major** points of the pipeline will be explained below, which **weren’t** totally wrong explained [here in book I](http://simonschreibt.de/gat/renderhell-book1), but might not be clear enough:
1. **Not** everything is done by the “tiny” GPU cores!  
2. There can be **several parallel** running pipelines!
## 1 . Not everything is done by the “tiny” GPU cores!
In the pipeline example above it might seem like every pipeline stage is done by the GPU Cores – This is **NOT** the case! In fact, most of the stuff is **not** done by them. In the new section in [[Verview#1 . Copy the data into system memory for fast access|1. Copy the data into system memory for fast access]] you already saw that several components are necessary to just bring the data to a core. So what work do the cores actually do?
Let’s observe one:
![[gpu_core_exhibitionist_01.webm]]
A core can receive commands and data. Then it executes the command by calculating the data in a floating point unit (FP UNIT) **or** an integer unit (INT UNIT). So you could say: A core can calculate pixels and vertices (maybe also other calculations like physics but let’s focus on graphic rendering).

Other important stuff like distribute the render-tasks, calculate tessellation, culling and preparing the fragments for the pixel shader, depth testing and writing pixels into the frame buffer are **NOT** done by the cores. This work is done by special, **not** programmable hardware blocks which are also placed in the GPU.

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
The driver receives the commands from the application and puts them into a [[Verview#5 . Command Buffer|command buffer]]. After a while (or when the programmer forces it), the commands are send to the GPU.
![[pipeline_driver_stage_01.webm]]
### 3.4 Read commands
Now we’re **on the graphic card**! The **Host Interface** reads commands to make them available for further use.
![[pipeline_readcommands_stage_01.webm]] 
### 3.5 Data Fetch
Some of the commands sent to the GPU can contain data or are instructions to copy data. The GPU typically has a dedicated engine to deal with copying data from RAM to VRAM and vice versa. This data could be anything filling vertex buffers, textures or other shader parameter buffers. Our frame would typically start with some camera matrices being sent.
![[pipeline_datafetch_stage_01.webm]]
**Important:**
1. I symbolize the data as geometries but in fact we’re talking just about vertex-lists (vertex buffer). For a long time the rendering process doesn’t care about the final model. Instead, most of the time, only single vertices/pixels are worked with.
2. Textures **only** get copied, if they’re not **already** in the VRAM on the graphic card!
3. If vertex buffer are used a lot, they can stay in the VRAM like textures and don’t have to be copied with every draw call
4. Vertex buffers **may** stay in the RAM (not VRAM) if they change a lot. Then the GPU can read the data directly from RAM to its Caches.

Now that all ingredients are ready the Gigathread Engine comes into play, it creates a thread for every vertex/pixel and bundles them into a package. NVIDIA calls such a package: **Thread Block**. Additional threads may also be created for vertices after tessellation or for geometry shaders (will be explained later). Thread blocks are then distributed to the **Streaming Multiprocessors**. ![[pipeline_workdistribution_01.webm]]
## 3 .6 Vertex Fetch

A Streaming Multiprocessor is a collection of different hardware units and one of them is the **Polymorph Engine**. For the sake of simplicity I present them like separate guys. :) The Polymorph Engine gets the needed data and copies it into caches so cores can work faster. Why it is useful to copy data into caches was explained [here in book I](http://simonschreibt.de/gat/renderhell-book1#update12-1). ![[pipeline_vertexfetch_01.webm]]
## 3 .7 Shader Execution
The main purpose of the Streaming Multiprocessor is executing program code written by the application developer, also called shaders. There is multiple types of shaders but each kind can run on any of these Streaming Multiprocesors and they all follow the same execution logic.

The Streaming Multiprocessor now takes his big Thread Block which he received from the Gigathread Engine and separates it into smaller chunks of work. He splits the Thread Block into heaps of 32 Threads. Such a smaller heap is called: **Warp**. In total, a Maxwell Streaming Multiprocessor can “hold” 64 of such warps. In my example and Maxwell GPUs there are 32 dedicated cores to work on the 32 Threads. ![[pipeline_workdistribution_02.webm]]
One Warp is then taken to be worked on. At this point the hardware should have all necessary data loaded into the registers so that the cores can work with it. We simplify the illustration here a bit: Maxwell’s Streaming Processor for example has 4 warp schedulers, which each would let one warp work and manage a subset of the Streaming Multiprocessor’s warps. ![[pipeline_workdistribution_03.webm]]
The actual work begins now. The cores itself never see the whole shader-code but only **one** command of it at the time. They do their work and then the next command is given to them by the Streaming Multiprocessor. All cores execute the same command but on different data (vertices/pixels). It’s **not** possible that some cores work on command A and some on command B at the same time. This method is called **lock-step**. ![[pipeline_workdistribution_04.webm]]
This lock-step method gets important if you have an IF-statement in your shader code which executes either **one** code block **or** another.
![[pipeline_workdistribution_05.webm]] This IF-Statement makes **some** of our cores execute the left code and some the right code. It can’t be done at the same time (like explained above). First one code-side would be executed and some cores would be “sleeping” and **then** the other side is executed afterwards. [Kayvon explains this here at 43:58 “What about conditional execution?”](http://scs.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=11e89f91-6ae0-44bc-bfc7-cea41b1af542).

In my example 16 pixels/vertices would be worked on but it’s of course possible to have IF-statements where only ONE pixel/vertex is calculated and the other 31 cores get masked out. The same applies to loops, if only one core has to stay in the loop long, all the others become idle. This phenomenon is also called “divergent threads” and should be minimized. Ideally all threads in the warp hit the same side of the IF-condition, because then we can entirely jump over the non-active side. ![[pipeline_workdistribution_06.webm]] But why can the Streaming Processor hold 64 warps, when the cores can only work on very few at a time?? This is because sometimes you can’t progress because you have to wait for some data. For example we need to calculate the lighting with the normal from our normal map texture. Even if the normal was in the cache it takes a while to access it, and if it wasn’t it can take a good while. Pro’s call this **Memory Stall** and this is greatly [explained by Kayvon](http://scs.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=11e89f91-6ae0-44bc-bfc7-cea41b1af542). Instead of doing nothing, the current warp will just be exchanged with one, where the necessary data is ready for use: ![[pipeline_workdistribution_07.webm]]
The explanation above was a bit simplified. Modern GPU architecture doesn’t _only_ allow a Streaming Processor working at **one** Warp at the time. Look for example [at this image](http://images.bit-tech.net/content_images/2014/02/nvidia-geforce-gtx-750-ti-review/gtx750ti-10b.jpg) showing a Streaming Processor (SMM) based on Maxwell architecture: **One** Streaming Processor has access to **four** Warp schedulers, each controlling 32 Cores. This makes him able to work on four Warps completely **parallel**. The book keeping for the work state of multiple threads is kept independently and is reflected by how many Threads the SM can hold in parallel, as noted on top.
There is more than just waiting for memory that allows us to switch active scheduling as [Guohui Wang](http://www.ece.rice.edu/~gw2/) noted:

> Since more than 4 Warps can run in parallel in Maxwell. Each warp scheduler can perform dual-issuing instruction in one clock clock to a warp, in this sense, every clock cycle we have up to 4 warps get their new instructions to work on (suppose at least 4 warps are ready by far). However, we also have instruction-level parallelism. That means when 4 warps are executing instructions (typically with 10-20 cycle latency), the next batch of 4 warps can accept new instructions in the next clock cycle. Therefore, it is possible to have more than 4 warps running in parallel if the resources are available. Actually, in one of the CUDA optimization video in GTC2013, more than 30 active warps are recommended to keep the pipeline fully occupied in a general case. You may want to revise the wording here to indicate that there will be multiple (more than 4) warps running in parallel, to avoid any potential confusion that people may think 4 scheduler could only hold 4 parallel warps.  
> – Guohui Wang
![[Pasted image 20240704161834.png|475]]

But what are our threads actually working on? For example a **Vertex Shader**!
## 3 .8 Vertex Shader

The vertex shader takes care of **one** vertex and modifies it how the programmer wants. Unlike normal software (e.g. Mail-Program) where you run **one** instance of the program and hand over a lot data which get taken care of (e.g. handling all the Mails), you run **one** instance of a vertex shader program **for every** vertex which then runs in in one thread managed by the Streaming Multiprocessor.

Our vertex shader transforms vertices or its parameters (pos, color, uv) like you want: ![[pipeline_vertex_shader_01.webm]]
