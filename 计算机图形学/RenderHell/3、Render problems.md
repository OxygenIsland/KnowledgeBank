---
title: "[[3、Render problems]]"
type: Reference
status: ing
Creation Date: 2026-06-09 16:51
tags:
---
Welcome to the 3rd book! Here we’ll checkout some problems which can occur during the rendering process. But first, some practice:
To know about a problem is useful. To actually **feel** the problem is even better for understanding. So let’s try to feel like a CPU/GPU.
## Experiment
Please create 10.000 small files (e.g. 1 KB each) and copy them from one hard drive to an other. It will take a long time even if the data amount is just 9,7 MB in total.
![[windows_copy_dialog_01.gif]]
Now create a single file with a size of 9,7 MB and copy it the same way. It will go a lot faster!

That’s right but for **every** copy-action there’s some stuff to do, for example: prepare the file transfer, allocate memory, read/write heads move back and forth in the HDD, … which is overhead for **every** write action. As you painful feel, this overhead is immense if you copy a lot small files. Rendering many meshes (which means executing many commands) is a lot more complex, but it feels similar.

![[windows_copy_dialog_02.gif]]
Let’s now have a look at the worst case you can get during the rendering process.
## Worst Case  
To have many small meshes is bad. If they’re using **different** material parameters on them, it gets even worse. But: Why?
### 1. Many Draw Calls
>Very often the GPU can render such small meshes faster than the CPU can send commands. Our application code doesn’t “just” send commands to GPU directly, there is some graphics API, driver, and operating system layers in between. Those add up to the cost for the CPU.

> [!quote]+ 
> “The main reason to make fewer draw calls is that graphics hardware can transform and render triangles much faster than you can submit them. If you submit few triangles with each call, you will be completely bound by the CPU and the GPU will be mostly idle. The CPU won’t be able to feed the GPU fast enough.” [f05]

![[commandbuffer_communication_cpubound.webm]]
In addition, every draw call produces some kind of overhead (like mentioned above):

> [!quote]+ 
> “There is driver overhead whenever you make an API call, and the best way to amortize this overhead is to call the API as little as possible.” [a02]

This overhead is now much lower on console APIs or the new APIs (DirectX12, Vulkan, Metal). It’s still best to make big work submissions, than small ones, but it’s not as bad as in the past.

More Details here: [NVIDIA OpenGL extension showcasing perf benefits of new concepts in APIs](http://on-demand.gputechconf.com/gtc/2015/presentation/S5135-Christoph-Kubisch-Pierre-Boudier.pdf)

### 2. Many Commands

>One example for such an overhead is the communication of CPU with GPU. Do you remember that the CPU fills the command buffer and the GPU reads from it? Well, they have to communicate about the changes and this creates overhead too (they do this by updating read/write pointers – [read more about it here](http://traxnet.wordpress.com/2011/07/18/understanding-modern-gpus-2/))!  Therefore the driver batches up several commands in something called a push-buffer, it does not hand over one command after another but first fills up this buffer and then hands over a complete chunk of commands to the GPU.
![[commandbuffer_communication_chunk.webm]]

The GPU would (hopefully) have stuff to do (e.g. working on the last chunk of commands) while the CPU builds up the new command buffer. To avoid that the GPU has to wait until the next chunk of work is ready, the driver has some heuristics around the size of the chunks, and sometimes it queues up more than an entire frame until really sending off the work.  
You can find the settings for this buffering in the control panel of the graphics driver (“maximum pre-rendered frames”). The down-side of high amount of frames, is that it we essentially render further in the “past”, our CPU frame already has the latest player input data, but our GPU renders something that is some frames in past. This added latency can be bad for certain content (virtual reality…).

Modern or console graphics APIs also allow you to fill several command buffers in parallel and the driver hands them over to the GPU one after another (serial submission queue).  
The key difference of DirectX 12’s vs DirectX 11’s command-buffers is essentially that the parallel built command-buffers are now created in such a way that makes them super quick to submit by the driver later. While in DirectX 11 the driver still had to do more tracking of things in the serial submission, which reduced the benefit of building in parallel.

We only spoke about many meshes with **the same** material parameters (render state). But what happens when you want to render meshes with different materials?

### 3. Many Meshes and Materials
Flush the pipeline.

> [!quote]+ 
> “When changing the state, there is sometimes a need to wholly or partially flush the pipeline. For this reason, changing shader programs or material parameters can be very expensive […]” [b01 page 711/712]

You thought it can’t get worse? Well … if you have different materials on different meshes, you may introduce additional setup time on both CPU and GPU. You set a render state for the first mesh, command to render it, set a new render state, command the next mesh-rendering and so on.

![[commandbuffer_communication_statechanges.webm]]

I colored the “change state” commands in red because a) they can be expensive and b) for better overview.  
Setting the render state sometimes results (not always, depends on what parameters you want to change and the available units on a GPU) in a “flush” of some parts of the pipeline. This means: every mesh which is currently processed by some hardware units (with the current render state) has to be finished before new meshes can be rendered (with the new render state). It would look like in the image above. Instead of taking a huge number of vertices (e.g. when you combine several meshes of the same render state – an optimization I’ll explain later), you would render a small amount before changing the render state which – this should be clear by now – is a bad thing.

As has been mentioned before, the majority of state-change costs came from the older graphics APIs on the CPU-side. Because of that minimum time for setting up a draw call (independent of the given mesh complexity, but depending on the API and operating system), you can assume that there is **no** difference in rendering 2 or 200 triangles. The GPU is crazy fast so it can render many of those meshes actually faster than the time it took to prepare them on the CPU.

This “rule” changes of course when we talk about combining several small meshes into one big mesh (we’ll look at this in a second).
![[commandbuffer_communication_polysweetspot.webm]]

### 4. Meshes and Multi-Materials
What when not only one material is assigned to a mesh but two or more? Basically, your mesh is ripped into pieces and then fed piece by piece into the command buffer.
![[copy_data_from_hdd_to_ram_vram_01_multimaterial 1.webm]]
This of course creates one draw call per mesh piece.

![[commandbuffer_communication_multimaterial.webm]]
### 5. Single Graphics Command Processor

Typical GPUs today have a single command processor / front-end for graphics. That means even with parallel “chunk” submission from the CPU, all graphics-related commands will be processed in serial once before they are distributed to the many parallel units on the GPU. More about how the GPU works in the [in-depth book in Book 2](http://simonschreibt.de/gat/renderhell-book2).

### 6. Thin Triangles
The rasterizing process may (depending on the hardware) have performance-related details which I already teased in [Book II “3.16 Rasterizing”](http://simonschreibt.de/gat/renderhell-book2):

Most current graphics hardware shades 2×2 quads belonging to one triangle (on NVIDA hardware this would be 8 such quads = 32 threads in one group).
![[pipeline_rasterizing02.webm]]

If some of those fragments don’t cover the triangle, their outputs will simply be ignored.

![[pipeline_rasterizing03.webm]]

You can imagine why something like long thin triangles are really bad for the hardware. because tons of those quads will have only a single of those 4 threads actually computing a pixel. It goes even so far that for very costly fullscreen post processing effects, we don’t render them as two triangles, but a giant triangle whose corners are outside of the view, so that only the area without any diagonals running through the screen is visible.

### 7. Useless Overdraw

A lot performance may be wasted when polygons are rendered with soft-alpha and big areas of the texture are 100% transparent. This may happen when you have a branch/leaf-texture or if you use a full-screen quad to render a vignette (which only darkens the image in the corners).

A solution to this problem will be presented in [Book IV – “Solutions”](http://simonschreibt.de/gat/renderhell-book4#update12-4).
### 8. Mobile vs. PC

A lot of mobile devices are good with blending and anti-aliasing, while more challenged with lots of geometry. In contrast desktop/console GPUs are a bit on the opposite end. The reason is that mobile GPUs use “on-die/on-chip memory” (those tiny caches) as intermediate frame-buffer (Xbox360 also had this). Hence they can do blends very quickly and also anti-aliasing at relatively lower performance hit.  
However, the amounts of memory needed to render in full HD would be way too expensive to have on chip, so they render the frame not in one go, but in little tiles (or chunks). One tile at a time the scene is rendered and after each tile is done, it is copied from the tile cache to the final frame-buffer memory. This is also more power-efficient than copying to frame-buffer memory directly as desktop GPUs do.  
The downside is that they have to process the geometry multiple times, as it may overlap several of the tiles. Which means lots of vertices become more costly.  
However, this approach works great for UI and text rendering (textured quads) with lots of blending, which is a dominant task for mobile devices.

I hope i could give you a small insight of what is bad about a lot meshes and materials. Let’s now look at some solutions because even all of this sounds really really bad: There are beautiful games out there which means that they solved the mentioned problems somehow.