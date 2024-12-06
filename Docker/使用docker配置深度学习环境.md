如何在 Windows 环境下使用 Docker 作为深度学习环境呢？一共分为三步：安装 Docker、配置 WSL2，开始玩。
安装 Docker、配置 WSL 2 这个就不讲了，配置好这两项之后，我们直接进入正题：

在使用 Docker 调用容器镜像前，我们还需要验证下 Docker 是否能够和 GPU 正常通信。
### 验证 Docker 中 GPU 是否能够被正常调用
可以先下载一个 Nvidia 官方的 PyTorch 镜像：
```bash
docker pull nvcr.io/nvidia/pytorch:23.07-py3
```
镜像比较大，需要耐心等待几分钟：
```bash
# docker pull nvcr.io/nvidia/pytorch:23.07-py3
23.07-py3: Pulling from nvidia/pytorch
Digest: sha256:c53e8702a4ccb3f55235226dab29ef5d931a2a6d4d003ab47ca2e7e670f7922b
Status: Downloaded newer image for nvcr.io/nvidia/pytorch:23.07-py3
```
当镜像下载完毕后，我们可以使用命令 `docker run -it --gpus=all --rm nvcr.io/nvidia/pytorch:23.07-py3 nvidia-smi` 来使用 Docker 启动一个容器，并在容器中调用 `nvidia-smi` 显卡管理程序，来查看显卡的状况：
```bash
# docker run -it --gpus=all --rm nvcr.io/nvidia/pytorch:23.07-py3 nvidia-smi
=============
== PyTorch ==
=============

NVIDIA Release 23.07 (build 63867923)
PyTorch Version 2.1.0a0+b5021ba

Container image Copyright (c) 2023, NVIDIA CORPORATION & AFFILIATES. All rights reserved.

Copyright (c) 2014-2023 Facebook Inc.
Copyright (c) 2011-2014 Idiap Research Institute (Ronan Collobert)
Copyright (c) 2012-2014 Deepmind Technologies    (Koray Kavukcuoglu)
Copyright (c) 2011-2012 NEC Laboratories America (Koray Kavukcuoglu)
Copyright (c) 2011-2013 NYU                      (Clement Farabet)
Copyright (c) 2006-2010 NEC Laboratories America (Ronan Collobert, Leon Bottou, Iain Melvin, Jason Weston)
Copyright (c) 2006      Idiap Research Institute (Samy Bengio)
Copyright (c) 2001-2004 Idiap Research Institute (Ronan Collobert, Samy Bengio, Johnny Mariethoz)
Copyright (c) 2015      Google Inc.
Copyright (c) 2015      Yangqing Jia
Copyright (c) 2013-2016 The Caffe contributors
All rights reserved.

Various files include modifications (c) NVIDIA CORPORATION & AFFILIATES.  All rights reserved.

This container image and its contents are governed by the NVIDIA Deep Learning Container License.
By pulling and using the container, you accept the terms and conditions of this license:
https://developer.nvidia.com/ngc/nvidia-deep-learning-container-license


NOTE: The SHMEM allocation limit is set to the default of 64MB.  This may be
   insufficient for PyTorch.  NVIDIA recommends the use of the following flags:
   docker run --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 ...

Sat Jul 29 01:44:04 2023
+---------------------------------------------------------------------------------------+
| NVIDIA-SMI 530.37                 Driver Version: 531.30       CUDA Version: 12.1     |
|-----------------------------------------+----------------------+----------------------+
| GPU  Name                  Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf            Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                                         |                      |               MIG M. |
|=========================================+======================+======================|
|   0  NVIDIA GeForce RTX 4090         On | 00000000:01:00.0  On |                  Off |
| 32%   38C    P8               23W / 450W|    571MiB / 24564MiB |      4%      Default |
|                                         |                      |                  N/A |
+-----------------------------------------+----------------------+----------------------+

+---------------------------------------------------------------------------------------+
| Processes:                                                                            |
|  GPU   GI   CI        PID   Type   Process name                            GPU Memory |
|        ID   ID                                                             Usage      |
|=======================================================================================|
|  No running processes found                                                           |
+---------------------------------------------------------------------------------------+
```
## example
所以，在环境就绪之后，我们来使用 Docker 来尝试运行上一篇文章《[使用 Docker 快速上手 Stability AI 的 SDXL 1.0 正式版](https://soulteary.com/2023/07/29/get-started-with-stability-ai-sdxl-1-0-release-using-docker.html)》中提到的 Stable Diffusion XL 1.0 的镜像，让它能够在 Windows 环境下正常使用。
### 下载模型文件和容器环境
我们可以从[网盘地址1](https://pan.baidu.com/s/1WKZEPFCvCpg-e4KlDT6bLw?pwd=soul)和[网盘地址2](https://pan.baidu.com/s/1MjJrtubxs-APvlEBO0XYCQ?pwd=soul)，分别下载官方的模型文件和整理好的 Docker 容器环境（环境只下载 `sdxl-runtime.tar` 即可）。
如果下载出现问题，可以前往 [soulteary/docker-sdxl](https://github.com/soulteary/docker-sdxl) 项目 issue 留言反馈或参考上一篇文章，从 HuggingFace 下载模型，和进行容器镜像的手动构建。
### 加载模型并准备工作目录
以 C 盘为例，我们在盘根创建一个名为 `docker-sdxl` 的目录，然后将 `sdxl-runtime.tar` 和下载模型目录中的 `stabilityai` 放到这个目录中。
然后，切换工作目录到 `C:/docker-sdxl`：
```bash
cd C:/docker-sdxl/
```
接着，执行命令，载入容器镜像文件 `docker load -i .\docker-sdxl\sdxl-runtime.tar`：
```bash
docker load -i .\docker-sdxl\sdxl-runtime.tar
68ad565f4346: Loading layer [==================================================>]   2.56kB/2.56kB
b279d196469f: Loading layer [==================================================>]  384.6MB/384.6MB
08135af11e7a: Loading layer [==================================================>]  1.536kB/1.536kB
6b36eae25335: Loading layer [==================================================>]  6.144kB/6.144kB
72a8d0a30e5a: Loading layer [==================================================>]  18.94kB/18.94kB
Loaded image: soulteary/sdxl:runtime
```
镜像加载完毕之后，我们就可以运行 Docker 容器，来玩 SDXL 啦：
```bash
docker run --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 --rm -it -v C:/docker-sdxl/stabilityai/:/app/stabilityai -p 7860:7860 soulteary/sdxl:runtime
```
**`--gpus all`**：
- 这表示将容器配置为使用所有可用的 GPU。如果你使用的是支持 GPU 的 Docker 和 Nvidia 驱动，这将启用对 GPU 的访问。在 linux 系统中，你需要确保安装了 NVIDIA Docker（NVIDIA Docker (nvidia-docker2) is primarily designed for Linux-based systems and is not natively supported on Windows. NVIDIA Docker relies on features provided by the Linux kernel, which are not present on Windows.）但是在 windows，Microsoft has introduced support for GPU-accelerated containers on Windows。
**`--ipc=host`**：
- 这个参数设置容器与宿主机共享 IPC（进程间通信）命名空间。它对一些高性能计算任务（如深度学习）很有用，因为它可以减少进程间的通信延迟。
**`--ulimit memlock=-1`** 和 **`--ulimit stack=67108864`**：
- 这两个选项调整了容器内存锁定和栈大小的限制。`memlock=-1` 允许无限制的内存锁定，`stack=67108864` 设置容器的栈大小为 64MB。这些选项通常用于高性能计算和机器学习任务，以避免内存相关的限制。
**`--rm`**：
- 在容器停止时自动删除容器文件系统，避免积累未清理的容器。
**`-it`**：
- 这两个选项分别表示交互式（`-i`）和终端模式（`-t`）。这通常用于启动交互式会话，例如进入一个 shell 或运行需要用户交互的应用程序。
**`-v C:/docker-sdxl/stabilityai/:/app/stabilityai`**：
- 这个选项将主机的 `C:/docker-sdxl/stabilityai/` 目录挂载到容器内的 `/app/stabilityai` 目录。这是用来共享数据或代码的。容器中的 `/app/stabilityai` 目录会映射到你主机上的 `C:/docker-sdxl/stabilityai/` 目录。
**`-p 7860:7860`**：
- 这个选项将主机的 `7860` 端口映射到容器的 `7860` 端口。通常这种设置用于 Web 服务的容器化，允许你从主机访问容器内运行的服务。
**`soulteary/sdxl:runtime`**：
- 这是你要运行的 Docker 镜像名称和标签。`soulteary/sdxl` 是镜像名称，`runtime` 是标签。确保镜像已经存在于你的 Docker 本地仓库，或者 Docker 会从 Docker Hub 拉取该镜像。

可以看到，命令和前一篇适用于 Linux 环境的文章几乎一致，除了在 Linux 环境下，我们可以通过 `pwd` 来表示当前目录，而 Windows 环境中，最佳实践是通过完整目录（`C:/docker-sdxl/stabilityai/`）来表示。
在命令执行完毕后，我们就进入了交互式的终端，接下来我们可以执行和上一篇文章一样的三个程序：`basic.py`、`refiner.py`、`refiner-low-vram.py`：
```bash
# 执行基础模型程序
python basic.py
# 执行全家桶模型程序
python refiner.py
# 执行使用显存稍低的程序
python refiner-low-vram.py
```
资源要求和消耗和上一篇并没有什么不同，唯一的差别可能是 WSL2 的数据传输性能相比 Linux 环境要低不少，模型加载的时间会长很多，需要耐心等待。
当模型完全加载完毕，我们能够看到下面的日志：
```bash
python basic.py
Loading pipeline components...: 100%|███████████████████████████████████████████████████████████████████████████| 7/7 [00:03<00:00,  1.95it/s]
Running on local URL:  http://0.0.0.0:7860/

To create a public link, set `share=True` in `launch()`.
```
接下来，访问 `http://localhost:7860` 或者 `http://你的IP:7860` 来访问 SDXL 1.0 的 Web 界面啦。
![[Pasted image 20241126104957.png|475]]
**虽然上面日志中加载模型的性能比较差，但实际推理的性能非常好，能够达到 `11~13it/s`，和 Linux 没有什么差异。（都在显存里了，没有数据交换）**

因为 Windows 默认会打开防火墙，限制程序对外暴露端口，避免一些安全问题。在使用的时候，如果你的 Windows 主机和你要访问这个服务的设备是两台设备，你需要关闭或者在防火墙内放行这个应用，有类似情况的小伙伴可以注意下，调整下系统防火墙配置。