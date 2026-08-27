---
title: "[[LicenseComponent]]"
type: Permanent
status: done
Creation Date: 2026-08-25 13:56
tags:
---
## 调用流程
1. 程序启动时，`main.cpp:110-140` 里创建 `RobotServiceMiddlewareImpl`：
    - `std::make_unique<RobotServiceMiddlewareImpl>(RobotType::IS/MC/MX/MX_DVT)`
2. 在构造函数里，`robot_service_impl.cpp:28-66` 执行：
    - `license_component_ = std::make_shared<LicenseComponent>();`
3. 这一步会触发 `LicenseComponent` 的构造函数，从而进入license相关的环节

## License 逻辑总览
下面按“入口 → 初始化 → 状态判定 → 文件/网络同步 → 对外 API”这条链路来梳理，核心代码分布在：
- 组件接口： LicenseComponent.hpp
- 业务实现： LicenseComponent.cpp
- 核心判定与远程同步： license_manager.cpp
- gRPC/GenericCall 入口： robot_service_impl.cpp:1962-2183

### 1. 整体结构
它分成 3 层：
1. `robot_service_impl.cpp`
    - 负责对外暴露 GenericCall 的方法
    - 识别 methodName，如 `CheckLicenseStatus`、`SetLicenseFile`、`GetSystemSN`、`RequestTemporaryLicense`
2. `LicenseComponent`
    - 是 SDK Server 对 license 的门面封装
    - 统一做文件写入、状态查询、SN 获取、临时 license 请求
    - 还会把授权状态同步给 RPS（`rps::SetLicenseValid`）
3. `LicenseManager`
    - 真正的 license 业务逻辑层
    - 读永久/临时 license 文件
    - 校验 RSA 签名和 SN/过期时间
    - 自动请求临时 license
    - 远程同步 license 到服务器
---
### 2. 组件初始化时做了什么
在 LicenseComponent.cpp:13-68 的构造函数里，启动流程是：
- 创建 license_mgr_
- 立刻调用一次 license_mgr_.check_status()
- 根据状态判断是否有效：
	- TEMPORARY_LICENSE
	- PERMANENT_LICENSE
- 设置 last_license_valid_state_
- 调用 rps::SetLicenseValid(1/0)
- 启动后台线程 license_valid_check_worker()
也就是说，启动时就会主动“先校验一次”。如果本机 license 没有或失效，RPS 侧会立刻收到 0，提醒上层机器人端授权无效。

这个后台线程会运行 2 分钟，每 3 秒检查一次，持续同步授权状态给 RPS。是一个“自愈/同步”线程，而不是核心裁决逻辑。