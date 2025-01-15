---
title: "[[unity内存管理]]"
type: Literature
status: done
Creation Date: 2024-05-27 09:43
tags:
---
## 1、什么是内存
操作系统有物理内存和虚拟内存两个概念：
### 物理内存
物理内存也就是我们真是的硬件设备，例如内存条。
**CPU访问内存是一个慢速过程。**
访问过程具体为：先访问Cache，Cache包含L1，L2，L3，也就是一级缓存，二级缓存和三级缓存，若在这些缓存里全没找到我们要的数据，再去访问内存，接着会把找到的数据存放到Cache中，完成一次操作。
在Cache中没有找到数据，我们称之为**Cache Miss**。因此**过多的Cache Miss就会导致大量的内存和Cache的IO交换，浪费大量时间**。
因此我们需要尽量减少 Cache Miss，来提高访问速度，Unity 为此提出了**ECS**方案，有兴趣的小伙伴可以看看之前有关 [ECS](https://link.zhihu.com/?target=https%3A//blog.csdn.net/wangjiangrong/article/details/106850847) 介绍的文章，它们可以将存储在内存中的不连续数据，变为连续的数据，从而降低 Cache Miss 的概率。

**台式设备和移动设备内存架构的差异**
1. 首先移动设备没有独立显卡。
2. 移动设备没有独立显存（显存的作用是用来存储显卡芯片处理过或者即将提取的渲染数据），所有在移动端数据内存和显存是同一块内存。所以有可能我们游戏占用的内存并不大，但是依旧爆内存了，其实是因为显存分配不出来了。这种情况，我们可以去查看一下Log，例如Android会有一个 OpenGL Error：Out Of Memory。
3. 移动设备的 CPU 面积更小，因此会导致缓存级数更少，大小也更小，例如一般的台式机三级缓存可能有8-16M，而移动设备则只有2M 左右。
### 虚拟内存
虚拟内存是利用磁盘空间虚拟出的一块逻辑内存，用作虚拟内存的磁盘空间被称为交换空间（Swap Space）。
**内存交换**
操作系统在使用内存不够的情况下，会尝试把一些不用的内存（Dead Memory）交换到硬盘上，从而节省出更多的物理内存。这个操作我们称之为**内存交换**，它会占用大量的硬盘空间。
**然而移动设备不做该操作**，因为移动设备的IO速度很慢，而且移动设备的可存储物（例如sd卡，内存芯片等）的可擦写次数也比硬盘少很多，会影响使用寿命。
**内存压缩**
在IOS中（Android没有）会将不活跃的内存压缩起来存储到一个特定空间里，来节省出物理内存空间，来给活跃的app使用，这个操作称之为**内存压缩**。（可以查看XCode的Virtual Memory）
### 内存寻址范围
内存寻址范围也称寻址空间，指的是CPU对于内存寻址的能力（最大能查找多大范围的地址）。数据在内存中存放是有规律的，CPU在运算的时候需要把数据提取出来就需要知道数据在那里，这时候就需要挨家挨户的找，这就叫做**寻址**，但如果地址太多超出了CPU的能力范围，CPU就无法找到数据了。
内存寻址范围和 Memory Controller（内存控制器）有关，和运算位数（32位或64位）无直接关系。当然一般情况下，64位的 CPU 寻址范围更大。
## 2、Android 内存管理
### 基本单位Page
Android是基于Linux操作系统，其内存基本单位称为：Page，默认4K为一个page。因此内存回收和分配的时候一般已4k进行处理，但是并不意味着所有的数据都是4k对齐的。

### 用户态和内核态
Android内存分用户态和内核态：
用户态：只能受限的访问内，所有app都是运行在用户态上的。
内核态：cpu可以访问内存的所有数据。
内核态的内存，用户态是严格不许访问的，例如一些Error Access，可能是指针飘到内核态上了。
### 内存杀手
Android 有一个内存管理工具：**Low Memory Killer**，当内存不足时，会清理内存，在 Android 上常见的一些后台 app 消失，一些手机服务消失，手机重启或者是 app 崩溃闪退等都和它有关。
### Android 应用分层

首先我们来了解下Android的应用分层，这也是杀手的追杀路线（会从最底层往上杀）

|             |                       |
| ----------- | --------------------- |
| Native      | 系统内核，例如adbd           |
| System      | 系统级应用，例如system server |
| Persistent  | 用户级应用，例如电话，蓝牙，wifi    |
| Foreground  | 前台应用，当前正在使用的Activity  |
| Perceptible | 辅助类应用，例如搜索，音乐，键盘      |
| Service     | 一些驻后台的线程服务，例如云服务，垃圾回收 |
| Home        | 桌面                    |
| Previous    | 上一个使用的应用              |
| Cached      | 后台应用                  |

若此时我们的手机内存不足，杀手会一层层的从下往上杀，直到内存足够为止。同时每杀一层都会造成一定的现象，例如：
- Cached 或 Previous 被杀，会导致再次使用之前应用的时候，应用重启。
- Home被杀导致桌面图标重建，或者壁纸不见了。
- Perceptible被杀会导致音乐停止等。
- Foreground被杀导致当前应用闪退。
- System被杀，就会导致手机重启。
- Native属于系统本身，因此是无法杀到的。

因此通过这些现象，我们就可以了解自己的 app 到底对内存的使用到了一个什么程度。例如使用自己 app 时，再返回上个 app 时导致上个 app 重启，说明杀手已经杀到了 Previous 层。
### 内存指标
首先我们要了解在计算app使用了多少内存时，系统需要统计共享页面（shared pages）。App在访问同一个service或者library的时候会共享内存页面。比如，Google地图和一个游戏app可能会共享一个定位服务。

常见的内存指标有如下三个

|   |   |
|---|---|
|Resident Set Size（RSS）|当前app所占用的所有内存，如果你的app通过Google Play Services分配了内存，那这部分内存也归你所有。（例如上面的例子中定位服务所占的内存就归自己app所有）|
|Proportional Set Size（PSS）|与RSS不同，通过Google Play Services分配的内存会平摊到所有呼叫这个服务的app上。（例如上面例子中定位服务所占的内存就会平摊到所有使用到的app上）|
|Unique Set Size（USS）|只有app自己占得内存，不算Google Play Services分配的内存（例如上面例子中，就不算算上定位服务所占的内存）|

一般来说内存占用大小有如下规律：RSS >= PSS >= USS

注：可能你的USS很低，但是由于调用了Google Play Services，导致PSS很高。
我们可以通过**procrank指令**来查看各种内存指标，例如
![](https://pic4.zhimg.com/80/v2-7367759ecf45a5b578eb4aa1ed8c79a7_720w.webp)
​可以帮助我们分析应用内存使用，一般我们要做 USS 的优化，以及避免在 PSS 上造成更大的压力。

## 3、Unity 内存管理

### Unity是一个C++引擎
Unity是一个C++引擎，并不是C#引擎，底层代码全部是由c++写的，除了一些Editor里面的Services可能会用到NodeJS这些网络的语言，Runtime里面用到的每一行Unity底层代码全是C++的。

Unity实际上分为三层：
- 最底层是我们的Runtime，全是Native C++代码。
- 最上层是我们的C#，Unity自己有一些C#，例如Unity的Editor是用C#写的，还有些Package也是C#写的。
- 中间还有一层我们叫Binding，可以看见很多的**.bindings.cs**文件（基于C#的binding语言，一开始是Unity自定义的一种语言），这些文件的作用就是把C++和C#联系在一起，为我的C#层提供所有的API。

因此我们平时使用Unity时看见的C# API，都是在Binding层中自定义的。这些文件底层运行的时候还是C++，只是个Wrapper（封装）。
最早我们的用户代码是运行在C#上，是MonoRuntime。但是现在可以通过IL2CPP将其转成C++代码，所有现在几乎没有纯正的C#在运行了。
Unity的VM（虚拟机：Virtual Machine）依旧还是存在，主要用于跨平台，有了一层VM抽象后，跨平台的工作会容易很多，IL2CPP本身也是个VM。
### 内存管理简介
Unity内存按照分配方式分为：**Native Memory**（原生内存）和**Managed Memory**（托管内存）。Native Memory并不会被系统自动管理，需要我们手动去释放。而Managed Memory的内存管理是自动的，会通过GC来释放。

此外Unity在Editor和Runtime下，内存的管理方式是不同的，除了内存大小不同，内存的分配时机以及分配方式也可能不同。例如Asset，在Runtime时，只有我们Load的时候才会进内存。而Editor模式下，只要打开Unity就会进内存（所以打开很慢）。因此后续有推出**Asset Pipeline 2.0**，它会一开始导入一些基本的Asset，剩下的Asset只有你使用的时候才会导入。

Unity按照内存管理方式分为：**引擎管理内存**和**用户管理内存**。引擎管理内存即引擎运行的时候自己要分配一些内存，例如很多的Manager和Singleton，这些内存开发者一般是碰触不到的。用户管理内存也就是我们开发者开发时使用到的内存，需要我们重点注意。
### Untiy检测不到的内存
即 Unity Profilter 无法检查到的内存，例如用户分配的 Native 内存。比如自己写的 Native 插件（C++插件）导入 Unity，这部分 Unity 是检测不到的，因为 Unity 没法分析已编译的 C++是如何分配和使用内存的。还有就是**Lua**，它完全自己管理的，Unity 也没法统计到它内部的情况。

## 4、Native Memory 介绍
### Allocator与Memory Lable
Unity在里面重载了C++的所有分配内存的操作符，例如alloc，new等。每个操作符在被使用的时候要求有一个额外的参数就是**Memory Lable**，Profilter中查看Memory Detailed里的Name很多就是Memory Label。它指的就是当前的这一块内存要分配到哪个类型池里。

### GetRuntimeMemory
Unity在底层会用**Allocator**，使用重载过的分配符分配内存的时候，会根据Memory Lable分配到不同的Allocator池里面。每个Allocator池，单独做自己的跟踪。当我们要在Runtime去Get一个Memory Lable下面池的时候，可以从对应的Allocator中取，可以从中知道有什么东西，有多少兆。

### NewAsRoot
前面提到的Allocator的生成是使用**NewAsRoot**，生成一个所谓的**Memory Island**，它下面会有很多的子内存。例如一个Shader，当我们加载一个shader进内存的时候，首先会生成一个shader的Root，也就是Memory Island。然后Shader底下的数据，例如Subshader，Pass，Properties等，会作为该Root底下的成员，依次的分配。所以我们最后统计Runtime的内存时，统计这些Root即可。

### 会及时返还给系统
因为是C++的，所以当我们去delete或free一个内存的时候，**会立刻返回给系统。这和托管内存堆不一样，需要GC后才返回。**

## Managed Memory介绍
### VM内存池
即Mono虚拟机的内存池，我们的内存以Block的形式管理，当一个Block**连续6次**GC没有被访问到，这块**内存会被返回给系统**，条件苛刻，比较难触发。

### GC
**GC的机制考量**

|   |   |
|---|---|
|Throughput（回收能力）|一次GC能收回多少内存|
|Pause times（暂停时长）|GC时对主线程的影响会多大（卡顿）|
|Fragmentation（碎片化）|对整体内存池的碎片化影响多少|
|Mutator overhead（额外消耗）|GC时的消耗，GC时需要做很多的统计会产生消耗|
|Scalability（可拓展性）|拓展到多核多线程会不会有什么bug|
|Portability（可移植性）|在不同的平台上是否可以使用|

**Boehm**
Unity用的Boehm GC，简单粗暴，不分代。
- Non-generational（非分代式），即全都堆在一起，因为这样会很快。分代的话就是例如大内存，小内存，超小内存分在不同的内存区域来进行管理（**SGen GC**的设计思想）。
- Non-Compacting（非压缩式），即当有内存被释放的时候，这块区域就空着。而压缩式的会重新排布，填充空白区域，使内存紧密排布。

上面的形式就会导致我们的内存碎片化，可能我们当前的内存并不大的时候，添加一块较大内存时，却没有任何的一个空间放得下（即使整体的空间足够），导致内存扩充很多。因此建议先操作大内存，然后操作小内存。
碎片化内存之间空出的内存可能就成为僵尸内存。这种情况实际上并不是内存泄露，因为这些内存并没有被泄露，泄露指这块内存没有任何人可以访问和管理，但实际上这块内存一直在内存池里。
IL2CPP GC 机制是 Unity 重新写的，属于一种升级版的 Boehm。

**Incremental GC**
Incremental GC（渐进式GC）：[https://blogs.unity3d.com/2018/11/26/feature-preview-incremental-garbage-collection/](https://link.zhihu.com/?target=https%3A//blogs.unity3d.com/2018/11/26/feature-preview-incremental-garbage-collection/)

主要解决主线程卡顿的问题，现在进行一次GC主线程被迫要停下来，遍历所有的Memory Island，决定哪些要被GC掉，会造成一定时间的主线程卡顿。Incremental GC把前面暂停主线程的事分帧做了，这样主线程不会出现峰值。

### 堆栈（Stack）和堆积（Heap）

我们看下Unity内存中重要的两部分，堆栈和堆积，因为只有了解了它们，我们才能知道应该如何优化内存，提高性能。

**堆栈：**

==堆栈是内存中存储**函数**和**值类型**的地方。==
例如我们调用一个函数A，会将这个函数体与函数收到的参数放入到堆栈中，若在函数A中调用函数B，同样会把函数B存放到堆栈中。当函数B运行结束，会将其从堆栈中移除，然后当A运行结束，把A从堆栈中移除。

因此我们在看Debug信息的时候，就会发现Log里面能够做到一层层的方法回溯，方便我们查看整体的调用过程，这也就是**堆栈回溯**。

由于是堆栈的结构，因此不会遇到碎片化或是垃圾收集（GC）的问题。但是可能会碰见堆栈溢出的问题，比如调用了太多的函数导致一直push东西进堆栈，占据越来越多的内存空间，导致**堆栈溢出**。

**堆积：**
==堆积是内存中另一个区域，要比堆栈大，我们将所有的**引用类型**存放在这。通常我们每创建一个新的对象，会在堆积中找到下一个足够存放的空位置，将其存储。但是当我们销毁对象后，**内存空间不会马上释放出来**，而是标记成未使用，之后垃圾收集器会释放这部分空间。==

**对象实例化和摧毁的过程其实很慢**，所以我们要尽可能地避免在堆积中配置内存的行为。如果我们需要的内存比之前已经配置好的还多，在放不下的情况下，**堆积会膨胀，并且每次都增长两倍，且不会再缩回去**，过大的堆积就会影响到我们游戏的性能。当我们在堆积中释放了一些占用空间小的对象，而后添加一些占用空间大的对象时，由于前面释放的空间不足以存放下，就会导致这些空间空出来，使得内存的使用情况就变得断断续续起来，这也就是内存的**碎片化**，同样降低我们的游戏性能。

而我们前面所提到的GC就是在堆积上进行的，每一次GC，都会遍历堆积上所有的对象，找到需要释放的东西，也就是没有被引用的对象，然后将其释放。但是有时候我们的一些错误引用，导致一些我们希望释放掉的对象没有被GC掉，那么就会造成**内存泄漏**。

假如游戏玩到一半，GC必须要释放数十或数百个游戏对象的内存，那么这会对你的游戏过程造成一个负载峰值，我们要避免这样的负载峰值。

---

## 优化 Native Memory

以下东西都是和我们Native Memory相关的，**使用不当可能导致Native Memory的增长**，这块内容也就和我们的性能优化相关了。
### Scene
导致Native Memory增长的原因，最常见的就是Scene。因为是c++引擎，所有的实体最终都会反映在c++上，而不会反映在托管堆上。所以当我们构建一个GameObject的时候，实际上在Unity的底层会构建一个或多个object来存储这一个GameObject的信息（Component信息等）。所以当一个Scene里面有过多的GameObject存在的时候，Native Memory就会显著的上升，甚至可能导致**内存溢出**。

注：当我们发现Native Memory大量上升时，可以先着重检查我们的Scene。
### Audio
**DSP Buffer：**DSP Buffer，是指一个声音的缓冲，当一个声音要播放的时候，需要向CPU去发送指令。如果声音的数据量非常的小，会造成频繁的向CPU发指令，造成IO压力。在Unity的**FMOD声音引擎**里面，一般会有一个Buffer，当Buffer填充满了才会去向CPU发送一次播放声音的指令。

DSP Buffer大小的设置一般会导致两种问题：
- 设置的值过大会导致声音的延迟，因为填充满需要很多的声音数据，当我们声音数据不大的时候，就会产生延时。
- 设置的值太小会导致CPU负担上升，因为会频繁的发送。
![|500](https://pic2.zhimg.com/80/v2-c0c2c479b0b7a905edc114a7f6a480ad_720w.webp)

DSP Buffer设置
**Force To Mono：** ​这个选项作用是强制单声道，很多声音为了追求质量会设置成双声道，导致声音在包体和内存中，占用的空间加倍，但是95%以上的声音，两个声道是完全一样的数据。**因此对声音不是很敏感的项目建议勾选此项**，来降低内存的占用。

![|223](https://pic1.zhimg.com/80/v2-aed8faecef34d2e3cd2d94475e36fad8_720w.webp)

Force To Mono设置
**Compression Format：** 不同的平台有不同的声音格式的支持，IOS 对 MP3有硬件支持，Android 暂时没有硬件支持。**建议 IOS 适合使用 ADPCM 和 MP3格式，Android 适合使用 Vorbis 格式。**
![|259](https://pic3.zhimg.com/80/v2-9d4a617188e8cd35b63df9226576a44a_720w.webp)

Compression Format设置
**Load Type：**决定声音在内存中的存在形态：

|   |   |   |
|---|---|---|
|Decompress On Load|当audio clip被加载时，解压声音数据|适用于小型音频文件（< 200kb）|
|Compressed In Memory|声音数据将以压缩的形式保存在内存当中|适用于中型音频文件（>= 200kb）|
|Streaming|从磁盘读取声音数据|适用于大型音频文件，例如背景音|

注：例如Decompress On Load，要求文件必须小于200kb，因为内部内存管理的问题，如果是大于200kb的文件，那么也还是只会被分配到不足200kb的内存。
![|357](https://pic3.zhimg.com/80/v2-98bd5233047c363a35395c252e25cc66_720w.webp)

Load Type设置
**Bitrate：** 我们可以对音频文件本身进行压缩，降低文件的**比特率**（bitrate），前提音频品质不会被破坏太严重。

![|373](https://pic4.zhimg.com/80/v2-e58d2583f833d77137679cb232b9b853_720w.webp)

**静音处理相关：** 一般游戏中都会有静音的设置，我们往往我们只是把 AudioSource 或 Mixer 的音量设置为0，这样还是会造成不必要的内存和 CPU 占用，因为关音量并不会释放音频的内存。因此建议在内存中卸载音频相关的来源或是内存中的音频文件，将 AudioSource 组件 Disable，同时有个上层管理系统负责过滤和音频相关的 API 调用。当然卸载和重新载入音频的成本也很高，要是玩家频繁的开启和关闭静音的话，就不适用了，当然了一般情况下玩家不会这么操作。

### Code Size
代码也是占内存的，需要加载进内存执行。**模板泛型的滥用**，会影响到Code Size以及打包速度（IL2CPP编译速度，单一一个cpp文件编译的话没办法并行的）。例如一个模板函数有四五个不同的泛型参数（float，int，double等），最后展开一个cpp文件可能会很大。因为实际上c++编译的时候我们用的所有的Class，所有的Template最终都会被展开成静态类型。因此当模板函数有很多排列组合时，最后编译会得到所有的排列组合代码，导致文件很大。

### AssetBundle
**TypeTree：** Unity 前后有很多的版本，不同的版本中很多的类型可能会有数据结构的改变，为了做数据结构的兼容，会在生成数据类型序列化的时候，顺便生成一个叫**TypeTree**的东西。就是当前这个版本用到了哪些变量，它们对应的数据类型是什么，当进行反序列化的时候，根据 TypeTree 去做反序列化。如果上一个版本的类型在这个版本没有，那 TypeTree 里就没有它，所以不会去碰到它。如果有新的的 TypeTree，但是在当前版本不存在的话，那要用它的默认值来序列化。从而保证了在不同版本之间不会序列化出错。

在Build AssetBundle的时候，有开关可以关掉TypeTree。
```text
BuildAssetBundleOptions.DisableWriteTypeTree
```
当我们当前AssetBundle的使用，和Build它的Unity的版本是一模一样的时候，就可以关闭。这样，一可以减少内存，二AssetBundle包大小会减少，三build和运行时会变快，因为不会去序列化和反序列化TypeTree。

**压缩方式（Lz4和 Lzma）：** 现在 Unity 主推 Lz4（也就是 ChunkBased，BuildAssetBundleOptions.ChunkBasedCompression），Lz4非常快，大概是 Lzma 的十倍左右，但是平均压缩比例会比 Lzma 差30%左右，即包体可能会更大些。Lz4的算法开源。

Lzma基本可以不用了，因为Lzma解压和读取速度都会非常慢，并且占大量的内存，因为不是ChunkBased，而是Stream，也就是一次全解压出来。而ChunkBased可以一块一块解压，每次解压可以重用之前的内存，减少内存的峰值。

**大小和数量：** AssetBundle 分两部分，一部分是头（用于索引），一部分是实际的打包的数据部分。如果每个 Asset 都打成一个 AssetBundle，那么可能头的部分比数据还大。

官方建议一个AssetBundle，在1-2M，但是现在进入5g时代的话，可以适当加大，因为网络带宽更大了。

### Resource
Resource文件夹里的内容被打进包的时候会做一个红黑树（R-B Tree）用做索引，即检索资源到底在什么位置。所以**Resource越大，红黑树越大，它不可卸载，并在刚刚加载游戏的时候就会被一直加在内存里，极大的拖慢游戏的启动时间**，因为红黑树没有分析和加载完，游戏是不会启动的，并造成持续的内存压力。所以建议不要使用Resource，使用AssetBundle。

### Texture
例如下图中左右两边使用的都是相同的模型与贴图，但是最终所占的磁盘大小却差了很多，就是因为一些设置导致的。

![](https://pic2.zhimg.com/80/v2-d86dc5be8582ea5af3e89b77af989009_720w.webp)

**Upload Buffer：** 在 Unity 的 Quality 里设置如图，和声音的 Buffer 类似，填满后向 GPU push 一次。
![|374](https://pic3.zhimg.com/80/v2-23c28e5a0d486cfcbb5eec8055f9db3e_720w.webp)

**Read/Write：** 没必要的话就关闭，正常情况，Texture 读进内存解析完了搁到 Upload Buffer 里之后，内存里那部分就会 delete 掉。除非开了 Read/Write，那就不会 delete 了，会在显存和内存里各一份。前面说过手机内存显存通用的，所以内存里会有两份。
![|143](https://pic1.zhimg.com/80/v2-7065d74dd94aac8adaf8158ef6f70644_720w.webp)
​**Mip Maps：** 例如 UI 元素这类相对于相机 Z 轴的值不会有任何变化的纹理，关闭该选项。
![|140](https://pic4.zhimg.com/80/v2-74a0fdbd722a95383d8a993c4f6beaab_720w.webp)
**Format：** 选择合适的 Format，可减少占用的空间。
![|293](https://pic4.zhimg.com/80/v2-5cecb7b39881433188258f34f2cc20c3_720w.webp)
​​**alpha：** 对于不透明纹理，关闭其 alpha 通道。
![|280](https://pic1.zhimg.com/80/v2-2e44c102cc98cb7e4e18841b5efc147c_720w.webp)
​​**Max Size：** 根据平台不同，纹理的 Max Size 设成该平台最小值。
**POT：** 纹理的大小尽量为2的幂次方（POT），因为有些压缩格式可能不支持非2的幂次方的。
**合并：** 尽量将多张纹理合并成为大图。
**压缩：**
**Android设备**运行平台要求支持**OpenGL ES 3.0**的使用**ETC2**，RGB压缩为RGB Compressed ETC2 4bits，RGBA压缩为RGBA Compressed ETC2 8bits。需要兼容**OpenGL ES 2.0**的使用**ETC**，RGB压缩为RGB Compressed ETC 4bits，RGBA压缩为RGBA 16bits。（压缩大小不能接受的情况下，压缩为2张RGB Compressed ETC 4bits）

**IOS设备**运行平台要求支持**OpenGL ES 3.0**的使用**ASTC**，RGB压缩为RGB CompressedASTC 6x6 block，RGBA压缩为RGBA Compressed ASTC 4x4 block。对于法线贴图的压缩精度较高可以选择RGB CompressedASTC 5x5 block。需要兼容**OpenGLES 2.0**的使用**PVRTC**，RGB压缩为PVRTC 4bits，RGBA压缩为RGBA 16bits。（压缩大小不能接受的情况下，压缩为2张RGB Compressed PVRTC 4bits）

![|500](https://pic1.zhimg.com/80/v2-d5f6a809657346791084b5045903f77c_720w.webp)

参考：

[Ssiya：[2018.1]Unity贴图压缩格式设置45 赞同 · 4 评论文章![](https://pic3.zhimg.com/v2-191b823d7dde669a563a5513bfb766a6_180x120.jpg)](https://zhuanlan.zhihu.com/p/113366420)

  

### Mesh
**Read/Write：** 同 Texture，若开启，Unity 会存储两份 Mesh，导致运行时的内存用量变成两倍。
**Compression：Mesh Compression**是使用压缩算法，将Mesh数据进行压缩，结果是会**减少占用硬盘的空间**，但是在Runtime的时候会被解压为原始精度的数据，因此**内存占用并不会减少**。
需要注意的是有些版本开了，实际解压之后内存占用大小会更严重。

![|263](https://pic1.zhimg.com/80/v2-583df00c8dc9c5e5a888d857458ada90_720w.webp)
​​**Rig：** 如果没有使用动画，请关闭**Rig**，例如房子，石头这些。
![|280](https://pic1.zhimg.com/80/v2-813aae415ebb3fb5dd717e4878aae4c4_720w.webp)
​​**Blendshapes：** 如果没有用到 Blendshapes，也关闭。
![|362](https://pic2.zhimg.com/80/v2-47942f3ede972b0e8b45b4a3b1a63e41_720w.webp)
**Material设置：**如果Material没有用到法向量和切线信息，关闭可以减少额外信息。
![|299](https://pic3.zhimg.com/80/v2-84634099ac913f7a7a7032bf0e03fef6_720w.webp)
### Assets
和整个的Asset管理有关系，在unity官网上有个关于资源管理的文章。
[https://docs.unity3d.com/Manual/MobileOptimizationPracticalGuide.html​docs.unity3d.com/Manual/MobileOptimizationPracticalGuide.html](https://link.zhihu.com/?target=https%3A//docs.unity3d.com/Manual/MobileOptimizationPracticalGuide.html)

## 优化 Managed Memory

### Destroy与null
用Destroy，别用null，显示的调用Destroy才能真正的销毁掉。
### Class和Struct
根据具体使用情况选择Class或Struct。

### 减少装箱拆箱操作
例如LINQ和常量表达式以装箱的方式实现，String.Format()也常常会产生装箱操作等。

### 对象池
虽然VM自己有内存池，但是我们还是需要自己使用内存池来管理。

在游戏程序中，创建和销毁对象事很常见的操作，通常会通过 **Instantiate** 和 **Destroy** 方法来实现，如果频繁的进行这些操作，GC的时候会导致负载很重，因为会有大量的已摧毁对象的存在，不仅会造成CPU的负载峰值，还可能导致堆积碎片化。因此我们可以使用对象池来处理这类问题。

使用对象池时需要注意，要决定对象池的大小，以及一开始要产生多少数量的对象在池中。因为如果你需要的对象数量多过池中现有的，就必须将对象池变大，扩的太大可能造成浪费，扩的小可能又造成频繁的添加。

### 闭包和匿名函数
所有的匿名函数和闭包在c#编IL代码时都会被new成一个Class（匿名class），所以在里面所有函数，变量以及new的东西，都是要占内存的。

### 协程
协程属于闭包和匿名函数的特例，游戏开始启动一个协程直到游戏结束才释放，错误的做法。因为协程只要没被释放，里面的所有变量，即使是局部变量（包括值类型），也都会在内存里。建议用的时候才生产一个协程，不用的时候就丢掉。

### 配置表
一个游戏，策划往往会通过excel配置很多的配置表，然后我会在游戏中加载这些excel来读取其中的数据。但是如果excel数量非常的庞大，我们最好不要一下子全丢到内存里，建议分关加载等。

### 单例
慎用单例，且不要什么都往里放，因为里面的变量会一直占用内存。

### Scriptable Objects
假设我们有一个控制敌人的组件，名叫Enemy，代码如下：
```text
public class Enemy : MonoBehaviour
{
    public float maxSpeed;
    public float attackRadius;
}
```

这个组件挂载在每个敌人身上，但是其中这两个浮点数（maxSpeed 和 attachRadius）的数值都是不变的。那么当场景中存在很多的敌人时，每次生成敌人的时候，这些数据就会重复一份。

所以即使所有数据都一样，这两个浮点数还是重复的出现在有此脚本的对象上。所以建议改用Scriptable Objects，这样就只会耗费一组这样数据的内存，代码如下：
#TODO serverconfig 是不是就是通过这样的方式来写的?????
```text
public class EnemyConfiguration : ScriptableObject
{
    public float maxSpeed;
    public float attackRadius;
}
public class Enemy : MonoBehaviour
{
    public EnemyConfiguration enemyConfiguration;
}
```

### 变量or属性

通常我们为了封装安全性，开发时会选择使用属性（getter/setter），而属性本质上是函数的调用，前面提到调用函数时，会在堆栈上分配内存，因此调用属性也是如此。当调用多次时，花费在堆栈中的时间就会增加。当然了，一般来说问题不大，但是如果在使用频繁的循环体中使用属性，可能就需要针对性的优化。

我们可以通过宏命令进行处理，例如在开发时使用属性，发布版本时使用变量，如下：

```text
#if DELELOPMENT_BUILD
    int m_health;
    public int health { get => m_health; }
#else
    public int health;
#endif
```

### 缓存一些Hash值
在我们想要在运行时修改动画或者材质的时候，可以使用下面方法来实现

```text
animator.SetTrigger("Idle");
material.SetColor("Color", Color.white);
```

这类方法往往也可以通过索引来作为参数，使用字符串只是能显示的更加直观，但是当我们传递字符串时，程序内部会进行一些处理，频繁调用的话可能就会造成性能的消耗。因此我们可以先找到对应的索引，并将其缓存起来，供后续使用，如下：

```text
int idleHash = Animator.StringToHash("Idle");
animator.SetTrigger(idleHash);
int colorId = Shader.PropertyToID("Color");
material.SetColor(colorId, Color.white);
```

### 缓存引用对象

例如我们常常会在游戏运行的时候去查找一些对象，**GameObject.Find**与其他所有关联的方法，需要遍历所有内存中的游戏对象以及组件，因此在复杂场景中，效率会很低。**GameObject.GetComponent**，会查询所有附加到GameObject上的组件，组件越多，GetComponent的成本就越高。若使用的是**GetComponentInChildren**，随着查询变复杂，成本会更高。

==因此不要多次查询相同的对象或组件，而且查询一次后将其缓存起来，方便后续的使用。==

---

前面我们基本上介绍了内存的概念以及和内存直接相关的一些优化方法，当然了，优化除了优化内存意外还有很多其他的优化，例如DrawCall，算法的时间复杂度等，接下来我们看看其他方面相关的一些优化。

## 图像（Graphics）的一些优化建议

基本上当Unity渲染游戏图像时，会调用 **draw call** 来对GPU下指令，让场景能成功渲染。对象，材质和纹理越多，处理起来需要的时间也越多。所以过多的drawcall就会影响游戏的优化，这对于瓶颈在GPU上的游戏影响特别大，也就是我们的游戏已经给GPU太大的压力了。

### 使用批处理：
我们可以使用**批处理**来尽量减少drawcall，使用批处理需要满足一些情况，例如，要批处理的对象必须引用一样的材质，并使用相同的纹理（纹理合并在这就很重要），但是使用的模型可以不一样。

**动态批处理：** 可以减少对于移动对象的 drawcall。只能用于**少于900个顶点**信息的情况，包含坐标、法线、uv0、uv1、切线。动态批处理每帧评估一次，由 CPU 负责。

**静态批处理：**  即对开启  static 标记的对象做批处理，在构建期完成。适用于绝大部分的静态 Mesh，因此任何不会动的对象都应标记为静态的。如果我们在运行时要添加静态对象，可以看一下 **StaticBatchUtility.Combine()** 的 API

有关SRP Batcher可以看下：
[SRP Batcher，Draw Call优化，Shader SRP Batcher compatible​blog.csdn.net/wangjiangrong/article/details/105518220![](https://pic2.zhimg.com/v2-fa4a63e6b3baaea5be76e7b472093bd5_180x120.jpg)](https://link.zhihu.com/?target=https%3A//blog.csdn.net/wangjiangrong/article/details/105518220)

### Cast Shadows

默认情况下，MeshRenderder组件的Cast Shadows是开启的。

![|312](https://pic1.zhimg.com/80/v2-c437d2e5b1870ac8a5f4356321bca948_720w.webp)

​阴影的渲染可以让游戏的光线增加真实度和深度感，但是某些情况下可能并不需要。在复杂场景中，可能会造成多余的阴影计算，阴影效果最后也看不见。

因此若场景有的对象是否有阴影对整体效果没有影响的话，就关闭这个选项。不计算阴影可以省下CPU时间。（具体渲染步骤可以在 Frame Debugger的Shadows.Draw中查看）

### 设置Light Culling Mask
![|308](https://pic4.zhimg.com/80/v2-7f7b3a74fafd378ffa53d563063166a7_720w.webp)
​在复杂场景中，许多光线紧靠彼此，你可能觉得光线不能影响特定对象。根据渲染流程的设置，场景中越多的光照，性能可能就会越差。因此我们要确保光照只影响特定的对象层（例如专门给角色打光的光源，设置成只影响角色），尤其是多光源和多对象彼此紧靠的时候。

### 避免使用手机原生分辨率
现在的手机分辨率非常的高，在手机呈现高分辨率可能会影响性能和手机过热的问题。因为会有大量的计算需求，如后期处理。如果游戏本身很耗GPU，高分辨率会恶化这些问题。建议使用 **Screen.SetResolution** 来降低游戏预设的解析设置（根据不同的设备来找到一些合适的值），来提高性能。

## UI的一些优化建议

### 显示与隐藏
如果这个 UI 显示隐藏比较频繁的话，UI 的隐藏我们可以使用将其移到 Canvas 外的方法，而不是利用 SetActive(false)的方法来隐藏。
### UI的批处理
如果UI元素会改变数值或是位置，会影响批处理，导致向GPU发送更多的drawcall。因此建议：
- 将更新频率不同的UI放在不同的Canvas上。
- 相同Canvas中的UI元素的Z值要相同，这样才不会打断批处理。
- 相同Canvas中的UI元素要使用相同的材质和纹理，材质或着色器可以有动态变换（例如一些特效），这不会影响批处理。
- 相同Canvas中的UI元素要使用相同裁剪矩阵。
### Graphic Raycaster

![|350](https://pic3.zhimg.com/80/v2-befd185b0e88bcac476895c14de5c60a_720w.webp)

​该组件是用来处理输入事件，默认挂载在每个Canvas上。有时不能互动的对象仍是canvas中的一部分，并附带了该组件，所以当每次鼠标或触控点击时，系统就要遍历所有可能接受输入事件的UI元素，就会造成多次的 “点落在矩形中” 的检查，来判断对象是否该作出反应。在UI很复杂的情况下，这个运算成本就会很高。因此建议确保只有可互动的Canvas才有该组件，节省CPU运行时间。
### 全屏UI的处理
游戏中可能会有些全屏UI（例如一些设置界面），会遮挡住场景物体或其他UI元素。然而它们即使被遮挡看不见，CPU和GPU还是会有消耗，因此建议：
- 3D场景完全被遮挡的话，关闭渲染3D场景的摄像机。
- 被遮蔽的UI，Disable这些Canvas，注意不是SetActive(false）。
- 尽可能的降低帧率，因为这些UI一般不需要刷新那么频繁。

## 其他一些优化
### GameObject的层次结构
某些情况下，场景中的物体可能有很深的嵌套结构，当我们对父节点的GameObject进行坐标转换时，就会产生**OnTransformChanged**事件，这消息会传递给该GameObject下所有子对象，即使这些对象没有任何渲染组件（也就是我们看不见任何变化），造成一些不必要的转换运算，包括平移，旋转和缩放。

此外，较深的结构也会导致在GC时，花费更多的时间在层级结构间遍历。

### 避免在Awake和Start中添加大量的逻辑
这对游戏启动很重要，Unity会在Awake和Start方法执行后渲染第一个画面，某些情况可能会导致启动画面或是载入画面需要花更长的时间渲染，因为你必须等每个游戏对象都完成Awake和Start的执行。同时若游戏启动时，黑屏太久，提包时可能会被退审。

### 删除空的Unity事件
Monobehaviour中的Start，Update这些方法即使是空的，也会带来些微的性能消耗，因此若为空，就删除它们。
### Accelerometer Frequency

![|500](https://pic1.zhimg.com/80/v2-940faec8dd3742eb1136f205cca49558_720w.webp)

​​这个设置在Project Settings->Player->IOS->Other Settings中，这个功能定义Unity从设备读取加速度仪信息的频率，在不需要加速仪的游戏中，将它启动或设置了高于需求的频率，会影响性能表现。因为读取硬件设备信息，会增加CPU的处理时间。

### 移动物体
Unity中有许多移动游戏对象的方法，例如 **transform.Translate**，如果对象需要碰撞判定，我们则会添加刚体和碰撞体，如果还是使用 transform.Translate 方法，会造成**PhysX物理引擎**整体重新计算，对于复杂的场景，成本可能很高。因此若要移动带有刚体的对象，使用**rigidBody.MovePosition**，并且要在**FixedUpdate**方法中执行。

建议使用transform.Translate就在Update中执行，使用rigidBody.MovePosition或AddForce方法在FixedUpdate中执行。

### 添加组件
在运行时调用**AddComponent**其实很没效率，尤其在一帧中多次启用这类调用。

当我们添加一个组件的时候，Unity会做下列操作：
- 先看组件有没有DisallowMultipleComponent的设置，如果有，就要去检查是否有同类型的组件已加入
- 然后检查RequireComponent设置是否存在，如果设置了，就代表这个组件需要别的组件同步加入（重复做添加组件的操作）
- 最后调用所有被加入的MonoBehaviour的Awake方法
上述这些步骤都**发生在堆积**上，所以可能会影响性能和增加GC的处理时间。
最好使用prefab
### 数据结构
也就是Array，List和Dictionary等，例如在Array或List中使用索引的成本很低，那么就适合要经常通过索引读取的情况。而要频繁增加和移除对象时，使用Dictionary是最合适的。