---
title: "[[常用Debug命令]]"
type: Permanent
status: ing
Creation Date: 2026-07-16 17:30
tags:
---
## 查看容器日志
```
docker logs -f sdk_server
```
- docker: Docker 客户端的主命令。
- logs: 用于获取容器的日志。
- -f: 这是 --follow 的缩写，意思是 持续跟踪（实时刷新）​ 日志输出。如果不加这个参数，命令只会打印当前已有的日志然后退出；加上后，它会像 tail -f 命令一样，一直挂起并实时显示新产生的日志。
- sdk_server: 这是容器的名称（也可以使用容器 ID）。它告诉 Docker 你要查看哪个容器的日志。
### 常用搭配参数（进阶）
可以组合其他参数来实现更精确的查看：
- **查看最后 N 行日志**：
    ```bash
    docker logs --tail 100 sdk_server  # 只查看最后100行
    ```
- **查看某个时间点之后的日志**：
    ```bash
    docker logs --since "2024-01-01T10:00:00" sdk_server
    docker logs --since "10m" sdk_server  # 查看最近10分钟的日志
    ```
- **显示时间戳**：
    ```bash
    docker logs -f -t sdk_server  # -t 会为每条日志加上时间戳
    ```
- **组合使用**：
    
    ```bash
    docker logs -f --tail 50 --since "5m" sdk_server
    # 含义：实时跟踪，从最近5分钟的日志开始，并先显示最后50行。
    ```
## 动态地修改指定日志记录器（Logger）的输出级别
```bash
ros2 service call /sdk/main_logger/set_severity rms_msgs/srv/ConfigLogger "level: 'debug'"
```
- `ros2 service call`: ROS 2 的命令行工具，用于**调用（触发）一个已经存在的 ROS 2 服务**。
- `/sdk/main_logger/set_severity`: 这是**服务的名称**。从命名可以看出：
    - `/sdk/`：通常与特定的 SDK 功能包相关。
    - `main_logger`：很可能指的是 SDK 中的“主日志记录器”。
    - `set_severity`：这个服务的目的是“设置严重性级别”（即日志等级）。
        
- `rms_msgs/srv/ConfigLogger`: 这是**服务的数据类型（接口定义）**。它告诉 ROS 2 这个服务使用 `rms_msgs` 包中定义的 `ConfigLogger` 这种请求-响应结构。
    
- `"level: 'debug'"`: 这是传递给服务的**请求数据（参数）**。这里将日志级别（`level`）设置为 `'debug'`。