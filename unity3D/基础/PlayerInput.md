## 一、PlayerInput 介绍
​ PlayerInput 是 InputSystem 提供的专门用于接受玩家输入来处理自定义逻辑的组件

​ 主要工作原理：
1. 配置输入文件（InputActions 文件）
2. 通过 PlayerInput 关联配置文件，它会自动解析该配置文件
3. 关联对应的响应函数，处理对应逻辑
​ 好处：
- 不需要自己进行相关输入的逻辑书写
- 通过配置文件即可配置想要监听的对应行为
- 让我们专注于输入事件触发后的逻辑处理
![[Pasted image 20240808175844.png|500]] 
Actions：行为
一套输入动作和玩家相关联，帮助我们监听一些按键的输入

Default Control Scheme：默认启用哪一个控制方案
Default Actions Map：默认启用哪一个行为映射方案
Camera：关联摄像机，当分屏设置时才需修改此选项

Behavior：如何通知游戏对象上执行对应逻辑

SendMessage：将逻辑脚本挂载在和 Playerlnput 同一对象上，会通过 SendMessage 通知执行对应函数
BroadcastMessage：将逻辑脚本挂载在其自身或子对象上。会通过 BroadcastMessage 通知执行对应函数
Invoke UnityEvent Actions：通过拖拽脚本关联函数指明想要执行的函数逻辑
Invoke CSharp Events：通过 C# 事件监听处理对应逻辑，通过获取 PlayerInput 进行事件监听
## 二、PlayerInput 行为模式
### （一）Send Messages
​ 在自定义脚本中，声明名为 “On+行为名” 的函数，没有参数或者参数类型为 InputValue
​ 将该自定义脚本挂载到 PlayerInput 依附的对象上，当触发对应输入时会自动调用函数，并且还有默认的 3 个和设备相关的函数可以调用
- 设备注册（当控制器从设备丢失中恢复并再次运行时会触发）：OnDeviceRegained (PlayerInput input)
- 设备丢失（玩家失去了分配给它的设备之一，例如，当无线设备耗尽电池时）：OnDeviceLost (PlayerInput input)
- 控制器切换：OnControlsChanged (PlayerInput input)
### （二）Broadcast Messages
​ 基本和 SendMessage 规则一致
​ 唯一的区别是，自定义脚本不仅可以挂载在 PlayerInput 依附的对象上，还可以挂载在其子对象下
### （三）Invoke Unity Events
​ 该模式可以让我们在 Inspector 窗口上通过拖拽的形式关联响应函数
​ 但是注意：响应函数的参数类型需要改为 InputAction. CallbackContext
![[Pasted image 20240809140727.png|450]]
```csharp
public class PlayerController : MonoBehaviour
{
    public void moveControl(InputAction.CallbackContext value)
    {
        Vector2 moveVal = value.ReadValue<Vector2>();
        Debug.Log(moveVal);
    }
}
```
### （四）Invoke C Sharp Events
Similar to `Invoke Unity Events`, except that the events are plain C# events available on the `PlayerInput` API. You cannot configure these from the Inspector. Instead, you have to register callbacks for the events in your scripts.
```csharp
// 1.获取PlayerInput组件
PlayerInput input = this.GetComponent<PlayerInput>();
// 2.获取对应事件进行委托函数添加
input.onDeviceLost      += OnDeviceLost;
input.onDeviceRegained  += OnDeviceRegained;
input.onControlsChanged += OnControlsChanged;
input.onActionTriggered += OnActionTrigger;

// input.currentActionMap["Move"].ReadValue<Vector2>()

// 3.当触发输入时会自动触发事件调用对应函数
	void OnEnable()
    {
        input.onActionTriggered += MyEventFunction;
    }
    void OnDisable()
    {
        input.onActionTriggered -= MyEventFunction;
    }
    void MyEventFunction(InputAction.CallbackContext value)
    {
        Debug.Log(value.action.name + (" was triggered"));
    }
```
在我自己尝试下发现上述四种的官方组件调用方式都只在输入发生时触发时发送一次输入返回，并不会持续发送，**所以如果要实现输入控制角色移动这种需要持续返回输入信号功能的并不适合该方式**。该方式仅适合如菜单界面点击按钮或者跳跃功能这种仅需输入时触发一次返回的功能。
## 三、脚本调用
基于上述提示，所以官方 PlayerInput 组件调用动作事件函数时并不能满足我们所有的场景需求（也可能是我在持续返回信号上没找到解决方案），所以我们还需要学习一下不借助官方 PlayerInput 组件的事件调用。我们直接在我们的脚本中调用 InputSystem 中的动作事件。

在我们使用脚本调用之前我们需要做一件事情，在我们创建好的 InputActions 属性面板中找到 Generate C# Class 并勾选, 随后点击 Apply 生成对应的脚本，之后我们就可以在我们自己写的 PlayerController 类中调用该脚本了
![[Pasted image 20240809141304.png|500]]
```csharp
using UnityEngine;
using UnityEngine.InputSystem;
public class CSharpEvent : MonoBehaviour
{
    private PlayerInputActions playerInputActions;
    //将对应的ActionMaps中对应的Action进行传址引用
    public Vector2 keyboardMoveAxes => playerInputActions.keyboard.moveControl.ReadValue<Vector2>();
    void Awake() 
    {
    	//实例化InputActions脚本
        playerInputActions = new PlayerInputActions();
    }
    private void OnEnable()
    {
    	//将要使用的ActionMap开启
        playerInputActions.keyboard.Enable();
    }
    private void OnDisable()
    {
    	//上述同理
        playerInputActions.keyboard.Disable();
    }
    private void Update()
    {
    	//在帧更新方法中调用所写的动作方法
        movePlayer();
    }
    private void movePlayer()
    {
    	//因为要在Update方法中使用，需要需要先判断是否有输入对应的Input操作
        if(keyboardMoveAxes != Vector2.zero){
        	//判断有输入后便执行对应方法
            Debug.Log(keyboardMoveAxes);
        }
    }
}
```