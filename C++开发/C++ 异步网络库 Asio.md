---
title: "[[C++ 异步网络库 Asio]]"
type: Permanent
status: done
Creation Date: 2026-08-20 13:51
tags:
---
## 1. 是什么（What）
**Asio** 是一个跨平台的 C++ 网络 / 底层 I/O 编程库，提供统一的**异步模型**来处理 socket、定时器、串口、信号等。

- **标准库 Asio (standalone asio)**：Chris Kohlhoff 维护，只依赖 C++ 标准库，[非 Boost 依赖](https://think-async.com/Asio/)。
- **Boost.Asio**：同一套代码，打包进 Boost，接口几乎一致（命名空间 `boost::asio` vs `asio`）。
- 已经标准化提案为 **C++ Networking TS (N4771)**，是 C++23/26 网络库的技术原型。

一句话定位：**Asio 是"事件循环 + 异步 I/O 原语"的基础设施，本身不是 HTTP/WebSocket 框架**，而是被上层协议库（Beast、websocketpp、gRPC、Drogon 等）用作 I/O 引擎。

本仓库中的证据（`comm` 模块）：

```cpp
// overlay_ws/src/sdk_server/comm/comm_server/websocket/include/websocket/websocket_server.ipp
server_.init_asio(ec);                     // websocketpp 内部持有一个 asio::io_service
server_.set_tcp_pre_init_handler(...);      // 拿到裸 socket 设置 TCP_NODELAY
server_.get_con_from_hdl(hdl)->get_raw_socket().set_option(Tcp::no_delay(true), ec);
```

[websocketpp](https://github.com/zaphoyd/websocketpp)（`websocketpp::config::asio` / `asio_no_tls`）就是**直接构建在 Asio 之上**的协议层库：它自己不写 epoll/IOCP 代码，全部委托给 Asio 的 `io_service`，自己只负责 WebSocket 握手、帧解析、TLS 封装。这是"库分层"思想的典型案例。

## 2. 为什么（Why）

### 2.1 解决什么问题
传统"每连接一个线程"（thread-per-connection）模型在高并发下有明显瓶颈：
- 线程创建/切换开销大，C10K 问题无法回避线程调度和内存开销（每线程 MB 级栈）。
- 阻塞 I/O 导致线程大部分时间在等待网络数据。

### 2.2 异步 I/O 的核心思路
- **Reactor 模式**（Linux/macOS：epoll/kqueue）：内核通知"可读/可写"，用户态发起非阻塞调用。
- **Proactor 模式**（Windows：IOCP）：用户态发起异步操作，内核完成后通知"已完成"。

Asio 的巧妙之处：**对外统一暴露 Proactor 风格的 API**（`async_read`、`async_write` 都是"发起操作 + 完成回调"），底层在 Linux 用 epoll 模拟出 Proactor 语义，在 Windows 直接用原生 IOCP。这样业务代码**一次编写、跨平台**，不用关心底层是 reactor 还是 proactor。

### 2.3 相比其他方案的取舍
| 方案 | 代表 | 特点 |
|---|---|---|
| Reactor 手写（裸 epoll） | muduo（陈硕） | "one loop per thread"，非常轻量但需要自己管理事件分发、几乎没有跨平台能力 |
| Asio（Proactor 封装） | Boost.Asio / standalone asio | 跨平台统一、异步组合操作丰富、生态成熟（Beast/websocketpp 依赖它） |
| Actor / Share-nothing per-core | Seastar（ScyllaDB） | 极致性能，每核一个 reactor + 无锁，学习成本高，生态窄 |
| libuv | Node.js | C 语言、事件循环 + 线程池模拟异步文件 I/O，回调地狱问题类似 |

Asio 胜在"生态 + 跨平台 + 组合能力"，所以成为 C++ 网络库事实标准，被 Beast（官方 HTTP/WebSocket）、websocketpp（本仓库用的库）、gRPC（部分）、Drogon 等广泛复用。

---

## 3. 怎么做（How）—— 核心概念与执行模型

### 3.1 `io_context`：事件循环的心脏
```cpp
asio::io_context io;
io.run();  // 阻塞，不断从内核取就绪事件并调用对应的 completion handler
```
- 所有异步操作（`async_*`）本质上是：**"注册一个操作 + 一个回调"**，操作完成后由 `io_context::run()` 所在线程调用回调。
- 没有事件时 `run()` 会阻塞休眠（epoll_wait），不会忙轮询。

### 3.2 Completion Handler（完成处理器）
```cpp
socket.async_read_some(asio::buffer(data),
    [](std::error_code ec, std::size_t n) {
        // I/O 线程（即调用 io.run() 的线程）里执行
    });
```
所有异步操作都遵循同一约定：`void(error_code, ...)` 签名的回调，在 `io_context::run()` 的线程里被调用——**这就是为什么业务逻辑不能在这里做耗时/阻塞操作**，否则会卡住整个事件循环。

### 3.3 多线程模型：`strand` 而不是裸锁
如果多个线程同时调用 `io.run()`（提高吞吐），同一个连接的多个 handler 可能被不同线程并发执行 → 数据竞争。
Asio 的答案是 **`strand`**：保证被同一个 strand 包裹的 handler **串行执行**（哪怕在不同线程上跑），既拿到多线程吞吐，又拿到单线程一样的"隐式互斥"，避免显式加锁。

```cpp
asio::strand<asio::io_context::executor_type> strand(io.get_executor());
asio::post(strand, [](){ /* 与同 strand 上的其他任务互斥 */ });
```

### 3.4 C++20 协程：告别回调地狱
早期 Asio 只有回调风格，容易写成"回调套回调"。C++20 后 Asio 支持 `asio::awaitable` + `co_spawn`，把异步代码写成"看起来同步"的顺序代码：

```cpp
asio::awaitable<void> echo(tcp::socket socket) {
    char data[1024];
    for (;;) {
        std::size_t n = co_await socket.async_read_some(asio::buffer(data), asio::use_awaitable);
        co_await asio::async_write(socket, asio::buffer(data, n), asio::use_awaitable);
    }
}
asio::co_spawn(io, echo(std::move(socket)), asio::detached);
```
这是目前业界推荐的现代写法（Boost 1.74+ / standalone asio 均支持），显著降低了嵌套回调的复杂度。

### 3.5 连接生命周期管理：`shared_from_this`
异步操作发起后对象不能立刻销毁（回调还没触发），行业惯例是让连接类继承 `std::enable_shared_from_this`，每次发起异步操作时用 `shared_from_this()` 延长生命周期到回调执行完毕：
```cpp
class Session : public std::enable_shared_from_this<Session> {
    void do_read() {
        auto self = shared_from_this();
        socket_.async_read_some(buf_, [this, self](auto ec, auto n){ ... });
    }
};
```

---

## 4. 行业优秀案例参考

1. **[Boost.Beast](https://github.com/boostorg/beast)**（Vinnie Falco）：官方推荐的 HTTP/WebSocket 库，直接基于 Boost.Asio 的 stream 概念构建，是"如何在 Asio 之上写协议层"的标准范本。
2. **[websocketpp](https://github.com/zaphoyd/websocketpp)**：本仓库 `comm_server/websocket` 模块直接使用的库，通过 `websocketpp::config::asio` 把 Asio 的 `io_service` 包装成自己的 endpoint，验证了"协议库 + Asio 传输层"的分层设计——值得直接阅读它的 `transport/asio` 目录作为学习范本。
3. **[muduo](https://github.com/chenshuo/muduo)**（陈硕）：虽不基于 Asio，但其"one loop per thread + 非阻塞 I/O + Reactor"设计与 Asio 的多 `io_context` 线程模型思想同源，中文资料丰富，适合对照理解 Reactor 原理。
4. **[Seastar](https://github.com/scylladb/seastar)**（ScyllaDB）：share-nothing、每核一个 reactor，代表异步框架的性能极限，可用来理解 Asio 多线程 `io_context` 模型与"每核一个 io_context"模式的取舍。
5. **本仓库实践**（`overlay_ws/src/sdk_server/comm`）：
   - 用 `set_tcp_pre_init_handler` 在 Asio 建连阶段直接操作裸 socket（设置 `TCP_NODELAY`），是"在协议库暴露的钩子里插入 Asio 原生调用"的实际例子。
   - `set_message_handler` 中没有直接处理消息，而是 `handler_callback_queue_->addCallback(...)` 扔到独立的回调队列/线程池处理——这正是 **3.2 节提到的"不要阻塞 io 线程"** 原则的工程化落地：把耗时的业务逻辑（License 校验、消息分发）从 Asio 的 I/O 线程转移到工作线程，避免拖慢事件循环吞吐。

---

## 5. 常见坑与最佳实践清单

- **不要在 completion handler 里做阻塞调用**（文件 IO、加锁等待、sleep），否则整个 `io_context::run()` 线程被卡死，其他连接都会延迟。→ 参考本仓库用独立 `CallbackQueue` 卸载耗时逻辑。
- **多线程 `io.run()` 时必须用 `strand` 或显式锁保护共享状态**，否则同一连接的读写回调可能被并发线程同时执行。
- **异步操作发起后立即返回，对象生命周期要用 `shared_from_this()` 管理**，避免回调触发时对象已析构（悬空引用是 Asio 新手最常见 crash 来源）。
- **`error_code` 一定要检查**：`operation_aborted`（连接被主动关闭/析构触发）是正常路径，不要当异常处理。
- **buffer 生命周期**：`asio::buffer()` 只是视图，不持有数据所有权，异步操作完成前底层 buffer 不能被析构或 resize。
- **优先用协程 (`awaitable` + `co_spawn`)** 写新代码，只有维护旧回调风格代码时才继续用回调链。

