---
title: "[[Template Method Pattern 模板方法模式]]"
type: Reference
status: done
Creation Date: 2025-05-02 14:40
tags:
  - 设计模式
---
## Definition
Define the skeleton of an algorithm in an operation, deferring some steps to subclasses. Template Method lets subclasses redefine certain steps of an algorithm without changing the algorithm's structure.  
定义一个操作中的算法的框架，而将一些步骤延迟到子类中。使得子类可以不改变一个算法的结构即可重定义该算法的某些特定步骤。
![[Pasted image 20250502153326.png|500]]
AbstractClass
 是抽象类，其实也就是一抽象模板，定义并实现了一个模版方法。这个模版方法一般是一个具体方法，它给出了一个顶级逻辑的骨架，而逻辑的组成步骤在相应的抽象操作中，推迟到子类实现。顶级逻辑也有可能调用一些具体方法。
 ![[Pasted image 20250502153540.png|525]]
 ConcreteClass，
 实现父类所定义的一个或多个抽象方法。每一个AbstractClass， 都可以有任意多个ConcreteClass与之对应，而每一个ConcreteClass都可以给出这些抽象方法（也就是顶级逻辑的组成步骤）的不同实现，从而使得顶级逻辑的实现各不相同。
 ![[Pasted image 20250502153639.png|400]]
 客户端调用
```csharp
 static void Main（string[] args）
{
    AbstractClass c;

    c = new ConcreteClassA（）;
    c.TemplateMethod（）;

    c = new ConcreteClassB（）;
    c.TemplateMethod（）;

    Console.Read（）;
}
```

模板方法模式是通过把不变行为搬移到父类，去除子类中的重复代码来体现它的优势。模板方法模式提供了一个很好的代码复用平台。因为有时候，我们会遇到由一系列步骤构成的过程需要执行。这个过程从高层次上看是相同的，但有些步骤的实现可能不同。当不变的和可变的行为在方法的子类实现中混合在一起的时候，不变的行为就会在子类中重复出现。我们通过模板方法模式把这些行为搬移到单一的地方，这样就帮助子类摆脱重复的不变行为的纠缠。

模板方法模式是很常用的模式，对继承和多态玩得好的人几乎都会在继承体系中多多少少用到它。
## Exemple
```csharp
//-------------------------------------------------------------------------------------
//	TemplateMethodPatternExample1.cs
//-------------------------------------------------------------------------------------

using UnityEngine;
using System.Collections;

/* 
 Used to create a group of sublcasses that have to execute a similar group of methods
 You create an abstract class that contains a method called the Template Method
 The Template method contains a series of method calls that every sublcass object will call
 The subclass objects can override some of the method calls
*/

namespace TemplateMethodPatternExample1
{
    public class TemplateMethodPatternExample1 : MonoBehaviour
    {
        void Start()
        {
            Hoagie cust12Hoagie = new ItalienHoagie();
            cust12Hoagie.MakeSandwich();

            Hoagie cust13Hoagie = new VeggieHoagie();
            cust13Hoagie.MakeSandwich();
        }
    }
    public abstract class Hoagie
    {
        public void MakeSandwich()
        {
            Debug.Log("Making new Sandwich");

            CutBun();

            if (CustomerWantsMeat())
            {
                AddMeat();
            }

            if (CustomerWantsCheese())
            {
                AddCheese();
            }

            if (CustomerWantsVegetables())
            {
                AddVegetables();
            }

            if (CustomerWantsCondiments())
            {
                AddCondiments();
            }

            WrapTheHoagie();
        }
        protected abstract void AddMeat();
        protected abstract void AddCheese();
        protected abstract void AddVegetables();
        protected abstract void AddCondiments();

        protected virtual bool CustomerWantsMeat() { return true; } // << called Hook
        protected virtual bool CustomerWantsCheese() { return true; }
        protected virtual bool CustomerWantsVegetables() { return true; }
        protected virtual bool CustomerWantsCondiments() { return true; }

        protected void CutBun()
        {
            Debug.Log("Bun is Cut");
        }

        protected void WrapTheHoagie()
        {
            Debug.Log("Hoagie is wrapped.");
        }
    }

    public class ItalienHoagie : Hoagie
    {
        protected override void AddMeat()
        {
            Debug.Log("Adding the Meat: Salami");
        }

        protected override void AddCheese()
        {
            Debug.Log("Adding the Cheese: Provolone");
        }

        protected override void AddVegetables()
        {
            Debug.Log("Adding the Vegetables: Tomatoes");
        }

        protected override void AddCondiments()
        {
            Debug.Log("Adding the Condiments: Vinegar");
        }
    }



    public class VeggieHoagie : Hoagie
    {
        protected override void AddMeat()
        {
        }

        protected override void AddCheese()
        {
        }

        protected override void AddVegetables()
        {
            Debug.Log("Adding the Vegetables: Tomatoes");
        }

        protected override void AddCondiments()
        {
            Debug.Log("Adding the Condiments: Vinegar");
        }

        protected override bool CustomerWantsMeat() { return false; }
        protected override bool CustomerWantsCheese() { return false; }

    }


    namespace BadExample
    {
        // this way you would have to rewrite a lot of code
        // especially if something changes or another class differs and does e.g. not AddMeat()
        public class ItalienHoagie
        {
            public void MakeSandwich()
            {
                CutBun();
                AddMeat();
                AddCheese();
                AddVegtables();
                AddCondiments();
                WrapHoagie();
            }

            public void CutBun()
            {
                Debug.Log("Hoagie is Cut");
            }

            public void AddMeat()
            {
                Debug.Log("Added Meat");
            }

            public void AddCheese()
            {
                Debug.Log("Added Cheese");
            }

            public void AddVegtables()
            {
                Debug.Log("Added Vegies");
            }

            public void AddCondiments()
            {
                Debug.Log("Added Condiments");
            }

            public void WrapHoagie()
            {
                Debug.Log("Wrapped Hoagie");
            }
        }
    }
}
```