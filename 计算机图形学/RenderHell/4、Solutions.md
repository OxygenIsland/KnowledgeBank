---
title: "[[4、Solutions]]"
type: Reference
status: todo
Creation Date: 2026-06-09 17:36
tags:
---
Now it gets interesting! Here I will present you some solutions i found during my research. This hopefully gives you an idea how an asset should be optimized to be well renderable.
## 1. Sorting  
Firstly you can sort all your commands (e.g. by render state) before you fill the command buffer. This would reduce the necessary state changes to the minimum since you go through all meshes of the same kind before changing the state.![[optimisation_sorting_01.webm]]
But you would still create a lot overhead by rendering every mesh one after another. To reduce this overhead, a technique called **Batching** seems to be useful.

## 2. Batching  
When sorting your meshes, you kind of pile them together to heaps of the same kind. The next step would be, to tell the GPU to render such a heap at once. This is what batching is about:
> [!quote]+ 
> “‘Batching’ means to group some meshes together before calling the API to draw them. This is why it takes less time to render a big mesh than multiple small meshes.” [a36]

So, **instead** of using one draw call per mesh (which share the same render state)…

![[optimisation_batching_01.mp4]]
…you would combine the meshes (with the same render state) and render them as one draw call. This is a **really** interesting topic because you can render **different** meshes (stone, chair or a sword) **at once** as long as they use the same render states (which basically means that the use the same material setup).

![[optimisation_batching_02.webm]]

It’s important to mention, that you combine the meshes in the system memory (RAM) and then send the newly created big mesh to the graphic card’s memory (VRAM). This takes time! Therefore batching is good for static objects (stones, houses, …) which you combine once and let them stay in the memory for long time.  
You can also batch together dynamic objects like for example laser-bullets in a space game. But since they’re moving you would have to create this bullet-cloud-mesh every frame and send it to the GPU memory!

Another point why you have to be careful (thx [koyima for mentioning](http://www.reddit.com/r/gamedev/comments/2djgnx/what_are_draw_calls_why_do_you_care_what_makes/cjqcd2j)): If an object isn’t in the camera frustum, you can just cull (ignore it for the rendering). But if you batch together several objects, you have to consider the whole new big mesh while rendering (even if only a small part of it is actually visible). This might decrease performance in some cases.

A better solution for handling **dynamic** objects is **Instancing**.

## 3. Instancing  
Instancing means, that you send only one mesh (e.g. a laser bullet) instead of many and let the GPU duplicate it several times. Having the same object at exact the same position with the same rotation or animation would be a bit boring. Therefore you can provide a stream of extra data like the transformation matrix to render the duplicates at different positions (and in different poses).
> [!quote]+ 
> Typical attributes per instance are the model-to-world transformation matrix, the instance color, and an animation player providing the bones used to skin the geometry packet.” [a37]

Don’t nail me down on that, but as far as i know, is this data stream just a list in the RAM where the GPU has access to.

This would result in only one draw call per mesh type! The difference in comparison to Batching is, that all instances look the same (because they’re copies of the same mesh) while a batched mesh can consist of several different meshes as long as they use the same render state parameters.![[optimisation_instancing_01.webm]]
Now it gets a bit more creative. I think the following tricks are very cool, even if they are only suitable for special cases:

## 4. Multi-Material-Shader  
A shader can access several textures and therefore it’s possible to not only have one diffuse/normal/specular/… map but e.g. two of them – which basically means, that you have two materials combined in one shader. The materials are blended into each other controlled by a blend-texture. Of course, this cost’s GPU power because the blending is expensive, but it reduces the draw call count because a mesh with two or more materials would **not** be ripped into pieces anymore (explained under “4. Meshes and Multi-Materials”).

## 5. Skinned Meshes  
Do you remember the laser-bullet-mesh i talked about? I said that this mesh would have to be updated every frame since the bullets constantly move. Batching them together and sending the resulting mesh every frame would be expensive.  
An interesting approach to this problems is to automatically add a bone to every bullet and give it skinning information. With that you would have one big mesh which could stay in the memory and you would only update the bone data for every frame. Of course, if a new bullet as shot or an old gets destroyed, you would have to create a new mesh. But it sounds like a really interesting idea to me.

## 6. Reduce Overdraw
Alex mentioned a nice approach which he used for his [App](https://play.google.com/store/apps/details?id=org.androidworks.livewallpaperstonesfree) to avoid too much overdraw while rendering a vignette:
> [!quote]+
> To reduce overdraw for full-screen vignette (which is usually made with full-screen quad and translucent texture) we’ve made it with quad mesh but hollow inside (where it is 100% transparent) and used vertex colors instead of texture. This results in even better looking vignette (no texture compression artifacts) and better performance (less overdraw – it is drawn only in opaque parts).  
– [Alex / Axiomworks](http://androidworks-kea.blogspot.de/)

![[Pasted image 20260609174417.png]]

Also the CryEngine Documentation speaks about it [here](http://docs.cryengine.com/display/SDKDOC2/Getting+Started+Modeling#GettingStartedModeling-TexturingandUVWs) and [this thread](http://www.polycount.com/forum/showthread.php?t=89154) is also really useful to read.

## 7. And a lot more magic

Graphics programming is in constant movement, APIs and hardware evolves, writing efficient render engines that can deal with a lot of use-cases is not easy and it needs lots of sophisticated engineering. Luckily many game developers are open to sharing some of their lessons learned and one can find interesting information about effects or rendering architecture at various events or developer websites (siggraph advanced real-time rendering course, unreal engine documentation and source code, frostbite engine presentations…). All major hardware vendors also typically have documentation, sample code or presentations on how to leverage graphics APIs and the hardware well.

The benefit today is that thanks to plenty rendering middleware, a lot of the heavy lifting is done already. For artists it is therefore mostly about knowing what optimizations they actually have to care for when making the content, as some things might be done under the hood anyway.

