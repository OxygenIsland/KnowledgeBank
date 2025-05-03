---
title: "[[Facade Pattern 外观模式]]"
type: Reference
status: done
Creation Date: 2025-05-03 09:38
tags:
  - 设计模式
---
## Definition
Provide a unified interface to a set of interfaces in a subsystem. Façade defines a higher-level interface that makes the subsystem easier to use.  
要求一个子系统的外部与其内部的通信必须通过一个统一的对象进行。外观模式提供一个高层次的接口，使得子系统更易于使用。外观模式完美地体现了[[3.一些设计原则#依赖倒转原则|依赖倒转原则]]和[[3.一些设计原则#迪米特法则|迪米特法则]]的思想
![[Pasted image 20250503100332.png|600]]
这个模式在《大话设计模式》这本书中，讲的十分不错，所以本文会使用该书的一些内容。

**股票​**​代表对一家公司的部分所有权，持有者（股东）享有公司分红、投票权等权益。投资者可以直接投资。
**​基金**​是汇集众多投资者的资金，由专业管理人投资于股票、债券、货币等资产。投资者持有基金份额，而非直接持有底层资产，收益取决于基金的整体表现。

通过这两个理财产品，我们对外观模式进行介绍。
炒股的代码
![[Pasted image 20250503095823.png|500]]
投资基金的代码
![[Pasted image 20250503100129.png|500]]

接下来我们再来看看外观模式的代码
子系统类
```csharp
class SubSystemOne
{
    public void MethodOne（）
    {
        Console.WriteLine（" 子系统方法一"）;
    }
    }
class SubSystemTwo
{
    public void MethodTwo（）
    {
        Console.WriteLine（" 子系统方法二"）;
    }
}

class SubSystemThree
{
    public void MethodThree（）
    {
        Console.WriteLine（" 子系统方法三"）;
    }
}

class SubSystemFour
{
    public void MethodFour（）
    {
        Console.WriteLine（" 子系统方法四"）;
    }
}
```
外观类
![[Pasted image 20250503101529.png|500]]
客户端调用
![[Pasted image 20250503101610.png|575]]

## 何时使用外观模式
首先，在设计初期阶段，应该要有意识的将不同的两个层分离，比如经典的三层架构，就需要考虑在数据访问层和业务逻辑层、业务逻辑层和表示层的层与层之间建立外观Facade，这样可以为复杂的子系统提供一个简单的接口，使得耦合大大降低。

其次，在开发阶段，子系统往往因为不断的重构演化而变得越来越复杂，大多数的模式使用时也都会产生很多很小的类，这本是好事，但也给外部调用它们的用户程序带来了使用上的困难，增加外观Facade可以提供一个简单的接口，减少它们之间的依赖。

第三，在维护一个遗留的大型系统时，可能这个系统已经非常难以维护和扩展了，但因为它包含非常重要的功能，新的需求开发必须要依赖于它。此时用外观模式Facade也是非常合适的。你可以为新系统开发一个外观Facade类，来提供设计粗糙或高度复杂的遗留代码的比较清晰简单的接口，让新系统与Facade对象交互，Facade与遗留代码交互所有复杂的工作。

## Exmple
```csharp
//-------------------------------------------------------------------------------------
//	FacadePatternExample1.cs
//-------------------------------------------------------------------------------------

using UnityEngine;
using System.Collections;

//This real-world code demonstrates the Facade pattern as a MortgageApplication object which provides a simplified interface to a large subsystem of classes measuring the creditworthyness of an applicant.

namespace FacadePatternExample1
{
    public class FacadePatternExample1 : MonoBehaviour
    {
        void Start()
        {
            // Facade
            Mortgage mortgage = new Mortgage();

            // Evaluate mortgage eligibility for customer
            Customer customer = new Customer("Ann McKinsey");
            bool eligible = mortgage.IsEligible(customer, 125000);

            Debug.Log("\n" + customer.Name +
                " has been " + (eligible ? "Approved" : "Rejected"));
        }
    }

    /// <summary>
    /// The 'Subsystem ClassA' class
    /// </summary>
    class Bank
    {
        public bool HasSufficientSavings(Customer c, int amount)
        {
            Debug.Log("Check bank for " + c.Name);
            return true;
        }
    }

    /// <summary>
    /// The 'Subsystem ClassB' class
    /// </summary>
    class Credit
    {
        public bool HasGoodCredit(Customer c)
        {
            Debug.Log("Check credit for " + c.Name);
            return true;
        }
    }

    /// <summary>
    /// The 'Subsystem ClassC' class
    /// </summary>
    class Loan
    {
        public bool HasNoBadLoans(Customer c)
        {
            Debug.Log("Check loans for " + c.Name);
            return true;
        }
    }

    /// <summary>
    /// Customer class
    /// </summary>
    class Customer
    {
        private string _name;

        // Constructor
        public Customer(string name)
        {
            this._name = name;
        }

        // Gets the name
        public string Name
        {
            get { return _name; }
        }
    }

    /// <summary>
    /// The 'Facade' class
    /// </summary>
    class Mortgage
    {
        private Bank _bank = new Bank();
        private Loan _loan = new Loan();
        private Credit _credit = new Credit();

        public bool IsEligible(Customer cust, int amount)
        {
            Debug.Log(cust.Name + "applies for " + amount+ " loan\n");

            bool eligible = true;

            // Check creditworthyness of applicant
            if (!_bank.HasSufficientSavings(cust, amount))
            {
                eligible = false;
            }
            else if (!_loan.HasNoBadLoans(cust))
            {
                eligible = false;
            }
            else if (!_credit.HasGoodCredit(cust))
            {
                eligible = false;
            }

            return eligible;
        }
    }
}
```

看完这个例子，其实仔细一想，nerf渲染的代码也可以封装成外观模式，但是感觉用外观模式有点大才小用，nerf渲染的逻辑也没有很复杂！