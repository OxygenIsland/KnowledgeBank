## 2.1 Sets and Mappings 集合和映射
Mappings, also called functions, are basic to mathematics and programming. Like a function in a program, a mapping in math takes an argument of one type and maps it to (returns) an object of a particular type. In a program we say “type”; in math we would identify the set.
![[Pasted image 20240424210127.png|218]]
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


