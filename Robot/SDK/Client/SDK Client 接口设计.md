---
title: "[[SDK Client 接口设计]]"
type: Permanent
status: ing
Creation Date: 2026-06-11 17:02
tags:
---
## Client 架构框图

![[Pasted image 20260611193145.png]]

## C# SDK Client 接口框架

<svg width="100%" viewBox="0 0 680 1910" xmlns="http://www.w3.org/2000/svg"
  style="font-family:'Segoe UI',sans-serif;background:#F5F7FA;border-radius:12px;padding:8px">
<defs>
  <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M2 1L8 5L2 9" fill="none" stroke="#5C6BC0" stroke-width="1.5"/>
  </marker>
</defs>

<!-- ① Unity Application Layer -->
<rect x="30" y="16" width="620" height="136" rx="12" fill="#DDEEFF" stroke="#7AAAD8" stroke-width="1"/>
<text x="340" y="40" text-anchor="middle" font-size="13" font-weight="bold" fill="#1A3A5C">① Unity Application Layer</text>
<rect x="48"  y="52" width="134" height="36" rx="6" fill="#fff" stroke="#7AAAD8" stroke-width="0.8"/><text x="115"  y="74" text-anchor="middle" font-size="10" fill="#1A3A5C">DaystarBotSDKSample</text>
<rect x="196" y="52" width="122" height="36" rx="6" fill="#fff" stroke="#7AAAD8" stroke-width="0.8"/><text x="257"  y="74" text-anchor="middle" font-size="10" fill="#1A3A5C">RobotSDKSample (IS)</text>
<rect x="332" y="52" width="144" height="36" rx="6" fill="#fff" stroke="#7AAAD8" stroke-width="0.8"/><text x="404"  y="74" text-anchor="middle" font-size="10" fill="#1A3A5C">MC_RobotSDKSample (MC)</text>
<rect x="490" y="52" width="140" height="36" rx="6" fill="#fff" stroke="#7AAAD8" stroke-width="0.8"/><text x="560"  y="74" text-anchor="middle" font-size="10" fill="#1A3A5C">PerceptionSDKSample</text>
<text x="340" y="118" text-anchor="middle" font-size="10" fill="#5577AA">Unity 应用层 · 调用 SDK 的示例脚本入口</text>
<line x1="340" y1="152" x2="340" y2="180" stroke="#5C6BC0" stroke-width="1.2" marker-end="url(#arr)" opacity="0.4"/>

<!-- ② SDK.API Layer -->
<rect x="30" y="190" width="620" height="278" rx="12" fill="#EDE7F6" stroke="#9575CD" stroke-width="1"/>
<text x="340" y="215" text-anchor="middle" font-size="13" font-weight="bold" fill="#311B92">② SDK.API Layer — Public Interface</text>
<text x="48" y="236" font-size="10" fill="#7E57C2">Entry points</text>
<rect x="48"  y="244" width="168" height="36" rx="6" fill="#fff" stroke="#9575CD" stroke-width="0.8"/><text x="132" y="266" text-anchor="middle" font-size="10" fill="#311B92">RobotSDKManager (Singleton)</text>
<rect x="230" y="244" width="128" height="36" rx="6" fill="#fff" stroke="#9575CD" stroke-width="0.8"/><text x="294" y="266" text-anchor="middle" font-size="10" fill="#311B92">RobotSportClient</text>
<rect x="372" y="244" width="148" height="36" rx="6" fill="#fff" stroke="#9575CD" stroke-width="0.8"/><text x="446" y="266" text-anchor="middle" font-size="10" fill="#311B92">RobotMutiMediaClient</text>
<rect x="534" y="244" width="96" height="36" rx="6" fill="#fff" stroke="#9575CD" stroke-width="0.8"/><text x="582" y="266" text-anchor="middle" font-size="10" fill="#311B92">StateListener</text>
<text x="48" y="300" font-size="10" fill="#7E57C2">Data model</text>
<rect x="48" y="308" width="112" height="36" rx="6" fill="#fff" stroke="#9575CD" stroke-width="0.8"/><text x="104" y="330" text-anchor="middle" font-size="10" fill="#311B92">MotionState</text>
<text x="48" y="362" font-size="10" fill="#7E57C2">Event listeners</text>
<rect x="48"  y="370" width="178" height="36" rx="6" fill="#fff" stroke="#9575CD" stroke-width="0.8"/><text x="137" y="392" text-anchor="middle" font-size="10" fill="#311B92">IConnectionStateListener</text>
<rect x="242" y="370" width="156" height="36" rx="6" fill="#fff" stroke="#9575CD" stroke-width="0.8"/><text x="320" y="392" text-anchor="middle" font-size="10" fill="#311B92">IEnableStateListener</text>
<rect x="414" y="370" width="156" height="36" rx="6" fill="#fff" stroke="#9575CD" stroke-width="0.8"/><text x="492" y="392" text-anchor="middle" font-size="10" fill="#311B92">IMotionStateListener</text>
<line x1="340" y1="468" x2="340" y2="496" stroke="#5C6BC0" stroke-width="1.2" marker-end="url(#arr)" opacity="0.4"/>

<!-- ③ SDK.Core Layer -->
<rect x="30" y="506" width="620" height="380" rx="12" fill="#E8F5E9" stroke="#66BB6A" stroke-width="1"/>
<text x="340" y="530" text-anchor="middle" font-size="13" font-weight="bold" fill="#1B5E20">③ SDK.Core Layer — Business Logic</text>

<!-- 三列标题 -->
<line x1="248" y1="538" x2="248" y2="876" stroke="#66BB6A" stroke-width="0.6" stroke-dasharray="4,3"/>
<line x1="452" y1="538" x2="452" y2="876" stroke="#66BB6A" stroke-width="0.6" stroke-dasharray="4,3"/>
<text x="139" y="550" text-anchor="middle" font-size="11" font-weight="bold" fill="#388E3C">Common</text>
<text x="350" y="550" text-anchor="middle" font-size="11" font-weight="bold" fill="#388E3C">Motion</text>
<text x="556" y="550" text-anchor="middle" font-size="11" font-weight="bold" fill="#388E3C">Interfaces</text>

<!-- Common 列 · Types -->
<rect x="40" y="558" width="200" height="118" rx="6" fill="#fff" stroke="#66BB6A" stroke-width="0.8"/>
<text x="140" y="574" text-anchor="middle" font-size="10" font-weight="bold" fill="#1B5E20">Types:</text>
<text x="52" y="590" font-size="9" fill="#388E3C">• RobotType (IS/MC)</text>
<text x="52" y="604" font-size="9" fill="#388E3C">• RobotPostureType</text>
<text x="52" y="618" font-size="9" fill="#388E3C">• RobotSceneType</text>
<text x="52" y="632" font-size="9" fill="#388E3C">• BionicActionType</text>
<text x="52" y="646" font-size="9" fill="#388E3C">• LightEmojiStyles</text>



<!-- Common 列 · States -->
<rect x="40" y="686" width="200" height="100" rx="6" fill="#fff" stroke="#66BB6A" stroke-width="0.8"/>
<text x="52" y="700" font-size="10" font-weight="bold" fill="#1B5E20">States:</text>
<text x="52" y="715" font-size="9" fill="#388E3C">• ConnectionState</text>
<text x="52" y="729" font-size="9" fill="#388E3C">• RobotEnableState</text>
<text x="52" y="743" font-size="9" fill="#388E3C">• RobotChargeState</text>
<text x="52" y="757" font-size="9" fill="#388E3C">• JointCalibrationState</text>
<text x="52" y="771" font-size="9" fill="#388E3C">• RobotSceneSwitchState</text>

<!-- Motion 列 · HighLevelSport -->
<rect x="258" y="558" width="186" height="48" rx="6" fill="#fff" stroke="#66BB6A" stroke-width="0.8"/>
<text x="351" y="576" text-anchor="middle" font-size="10" font-weight="bold" fill="#1B5E20">HighLevelSport:</text>
<text x="268" y="596" font-size="9" fill="#388E3C">• RobotSportService</text>

<!-- Motion 列 · Interfaces -->
<rect x="258" y="616" width="186" height="82" rx="6" fill="#fff" stroke="#66BB6A" stroke-width="0.8"/>
<text x="268" y="632" font-size="10" font-weight="bold" fill="#1B5E20">Interfaces:</text>
<text x="268" y="648" font-size="9" fill="#388E3C">• IRobotSportService</text>
<text x="268" y="662" font-size="9" fill="#388E3C">• IBasicSystemStateListener</text>
<text x="268" y="676" font-size="9" fill="#388E3C">• IMotionConnectStateListener</text>
<text x="268" y="690" font-size="9" fill="#388E3C">• IPerceptionConnectState...</text>

<!-- Motion 列 · StateMachines -->
<rect x="258" y="708" width="186" height="56" rx="6" fill="#fff" stroke="#66BB6A" stroke-width="0.8"/>
<text x="268" y="724" font-size="10" font-weight="bold" fill="#1B5E20">StateMachines:</text>
<text x="268" y="740" font-size="9" fill="#388E3C">• BasicSystemStateMachine</text>
<text x="268" y="754" font-size="9" fill="#388E3C">• SportStateMachine</text>

<!-- Interfaces 列 · IOTAUpgradeStatusListener -->
<rect x="462" y="558" width="178" height="56" rx="6" fill="#fff" stroke="#66BB6A" stroke-width="0.8"/>
<text x="551" y="576" text-anchor="middle" font-size="10" font-weight="bold" fill="#1B5E20">IOTAUpgradeStatus</text>
<text x="551" y="596" text-anchor="middle" font-size="10" fill="#1B5E20">Listener</text>

<line x1="340" y1="886" x2="340" y2="914" stroke="#5C6BC0" stroke-width="1.2" marker-end="url(#arr)" opacity="0.4"/>

<!-- ④ SDK.Protocol Layer -->
<rect x="30" y="924" width="620" height="510" rx="12" fill="#FFF8E1" stroke="#FFB300" stroke-width="1"/>
<text x="340" y="948" text-anchor="middle" font-size="13" font-weight="bold" fill="#3E2723">④ SDK.Protocol Layer — Communication</text>

<!-- 上半区竖分隔: Common &amp; Adapters | Interfaces -->
<line x1="340" y1="956" x2="340" y2="1072" stroke="#FFB300" stroke-width="0.6" stroke-dasharray="4,3"/>
<text x="185" y="970" text-anchor="middle" font-size="11" font-weight="bold" fill="#795548">Common &amp; Adapters</text>
<text x="495" y="970" text-anchor="middle" font-size="11" font-weight="bold" fill="#795548">Interfaces</text>
<line x1="42" y1="975" x2="638" y2="975" stroke="#FFB300" stroke-width="0.5"/>

<!-- Common sub -->
<text x="52" y="989" font-size="9" font-weight="bold" fill="#3E2723">Common:</text>
<rect x="42" y="994" width="128" height="50" rx="4" fill="#fff" stroke="#FFB300" stroke-width="0.6"/>
<text x="52" y="1008" font-size="9" fill="#795548">• ProtocolManager</text>
<text x="52" y="1022" font-size="9" fill="#795548">• SDKConfigManager</text>

<!-- Adapters sub -->
<text x="182" y="989" font-size="9" font-weight="bold" fill="#3E2723">Adapters:</text>
<rect x="178" y="994" width="154" height="68" rx="4" fill="#fff" stroke="#FFB300" stroke-width="0.6"/>
<text x="188" y="1008" font-size="9" fill="#795548">• IRobotAdapter</text>
<text x="188" y="1022" font-size="9" fill="#795548">• QuadrupedAdapter (IS)</text>
<text x="188" y="1036" font-size="9" fill="#795548">• HexapodAdapter (MC)</text>
<text x="188" y="1050" font-size="9" fill="#795548">• HexapodMoveCommand</text>

<!-- Interfaces sub -->
<rect x="348" y="980" width="284" height="56" rx="4" fill="#fff" stroke="#FFB300" stroke-width="0.6"/>
<text x="358" y="994" font-size="9" fill="#795548">• IMotionProtocolEngine</text>
<text x="358" y="1008" font-size="9" fill="#795548">• IPerceptionProtocolEngine</text>
<text x="358" y="1022" font-size="9" fill="#795548">• IAdaptedCommand</text>

<!-- Dual Protocol System banner -->
<rect x="42" y="1076" width="596" height="22" rx="4" fill="#FFE082" stroke="#FFB300" stroke-width="0.6"/>
<text x="340" y="1091" text-anchor="middle" font-size="11" font-weight="bold" fill="#5D4037">Dual Protocol System</text>

<!-- SYSA + SYSB outer box -->
<rect x="42" y="1104" width="596" height="316" rx="6" fill="#FFF3C4" stroke="#FFB300" stroke-width="0.8"/>
<line x1="340" y1="1104" x2="340" y2="1420" stroke="#FFB300" stroke-width="0.6" stroke-dasharray="4,3"/>

<!-- SYSA header -->
<text x="191" y="1120" text-anchor="middle" font-size="11" font-weight="bold" fill="#5D4037">SYSA (gRPC System)</text>
<line x1="42" y1="1126" x2="338" y2="1126" stroke="#FFB300" stroke-width="0.5"/>

<!-- SYSA GRPC Engine -->
<text x="52" y="1140" font-size="9" font-weight="bold" fill="#3E2723">GRPC Engine:</text>
<text x="52" y="1153" font-size="9" fill="#795548">• GrpcEngine.cs</text>
<text x="52" y="1165" font-size="9" fill="#795548">• SDKProtocolManager.cs</text>

<!-- SYSA Proto Generated Services -->
<text x="52" y="1181" font-size="9" font-weight="bold" fill="#3E2723">Proto Generated Services:</text>
<text x="52" y="1194" font-size="9" fill="#795548">• RobotService + RobotServiceGrpc</text>
<text x="52" y="1206" font-size="9" fill="#795548">• McsService (Motion Control)</text>
<text x="52" y="1218" font-size="9" fill="#795548">• RpsService (Robot Positioning)</text>
<text x="52" y="1230" font-size="9" fill="#795548">• OtaService (OTA Updates)</text>
<text x="52" y="1242" font-size="9" fill="#795548">• LogService (Logging)</text>
<text x="52" y="1254" font-size="9" fill="#795548">• SnmpService (Network Management)</text>
<text x="52" y="1266" font-size="9" fill="#795548">• CommonTypes</text>

<!-- SYSA Use Cases -->
<text x="52" y="1282" font-size="9" font-weight="bold" fill="#3E2723">Use Cases:</text>
<text x="52" y="1295" font-size="9" fill="#795548">• Robot Motion Control</text>
<text x="52" y="1307" font-size="9" fill="#795548">• System Management</text>
<text x="52" y="1319" font-size="9" fill="#795548">• OTA Firmware Updates</text>
<text x="52" y="1331" font-size="9" fill="#795548">• Network Monitoring</text>
<text x="52" y="1343" font-size="9" fill="#795548">• Log Collection</text>

<!-- SYSB header -->
<text x="491" y="1120" text-anchor="middle" font-size="11" font-weight="bold" fill="#5D4037">SYSB (WebSocket System)</text>
<line x1="342" y1="1126" x2="638" y2="1126" stroke="#FFB300" stroke-width="0.5"/>

<!-- SYSB WebSocket Engine -->
<text x="350" y="1140" font-size="9" font-weight="bold" fill="#3E2723">WebSocket Engine:</text>
<text x="350" y="1153" font-size="9" fill="#795548">• WebSocketEngine.cs (Singleton)</text>
<text x="350" y="1165" font-size="9" fill="#795548">• WebSocketClient.cs</text>

<!-- SYSB Use Cases -->
<text x="350" y="1181" font-size="9" font-weight="bold" fill="#3E2723">Use Cases:</text>
<text x="350" y="1194" font-size="9" fill="#795548">• PTZ Control (Camera)</text>
<text x="350" y="1206" font-size="9" fill="#795548">• Real-time Perception Data</text>
<text x="350" y="1218" font-size="9" fill="#795548">• Live Video Streaming</text>
<text x="350" y="1230" font-size="9" fill="#795548">• Real-time Status Updates</text>

<line x1="340" y1="1434" x2="340" y2="1462" stroke="#5C6BC0" stroke-width="1.2" marker-end="url(#arr)" opacity="0.4"/>

<!-- ⑤ SDK.Utilities Layer -->
<rect x="30" y="1472" width="620" height="134" rx="12" fill="#FBE9E7" stroke="#FF7043" stroke-width="1"/>
<text x="340" y="1496" text-anchor="middle" font-size="13" font-weight="bold" fill="#BF360C">⑤ SDK.Utilities Layer — Tools &amp; Config</text>
<rect x="48"  y="1508" width="176" height="48" rx="6" fill="#fff" stroke="#FF7043" stroke-width="0.8"/>
<text x="136" y="1527" text-anchor="middle" font-size="11" font-weight="bold" fill="#BF360C">LocalConfigParser</text>
<text x="136" y="1545" text-anchor="middle" font-size="10" fill="#E64A19">Configuration management</text>
<rect x="242" y="1508" width="196" height="48" rx="6" fill="#fff" stroke="#FF7043" stroke-width="0.8"/>
<text x="340" y="1527" text-anchor="middle" font-size="11" font-weight="bold" fill="#BF360C">SDKConnectionManager</text>
<text x="340" y="1545" text-anchor="middle" font-size="10" fill="#E64A19">Connection lifecycle</text>
<rect x="456" y="1508" width="144" height="48" rx="6" fill="#fff" stroke="#FF7043" stroke-width="0.8"/>
<text x="528" y="1527" text-anchor="middle" font-size="11" font-weight="bold" fill="#BF360C">SDKLogger</text>
<text x="528" y="1545" text-anchor="middle" font-size="10" fill="#E64A19">Unified logging</text>
<line x1="340" y1="1606" x2="340" y2="1634" stroke="#5C6BC0" stroke-width="1.2" marker-end="url(#arr)" opacity="0.4"/>

<!-- ⑥ SDK.Dependency Layer -->
<rect x="30" y="1644" width="620" height="138" rx="12" fill="#F3E5F5" stroke="#AB47BC" stroke-width="1"/>
<text x="340" y="1668" text-anchor="middle" font-size="13" font-weight="bold" fill="#4A148C">⑥ SDK.Dependency Layer — Third-party Libraries</text>
<rect x="48"  y="1680" width="138" height="48" rx="6" fill="#fff" stroke="#AB47BC" stroke-width="0.8"/>
<text x="117" y="1699" text-anchor="middle" font-size="11" font-weight="bold" fill="#4A148C">Google.Protobuf</text>
<text x="117" y="1717" text-anchor="middle" font-size="10" fill="#7B1FA2">Protobuf serialization</text>
<rect x="202" y="1680" width="112" height="48" rx="6" fill="#fff" stroke="#AB47BC" stroke-width="0.8"/>
<text x="258" y="1699" text-anchor="middle" font-size="11" font-weight="bold" fill="#4A148C">Grpc.Core</text>
<text x="258" y="1717" text-anchor="middle" font-size="10" fill="#7B1FA2">Runtime &amp; libs</text>
<rect x="330" y="1680" width="150" height="48" rx="6" fill="#fff" stroke="#AB47BC" stroke-width="0.8"/>
<text x="405" y="1699" text-anchor="middle" font-size="11" font-weight="bold" fill="#4A148C">Grpc.Core/runtimes</text>
<text x="405" y="1717" text-anchor="middle" font-size="10" fill="#7B1FA2">Platform-specific</text>
<rect x="496" y="1680" width="124" height="48" rx="6" fill="#fff" stroke="#AB47BC" stroke-width="0.8"/>
<text x="558" y="1699" text-anchor="middle" font-size="11" font-weight="bold" fill="#4A148C">Grpc.Core.Api</text>
<text x="558" y="1717" text-anchor="middle" font-size="10" fill="#7B1FA2">API definitions</text>
<text x="340" y="1758" text-anchor="middle" font-size="10" fill="#9C27B0">Protocol Buffers 序列化 · gRPC 运行时 · 平台原生库 · API 定义</text>
</svg>

## C# SDK Client接口目录结构：
```
📁 Runtime/
├── 📄 Company.Daystar.Runtime.asmdef          # Assembly Definition文件
│
├── 📁 SDK.API/                                # 🔵 公共API接口层
│   ├── 📄 IConnectionStateListener.cs         # 连接状态监听接口
│   ├── 📄 IEnableStateListener.cs             # 使能状态监听接口
│   ├── 📄 IMotionStateListener.cs             # 运动状态监听接口
│   ├── 📄 MotionState.cs                      # 运动状态数据模型
│   ├── 📄 RobotMutiMediaClient.cs             # 多媒体客户端(PTZ控制等)
│   ├── 📄 RobotSDKManager.cs                  # SDK管理器(单例入口)
│   ├── 📄 RobotSportClient.cs                 # 运动控制客户端
│   └── 📄 RobotStateListener.cs               # 状态监听器
│
├── 📁 SDK.Core/                               # 🔵 核心业务逻辑层
│   ├── 📁 Common/                             # 通用组件
│   │   ├── 📁 Interfaces/                     # 通用接口定义
│   │   │   └── 📄 IOTAUpgradeStatusListener.cs # OTA升级状态监听接口
│   │   ├── 📁 States/                         # 状态管理
│   │   │   ├── 📄 ConnectionState.cs          # 连接状态枚举
│   │   │   ├── 📄 JointCalibrationState.cs    # 关节校准状态
│   │   │   ├── 📄 RobotChargeState.cs         # 机器人充电状态
│   │   │   ├── 📄 RobotEnableState.cs         # 机器人使能状态
│   │   │   └── 📄 RobotSceneSwitchState.cs    # 场景切换状态
│   │   └── 📁 Types/                          # 类型定义
│   │       ├── 📄 BionicActionType.cs         # 仿生动作类型(跳跃、前空翻等)
│   │       ├── 📄 CommandType.cs              # 命令类型
│   │       ├── 📄 ControlType.cs              # 控制类型(遥控器/导航模式)
│   │       ├── 📄 LightEmojiStyles.cs         # 光效表情样式
│   │       ├── 📄 ProtocolType.cs             # 协议类型
│   │       ├── 📄 RobotPostureType.cs         # 机器人姿态类型(站立/趴下)
│   │       ├── 📄 RobotSceneType.cs           # 机器人场景类型(步行/楼梯/斜坡)
│   │       ├── 📄 RobotType.cs                # 机器人类型(IS四足/MC人形)
│   │       └── 📄 ServiceType.cs              # 服务类型
│   └── 📁 Motion/                             # 运动控制模块
│       ├── 📁 HighLevelSport/                 # 高级运动控制
│       │   └── 📄 RobotSportService.cs        # 机器人运动服务实现
│       ├── 📁 Interfaces/                     # 运动接口
│       │   ├── 📄 IBasicSystemStateListener.cs      # 基础系统状态监听接口
│       │   ├── 📄 IMotionConnectStateListener.cs    # 运动连接状态监听接口
│       │   ├── 📄 IPerceptionConnectStateListener.cs # 感知连接状态监听接口
│       │   └── 📄 IRobotSportService.cs              # 机器人运动服务接口
│       └── 📁 StateMachines/                  # 状态机
│           ├── 📄 BasicSystemStateMachine.cs  # 基础系统状态机
│           └── 📄 SportStateMachine.cs        # 运动状态机
│
├── 📁 SDK.Protocol/                           # 🔵 通信协议层
│   ├── 📁 Adapters/                           # 协议适配器 - 不同机器人类型的适配
│   │   ├── 📄 HexapodAdapter.cs              # 六足机器人适配器
│   │   ├── 📄 HexapodMoveCommand.cs          # 六足移动命令
│   │   ├── 📄 IRobotAdapter.cs               # 机器人适配器接口
│   │   └── 📄 QuadrupedAdapter.cs            # 四足机器人适配器
│   ├── 📁 Common/                             # 通用协议组件
│   │   ├── 📄 ProtocolManager.cs             # 协议管理器
│   │   └── 📄 SDKConfigManger.cs             # SDK配置管理器
│   ├── 📁 Interfaces/                         # 协议接口
│   │   ├── 📄 IAdaptedCommand.cs             # 适配命令接口
│   │   ├── 📄 IMotionProtocolEngine.cs       # 运动协议引擎接口
│   │   └── 📄 IPerceptionProtocolEngine.cs   # 感知协议引擎接口
│   ├── 📁 SYSA/                               # 🟠 系统A协议 - gRPC通信
│   │   └── 📁 Engines/                        # 引擎层
│   │       └── 📁 GRPC/                       # gRPC引擎
│   │           ├── 📄 GrpcEngine.cs           # gRPC引擎实现
│   │           ├── 📄 SDKProtocolManager.cs   # SDK协议管理器
│   │           └── 📁 ProtoGenerate/          # Protocol Buffers生成的代码
│   │               ├── 📄 CommonTypes.cs      # 通用类型定义
│   │               ├── 📄 LogService.cs       # 日志服务
│   │               ├── 📄 McsService.cs       # MCS服务(Motion Control Service)
│   │               ├── 📄 OtaService.cs       # OTA升级服务
│   │               ├── 📄 RobotService.cs     # 机器人服务
│   │               ├── 📄 RobotServiceGrpc.cs # 机器人服务gRPC客户端
│   │               ├── 📄 RpsService.cs       # RPS服务(Robot Positioning Service)
│   │               └── 📄 SnmpService.cs      # SNMP服务
│   └── 📁 SYSB/                               # 🟠 系统B协议 - WebSocket通信
│       ├── 📁 Engines/                        # 引擎层
│       │   └── 📁 WebSocket/                  # WebSocket引擎
│       │       ├── 📄 README.md               # WebSocket使用说明
│       │       ├── 📄 WebSocketClient.cs      # WebSocket客户端(连接管理)
│       │       └── 📄 WebSocketEngine.cs      # WebSocket引擎(单例,业务逻辑)
│       └── 📁 Examples/                       # 示例代码
│           └── 📄 WebSocketExample.cs         # WebSocket使用示例
│
├── 📁 SDK.Utilities/                          # 🔵 工具类层
│   ├── 📄 LocalConfigParser.cs               # 本地配置文件解析器
│   ├── 📄 SDKConnectionManager.cs            # SDK连接管理器
│   └── 📄 SDKLogger.cs                       # 统一日志系统
│
└── 📁 SDK.Dependency/                         # 🔵 第三方依赖层
    ├── 📁 Google.Protobuf/                    # Google Protocol Buffers
    │   └── 📁 lib/                            # Protocol Buffers库文件
    ├── 📁 Grpc.Core/                          # gRPC核心库
    │   ├── 📁 lib/                            # gRPC库文件
    │   └── 📁 runtimes/                       # 运行时库
    └── 📁 Grpc.Core.Api/                      # gRPC API库
```


## 接口设计思想
**分层架构设计**
1. API层(SDK.API): 对外暴露的公共接口
2. 核心层(SDK.Core): 业务逻辑和数据模型
3. 协议层(SDK.Protocol): 通信协议实现
4. 工具层(SDK.Utilities): 通用工具和配置
5. 依赖层(SDK.Dependency): 第三方库

 **核心组件**
6. WebSocket引擎: 感知主机通信方式
7. gRPC协议: 运动控制主机通信方式
8. 状态管理: 完整的机器人状态监听体系
9. 多客户端模块架构: 分离运动控制和多媒体控制

**支持的机器人类型**
1. IS型机器人: 足式机器人
2. MC型机器人: 轮式机器人
3. 适配器模式: 通过HexapodAdapter和QuadrupedAdapter支持不同机器人

**设计模式应用**
1. 单例模式: SDKManager, WebSocketEngine
2. 工厂模式：根据机器人类型创建不同的适配器、不同模块客户端
3. 适配器模式: 不同机器人类型的协议适配
4. 观察者模式: 状态监听和事件回调
5. 状态机模式: 运动和系统状态管理

## SDK Client 和SYSB SDK Server 通信

<svg width="100%" viewBox="0 0 760 1480" role="img" xmlns="http://www.w3.org/2000/svg">
<title>WebSocket 连接通信整体框架</title>
<desc>三层架构：应用层 WebSocketEngine、传输层 WebSocketClient、网络层 ClientWebSocket</desc>
<defs>
  <marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M1 2L8 5L1 8" fill="none" stroke="context-stroke" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
</defs>

<text x="380" y="28" text-anchor="middle"
  style="font:700 15px/1 'Consolas',monospace;fill:#26215C;letter-spacing:.5px">
  WebSocket 连接通信整体框架
</text>

<rect x="20" y="42" width="720" height="812" rx="12"
  fill="#EEEDFE" stroke="#7F77DD" stroke-width="1.2" stroke-dasharray="7 3"/>
<text x="380" y="64" text-anchor="middle"
  style="font:500 13px 'Consolas',monospace;fill:#534AB7">
  应用层 (Application Layer)
</text>

<rect x="36" y="74" width="688" height="770" rx="8"
  fill="#dce9f7" stroke="#378ADD" stroke-width="1" stroke-dasharray="5 3"/>
<text x="380" y="96" text-anchor="middle"
  style="font:700 13px 'Consolas',monospace;fill:#0C447C">
  WebSocketEngine
</text>

<rect x="52" y="106" width="196" height="150" rx="7"
  fill="#FAEEDA" stroke="#EF9F27" stroke-width="1" stroke-dasharray="4 2"/>
<text x="150" y="126" text-anchor="middle"
  style="font:600 12px 'Consolas',monospace;fill:#633806">业务接口</text>
<text x="68" y="146" style="font:400 11px 'Consolas',monospace;fill:#854F0B">• CallService()</text>
<text x="68" y="163" style="font:400 11px 'Consolas',monospace;fill:#854F0B">• NavigateTo()</text>
<text x="68" y="180" style="font:400 11px 'Consolas',monospace;fill:#854F0B">• SetPtzPosition</text>
<text x="68" y="197" style="font:400 11px 'Consolas',monospace;fill:#854F0B">• SubscribeTopic</text>
<text x="68" y="214" style="font:400 11px 'Consolas',monospace;fill:#854F0B">• ...</text>
<text x="150" y="244" text-anchor="middle"
  style="font:400 10.5px 'Consolas',monospace;fill:#BA7517">（业务调用入口）</text>

<rect x="270" y="106" width="220" height="150" rx="7"
  fill="#E1F5EE" stroke="#1D9E75" stroke-width="1" stroke-dasharray="4 2"/>
<text x="380" y="126" text-anchor="middle"
  style="font:600 12px 'Consolas',monospace;fill:#085041">心跳管理</text>
<text x="286" y="146" style="font:400 11px 'Consolas',monospace;fill:#0F6E56">• StartHeartbeat</text>
<text x="286" y="163" style="font:400 11px 'Consolas',monospace;fill:#0F6E56">• StopHeartbeat</text>
<text x="286" y="180" style="font:400 11px 'Consolas',monospace;fill:#0F6E56">• SendPing()</text>
<text x="286" y="197" style="font:400 11px 'Consolas',monospace;fill:#0F6E56">• OnHeartbeatTimer</text>
<text x="380" y="244" text-anchor="middle"
  style="font:400 10.5px 'Consolas',monospace;fill:#1D9E75">（Ping/Pong 心跳）</text>

<rect x="512" y="106" width="196" height="150" rx="7"
  fill="#FBEAF0" stroke="#D4537E" stroke-width="1" stroke-dasharray="4 2"/>
<text x="610" y="126" text-anchor="middle"
  style="font:600 12px 'Consolas',monospace;fill:#72243E">消息处理</text>
<text x="528" y="146" style="font:400 11px 'Consolas',monospace;fill:#993556">• HandlePing()</text>
<text x="528" y="163" style="font:400 11px 'Consolas',monospace;fill:#993556">• HandlePong()</text>
<text x="528" y="180" style="font:400 11px 'Consolas',monospace;fill:#993556">• HandlePublish()</text>
<text x="528" y="197" style="font:400 11px 'Consolas',monospace;fill:#993556">• HandleServiceResp</text>
<text x="528" y="214" style="font:400 11px 'Consolas',monospace;fill:#993556">• ...</text>

<line x1="380" y1="258" x2="380" y2="280"
  stroke="#BA7517" stroke-width="1.5" marker-end="url(#ar)"/>
<text x="396" y="274"
  style="font:400 11px 'Consolas',monospace;fill:#854F0B">超时检测</text>

<rect x="170" y="284" width="420" height="54" rx="7"
  fill="#FAECE7" stroke="#D85A30" stroke-width="1.2"/>
<text x="380" y="307" text-anchor="middle"
  style="font:500 12px 'Consolas',monospace;fill:#712B13">_lastPongReceived 超时？</text>
<text x="380" y="326" text-anchor="middle"
  style="font:400 11px 'Consolas',monospace;fill:#993C1D">（超过 N 个心跳间隔未收到）</text>

<line x1="380" y1="338" x2="380" y2="360"
  stroke="#0F6E56" stroke-width="1.5" marker-end="url(#ar)"/>
<text x="390" y="354"
  style="font:400 11px 'Consolas',monospace;fill:#085041">是</text>

<rect x="170" y="364" width="420" height="40" rx="7"
  fill="#E1F5EE" stroke="#0F6E56" stroke-width="1.2"/>
<text x="380" y="389" text-anchor="middle"
  style="font:500 12px 'Consolas',monospace;fill:#085041">
  webSocketClient.TriggerReconnect()
</text>

<rect x="52" y="420" width="652" height="202" rx="7"
  fill="#F1EFE8" stroke="#888780" stroke-width="1" stroke-dasharray="4 2"/>
<text x="72" y="441"
  style="font:600 12px 'Consolas',monospace;fill:#444441">事件回调</text>

<text x="72" y="468"
  style="font:500 12px 'Consolas',monospace;fill:#185FA5">OnConnectionRestored</text>
<line x1="248" y1="464" x2="298" y2="464"
  stroke="#1D9E75" stroke-width="1.5" marker-end="url(#ar)"/>
<text x="306" y="456"
  style="font:600 11.5px 'Consolas',monospace;fill:#085041">OnWebSocketConnected()</text>
<text x="306" y="472"
  style="font:400 11px 'Consolas',monospace;fill:#0F6E56">• AdvertisePtzTopic()</text>
<text x="306" y="488"
  style="font:400 11px 'Consolas',monospace;fill:#0F6E56">• StartHeartbeat()</text>
<text x="450" y="488"
  style="font:400 10px 'Consolas',monospace;fill:#BA7517">← 重连后重启</text>
<text x="306" y="504"
  style="font:400 11px 'Consolas',monospace;fill:#0F6E56">• 通知上层连接恢复</text>

<line x1="68" y1="518" x2="688" y2="518"
  stroke="#C4C2B8" stroke-width="0.6"/>

<text x="72" y="542"
  style="font:500 12px 'Consolas',monospace;fill:#A32D2D">OnConnectionLost</text>
<line x1="218" y1="538" x2="298" y2="538"
  stroke="#E24B4A" stroke-width="1.5" marker-end="url(#ar)"/>
<text x="306" y="530"
  style="font:600 11.5px 'Consolas',monospace;fill:#791F1F">OnWebSocketDisconnected()</text>
<text x="306" y="546"
  style="font:400 11px 'Consolas',monospace;fill:#A32D2D">• StopHeartbeat()</text>
<text x="306" y="562"
  style="font:400 11px 'Consolas',monospace;fill:#A32D2D">• 通知上层连接丢失</text>
<text x="306" y="609"
  style="font:400 10.5px 'Consolas',monospace;fill:#888780">（箭头颜色与目标模块一致）</text>

<rect x="52" y="636" width="652" height="28" rx="5"
  fill="#E8E6FC" stroke="#7F77DD" stroke-width="0.6"/>
<text x="68" y="654"
  style="font:400 10.5px 'Consolas',monospace;fill:#444441">颜色说明：</text>
<rect x="142" y="641" width="11" height="11" rx="2" fill="#FAEEDA" stroke="#EF9F27" stroke-width="0.6"/>
<text x="157" y="653" style="font:400 10.5px 'Consolas',monospace;fill:#444441">业务接口</text>
<rect x="228" y="641" width="11" height="11" rx="2" fill="#E1F5EE" stroke="#1D9E75" stroke-width="0.6"/>
<text x="243" y="653" style="font:400 10.5px 'Consolas',monospace;fill:#444441">心跳/连接管理</text>
<rect x="348" y="641" width="11" height="11" rx="2" fill="#FBEAF0" stroke="#D4537E" stroke-width="0.6"/>
<text x="363" y="653" style="font:400 10.5px 'Consolas',monospace;fill:#444441">消息处理</text>
<rect x="432" y="641" width="11" height="11" rx="2" fill="#FAECE7" stroke="#D85A30" stroke-width="0.6"/>
<text x="447" y="653" style="font:400 10.5px 'Consolas',monospace;fill:#444441">决策/超时</text>
<rect x="516" y="641" width="11" height="11" rx="2" fill="#F1EFE8" stroke="#888780" stroke-width="0.6"/>
<text x="531" y="653" style="font:400 10.5px 'Consolas',monospace;fill:#444441">事件回调</text>

<line x1="380" y1="858" x2="380" y2="892"
  stroke="#888780" stroke-width="1.6" marker-end="url(#ar)"/>
<rect x="328" y="861" width="104" height="20" rx="5"
  fill="white" stroke="#C4C2B8" stroke-width="0.6"/>
<text x="380" y="875" text-anchor="middle"
  style="font:400 11px 'Consolas',monospace;fill:#5F5E5A">层间调用</text>

<rect x="20" y="896" width="720" height="412" rx="12"
  fill="#E1F5EE" stroke="#1D9E75" stroke-width="1.2" stroke-dasharray="7 3"/>
<text x="380" y="918" text-anchor="middle"
  style="font:700 13px 'Consolas',monospace;fill:#085041">
  传输层 (Transport Layer)
</text>

<rect x="36" y="928" width="688" height="368" rx="8"
  fill="#d4edda" stroke="#3B6D11" stroke-width="1" stroke-dasharray="5 3"/>
<text x="380" y="950" text-anchor="middle"
  style="font:700 13px 'Consolas',monospace;fill:#27500A">WebSocketClient</text>

<rect x="52" y="960" width="196" height="120" rx="7"
  fill="#E1F5EE" stroke="#1D9E75" stroke-width="1" stroke-dasharray="4 2"/>
<text x="150" y="979" text-anchor="middle"
  style="font:600 12px 'Consolas',monospace;fill:#085041">连接管理</text>
<text x="68" y="998" style="font:400 11px 'Consolas',monospace;fill:#0F6E56">• InitWebSocket</text>
<text x="68" y="1015" style="font:400 11px 'Consolas',monospace;fill:#0F6E56">• CloseWebSocket</text>
<text x="68" y="1032" style="font:400 11px 'Consolas',monospace;fill:#0F6E56">• IsConnected</text>
<text x="68" y="1049" style="font:400 11px 'Consolas',monospace;fill:#0F6E56">• TriggerReconnect</text>
<text x="68" y="1071" style="font:400 10.5px 'Consolas',monospace;fill:#888780">（连接生命周期）</text>

<rect x="280" y="960" width="200" height="120" rx="7"
  fill="#FAEEDA" stroke="#EF9F27" stroke-width="1" stroke-dasharray="4 2"/>
<text x="380" y="979" text-anchor="middle"
  style="font:600 12px 'Consolas',monospace;fill:#633806">重连管理</text>
<text x="296" y="998" style="font:400 11px 'Consolas',monospace;fill:#854F0B">• needReconnect</text>
<text x="296" y="1015" style="font:400 11px 'Consolas',monospace;fill:#854F0B">• reconnectTimer</text>
<text x="296" y="1032" style="font:400 11px 'Consolas',monospace;fill:#854F0B">• AttemptReconnect</text>
<text x="296" y="1049" style="font:400 11px 'Consolas',monospace;fill:#854F0B">• maxReconnectAttempts</text>

<rect x="502" y="960" width="210" height="120" rx="7"
  fill="#FBEAF0" stroke="#D4537E" stroke-width="1" stroke-dasharray="4 2"/>
<text x="607" y="979" text-anchor="middle"
  style="font:600 12px 'Consolas',monospace;fill:#72243E">收发消息</text>
<text x="518" y="998" style="font:400 11px 'Consolas',monospace;fill:#993556">• SendMessage()</text>
<text x="518" y="1015" style="font:400 11px 'Consolas',monospace;fill:#993556">• SendMessageAsync()</text>
<text x="518" y="1032" style="font:400 11px 'Consolas',monospace;fill:#993556">• ReceiveLoop()</text>
<text x="518" y="1049" style="font:400 11px 'Consolas',monospace;fill:#993556">• SendBinaryMessage()</text>

<line x1="380" y1="1082" x2="380" y2="1104"
  stroke="#1D9E75" stroke-width="1.5" marker-end="url(#ar)"/>

<rect x="100" y="1108" width="560" height="116" rx="7"
  fill="#042C53" stroke="#378ADD" stroke-width="1.2"/>
<text x="380" y="1130" text-anchor="middle"
  style="font:700 12px 'Consolas',monospace;fill:#B5D4F4">MonitorLoopAsync()</text>
<text x="380" y="1147" text-anchor="middle"
  style="font:400 11px 'Consolas',monospace;fill:#85B7EB">（简化版 - 仅连接状态监控）</text>
<text x="122" y="1166" style="font:400 11px 'Consolas',monospace;fill:#9FE1CB">while (!cancelled) {</text>
<text x="138" y="1183" style="font:400 10.5px 'Consolas',monospace;fill:#9FE1CB">  if (socket not open) { if (needReconnect) AttemptReconnectAsync }</text>
<text x="122" y="1200" style="font:400 11px 'Consolas',monospace;fill:#9FE1CB">  await Delay(500ms) }</text>

<rect x="100" y="1238" width="560" height="48" rx="6"
  fill="#FCEBEB" stroke="#E24B4A" stroke-width="1" stroke-dasharray="4 2"/>
<text x="120" y="1257"
  style="font:600 11px 'Consolas',monospace;fill:#A32D2D">✕  移除的逻辑：</text>
<text x="120" y="1273"
  style="font:400 10.5px 'Consolas',monospace;fill:#712B13">• SendHeartBeatAsync() {"op":"heartbeat"} 服务器不支持  •  lastHeartbeatTime 超时检测</text>

<line x1="380" y1="1312" x2="380" y2="1348"
  stroke="#888780" stroke-width="1.6" marker-end="url(#ar)"/>

<rect x="20" y="1352" width="720" height="112" rx="12"
  fill="#E6F1FB" stroke="#378ADD" stroke-width="1.2" stroke-dasharray="7 3"/>
<text x="380" y="1373" text-anchor="middle"
  style="font:700 13px 'Consolas',monospace;fill:#0C447C">
  网络层 (Network Layer)
</text>

<rect x="36" y="1384" width="296" height="62" rx="7"
  fill="#B5D4F4" stroke="#185FA5" stroke-width="1"/>
<text x="184" y="1408" text-anchor="middle"
  style="font:600 12px 'Consolas',monospace;fill:#042C53">System.Net.WebSockets</text>
<text x="184" y="1428" text-anchor="middle"
  style="font:400 11px 'Consolas',monospace;fill:#0C447C">ClientWebSocket</text>

<line x1="332" y1="1415" x2="396" y2="1415"
  stroke="#7F77DD" stroke-width="1.5" marker-end="url(#ar)"/>

<rect x="400" y="1384" width="340" height="62" rx="7"
  fill="#9FE1CB" stroke="#0F6E56" stroke-width="1"/>
<text x="570" y="1408" text-anchor="middle"
  style="font:600 12px 'Consolas',monospace;fill:#04342C">服务端</text>
<text x="570" y="1428" text-anchor="middle"
  style="font:400 11px 'Consolas',monospace;fill:#085041">SYSB WebSocket Server（支持 ping/pong 协议）</text>

</svg>
## 心跳与重连流程图

## SYSA 接口调用链路

![[Pasted image 20260612105456.png]]

RobotNetworkClient.SetRobotConnectWifi()
→ IRobotAdapter.AdapterConnectWifi()
→ ProtocolManager.ConnectWifi()
→ IMotionProtocolEngine.ConnectWifi()
→ GrpcEngine.ConnectWifi()
→ _robotSDKClient.ConnectWifi() \[gRPC调用]
          
## SYSB接口调用链路

RobotNavigationClient.TransformImageToWorld
-> ISRobotPerceptionAdapter.AdapterPointMove
-> ProtocolManager.PointMove
-> IPerceptionProtocolEngine.PointMove
-> WebSocketEngine.PointMove