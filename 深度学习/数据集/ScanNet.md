ScanNet 是一个大规模的 RGB-D 视频数据集，包含 **1500 多个扫描场景**中的 **250 万张视图**，并标注了 **3D 相机位姿**、**表面重建**和**实例级语义分割**。该数据集广泛用于 3D 场景理解任务，如物体分类、语义分割和 3D 重建。
### 数据组织
ScanNet 数据按 **RGB-D 序列**组织。每个序列存储在以 `scene<spaceId>_<scanId>` 或 `scene%04d_%02d` 命名的目录下，其中每个 `spaceId` 对应一个唯一的位置（从 0 开始索引）。每个序列目录包含以下文件：
![[Pasted image 20250109180238.png|343]]
```text
<scanId>
|-- <scanId>.sens                  # RGB-D 传感器流，包含彩色帧、深度帧、相机位姿等
|-- <scanId>_vh_clean.ply          # 高质量重建网格
|-- <scanId>_vh_clean_2.ply        # 用于语义标注的清理和简化网格
|-- <scanId>_vh_clean_2.0.010000.segs.json  # 标注网格的过分割结果
|-- <scanId>.aggregation.json      # 低分辨率网格上的实例级语义标注
|-- <scanId>_vh_clean.aggregation.json  # 高分辨率网格上的实例级语义标注
|-- <scanId>_vh_clean_2.labels.ply # 语义分割可视化文件（按 nyu40 标签着色）
|-- <scanId>_2d-label.zip          # 原始 2D 标注标签投影（16 位 PNG）
|-- <scanId>_2d-instance.zip       # 原始 2D 实例标注投影（8 位 PNG）
|-- <scanId>_2d-label-filt.zip     # 过滤后的 2D 标注标签投影（16 位 PNG）
|-- <scanId>_2d-instance-filt.zip  # 过滤后的 2D 实例标注投影（8 位 PNG）
```
### 数据格式
1. **重建表面网格文件（*.ply）**：
    - 二进制 PLY 格式，+Z 轴朝上。    
2. **RGB-D 传感器流文件（*.sens）**：
    - 压缩二进制格式，包含每帧的彩色图像、深度图像、相机位姿等数据。
    - 可使用 ScanNet C++ Toolkit 或 SensReader/python 解析。
3. **表面网格分割文件（*.segs.json）**：
    - 包含分割参数和每个顶点的分割索引。
4. **语义标注文件（*.aggregation.json）**：
    - 包含场景 ID、标注工具 ID 和实例级语义标注信息。
5. **2D 标注投影文件（*_2d-label.zip, *_2d-instance.zip 等）**：
    - 将 3D 标注投影到 RGB-D 帧中，生成 2D 标签或实例图。
### ScanNet 工具
1. **ScanNet C++ Toolkit**：
    - 用于处理 ScanNet 数据，如解析 `.sens` 文件。
2. **相机参数估计代码**：
    - 用于估计相机参数和深度去畸变。
3. **网格分割代码**：
    - 用于预处理网格并准备语义标注。
4. **BundleFusion 重建代码**：
    - ScanNet 使用 BundleFusion 进行 3D 重建。
5. **ScanNet Scanner iPad App**：
    - 用于通过 iPad 和 Structure.io 传感器捕获 RGB-D 序列。
6. **ScanNet 数据管理 UI**：
    - 基于 Web 的界面，用于管理扫描数据和标注流程。
7. **语义标注工具**：
    - 提供基于 Web 的标注界面，支持语义标注任务。
### 基准任务
ScanNet 提供了多个场景理解任务的基准代码，包括：
- **3D 物体分类**
- **3D 物体检索**
- **语义体素标注**
任务数据包含训练/测试集划分、标签映射和预训练模型。
### 标签映射
ScanNet 标注中的标签与 NYUv2、ModelNet、ShapeNet 和 WordNet 的类别集进行了映射。标签映射文件 (`scannet-labels.combined.tsv`) 可随任务数据一起下载。
.\micromamba.exe --help
 D:\__Profile\mamba