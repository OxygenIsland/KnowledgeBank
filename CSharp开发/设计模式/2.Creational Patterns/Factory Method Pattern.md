---
title: "[[Factory Method Pattern]]"
type: Permanent
status: ing
Creation Date: 2025-03-30 13:18
tags: 
---
## Definition
Define an interface for creating an object, but let subclasses decide which class to instantiate. Factory Method lets a class defer instantiation to subclasses.  
工厂方法使一个类的实例化延迟到其子类。
![[Pasted image 20250502131756.png]]
## Participants
The classes and objects participating in this pattern are:
### Product (Page)
- defines the interface of objects the factory method creates
- ConcreteProduct (SkillsPage, EducationPage, ExperiencePage)具体产品
- implements the Product interface
### Creator (Document)
- declares the factory method, which returns an object of type Product. Creator may also define a default implementation of the factory method that returns a default ConcreteProduct object.
- may call the factory method to create a Product object.
### ConcreteCreator (Report, Resume)
- overrides the factory method to return an instance of a ConcreteProduct.

简单工厂模式，就是工厂模式的一个简化板，简单工厂模式中的工厂类和产品类，没有一个统一的接口，所有的产品都是直接面向工厂的。工厂模式就是在简单工厂模式的基础上对工厂类和产品类进行抽象，下面是工厂模式的一个结构实现：
```csharp
namespace FactoryMethodStructure
{
    public class FactoryMethodStructure : MonoBehaviour
    {
	    void Start ( )
        {
            // An array of creators
            Creator[] creators = new Creator[2];

            creators[0] = new ConcreteCreatorA();
            creators[1] = new ConcreteCreatorB();

            // Iterate over creators and create products
            foreach (Creator creator in creators)
            {
                Product product = creator.FactoryMethod();
                Debug.Log("Created "+product.GetType().Name);
            }
        }
    }

    /// <summary>
    /// The 'Product' abstract class
    /// </summary>
    abstract class Product
    {
    }

    /// <summary>
    /// A 'ConcreteProduct' class
    /// </summary>
    class ConcreteProductA : Product
    {
    }

    /// <summary>
    /// A 'ConcreteProduct' class
    /// </summary>
    class ConcreteProductB : Product
    {
    }

    /// <summary>
    /// The 'Creator' abstract class
    /// </summary>
    abstract class Creator
    {
        public abstract Product FactoryMethod();
    }

    /// <summary>
    /// A 'ConcreteCreator' class
    /// </summary>
    class ConcreteCreatorA : Creator
    {
        public override Product FactoryMethod()
        {
            return new ConcreteProductA();
        }
    }

    /// <summary>
    /// A 'ConcreteCreator' class
    /// </summary>
    class ConcreteCreatorB : Creator
    {
        public override Product FactoryMethod()
        {
            return new ConcreteProductB();
        }
    }
}
```

## Exemple
```csharp
//This real-world code demonstrates the Factory method offering flexibility in creating different documents. 
//The derived(派生的) Document classes Report and Resume instantiate extended versions of the Document class. Here, the Factory Method is called in the constructor of the Document base class.

namespace FactoryMethodPatternExample1
{
    public class FactoryMethodPatternExample1 : MonoBehaviour
    {
        void Start()
        {
            // Note: constructors call Factory Method
            Document[] documents = new Document[2];

            documents[0] = new Resume();
            documents[1] = new Report();

            // Display document pages
            foreach (Document document in documents)
            {
                Debug.Log("\n" + document.GetType().Name + "--");
                foreach (Page page in document.Pages)
                {
                    Debug.Log(" " + page.GetType().Name);
                }
            }

        }
    }

    /// <summary>
    /// The 'Product' abstract class
    /// </summary>
    abstract class Page
    {
    }

    /// <summary>
    /// A 'ConcreteProduct' class
    /// </summary>
    class SkillsPage : Page
    {
    }

    /// <summary>
    /// A 'ConcreteProduct' class
    /// </summary>
    class EducationPage : Page
    {
    }

    /// <summary>
    /// A 'ConcreteProduct' class
    /// </summary>
    class ExperiencePage : Page
    {
    }

    /// <summary>
    /// A 'ConcreteProduct' class
    /// </summary>
    class IntroductionPage : Page
    {
    }

    /// <summary>
    /// A 'ConcreteProduct' class
    /// </summary>
    class ResultsPage : Page
    {
    }

    /// <summary>
    /// A 'ConcreteProduct' class
    /// </summary>
    class ConclusionPage : Page
    {
    }

    /// <summary>
    /// A 'ConcreteProduct' class
    /// </summary>
    class SummaryPage : Page
    {
    }

    /// <summary>
    /// A 'ConcreteProduct' class
    /// </summary>
    class BibliographyPage : Page
    {
    }

    /// <summary>
    /// The 'Creator' abstract class
    /// </summary>
    abstract class Document
    {
        private List<Page> _pages = new List<Page>();

        // Constructor calls abstract Factory method
        public Document()
        {
            this.CreatePages();
        }
        public List<Page> Pages
        {
            get { return _pages; }
        }
        // Factory Method
        public abstract void CreatePages();
    }

    /// <summary>
    /// A 'ConcreteCreator' class
    /// </summary>
    class Resume : Document
    {
        // Factory Method implementation
        public override void CreatePages()
        {
            Pages.Add(new SkillsPage());
            Pages.Add(new EducationPage());
            Pages.Add(new ExperiencePage());
        }
    }

    /// <summary>
    /// A 'ConcreteCreator' class
    /// </summary>
    class Report : Document
    {
        // Factory Method implementation
        public override void CreatePages()
        {
            Pages.Add(new IntroductionPage());
            Pages.Add(new ResultsPage());
            Pages.Add(new ConclusionPage());
            Pages.Add(new SummaryPage());
            Pages.Add(new BibliographyPage());
        }
    }
}
```

## 简单工厂vs.工厂方法
简单工厂模式的最大优点在于工厂类中包含了必要的逻辑判断，根据客户端的选择条件动态实例化相关的类，对于客户端来说，去除了与具体产品的依赖。
在简单工厂中，如果我们需要增加新的产品，我们需要先增加相应的产品类，然后去更改工厂方法，当中加‘Case’语句来做判断，当我们去修改工厂方法的时候就违背了[[3.一些设计原则#开放-封闭原则|开放-封闭原则]] ，因为我们对修改开放了！
> [!note]+ 封装变化
> 其实封装变化的方式十分简单，只要将可能发生变化的地方同一都继承一个接口，当发生变化的时候，新建一个继承了接口的类来完成需求，这样，我们就不需要修改原本的类了，这样我们就实现了 开放-封闭原则

在工厂模式中的体现就是，我们抽象了一个工厂类，新增一个产品的时候，我们就新建一个工厂，这样一来，原本的代码就不需要改动了。
但是工厂方法模式实现时，客户端需要决定实例化哪一个工厂来实现运算类，选择判断的问题还是存在的，也就是说，工厂方法把简单工厂的内部逻辑判断移到了客户端代码来进行。你想要加功能，本来是改工厂类的，而现在是修改客户端！

其实对于使用者来说，不需要知道对于的工厂类型，这就意味着，我们不需要具体的工厂类，我们只需要拿到工厂接口的引用，调用工厂方法就可以了，这样封装是最好的。