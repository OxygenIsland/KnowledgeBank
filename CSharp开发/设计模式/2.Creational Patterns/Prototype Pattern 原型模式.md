---
title: "[[Prototype Pattern 原型模式]]"
type: Reference
status: done
Creation Date: 2025-05-02 13:23
tags:
  - 设计模式
---
## Definition
Specify the kind of objects to create using a prototypical instance, and create new objects by copying this prototype.  
用原型实例指定创建对象的种类，并且通过拷贝这些原型创建新的对象。
![[Pasted image 20250502132817.png|600]]
原型模式其实就是从一个对象再创建另外一个可定制的对象，而且不需知道任何创建的细节
Prototype
![[Pasted image 20250502133112.png|500]]
ConcretePrototype
![[Pasted image 20250502133154.png|600]]
需要注意的是，图中的“复制引用”与“复制引用的对象”的区别，这二者的区别其实就是[[Shallow Copy and Deep Copy|浅拷贝和深拷贝]]的区别
Client
![[Pasted image 20250502133236.png|450]]
但对于.NET而言，那个原型抽象类Prototype是用不着的，因为克隆实在是太常用了，所以.NET在System命名空间中提供了ICloneable接口 ，其中就是唯一的一个方法Clone（），这样就只需要实现这个接口就可以完成原型模式了
## Exemple
下面是一个简历的例子
简历类
![[Pasted image 20250502141519.png|475]]
![[Pasted image 20250502141540.png|475]]
客户端调用代码
![[Pasted image 20250502141628.png|475]]

原型模式对性能也是有好处的。当我们创建一个新对象的时候，每NEW一次，都需要执行一次构造函数，如果构造函数的执行时间很长，那么多次的执行这个初始化操作就实在是太低效了。一般在初始化的信息不发生变化的情况下，克隆是最好的办法。这既隐藏了对象创建的细节，又对性能是大大的提高。
