---
title: "[[C++ WebSocket 库 websocketpp]]"
type: Permanent
status: done
Creation Date: 2026-08-20 14:27
tags:
---
## 1. 是什么（What）
**[websocketpp](https://github.com/zaphoyd/websocketpp)** 是一个只依赖头文件（header-only）的 C++ [[WebSocket]] **协议实现库**：它负责 HTTP 升级握手、帧（frame）编解码、分片消息重组、扩展协商（如压缩）、TLS 封装，但**不自己写底层 socket/事件循环**，而是把传输层委托给 Asio（`websocketpp::config::asio` / `asio_no_tls`）或用户自定义的传输策略。

一句话定位：**websocketpp 是"协议层"，Asio 是"传输层"**——这也是 [[C++ 异步网络库 Asio]]中提到的分层案例的另一半。

本仓库的真实用法（`overlay_ws/src/sdk_server/comm/comm_server/websocket`）：

```cpp
// websocket_types.hpp
using ConnectionHandlePtr = websocketpp::connection_hdl;
using OpCode = websocketpp::frame::opcode::value;

// websocket_server.ipp
server_.init_asio(ec);                                  // 内部持有一个 asio::io_service
server_.set_validate_handler(...);                        // 握手前校验（License / 身份码）
server_.set_open_handler(...);
server_.set_close_handler(...);
server_.set_message_handler(...);
```

---

## 2. 为什么（Why）

### 2.1 为什么不直接用 Asio 写 WebSocket
WebSocket 协议本身包含：HTTP Upgrade 握手、掩码帧解析、分片消息合并、Ping/Pong 心跳、扩展协商（如 `permessage-deflate` 压缩）、子协议（Sec-WebSocket-Protocol）选择……这些都是**协议状态机**，如果每个项目都在 Asio 裸 socket 上重新实现一遍，既容易出 bug（尤其是帧解析的边界情况和安全问题），也难以维护。websocketpp 把这套状态机标准化、经过大量项目验证，业务代码只需要挂 handler。

### 2.2 为什么选 websocketpp 而不是 Boost.Beast
| 维度 | websocketpp | Boost.Beast |
|---|---|---|
| 依赖 | header-only，可选 Boost 或 standalone asio | 依赖 Boost（Asio + Beast） |
| API 风格 | Handler/回调注册（`set_xxx_handler`），Endpoint-Connection 模型 | Stream-based，贴近 Asio 原生 `async_read`/`async_write` 语义，更适合与协程结合 |
| 成熟度/生态 | 2013 年至今，广泛用于机器人/嵌入式领域（如 **Foxglove**、**rosbridge**） | Boost 官方库，通用 Web 服务生态更广（HTTP + WebSocket 一体） |
| 学习曲线 | 中，模板化 config 略绕 | 中，需要理解 Beast 的 stream 抽象 |

本仓库选择 websocketpp，与它在机器人领域的事实标准地位直接相关（见下节行业案例）。

### 2.3 策略化配置（Policy-based Config）解决了什么
websocketpp 用一个 **config trait 结构体**（模板参数）决定"用什么并发模型、什么日志实现、要不要 TLS、用什么底层 transport"，而不是运行时 if/else 或继承虚函数。好处是**编译期确定行为、零虚函数开销**，代价是模板报错信息比较长。本仓库正是这样做的：

```cpp
// websocket_no_security.hpp —— 明文连接的编译期配置
struct WebSocketNoSecurity : public websocketpp::config::core {
    typedef CallbackLogger alog_type;   // 用自定义日志替换默认日志实现
    typedef CallbackLogger elog_type;
    struct transport_config : public base::transport_config {
        typedef websocketpp::transport::asio::basic_socket::endpoint socket_type; // 明文 socket
    };
    typedef websocketpp::transport::asio::endpoint<transport_config> transport_type;
};
```
`websocket_security.hpp` 则是同样的套路但把 `socket_type` 换成 TLS socket —— **一套 Server、\<ServerConfiguration> 模板代码，靠不同 config 类型在编译期切出明文/TLS 两个版本**，是 C++ 模板策略模式的经典应用。

---

## 3. 怎么做（How）—— 核心概念与 Handler 生命周期

### 3.1 Endpoint / Connection 两层模型
- **Endpoint**（本仓库里的 `server_`）：代表整个服务，管理监听 socket、全局配置、所有连接的集合。
- **Connection**：每个已建立的 TCP 连接对应一个 connection 对象，但业务代码**不直接持有它的裸指针**，而是拿到一个轻量句柄 `connection_hdl`（本质是 `std::weak_ptr`）：

```cpp
using ConnectionHandlePtr = websocketpp::connection_hdl;
auto con = server_.get_con_from_hdl(hdl);   // weak_ptr.lock()，如果连接已关闭这里可能抛异常/为空
```
这样设计是为了**避免悬空指针**：即使连接已经断开、connection 对象已销毁，业务代码持有的 `connection_hdl` 依然是安全的（只是 `lock` 会失败），不会像裸指针那样造成 UAF。

### 3.2 Handler 注册即状态机回调
websocketpp 把 WebSocket 生命周期拆成一串可挂载的 handler，本仓库全部用到了：

```
TCP 连接建立 → tcp_pre_init_handler（拿到裸 socket，设置 TCP_NODELAY）
            → validate_handler（HTTP 握手阶段：License 校验、身份码校验、子协议协商，返回 true/false 决定是否 101）
            → open_handler（握手成功，连接正式建立）
            → message_handler（收到一帧完整消息）
            → close_handler（连接关闭，清理资源）
```

`validate_handler` 是本仓库鉴权体系的核心（对应 [repo memory: sdk_websocket_debug.md](../../../../../SDK_SERVER_ONBOARDING.md) 里记的三要素）：

```cpp
// websocket_server.ipp
inline bool Server<ServerConfiguration>::validateConnection(ConnectionHandlePtr hdl) {
    auto con = server_.get_con_from_hdl(hdl);
    ...
    if (!license_ok) {
        con->set_body(body.dump());
        con->set_status(websocketpp::http::status_code::forbidden);
        return false;                     // 返回 false = 握手失败，HTTP 403
    }
    ...
    if (std::find(subprotocols.begin(), subprotocols.end(), SUPPORTED_SUBPROTOCOL) != subprotocols.end()) {
        con->select_subprotocol(SUPPORTED_SUBPROTOCOL);   // 子协议协商
        return true;                      // 返回 true = 握手成功，HTTP 101
    }
```
这是 websocketpp 的标准套路：**在握手阶段返回 `bool` 就能实现自定义鉴权/白名单/限流**，无需修改协议解析代码。

### 3.3 子协议与扩展协商
- **子协议**（`Sec-WebSocket-Protocol`）：本仓库定义 `SUPPORTED_SUBPROTOCOL = "comm.websocket.v1"`，客户端和服务端必须约定同一个字符串，`con->select_subprotocol(...)` 完成协商。
- **扩展**（如 `permessage_deflate`）：在 config trait 里声明 `permessage_deflate_type`，即可对大消息自动压缩，减少带宽——这是 websocketpp 用同一套 policy 机制暴露的另一个可插拔点。

### 3.4 线程模型：Handler 默认单线程执行
websocketpp 的 handler（包括 `message_handler`）默认在 **Asio 的 io_service 线程**里同步调用（同 Asio 笔记 3.2 节的"不要阻塞 I/O 线程"原则）。本仓库的做法是：**message_handler 里不直接处理业务，而是转发到独立回调队列**：

```cpp
server_.set_message_handler([this](ConnectionHandlePtr hdl, MessagePtr msg) {
    handler_callback_queue_->addCallback([this, hdl, msg]() {
        this->handleMessage(hdl, msg);   // 真正耗时的业务逻辑在这里，脱离 io 线程
    });
});
```
这是把 Asio 笔记里"避免阻塞事件循环"的原则应用到 websocketpp 层的具体工程实践。

---

## 4. 行业优秀案例参考

1. **[ros-foxglove-bridge](https://github.com/foxglove/ros-foxglove-bridge)**：机器人可视化工具 Foxglove Studio 官方的 ROS/ROS2 桥接服务，底层同样用 websocketpp 实现 Foxglove WebSocket 协议。**本仓库的 capability 常量几乎与 Foxglove 协议同名**（`subscribe`/`advertise`/`call_service`/`fetch_asset`/`fetch_asset_chunk` 等，见 [websocket_types.hpp](../comm_server/websocket/include/websocket/websocket_types.hpp)），说明本项目的 WebSocket 协议设计明显参考/对齐了 Foxglove 的 ws-protocol 规范，是学习"如何用 websocketpp 设计一个可扩展的实时数据订阅/发布协议"的最佳对照案例。
2. **[rosbridge_suite](https://github.com/RobotWebTools/rosbridge_suite)**：ROS 生态更早期的 WebSocket 网桥（Python 实现，协议理念类似：`op` 字段区分 `subscribe`/`publish`/`call_service` 等），可以理解本仓库协议设计的"祖先"思路，即使实现语言和库不同。
3. **[websocketpp 自带示例](https://github.com/zaphoyd/websocketpp/tree/master/examples)**：`echo_server`、`chat_server`、`broadcast_server` 是官方最小可运行范例，適合用来单独调试 handler 注册顺序，不需要引入本仓库的鉴权/License 复杂度。
4. **Boost.Beast 的 WebSocket 部分**：作为对照阅读，能体会"回调注册式"（websocketpp）与"stream + 协程"（Beast）两种 API 风格在同一协议上的不同设计取舍。

---

## 5. 常见坑与最佳实践清单

- **`connection_hdl` 只是弱引用**：拿到 hdl 后要先 `get_con_from_hdl` 再用，且要考虑连接可能已经在另一线程被关闭，`get_con_from_hdl` 失败要有兜底处理（本仓库在 `close_handler` 里做资源清理正是为此）。
- **`validate_handler` 里调用 `append_header()` 无效**：本仓库注释明确记录了这个坑——websocketpp 在 `validate_handler` 返回 `false` 时会丢弃自定义状态码相关的自定义头，只能通过 `set_body()` 把错误信息放进 HTTP body，而不是 header。
- **不要在 handler 里做阻塞/耗时操作**：所有 handler 默认跑在 Asio 的 io 线程，重逻辑要像本仓库一样丢到 `CallbackQueue`/线程池。
- **子协议必须双端一致**：忘记在客户端设置 `Sec-WebSocket-Protocol` header 会导致 `validateConnection` 里协商失败、握手被拒绝（见 [repo memory 记录的三要素](../../../../../SDK_SERVER_ONBOARDING.md)）。
- **TLS/明文用不同 config 类型是编译期选择**，不能运行时切换——如果要同时支持 ws:// 和 wss://，需要跑两个 `Server<Config>` 实例（分别用 `WebSocketNoSecurity` / `WebSocketSecurity`）。
- **消息大小限制**：默认 `max_message_size` 只有几 MB，传输大文件/图片前要显式调大（本仓库设为 100MB，见 `server_.set_max_message_size(...)`）。

---
