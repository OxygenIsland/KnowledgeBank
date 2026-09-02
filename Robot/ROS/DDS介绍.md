---
title: "[[DDS介绍]]"
type: Permanent
status: done
Creation Date: 2026-09-02 11:25
tags:
---
## 1. DDS 是什么，解决什么问题
**DDS（Data Distribution Service）是 OMG（Object Management Group）制定的工业级发布/订阅中间件标准**（规范全称 *Data Distribution Service for Real-Time Systems*），最早发布于 2004 年，广泛用于航空航天、国防、金融交易、工业自动化等对**实时性、可靠性、去中心化**要求很高的领域。ROS2 只是 DDS 的众多使用者之一，不是 DDS 的发明者。

### 1.1 DDS 要解决的核心问题
传统的"谁都要连谁"式通信（比如手写 socket、或者 ROS1 靠 Master 撮合）有几个天然缺陷：

| 问题   | 传统方式的困境                   | DDS 的解法                                                 |
| ---- | ------------------------- | ------------------------------------------------------- |
| 发现   | 需要提前知道对方 IP/端口，或依赖中心注册表   | **去中心化自动发现**：参与者自己在网络上广播/监听                             |
| 单点故障 | 中心 Broker/Master 挂了，全系统瘫痪 | 没有 Broker；任意节点加入/退出都不影响其他人通信                            |
| 服务质量 | "尽力而为"和"绝对可靠"二选一，无法精细控制   | **QoS 策略**：可靠性、历史深度、超时、存活检测等均可配置                        |
| 强类型  | 二进制协议手搓，容易解析出错            | **IDL（Interface Definition Language）** 定义数据类型，自动生成序列化代码 |
| 扩展性  | 中心节点容易成为吞吐瓶颈              | 点对点/组播直连，理论上可扩展到成千上万节点                                  |

一句话理解：**DDS 提供的是"全局数据空间"的抽象**——发布者把数据写入一个逻辑上的全局共享空间（按 Topic 命名），订阅者从这个空间里按需读取，彼此不需要知道对方的网络地址，中间件负责发现、路由、过滤、质量保证等所有脏活。

### 1.2 DDS 规范的两层结构
OMG 把 DDS 拆成两个独立可替换的规范，这也是"发现层"能在不同厂商实现间互操作的原因：
```text
┌────────────────────────────────────────┐
│  DCPS (Data-Centric Publish-Subscribe) │  ← 编程模型：Topic/DataWriter/DataReader/QoS
├────────────────────────────────────────┤
│  RTPS (Real-Time Publish-Subscribe)    │  ← 线上协议：怎么在网络上发现彼此、传数据
└────────────────────────────────────────┘
```

- **DCPS** 是应用层看到的 API 模型（本文第 2 节）；
- **RTPS**（`DDSI-RTPS`）是具体的网络传输协议规范，规定了报文格式、发现协议细节，使得**不同厂商的 DDS 实现只要都遵循 RTPS，就可以互相通信**（本文第 5 节）。

## 2. 核心概念模型：以数据为中心的发布订阅（DCPS）
DDS 官方叫这套模型 **DCPS（Data-Centric Publish-Subscribe）**，强调"以数据为中心"——关注的是"数据本身长什么样、有什么质量要求"，而不是"谁给谁发了什么消息"。
### 2.1 六个核心实体
```text
DomainParticipant  ← 一个进程接入某个 Domain 的入口（通常一个进程一个）
      │
      ├── Publisher   （发布侧的容器，管理多个 DataWriter）
      │      └── DataWriter  ← 真正"写数据"的对象，绑定一个 Topic
      │
      ├── Subscriber   （订阅侧的容器，管理多个 DataReader）
      │      └── DataReader  ← 真正"读数据"的对象，绑定一个 Topic
      │
      └── Topic        ← 数据的"身份"：名字 + 类型（由 IDL 定义）
```

| 实体                    | 职责                                              | ROS2 里的对应物                                                  |
| --------------------- | ----------------------------------------------- | ----------------------------------------------------------- |
| **DomainParticipant** | 加入某个 Domain，持有该进程在这个 Domain 里的全部资源              | 大致对应一个 ROS2 进程里的 `Context`（同进程多个节点可共享一个 Participant，见第 9 节） |
| **Topic**             | 数据的名字 + 类型定义，是发布者和订阅者"对上暗号"的依据                  | ROS2 的 topic 名 + msg 类型                                     |
| **Publisher**         | DataWriter 的工厂/容器，可以对一组 DataWriter 统一设置 QoS     | rclcpp 中较少直接暴露，多数场景一个 publisher 对应一个 DataWriter             |
| **DataWriter**        | 真正调用 `write()` 发送数据的对象，一个 DataWriter 绑定一个 Topic | `rclcpp::Publisher`                                         |
| **Subscriber**        | DataReader 的工厂/容器                               | 同 Publisher                                                 |
| **DataReader**        | 真正 `read()`/`take()` 数据、触发监听回调的对象               | `rclcpp::Subscription`                                      |

### 2.2 匹配（Matching）的本质
发布者和订阅者能否"配对"通信，取决于三件事同时成立：
1. **Topic 名字相同**；
2. **数据类型兼容**（理想情况完全一致，也支持类型演进兼容性）；
3. **QoS 兼容**（发布者提供的 ≥ 订阅者要求的，见第 6 节）。

三者都满足时，中间件会自动建立连接——这个过程叫 **匹配（Match）**，完全由中间件在后台完成，应用代码不需要手写任何"连接"逻辑。

### 2.3 监听器与条件（Listener / Condition / WaitSet）
DDS 提供两种"我怎么知道有新数据/有新事件"的方式（ROS2 的 Executor 内部就是基于这套机制实现的，参见 [ROS2核心原理与开发笔记.md 第 3 节](ROS2核心原理与开发笔记.md#3-执行模型executor-与线程)）：
- **Listener（监听器/回调式）**：注册回调函数，事件发生时中间件主动调用；
- **WaitSet + Condition（轮询/阻塞等待式）**：应用主动调用 `wait()`，等待关心的条件（比如"某个 DataReader 有新数据"）被满足。
ROS2 的 Executor 本质上是"帮你管理了一个 WaitSet，帮你把不同实体的 Condition 都注册进去，然后循环 `wait()`+ 分发回调"。

## 3. Domain 与 DomainParticipant：网络级别的隔离
**Domain（域）** 是 DDS 里最外层的隔离单位，用一个整数 **Domain ID** 标识：
- 同一个 Domain ID 里的 Participant 才能互相发现、通信；
- 不同 Domain ID 的系统即使在同一物理网络上，也**完全互不感知**（发现协议会按 Domain ID 计算不同的组播地址/端口，天然隔离）。

ROS2 里对应环境变量 `ROS_DOMAIN_ID`（默认 0，合法范围通常是 0~232，具体上限取决于底层 DDS 实现的端口分配公式）：
```bash
export ROS_DOMAIN_ID=42   # 同一台机器/网络上跑多套独立的 ROS2 系统，互不干扰
```

**典型用途**：同一局域网里有多台机器人，每台机器人的软件栈用不同 `ROS_DOMAIN_ID`彼此隔离，避免互相收到对方的 topic 数据；或者本地开发时避免和同网络里其他人的ROS2 进程"串线"。

> **端口计算公式（RTPS 标准公式）**：DDS 的发现端口由 `PB + DG * domainId + d0`这样的公式算出（不同实现常量略有差异），这也是为什么 Domain ID 太大可能会算出超出合法范围的端口号而报错。

## 4. 发现机制：没有中心节点，怎么互相找到对方
这是 DDS 相对传统方案最核心的能力，分两阶段：

### 4.1 SPDP（Simple Participant Discovery Protocol）—— 发现"有哪些参与者"
- 每个 `DomainParticipant` 启动后，**周期性地通过组播（multicast）广播自己的存在**（包含自己的 GUID、监听地址、支持的协议版本等元数据）；
- 同时监听组播地址，收集其他 Participant 广播的信息；
- 这一步只关心"网络里有哪些参与者"，还不涉及具体 Topic。

### 4.2 SEDP（Simple Endpoint Discovery Protocol）—— 发现"每个参与者有哪些读写端点"
- 两个 Participant 通过 SPDP 互相认识后，会**建立一条内部通信通道**，交换各自持有的 DataWriter/DataReader 列表（含 Topic 名、类型、QoS）；
- 中间件对比双方的 Topic 名 + 类型 + QoS，凡是能匹配上的，就在底层建立真正的数据传输通道（Match 成功）。
```text
Participant A 启动
   │  组播广播"我在这里"(SPDP)
   ▼
Participant B 收到广播，回应自己的信息(SPDP)
   │
   ▼
A、B 互相知道对方存在 → 建立点对点发现通道
   │  交换各自的 DataWriter/DataReader 清单(SEDP)
   ▼
比对 Topic 名 + 类型 + QoS → 匹配成功的收发端点之间建立数据通道
   │
   ▼
真正的用户数据开始点对点/组播传输(用户数据不再走发现阶段的组播)
```

### 4.3 为什么"发现是组播"这件事很重要（排坑关键点）
- 默认发现依赖 **UDP 组播**，如果所在网络环境**禁用组播**（常见于云主机、容器跨 host 网络、某些企业 Wi-Fi），节点之间会发现不了彼此，且**没有明显报错**；

- 参与者数量越多，发现阶段的广播流量呈**平方级增长**（每个新节点都要和所有已有节点交换信息），这是大规模系统（几十上百个节点）常见的"启动慢、CPU 占用高"的根因——解决方案见第 7.3 节的 **Discovery Server**。

## 5. RTPS：DDS 的线上协议，互操作性的关键
**RTPS（Real-Time Publish-Subscribe Protocol）** 是 OMG 定义的另一份独立规范（`DDSI-RTPS`），规定了 DDS 概念在网络上具体怎么编码传输：
- 报文格式（Header + 一串 Submessage）；
- 发现协议的具体行为（即上面的 SPDP/SEDP）；
- 可靠传输的心跳（Heartbeat）/确认（ACKNACK）机制。

**关键意义**：只要两个 DDS 实现都遵循 RTPS 规范，**即使是不同厂商的实现，也能直接互通**（比如 Fast DDS 的发布者和 Cyclone DDS 的订阅者可以互相通信）。这也是 ROS2能在 `rmw` 层做到"换厂商实现、上层代码不用改"的底层保证——各家 RMW 适配层都是把DDS/RTPS 的能力包了一层统一接口，而不是各自发明协议。

> 排查网络问题时，如果怀疑是协议层的收发问题，可以用 **Wireshark** 抓包（它自带RTPS 协议解析插件），直接看到 SPDP/SEDP 报文和心跳/ACKNACK 交互过程，比日志更直观。

## 6. QoS 体系深入：策略、兼容性、Offer-Request 模型

[[ROS2 核心概念#6. QoS（服务质量）]]已经讲了QoS 的常用策略和预置 Profile，这里补充 **DDS 原生视角** 下更完整的框架。

### 6.1 完整的 QoS 策略清单（DCPS 规范定义）
| 策略                                        | 作用对象                        | 含义                                                                                          |
| ----------------------------------------- | --------------------------- | ------------------------------------------------------------------------------------------- |
| `RELIABILITY`                             | Topic/DataWriter/DataReader | Best Effort（尽力而为）vs Reliable（可靠，会重传直到确认）                                                    |
| `DURABILITY`                              | 同上                          | Volatile（不管迟到者）/ Transient Local（本地缓存补发）/ Transient / Persistent（后两者需要独立的持久化服务，较少用）         |
| `HISTORY`                                 | 同上                          | Keep Last(N) / Keep All                                                                     |
| `RESOURCE_LIMITS`                         | 同上                          | 限制最大可缓存的样本数/实例数，防止内存无限增长                                                                    |
| `DEADLINE`                                | 同上                          | 期望的最大发布/接收间隔，超时会触发 `on_offered/requested_deadline_missed`                                   |
| `LATENCY_BUDGET`                          | 同上                          | 提示中间件"可以容忍多少延迟来做批量优化"，不是硬约束                                                                 |
| `LIVELINESS`                              | 同上                          | Automatic（中间件自动续约）/ Manual by Participant / Manual by Topic，用于判断对端是否还存活                     |
| `LIFESPAN`                                | DataWriter                  | 数据从发布起超过多久视为过期，过期数据不会再被读取                                                                   |
| `OWNERSHIP`                               | 同上                          | Shared（多个 Writer 可以同时写同一个 Instance）/ Exclusive（只有 Ownership Strength 最高的 Writer 生效，常用于主备切换） |
| `OWNERSHIP_STRENGTH`                      | DataWriter                  | 配合 Exclusive Ownership 使用的优先级数值                                                             |
| `DESTINATION_ORDER`                       | 同上                          | 按接收时间戳还是按源发送时间戳排序数据                                                                         |
| `PARTITION`                               | Publisher/Subscriber        | 逻辑分区，即使 Topic 名相同，不同 Partition 也不会匹配（类似"软隔离"，比 Domain 更轻量）                                  |
| `TRANSPORT_PRIORITY`                      | DataWriter                  | 提示底层传输优先级（是否生效取决于具体实现/网络支持）                                                                 |
| `USER_DATA` / `TOPIC_DATA` / `GROUP_DATA` | 各实体                         | 附加的自定义元数据，随发现协议一起交换，不影响匹配逻辑                                                                 |

> ROS2 目前只暴露了其中最常用的一部分（History/Depth/Reliability/Durability/
> Deadline/Lifespan/Liveliness），`OWNERSHIP`/`PARTITION` 等策略需要绕开 `rclcpp`
> 直接操作底层 DDS API（不同 RMW 实现方式不同），属于进阶用法。

### 6.2 Offer-Request 兼容性模型
DDS 官方称之为 **"Request vs Offered"（RxO）模型**：
- **DataWriter "提供"（Offer）** 一组 QoS，代表"我能保证达到这个质量水平"；
- **DataReader "请求"（Request）** 一组 QoS，代表"我最低需要这个质量水平"；
- 只有 **Offered ≥ Requested**（按每个策略各自的偏序关系）时才能匹配成功。

对于多数策略（Reliability、Durability、Deadline...），这个"≥"有明确定义：Reliable ≥ Best Effort，Transient Local ≥ Volatile，更短的 Deadline ≥ 更长的 Deadline。

**不兼容时的行为是静默的**：不会报错、不会抛异常，DataWriter/DataReader 各自都能正常创建，只是永远不会建立匹配、永远收不到数据——这是 DDS/ROS2 新手最容易踩的坑，必须主动用工具查（见第 10 节）。

  
### 6.3 QoS 事件通知

除了"能不能匹配"，DDS 还会在运行时持续上报一系列 QoS 相关事件（ROS2 里对应`rclcpp` 的 `on_xxx_event` 回调，或者可以订阅特殊的 `/parameter_events` 之外的`Status` 信息）：
- `OFFERED_DEADLINE_MISSED` / `REQUESTED_DEADLINE_MISSED`：超过 Deadline 没发布/没收到；
- `LIVELINESS_LOST` / `LIVELINESS_CHANGED`：对端存活状态变化；
- `OFFERED_INCOMPATIBLE_QOS` / `REQUESTED_INCOMPATIBLE_QOS`：**QoS 不兼容时唯一会产生的显式信号**——如果怀疑收不到消息是 QoS 不匹配，代码里可以主动监听这个Status 事件，而不是干等日志。

## 7. 传输层：UDP、共享内存、Discovery Server
### 7.1 默认传输：UDP（单播 + 组播）
- 发现阶段（SPDP）依赖组播；
- 用户数据默认走 UDP 单播（一对一）或组播（一对多，同 Topic 多个订阅者时可以复用一份网络流量）；
- 优点是跨主机天然可用；缺点是同机进程间也要走一遍网络栈序列化/内核收发。

### 7.2 共享内存传输（Shared Memory Transport）
主流实现（Fast DDS、Cyclone DDS 等）都支持**同一台机器上的进程间通信自动走共享内存**，跳过网络协议栈序列化，显著降低延迟、提高吞吐——这对同机多节点的机器人系统（大多数本仓库场景）非常关键。通常是**自动生效**的（只要传输层配置里没有禁用），应用代码不需要感知。

### 7.3 Discovery Server（应对大规模系统的发现风暴）
默认的 SPDP/SEDP 是"全对全（all-to-all）"广播式发现，节点数一多，发现流量和 CPU开销会明显上升，启动也会变慢。多数主流实现提供了**发现服务器（Discovery Server）**模式作为替代方案：
```text
默认模式（Simple Discovery）：
   N 个节点  →  两两互相组播/交换发现信息  →  O(N²) 流量

Discovery Server 模式：
   N 个节点  →  只和 1（或几个）Discovery Server 交换信息  →  O(N) 流量
              Server 之间/Server 与客户端之间用普通 TCP/UDP 单播，不依赖组播

```
好处：不依赖组播（适合组播受限的云环境/容器网络），且发现流量线性增长。
代价：Discovery Server 本身是一个新的"需要保持在线的组件"，需要额外部署与监控（不同于 DDS 一贯"去中心化"的理念，是一种为规模化做的工程妥协）。

Fast DDS 的具体命令（本仓库使用 Fast DDS，见第 11 节）：
```bash
# 启动一个独立的 discovery server 进程（监听 11811 端口）
fastdds discovery -i 0

# 客户端进程设置环境变量，指向 discovery server 而不是用组播发现
export ROS_DISCOVERY_SERVER="127.0.0.1:11811"
```

## 8. 常见 DDS 实现对比

| 实现                         | 开源协议            | 特点                                                                                   | ROS2 对应 RMW 包                     |
| -------------------------- | --------------- | ------------------------------------------------------------------------------------ | --------------------------------- |
| **eProsima Fast DDS**      | Apache 2.0      | ROS2 的**默认**实现（Humble/Jazzy 等主流发行版），功能全面，自带 Discovery Server、Shared Memory Transport | `rmw_fastrtps_cpp`（本仓库使用，见第 11 节） |
| **Eclipse Cyclone DDS**    | EPL/EDL         | 轻量、代码简洁，性能与内存占用口碑较好，部分发行版可选默认                                                        | `rmw_cyclonedds_cpp`              |
| **RTI Connext DDS**        | 商业授权（有免费研究/评估版） | 工业界最老牌的实现之一，工具链成熟（如 RTI Admin Console），常见于国防/航空场景                                    | `rmw_connextdds`                  |
| **GurumNetworks GurumDDS** | 商业              | 较少见，主要面向特定行业客户                                                                       | `rmw_gurumdds_cpp`                |
| **Zenoh**（非严格意义 DDS，兼容层）   | Apache 2.0      | 新一代"以数据为中心"协议，定位是替代/补充 DDS，尤其擅长广域网/低带宽/大规模场景                                         | `rmw_zenoh_cpp`（较新，Jazzy 之后逐渐流行）  |
  
**切换实现的方式**（编译期已经装好对应的 rmw 包的前提下）：
```bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp   # 不用重新编译业务代码，运行时切换
ros2 run my_package my_node
```
> 编译期常量 `DEFAULT_RMW_IMPLEMENTATION` 只是"没设置环境变量时用哪个默认值"，本仓库 `compile_commands.json` 里能看到 `-DDEFAULT_RMW_IMPLEMENTATION=rmw_fastrtps_cpp`，说明构建时选择了 Fast DDS 作为默认 RMW。

## 9. ROS2 如何映射到 DDS 概念

| ROS2 概念 | DDS 概念 | 备注 |
|---|---|---|
| `rclcpp::Node` | 不直接等价于任何 DDS 实体 | 节点是 ROS2 客户端库层面的抽象，多个节点可能共享同一个底层 `DomainParticipant`（取决于 RMW 实现是否做了合并优化） |
| `Context`（`rclcpp::init()` 创建） | 通常对应一个 `DomainParticipant` | 一个进程可以有多个 Context，各自独立发现 |
| Topic 名 `/foo` | DDS Topic 名 | ROS2 会在真正的 DDS 层给 topic 名加前缀，如 `rt/foo`（"ROS Topic"），service 用 `rq/`/`rr/` 前缀区分请求/响应通道 |
| `.msg` 类型 | DDS 类型（通过 IDL 生成） | `rosidl` 工具链把 `.msg`/`.srv`/`.action` 转成对应的 C++/Python 结构体 + IDL 描述，供 DDS 序列化用 |
| `rclcpp::Publisher` | `DataWriter` | 一对一封装 |
| `rclcpp::Subscription` | `DataReader` | 一对一封装 |
| `ros2 topic pub/echo` | 新建一个临时 DataWriter/DataReader | 本质就是命令行版的发布者/订阅者，不会干扰系统里已有的实体 |
| Service | 两个 Topic（请求 + 响应）伪装成的 RPC | `rq/xxx/_request` 和 `rr/xxx/_reply`，本质仍是发布订阅，只是客户端库帮你做了"匹配请求 ID、等待对应响应"的封装 |
| `ROS_DOMAIN_ID` | DDS Domain ID | 见第 3 节 |

## 10. 排查工具与常见坑
### 10.1 常见坑速查表
| 现象 | 大概率原因 | 排查方式 |
|---|---|---|
| 两个节点都在跑，但收不到彼此的消息，无任何报错 | QoS 不兼容（Reliability/Durability 不匹配） | `ros2 topic info /xxx --verbose` 对比双方 QoS |
| 局域网内两台机器互相发现不了 | 组播被网络/防火墙/云安全组屏蔽 | 换成 Discovery Server 模式，或检查网络是否允许组播 |
| 容器内 ROS2 节点和宿主机/其他容器发现不了彼此 | Docker 默认 bridge 网络不转发组播 | 用 `--network host`，或配置 Discovery Server，或用支持组播的自定义网络 |
| 同一网络里多个人的 ROS2 系统"串台"（收到别人的 topic） | `ROS_DOMAIN_ID` 冲突（都用默认的 0） | 每个人/每套系统设置不同的 `ROS_DOMAIN_ID` |
| 节点数一多，启动特别慢、CPU 占用高 | Simple Discovery 的 O(N²) 发现流量 | 切换到 Discovery Server 模式（见第 7.3 节） |
| 换了台机器/换了个网络环境，某些历史遗留 launch 突然收不到消息了 | 该网络环境组播规则和之前不同 | 同上，且优先怀疑网络环境变化而不是代码变化 |

### 10.2 排查工具箱
```console
# 1. ROS2 层面：看两端实际协商出来的 QoS 是否兼容（最常用）
$ ros2 topic info /some_topic --verbose
$ ros2 service info /some_service --verbose

# 2. 环境自检
$ ros2 doctor                       # 检查 ROS2 环境常见配置问题
$ ros2 doctor --report              # 更详细的报告，含网络接口信息

# 3. 图形化拓扑
$ rqt_graph                         # 看节点-topic 连接关系是否符合预期
  
# 4. Fast DDS 专属：查看/管理 discovery server
$ fastdds discovery -i 0
$ fastdds --help
  
# 5. 抓包分析（协议层终极手段）
$ wireshark                         # 自带 RTPS dissector，可直接看 SPDP/SEDP/心跳报文

# 6. 环境变量自检（常见需要确认的几个）
$ echo $ROS_DOMAIN_ID
$ echo $RMW_IMPLEMENTATION
$ echo $ROS_DISCOVERY_SERVER
$ echo $ROS_LOCALHOST_ONLY          # =1 时只在本机回环网卡通信，常用于隔离/调试
```

### 10.3 `ROS_LOCALHOST_ONLY`
调试时如果确定不需要跨机通信，可以设置 `export ROS_LOCALHOST_ONLY=1`，强制发现和数据流量都走回环网卡（`127.0.0.1`），避免被同网络里其他机器的同 Domain 系统干扰，也能减少不必要的组播流量。

## 11. 与本仓库的对照

- 本仓库编译时选择的默认 RMW 是 **`rmw_fastrtps_cpp`**（即 eProsima Fast DDS）， 可以在 [compile_commands.json](../../../../../compile_commands.json) 里搜到`-DDEFAULT_RMW_IMPLEMENTATION=rmw_fastrtps_cpp` 确认；

- `overlay_ws`/`ros2_ws` 的构建日志（`log/latest_build/logger_all.log`）里能看到`Using configuration from '.../fastdds.meta'`，说明 colcon 元数据层面也是按 Fast DDS配置的；

- 因此第 7.3 节的 Discovery Server 命令、第 8 节 Fast DDS 的特性（共享内存传输、`fastdds` CLI 工具）都可以直接在本仓库环境里使用；

- `DaystarServiceNode`（继承 `LifecycleNode`，见 [[ROS2 核心概念#13. 与本仓库 daystar_api 的对照]]）和 `Navigation` 单例各自的 Executor，最终都跑在**同一个 Fast DDS DomainParticipant网络行为**之上——即它们各自的发现、QoS 匹配、传输方式都遵循本文讲的这套机制，只是 ROS2 客户端库把这些细节都封装掉了。

- 若排查"服务/话题收不到数据"一类问题，优先按第 10 节的顺序：先查 QoS（`ros2 topic info --verbose`），再查网络/Domain 隔离，最后才考虑抓包。