## 一、前言
### 1-1、EventTrigger简介
EventTrigger 是 Unity 中用于处理 UI 事件的一个组件。它允许我们为 UI 元素（如按钮、图像等）添加事件监听器，从而响应各种交互事件，如鼠标点击、悬停、拖拽等。使用 `EventTrigger` 可以避免手动编写复杂的事件处理代码，使 UI 事件的响应更加简洁和易于管理。比手写 UI 的 Event 快很多,方便很多。
### 1-2、EventTrigger 触发条件
EventTrigger想要触发，需要有EventSystem、StandaloneInputModule、TouchInputModule，后面两个组件都继承自`BaseInputModule`。

EventSystem组件主要负责处理输入、射线投射以及发送事件。  
一个场景中只能有一个 `EventSystem` 组件，并且需要 BaseInputModule 类型组件的协助才能工作。EventSystem 在一开始的时候会把自己所属对象下的 BaseInputModule类型组件加到一个内部列表，并且在每个 Update 周期通过接口 `TickModules` 接口调用这些基本输入模块的 `UpdateModule` 接口，然后 `BaseInputModule` 会在 `UpdateModule` 接口中将自己的状态修改成’Updated’，之后 `BaseInputModule` 的 Process 接口才会被调用。
![[Pasted image 20241213164759.png|511]]
BaseInputModule 是一个基类模块，负责发送输入事件（点击、拖拽、选中等）到具体对象。EventSystem下的所有输入模块都必须继承自 BaseInputModule组件。  
StandaloneInputModule和 TouchInputModule组件是系统提供的标准输入模块和触摸输入模块，我们可以通过继承 BaseInputModule实现自己的输入模块。
![[Pasted image 20241213165030.png|408]]
除了以上两个组件，还有一个很重要的组件通过 EventSystem 对象我们看不到，它是 BaseRaycaster 组件。BaseRaycaster 也是一个基类，前面说的输入模块要检测到鼠标事件必须有射线投射组件才能确定目标对象。系统实现的射线投射类组件有 PhysicsRaycaster, Physics2DRaycaster, GraphicRaycaster。这个模块也是可以自己继承 BaseRaycaster 实现个性化定制。
![[Pasted image 20241213165047.png|414]]
总的来说，EventSystem 负责管理，BaseInputModule 负责输入，BaseRaycaster 负责确定目标对象，目标对象负责接收事件并处理，然后一个完整的事件系统就有.
### 1-3、EventTrigger 使用步骤（可视化）
添加 EventTrigger 组件：
![[Pasted image 20241213170036.png|426]]
添加响应事件类型：
![[Pasted image 20241213170052.png|412]]
实现响应函数：
![[Pasted image 20241213170114.png|403]]
接下来是代码添加 `EventTrigger` 的步骤。
### 1-4、EventTrigger使用步骤（代码）
1. 添加 EventTrigger 组件：
``` csharp
   gameObject.AddComponent<EventTrigger>();
```
2. 创建 EventTrigger.Entry 对象
   在脚本中，为每种需要监听的事件创建一个 EventTrigger.Entry 对象。
3. 设置 EventID 和回调函数
   为每个 EventTrigger.Entry 对象设置 eventID，这是一个枚举类型，表示不同的事件类型（如 PointerEnter、PointerClick 等）。  
   通过 callback.AddListener 方法添加回调函数。这些函数将在事件发生时被调用。
4. 将 Entry 对象添加到 EventTrigger
   将每个 EventTrigger.Entry 对象添加到 EventTrigger 组件的 triggers 列表中。
5. 实现回调函数
   在脚本中实现回调函数，处理事件。例如，我们可以改变 UI 元素的颜色、播放声音或更新游戏状态。
```csharp
using UnityEngine.EventSystems; 
public class PointerTest : MonoBehaviour 
{ 
	public Transform Target; 
	void Start() 
	{ 
		AddListener(Target, EventTriggerType.PointerClick, (PointerEventData data) => { Debug.Log("点击到物体。"); }); 
	} 
	public void AddListener(Transform tra,EventTriggerType eventType, Action<PointerEventData> listenedAction) 
	{ 
		EventTrigger.Entry entry = new EventTrigger.Entry(); 
		entry.eventID = eventType; 
		entry.callback.AddListener(data => listenedAction.Invoke((PointerEventData)data)); 
		tra.GetComponent<EventTrigger>().triggers.Add(entry); 
	} 
}
```
**代码提示：**  
1、获得EventTrigger组件  
2、声明EventTrigger组件中的内部类Entry对象  
3、设置Entry的EventID和callback函数  
4、将声明好的 Entry 对象添加到 EventTrigger 中的 List 类型的列表 trigger 中即可
## 二、正文
### 2-1、添加响应组件
`EventTrigger`想要触发，需要有`EventSystem、StandaloneInputModule`组件。
`EventSystem` 组件主要负责处理输入、射线投射以及发送事件：
![[Pasted image 20241213170825.png|411]]
`StandaloneInputModule` 组件是系统提供的标准输入模块和触摸输入模块，我们可以通过继承 `BaseInputModule` 实现自己的输入模块：
![[Pasted image 20241213170842.png|408]]
输入模块要检测到鼠标事件必须有射线投射组件才能确定目标对象。系统实现的射线投射类组件有 `PhysicsRaycaster`：
![[Pasted image 20241213170902.png|414]]
### 2-2、实现 EventTrigger 对3D 物体的响应
使用拓展类来封装 EventTrigger 事件：
```csharp
public static class UnityActonTools 
{ 
	public static void AddEvent(this Transform tra, EventTriggerType eventType, Action<PointerEventData> listenedAction) 
	{ //添加组件——EventTrigger 
		EventTrigger trigger = null; 
		if (tra.GetComponent<EventTrigger>() != null) 
		{ 
			trigger = tra.GetComponent<EventTrigger>(); 
		} 
		else 
		{ 
			trigger = tra.gameObject.AddComponent<EventTrigger>(); 
		} 
		EventTrigger.Entry entry = new EventTrigger.Entry(); 
		entry.eventID = eventType; 
		entry.callback.AddListener(data => listenedAction.Invoke((PointerEventData)data)); 
		trigger.triggers.Add(entry); 
	} 
}
```
实现过程1-4小节已经说明，这里不再赘述。
**调用：**
```csharp
public class PointerTest : MonoBehaviour 
{ 
	public Transform Target; 
	void Start() 
	{ 
		Target.MouseClickAction(EventTriggerType.PointerClick, (PointerEventData data) => { Debug.Log("点击到物体。"); }); 
	} 
	public void MouseClickAction(Transform target, Action act = null) 
	{ 
		target.GetComponent<BoxCollider>().enabled = true; 
		target.AddEvent(EventTriggerType.PointerClick, (PointerEventData data) => 
		{ 
			target.GetComponent<BoxCollider>().enabled = false; 
			act?.Invoke(); 
		}); 
	} 
}
```
### 2-3、使用 EventTrigger 可视化响应
先实现代码：
```csharp
public class PointerTest : MonoBehaviour 
{ 
	public Transform Target; 
	Color oricolor = Color.white;//物体本来的颜色 
	public void ChangCutMat(int index) 
	{ 
		switch (index) 
		{ 
			case 0: 
				Target.GetComponentInChildren<Renderer>().material.color = Color.cyan; 
				break; 
			case 1: 
				Target.GetComponentInChildren<Renderer>().material.color = oricolor; 
				break; 
			case 2: 
				Debug.Log("点击到物体。"); 
				break; 
		} 
	} 
}
```
然后给物体增加 EventTrigger 组件，添加进入、离开、点击事件：
![[Pasted image 20241213171531.png|404]]
运行结果：
![[QkqBJXMxzjiZAS7hlL1cfuvKRU4N.gif|475]]
### 2-4、OnMouseEnter 与 EventTrigger 互相影响的问题
众所周知，OnMouseEnter可以响应鼠标进入的响应，EventTrigger也可以做到，那么他们同时启用，会有什么结果呢？
请看 VCR，不对，请看代码：
```csharp
public class ModelTagShow : MonoBehaviour 
{ 
	Color oricolor = Color.white;//物体本来的颜色 
	private void Start() 
	{ 
		Transform target = this.transform; 
		target.AddEvent(EventTriggerType.PointerEnter, (PointerEventData data) => 
		{ 
			GetComponentInChildren<Renderer>().material.color = oricolor; 
		}); 
		target.AddEvent(EventTriggerType.PointerExit, (PointerEventData data) => 
		{ 
			GetComponentInChildren<Renderer>().material.color = Color.cyan; 
		}); 
	} 
	void OnMouseEnter() 
	{ 
		GetComponentInChildren<Renderer>().material.color = Color.cyan; 
	} 
	void OnMouseExit() 
	{ 
		GetComponentInChildren<Renderer>().material.color = oricolor; 
	} 
}
```
提示：  
OnMouseEnter进入变色，OnMouseExit退出变成原色。  
EventTriggerType.PointerEnter 进入变成原色，EventTriggerType.PointerExit 退出变色。
那么，会发生什么呢，把脚本挂载在对象上：
![[Pasted image 20241213171932.png|407]]
运行程序：
![[QkqBJXMxzjiZAS7hlL1cfuvKRU4N 1.gif|500]]
答案是都影响，并且相互影响。
所以，还是不推荐大家两种鼠标进入事件同时使用，可以使用 `OnMouseEnter` 进入，`OnMouseExit` 退出，加上 `EventTrigger` 的点击，非常好用，示例代码：
```csharp
public class ModelTagShow : MonoBehaviour 
{ 
	Color oricolor = Color.white;//物体本来的颜色 
	private void Start() 
	{ 
		Transform target = this.transform; 
		target.AddEvent(EventTriggerType.PointerClick, (PointerEventData data) => { Debug.Log("点击到物体。"); }); 
	} 
	void OnMouseEnter() 
	{ 
		GetComponentInChildren<Renderer>().material.color = Color.cyan; 
	} 
	void OnMouseExit() 
	{ 
	GetComponentInChildren<Renderer>().material.color = oricolor; 
	} 
}
```