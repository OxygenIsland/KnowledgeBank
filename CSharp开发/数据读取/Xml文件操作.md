---
title: "[[Xml文件操作]]"
type: Literature
status: done
Creation Date: 2024-03-31 20:32
tags:
---
Xml 文件，是一个可拓展标记语言，它可以用来标记数据局、定义数据类型等。
需要注意的是它的节点，Xml 文件必须要有一个根节点，然后根据根节点去找子节点，然后根据子节点去找子节点的子节点，所以在这一点上跟其他文件还是不太一样的。
而正是由于这个特点，Xml 非常适合在万维网传输，提供统一的方法来描述的结构化数据。
## 1、创建 Xml 文件
```csharp
using System.IO;
using System.Xml;
using UnityEngine;

public class Demo5 : MonoBehaviour
{
    void Start()
    {
        CreateXML();
    }

    //创建XML
    void CreateXML()
    {
        string path = Application.streamingAssetsPath + "/data.xml";
        //创建xml文档
        XmlDocument xml = new XmlDocument();
        //创建根节点
        XmlElement root = xml.CreateElement("Node");

        //创建根节点的子节点
        XmlElement element = xml.CreateElement("Person");
        //设置根节点的子节点的属性
        element.SetAttribute("id", "1");
        //添加两个子节点到根节点的子节点的下面
        XmlElement elementChild1 = xml.CreateElement("Name");
        elementChild1.SetAttribute("name", "");
        elementChild1.InnerText = "王五";
        XmlElement elementChild2 = xml.CreateElement("Age");
        elementChild2.SetAttribute("age", "");
        elementChild2.InnerText = "18";
        //把节点一层一层的添加至xml中，注意他们之间的先后顺序，这是生成XML文件的顺序
        element.AppendChild(elementChild1);
        element.AppendChild(elementChild2);


        //再创建一个根节点的子节点
        XmlElement element2 = xml.CreateElement("Person");
        //设置根节点的子节点的属性 名字一样 属性不一样也可以
        element2.SetAttribute("id", "2");
        //添加两个子节点到根节点的子节点的下面
        XmlElement elementChild3 = xml.CreateElement("Name");
        elementChild3.SetAttribute("name", "");
        elementChild3.InnerText = "李四";
        XmlElement elementChild4 = xml.CreateElement("Age");
        elementChild4.SetAttribute("age", "");
        elementChild4.InnerText = "22";
        element2.AppendChild(elementChild3);
        element2.AppendChild(elementChild4);

        //把节点一层一层的添加至xml中，注意他们之间的先后顺序，这是生成XML文件的顺序
        root.AppendChild(element);
        root.AppendChild(element2);
        xml.AppendChild(root);

        //最后保存文件
        xml.Save(path);
    }
}
```
运行结果如下图所示：
![[Pasted image 20240205102212.png|339]]
## 2、读取 Xml 文件
读取Xml，需要从根节点一层一层往下找，根节点找子节点，子节点找孙节点。
### 属性查找
```csharp
using System.IO;
using System.Xml;
using UnityEngine;

public class Demo5 : MonoBehaviour
{
    void Start()
    {
        LoadXml();
    }

    //读取XML
    void LoadXml()
    {
        XmlDocument xml = new XmlDocument();
        xml.Load(Application.streamingAssetsPath + "/data.xml");
        XmlNodeList xmlNodeList = xml.SelectSingleNode("Node").ChildNodes;
        //遍历所有子节点
        foreach (XmlElement xl1 in xmlNodeList)
        {
            if (xl1.GetAttribute("id") == "1")
            {
                //继续遍历id为1的节点下的子节点
                foreach (XmlElement xl2 in xl1.ChildNodes)
                {
                    if (xl2.GetAttribute("name") == "")
                    {
                        Debug.Log(xl2.InnerText);
                    }
                    else if (xl2.GetAttribute("age") == "")
                    {
                        Debug.Log(xl2.InnerText);
                    }
                }
            }
        }
    }
}
```
运行结果如下：
![[Pasted image 20240205103013.png|464]]
### 节点名字查找
```csharp
using System.IO;
using System.Xml;
using UnityEngine;

public class Demo5 : MonoBehaviour
{
    void Start()
    {
        ReadXml();
    }

    //读取XML
    void ReadXml()
    {
        XmlDocument xml = new XmlDocument();
        xml.Load(Application.streamingAssetsPath + "/data.xml");
        XmlNodeList xmlNodeList = xml.SelectSingleNode("Node").ChildNodes;
        //遍历所有子节点
        foreach (XmlElement xl1 in xmlNodeList)
        {
            if (xl1.Name == "Person" && xl1.GetAttribute("id") == "1")
            {
                //继续遍历名字叫做Person，id为1的节点下的子节点
                foreach (XmlElement xl2 in xl1.ChildNodes)
                {
                    if (xl2.Name == "Name")
                    {
                        Debug.Log(xl2.InnerText);
                    }
                    else if (xl2.Name == "Age")
                    {
                        Debug.Log(xl2.InnerText);
                    }
                }
            }
        }
    }
}
```
### 其他查找方式
```csharp
using System.IO;
using System.Xml;
using UnityEngine;

public class Demo5 : MonoBehaviour
{
    void Start()
    {
        ReadXml();
    }
    //读取XML
    void ReadXml()
    {
        XmlDocument xml = new XmlDocument();
        xml.Load(Application.streamingAssetsPath + "/data.xml");
        //获取根节点
        XmlNode rootNode = xml.FirstChild;
        XmlNodeList nodeList = rootNode.ChildNodes;
        //遍历所有子节点
        int Count = nodeList.Count;
        for (int i = 0; i < Count; i++)
        {
            Debug.Log(nodeList.Item(i).InnerText);
        }
    }
}
```
## 3、序列化
如何将 c# 中的一个类转换为 xml 文件呢？如何将 xml 文件转换为 c # 中的一个类文件呢？首先要创建一个与 xml 文件结构类似的类进行转换。
```csharp
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Xml.Serialization;

[System.Serializable] //可序列化标签
public class TestSerilize
{
	[XmlAttribute("Id")]   //xml标签(需要序列化的数据都需要加上标签)
	public int Id { get; set; }
	[XmlAttribute("Name")] 
	public string Name { get; set;}
	[XmlElement("List")]   //序列化一个链表的标签
	public List<int> List { get; set; }
	public bool ShouldSerializeList
	{
		//该函数在序列化的时候被自动调用，如果返回的是true，则序列化List字段，反之则不进行序列化。
	}
}
```
有了这个类文件之后，就可以实现二者之间的互相转换
```csharp
using System.Collections;
using System.Collections.Generic;
using System.Xml.Serialization;
using UnityEngine;
using System.IO;  //文件流
public class ClassToXmlTest : MonoBehaviour 
{
   void Start()
   {
		SerializeTest();  //序列化
		DeSerializerTest();  //反序列化
   }	
    void SerializeTest()
    {
        //给类先赋值（测试需要）
        TestSerilize testSerilize = new TestSerilize();
        
        //创建文件流  FileStream第一个参数是创建文件的路径
        FileStream fileStream = new FileStream(Application.dataPath + "/test.xml", 
        FileMode.Create, FileAccess.ReadWrite, FileShare.ReadWrite);
        //创建写入流
        StreamWriter sw = new StreamWriter(fileStream, System.Text.Encoding.UTF8);
        //序列化
        XmlSerializer xml = new XmlSerializer(testSerilize.GetType());
        //设置名称空间
        XmlSerializerNamespaces namespaces = new XmlSerializerNamespaces(); 
        namespaces.Add("name", "namespaceURI"); 
        
        xml.Serialize(sw, testSerilize，namespaces);
        //关闭文件流
        sw.Close();
        fileStream.Close();
    }
    void DeSerializerTest();
    {
	    FileStream fs = new FileStream(Application.dataPath + "/test.xml", FileMode.Open, 
        FileAccess.ReadWrite, FileShare.ReadWrite);
        XmlSerializer xs = new XmlSerializer(typeof(TestSerilize));
        TestSerilize testSerilize = (TestSerilize)xs.Deserialize(fs);
        fs.Close();
    }
}
```