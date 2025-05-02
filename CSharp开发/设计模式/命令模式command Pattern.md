---
title: "[[命令模式command Pattern]]"
type: Literature
status: done
Creation Date: 2024-05-22 09:48
tags:
  - 设计模式
---
## Definition
Encapsulate a request as an object, thereby letting you parameterize clients with different requests, queue or log requests, and support undoable operations.  
命令模式将“请求”封装成对象，以便使用不同的请求、队列或者日志来参数化其他对象，同时支持可撤消的操作。
既然命令变成了数据，就是可以被传递、存储、重复利用的：
- 通过命令数据队列或栈可以轻易实现撤销、重做、时光倒流
- 命令数据还可以形成日志，用于复现用户行为，便于重复测试同样序列命令对各种目标的影响
- 这些命令数据可以发送给不同的目标，比如同样的“出发，5分钟后，停止”，发送给飞机就可以变成“起飞，5分钟后，降落”，发送给轮船就成了“离港，5分钟后，抛锚”

命令模式可能会导致大量的实例化，从而浪费内存，但是另一种设计模式享元模式可以代替大量的实例化
### 适用场景
1. **需要将请求发送者和接收者解耦**: 命令模式可以将请求发送者（客户端）与请求接收者（执行操作的对象）解耦。发送者只需知道如何发送命令，而不需要知道接收者的具体实现细节。（这个场景用消息模型是不是也可以实现？）
    
2. **需要支持撤销和重做操作**: 命令模式通过将操作封装成对象，可以轻松支持撤销和重做功能。每个命令对象都包含了执行和撤销操作的逻辑，因此可以方便地撤销和重做操作。
    
3. **需要对操作进行参数化或延迟执行**: 命令模式允许将操作参数化，使得可以使用不同的参数来执行相同的操作。此外，命令对象可以延迟执行操作，因为它们可以被存储、传递和执行在不同的时间和地点。
    
4. **需要构建可扩展的命令系统**: 命令模式可以帮助构建一个灵活的命令系统，可以轻松地添加新的命令类型，而无需修改现有的代码。通过添加新的具体命令类，可以方便地扩展系统的功能。
    
5. **需要实现事务性操作**: 命令模式可以用于实现事务性操作，即将一系列操作封装成一个命令对象，并确保它们要么全部执行成功，要么全部失败。这样可以确保系统的一致性和可靠性。
## Participants
![[Pasted image 20240512164820.png|388]] 
### Command
- declares an interface for executing an operation
- 抽象基类，包含了时间戳和运行、回退的虚方法
### ConcreteCommand
- defines a binding between a Receiver object and an action
- implements Execute by invoking the corresponding operation(s) on Receiver
### Client
- creates a ConcreteCommand object and sets its receiver
### Invoker
- asks the command to carry out the request
### Receiver
- knows how to perform the operations associated with carrying out the request.、
小结：client 创建具体的 concreteCommand，concreteCommand 中包含有对应的 receiver，invoker 收到 concreteCommand 之后根据 concreteCommand 中的 receiver 来执行命令
## Example
### 计算器
```csharp
//This real-world code demonstrates the Command pattern used in a simple calculator with unlimited number of undo's and redo's.  
//Note that in C#  the word 'operator' is a keyword. Prefixing it with '@' allows using it as an identifier.  
  
using System;  
using UnityEngine;  
using System.Collections;  
using System.Collections.Generic;  
  
namespace CommandExample1  
{  
    public class CommandExample1 : MonoBehaviour  
    {  
        void Start ( )  
        {            // Create user and let her compute  
            User user = new User();  
  
            // User presses calculator buttons  
            user.Compute('+', 100);  
            user.Compute('-', 50);  
            user.Compute('*', 10);  
            user.Compute('/', 2);  
  
            // Undo 4 commands  
            user.Undo(4);  
  
            // Redo 3 commands  
            user.Redo(3);  
        }    
    }  
    /// <summary>  
    /// The 'Command' abstract class    
    /// </summary>    
    abstract class Command  
    {  
        public abstract void Execute();  
        public abstract void UnExecute();  
    }  
    /// <summary>  
    /// The 'ConcreteCommand' class;    /// 表示具体的计算器命令，其中包含了执行计算的逻辑以及撤销计算的逻辑。  
    /// </summary>  
    class CalculatorCommand : Command  
    {  
        private char _operator;  
        private int _operand;  
        private Calculator _calculator;  
  
        // Constructor  
        public CalculatorCommand(Calculator calculator, char @operator, int operand)  
        {            this._calculator = calculator;  
            this._operator = @operator;  
            this._operand = operand;  
        }  
        // Gets operator  
        public char Operator  
        {  
            set { _operator = value; }  
        }  
  
        // Get operand  
        public int Operand  
        {  
            set { _operand = value; }  
        }  
  
        // Execute new command  
        public override void Execute()  
        {            
	        _calculator.Operation(_operator, _operand);  
        }  
        // Unexecute last command  
        public override void UnExecute()  
        {            
	        _calculator.Operation(Undo(_operator), _operand);  
        }  
        // Returns opposite operator for given operator  
        private char Undo(char @operator)  
        {            
	        switch (@operator)  
            {                
	            case '+': return '-';  
                case '-': return '+';  
                case '*': return '/';  
                case '/': return '*';  
                default:  
                    throw new  
	            ArgumentException("@operator");  
            }        
        }    
    }  
    /// <summary>  
    /// The 'Receiver' class;    /// 命令的接收者，负责实际执行计算操作  
    /// </summary>  
    class Calculator  
    {  
        private int _curr = 0;  
  
        public void Operation(char @operator, int operand)  
        {            
	        switch (@operator)  
            {                
	            case '+': _curr += operand; break;  
                case '-': _curr -= operand; break;  
                case '*': _curr *= operand; break;  
                case '/': _curr /= operand; break;  
            }            
            Debug.Log("Current value = " + _curr+ " ( following "+ @operator+operand+" )");  
        }    
    }  
    /// <summary>  
    /// The 'Invoker' class    /// </summary>    
    class User  
    {  
        // Initializers  
        private Calculator _calculator = new Calculator();  
        private List<Command> _commands = new List<Command>();  
        private int _current = 0;  
  
        public void Redo(int levels)  
        {            
	        for (int i = 0; i < levels; i++)  
            {                
	            if (_current < _commands.Count - 1)  
                {                    
	                Command command = _commands[_current++];  
                    command.Execute();  
                }            
            }        
        }  
        public void Undo(int levels)  
        {            
	        Debug.Log("\n---- Undo "+ levels + " levels");  
            // Perform undo operations  
            for (int i = 0; i < levels; i++)  
            {                
	            if (_current > 0)  
                {                    
	                Command command = _commands[--_current] as Command;  
                    command.UnExecute();  
                }            
            }        
        }  
        public void Compute(char @operator, int operand)  
        {            
	        // Create command operation and execute it  
            Command command = new CalculatorCommand(_calculator, @operator, operand);  
            command.Execute();  
            // Add command to undo list  
            _commands.Add(command);  
            _current++;  
        }    
	}
}
```
从这个例子中也可以看出命令模式的一个缺点，比如现在要求添加一个开方和乘方的命令就需要构建新的 CalculatorCommand 和 Calculator，随着命令的增加，可能会导致大量的对象实例化，从而增加内存消耗。如果对内存消耗有较高的关注，可以考虑一些优化策略，例如对象池技术，通过重用已有的命令对象来减少实例化开销；
