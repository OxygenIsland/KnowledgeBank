---
title: "[[2、 Miscellaneous Math]]"
type: Literature
status: done
Creation Date: 2024-05-30 18:33
tags:
---
## 2.1 Sets and Mappings 集合和映射
Mappings, also called functions, are basic to mathematics and programming. Like a function in a program, a mapping in math takes an argument of one type and maps it to (returns) an object of a particular type. In a program we say “type”; in math we would identify the set.

Given any two sets A and B, we can create a third set by taking the Cartesian product of the two sets, denoted A × B. This set A × B is composed of all possible ordered pairs (a, b) where a ∈ A and b ∈ B. As a shorthand, we use the notation A2 to denote A × A. We can extend the Cartesian product to create a set of all possible ordered triples from three sets and so on for arbitrarily long ordered tuples from arbitrarily many sets. 
Common sets of interest include：
![[Pasted image 20240424205945.png|500]]
Note that although S2 is composed of points embedded in three-dimensional space, they are on a surface that can be parameterized with two variables, so it can be thought of as a 2D set.
映射的符号表示如下：
$f:\mathbb R \longmapsto \mathbb Z$       其中，$\mathbb R$ 为函数 $f$ 的 domain；$\mathbb Z$ 为函数 $f$ 的 target。
在图形学中是这样描述这个函数的：函数 f 有一个 real argument（实参）并返回一个 integer（实数）即：
$integer f(real)   \longleftarrow equivalent \longrightarrow f:\mathbb R \longmapsto \mathbb Z$
The point f(a) is called the image of a, and the image of a set A (a subset of the domain) is the subset of the target that contains the images of all points in A.
The image of the whole domain is called the range of the function. 也就是值域啦

### 2.1.1 Inverse Mappings 逆映射
![[Pasted image 20240424210127.png|218]]
两个集合 Set d 和 Set D 存在映射函数 $f$ 和 $f^{-1}$ 可以将两个集合中的值一一对应，而且有且只有一个值，这种映射函数称为 bijection（双射）
这里有一个很有意思的比喻
A bijection between a group of riders and horses indicates that everybody rides a single horse, and every horse is ridden. The two functions would be rider(horse) and horse(rider). 
![[Pasted image 20240519123958.png|208]]
These are inverse functions of each other. Functions that are not bijections have no inverse
**Example： $f(x)=x^3$ 和 $f^{-1}(x)=\sqrt{x}$**
在这里吐槽一下原文吧，请看原文
This exmple shows that the standard notation can be somewhat awkward because x is used as a dummy variable in both $f$ and $f^{-1}$
 他说使用标准的符号也就是 x 来表示的时候有点 awkward?？ 尴尬?? 理解不了一点，这里的 x 是用来表示虚拟变量的、
  It is sometimes more intuitive to use different dummy variable
  
### 2.1.2 Intervals 区间
Often we would like to specify that a function deals with real numbers that are restricted in value. One such constraint is to specify an interval. 一些基本的知识我这里就略过了......
![[Pasted image 20240519145734.png|210]]
The Cartesian (笛卡尔) products of intervals are often used. For example, to indicate that a point x is in the unit cube in 3D, we say $x\in[0,1]^3$
### 2.1.3 Logarithms 对数
The “log base a” of x is written $log_a x$ and is defined as “the exponent (指数) to which a must be raised to get x,”
											$y=log_ax   \Leftrightarrow   a^y=x$ 
上面的函数互为 Inverses，This basic definition has several consequences:
$a^{log_a(x)=x}$ 
$log_a (a^x)=x$ 
$log_a(xy)=log_ax+log_ay$ 
$log_a(x/y)=log_ax-log_ay$ 
$log_a(x)=log_ab *log_bx$ 
When we apply calculus to logarithms, the special number e = 2.718 ... often turns up. The logarithm with base e is called the natural logarithm. We adopt the common shorthand ln to denote it:
$lnx\equiv log_ex$
 Like π, the special number e arises in a remarkable number of contexts
有一个我读书的时候就比较好奇的问题，为什么 e 被称为自然数呢？书中是这样说的：
The derivatives (导数) of logarithms and exponents illuminate why the natural logarithm is “natural”:
$\frac{d}{dx} log_ax=\frac{1}{xln_a}$
$\frac{d}{dx}a^x=a^xln_a$ 
The constant multipliers above are unity only for a = e.  常数乘数是什么鬼？还是不懂
## 2.2 Solving Quadratic Equations 解二次方程
A quadratic equation has the form：
$Ax^2+Bx^2+Cx^2=0$
If you think of a 2D xy plot with $y = Ax^2 + Bx^2 + C$, the solution is just whatever x values are “zero crossings” in y
$y = Ax^2 + Bx^2 + C$,是一个 Parabola（抛物线）,
![[Pasted image 20240523215353.png|233]]
这个对我来说肯定很简单啦啦，经过推算之后我们可以得到一个求根公式：
$x=\frac{-B\pm \sqrt{B^2-4AC}}{2A}$,当然无根、1 个根、2 个根，的区分就依靠 $B^2-4AC$ 啦，which is called the discriminant（判别式） of the quadratic equation
## 2.3 Trigonometry (三角学)
In graphics we use basic trigonometry in many contexts. Usually, it is nothing too fancy（幻想？花里胡哨！）, and it often helps to remember the basic definitions.
### 2.3.1 Angles
Although we take angles somewhat for granted, we should return to their definition so we can extend the idea of the angle onto the sphere. An angle is formed between two half-lines (infinite rays stemming from an origin) or directions, and some convention（约定、惯例） must be used to decide between the two possibilities for the angle created between them as shown in Figure 2.6
![[Pasted image 20240523221313.png|275]]
单位圆的 perimeter（周长）为 $2\pi$ ,弧长的单位是 radians，Another common unit is degrees, where the perimeter of the circle is 360 degrees. Thus, an angle that is π radians is 180 degrees, usually denoted $180^\circ$. The conversion between degrees and radians is:
$degrees=\frac{180}{\pi}radians$
$radians=\frac{\pi}{180}degrees$
### 2.3.2 Trigonometric Functions
![[Pasted image 20240523223647.png|284]]
勾股定理，自己也可以推出来哦
