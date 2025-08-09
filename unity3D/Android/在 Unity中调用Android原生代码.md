---
title: "[[在 Unity中调用Android原生代码]]"
type: Permanent
status: done
Creation Date: 2025-08-09 10:59
tags: 
---

**1. 创建正确的文件夹结构**

Unity 对插件的存放位置有特殊要求。
- 在你的 Unity 项目的 Assets 文件夹下，创建一个名为 Plugins 的文件夹。[4](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHx86Pium89-KhZRC1sJS96kQ4iffDEA37OFBhYa3XO2-KYk9h0XTO12qxUgc29r2spM31kHG6jzI1HdE4ASBMSceRMA8epOyRnmBlv_7RMkomyina8avpD9mjA-LVkJYaEv8sX_kY%3D)
- 在 Plugins 文件夹下，再创建一个名为 Android 的文件夹。[4](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHx86Pium89-KhZRC1sJS96kQ4iffDEA37OFBhYa3XO2-KYk9h0XTO12qxUgc29r2spM31kHG6jzI1HdE4ASBMSceRMA8epOyRnmBlv_7RMkomyina8avpD9mjA-LVkJYaEv8sX_kY%3D)
    
**2. 导入 AAR 文件**
- 将你在 Android Studio 中生成的 .aar 文件复制到 Assets/Plugins/Android 目录下。[10](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQFlsJnP8YhcORLJ46tmYBunetWdCg3GMH4n-t0aLgGgkEP9Xxf_GOWETNfS1-UZeNFQLYryrPqYmGYmbM87Qtx3ZRobRO7S4XG1-ptjIH53SPiGb1ariFOoudXh9kTadgAh04B4z6JJzfzDR-NNALfOCe6EIR1nSxGmS2B7vi4UsdVFgl7ciME2U-oT5jnr)
    
**3. 在 Unity (C#) 中调用原生代码**

现在你可以通过 C# 脚本来调用你在 Java/Kotlin 中编写的方法了。Unity 提供了 AndroidJavaClass 和 AndroidJavaObject 两个核心类来实现这一功能。[11](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHC-QjheB-RMPi7Rk9ierlCmgcfSTvbYbWMxHiEGcEnCmS-_iSk_kZfRHLTkuNzS4cI4mRurR4wTijh3u64gXQCk4nlSz2aANohBh2gHeMPnZGCmJ4v2SPWKba-IrHvHcwRjpvhW6vY8BCPYu_Ob5AXrY8-Nd8tRjO9vLincPY9x7w6HE-LJr0eqphAsDjPMrS6GHFro1fjTa4TXA%3D%3D)[12](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHjS6_rckModhyP9ip8SyfX3nAq7fQN5EkH3815rl4RJ-Uw64MMf_rqdv9JKfh0QQ6Qkh6ucw-dYAnrdGV12ScM4Zqmk4V4xJBA5bKwC4aul-Cc4xlCUpolC4wq2uLyT8LkcSIcEYrUX2fAmhOwfmi8DhJdsHF9TDrF9SeOmt2bqpj8iKZL5PI%3D)
- AndroidJavaClass: 用于访问 Java 类中的静态方法和静态字段。[13](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQFi_ucADYTj5rlw4C4IatyB4VftFwD8OtoyvAhGrFdL44kjK_XpQB-qAdiCIIodC-6lRwkK79Mhe6mM18IcSjt0irWjg_0wLO_wKvoiihfUkZArNvAzjBy3L5GKgw7XoFub_mFzfUveKqY5I1zQOuw_LA%3D%3D)
- AndroidJavaObject: 用于创建 Java 类的实例，并调用实例方法和访问实例字段。[13](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQFi_ucADYTj5rlw4C4IatyB4VftFwD8OtoyvAhGrFdL44kjK_XpQB-qAdiCIIodC-6lRwkK79Mhe6mM18IcSjt0irWjg_0wLO_wKvoiihfUkZArNvAzjBy3L5GKgw7XoFub_mFzfUveKqY5I1zQOuw_LA%3D%3D)
下面是一个 C# 脚本示例，演示如何调用我们之前创建的插件：
```csharp
using UnityEngine;
using UnityEngine.UI;

public class PluginTester : MonoBehaviour
{
    // Java 类的完整路径 (包名 + 类名)
    private const string PluginName = "com.example.myunityplugin.MyPlugin";

    private AndroidJavaClass pluginClass;
    private AndroidJavaObject pluginInstance;

    void Start()
    {
        // 获取 Unity Player 的 Activity
        AndroidJavaClass unityPlayer = new AndroidJavaClass("com.unity3d.player.UnityPlayer");
        AndroidJavaObject activity = unityPlayer.GetStatic<AndroidJavaObject>("currentActivity");

        // 获取我们的插件类
        pluginClass = new AndroidJavaClass(PluginName);

        // 调用静态方法，将 Activity 传给插件
        pluginClass.CallStatic("receiveUnityActivity", activity);
    }

    public void OnShowToastButtonClick()
    {
        // 调用插件的静态方法来显示 Toast
        pluginClass.CallStatic("showToast", "Hello from Unity!");
    }

    public void OnGetNumberButtonClick()
    {
        // 调用插件的静态方法并获取返回值
        int number = pluginClass.CallStatic<int>("getFive");
        Debug.Log("Number from plugin: " + number);
    }
}
```

**4. 从安卓插件调用 Unity 方法**

如果你需要在原生代码执行完某些操作后通知 Unity（例如，广告加载完成、支付成功等），你可以使用 UnityPlayer.UnitySendMessage 方法。[14](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQFrwCcPAkbXUKLYQ8YLdLhUQufyjOjlp-G0vyJ5Eoq-Uzqfk0DazFynyKcsCuyN7SOa3_X9MBvHbuTw0396yiCN20pWe4l0viDbEkq4Xuu4YRqfrwo_fUpF983_8F9x8d0LgaSSNmXdDxEOnbIYedJCmEJS41qCh28BR5uLJFX09FB1xbdoHzKf-gSrIFn5y6sItvHc)

- **UnityPlayer.UnitySendMessage 的三个参数:**
    1. GameObject 名称：场景中挂载了接收脚本的游戏对象的名称。
    2. Method 名称：要调用的 C# 方法的名称。
    3. Message：要传递的字符串参数。
```java
import com.unity3d.player.UnityPlayer;

public class MyPlugin {
    // ... 其他代码 ...
    public static void SendMessageToUnity() {
        // 参数1: 场景中的游戏对象名
        // 参数2: 该对象上脚本中的公共方法名
        // 参数3: 传递的字符串消息
        UnityPlayer.UnitySendMessage("MyGameObject", "HandlePluginMessage", "This is a message from Android!");
    }
}
```

```csharp
using UnityEngine;

public class UnityReceiver : MonoBehaviour
{
    public void HandlePluginMessage(string message)
    {
        Debug.Log("Received message from Android plugin: " + message);
    }
}
```
确保将此脚本挂载到场景中一个名为 "MyGameObject" 的游戏对象上。