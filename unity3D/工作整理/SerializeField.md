---
title: "[[SerializeField]]"
type: Literature
status: done
Creation Date: 2023-09-27 12:47
tags:
---
## 可被 Serialize 的变量的定义方法

## 1. public 变量
在没有加入任何Attribute的前提下，public变量是默认被视为可以被Serialize的。
## 2. [SerializeField]Attribute
有时候我们需要Serialize一份private或者protected数据段，这个时候可以使用[SerializeField]这个Attribute:
[SerializeField] protected int foobar = 0;
注意: 这样定义出的成员变量是会在Inspector中显示出来。
## 3. 单独的class或structu
有时候我们会自定义一些单独的 class/struct, 由于这些类并没有从 MonoBehavior 派生所以默认并不被 Unity3D 识别为可以 Serialize 的结构。自然也就不会在 Inspector 中显示。我们可以通过添加 [System.Serializable]这个 Attribute 使 Unity3D 检测并注册这些类为可 Serialize 的类型。具体做法如下：
```csharp
[System.Serializable]
public class FooBar 
{
    public int foo = 5;
    public int bar = 10;
}
```
## 4. ScriptableObject
ScriptableObject 是Unity3D提供的一种特殊的处理数据存储的方法，具体请参考ScriptableObject的运用
# NonSerialize的变量的定义方法
## 1. protected, private, internal 变量
默认情况下，protected, private, internal变量将不会被serialize.
## 2. `[System.NonSerialized]`Attribute
有时候我们需要定义一些public变量方便操作，但是又不希望这些变量保留。这个时候可以利用[System.NonSerialized]来完成这个操作:
`[System.NonSerialized] public float foobar = 1.0f;`
## 3. readonly, const, static 修饰符
如果变量加入了 readonly, const, static 等修饰符，无论他的 serialize 设置如何，都将不会进行 serialize
## 4. Dictionary<T,K>
Unity3D 可以对 `List<T>` 进行序列化显示，但是由于他们的程序员偷懒或不够强大，以至于我们到现在都不能 `serialize Dictionary<T,K>` 这么一个较为常用的类型。通常我们会通过 Serialize 一份 `List<T>`，然后在 Awake 中初始化 Dictionary 的方法来完成 Dictionary 的 serialize 操作。
```csharp
[System.Serializable]
public class NameToID 
{
    public string name = "";
    public int ID = -1;
}
public List<NameToID> nameToIDList = new List<NameToID>();
Dictionary<string,int> nameToID = new Dictionary<string,int>();
void Awake () 
{
    foreach ( NameToID info in nameToIDList ) 
    {
        nameToID[info.name] = info.ID;
    }
    nameToIDList = null; // put it null make garbage collect it (I wish)
}
```
# Inspector 中的显示
变量在 Inspector 中会根据变量的大写字母来隔开来显示，并且会将首字母强制大写的方式显示。如:
`public int myFooBar = 0;`
首先，Unity 会自动为 Public 变量做序列化，序列化的意思是说再次读取 Unity 时序列化的变量是有值的，不需要你再次去赋值，因为它已经被保存下来。然后，什么样的值会被显示在面板上呢？答案是：已经被序列化，但是没有用 `[HideInInspector]` 标记的值。`[HideInInspector]`表示将原本显示在面板上的序列化值隐藏起来。
`[SerializeField]`表示将原本不会被序列化的私有变量和保护变量变成可以被序列化的，那么它们在下次读取的值就是你上次赋值的值。
## 1、如果 a 是公有的序列化变量。
（1）如果你想要在面板中看到变量a，那么用：  public int a;
（2）如果你不想在面板中看到变量a，那么用：`[HideInInspector]public int a;`
这样a可以在程序中被代码赋值，但不会在面板中看到,也不能手动设置赋值。
## 2、如果a是私有的序列化变量，你想在面板中读取并赋值，那么用:
`[SerializeField] private int a;`
## 3、如果 a 是私有的序列化变量，你想在面板中读取，但是不赋值，那么用：
```csharp
[HideInInspector][SerializedField] 
private int a;
public int b
{
	get{return a;}
}
```
## 4、如果 a 是私有序列化变量，你不想在面板中做任何操作(不想看到，也不想写)，但是想要在程序中给它赋值，那么用
```csharp
[HideInInspector][SerializedField]
 private int a;
 public int b
{
    get{return a;}
    set{a = value;}
}
```
