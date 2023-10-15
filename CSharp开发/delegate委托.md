## 1.前言
###  1.1 C#中的委托 、事件引入
首先引入一个情景，在全球化形势下，不同语种的小伙伴们要问候早安。那么最直观的做法，无非是判断哪国人，然后说英语的调用说英语的方法，说中文的调用说中文的方法，之后再有说日语的，说法语的还要再调用说日语的，说法语的方法。这样做当然 OK，但是拓展性很差。
首先是不考虑使用委托时的写法
```c#
using UnityEngine;
using System.Collections;
public class delegateFanyoy : MonoBehaviour
{
    // Use this for initialization
    public UIButton testBtn;
    void Start ()
    {
        EventDelegate.Add (this.testBtn.onClick, this.BtnClick);
    }
    public void BtnClick()
    {
        GoodMoring ("chenjd");
    }
    public void GoodMoring(string name)
    {
        Debug.Log ("GoodMoring " + name);
    }
}
```
很简单，首先利用 EventDelegate 为按钮的 OnClick 事件绑定一个方法，用来测试我们上面提到的问早安的功能。
结果如下：
![[Pasted image 20230727222306.png|700]]
那么问题来了，小匹夫可是堂堂中国人啊，怎么能不说中文反而天天鼓捣英语呢？所以刚刚实现问早的方法 GoodMoring ()就不能用咯，还要新写一个方法，要输出中文早安，然后再和点击按钮的事件绑定。这样是不是很麻烦呢？
如果有小伙伴觉得不麻烦，那小匹夫只能演示一种小匹夫认为不使用委托的前提下最直接的一种写法了。这时候，GoodMoring 就需要改一改了，肯定要根据不同的人来选择不同的问候语咯。这里为了方便，定义一个枚举 Language 作为判断的依据：
```c#
using UnityEngine;
using System.Collections;
public class delegateFanyoy : MonoBehaviour {
    // Use this for initialization
    public UIButton testBtn;
    void Start () {
        EventDelegate.Add (this.testBtn.onClick, this.BtnClick);
    }
    public void BtnClick()
    {
        GoodMoring ("chenjd", Language.Chinese);
    }
    public void GoodMoring(string name, Language l)
    {
        switch (l)
        {
        case Language.Chinese:
            MoringChinese(name);
            break;
        case Language.English:
            MoringEnglish(name);
            break;
        }
    }
    public void MoringChinese(string n)
    {
        Debug.Log ("早上好 " + n);
    }
    public void MoringEnglish(string n)
    {
        Debug.Log ("goodmoring" + n);
    }
    public enum Language
    {
        Chinese,
        English
    }
}
```
如果再来一个日语普通话的小伙伴，或者再来一个韩语思密达的小伙伴，那么不可避免我们需要去修改 GoodMoring 这个函数去实现判断并调用正确的语言输出方法。这样拓展性体现在哪里呢？
如果说能有一个方法 A，它的参数也是一个方法 B，那么我们保留那个方法 A 而只需要传入不同的参数（方法 B），不就可以灵活的应对了吗？再来一个日本人，一个韩国人，无非只是将说日语和说韩语的方法 B 传入到那个无需改动的方法 A 中就可以了，点击按钮触发的事件只需要方法 A 响应就可以咯。这里方法 A 就是我们的 GoodMoring 方法，而方法 B 作为参数是不同语言的 MoringXXXX 方法。
那么我们就可以引入代理的概念了。嗯，是那句很老套的——方法的参数是方法。
### 1.2 方法的参数是方法
既然方法 A 的某个参数是方法 B，我们所要利用的无非就是使用传入的方法 B。所以我们之前的方法 A--GoodMoring (string name, language l)方法就变成了
```c#
GoodMoring(string name, XXX MoringLanguage)
{
    MoringLanguage(name);
}
```
直接调用作为参数传入的方法。　　
但是这里又有新的问题出现了，涉及到要将方法作为参数传入另一个方法，我们都知道，参数的传入是需要有类型的呀。你 MoringLanguage 到底是个啥？
这里我们似乎又想到了，区分方法，无非是它的返回值，和传入参数类型个数。想到这里，豁然开朗，只要我们***规定了传入的 MoringLanguage 的返回类型和 MoringLanguage 的参数类型是不是就可以证明传入的 MoringLanguage 的身份了呢？对！这就是代理了 delegate 了。***
那我们按照 MoringChinese 和 MoringEnglish 的返回类型和参数类型来定义这个委托。
`public delegate void MoringDelegate(string name);`
那么我们将 GoodMoring 的修改为
```c#
GoodMoring(string name, MoringDelegate MoringLanguage)
{
    MoringLanguage(name);
}
```
就可以了。下面上代码。
```c#
using UnityEngine;
using System.Collections;
public class delegateFanyoy : MonoBehaviour {
    // Use this for initialization
    public UIButton testBtn;
    void Start () {
        EventDelegate.Add (this.testBtn.onClick, this.BtnClick);
    }
    public void BtnClick()
    {
        GoodMoring ("chenjd", MoringEnglish);
        GoodMoring ("小匹夫", MoringChinese);
    }
    public void GoodMoring(string name, MoringDelegate MoringLanguage)
    {
        MoringLanguage (name);
    }
    public delegate void MoringDelegate(string n);
    public void MoringChinese(string n)
    {
        Debug.Log ("早上好 " + n);
    }
    public void MoringEnglish(string n)
    {
        Debug.Log ("goodmoring" + n);
    }
    public enum Language
    {
        Chinese,
        English
    }
}
```
***所谓委托就是一个类，它定义了方法的类型，所有满足这个类型的方法都可以被当作另一个方法的参数来进行传递。***
1. 委托在使用时遵循**三步走的原则**，即定义声明委托、实例化委托以及调用委托。
2. 委托是 C# 语言中的一个特色，通常将委托分为**命名方法委托、多播委托、匿名委托**，其中命名方法委托是使用最多的一种委托。
## 2. 委托的使用
委托可以理解为存储方法的数组，通过委托可以将几个具有相同形参类型和返回值类型的方法加入到一个委托中一并执行
### 2.1 定义委托
```csharp
Private int delegate VoidDelegate (int a, int b);   // 括号内为传递的参数
```
### 2.2 实例化委托
```csharp
VoidDelegate d1; 
// 如果利用new关键字定义委托，同时需要为其赋初值
VOidDelegate d1 = new VoidDelegate(Func1); 
```
### 2.3 向委托中添加/删除函数
```csharp
d1 = Func1;    // 添加第一个函数时需要直接赋值
d1 += Func2;   // 注意这里只能传递一个函数名进去，如果函数名后面加了括号，就会执行该函数一次
d1 += Func3;   
d1 -= Func1;
```
### 2.4 调用委托
```csharp
d1();    // 直接调用
d1.Invoke(a, b)   // 利用Invoke调用
```
### 2.5 完整代码
```csharp
public delegate int IntDelegate(int a, int b);
private void IntDelegateTest()
{
    IntDelegate id;
    id = (a, b) => { return a + b; };
    id += (a, b) => { return a - b; };
    id += (a, b) => { return a * b; };
    int res = id.Invoke(1, 2);   // int res = id(1, 2);
    Debug.Log(res);
}
// 返回值为2，当委托存在返回值时，就只会返回最后加进去的函数的返回值
```
输出结果：
![[Pasted image 20230820170326.png|288]]
### 2.6 补充
#### 2.6.1 多播委托
在 CSharp语言中多播委托是指在一个委托中注册多个方法，在注册方法时可以在委托中使用加号运算符或者减号运算符来实现添加或撤销方法。
在现实生活中，多播委托的实例是随处可见的，例如某点餐的应用程序，既可以预定普通的餐饮也可以预定蛋糕、鲜花、水果等商品，代码如下。
```c#
class Program
{
    //定义购买商品委托
    public delegate void OrderDelegate();
    static void Main(string[] args)
    {
        //实例化委托
        OrderDelegate orderDelegate = new OrderDelegate(Order.BuyFood);
        //向委托中注册方法
        orderDelegate += Order.BuyCake;
        orderDelegate += Order.BuyFlower;
        //调用委托
        orderDelegate();
    }
}
class Order
{
    public static void BuyFood()
    {
        Console.WriteLine("购买快餐！");
    }
    public static void BuyCake()
    {
        Console.WriteLine("购买蛋糕！");
    }
    public static void BuyFlower()
    {
        Console.WriteLine("购买鲜花！");
    }
}
```
#### 2.6.2 匿名委托
在 C# 语言中匿名委托是指使用匿名方法注册在委托上，实际上是在委托中通过定义代码块来实现委托的作用，具体的语法形式如下。
```c#
//1. 定义委托
修饰符  delegate  返回值类型  委托名 ( 参数列表 );
//2. 定义匿名委托
委托名  委托对象 = delegate
{
    //代码块
};
//3. 调用匿名委托
委托对象名 ( 参数列表 );
```
通过上面 3 个步骤即可完成匿名委托的定义和调用，需要注意的是，在定义匿名委托时代码块结束后要在 {} 后加上分号。
下面通过实例来演示匿名委托的应用。
【委托】使用匿名委托计算长方形的面积，代码如下。
```c#
class Program
{
    public delegate void AreaDelegate(double length, double width);
    static void Main(string[] args)
    {
        Console.WriteLine("请输入长方形的长：");
        double length = double.Parse(Console.ReadLine());
        Console.WriteLine("请输入长方形的宽：");
        double width = double.Parse(Console.ReadLine());
        AreaDelegate areaDelegate = delegate
        {
            Console.WriteLine("长方形的面积为：" + length * width);
        };
        areaDelegate(length, width);
    }
}
```
从上面的执行效果可以看岀，在使用匿名委托时并没有定义方法，而是在实例化委托时直接实现了具体的操作。
由于匿名委托并不能很好地实现代码的重用，匿名委托通常适用于实现一些仅需要使用一次委托中代码的情况，并且代码比较少。

## 3. Event 事件
事件可以理解为委托的一个实例 (不太严谨)，在类的内部声明事件，必须先声明该事件对应的委托类型，同时 **事件不仅可以添加函数进去，还可以加入委托**
相较委托更安全，***因为使用事件只能对事件进行添加减少***，不能获得其他的方法，防止了数据污染和非法调用，而且通过委托可以对事件响应者要调用的方法进行约束，减少 bug 出现频率

事件在类中声明且生成，且通过使用同一个类或其他类中的委托与事件处理程序关联。包含事件的类用于发布事件。这被称为发布器（publisher） 类。其他接受该事件的类被称为订阅器（subscriber） 类。事件使用发布-订阅（publisher-subscriber） 模型。
- 发布器（publisher） 
	是一个包含事件和委托定义的对象。事件和委托之间的联系也定义在这个对象中。发布器（publisher）类的对象调用这个事件，并通知其他的对象。
- 订阅器（subscriber） 
	是一个接受事件并提供事件处理程序的对象。在发布器（publisher）类中的委托调用订阅器（subscriber）类中的方法（事件处理程序）。
```csharp
public delegate void VoidDelgate(int a);
public static event VoidDelgate voidEvent;
private void VoidEventTest()
{
    // 先定义一个委托
    VoidDelgate vd;
    vd = a => Debug.Log(a);
    vd += a => Debug.Log(a * a);
    // 向事件内添加委托和函数
    voidEvent = vd;
    voidEvent += a => Debug.Log(a - 1);
    voidEvent += a => Debug.Log(a + 1);
    voidEvent(6);
}
```
输出结果：
![[Pasted image 20230820171152.png|351]]
事件与委托的区别：
- 委托创建时会定义方法的类型（是否有无参数、有无返回值）
- 事件的创建需要一个委托才能声明（因为事件就是委托的实例）
- 委托可以在任何类中或类外声明，但是事件只能在类中声明（类型跟实例，实例要运行所以要在类里面咯）
- **事件只能在当前声明的类中调用**，但是可以在其他类中为其添加/删除函数，无论将事件设置成 public 还是 static 其他类都无法调用
```c#
//经典面试题—猫叫，主人醒，老鼠跑
using System;
namespace DelegateDemo
{
    //定义猫叫委托
    public delegate void CatCallEventHandler();
    public class Cat
    {
        //定义猫叫事件
        public event CatCallEventHandler CatCall;
        public void OnCatCall()
        {
            Console.WriteLine("猫叫了一声");
            CatCall?.Invoke();
        }
    }
    public class Mouse
    {
        //定义老鼠跑掉方法
        public void MouseRun()
        {
            Console.WriteLine("老鼠跑了");
        }
    }
    public class People
    {
        //定义主人醒来方法
        public void WakeUp()
        {
            Console.WriteLine("主人醒了");
        }
    }
    class Program
    {
        static void Main(string[] args)
        {
            Cat cat = new Cat();
            Mouse m = new Mouse();
            People p = new People();
            //关联绑定
            cat.CatCall += new CatCallEventHandler(m.MouseRun);
            cat.CatCall += new CatCallEventHandler(p.WakeUp);
            cat.OnCatCall();
            Console.ReadKey();
        }
    }
}
```
## 4. Action
Action 可以理解为系统定义好的带泛型的 delegate，**Action 是无返回值的**
要使用 Action 需要引用头文件 `using System`
Action 的泛型 T 代表参数，T 内可以传多个参数
```csharp
private void ActionTest()
{
    Action action;   // 无参的Action
    action = () => Debug.Log("action use once");
    action += () => Debug.Log("action use twice");
    action();

    Action<int, string> action2;   // 有多个参数的Action
    action2 = (a, b) => Debug.Log("name: " + b + "\tage: " + a.ToString());
    action2 += (a, b) => Debug.Log("name: " + b + "\tage: " + (a + 1).ToString());
    action2(18, "Ousun");
}
```
输出结果：
![[Pasted image 20230820171651.png|347]]
## 5. Func
Func 可以理解为系统定义好的带泛型的 delegate，**Func 是有返回值的**
要使用 Func 需要引用头文件 `using System`
Func<T,K>的前 n-1个泛型代表参数，最后一个泛型代表返回值类型
```csharp
private void FuncTest()
{
    Func<int, int> func;
    func = (a) => { Debug.Log(a); return a; };
    func += (a) => { a += 1; Debug.Log(a); return a; };
    func += (a) => { a += 2; Debug.Log(a); return a; };
    int res = func(1);
    Debug.Log("res = " + res.ToString());
}
```
输出结果：
![[Pasted image 20230820172818.png|342]]
