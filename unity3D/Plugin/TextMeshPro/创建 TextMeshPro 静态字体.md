---
title: "[[创建 TextMeshPro 静态字体]]"
type: Literature
status: done
Creation Date: 2024-04-03 15:07
tags:
  - unity
  - 插件
---
## 1、在 Unity 中新建一个文件夹，用来存储字体，并把你想要转换的中文字体放进去。比如微软雅黑等。
## 2 、打开 Font Asset Creator 窗口： Window > TextMeshPro > Font Asset Creator.
	![[Pasted image 20240403151325.png|500]]
## 3 、Font Asset Creator 窗口如下，选项很多，接下来逐一解释一下。
	![[Pasted image 20240403151409.png|450]]
3.1. Source Font File: 选择你刚才放到 Unity 里面的中文字体。
Sampling Point Size / Font Size: 创建字体时采样的 SDF（符号距离字段）准确性（翻译自英文文档，我也不太懂。）默认是 Auto Size，会尝试使用字体中的所有字符。当然数值越高越好，一般来说 50 to 70 为宜。注意，过大的数值会导致一些字符采不到。我就是用的默认 Auto Size

Padding: 字体中效果 (outlines, glow, bevels, etc.) 的大小。一般来说，最好和 sampling size 的比例为 1:10。如 sampling size 为 60 时，padding size 最好取 6。当然你也可以尝试更改这个比例，可能会产生意想不到的效果。我使用的默认5.

Packing Method: 创建字体的方式。Fast 可用于快速预览效果，Optimum 用于创建最终字体。

Atlas Resolution: 可以理解为分辨率。对于面向手机等移动端的项目，你应该设置为 2048 x 2048。面向电脑端的数值官方没说，我猜是 4096 x 4096，我试了一下效果还行。

Character Set: 你创建的字体的字符范围，也就是说你要创建的 TextMeshPro 字体中，要包含的所有字符。在我们这里就是所有的中文字符。一般来说常见中文字+英文单词+符号即可。
下拉选择 Characters from File，然后选择包含所有所需字符的 txt 文件（需要先导入 Unity）。
![[Pasted image 20240403151745.png|500]]
这样能够基本满足任何使用场景，但是这样创建的 TextMeshPro 文件会较大，我创建的有33MB。为了减小文件大小，你可以下拉选择 Custom Characters，填入你项目中需要用到的所有字体。
![[Pasted image 20240403153347.png|475]]
同理，如果你的项目中包含一些生僻字，可以选择 Custom Characters，然后复制填入上面下载的文件中的所有内容，再输入你需要用到的生僻字，如：龓。
**Render Mode:** 渲染模式。在仍然支持光栅化位图处显示文本时，除非您在1：1的比率上呈现小字体（即，10pt 字体在屏幕上呈现10px），否则使用 SDF 模式。
1. **SDFAA_HINTED（带有字形提示的带符号距离场抗锯齿）**：该模式使用带有字形提示的带符号距离场（Signed Distance Field）纹理进行渲染。它提供了高质量的抗锯齿效果，即使在小字号下也能保持清晰的渲染效果。字形提示确保了字符在小字号下保持形状和清晰度。
    
2. **SMOOTH_HINTED（带有字形提示的平滑抗锯齿）**：该模式使用带有字形提示的平滑抗锯齿进行渲染。与SDFAA_HINTED类似，但可能会在一定程度上牺牲一些锐度以获得更平滑的边缘。
    
3. **SDFAA（不带字形提示的带符号距离场抗锯齿）**：该模式使用不带字形提示的带符号距离场纹理进行抗锯齿渲染。与带提示的模式相比，字符在小字号下可能显得略不清晰，但保持了较为平滑的边缘。
    
4. **SMOOTH（不带字形提示的平滑抗锯齿）**：该模式提供不带字形提示的平滑抗锯齿渲染。它可能会导致字符边缘更为柔和，尤其在小字号下。
    
5. **NORMAL_HINTED（带有字形提示的标准抗锯齿）**：该模式使用标准抗锯齿和字形提示进行渲染。它提供了标准的抗锯齿渲染，并应用字形提示以保持字符的清晰度。
    
6. **NORMAL（不带字形提示的标准抗锯齿）**：该模式提供不带字形提示的标准抗锯齿渲染。它在字符渲染中平衡了锐度和平滑度。

Get Kerning Pairs: TextMesh Pro can optionally use the kerning information embedded in the font, if available.

Generate Font Asset: 生成 TextMeshPro 中文字体。点击后开始生成文件。完成后保存。然后在你的 TextMeshPro 中选择刚才生成的文件即可：
![[Pasted image 20240403154626.png|475]]
