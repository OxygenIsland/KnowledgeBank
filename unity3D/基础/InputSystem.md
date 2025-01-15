---
title: "[[InputSystem]]"
type: Literature
status: done
Creation Date: 2024-08-08 15:20
tags:
---
新的 Input System 在使用上与旧的 Input Manager 有很大的区别。旧的 Input Manager 虽然也是通过配置来设置很多的“虚拟轴”，然后在代码中获取“虚拟轴”来获取用户的输入，然后做进一步的处理。并且，这些代码都需要放置到 Update 方法中执行。而新的 Input System 系统也需要进行一些配置。显然，这些配置比旧系统更加复杂。新系统配置主要就是添加一个个的 InputAction，每一个 InputAction 同可以绑定不同的输入设备上面的按键。这个 InputAction 非常类似旧系统中的“虚拟轴”。但是两者的区别在于，旧系统的设备输入是通过在代码中进行判断的；而新系统则是通过“Player Input”这个组件来获取，并指定脚本方法来执行的。从设计角度出发，旧系统只是对输入设备的封装，而新系统不仅是对输入设备的封装，还是对输入逻辑的封装。因此，新系统虽然复杂一下，但是去掉配置的内容之外（就是我们添加的 inputactions 文件，我们可以在这个文件中配置所有的输入情况），剩余的就是使用脚本方法来处理不同输入对应的游戏逻辑。新系统使得我们的代码书写结构更加清晰，每一个输入都对应一个脚本方法来处理，这个设计还是非常不错的。

Input System 有两种使用方式。第一种就是直接从输入设备获取输入；第二种就是基于 InputAction 输入动作来获取。我们重点介绍第二种 InputAction 输入动作。
## InputActions
### InputActions 概念及结构关系
在 InputSystem 中所用到结构关系为 :    InputSystem=>InputActions=>ActionMaps=>Actions
首先，我们要理解如下概念：
- InputAction：玩家的每一个输入都可以理解为是一个 InputAction（输入动作）。
- InputActionMap：就是管理一些 InputAction 的一个集合（例如前后左右输入动作）。
- InputController：就是管理具体硬件设备的输入（可以设置不同设备的按键）。
- InputBinding：用于绑定 InputAction 和 InputController（设备按键和输入动作关联）。
### ActionMaps
简单来说我们可以将 InputActions 视为我们项目里其中一个控制器的输入操作管理集，而 ActionMaps 则为该控制器其中的一个输入映射集。
![[Pasted image 20240809141907.png|425]]
### Actions
Actions为ActionMaps里其中一个动作输入映射
#### ActionProperties
在Actions中也有许多参数，其中ActionType则是我们最常用到。其概念为我们该动作输入映射的类型，有以下三种类型
![[Pasted image 20240809135817.png|500]]
- Value：主要用于状态连续更改的输入，例如鼠标的移动，游戏手柄的摇杆等等。如果有多个设备绑定这个 Action（不同的设备该如何绑定这个 action? ），只会发送当前使用设备的输入。
- Button ：用于每次按下时触发的 Action，就是普通的按键而已。默认值。
- Pass-Through：和 Value 一样，区别在于如果有多个设备绑定这个 Action，会发送所有设备的输入。
在使用 Value 或者 Pass Through Types 时，你会看到一个额外的选项 Control Type 为该 Value 的返回值类型
![[Pasted image 20240809140033.png|500]]
#### InputActions 常用实例
在我们Unity项目中输入检测做常用的两种功能实现  
1.角色移动时持续输入 - Value  
在我们选择 ActionType 为 Value 之后会出现 Control Type，以下为常用的 Control Type 列举

| Control Type | 使用场景     |
| ------------ | -------- |
| Axis         | 仅为单轴方向数值 |
| Vector 2     | 为双轴方向数值  |
| Vector 3     | 为三轴方向数值  |
2.攻击或点击菜单栏时一次性输入 - Button
### Notification behaviors
You can use the [`Behavior`](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.10/api/UnityEngine.InputSystem.PlayerInput.html#UnityEngine_InputSystem_PlayerInput_notificationBehavior) property in the Inspector to determine how a `PlayerInput` component notifies game code when something related to the player has occurred.
## Exemple
在Actions中也有许多参数，其中ActionType则是我们最常用到。其概念为我们该动作输入映射的类型，有以下三种类型
接下来，我们就来演示如何使用，创建一个立方体 Cube，然后为其添加一个 [[PlayerInput|PlayerInput]] 组件。
![[Pasted image 20240808183129.png|429]]
添加好组件后，如果我们要接受到输入，还需要创建 InputAction。我们可以点击组件上的 Create Actions 按钮来创建。这个文件其实就是一个配置文件（纯 JSON 格式存储），它包含了输入动作及其关联的绑定和控制方案。虽然它是一个文件，但是 Unity 提供了该文件的图形编辑界面。如下所示
![[Pasted image 20240808183250.png|550]]
最左边是两个 Action Maps，他们分别是 Player 和 UI。他们是 Unity 为我们提前预制的 Action Maps。我们点击“Player”就会在右边的“Actions”中显示该集合下面的 InputAction。我们看到分别有三个：Move，Look，Fire。我们继续点开查看下级具体的 InputAction。例如，我们点开 Move 这个 InputAction，它的下面就是多个 InputBinding。注意 InputBinding 的类型不一样的话，它的设置也不一样的。
![[Pasted image 20240808184021.png|500]]
![[Pasted image 20240808184040.png|500]]
我们可以点击其中一个 InputBinding，比如上图中的“WASD”。这个 InputBinding 根据名称我们大致理解，是用来控制上下左右四个方向的输入。因此它的下一级最少要设置四个方向（up, down, left, right）的输入配置。例如上图中的第一个输入设置“Up: W\[Keyboard]”, 这个应该是键盘的字母 W 按键，对应的就是向上“Up”的输入信息。同时，我们可以在右边的“Binding Properties”中看到详细的配置。
- Path 就是我们的设备按键。
- Composite Part 应该是多个输入值的选项。
- Use in control scheme 则是设备类型，他们的值含义如下
	- Keyboard&Mouse：键盘和鼠标
	- Gamepad：游戏手柄
	- Touch：触摸屏
	- Joystick：摇杆
	- XR：VR/AR 设备
接下来，我们就手动添加一个自定义的“InputAction”
我们点击“Actions”右边的加号，添加一个新的“InputAction”，命名为“Test”。接下来，我们来查看“Test”右边的“Action Properties”界面。该界面一共有三个配置项：Action，Interactions 和 Processors。我们重点介绍 Action 里面的内容。Action Tpye 来定义我们“InputAction”的类型，它一共有三个值可以选择：[[InputSystem#ActionProperties|Value，Button 和 Pass-Through]]。


接下来，我们就可以给我们的“Test”添加“InputBinding”绑定，这个“InputBinding”可以添加多个的，也就是说一个“InputAction”可以添加多个“InputBinding”。这里，我们添加一个就行了。我们点击“Test”右边的加号，我们可以添加不同类型的 InputBinding。
![[Pasted image 20240809113130.png|500]]
- Add Binding 普通的绑定，可以绑定一个按键，鼠标，游戏手柄等
- Add Positive\NegativeBinding 两个按键的组合, 一个代表正数, 一个为负数
- Add Button With One Modifier 需要同时按下两个按钮的组合，例如 ctrl + j
- Add Button With Two Modifiers 需要同时按下三个按钮的组合，例如 shift + ctrl + j

其实我们发现在“Test”的下面就已经默认有一个\<No Binding>了，它就是一个 Add Binding 普通的绑定，我们就直接使用它就可以了。请注意，这个“Test”和我们上面介绍的“WASD”是不一样的类型设置。我们点击选中它，然后查看右边的“Binding Properties”界面。
![[Pasted image 20240809113301.png|500]]
选择“Keyboard”键盘
![[Pasted image 20240809113544.png|275]]
我们选择“By Character Mapped to Key”
![[Pasted image 20240809113625.png|227]]
我们随便选择一个“M”字母按键
![[Pasted image 20240809113650.png|475]]
此时，Path 处就会显示我们的“M”按键，我们在勾选“Keyboard&Mouse”一项即可完成“InputAction”的设置啦。接下来，我们回到“Player Input”组件中去。我们在该组件中找到“Behavior”行为一项，它的默认值是“Send Messages”，我们换成“Invoke Unity Events”。
![[Pasted image 20240809113806.png|454]]
选择完毕后，就会下面出现“Events”项目，在该项目的下面会有“Player”和“UI”两个子项目。大家应该能够猜到，这两个就是我们刚刚在“NewInputProject. Inputactions”配置文件中显示的“Action Maps”。我们可以点开“Player”查看它的子项目
![[Pasted image 20240809134133.png|429]]
 在最下面就会出现我们刚刚添加的“Test”的 InputAction 项目。接下来，我们需要创建一个脚本“TestScript.cs”文件，并且附加到 Cube 上面。
```csharp
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
 
public class TestScript : MonoBehaviour
{
    public void OnTest()
    {
        Debug.Log("Input M");
    }
}
```
我们可以点击下面的加号添加上面的脚本，并将 OnTest 方法赋予我们的“Test” 的“InputAction”项目。如下所示
![[Pasted image 20240809134640.png|454]]
添加完之后，我们就可以运行整个工程了。然后按下键盘上面的“M”按键测试。
![[Pasted image 20240809134656.png]]
