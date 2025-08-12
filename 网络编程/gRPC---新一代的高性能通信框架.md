---
title: "[[gRPC---新一代的高性能通信框架]]"
type: Permanent
status: done
Creation Date: 2025-08-12 17:43
tags:
---
gRPC (gRPC Remote Procedure Calls) 是由 Google 开发的一个开源、高性能的远程过程调用（RPC）框架。
您可以把它想象成一种**超高效的、跨语言的“函数调用”方式**。客户端可以像调用本地函数一样，直接调用运行在另一台机器（服务器）上的函数，而无需关心底层的网络通信细节。
## gRPC vs. 传统 REST (JSON over [[Http|HTTP]]/1.1)
为了更好地理解，我们把它和最常见的 REST API 做个对比：

|          |                                           |                                  |
| -------- | ----------------------------------------- | -------------------------------- |
| 特性       | gRPC                                      | RESTful API                      |
| **数据格式** | **Protocol Buffers (Protobuf)** - 二进制，小、快 | **JSON** - 文本，人类可读但冗长            |
| **传输协议** | **HTTP/2** - 支持多路复用、头部压缩、服务端推送            | **HTTP/1.1** - 请求-响应模式，有队头阻塞问题   |
| **通信模式** | **支持四种**：一元、服务端流、客户端流、双向流                 | **单一**：请求-响应                     |
| **契约定义** | **强制**。使用 .proto 文件定义服务和消息，强类型            | **可选**。通常使用 OpenAPI/Swagger，但非强制 |
| **代码生成** | **原生支持**。从 .proto 文件自动生成客户端和服务器代码         | 依赖第三方工具                          |
| **性能**   | **极高**，CPU 和网络占用都更低                       | **较低**，JSON解析和HTTP/1.1开销较大       |
## gRPC 的核心三大支柱
1. **服务定义 (Service Definition - .proto 文件)**  
    这是 gRPC 的核心契约。你使用一种名为 **Protocol Buffers** 的接口定义语言（IDL）在一个 .proto 文件中定义你的服务。这包括：
    - service: 定义服务名称，如 GameServer。
    - rpc: 定义可被远程调用的函数，如 GetPlayerData。
    - message: 定义请求和响应的数据结构，如 PlayerRequest 和 PlayerDataResponse。

```Protobuf
// greet.proto
syntax = "proto3";

option csharp_namespace = "GrpcGame"; // 指定生成的C#代码的命名空间

// Greeter 服务定义
service Greeter {
  // SayHello 是一个一元 RPC
  rpc SayHello (HelloRequest) returns (HelloReply);
}

// 请求消息
message HelloRequest {
  string name = 1;
}

// 响应消息
message HelloReply {
  string message = 1;
}
```

2. **代码生成 (Code Generation)**  
    使用 gRPC 的工具链，你可以将这个 .proto 文件自动生成为多种语言（C#, C++, Java, Python, Go...）的客户端“存根”（Stub）和服务端“骨架”（Skeleton）代码。这意味着你无需手动编写任何网络和序列化相关的模板代码。
    
3. **四种通信模式 (Communication Patterns)**
    - **一元 RPC (Unary RPC)**: 客户端发送一个请求，服务器返回一个响应。这是最常见的模式，类似一次普通的函数调用。
    - **服务端流 RPC (Server streaming RPC)**: 客户端发送一个请求，服务器返回一个数据流。适合用于服务器需要持续向客户端推送数据的场景，如游戏内通知、排行榜实时更新。
    - **客户端流 RPC (Client streaming RPC)**: 客户端持续发送一个数据流，服务器处理完毕后返回一个响应。适合用于客户端需要发送大量数据的场景，如上传文件、发送连续的玩家输入遥测数据。
    - **双向流 RPC (Bidirectional streaming RPC)**: 客户端和服务器都可以独立地、双向地发送数据流。这是最强大的模式，非常适合需要实时双向通信的场景，如在线聊天、多人游戏中的状态同步。

## 在 Unity 中使用 gRPC - 完整示例
我们将创建一个简单的“问候”应用：Unity客户端发送一个名字，.NET服务器返回一句问候语。
**核心工作流**：在Unity外部生成代码 -> 将生成的代码和依赖库导入Unity -> 在Unity中编写客户端逻辑。

### 步骤1：定义 .proto 文件并生成代码
>这是在 Unity **外部** 完成的。
1. 创建一个新文件夹，例如 GrpcUnityExample。
2. 在其中创建一个子文件夹 Protos，并将我们上面定义的 greet.proto 文件放进去。
3. 在 GrpcUnityExample 根目录下，创建一个 C# 项目文件 GrpcUnityExample.csproj。这个文件的唯一目的就是用来**触发代码生成**。填入以下内容：
```Xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net6.0</TargetFramework>
  </PropertyGroup>

  <ItemGroup>
    <!-- 核心 gRPC 包引用 -->
    <PackageReference Include="Google.Protobuf" Version="3.21.9" />
    <PackageReference Include="Grpc.Net.Client" Version="2.49.0" />
    <PackageReference Include="Grpc.Tools" Version="2.50.0">
      <IncludeAssets>runtime; build; native; contentfiles; analyzers; buildtransitive</IncludeAssets>
      <PrivateAssets>all</PrivateAssets>
    </PackageReference>
  </ItemGroup>

  <ItemGroup>
    <!-- 告诉 gRPC 工具去处理 Protos 文件夹下的 .proto 文件 -->
    <Protobuf Include="Protos\greet.proto" GrpcServices="Client" />
  </ItemGroup>

</Project>
```

4. **执行代码生成**: 打开终端，导航到 GrpcUnityExample 文件夹，然后运行：
```bash
dotnet build
```
编译成功后，生成的C#文件会出现在 obj/Debug/net6.0/Protos/ 目录下。你会找到 Greet.cs 和 GreetGrpc.cs 这两个文件。

### 步骤2：准备 Unity 项目

1. **导入 gRPC 依赖库**:  
    你需要将 gRPC 运行所需的 DLL 文件放入 Unity。最简单的方式是从 NuGet 下载。你可以使用一个在线的 NuGet 下载网站（如 nuget.org）或命令行工具。你需要以下核心包的 .NET Standard 2.1 版本的 DLL：
    - Google.Protobuf
    - Grpc.Net.Client
    - Grpc.Core.Api
    - System.Buffers
    - System.Memory
    - System.Diagnostics.DiagnosticSource
    - Microsoft.Extensions.Logging.Abstractions  
        将这些 DLL 文件放入 Unity 项目的 Assets/Plugins/Grpc 文件夹中。

2. **导入生成的代码**:  
    将在步骤1中生成的 Greet.cs 和 GreetGrpc.cs 两个文件复制到你的 Unity 项目中，例如 Assets/Scripts/Generated/.
    
### 步骤3：编写 Unity 客户端
创建一个新的 C# 脚本 GrpcClientExample.cs 并挂载到一个场景的游戏对象上。
```csharp
using UnityEngine;
using UnityEngine.UI;
using Grpc.Net.Client;
using GrpcGame; // 这是我们在 .proto 中定义的命名空间
using System.Threading.Tasks;
using Cysharp.Threading.Tasks; // 强烈推荐 UniTask 来处理 Unity 的异步

public class GrpcClientExample : MonoBehaviour
{
    public Button sendButton;
    public InputField nameInput;
    public Text resultText;
    
    private Greeter.GreeterClient _client;
    private GrpcChannel _channel;

    void Start()
    {
        // 服务器地址和端口
        // 注意：在真实项目中，这个地址应该是可配置的
        // 对于安卓真机调试，不能用localhost，要用PC的局域网IP
        var serverAddress = "http://localhost:50051";

        // 创建一个 gRPC 通道
        _channel = GrpcChannel.ForAddress(serverAddress);

        // 使用通道创建一个客户端存根
        _client = new Greeter.GreeterClient(_channel);

        sendButton.onClick.AddListener(() => SayHelloAsync().Forget());
    }

    private async UniTaskVoid SayHelloAsync()
    {
        var playerName = nameInput.text;
        if (string.IsNullOrEmpty(playerName))
        {
            resultText.text = "Please enter a name.";
            return;
        }

        resultText.text = "Sending...";
        try
        {
            var request = new HelloRequest { Name = playerName };
            
            // 像调用本地函数一样调用远程服务！
            var reply = await _client.SayHelloAsync(request);

            // 重要：gRPC调用在后台线程返回，更新UI必须回到主线程
            await UniTask.SwitchToMainThread();
            
            resultText.text = reply.Message;
        }
        catch (System.Exception ex)
        {
            await UniTask.SwitchToMainThread();
            resultText.text = $"Error: {ex.Message}";
        }
    }

    void OnDestroy()
    {
        // 关闭通道释放资源
        _channel?.ShutdownAsync().Wait();
    }
}
```

### 步骤4：创建并运行 gRPC 服务器

gRPC 服务器是一个独立的 .NET 控制台应用，**它不运行在 Unity 中**。
1. 创建一个新的控制台项目 MyGrpcServer。
2. 也添加 Grpc.AspNetCore 包引用。
3. 将 greet.proto 文件也复制到服务器项目中。
4. 编写服务器代码：
    - GreeterService.cs (服务逻辑实现)
```csharp
using Grpc.Core;
using GrpcGame;

public class GreeterService : Greeter.GreeterBase
{
    public override Task<HelloReply> SayHello(HelloRequest request, ServerCallContext context)
    {
        return Task.FromResult(new HelloReply
        {
            Message = $"你好, {request.Name}! 这里是 gRPC 服务器。"
        });
    }
}
```
Program.cs (启动服务器)
```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddGrpc();
var app = builder.Build();
app.MapGrpcService<GreeterService>();
app.Run();
```
5. **先运行服务器，再运行 Unity 客户端**。点击 Unity 中的按钮，你就能看到从服务器返回的问候语了！
    

### 关键注意事项
- **线程安全**: gRPC 的响应默认在后台线程上返回。任何与 Unity API（如修改 GameObject、更新UI）的交互都必须切换回主线程。UniTask.SwitchToMainThread() 是解决这个问题的完美工具。
- **WebGL 平台**: 标准的 gRPC over HTTP/2 在浏览器中无法工作。你需要使用 **gRPC-Web**。Grpc.Net.Client.Web 包可以帮助你配置客户端以支持 gRPC-Web，但服务器也需要进行相应的配置。
- **移动平台**: 在 iOS 和 Android 上，gRPC 可以正常工作。注意服务器地址不能使用 localhost，而应使用 PC 在局域网中的IP地址。