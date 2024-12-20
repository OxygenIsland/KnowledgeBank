
![[Pasted image 20241113095226.png]]
为了使机器人获得足够的经验，仿真环境肯定越丰富越好，李飞飞团队提出了一个数字表亲的概念，用来泛化机器人的仿真训练环境，比如说.
对于 3 DGS 环境来说，要想实现局部地图的裁剪替换更新，除了需要获得局部地图的语义信息和位姿信息，还需要对裁剪后的 mesh 和 nerf 的画面进行处理，比较复杂，我这边只讨论一个简单的 pipeline，就是获取 3 DGS 场景中单个物体实例的语义信息、位置信息 position 还有物体正面的一个大概方向，这样可以让机器人对场景有一个大概的理解
## 一个简单的 pipeline
目标：希望可以获取到 3DGS 场景中物体实例的信息（包括语义信息、位置信息、和物体的一个大概的朝向信息）
目前 3 DGS 地图的语义层中，虽然没有对场景进行分割，但是也对场景进行了理解，包含了前两个信息
![[Pasted image 20241120110518.png|500]]
mesh 网格相对于点云信息来说损失了很多细节，所以用 mesh 来判断物体朝向，从而给一个推荐的正方向是比较困难的，点云的大体形状是比较准确的（保留的几何细节是比较多的）
![[1732247118960.png|500]]![[1732248291052.png|500]]

如何获取实例级的点云？3DGS 的点云是场景的点云，对点云进行实例分割是一个比较大的话题
### 点云的实例分割
主流的方法其实可以分为两类，第一类是深度学习相关的方法，第二类是传统计算的方法，比如聚类、区域生长算法，传统算法的分割精度不高，下面主要介绍一下基于深度学习的相关算法
- PointNet++: 将点云带入深度学习的开山鼻祖，但是对场景分割的粒度不够，分割结果还是比较粗糙的
	![[Pasted image 20241122135507.png|500]]

- RandLA-Net (大场景下的点云语义分割)  : 
	==点云牺牲了真实的拓扑结构，对于距离比较近的物体可能无法分割==，对于场景的点云分割，大部分的方法都是在一个块上进行操作的。比方说一间房子的点云，20 m×20 m，里面的点非常多，所以一般会在俯视视角上，切一个比如 1 m×1 m×H 的长方体，在这个长方体内做操作，而且这个长方体内的点云也是非常多的，所以还要再做一个采样，比如采样 4096 个点。那么这种切块操作带来的问题就显而易见了，一个桌子切成两半，然后在各自的块内做分割，这就缺少了一种整体的特征。

- 3D-BoNet: 实例分割
	 针对简单场景的语义分割结果还可以，但是 3DGS 的场景一般都比较复杂，细节比较多，在这种复杂场景上的分割表现还不太理想
	 ![[2517c9572399ca2cfb49b39118dd8423.gif|500]]

其实点云上的实例分割的难度主要来源于点云数据的特点（稀疏性、不规则性、无序性）
与2D图像不同，点云数据缺少全局的上下文信息，这使得对物体进行全局理解变得困难。虽然点云包含了物体的空间布局，但缺乏像图像那样的纹理和颜色信息，导致分割模型难以借助全局上下文来判断不同实例之间的关系。

2D 图像的语义分割已经十分成熟了，像素级的分割也已经十分准确了，之前深度学习的 CV 领域都在卷 2 D 图像的实例分割、语义分割的准确性，这种现象的终结者是 meta 发布的一个模型 Segment Anything Model ，他通过提示来进行分割，还支持 0 样本迁移，基于 SAM 进行语义分割的方法也遍地开花。
能不能将 2D 图像上这种识别的准确性带到点云中呢？

- SAM 3D: Segment Anything in 3D Scenes
	 **数据特点**
	 利用了点云和 RGB 图像的对应关系，其实 3 DGS 的原始数据可以通过深度相机进行拍摄，获得一张包含纹理信息的 RGB 图，还有一张包含深度信息的深度图，RGB 图像和 Depth 图像是配准的，因而像素点之间具有一对一的对应关系。利用这种对应关系，就可以利用 RGB 图像的精准分割能力对，深度信息进行准确的分割，从而生成对应实例的点云信息。
	 ![[Pasted image 20241122143707.png|500]]
	 **深度信息 To 点云**
	 深度图转为点云说其实就是坐标系的变换：图像坐标系转换为世界坐标系。变换的约束条件就是相机内参
	 ![[Pasted image 20241122144701.png|500]]
	 
	1. 利用 SAM 在 RGB 上的 Mask，分割点云。
	2. 数据是有相机姿态的 RGB 图像以及对应 3 D 点云，首先使用 SAM 预测 RGB 图像的 Mask，然后将 2D Mask 投影到 3D 点云中，之后迭代地合并 3D Mask。
	3. 在每一次迭代，使用 bidirectional merging 方法合并两个相邻帧的点云 Mask，从不同帧预测的 3DMask 逐渐合并到整个 3D 场景。
		![[Pasted image 20241113114631.png|500]]

### 点云的方向估计 （PCA 主成分分析）
其实就算是拿到一个完整的模型信息，去判断模型的正方向也是一件比较抽象和比较难的事情
![[Pasted image 20241122150859.png|425]] ![[Pasted image 20241122150922.png|399]] ![[Pasted image 20241122151010.png|396]]
我去判断一个物体的正面的时候，一个朴素的想法是，哪一个面具有最多的细节，可以让人们获得到更多的信息，那么这个面就是正面
这种判断的思路与 PCA 主成分分析的想法很类似，PCA 其实是一种数据降维算法

首先先举个例子来认识一下数据。  
假设我们有一组二维数据(x,y)，它的分布如下：
![[Pasted image 20241122152639.png|500]]
可以看到，数据在 x 轴上的变化大，而在 y 轴变化小，变化小意味着数据在这个特征上没有太大的差异，因此它包含的信息就比较少，那么我们就可以认为它是不重要的或者是噪音，从而可以直接将这个维度上的数据舍去，只用 x 轴上的数据来代替。

那么假如数据是这样分布的呢？
![[Pasted image 20241122152719.png|450]]

这个图我们就不太好看出到底是谁比较重要了，因为 x 和 y 变化都比较大，那么是不是就不能降维了？ 也可以进行降维
![[Pasted image 20241122152830.png|475]]
新坐标系下数据的坐标值就是数据在坐标轴上的投影，这时候的情况就和上面那个例子一样了。

从这个例子也可以看到，数据本身的具体数值其实是不重要的，重要的是数据之间的关系，数据的整体分布。原来的数据是在 E 坐标系下，然后我们换了一个坐标系来表示，本质上相当于对数据进行了一次正交变换（从数学公式看），在新的坐标系下，我们能更清楚的看到数据的特点，这为我们后续进一步操作数据提供了可能。

我们的点云数据包含 xyz、法线、颜色的各种维度的信息，也属于是高维信息，但是我们去估计方向的话，只需要用到 xyz 的信息。所以我们进行主成分分析的时候，输入是一个 3 维的点云信息，我们要将点云投影到某个平面上，使得点云可以最大程度的保留信息，那么对应点云模型的正面就是垂直于主成分方向的投影方向。

如果 PCA 分析的结果与我们的主观或者目标不一致该怎么办
![[Pasted image 20241122154530.png|500]]
按照 PCA 算法对飞机进行分析的时候，得到的模型正面应该是飞机的俯视视角，与我们印象中的飞机正面是不一致的。在这种情况下，我们需要通过人工进行干预，手动选择模型包围盒的一个面作为模型的正面，如下图。

![[Pasted image 20241120142016.png|500]]

Test demo (广告牌)
![[Pasted image 20241202163124.png|500]]
![[Pasted image 20241202164709.png|500]]

### think

1、是否可以通过物体的点云实例，生成对应的更精细的 mesh 模型，从而生成具有明确的语义和结构的场景 Mesh？有了这样的场景 mesh，对应场景中的一个实例来说，我们就拥有了更丰富的信息，包括 position、rotation
2、纯视频训练的 nerf   的点云 和 Segment Any Mesh 生成的点云差异是否可接受
3、 激光扫描出来的点云该如何处理？

1、重新喂一个正方向的数据（问一下工作量）
2、PCA 配准（cad 点云）
3、包含多层次的信息去推断（环境中信息，比如道路的方向，距离道路的最小值）


# 参考资料
## 1 、查询相同语义的物体（相似度计算）
### 1.1 网格模型的相似度评估
1. **基于几何形状的相似度**
	- **Hausdorff 距离（Hausdorff Distance）**：测量两个点集之间的最大距离。对于点云或网格的比较，Hausdorff 距离能反映两个模型中某点到另一个模型最远点的距离，可以作为相似度的度量，值越小表示越相似。
	- **点云对齐（ICP）**：使用迭代最近点（Iterative Closest Point, ICP）算法对两个点云进行对齐，然后计算重叠部分的误差或点云之间的匹配度。==计算量大，效率低。==
2. 基于特征的相似度
	- **主成分分析（PCA）**：对点云或网格模型的点进行主成分分析（PCA），提取其主要特征（例如，主要方向、表面法线等）。通过比较两个模型的主成分，可以得出它们在几何空间中的相似度。==对模型的旋转、平移和尺度变化敏感，==
3. 基于深度学习的相似度
	- 通过学习模型的几何和拓扑特征来评估相似度。==计算资源消耗大==
### 1.2 数字表亲数据库
![[Pasted image 20241113100109.png|500]]
首先要构建表亲数据库，数据库中的每一个表亲数据都应该具有以下的数据
$ai = (ti, Ii, \{iis\}_{s=1}^{Nsnap})$
其中, **ti**是资产类别，**Ii**是代表性快照，${iis}_{s=1}^{Nsnap}$ 是该资产的多个快照， Nsnap 表示快照的数量。

给定一个输入物体表示（**oi**），应该包含以下信息，
${oi=(li,mi,pi,xi)}_{i=1}^{N}$
其中**物体标签（li）**、**物体掩模（mi）**、**物体点云（pi）** 和**物体像素（xi）**

计算**CLIP 相似度**得分来选取候选的资产类别。选择 $k_{cat}$ 个最接近的类别。

在这 $k_{cat}$ 中，计算 **DINOv 2 特征嵌入距离** 选择 $k_{cand}$ 个最接近的数字表亲候选。

最后对每个候选数字表亲的所有**快照**（**iis**）计算**DINOv 2 嵌入距离**。即对于每个候选资产的不同方向的快照，重新计算与输入物体区域的匹配度。
选择**kcous**个最接近的数字表亲（即最符合要求的虚拟资产），每个选中的数字表亲包括：
	    - **虚拟资产（Ac）**：选择的虚拟资产。
	    - **特定方向（qc）**：基于选中的快照，确定的虚拟资产的方向。
综合不同维度的信息进行查询，查询准确度较好

## 2、对场景中的模型进行裁剪
### 2.1 对 mesh 进行裁剪
#### 2.1.1 具有明确的语义和结构的场景 Mesh
![[Pasted image 20241115150811.png|500]]
#### 2.1.2 利用深度学习进行 mesh 的实例分割
- PointNet++: ==点云牺牲了真实的拓扑结构，对于距离比较近的物体可能无法分割==，对于场景的点云分割，大部分的方法都是在一个块上进行操作的。比方说一间房子的点云，20m×20m，里面的点非常多，所以一般会在俯视视角上，切一个比如1m×1m×H 的长方体，在这个长方体内做操作，而且这个长方体内的点云也是非常多的，所以还要再做一个采样，比如采样4096个点。那么这种切块操作带来的问题就显而易见了，一个桌子切成两半，然后在各自的块内做分割，这就缺少了一种整体的特征。
- RandLA-Net (大场景下的点云语义分割) : 
- MeshCNN：保留了 mesh 的拓扑信息进行卷积
- 3D-BoNet: 实例分割
- SAM3D: Segment Anything in 3D Scenes
	1. 利用 SAM 在 RGB 上的 Mask，分割点云。
	2. 数据是有相机姿态的 RGB 图像以及对应 3D 点云，首先使用 SAM 预测 RGB 图像的 Mask，然后将 2D Mask 投影到 3D 点云中，之后迭代地合并 3D Mask。
	3. 在每一次迭代，使用 bidirectional merging 方法合并两个相邻帧的点云 Mask，从不同帧预测的 3 DMask 逐渐合并到整个 3D 场景。
		![[Pasted image 20241113114631.png|500]]
### 2.2 对 nerf 画面进行裁剪
#### 2.2.1 GaussianEditor
#### 2.2.2 手工裁剪
单纯的对高斯画面进行裁剪编辑的工具：
1. Unity playground tool [https://github.com/aras-p/UnityGaussi...](https://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbnV2S3locGZ6RmxyNUdiQ3JxSnRPc29NbXEzUXxBQ3Jtc0ttTm93X3JraVZ6TTJDV1dfYjBQeEg2SUNnWGNDNVRSMG9tRWVEVmxTdEJaaDQ2ZDBKZksydjhvZVNzV0wyMy1Tc1VBc2dKeFc3dmZ1MnVZUER2T1QyZTVsWlpxX2twZGRLR0R0b1RJc1BYXzlrSFVkaw&q=https%3A%2F%2Fgithub.com%2Faras-p%2FUnityGaussianSplatting&v=9pWKnyw74LY) 
2. 3 D Gaussian Plugin for UE 5 [https://www.unrealengine.com/marketpl...](https://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbTRMdlQxYzVFU29xTjFzczQ1NjJVSDJyb3pEd3xBQ3Jtc0trOUJTbENDRHJONllGX0F4QlVrSWJja3NLNVJrTndBZG1leklqb2t3NHgwOFV3dHByams1dWxCcWlrQWZMSDZVUXJ0bjk1YXMyQkF2X0UtVzJ5WndPU3d2RGlMNG9uVkFMbTR2a0hmNEZ6Rl9pME5QQQ&q=https%3A%2F%2Fwww.unrealengine.com%2Fmarketplace%2Fen-US%2Fproduct%2F3d-gaussians-plugin&v=9pWKnyw74LY) UPDATE! In version v 0.8.0 selection can now subtract from selection while Ctrl key is pressed 
3. Luma AI tool for UE 5.3 NOW IN UE MARKETPLACE [https://www.unrealengine.com/marketpl...](https://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbXhoTkkxb0Z5Q1ZLOE5uYWhuZGc1YTI3c1Fsd3xBQ3Jtc0tuaEI5SlE1SjNTem9CdjBvUS1kd1NyVVJxQ2lycE5QOGt3ZGVwczZ3R0d5UFhpZmNGaGpLMEJfdTAwWURZYnpaalBuR2hhS3dKa04xaEVyeTlFaEZsTXlRdElhalJTb1k4Y19tZ0pUcG9vczVsVk5QOA&q=https%3A%2F%2Fwww.unrealengine.com%2Fmarketplace%2Fen-US%2Fproduct%2Fluma-ai&v=9pWKnyw74LY) Another place to get Luma plugin: [https://lumaai.notion.site/Luma-Unrea...](https://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbFlkd0ZsZzRydUxhN3lQTl8ySXo4cGRLbzhIQXxBQ3Jtc0tsbGM4RGpUUkJ3WnhZSjRPZ2dUVVVqcGhsZDZ4MDhuWHRxSVFLbU1ZYkh4MlBRbTMtdEQ1TkhpZmVLLU9rbDlLRm1ZajlvUDhqLUJlTUd5V2YxY2YyN2FwMDBHU0RlY2VSMzZzQnJYYTNEeG1HeVZ1UQ&q=https%3A%2F%2Flumaai.notion.site%2FLuma-Unreal-Engine-Plugin-0-4-8005919d93444c008982346185e933a1&v=9pWKnyw74LY) 
4. Gaussians for Blender' [https://github.com/ReshotAI/gaussian-...](https://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbDFkSDViMWsyUm10SERuaE1LdUt3cWE1aGZiUXxBQ3Jtc0tsZWdjTDhQQVBVaEItMExvY3ZfcFh2SE54dzZCdV9Wa2ZKMFlaNURMbkNzdzR5cmowM1JiYkN4bmxRSk5JWldwYjRJSGdEa3JnSEFlbVRsdElpbTFZb0NyTUxuanJqd2hualB5azdLcFZlZFFDcVlmbw&q=https%3A%2F%2Fgithub.com%2FReshotAI%2Fgaussian-splatting-blender-addon&v=9pWKnyw74LY)
	- Check out also tutorial video from Max Novak    [![](https://www.gstatic.com/youtube/img/watch/yt_favicon_ringo2.png) • Gaussian Splatting + Blender is AWESO...]( https://www.youtube.com/watch?v=yKz7OfomyCo&t=0s )  
5. UEGaussianSplatting [https://www.unrealengine.com/marketpl...](https://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbGlzTTU2a2lhUklZQU9kcFc2d0p1enFEelREUXxBQ3Jtc0tsdHh1dExacC16MmFUNXZNQS03Wm5Jd1FxMi1QeTRfNlFya3ZOZ2dZNzJEUXVacDNLV3UxQjhXU3dXbFQxcEx6M1ZRS2hObl9ncUk1X3QtUm9sQkhvNVhVR0FIWG1QRTJUQUYydkFjTndvR1hxMEYtRQ&q=https%3A%2F%2Fwww.unrealengine.com%2Fmarketplace%2Fen-US%2Fproduct%2Fuegaussiansplatting-3d-gaussian-splatting-rendering-feature-for-ue&v=9pWKnyw74LY) 
6. Super Splat [https://playcanvas.com/super-splat](https://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbGNqaE0tcDFmR0J0OGRoVGllUm1BSkFMa3dDd3xBQ3Jtc0ttUVlueFVWVUhSRXdId2RQeTJ6bnpEa2RnMmM1VWF6MHJCNFNpUURMT1hwOGxwcEY1WHVLRGFubkRhN2pSQ2tjQUhjNUFQeGZBNjIxV29LT1I1bHA1bmhEcUZYemNGZU9wQXJOYTJnNE90SHpTYkE2bw&q=https%3A%2F%2Fplaycanvas.com%2Fsuper-splat&v=9pWKnyw74LY)
### 2.3 3DGS 语义分割
#### 2.3.1 Segment Any 3D Gaussians
将二维分割模型与三维高斯 Splatting（3DGS）相结合。有效地将分割模型生成的多粒度二维分割结果嵌入到三维高斯点特征中。 可以在几毫秒内完成 3D 分割，还实现了多粒度分割，并适应各种提示，包括点、涂鸦和 2D mask。
![[bbc3aefef2e1a7a4ff2c79d8d3faed7d.gif|500]]
#### 2.3.2 CLIP-GS: CLIP-Informed Gaussian Splatting for Real-time and View-consistent 3D Semantic Understanding
该方法将 CLIP 模型的语义信息与3D 高斯溅射相结合，用于实现对3D 场景的实时、精确语义理解。
![[Pasted image 20241113150228.png|500]]
#### 2.3.3 LangSplat: 3D Language Gaussian Splatting
LangSplat 提供了一种新颖且高效的方式，通过 3D 高斯斑点和自编码器来表示和查询 3D 语言特征，相比于现有方法大幅提升了查询的精度和计算效率
![[Pasted image 20241113150352.png|500]]

#### 2.3.4 Gaussian Grouping: Segment and Edit Anything in 3D Scenes
Gaussian Grouping 的核心技术在于其对高斯喷射技术的扩展。传统的 3 D 重建方法主要关注场景的外观和几何建模，而 Gaussian Grouping 在此基础上引入了对象级别的场景理解。通过为每个高斯分布添加身份编码，系统能够在不依赖昂贵的 3 D 标签的情况下，通过 2 D 掩码预测和 3 D 空间一致性正则化来监督身份编码的学习。这种离散且分组的高斯分布不仅能够高效地重建和分割 3 D 场景，还能支持多种复杂的编辑操作，如 3 D 对象移除、修复、风格转换和场景重组。
![[Pasted image 20241113143454.png|500]]
## 3、对场景中的模型进行同语义替换
位置：根据 digital cousins 的 bounding box center，可以将数字表亲模型放到对应位置吗？
需要具有明确的语义和结构的场景 Mesh，由不同语义的 mesh 组合起来，可以获得对应语义 mesh 的空间坐标（要以模型的质心坐标为准），从而将表亲数据放置到对应位置
方向：
scale：


## 4、位姿估计
1. DenseFusion: 6D Object Pose Estimation by Iterative Dense Fusion（2019）
    提出了一种将 RGB-D 输入的颜色和深度信息融合起来的基础方法。利用嵌入空间中的2D 信息来增加每个3D 点的信息，并使用这个新的颜色深度空间来估计6D 位姿。
    在神经网络架构中集成了一个迭代的微调过程，消除了之前后处理 ICP 步骤的依赖性。
    
	- **创新的密集特征融合**：通过设计密集融合网络，DenseFusion 能够更有效地融合 RGB 和深度信息，显著提升6D 姿态估计的精度。
	- **迭代优化**：集成的端到端迭代姿态优化过程进一步提高了估计精度，使得模型能够在复杂场景下表现得更加稳定和精确。
	- ![[Pasted image 20241125105038.png|500]]
2. Normalized Object Coordinate Space for Category-Level 6D Object Pose and Size Estimation（2019）
    本文的目标是估计 RGB-D 图像中从未见过的物体实例的6D 位姿和尺寸。与“实例级”6D 位姿估计任务相反，作者假设在训练或测试期间没有精确的 CAD 模型可用。为了处理给定类别中不同的和从未见过的物体实例，作者引入了标准化物体坐标空间（简称 NOCS），即同一个类别中的所有物体实例使用一个共享的标准模型来表示。然后，通过训练神经网络来推断观察到的像素与共享标准模型的对应关系以及其他信息，例如类别标签和 mask。通过将预测图像与深度图相结合，共同估计杂乱场景中多个物体的6D 位姿和尺寸。为了训练网络，作者提出了一种新的上下文感知技术来生成大量带注释的混合现实数据。为了进一步改进模型并评估它在真实数据上的性能，作者还提供了一个完全注释的真实场景下的数据集。大量实验表明，该方法能够鲁棒地估计真实场景中从未见过物体的位姿和大小。
    ![[Pasted image 20241125105907.png|500]]
3. FoundationPose: Unified 6D Pose Estimation and Tracking of Novel Objects （2024.6）
    3.1 基于大语言模型 LLM 和扩散模型，通过文字信息，引导生成指定的物体3D 模型纹理和外观，生成大规模训练数据。
    3.2 在没有物体的3D CAD 模型的情况下，通过神经隐式场表示来进行高效的物体建模。
    3.3 生成多个假设的姿态，主要有两步过程，生成初始姿态和姿态细化
    3.4 最后选出最准确的姿态。
    FoundationPose 的思路流程，如下图所示，看一下输入和输出：
	- FoundationPose 支持两种数据的输入，可以选择一些物体的 RGBD 图片，也可以直接输入物体的 CAD 模型。
	- 其中，输入物体的 RGBD 图片，可以是4张、8张、16张等，模型会用基于 SDF 的 NeRF 构建物体的3D 模型。
    ![[Pasted image 20241125111605.png|500]]
    - 输出结果也有两种，一种是实时预测的位姿信息，另一种是使用跟踪算法计算出物体位姿信息。
	- 看官方的 demo 代码，先对物体进行一次实时位姿预测，然后基础这个结果进行跟踪。
    References
    - [【6D位姿估计】FoundationPose 跑通demo 训练记录_foundationpose demo-CSDN博客](https://blog.csdn.net/qq_41204464/article/details/138619210?spm=1001.2014.3001.5501&login=from_csdn)
    - [【6D位姿估计】FoundationPose 支持6D位姿估计和跟踪 CVPR 2024_一颗小树x-开放原子开发者工作坊](https://openatomworkshop.csdn.net/673fe99559bcf8384a83ff9a.html?dp_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NzA3Nzg0LCJleHAiOjE3MzMxMDg5ODEsImlhdCI6MTczMjUwNDE4MSwidXNlcm5hbWUiOiJ1MDEyNDIxNjE2In0.Q87nJomid96zCc_HrL7e6K1ntF3Yk3V-Cg11nfVMjso&spm=1001.2101.3001.6650.2&utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromBaidu%7Eactivity-2-138537252-blog-137132253.235%5Ev43%5Epc_blog_bottom_relevance_base4&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7EBlogCommendFromBaidu%7Eactivity-2-138537252-blog-137132253.235%5Ev43%5Epc_blog_bottom_relevance_base4&utm_relevant_index=4)
    复现流程：
    升级 python `conda install python=3.9`
    升级 gcc、g++
    `conda install -c conda-forge gcc=11 gxx=11`
    


4. Omni6D: Large-Vocabulary 3D Object Dataset for Category-Level 6D Object Pose Estimation
    **现有方法的评估与分析**：我们在 Omni6D 数据集上评估了现有的类别级 6D 物体位姿估计方法，深入分析了这些方法面临的挑战，帮助识别当前技术的不足之处。
5. SAM-6D: Segment Anything Model Meets Zero-Shot 6D Object Pose Estimation
    ![[Pasted image 20241125114740.png|500]]
    docker run -it --gpus "device=0" -v D:/work/DeepLearningSpace/SAM-6D-main/:/workspace  lihualiu/sam-6d: 1.0 /bin/bash 
    ![[vis_pem.png|500]]
    
    -  输入 RGBD 图像数据、待位姿估计的物体数据，可以输入多个要估计的物体。
    - 实例分割，RGBD 数据输入到 Segment Anything 模型（SAM）进行实例分割，生成所有可能的物体区域。
    - 匹配对应目标物体，生成的物体区域会有多个，需要逐一和待估计的物体进行匹配。
    - 姿态估计，输入包括 RGB-D 图像中提取的观测点云、目标物体的3D 模型点云；首先进行粗略匹配，再进行精细匹配。
    - 输出6D 位姿信息，包括三维位置、三维方向。

6 D 位姿估计的算法是否可行？是否可以融入到 nerf 地图训练的流程中，最终在 json 中提供对应的位姿
测试 6 D 位姿的算法，对应的测试数据
metaspace 训练 nerf 地图的流程、训练 3 DGS 地图的流程

数据相关的问题：
从点云生成深度图，
从深度图生成点云
