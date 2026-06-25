---
title: "[[vcstool 与 .repos 多仓库管理]]"
type: Permanent
status: done
Creation Date: 2026-06-25 17:20
tags:
---
## 1. 为什么需要它（Why）
### 1.1 真实痛点
一个稍微大一点的项目（尤其是 ROS2 / 机器人项目），代码往往不在一个 Git 仓库里，而是散落在**几十个仓库**中：
- 业务代码一个仓库（`daystar_api`）
- 各种消息定义一个仓库（`api_msgs`、`rms_msgs`、`cam_msgs`…）
- 第三方依赖各一个仓库（`nlohmann-json`、`bond_core`、`diagnostics`…）
- ROS2 本体源码又是一个仓库（`ros2`）
如果手动管理，你每天要做的事情是：
```bash
git clone urlA && cd A && git checkout 分支A && cd ..
git clone urlB && cd B && git checkout 分支B && cd ..
git clone urlC && cd C && git checkout 分支C && cd ..
# ……重复 30 遍
```
更新时还要：
```bash
cd A && git pull && cd ..
cd B && git pull && cd ..
# ……再重复 30 遍
```

**问题在哪？**

| 痛点     | 说明                            |
| ------ | ----------------------------- |
| 重复劳动   | 几十个仓库逐个 clone / pull，机械且易漏    |
| 无法版本固化 | 每个仓库该用哪个分支/commit，全靠口口相传或脑记   |
| 难以复现   | 新人入职、CI 流水线没法「一键还原」整套源码树      |
| 易出错    | 手敲 30 个 url + 30 个分支，错一个就编译失败 |

### 1.2 核心思想
> **用一个文本文件（`.repos`）声明「我需要哪些仓库、各用什么版本」，再用一条命令（`vcs import`）把它们一次性全部拉下来。**

这就是 **vcstool** 做的事：把「多仓库的状态」变成**可版本控制的配置文件**，实现一键克隆、一键更新、一键复现。

可以类比：
- `.repos` 文件 ≈ Python 的 `requirements.txt`（声明依赖清单）
- `vcs import` ≈ `pip install -r requirements.txt`（按清单一次装好）

## 2. vcstool 是什么（What）
**vcstool** 是一个命令行工具，提供 `vcs` 命令，用来**批量操作一组版本控制仓库**（git、hg、svn、bzr 都支持，最常用的是 git）。

- 它**不替代 git**，而是「在一堆仓库上批量跑 git 命令」的指挥官。
- 它是 ROS / ROS2 社区事实上的标准工具（官方用它管理 ROS2 源码）。
- 包名叫 `vcstool`，但命令是 `vcs`（注意：不要和另一个老工具 `vcs`/`wstool` 混淆，vcstool 是新一代）。

一句话：**`.repos` 是清单，`vcs` 是按清单干活的工人。**

## 3. `.repos` 文件详解
`.repos` 本质是一个 **YAML 文件**，结构非常简单，只有三层。
### 3.1 基本结构
```yaml
repositories:          # 顶层固定关键字
  本地目录名:           # clone 下来后的文件夹名（你自己起）
    type: git          # 仓库类型：git / hg / svn / bzr
    url: <仓库地址>     # 远程仓库 URL
    version: <版本>     # 分支名 / tag / commit，可省略（省略则用默认分支）
```
### 3.2 一个最小例子
```yaml
repositories:
  nlohmann-json:
    type: git
    url: https://github.com/nlohmann/json.git
    version: master
```
执行 `vcs import` 后，会在当前目录生成 `nlohmann-json/` 文件夹，并 checkout 到 `master`。
### 3.3 字段说明
| 字段             | 必填  | 说明                                        |
| -------------- | --- | ----------------------------------------- |
| `repositories` | 是   | 顶层根键，固定写法                                 |
| 目录名（如 `comm`）  | 是   | 决定 clone 到本地后的文件夹名，可带子路径如 `src/comm`      |
| `type`         | 是   | 一般写 `git`                                 |
| `url`          | 是   | 远程地址，支持 https / ssh                       |
| `version`      | 否   | 分支、tag 或 commit hash；不写则用远端默认分支（如 `main`） |

### 3.4 `version` 可以是什么
`version` 非常灵活，决定了「版本固化」的精确程度：
```yaml
version: main                                   # 跟踪某个分支（会随 pull 更新）
version: v2.0-dev                               # 跟踪某个分支
version: 1.2.3                                  # 指向某个 tag（相对稳定）
version: a1b2c3d4e5f6...                        # 指向某个具体 commit（完全锁死，最可复现）
```
> 经验：CI / 发布环境追求「可复现」时，用 **tag 或 commit**；日常开发追求「跟上最新」时，用**分支名**。
## 4. 核心命令速查（How - 命令）
假设你在一个工作目录里，手上有一个 `my.repos` 文件。
### 4.1 `vcs import` —— 按清单克隆（最常用）
```bash
# 从 my.repos 读取清单，把所有仓库 clone 到当前目录
vcs import < my.repos
# clone 到指定子目录（如 src/，ROS2 项目常用）
vcs import src < my.repos
mkdir -p src && vcs import src < my.repos   # 目录不存在时先建
```
> 注意那个 `<`：vcs import 默认从**标准输入**读清单，所以用重定向把文件喂给它。
### 4.2 `vcs pull` —— 批量更新
```bash
# 对目录下所有仓库执行 git pull
vcs pull src
```
### 4.3 `vcs export` —— 反向导出当前状态（生成 `.repos`）
```bash
# 扫描 src/ 下所有仓库，导出它们当前的 url 和 commit
vcs export src > snapshot.repos
# 导出精确 commit（而非分支名），用于锁定可复现快照
vcs export --exact src > locked.repos
```
> 这是一个非常有用的功能：你把环境调通后，用 `vcs export` 把当前所有仓库的精确版本固化成文件，别人 `import` 就能 100% 复现。
### 4.4 `vcs status` / `vcs diff` —— 批量查看
```bash
vcs status src    # 一次看所有仓库的 git status
vcs diff src      # 一次看所有仓库的改动
```
### 4.5 `vcs custom` —— 对所有仓库跑任意 git 命令（万能逃生口）
```bash
# 对每个仓库执行 git checkout main
vcs custom src --git --args checkout main
# 对每个仓库执行 git log -1
vcs custom src --git --args log -1
```
### 4.6 命令小结
| 命令           | 作用            | 类比               |
| ------------ | ------------- | ---------------- |
| `vcs import` | 按清单批量 clone   | `pip install -r` |
| `vcs pull`   | 批量拉取更新        | 批量 `git pull`    |
| `vcs export` | 导出当前状态成清单     | `pip freeze`     |
| `vcs status` | 批量查看状态        | 批量 `git status`  |
| `vcs diff`   | 批量查看改动        | 批量 `git diff`    |
| `vcs custom` | 批量执行任意 git 命令 | 万能批处理            |

## 5. 安装与第一次上手（How - 准备）
### 5.1 安装
```bash
# 方式一：pip（跨平台，推荐）
pip install vcstool

# 方式二：apt（Ubuntu / ROS 环境常见）
sudo apt install python3-vcstool

# 验证
vcs --version
```

### 5.2 三分钟跑通一个例子
```bash
# 1. 写一个 demo.repos
cat > demo.repos <<'EOF'
repositories:
  json:
    type: git
    url: https://github.com/nlohmann/json.git
    version: master
EOF

# 2. 一键导入
mkdir -p src && vcs import src < demo.repos

# 3. 查看结果
ls src/            # 看到 json/ 文件夹
vcs status src     # 看到它的 git 状态
```

## 6. 结合本项目看真实用法
本仓库 `sdk-server-deployment` 正是用 vcstool 来聚合管理所有源码的。看几个真实文件：
### 6.1 真实的 `.repos` 片段
来自 [sdk_server.repos](../../sdk_server.repos)：
```yaml
repositories:
  comm:
    type: git
    url: https://gitlab.xpaas.lenovo.com/lrsh-sds-robot/rms/comm.git
    version: sdk_server          # 跟踪 sdk_server 分支

  navigation_msgs:
    type: git
    url: https://gitlab.xpaas.lenovo.com/lrsh-sds-robot/navigation/navigation_msgs
    version: rms2.0-interfaces    # 不同仓库可以用不同分支

  daystar_api:
    type: git
    url: https://gitlab.xpaas.lenovo.com/lrsh-sds-bsp/projects/robot-sdk/daystar_api.git
    version: sdk_server
```

> 注意：本项目里 url 中带了 `oauth2:<token>@` 形式的访问令牌。这是为了 CI 自动拉取私有仓库，但**有安全风险**，见[第 9 节](#9-安全提示凭据不要硬编码)。

### 6.2 项目把仓库按用途拆成了三个清单
| 文件 | 内容 | 类比 |
|------|------|------|
| [ros2.repos](../../ros2.repos) | ROS2 本体源码 | 操作系统级依赖 |
| [third_party.repos](../../third_party.repos) | 第三方库（json、diagnostics…） | 第三方依赖 |
| [sdk_server.repos](../../sdk_server.repos) | 自家业务 + 消息定义 | 业务代码 |

> 拆分的好处：不同类别的更新频率、权限、缓存策略可以分开管理。第三方库很少动，可以单独缓存加速 CI。

### 6.3 真实的一键拉取脚本
来自 [CI.bash](../../CI.bash)，这正是 vcstool 在工程里最典型的用法：

```bash
#!/bin/bash
set -exu

# 按三个清单分别导入到三个目录
mkdir -p ros2         && vcs import ros2         < ros2.repos
mkdir -p third_party  && vcs import third_party  < third_party.repos
mkdir -p sdk_server   && vcs import sdk_server   < sdk_server.repos

# 批量更新到各自分支最新
vcs pull ros2
vcs pull third_party
vcs pull sdk_server
```

读懂这段脚本，你就理解了 vcstool 在真实项目里的角色：**CI / 新人环境搭建的「源码一键还原」入口**。

## 7. 典型工作流
### 7.1 新人/CI：从零搭建源码树
```bash
git clone <本部署仓库>          # 1. 先拿到含 .repos 的「总仓库」
cd sdk-server-deployment
bash CI.bash                    # 2. 一条脚本把几十个仓库全拉下来
# 之后就是正常的 colcon build 等
```
### 7.2 日常：同步最新代码
```bash
vcs pull sdk_server             # 把业务仓库都更新到各自分支最新
```
### 7.3 发版：固化一份可复现快照
```bash
# 把当前所有仓库的精确 commit 导出，存档为发布版本清单
vcs export --exact sdk_server > release-2.5.2.repos
# 以后任何人用这份文件 import，得到的源码 100% 一致
```
### 7.4 切分支：所有仓库一起切
```bash
vcs custom sdk_server --git --args checkout release-branch
```
## 8. 常见坑与排错

| 现象                       | 原因                 | 解决                                                                  |
| ------------------------ | ------------------ | ------------------------------------------------------------------- |
| `vcs: command not found` | 没装或装错包             | `pip install vcstool`，注意包名是 `vcstool`                               |
| `import` 后目录是空的          | 忘了 `<` 重定向         | 用 `vcs import dir < file.repos`                                     |
| 已存在的仓库没更新                | `import` 默认不覆盖已有改动 | 用 `vcs pull` 更新，或 `vcs import --force` 重置                           |
| 私有仓库拉取失败 401/403         | 没有凭据或 token 过期     | 配置 SSH key 或更新 token（别写进 `.repos`）                                  |
| YAML 解析报错                | 缩进/冒号格式错误          | YAML 对缩进敏感，统一用 2 空格，不要用 Tab                                         |
| 某仓库不想被编译                 | colcon 会扫描所有子目录    | 在该目录放一个 `COLCON_IGNORE` 空文件（本项目 CI.bash 就这么处理 `chenxing_agent_ros`） |

> `--force` 会丢弃本地改动，属于不可逆操作，使用前确认没有未提交的工作。
## 9. 安全提示：凭据不要硬编码
本项目的 `.repos` 里出现了这种写法：
```yaml
url: https://oauth2:<真实token>@gitlab.xpaas.lenovo.com/.../comm.git
```
把访问令牌（token）直接写进会被提交的文件里，是一个**安全隐患**：
- 任何能看到这个仓库的人都拿到了凭据
- token 泄露后可访问对应的所有私有仓库
- Git 历史里会永久留存，即使后来删掉也能翻出来
**更安全的做法（按推荐度排序）：**
1. **用 SSH 地址 + SSH key**：`git@gitlab.xpaas.lenovo.com:lrsh-.../comm.git`，凭据放在本地 SSH key，不进文件。
2. **用 git credential helper**：把 token 交给系统凭据管理器，`.repos` 里只放纯净 https url。
3. **CI 里用环境变量注入**：`.repos` 用占位 url，CI 运行时通过 `git config` 的 `url.<base>.insteadOf` 动态拼接 token。
> 如果这些 token 已经提交过，建议尽快在 GitLab 后台**吊销并轮换**，因为它已经存在于 Git 历史中。
  
## 10. 对比与延伸：和 git submodule / repo 的区别

| 工具                    | 思路                     | 优点                  | 缺点                          |
| --------------------- | ---------------------- | ------------------- | --------------------------- |
| **vcstool（`.repos`）** | 独立 YAML 清单 + 批量命令      | 简单、灵活、ROS 生态标准、易读易改 | 版本不自动锁定（除非用 export --exact） |
| **git submodule**     | 把子仓库嵌进父仓库的 git 元数据     | 版本强绑定到父仓库 commit    | 操作繁琐、易踩坑、新手不友好              |
| **Google `repo`**     | manifest XML + repo 命令 | 适合超大规模（Android）     | 偏重、学习成本高                    |


**为什么 ROS2 选 vcstool？** 因为机器人项目仓库多、组合灵活、需要频繁切换不同分支组合，vcstool 的「纯文本清单 + 一键命令」恰好命中这个场景，既轻量又可复现。

## 11. 一页速查表
```text
概念
  .repos   = 仓库清单（YAML），声明「要哪些仓库、用什么版本」
  vcs      = 按清单批量干活的命令行工具（包名 vcstool）
  
安装
  pip install vcstool

最常用四条命令
  vcs import <dir> < x.repos     # 按清单批量 clone
  vcs pull   <dir>               # 批量更新
  vcs export --exact <dir>       # 导出精确版本快照（可复现）
  vcs status <dir>               # 批量看状态

.repos 结构
  repositories:
    <本地目录名>:
      type: git
      url: <地址>
      version: <分支/tag/commit，可省略>

本项目入口
  bash CI.bash                   # 一键还原全部源码树

安全
  别把 token 写进 .repos，改用 SSH key 或 credential helper
```
