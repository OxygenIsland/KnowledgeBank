---
title: "[[SYSA_SDK_Server]]"
type: Permanent
status: ing
Creation Date: 2026-06-11 15:37
tags:
---
## 概述 (Overview)
Robot SDK Server 是一个中间件服务，为控制和监控六足机器人 (IS) 和四足机器人 (MC/MX) 提供了统一的 gRPC 接口。它抽象了底层硬件差异，并为机器人应用程序提供了一致的 API。
### 主要特性
- 多平台支持：支持 x86_64、ARM (Jetson) 和 Rockchip 架构
- 机器人类型兼容：兼容六足 (IS) 和四足 (MC/MX) 机器人
- 基于 gRPC 的 API：高性能、跨语言通信
- 模块化架构：分离了机器人控制、RPS等服务
- 实时能力：低延迟的机器人控制和状态监控
### 支持的服务
- MCS (运动控制服务)：机器人移动、姿态和场景管理
- RPS (机器人外设服务)：电池电量、灯效板、风扇
- OTA (OTA升级)：远程固件更新
- SNMP：网络设备监控
- Logging：系统诊断和调试
## SDK Server 架构

### 构建命令
```
./build.sh [ARCH] [ROBOT_TYPE]
```
### 参数
**\[ARCH] 目标架构：**
- `x86_64`﻿  x86 64位架构
- `arm﻿`    ARM 架构
- `rk﻿`    Rockchip 架构
**\[ROBOT_TYPE] 机器人类型：**
- `IS﻿`   Hexapod robot (六足机器人)
- `MC/MX﻿`  Quadruped robot (四足机器人)
### 示例
```
# 为 Rockchip 架构构建六足机器人版本
./build.sh rk IS
# 为 ARM(Jetson) 架构构建四足机器人版本
./build.sh arm MC
# 为 x86_64 架构构建六足机器人版本
./build.sh x86_64 IS
```
## 构建产出 (Build Output)
编译成功后，将生成以下文件：
**可执行文件**
- robot_service_middleware  主可执行文件
- 位置：/home/daystarm/systema-sdk-server/﻿

**依赖库**
- libmcs_client_lib.so MCS 客户端库
- librps_api.so RPS API 库

**位置（取决于目标架构）：**

RK 平台：﻿/home/daystarm/systema-sdk-server/robot-service-midware/lib/aarch64/﻿
Jetson 平台：﻿/home/daystarm/systema-sdk-server/robot-service-midware/lib/lib_arm/﻿
NUC 平台：﻿/home/daystarm/systema-sdk-server/robot-service-midware/lib/x86_64/﻿
## 部署 (Deployment)

将构建好的文件部署到机器人设备：
1. 停止服务	
	`sudo systemctl stop lenovo-sdk.service`
2. 复制文件到机器人设备
	将可执行文件和依赖库复制到机器人的 ﻿~/share/sdk/bin/﻿目录：
	```
    # 复制可执行文件
	cp robot_service_middleware ~/share/sdk/bin/
	# 复制依赖库（根据你的目标架构选择相应的路径）
	# RK 平台 (aarch64):
	cp robot-service-midware/lib/aarch64/libmcs_client_lib.so ~/share/sdk/bin/
	cp robot-service-midware/lib/aarch64/librps_api.so ~/share/sdk/bin/
	# Jetson 平台 (lib_arm):
	cp robot-service-midware/lib/lib_arm/libmcs_client_lib.so ~/share/sdk/bin/
	cp robot-service-midware/lib/lib_arm/librps_api.so ~/share/sdk/bin/
	# NUC 平台 (x86_64):
	cp robot-service-midware/lib/x86_64/libmcs_client_lib.so ~/share/sdk/bin/
	cp robot-service-midware/lib/x86_64/librps_api.so ~/share/sdk/bin/
	```
3. 重启服务
	`sudo systemctl start lenovo-sdk.service`
4. 验证部署
	检查服务状态：
	`sudo systemctl status lenovo-sdk.service`
	检查 SDK server 版本和子模块：
	```
	cd ~/share/sdk/bin/
	./robot_service_middleware --version
	```
### 输出示例：
```
daystarm@RK3588:~/share/sdk/bin/$ ./robot_service_middleware --version
Robot Service Middleware
Version: 2.0.3
Build Date: 2025-07-29 18:43:12
Dependency Libraries:
MCS Client: 1.0.0 (Build: 2025-07-29 18:42:10)
RPS Client: 1.0.0 (Build: 2025-07-29 18:42:47)
TPLink SNMP: 1.0.0 (Build: 2025-07-29 18:43:01)
```
注意：在部署前，请确保您拥有适当的权限并且服务已正确配置。
## 项目架构
```
systema-sdk-server/
├── README.md # 项目文档
├── build.sh # 主构建脚本
├── RELEASE_NOTES.md # 版本发布说明
├── robot_service_middleware # 生成的可执行文件（构建后）
│
├── robot-service-midware/ # 主中间件服务
│ ├── BUILD_NOTES.md # 构建相关文档
│ ├── BUILD_SUMMARY.md # 构建过程摘要
│ ├── build.sh # 中间件构建脚本
│ ├── CMakeLists.txt # CMake 构建配置
│ ├── glibc.map # GLIBC 符号映射
│ ├── README.md # 中间件文档
│ │
│ ├── include/ # 头文件
│ │ ├── version.hpp.in # 版本模板文件
│ │ ├── external/ # 外部库头文件
│ │ │ ├── common/ # 通用工具
│ │ │ ├── is_robot/ # IS 机器人专用头文件
│ │ │ │ ├── mcs_client_api.h # MCS 客户端 API
│ │ │ │ ├── rps_api.h # RPS API
│ │ │ │ └── tplink_config.h # TPLink 配置
│ │ │ └── mc_robot/ # MC 机器人专用头文件
│ │ │ ├── highlevel.h # 高级控制 API
│ │ │ └── lowlevel.h # 低级控制 API
│ │ │
│ │ └── sdk/ # SDK 接口头文件
│ │ ├── common/ # 通用 SDK 组件
│ │ │ ├── IRobotDeviceManager.hpp # 设备管理器接口
│ │ │ ├── ISportComponent.hpp # 运动组件接口
│ │ │ ├── logger.hpp # 日志工具
│ │ │ └── robot_service_impl.hpp # 服务实现
│ │ ├── is/ # IS (六足) 专用组件
│ │ │ ├── IS_SportComponent.hpp # IS 运动组件
│ │ │ ├── ISRobotDeviceManager.hpp # IS 设备管理器
│ │ │ ├── log_component.hpp # 日志组件
│ │ │ ├── mcs_component.hpp # MCS 组件
│ │ │ ├── ota_component.hpp # OTA 组件
│ │ │ ├── rps_component.hpp # RPS 组件
│ │ │ └── snmp_component.hpp # SNMP 组件
│ │ └── mc/ # MC (四足) 专用组件
│ │ ├── MC_SportComponent.hpp # MC 运动组件
│ │ └── MCRobotDeviceManager.hpp # MC 设备管理器
│ │
│ ├── src/ # 源代码
│ │ ├── main.cpp # 主程序入口
│ │ ├── sdk.server.api/ # API 实现
│ │ │ └── robot_service_impl.cpp # gRPC 服务实现
│ │ ├── sdk.server.core/ # 核心功能
│ │ │ ├── is/ # IS 机器人核心组件
│ │ │ └── mc/ # MC 机器人核心组件
│ │ ├── sdk.server.dependency/ # 依赖管理
│ │ ├── sdk.server.protocol/ # 协议定义
│ │ │ └── grpc/ # gRPC 协议文件
│ │ └── sdk.server.utilities/ # 工具函数
│ │
│ ├── lib/ # 编译后的库（构建后）
│ │ ├── aarch64/ # RK 平台库
│ │ │ ├── libmc_sdk.so # MC SDK 库
│ │ │ ├── libmcs_client_lib.so # MCS 客户端库
│ │ │ ├── librps_api.so # RPS API 库
│ │ │ └── libtplink_config_lib.a # TPLink 配置库
│ │ ├── lib_arm/ # Jetson 平台库
│ │ │ ├── libmcs_client_lib.so # MCS 客户端库
│ │ │ ├── librps_api.so # RPS API 库
│ │ │ └── libtplink_config_lib.a # TPLink 配置库
│ │ └── x86_64/ # NUC 平台库
│ │ ├── libmc_sdk.so # MC SDK 库
│ │ ├── libmcs_client_lib.so # MCS 客户端库
│ │ ├── librps_api.so # RPS API 库
│ │ └── libtplink_config_lib.a # TPLink 配置库
│ │
│ └── test/ # 测试文件
│ ├── CMakeLists.txt # 测试构建配置
│ └── robot_service_test.cpp # 单元测试
│
├── mcs-client/ # MCS (运动控制服务) 客户端
│ ├── build.sh # MCS 客户端构建脚本
│ ├── CMakeLists.txt # CMake 配置
│ ├── README.md # MCS 客户端文档
│ ├── include/ # MCS 客户端头文件
│ │ ├── cmd_client.h # 指令客户端接口
│ │ ├── logger.hpp # 日志工具
│ │ ├── state_client.h # 状态客户端接口
│ │ └── c_api/ # C API 头文件
│ │ └── mcs_client_api.h # MCS 客户端 C API
│ ├── src/ # MCS 客户端源代码
│ │ ├── c_api_example.c # C API 使用示例
│ │ ├── cmd_client.cc # 指令客户端实现
│ │ ├── main.cc # MCS 客户端主程序
│ │ ├── mcs_client_api.cc # C API 实现
│ │ └── state_client.cc # 状态客户端实现
│ └── protos/ # Protocol buffer 定义
│ ├── cmd_issuance_entry.proto # 指令下发消息
│ ├── state_feedback_entry.proto # 状态反馈消息
│ └── common/ # 通用协议定义
│ └── entry_messages.proto # 通用消息定义
│
├── rps-client/ # RPS (机器人定位服务) 客户端
│ ├── build.sh # RPS 客户端构建脚本
│ ├── CMakeLists.txt # CMake 配置
│ ├── README.md # RPS 客户端文档
│ ├── rps_config.ini.example # 配置文件示例
│ ├── include/ # RPS 客户端头文件
│ │ ├── rps_api.h # RPS API 接口
│ │ └── rps_ws_client.h # WebSocket 客户端接口
│ ├── src/ # RPS 客户端源代码
│ │ ├── rps_api.cpp # RPS API 实现
│ │ ├── rps_api_demo.cpp # API 使用演示
│ │ └── rps_ws_client.cpp # WebSocket 客户端实现
│ ├── client/ # 客户端专用代码
│ └── example/ # 使用示例
│
└── tplink-snmp/ # TPLink SNMP 客户端
├── build.sh # SNMP 客户端构建脚本
├── CMakeLists.txt # CMake 配置
├── README_CPP.md # C++ 文档
├── include/ # SNMP 客户端头文件
│ └── tplink_config.h # TPLink 配置接口
└── src/ # SNMP 客户端源代码
├── test.cpp # 测试程序
└── tplink_config.cpp # TPLink 配置实现
```
### 关键组件说明
**主服务 (﻿robot-service-midware/﻿)**
- 核心中间件服务：集成了所有机器人控制组件
- 条件编译：支持 IS (六足) 和 MC/MX (四足) 机器人
- gRPC 服务器实现：提供统一的机器人控制 API
- 平台特定库：针对不同硬件架构的库文件

**MCS 客户端 (﻿mcs-client/﻿)**
- 运动控制服务客户端：用于机器人移动和姿态控制
- 指令和状态接口：用于实时机器人控制
- Protocol buffer 定义：用于高效通信
- C API 封装：用于跨语言兼容性

**RPS 客户端 (﻿rps-client/﻿)**
- 机器人定位服务客户端：用于定位和导航
- 基于 WebSocket 的通信：用于实时位置更新
- 配置管理：用于管理定位参数
- 
**TPLink SNMP (﻿tplink-snmp/﻿)**
- 网络设备监控：通过 SNMP 协议
- TPLink 设备配置：管理功能
- 网络诊断：和监控能力

## 系统要求 (System Requirements)
### 支持的平台
- RK3588：基于 Rockchip 的机器人控制器
- Jetson：NVIDIA Jetson 系列 (Xavier, Orin 等)
- NUC：Intel NUC 或 x86_64 系统
### 依赖项
- CMake: >= 3.10
- GCC/G++: >= 7.0 (支持 C++14)
- gRPC: >= 1.30.0
- Protocol Buffers: >= 3.12.0
- 交叉编译工具链(针对 ARM/RK 目标)
### 运行时要求
- Linux: Ubuntu 18.04+ 或兼容版本
- SystemD: 用于服务管理
- 网络访问: 用于 gRPC 通信
## 配置 (Configuration)
服务配置通过以下方式管理：
- SystemD 服务文件: ﻿/etc/systemd/system/lenovo-sdk.service﻿
- 运行时参数: 通过命令行或环境变量传递
- gRPC 端口: 可通过服务参数配置

默认服务端口：
- MCS Service: 48053 (指令), 48054 (状态)
## 故障排查 (Troubleshooting)
### 常见问题
1. 服务启动失败
```
# 检查服务状态和日志
sudo systemctl status lenovo-sdk.service
sudo journalctl -u lenovo-sdk.service -f
```
2. 找不到库文件错误
```
# 验证库文件是否存在
ls -la ~/share/sdk/bin/lib*.so
# 检查库依赖
ldd ~/share/sdk/bin/robot_service_middleware
```
3. 权限被拒绝
```
# 确保拥有正确权限
sudo chmod +x ~/share/sdk/bin/robot_service_middleware
sudo chown root:root ~/share/sdk/bin/robot_service_middleware
```
### 日志文件
- SDK INFO 日志查看:`tail -f /var/log/syslog﻿`

- SDK Total 日志查看（包含Debug日志）：﻿`sudo journalctl -u lenovo-sdk.service -f﻿`

- 应用程序日志: 检查应用程序特定的日志配置

### 调试模式
手动运行服务进行调试：
```
cd ~/share/sdk/bin/
./robot_service_middleware --debug --verbose
```