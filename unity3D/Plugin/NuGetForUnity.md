---
title: "[[NuGetForUnity]]"
type: Reference
status: done
Creation Date: 2025-09-03 16:54
tags:
---
### 什么是 NuGetForUnity？
NuGetForUnity 是一个非官方但广受欢迎的 Unity 插件，它允许你在 Unity 项目中直接使用 NuGet 包管理器。NuGet 是 .NET 平台最主要的包管理器，拥有庞大的开源库生态系统。默认情况下，Unity 使用自己的包管理系统（Unity Package Manager, UPM），但 UPM 主要用于管理 Unity 官方和社区发布的 Unity 特有包。

有了 NuGetForUnity，你就可以在 Unity 中方便地引用和使用那些为 .NET 平台设计的第三方库，例如 JSON.NET (Newtonsoft.Json)、各种网络库、数学库、数据结构库等，而无需手动下载 DLL 文件并添加到项目中。

**主要特点：**
- **集成度高：** 直接在 Unity 编辑器中操作，无需离开 Unity。
- **版本管理：** 方便地安装、更新和卸载 NuGet 包，处理依赖关系。
- **生态丰富：** 访问 NuGet 庞大的开源库生态系统。
- **兼容性：** 能够处理 Unity 的特殊编译环境。
    
### 为什么在 Unity 中使用 NuGetForUnity？
1. **访问丰富的 .NET 库：** 许多高质量、经过充分测试的 .NET 库并非专门为 Unity 设计，但它们的功能在游戏开发中同样有用。例如，你可能需要一个强大的 JSON 序列化库、一个高性能的数学库、或者一个用于特定数据处理的库。
2. **避免重复造轮子：** 社区中已经有成熟解决方案的功能，通过 NuGet 可以直接引入，节省开发时间。
3. **标准化依赖管理：** 对于熟悉 .NET 开发的团队来说，NuGet 提供了一致的包管理体验。
4. **简化团队协作：** 依赖项可以自动恢复，新成员克隆项目后可以快速设置好开发环境。
    
### 如何安装 NuGetForUnity？
NuGetForUnity 的安装通常通过两种方式：
1. **Unity Package Manager (UPM) 通过 Git URL 安装 (推荐)：**
    - 在 Unity 编辑器中，打开 Window > Package Manager。
    - 点击左上角的 + 按钮，选择 Add package from git URL...。
    - 输入 NuGetForUnity 的 Git 仓库地址，通常是：https://github.com/NuGetForUnity/NuGetForUnity.git
    - 点击 Add。

2. **手动下载 .unitypackage 文件：**
    - 访问 NuGetForUnity 的 GitHub Release 页面：https://github.com/NuGetForUnity/NuGetForUnity/releases。
    - 下载最新版本的 NuGetForUnity.unitypackage 文件。
    - 将下载的文件拖放到你的 Unity 项目中（或双击打开），然后导入所有内容。

安装完成后，你会在 Unity 编辑器顶部的菜单栏中看到一个名为 NuGet 的新菜单项。

### NuGetForUnity 的基本用法
当你在 Unity 项目中安装 NuGet 包后，NuGetForUnity 会将相关的 DLL 文件放置在项目中的特定文件夹（通常是 Assets/NuGetPackages 或类似路径），并自动处理 Unity 项目的引用。

对于新版 Unity（2019.4+，特别是 2021.2+），它会尝试将 NuGet 包的引用添加到 Assets/csc.rsp 文件中。这个文件是一个 C# 编译器响应文件，允许你向 Unity 的 C# 编译器传递额外的命令行参数，包括引用外部 DLL。
这是一个 csc.rsp 文件的例子：

```Code
-r:Assets/NuGetPackages/Newtonsoft.Json.13.0.3/lib/netstandard2.0/Newtonsoft.Json.dll
-r:Assets/NuGetPackages/SomeOtherPackage.1.0.0/lib/netstandard2.0/SomeOtherPackage.dll
```

**排除平台和架构：**
在某些情况下，NuGet 包可能包含针对不同平台（如 Windows, macOS, Linux）或不同架构（如 x86, x64, ARM）的 DLL。NuGetForUnity 通常会智能地选择正确的 DLL。如果遇到冲突或不必要的 DLL，你可以在 Unity Inspector 中选中这些 DLL，然后在 Platform settings 中将其设置为 Exclude platforms，以避免编译错误或文件膨胀。

### 相关的包管理知识
**1. 包管理器 (Package Manager)：**
包管理器是自动化软件开发中依赖管理过程的工具。它允许开发者声明项目所需的库和工具，然后自动下载、安装和管理这些依赖项。
- **NuGet (for .NET):** 微软官方支持的 .NET 平台包管理器，拥有最大的 .NET 库生态。
- **Unity Package Manager (UPM):** Unity 官方的包管理器，用于分发和管理 Unity 官方包、Asset Store 包和自定义本地包。
- **npm (for JavaScript):** JavaScript 生态系统中最流行的包管理器。
- **Maven/Gradle (for Java):** Java 生态系统常用的构建工具和包管理器。
- **pip (for Python):** Python 官方的包管理器。

**2. 依赖管理 (Dependency Management)：**
- **直接依赖：** 你的项目直接引用和使用的库。
- **间接依赖 (Transitive Dependencies)：** 你的直接依赖项所依赖的其他库。包管理器通常会自动解析和安装所有间接依赖。
- **版本冲突：** 当不同的依赖项需要同一个库的不同版本时，可能发生版本冲突。优秀的包管理器会尝试解决这些冲突，或者提供工具让你手动解决。
- **锁定文件 (Lock File)：** 许多包管理器会生成一个锁定文件（例如 NuGet 的 packages.lock.json 或 project.assets.json），记录了项目所有依赖项的精确版本。这确保了在不同环境中构建时，依赖项的版本一致性，提高了构建的可重复性。

**3. NuGet 包结构：**
一个 NuGet 包本质上是一个 .nupkg 文件，它是一个 ZIP 格式的压缩包，包含：
- **程序集 (Assemblies):** 编译好的 DLL 文件，这是实际的代码库。这些文件通常位于 lib 文件夹下，并按目标框架（Target Framework Moniker, TFM）组织，例如 lib/netstandard2.0、lib/net472 等。
- **元数据 (Metadata):** 描述包的信息，如名称、版本、作者、许可证、依赖项等。
- **内容文件 (Content Files):** 可能包含一些源代码、配置模板或静态资源。
    
**4. .NET Standard 和 .NET Framework：**
在 Unity 中使用 NuGet 包时，理解 .NET Standard 和 .NET Framework 的区别非常重要：
- **.NET Standard:** 是一个 .NET API 规范。它定义了一组可以在所有 .NET 实现（如 .NET Core、.NET Framework、Mono/Unity）中使用的 API。一个面向 .NET Standard 的库可以在任何支持该标准或更高版本的 .NET 平台上运行。**推荐 NuGet 包面向 .NET Standard 2.0 或 2.1，因为 Unity 最新版本（2021+）通常支持这些标准。**
    
- **.NET Framework:** 是微软早期开发的 Windows 平台专用 .NET 实现。许多旧的 NuGet 包可能只面向 .NET Framework 4.x。如果你的 Unity 项目运行在较新的 Scripting Runtime Version (例如 .NET Standard 2.1) 上，可能无法直接引用只面向 .NET Framework 的包。
    
当你安装 NuGet 包时，NuGetForUnity 会尝试选择与你 Unity 项目的 Scripting Runtime Version 兼容的程序集（DLL）。你可以在 Edit > Project Settings > Player > Other Settings 中查看和修改 Scripting Runtime Version 和 Api Compatibility Level。