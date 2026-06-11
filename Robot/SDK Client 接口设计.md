---
title: "[[SDK Client 接口设计]]"
type: Permanent
status: ing
Creation Date: 2026-06-11 17:02
tags:
---

## Client 架构框图

![[Pasted image 20260611170608.png]]

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

