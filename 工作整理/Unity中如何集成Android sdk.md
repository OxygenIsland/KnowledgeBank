## **​1. 导入SDK到Unity​**​
- ​**​[[Android Archive|AAR包]]放置​**​： 
    将AAR文件复制到Unity项目的 `Assets/Plugins/Android/libs` 目录。
- ​**​依赖声明​**​：  
    创建 `Assets/Plugins/Android/mainTemplate.gradle`，添加远程仓库和依赖：
    遥控器 SDK（如 `rcsdk-v1.7.9.aar`）可能未发布在 Unity 默认的仓库（如 Google Maven 或 Maven Central）中。需在 `repositories` 块中添加其存储位置（如私有 Maven 仓库或本地路径）；
    
```gradle
repositories { 
    flatDir { dirs 'libs' } 
    google()  // 必需
}
dependencies {
    implementation(name: 'rcsdk-v1.7.9', ext: 'aar')
    // 其他依赖（如H16需单独导入）[1](@ref)
}
```
mainTemplate.gradle是 Unity 提供的模板文件，详见[[Gradle templates]].
上面这个配置文件做了两件事
1. **声明远程仓库​**​  
    遥控器 SDK（如 `rcsdk-v1.7.9.aar`）可能未发布在 Unity 默认的仓库（如 Google Maven 或 Maven Central）中。需在 `repositories` 块中添加其存储位置（如私有 Maven 仓库或本地路径）。
```gradle
repositories {
    flatDir { dirs 'libs' }  // 本地libs目录
    google()                  // Google仓库
    mavenCentral()            // Maven中央仓库
}
```
2. ​**​添加依赖项​**​  
    通过 `dependencies` 块声明需集成的 SDK AAR 包，例如：
```gradle
dependencies {
    implementation files("libs/rcsdk-v1.7.9.aar")
    implementation files('libs/h16_airlink.aar') // 仅H16设备需要
}
```

## **2. Unity与Android原生代码交互​**​
在 Unity 中使用 C# 调用 Android SDK 时，`AndroidJavaClass` 和 `AndroidJavaObject` 是关键的桥梁工具，其核心作用是通过 ​**​Java Native Interface (JNI)​**​ 实现 C# 与 Android Java 代码的交互。
### ⚙️ ​**​1. 根本原因：语言与运行环境的差异​**​
- ​**​C# 运行于 Mono/.NET 环境​**​：Unity 使用 Mono 或 IL2CPP 作为脚本运行时，与 Android 的 Java 虚拟机（JVM/Dalvik）隔离。
- ​**​Android SDK 基于 Java​**​：系统 API（如摄像头、蓝牙）和第三方 SDK 均以 Java 类库形式提供。
- ​**​解决方案​**​：`AndroidJavaClass` 和 `AndroidJavaObject` 封装了 JNI 调用，使 C# 能动态访问 Java 层的类、对象和方法。
---
### 🔍 ​**​2. 核心类的作用与区别​**​
#### ​**​(1) AndroidJavaClass：访问 Java 静态成员​**​
- ​**​功能​**​：操作 Java 类的​**​静态方法/字段​**​。
- ​**​使用场景​**​：
    - 调用系统工具类（如 `android.util.Log`）。
    - 获取全局单例（如 Unity 的 `UnityPlayer` 类）。
- ​**​示例​**​：调用 Android 的日志功能
```csharp
AndroidJavaClass logClass = new AndroidJavaClass("android.util.Log");
logClass.CallStatic<int>("e", "UnityTag", "Error Message"); // 调用 Log.e()
```[1,6](@ref)
```
#### **(2) `AndroidJavaObject`：操作 Java 对象实例​**​
- ​**​功能​**​：创建 Java 对象实例，并调用其​**​非静态方法/字段​**​。
- ​**​使用场景​**​：
    - 实例化自定义 Java 类。
    - 调用 SDK 中需要对象上下文的方法（如启动 Activity）。
- ​**​示例​**​：启动 Android 浏览器
```csharp
AndroidJavaObject intent = new AndroidJavaObject("android.content.Intent", 
    "android.intent.action.VIEW", 
    new AndroidJavaObject("android.net.Uri").CallStatic<AndroidJavaObject>("parse", "https://example.com")
);
currentActivity.Call("startActivity", intent); // currentActivity 通过 UnityPlayer 获取
```[1,9](@ref)
```

### 3. 示例
- **C#调用Android SDK**
```csharp
public class RemoteControllerManager : MonoBehaviour {
    void ConnectToRC() {
        AndroidJavaClass rcClass = new AndroidJavaClass("com.skydroid.rcsdk.RCSDKManager");
        rcClass.CallStatic("connectToRC");
    }
}
```
- **回调处理​**​，通过 `AndroidJavaProxy` 接收Android回调：
```csharp
class RCCallback : AndroidJavaProxy {
    public RCCallback() : base("com.skydroid.rcsdk.SDKManagerCallBack") {}
    public void onRcConnected() => Debug.Log("遥控器已连接");
}
// 初始化时传入代理
rcClass.CallStatic("initSDK", new RCCallback());
```
## **3. 遥控器核心功能实现​**​
- ​**​摇杆数据读取​**​（100ms轮询）
```csharp
IEnumerator ReadJoystickData() {
    while (true) {
        AndroidJavaObject channelData = KeyManager.CallStatic<AndroidJavaObject>("get", "KeyChannels");
        int[] values = AndroidJNIHelper.ConvertFromJArray<int[]>(channelData.GetRawObject());
        yield return new WaitForSeconds(0.1f); // 严格间隔[1](@ref)
    }
}
```