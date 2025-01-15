---
title: "[[URI]]"
type: Literature
status: done
Creation Date: 2024-02-18 13:52
tags:
---
URI（Uniform Resource Identifier 统一资源标识符），是互联网上用于标识和定位资源的重要概念，包括 URL（Uniform Resource Locator 统一资源定位符）和 URN（(Uniform Resource Name 统一资源名称）
![[Pasted image 20240218135241.png|475]]
## URN
URN（(Uniform Resource Name 统一资源名称，它命名资源但不指定如何定位资源）
## URL
 URL（Uniform Resource Locator 统一资源定位符, 负责定位资源）
### url 通用格式
**<协议>：//<用户名>：<密码>@<主机域名或者ip地址>：<端口号>/<路径>；<参数>？<查询>#<片段>**
其中最重要的是<协议><主机域名><路径>
url（统一资源定位符）的作用就是通过浏览器发送给服务器，告诉服务器我们想要什么资源在什么位置，并发送给我们的浏览器，通过上边的格式，我们举几个例子：
http://www.baidu.com:80/main/index.html
这是一个简单的例子，有协议 http，主机域名 www.baidu.com ，资源路径/main/index. Html，其它部分都可以省略
下面是一个复杂的例子，我们结合下边这个例子具体介绍每一部分的作用和用法
http://joe:password@www.baidu.com:80/main/index.html;type=a;color=b?Name=bob&id=123#main
#### 协议
访问的协议可以是 http（超文本传输协议）、ftp（文件传输协议）、rtsp（实时流传输协议）、telnet（远程登陆访问）等。每个协议都遵循上述格式，只是有些协议的一些部分没有，如 telnet 协议就没有<参数>，<查询>，<片段>这几部分。
#### 用户名和密码
例子中的用户名和密码是 joe：password。比如我们使用 ftp 协议传输时就需要输入用户名和密码，但是我们的 http 协议中，如果把用户名和密码就放在 url 里，那很不安全，所以一般放在 cookie 里，这里就不详细说了，总之就是不经常使用。
#### 主机域名或者 ip 地址、端口
例子中的主机域名和端口是 www.baidu.com ：80，http 协议的默认端口是 80，端口就是开放服务的地方，我的前边的文章有讲过。
Url 中除了使用主机域名，还可以用 ip 地址，如可以写做：http://163.177.151.109:80/main/index.html
#### 路径
路径就是文件路径，和我们文件管理器的命名方法一样，就是\\ /不一样
![[Pasted image 20240218142020.png|452]]
例子中的路径是/main/index.Html表示在根文件目录里的main文件夹里的index. Html 文件，“/”表示根目录，“./”表示该文件上一级目录。

路径有绝对路径和相对路径，在 html 网页中我们使用相对路径，浏览器会自动帮我们补全。比如我们在基础 html 网页 http://www.baidu.com/main/index.html 中写一个相对路径（./img.Jpeg），./意思是当前 main 目录下的文件，相当于我们访问 http://www.baidu.com/main/img.jpeg
#### 参数
参数（params）一般使用“；”与路径分开，如果有多个参数也使用“；”分隔开。例子中的参数有两个，分别是 type 和 color；type=a；color=b
我们访问一些资源，只有路径端口是不够的，有时候需要向解析 url 的应用程序提供参数才能去访问资源，如参数可能会定义传输格式等等。
#### 查询
查询（query）使用“？”与前边的东西分开，如果有多个查询的问题，需要使用“&”连接。
访问一些资源时，有些需要查询数据库进行搜索来缩小请求资源范围，就像我们查东西时指定关键字一样，例子中的查询语句是？Name=bob&id=123
意思是，在该路径下，查询 name=bob，id=123 的资源。
#### 片段
我们访问资源时，可以不直接访问该资源，而是访问资源的一部分。比如我们访问一本书，可以直接指定访问某一部分。片段用“#”与其它东西分开，后边写指定部分的名字。如例子中的#main ，表示访问资源/index. Html 中的名字叫做 main 的部分。
但，其实 http 服务器仍然是把整个对象资源发给你的浏览器，浏览器获得整个资源后，根据片段显示你要的资源。
#### Url 编码
先看看现实中的 url 编码。我们看 csdn 中的文章时，看一下文章的 url 就会发现有很多%和 16 进制数字，跟我们上边说的格式一点都不一样。
![[Pasted image 20240218143127.png]]
这是因为 url 要同一命名网上的所有资源，还要通过不同的协议传输这些资源，那么我们的 url 要避开别的协议的编码机制，成为独一、完整、可移植性、可读的安全编码。因此就出现了“转义”编码机制，这种转义表示法包括一个%和两个表示字符 ascii 码的 16 进制数。当我们的 url 中出现一些可能在传输时不安全，被别的机制编码的情况时，我们就提前使用“转义”编码机制进行编码
![[Pasted image 20240218143227.png|500]]
当我们的 url 有“~” “ %”时，要给他们编码，下边的图显示了哪些字符需要编码：
![[Pasted image 20240218143245.png|500]]
使用受限的字符就是不安全的，在 url 上使用时，我们需要给他编码。
## URI
 可以说 URI 同时具备 locator 和 name 特性的一个东西。URN 作用就好像一个人的名字，URL 就像一个人的地址。换句话说：URN 确定了东西的身份，URL 提供了找到它的方式。


当然，现在最主要的弄清楚 URI 和 URL 的区别
首先看一下在 web 项目中的 servlet 中分别通过 request.GetRequestURI ()和 request.GetRequestURL ()输出的 URI 和 URL 格式如下
URI： /servlet 3_exercise/login
URL： http://localhost:8080/servlet3_exercise/login
