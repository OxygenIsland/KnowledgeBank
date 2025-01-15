---
title: "[[1、macOS系统如何将App安装至移动硬盘]]"
type: Literature
status: done
Creation Date: 2024-04-08 09:37
tags:
---
Win 软件在安装的时候，大多数软件会依赖一些库之类的，这些库可能会分布在系统里面，也可能分布在软件的安装目录下面，所以安装好一个 Win 软件之后，其安装目录下除了我们会直接双击运行的那个 EXE 文件外，还会有各种其它的文件。
其实软件安装也是 Win 上的一个表现，Mac 上是可以忽略安装这一步的，当然一些特殊的软件除外。在 Mac 上，基本上可以理解为一个软件就是一个文件（以 .app 为后缀的文件），这个文件可以随你所好，放置在任意的位置，不管是你的用户目录，还是 u 盘，或者移动硬盘都是可以的，你可以直接双击运行它，所以你想要变更应用程序的位置，可以先复制，然后将其粘贴过去，再删除原来位置的，用快捷键就是 Command + c 复制，然后 Option +Command + v 粘贴并且删除原来的（就是 win 的剪切然后再粘贴）。需要说明一点， Mac 的软件也有很多依赖库的，只不过它把这些库全打包在 app 里面了，app 文件其实就一个文件夹，感兴趣可以右键，然后显示包内容，你就明白，其实和 win 的差不多，只是 mac 在这方面的处理更加的对用户友好。

其实取决于软件。
大部分 Cocoa app 确实是可以随处放的。
但是，也有很多并非是直接拖动就可以安装的，而是要运行一个安裝程序一才能装好的。像一些专业软件很多都是这样的，PhotoShop、AutoCAD 之类的。

这个时候就需要一点 trick 了，针对每个软件的方法不一定一样，但大致思路就是把实际文件移到移动硬盘上，但是通过软链接一把文件链回原来的位置，这样才能保证软件运行不出错。很多调用都是默认在主目录一进行而不是根据. App 文件夹位置来的。很多软件除了在~/Library/Application Support 下有文件外，还会在别的地方有文件，多半是在~/Library 下，可能需要你自己装好了之后一一找到再进行以上操作。
举个例子：
假设有一个软件 A，它默认会在/Applications 目录下放一个A.app 文件（文件夹），以及会在
~/Library/Application Support/A 目录下放其它的必要文件。
假设你要把软件装到你的移动硬盘/olumes/MobileDisk 上，可以这么干：
```linux
#1.在移动硬盘上创建应用程序目录。
mkdir /Volumes/MobileDisk/Applications 

#2.把A.app移到移动硬盘上。
mv /Applications/A.app /Volumes/MobileDisk/Applications

#3.把A.app文件链接回内部硬盘。
ln -s /Volumes/MobileDisk/Applications/A.app /Applications

#4.在移动硬盘上创建库目录和Application Support目录。
mkdir -p /Volumes/MobileDisk/Library/Application\ Support 

#5.把A.app的Application Support目录移到移动硬盘上。
mv ~/Library/Application\ Support/A /Volumes/MobileDisk/Library/Application\ Support

#6.把A.app的Application Support/A目录链接回内部硬盘。
ln -s /Volumes/MobileDisk/Library/Application\ Support/A ~/Library/Application\ Support
```
