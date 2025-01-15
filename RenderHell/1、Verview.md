---
title: "[[1、Verview]]"
type: Literature
status: todo
Creation Date: 2024-07-03 17:58
tags:
---
Artists must be strong now: From a computers perspective, your assets are just lists of vertex- and texture data. Converting this raw data into a next-gen image, is mainly done by your system processor (**CPU**) and your graphics processor (**GPU**).
## 1 . Copy the data into system memory for fast access
At first all necessary data is loaded from your hard drive (**HDD**) into the system memory (**RAM**) for faster access. Now the necessary meshes and textures are loaded into the memory on the graphic card (**VRAM**). This is because the graphic card can access the VRAM (显存) a lot faster. ![[copy_data_from_hdd_to_ram_vram_01.webm]] If a texture isn’t needed anymore (after loading it into the VRAM), it can be thrown out of the RAM (but you should be sure, that you won’t need it again soon, because reloading it from HDD costs a lot time). The meshes should stay in the RAM because it’s most likely that the CPU wants to have access to them e.g. for collision detection.(碰撞检测)
![[delete_data_in_ram.webm]]
Now the data is on the graphic card (in the VRAM). But the transfer speed from VRAM to GPU is still too slow. The GPU can work a lot faster than the data can be delivered.
Therefore the hardware engineers put small memory **directly inside** the processor chips, typically called ==on-chip caches==. It’s not a lot of memory because it’s crazy expensive to put it inside the processor chip. The GPU copies currently necessary data in small portions there.
![[copy_data_from_vram_to_l2_01.webm]]
Our copied data lays in the so called L 2 Cache now. This is basically a small memory (on NVIDIA GM 204: 2048 KB) which sits on the GPU and can be accessed faster than the VRAM.
But even this is too slow to work efficient! So there’s an even smaller L 1 cache (on NVIDIA GM 204: 384 KB (4 x 4 x 24 KB)) which sits not only on the GPU but even NEARER to its cores!
![[copy_data_from_l2_to_l1_01.webm]]
Plus, there’s another memory which is reserved for input and output data for the GPU Cores: registers（寄存器） or register file（寄存器堆）. From here the GPU Cores take e.g. two values, calculate them and put the result into a register (which is basically a memory address in the register file):

The results in the registers are then taken and stored back into L1/L2/VRAM to have space for new values in the register file. As a programmer you normally don’t have to worry too much about that stuff.
![[copy_data_from_l1_to_register_01.webm]]
Before the render-party can start, the CPU sets some global values which describe **how** the meshes shall be rendered. This value collection is called **Render State**.
## 2. Set the Render State
A render state is kind of a global definition of **how** meshes are rendered. It contains information like:

> “vertex and pixel shader, texture, material, lighting, transparency, etc. […]” [b01 page 711]

==**Important:**== Each mesh, which the CPU commands the GPU to draw, will be rendered under these conditions! You can render a stone, a chair or a sword – they all get the same render values assigned (e.g. the material) if you don’t change the render state before rendering the next mesh. ![[renderstate.webm]]After the preparation is done, the CPU can finally call the GPU and tell it what to draw. This command is known as: ==**Draw Call**==.
## 3 . Draw Call  
A draw call is a command to render **one** mesh. It is given by the CPU. It is received by the GPU. The command only points to a mesh which shall be rendered and **doesn’t** contain any material information since these are already defined via the render state. The mesh resides at this point in the memory of your graphic card (VRAM).
![[cpu_calls_gpu.webm]]
After the command is given, the GPU takes the render state values (material, textures, shader, …) and all the vertex data to convert this information via some code magic into (hopefully) beautiful pixels on your screen. This conversion process is also known as ==**Pipeline**==.
## 4. Pipeline
As i said at the beginning, an asset is more or less just a list of vertex- and texture data. To convert those into a mind blowing image, the Graphic Card has to create triangles out of the vertices, calculate how they are lit, paint texture-pixels on them and a lot more. These actions are called states， Pipeline states.  
Depending on where you read, you’ll find that most of the stuff is done by the GPU. But sometimes they say, that for example the triangle creation & fragment creation is done by other parts of the graphic card.
Here are some example steps the hardware does for **one** triangle:
![[pipeline_overview.webm]]
Rendering is basically doing an immense (庞大) number of small tasks such as calculate something for thousands of vertices or painting millions of pixels on a screen. At least in (hopefully) 30fps.

It’s necessary to be able to compute a lot of that stuff **at the same time** and not every vertex/pixel one after another. In the good old days（早些年）, processors had only one core and no graphic acceleration – they could only do one thing at the same time. The games looked … retro. Modern CPUs have 6-8 cores while GPUs have several thousands (they aren’t that complex like CPU-Cores, but perfect for pushing through a lot vertex and pixel data).

现代的 CPU 有4-8个 Core，每个 Core 可以同时执行4-8个浮点操作，因此我们假设 CPU 有64个浮点执行单元，然而 GPU 却可以有上千个这样的执行单元。仅仅只是比较 GPU 和 CPU 的 Core 数量是不公平的，因为它们的职能不同，组织形式也不同。GPU 厂商倾向于使用 Core 作为最小的执行单元，而 CPU 厂商则倾向于使用更高级的单元。在 Book II 中将会阐述 GPU 内部由高到低执行单元组织形式的更多细节。

When data (e.g. a heap of vertices) is put into a pipeline stage, the work of transforming the points/pixels is divided onto several cores, so that a lot of those small elements are formed parallel (并行的) to a big picture:
![[pipeline_overview_multicore.webm]]
Now we know, that the GPU can work on stuff in parallel. But what’s about the communication between CPU and GPU? Does the CPU has to wait until the GPU finished the job before it can receive new commands?
![[tut_cpu_commands_gpu_zzz.gif|500]]
<font color=Blue size=10>NO!</font>
Thankfully not! The reason is, that such a communication would create bottlenecks (瓶颈) (e.g. when the CPU can’t deliver commands fast enough) and would make parallel working impossible. The solution is a list where commands can be added by the CPU and read by the GPU – independent from each other! This list is called: **Command Buffer**.
## 5 . Command Buffer
The command buffer makes it possible that CPU and GPU can work independent from each other. When the CPU wants something to be rendered, it can push that command into the queue and when the GPU has free resources, it can take the command out of the list and execute it (but the list works as a [FIFO](http://en.wikipedia.org/wiki/FIFO) – so the GPU can only take the oldest item in the list (which was first/earlier added than all others) and work on that).
![[commandbuffer_communication.webm]]==By the way: there are different commands possible. One example is a draw call, another would be to change the render state.==

That’s it for the first book. Now you should have an overview about asset data during rendering, draw calls, render states and the communication between CPU and GPU.
