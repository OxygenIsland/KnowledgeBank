---
title: "[[comm-ros2-websocket]]"
type: Permanent
status: done
Creation Date: 2026-08-20 14:48
tags:
---
## 一、这个模块是干什么的？
简单一句话：**把机器人内部的 [[ROS2 入门|ROS2]] 话题/服务，通过 [[WebSocket]] 暴露给外部客户端（手机 App、PC 上位机、SDK）。**
```
外部客户端 (C# SDK / 手机 / 浏览器)
        ↕  WebSocket (JSON / 二进制)
  comm_server (这个模块)
        ↕  ROS2 话题/服务 (DDS)
机器人内部其他 ROS 节点 (导航、感知、语音...)
```
---
## 二、仓库目录结构
```
comm/
├── comm_server/
│   ├── websocket/          ← 纯 WebSocket 服务器层（不感知 ROS）
│   │   └── include/websocket/
│   │       ├── websocket_server.hpp/.ipp   ← 服务器核心模板实现
│   │       ├── server_base.hpp             ← 抽象接口
│   │       ├── websocket_types.hpp         ← 所有数据结构定义
│   │       ├── callback_queue.hpp          ← 多线程回调队列
│   │       ├── asset_transfer_manager.hpp  ← 文件分块传输管理
│   │       ├── server_factory.hpp          ← 工厂方法（含/不含TLS）
│   │       └── utils.hpp                  ← 工具函数
│   │
│   └── comm_bridge/        ← ROS2 桥接层（连接 WebSocket 与 ROS）
│       ├── include/comm_ros2_bridge/
│       │   ├── comm_ros2_bridge.hpp        ← 桥接核心类
│       │   └── comm_ros2_component.hpp     ← ROS2 生命周期节点包装
│       └── src/
│           ├── comm_ros2_bridge.cpp        ← 所有业务逻辑实现
│           ├── comm_ros2_component.cpp     ← 生命周期回调
│           └── comm_ros2_bridge_node.cpp   ← 独立进程入口
│
├── dynmsg/                 ← 动态消息序列化库（JSON ↔ ROS CDR）
│   └── src/
│       └── msg_parser_cpp.cpp  ← json_and_typeinfo_to_rosmsg 等
│
└── comm_client/            ← 客户端（目前未激活，有 COLCON_IGNORE）
```
---
## 三、三层分层设计
这个模块严格分三层，每层各司其职：
```
┌─────────────────────────────────────────────────────────┐
│  层1：ROS 生命周期层                                     │
│  CommROS2Component (comm_ros2_component.hpp)            │
│  ── 继承 rclcpp_lifecycle::LifecycleNode                │
│  ── 管理 Configure / Activate / Deactivate / Shutdown   │
│  ── 持有 CommRos2Bridge 的所有权                         │
└────────────────────┬────────────────────────────────────┘
                     │ 创建并调用
┌────────────────────▼────────────────────────────────────┐
│  层2：业务桥接层                                         │
│  CommRos2Bridge (comm_ros2_bridge.hpp/.cpp)             │
│  ── 持有 server_ (ServerBase 指针)                      │
│  ── 将 WebSocket 事件转化为 ROS 操作                     │
│  ── 将 ROS 消息转化为 WebSocket 发送                     │
│  ── 持有 dynmsg 做序列化                                 │
└────────────────────┬────────────────────────────────────┘
                     │ 调用
┌────────────────────▼────────────────────────────────────┐
│  层3：纯 WebSocket 传输层                                │
│  Server<ServerConfiguration> (websocket_server.hpp/.ipp)│
│  ── 基于 websocketpp + Asio                             │
│  ── 完全不感知 ROS，只处理 WebSocket 帧和连接           │
│  ── 通过 ServerHandlers 回调结构回调上层                │
└─────────────────────────────────────────────────────────┘
```
---
## 四、层3 详解：[[WebSocket]] 服务器（websocket_server.ipp）
### 4.1 类模板设计
```cpp
// websocket_server.hpp
template <typename ServerConfiguration>
class Server : public ServerBase<ConnectionHandlePtr> {
    // ServerConfiguration 决定是否用 TLS
    // 实际实例化时有两种：不加密 / TLS加密
};
```

### 4.2 关键数据成员

| 成员 | 类型 | 作用 |
|------|------|------|
| `server_` | `websocketpp::server<Config>` | websocketpp 的核心，持有所有连接 |
| `server_thread_` | `unique_ptr<thread>` | 运行 `server_.run()` 的单线程，负责所有网络 I/O |
| `handler_callback_queue_` | `unique_ptr<CallbackQueue>` | 5个线程，处理收到消息的业务逻辑 |
| `ping_timer_` | `shared_ptr<Timer>` | 定时器，每隔 N 秒广播 ping |
| `clients_` | `map<hdl, ClientInfo>` | 当前所有已连接客户端 |
| `channels_` | `map<topic, ChannelWithoutId>` | 服务端已发布的所有 ROS 话题 |
| `services_` | `map<name, ServiceWithoutId>` | 服务端已发布的所有 ROS 服务 |
| `handlers_` | `ServerHandlers<hdl>` | **上层注入的回调函数集合** |

### 4.3 ServerHandlers：上下层的唯一接口

```cpp
// server_base.hpp
template <typename ConnectionHandle>
struct ServerHandlers {
    // ── 客户端订阅/取消 ──────────────────────────────────
    std::function<void(TopicName, ConnectionHandle)> subscribe_handler;
    std::function<void(TopicName, ConnectionHandle)> unsubscribe_handler;

    // ── 客户端发布话题 ────────────────────────────────────
    std::function<void(ClientAdvertisement, ConnectionHandle)> client_advertise_handler;
    std::function<void(TopicName, ConnectionHandle)>           client_unadvertise_handler;
    std::function<void(ClientMessage, ConnectionHandle)>       client_message_handler;

    // ── 客户端调用服务 ────────────────────────────────────
    std::function<void(ServiceRequest, ConnectionHandle)>      client_service_request_handler;
    std::function<void(ServiceResponse, ConnectionHandle)>     client_service_response_handler;

    // ── 客户端暴露服务 ────────────────────────────────────
    std::function<void(ServiceWithoutId, ConnectionHandle)>    client_service_advertise_handler;
    std::function<void(ServiceNameType, ConnectionHandle)>     client_service_unadvertise_handler;

    // ── 文件传输 ──────────────────────────────────────────
    std::function<void(string, uint32_t, ConnectionHandle)>    fetch_asset_handler;
    std::function<void(FetchAssetChunkRequest, ConnectionHandle)> fetch_asset_chunk_handler;
    std::function<void(string, string, uint64_t, uint32_t, ConnectionHandle)> begin_upload_asset_handler;
    std::function<void(string, string, uint32_t, ConnectionHandle)> complete_upload_asset_handler;

    // ── 音频 ──────────────────────────────────────────────
    std::function<void(vector<uint8_t>, ConnectionHandle)>     audio_data_handler;
};
```

> **理解要点：** `ServerHandlers` 里全是 `std::function`（类似函数指针）。WebSocket 层收到消息后调这些函数，调哪个具体实现由上层（`CommRos2Bridge`）在初始化时绑定好。这种设计叫**依赖注入**。

### 4.4 线程模型（共 8 个线程）

```
线程1：server_thread_
    server_.run()  ← Asio io_service 单线程
    职责：TCP 读写、WebSocket 帧拆装、握手
    接收消息后：快速调用 message_handler → 塞进队列，立即返回
    发送消息时：所有 con->send() 最终都在这里异步执行

线程2-6：handler_callback_queue_ (5个线程)
    从共享 deque 取任务 → 执行 handleMessage
    handleTextMessage：parse JSON → 分发 op
    handleBinaryMessage：读 opcode → 分发二进制协议
    调用 handlers_.xxx_handler → 进入 CommRos2Bridge 层

线程7：ping_timer_
    每隔 broadcast_ping_interval 秒触发
    调用 startBroadCastPing() → sendJson() → con->send()
    con->send() 是非阻塞的，投递给 server_thread_ 的 io_service

线程8：rosgraphListenThread_ (在 CommRos2Bridge 创建)
    每 200ms 检查 ROS 计算图变化
    话题/服务有增减时 → updateAdvertisedTopics/Services
    → server_->addChannels/removeChannels

ROS executor 线程(数量取决于节点配置)
    运行 rosMessageHandler（ROS 订阅回调）
    → server_->sendMessage() → con->send()（非阻塞）
```

**关键规律：** `con->send()` 是非阻塞的，把数据投递到 io_service 队列，真正的网络写由 `server_thread_` 执行。所以发送消息的线程可以立刻返回。

### 4.5 消息收发流程

#### 收（客户端 → 服务端）

```
网络 TCP 数据包
  → server_thread_ async_read_some() 回调（多次）
  → websocketpp 状态机拼装 WebSocket 帧
  → 帧组装完成，调用 message_handler lambda（极快）
     addCallback([]{handleMessage(hdl, msg)})
  → server_thread_ 立刻返回继续处理其他 IO 事件

callback_queue 某线程：
  → handleMessage
  → if (TEXT)  → handleTextMessage → json::parse → 按 op 分发
  → if (BINARY) → handleBinaryMessage → 读 opcode → 分发

TEXT 消息的 op 映射：
  "subscribe"         → handleSubscribe   → handlers_.subscribe_handler
  "unsubscribe"       → handleUnsubscribe → handlers_.unsubscribe_handler
  "advertise"         → handleAdvertise   → handlers_.client_advertise_handler
  "unadvertise"       → handleUnadvertise → handlers_.client_unadvertise_handler
  "publish"           → handlePublish     → handlers_.client_message_handler
  "call_service"      → handleCallService → handlers_.client_service_request_handler
  "service_response"  → handleServiceResponse → handlers_.client_service_response_handler
  "advertise_service" → handleServiceAdvertise → handlers_.client_service_advertise_handler
  "ping"              → handlePing        → 直接回 pong（不走 handlers_）
  "pong"              → handlePong        → 更新连接活跃时间戳

BINARY 消息的 opcode 映射（第1字节决定）：
  UPLOAD_ASSET_REQUEST       → handlers_.upload_asset_handler
  UPLOAD_ASSET_CHUNK_REQUEST → handlers_.upload_asset_chunk_handler
  AUDIO_DATA                 → handlers_.audio_data_handler
```

#### 发（服务端 → 客户端）

```
// 方式1：服务端主动广播（ROS 话题数据）
ROS executor 线程 → rosMessageHandler
  → server_->sendMessage(hdl, topic, payload, size)
  → 检查缓冲区 & 客户端是否订阅
  → sendJson(con, payload)
  → con->send(payload.dump(), TEXT)  ← 非阻塞，投递给 io_service
  → server_thread_ 异步 async_write

// 方式2：服务端回复客户端请求
callback_queue 线程 → handlePing → sendJson → ...（同上）

// 方式3：定时 ping
ping_timer_ 线程 → startBroadCastPing → sendJson → ...（同上）

// 方式4：二进制数据（文件块下载等）
sendFetchAssetResponse / sendFetchAssetChunkResponse
  → con->get_message() → message->append_payload() → con->send(message)
  → server_thread_ 异步发送
```

---

## 五、层2 详解：CommRos2Bridge（业务桥接层）

### 5.1 核心职责
`CommRos2Bridge` 是整个模块的业务核心，它：
1. **持有 WebSocket server** 并向其注入所有 handlers
2. **维护订阅关系** — 记录哪个 WebSocket 客户端订阅了哪个 ROS 话题
3. **做消息格式转换** — JSON ↔ ROS CDR 二进制 (via dynmsg)
4. **监控 ROS 计算图** — 话题/服务增减时自动更新 WebSocket 端的广播列表
5. **处理文件传输** — fetchAsset/uploadAsset/分块传输
6. **处理音频播放** — 接收 PCM 数据并通过 ALSA 播放

### 5.2 关键数据成员

```cpp
// comm_ros2_bridge.hpp（成员变量部分）
unique_ptr<ServerBase<ConnectionHandlePtr>> server_;   // WebSocket 服务器

// ROS 订阅管理
map<TopicName, ChannelWithoutId> advertised_topics_;   // 当前已广播给 WS 客户端的话题
map<TopicName, SubscriptionsByClient> subscriptions_;  // topic → {客户端hdl → ROS订阅者}
mutex subscription_mutex_;

// 客户端发布管理
map<hdl, ClientPublications> client_advertised_publications_; // hdl → {topic → ROS发布者}
mutex client_advertisements_mutex_;

// 服务管理
map<ServiceName, ServiceWithoutId> advertised_services_; // 已广播给 WS 的 ROS 服务
map<ServiceName, GenericServer::SharedPtr> service_servers_; // 客户端暴露的服务
map<ServiceName, GenericClient::SharedPtr> service_clients_; // 调用 ROS 服务的客户端

// 线程
unique_ptr<thread> rosgraph_listen_thread_;

// 音频播放
AudioPlaybackBuffer audio_buffer_;
atomic<bool> playback_active_;
unique_ptr<thread> playback_thread_;
```

### 5.3 生命周期（由 CommROS2Component 驱动）

```
节点启动
    ↓
CommROS2Component 构造
    → CommRos2Bridge 构造（仅初始化，不启动服务）

onConfigure 被调用
    → CommRos2Bridge::Configure()
    → 读取 ROS 参数 (port, ping_interval, whitelist...)
    → server_ = ServerFactory::create(...)   ← 创建 WebSocket 服务器
    → 向 server_ 注入所有 ServerHandlers     ← 绑定回调
    → server_->start(host, port)             ← 启动 server_thread_，开始监听

onActivate 被调用
    → CommRos2Bridge::Activate()
    → 扫描当前 ROS 计算图 → updateAdvertisedTopics/Services
    → 启动 rosgraph_listen_thread_           ← 开始监控话题/服务变化

onDeactivate 被调用
    → CommRos2Bridge::Deactivate()
    → activate_ = false → rosgraph_listen_thread_ 退出

onShutdown 被调用
    → CommRos2Bridge::Shutdown / 析构
    → rosgraph_listen_thread_.join()
    → playback_thread_.join()
    → server_->stop()                        ← 关闭所有连接，停止 server_thread_
```

### 5.4 核心场景：客户端订阅 ROS 话题

```
WebSocket 客户端发送：{"op":"subscribe","topic":"/sdk/nav/pose"}

  ↓ server_thread_ 接收帧
  ↓ callback_queue 线程
  handleSubscribe(payload, hdl)
    → 检查话题是否在 channels_ 里（已广播的话题）
    → 调用 handlers_.subscribe_handler(topic, hdl)
         ↓
         CommRos2Bridge::subscribe(topic, hdl)
           → lock subscription_mutex_
           → node_ptr_->create_generic_subscription(
                 topic, type, qos,
                 bind(&CommRos2Bridge::rosMessageHandler, topic, type, hdl, _1)
             )                         ← 创建 ROS 订阅者
           → subscriptions_[topic][hdl] = subscriber  ← 记录映射关系
           → lock.unlock()
    → clients_[hdl].subscriptions_by_channel[topic] = channel  ← WebSocket 层也记录

以后每次 ROS 有新消息发布 /sdk/nav/pose：
  ROS executor 线程 → rosMessageHandler(topic, type, hdl, serialized_msg)
    → rmw_deserialize(CDR → C++ struct)
    → dynmsg::cpp::message_to_json(ros_msg) → nlohmann::json
    → payload = {"op":"publish","topic":...,"msg":{"x":1.2,...},"timestamp":...}
    → server_->sendMessage(hdl, topic, payload, size)
         → 检查缓冲区未满
         → 检查 clients_[hdl] 确实订阅了该话题
         → sendJson(con, payload)
         → con->send(json_string, TEXT)  ← 非阻塞，投递给 io_service
         → server_thread_ 发出 WebSocket 帧
```

### 5.5 核心场景：客户端向服务端发布话题（反向）

```
步骤1 — 声明：WebSocket 客户端发送 {"op":"advertise","topic":"/speech/pass_asr_audio","type":"std_msgs__Float32MultiArray"}

  callback_queue 线程 → handleAdvertise → handlers_.client_advertise_handler
    ↓
    CommRos2Bridge::clientAdvertise(advertisement, hdl)
      → node_ptr_->create_generic_publisher(topic, type, qos)  ← 创建 ROS 发布者
      → client_advertised_publications_[hdl][topic] = publisher ← 记录
      → server_->sendClientSubscribe(hdl, advertisement)        ← 发回订阅确认

步骤2 — 发布：WebSocket 客户端发送 {"op":"publish","topic":"/speech/pass_asr_audio","msg":{"data":[...]}}

  callback_queue 线程 → handlePublish(payload, hdl)
    → msg_value = getRequiredString(payload, "msg")    ← 提取 msg 字段，重新序列化为 string
    → handlers_.client_message_handler(clientMessage, hdl)
         ↓
         CommRos2Bridge::clientMessage(message, hdl)
           → dynmsg::cpp::json_and_typeinfo_to_rosmsg(type_info, json_str, buffer)
               ← 重新 parse JSON → 填充 C++ 结构体
           → rmw_serialize(C++ struct → CDR 二进制)
           → publisher->publish(serialized_message)   ← 发布到 ROS DDS
           → ROS 内其他节点（如 asr_ros）收到消息
```

### 5.6 核心场景：客户端调用 ROS 服务

```
WebSocket 客户端发送：
  {"op":"call_service","service":"/sdk/nav/set_goal","args":{"x":1.0,"y":2.0},"id":"42"}

  callback_queue 线程 → handleCallService → handlers_.client_service_request_handler
    ↓
    CommRos2Bridge::clientServiceRequest(request, hdl)
      → 找到 service_clients_[service_name]（没有则创建 GenericClient）
      → dynmsg::json_and_typeinfo_to_rosmsg(type_info, request.json_data_str)
      → rmw_serialize(C++ struct → CDR)
      → client->async_send_request(req_msg, callback)  ← 异步发送，不阻塞
           ↓（收到 ROS 服务响应后，callback 在 ROS executor 线程中被调用）
           callback(future)
             → rmw_deserialize(CDR → C++ struct)
             → dynmsg::message_to_json(ros_msg)  → nlohmann::json
             → ServiceResponse{call_id=42, service_name, json_str}
             → server_->sendServiceResponse(hdl, response)
             → WebSocket 客户端收到：{"op":"service_response","service":...,"values":{...},"id":"42"}
```

---

## 六、层1 详解：CommROS2Component（生命周期节点）

```cpp
// comm_ros2_component.hpp
class CommROS2Component : public daystar_utils::ros_integration::LifecycleNode {
    unique_ptr<CommRos2Bridge> comm_ros_bridge_ptr_;

    // 6个生命周期回调，对应 ROS2 节点状态机：
    onConfigure()  → bridge.Configure()   // 读参数、创建 server、绑定 handlers
    onActivate()   → bridge.Activate()    // 启动话题扫描线程
    onDeactivate() → bridge.Deactivate()  // 停止话题扫描线程
    onShutdown()   → bridge.Shutdown()    // 关闭所有资源
    onCleanUp()    → bridge.CleanUp()
    onError()      → 错误处理
};
```

这层的主要价值是把 `CommRos2Bridge` 融入 ROS2 的生命周期管理体系，让系统管理器可以统一控制启停。

---

## 七、dynmsg：消息序列化库

### 7.1 作用

在 JSON 和 ROS CDR 二进制之间做双向转换，且在运行时动态处理任意消息类型（不需要编译时知道消息类型）。

```
JSON string → nlohmann::json::parse() → json 对象
           → json_to_rosmsg_impl()     → C++ ROS message struct
           → rmw_serialize()           → CDR 二进制（可以发给 ROS DDS）

CDR 二进制  → rmw_deserialize()         → C++ ROS message struct
           → dynmsg::message_to_json()  → nlohmann::json 对象
           → payload.dump()             → JSON string（可以发给 WebSocket 客户端）
```

### 7.2 关键函数

```cpp
// msg_parser_cpp.cpp
void json_and_typeinfo_to_rosmsg(
    const TypeInfo_Cpp* type_info,
    const std::string& json_str,    // JSON 字符串，如 {"data":[1.0, 2.0, ...]}
    void* ros_message               // 指向已分配好的 ROS 消息内存
) {
    nlohmann::json root = nlohmann::json::parse(json_str);  // ← 第一次 parse
    impl::json_to_rosmsg_impl(root, type_info, buffer);     // ← 递归填充字段
}

// 反方向
nlohmann::json dynmsg::cpp::message_to_json(const RosMessage_Cpp& ros_msg);
```

### 7.3 性能注意

对于含大量数值的消息（如 `Float32MultiArray` 有 144384 个 float），`json_and_typeinfo_to_rosmsg` 会执行两次 JSON 解析（因为 `getRequiredString` 先 dump 再传入），在嵌入式 ARM 平台上非常耗时（3-5 秒）。**大数据量消息应使用二进制协议传输。**

---

## 八、文件传输机制

### 8.1 小文件（< LARGE_FRAME_THRESHOLD）

```
客户端发 {"op":"fetch_asset","uri":"package://daystar_resource/xxx.png","request_id":1}
  ↓
fetchAsset(uri, request_id, hdl)
  → resource_retriever::get(uri)   ← 读文件
  → server_->sendFetchAssetResponse(hdl, response)
  ← 二进制帧：[opcode:1][request_id:4][status:1][err_len:4][data_len:4][data:N]
```

### 8.2 大文件（分块下载）

```
① 客户端发 fetch_asset → 服务端返回 fetch_asset_meta_response（含 session_id、total_chunks）
② 客户端循环发 fetch_asset_chunk(session_id, chunk_index) → 服务端返回每块数据 + CRC32
③ 客户端自行拼合、校验
```

### 8.3 分块上传

```
① 客户端发 begin_upload_asset(uri, md5, file_size) → 服务端返回 session_id、chunk_size
② 客户端分块发二进制帧 UPLOAD_ASSET_CHUNK_REQUEST(session_id, chunk_index, crc32, data)
③ 客户端发 complete_upload_asset(session_id, uri) → 服务端拼合、校验、写文件
```

---

## 九、连接管理与心跳

### 9.1 连接限制

```cpp
// validateConnection() 中：
backdoor_connection_count_  ← "daystarbot_sdk" 身份码的连接，最多 max_connections 个
normal_connection_count_    ← 普通身份码连接，最多 1 个
```

### 9.2 心跳机制

```
服务端 ping_timer_（每隔 broadcast_ping_interval 秒）
  → startBroadCastPing()
  → 对每个连接：
      if (now - client.time_point > broadcast_timeout_limit)
          → connection.close()  ← 超时主动断开
      else
          → sendJson({"op":"ping","from":"comm_ros2_bridge","timestamp":...})

客户端收到 ping 应回 pong：
  handlePong() → clients_[hdl].time_point = now  ← 更新活跃时间戳

配置（param.yaml）：
  broadcast_ping_interval: 10   秒（服务端发 ping 的间隔）
  broadcast_timeout_limit: 30   秒（多久没收到 pong 断开连接）
```

---

## 十、所有锁和它们保护什么

| 锁 | 类型 | 保护的数据 |
|----|------|-----------|
| `clients_mutex_` | `shared_mutex` | `clients_` map（连接表） |
| `channels_mutex_` | `shared_mutex` | `channels_` map（服务端话题表） |
| `services_mutex_` | `shared_mutex` | `services_` map（服务端服务表） |
| `client_channels_mutex_` | `shared_mutex` | `client_channels_` map（客户端发布的话题，WS层） |
| `client_services_mutex_` | `shared_mutex` | `client_services_` map（客户端暴露的服务，WS层） |
| `subscription_mutex_` | `mutex` | `subscriptions_` & `advertised_topics_`（桥接层） |
| `client_advertisements_mutex_` | `mutex` | `client_advertised_publications_`（桥接层） |

> `shared_mutex` 支持多读单写（shared_lock 读 / unique_lock 写），读多写少的场景下性能更好。

---

## 十一、关键数据结构速查

```cpp
// websocket_types.hpp

// 客户端连接信息
struct ClientInfo {
    string name;           // IP:port
    bool is_backdoor_connection;
    time_point time_point; // 最后收到 pong 的时间，用于心跳超时判断
    map<TopicName, ChannelWithoutId> subscriptions_by_channel; // 已订阅话题
    set<TopicName>         advertised_topics;    // 客户端发布的话题
    set<ServiceNameType>   advertised_services;  // 客户端暴露的服务
    bool subscribed_to_con_graph;
};

// 话题通道（不含 ID）
struct ChannelWithoutId {
    TopicName topic;
    string type;    // 如 "std_msgs/msg/String"
    string schema;
};

// 客户端发来的消息（publish）
struct ClientMessage {
    uint64_t log_time;
    uint64_t publish_time;
    uint32_t sequence;
    ClientAdvertisement advertisement;  // 包含 topic 和 type
    size_t data_length;
    string json_str;   // msg 字段的 JSON 字符串（{"data":[...]}）
};

// 服务请求/响应
struct ServiceRequest {
    uint32_t call_id;
    string service_name;
    string json_data_str;
};

struct ServiceResponse {
    uint32_t call_id;
    string service_name;
    string json_data_str;
};
```

---

## 十二、整体调用关系图（一图总结）

```
                         机器人内部 ROS 世界
                    ┌──────────────────────────────┐
                    │  /sdk/nav/pose (1Hz 发布)     │
                    │  /sdk/speech/asr_result       │
                    │  /sdk/system/battery          │
                    │  /speech/pass_asr_audio       │
                    └───────────┬──────────────────┘
                                │ DDS (rmw)
                    ┌───────────▼──────────────────────────────────┐
                    │           CommRos2Bridge                      │
                    │                                               │
                    │  rosgraphListenThread (1线程)                 │
                    │    └→ updateAdvertisedTopics/Services         │
                    │       └→ server_->addChannels()               │
                    │                                               │
                    │  ROS executor 线程                            │
                    │    └→ rosMessageHandler(topic, type, hdl, msg)│
                    │       CDR反序列化 → JSON → server_->sendMessage│
                    │                                               │
                    │  callback_queue 线程（来自WS层）              │
                    │    └→ subscribe/unsubscribe                   │
                    │       create_generic_subscription/publisher   │
                    │    └→ clientMessage                           │
                    │       JSON → CDR序列化 → publisher->publish   │
                    │    └→ clientServiceRequest                    │
                    │       JSON → CDR → async_send_request         │
                    └──────────────────┬───────────────────────────┘
                          server_->xxx │ (ServerBase 接口)
                    ┌──────────────────▼───────────────────────────┐
                    │    WebSocket Server (Server<Config>)          │
                    │                                               │
                    │  server_thread_ (1线程)                       │
                    │    Asio io_service: TCP读写、WS帧处理         │
                    │    所有 con->send() 最终在这里执行            │
                    │                                               │
                    │  handler_callback_queue_ (5线程)              │
                    │    handleTextMessage → JSON parse → 分发      │
                    │    handleBinaryMessage → opcode → 分发        │
                    │    → handlers_.xxx_handler → CommRos2Bridge   │
                    │                                               │
                    │  ping_timer_ (1线程)                          │
                    │    每10秒 → startBroadCastPing                │
                    └────────────────┬─────────────────────────────┘
                                     │ WebSocket 帧 (TCP)
                    ┌────────────────▼─────────────────────────────┐
                    │           外部 WebSocket 客户端               │
                    │    C# SDK / 手机 App / 浏览器 / 调试工具      │
                    └──────────────────────────────────────────────┘
```

---

## 十三、初学者常见疑问解答

**Q: `Server` 是一个模板类，为什么要用模板？**

A: 为了复用代码支持有 TLS（加密）和无 TLS 两种版本。`ServerConfiguration` 是 websocketpp 的配置类型，TLS 版和非 TLS 版的类型不同，但逻辑完全一样，所以用模板一份代码搞定两种情况。`ServerFactory::create()` 根据参数决定实例化哪个版本。

**Q: `.ipp` 文件是什么？**

A: `.ipp` 是模板的实现文件。C++ 模板的实现必须对使用者可见（因为编译器要在使用时展开），所以不能放在 `.cpp` 文件里。`.ipp` 文件在 `.hpp` 结尾被 `#include` 进来，本质上就是 `.hpp` 的一部分，只是为了把接口声明和实现代码分开放置，方便阅读。

**Q: `ConnectionHandlePtr` 是什么？**

A: 是 `websocketpp::connection_hdl`（本质是 `weak_ptr<void>`）。它代表一个连接的"弱引用句柄"。弱引用的好处是：即使连接已经断开，持有 hdl 也不会崩溃，只是 `server_.get_con_from_hdl()` 会返回 nullptr 或出错。

**Q: `std::bind` 是干什么的？**

A: `std::bind` 把一个成员函数绑定成一个 `std::function`，类似于"给函数预填充部分参数"。比如：

```cpp
// 原函数：void CommRos2Bridge::subscribe(TopicName topic, ConnectionHandlePtr hdl)
// bind 之后：只需要传 topic 和 hdl，this 已经绑定好了
handlers.subscribe_handler = std::bind(&CommRos2Bridge::subscribe, this, _1, _2);
// 等价于 lambda：
handlers.subscribe_handler = [this](TopicName t, ConnectionHandlePtr h){ subscribe(t, h); };
```

**Q: `shared_mutex` 和普通 `mutex` 的区别？**

A: `shared_mutex` 支持两种锁：
- `shared_lock`（读锁）：多个线程可以同时持有，互不阻塞
- `unique_lock`（写锁）：独占，阻塞所有其他读写

对于 `clients_` 这种"读多写少"的数据结构（发消息时读，连接建立/断开时写），`shared_mutex` 性能更好。

**Q: WebSocket 的 `op` 字段和 ROS 话题是怎么对应的？**

A: 没有直接对应关系。`op` 是 WebSocket 协议层的操作码（subscribe/publish/advertise 等），决定"做什么动作"。话题名称在消息的 `topic` 字段里，内容在 `msg` 字段里。整个流程是：客户端用 `op=subscribe` 表示想订阅某话题 → 服务端建立 ROS 订阅 → ROS 收到数据后用 `op=publish` 推给客户端。
