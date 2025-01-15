---
title: "[[Unity的程序集划分]]"
type: Reference
status: done
Creation Date: 2024-04-28 09:48
tags:
---
Assembly Definitions and Assembly References are assets that you can create to organize your **scripts**into assemblies.
An assembly is a C# code library that contains the compiled classes and structs that are defined by your scripts and which also define references to other assemblies. 
==By default, Unity compiles almost all of your game scripts into the predefined assembly, **Assembly-CSharp.dll**. ==
This arrangement works acceptably for small projects, but has some drawbacks as you add more code to your project:
- Every time you change one script, Unity has to recompile all the other scripts, increasing overall compilation time for iterative code changes.
- Any script can directly access types defined in any other script, which can make it more difficult to refactor and improve your code.
- All scripts are compiled for all platforms.

By defining assemblies, you can organize your code to promote modularity（模块化） and reusability（可重用性）. Scripts in the assemblies you define for your project are no longer added to the default assemblies and can only access scripts in those other assemblies that you designate.
![[Pasted image 20240427191620.png|475]]
如上图，Main 引用了 Stuff，所以 Main 中的代码修改不会影响 Stuff 中的代码，同时，由于 Library 不依赖于任何其他程序集，所以你可以更轻松地在另一个项目中重复使用 Library 中的代码。
## Defining assemblies
1. 每个程序集单独创建一个文件夹，并在文件夹下创建一个 Assembly Definition Asset 来定义程序集属性
 ![[Pasted image 20240427193737.png|500]]
1. Unity takes all of the scripts in a folder that contains an Assembly Definition asset and compiles them into an assembly, using the name and other settings defined by the asset. Unity also includes scripts in any child folders in the same assembly, unless the child folder has its own Assembly Definition or Assembly Reference asset.
2. To include scripts from a non-child folder in an existing assembly, create an Assembly Reference asset in the non-child folder and set it to reference the Assembly Definition asset that defines the target assembly. For example, you can combine the scripts from all the Editor folders in your project in their own assembly, no matter where those folders are located.   ---将多个不同文件夹中的脚本放置到一个程序集中
## References and dependencies
When one type (such as a class or struct) uses another type, the first type is dependent on the second. When Unity compiles a script, it must also have access to any types or other code the script depends upon. Likewise, when the compiled code runs, it must have access to the compiled versions of its dependencies.
If two types are in different assemblies, an assembly containing a dependent type must declare a reference to the assembly containing the type upon which it depends. 声明引用需要在 Assembly Definition Asset 文件中添加对应程序集的引用
The Assembly Definition settings include:
- Auto Referenced： 预定义程序集（Assembly-CSharp.dll）是否引用程序集
- Assembly Definition References：引用其他数据集
- Override References + Assembly References：预编译（插件）程序集的引用
- No Engine References：引用 UnityEngine 程序集
### Default references
By default, the predefined assemblies reference all other assemblies, including：
- those created with Assembly Definitions (1) 
- precompiled assemblies added to the project as plugins (2). Unity中的预编译程序集通常是.dll（动态链接库）文件，其中包含了项目中的代码和依赖项的编译结果。这些程序集可以包括游戏逻辑、脚本、插件等，它们最终会被打包到生成的游戏或应用程序中。
- assemblies you create with an Assembly Definition asset automatically reference all precompiled assemblies (3):
![[Pasted image 20240427194812.png|473]]
>编译：编译是将源代码转换为可执行代码或者中间代码的过程。编译器将源代码翻译成机器语言或者中间代码，以便计算机能够理解和执行。编译器会将源代码中的语法和语义转换成目标平台所需的指令。
>
>**DLL（动态链接库）**：DLL 是一种包含可重用代码、数据和资源的文件类型。它们是用来存储函数、类、变量和资源的，这些可以被其他程序使用。DLL 提供了一种在不同程序之间共享代码的方式，这样可以减少代码的重复，并且方便了代码的维护和更新。
>
>关系：
>- 编译器在编译源代码时，会将代码中引用的函数和变量解析成地址或者符号。
>- 如果这些函数和变量是在 DLL 中实现的，编译器会生成对应的引用。
>- 当程序执行时，操作系统会加载程序需要的 DLL，并将其中的函数和变量的地址解析到内存中，使得程序能够调用这些函数和变量。
>- 因此，编译器和 DLL 之间的关系在于编译器需要知道如何调用 DLL 中的函数和变量，而 DLL 提供了这些函数和变量的实现。

In the default setup, classes in the predefined assemblies can use all types defined by any other assemblies in the project. Likewise, assemblies you create with an Assembly Definition asset can use all types defined in any precompiled (plug-in) assemblies.
### Cyclical references
A cyclical assembly reference exists when one assembly references a second assembly that, in turn, references the first assembly. Such cyclical references between assemblies are not allowed and are reported as an error with the message, “Assembly with cyclic references detected.”

Typically, such cyclical references between assemblies occur because of cyclical references within the classes defined in the assemblies. While there is nothing technically invalid about cyclical references between classes in the same assembly, cyclical references between classes in different assemblies are not allowed. If you encounter a cyclical reference error, you must refactor your code to remove the cyclical reference or to put the mutually referencing classes in the same assembly.

## 两个资产的区别
1. **Assembly Definition（程序集定义）asset**：
    - Assembly Definition（简称为"asmdef"）asset用于创建新的程序集，定义程序集的名称、依赖关系和编译选项。
    - 创建asmdef asset时，您可以选择包含特定目录中的脚本文件，并为这些文件定义一个独立的程序集。
    - asmdef asset本身是一个文件，用于描述一个独立的代码程序集，其中可以包含一组相关的脚本文件。
    - asmdef asset 定义了程序集的基本属性，例如名称、版本、平台等。

1. **Assembly Definition Reference（程序集定义参考）asset**：
    - Assembly Definition Reference（ADR）asset用于引用现有的程序集定义（asmdef）。
    - 创建ADR asset时，您可以指定已存在的asmdef asset，以及选择是否在当前程序集中添加额外的脚本文件。
    - ADR asset本身不会创建新的程序集，而是将现有的程序集引入到当前程序集中，并允许在其中添加其他脚本文件。
    - ADR asset用于管理程序集之间的依赖关系，确保编译时能够正确地引用其他程序集中的类和方法。

综上所述，Assembly Definition asset用于创建新的独立程序集，而Assembly Definition Reference asset用于引用现有的程序集并管理程序集之间的依赖关系。它们共同提供了一种灵活的方式来组织和管理项目中的代码程序集。