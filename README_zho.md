<p align="center">
  <img src="images/ARMOR_BANNER.svg" alt="ARMOR-COMMON banner" width="100%">
</p>

# 🧾 ARMOR-COMMON

<p align="center">
  <a href="README.md">🇺🇸 English</a> |
  <a href="README_spa.md">🇪🇸 Español</a> |
  <a href="README_fra.md">🇫🇷 Français</a> |
  <a href="README_ita.md">🇮🇹 Italiano</a> |
  <a href="README_deu.md">🇩🇪 Deutsch</a> |
  🇨🇳 <b>简体中文</b> |
  <a href="README_jpn.md">🇯🇵 日本語</a> |
  <a href="README_por.md">🇵🇹 Português</a>
</p>

### 消息契约、验证、各节点共用的固件基础和共享的项目启动器

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0-blue.svg" alt="GPL 3.0">
  <img src="https://img.shields.io/badge/Language-Python%203.11%2B-3776ab.svg" alt="Language">
  <img src="https://img.shields.io/badge/Dependencies-none-2ea44f.svg" alt="Dependencies">
  <img src="https://img.shields.io/badge/Vectors-1225-00E5FF.svg" alt="Vectors">
  <img src="https://img.shields.io/badge/Version-0.7.7-0f6cbd.svg" alt="Version">
  <img src="https://img.shields.io/badge/Maturity-established-2EA44F.svg" alt="Maturity">
</p>

---

**诚实性检查 - 今天真正能运行的部分:** 各模式（遥测、健康、命令、节点信息、太阳能逆变器和电池、电气、带命令和结果的报警、网络）、Python 验证器、1225 个一致性向量、生成的 TypeScript 和 Kotlin 类型、服务器的 OpenAPI 文件（190 个路径）、五个节点共用的固件基础以及共享的项目启动器都是真实的并经过测试（170 个测试）。Kotlin 文件已生成，但 ARMOR-ANDROID-CONTROL **尚未使用**（它保留自己的解析），`set_thresholds` 命令只带一个 `sensitivity` 字段，因为真实的雷达参数要等固件存在才能确定。

---

## 📋 速览

| | |
|---|---|
| 版本 | `0.7.7` |
| 成熟度 | 成熟 |
| 测试 | 170 (`python -m unittest discover -s tests`) 以及 1225 个一致性向量 |
| 技术栈 | Python 3.11+ / JSON Schema / OpenAPI |
| 真实硬件 | 只有雷达节点在电路板上运行过：它的消息就是 CM5 服务器、Studio 和 Android 应用每天使用的消息；其他节点的消息对照替身检查 |

## 🚦 项目状态

每一行是本仓库的一个部分，灯号表示它今天做到了哪一步。内容依据仓库能够展示的证据（测试、构建、运行），而不是计划。

🟢 已完成并验证 · 🟡 可用，有已知限制 · 🟠 部分完成或尚未验证 · 🔴 未完成或不可用

| 领域 | 状态 | 在这里的含义 |
|---|---|---|
| 软件 | 🟢 | 模式、Python 验证器、生成的 TypeScript 和 Kotlin 类型、服务器的 OpenAPI 文件以及五个节点共用的固件基础均已就绪。 |
| 测试 | 🟢 | 170 项测试和 1225 个一致性向量通过；固件的 JSON、蓝牙和 Improv 解析器还用 libFuzzer 做了模糊测试。 |
| 协议与数据 | 🟡 | 只有雷达节点的消息每天在真实板子和服务器上使用；其他节点的消息是对照模拟检查的。 |
| 集成 | 🟡 | 会检查固件基础在每个节点中完全相同；Kotlin 类型已生成，但 Android 应用尚未使用，它仍保留自己的解析。 |
| 硬件 | 🟠 | 只有雷达节点在板子上运行过这套共用固件；其他四个节点没有。 |
| 安全 | 🟡 | 固件签名检查和蓝牙 PIN 的推导已在主机上测试；没有经过独立审查。 |
| 文档 | 🟢 | 八种语言、OpenAPI 文件、一致性指南和更新日志均为最新。 |

## 🎯 概述

**ARMOR-COMMON** 掌管每条 A.R.M.O.R. 消息的含义。雷达节点、太阳能网关节点和模拟器产生这些消息；服务器、视觉 AI 和语音服务消费它们。如果两个项目对某个字段有分歧，由本仓库裁决。

* **唯一的事实来源：**`src/armor_common/schemas/` 中的 JSON Schema，涵盖遥测、健康、命令、节点信息、两种太阳能消息（逆变器、含电芯和容量的电池）、电气消息（读数、命令、结果）、报警消息（状态、命令、结果）和网络消息。未知字段和不可能的组合会被拒绝。
* **无法跳过规则的验证器：**它直接解释模式，并拒绝使用了它未实现的关键字的模式。
* **一致性向量：**1225 个被接受和被拒绝的负载，由每个实现运行（这里是 Python，ARMOR-SERVER 中是 TypeScript，以及固件仓库的检查），因此偏差会让构建失败。
* **生成的客户端：**TypeScript 和 Kotlin 类型来自模式（`tools/generate_types.py --check` 保持其最新）。
* **HTTP 契约：**`openapi/armor-server.yaml` 描述服务器的每条路由（190 个路径、245 个操作）、其访问规则，以及每个请求体、响应和错误的具名模式；测试会检查服务器注册的路由与其描述的路由完全一致（方法和路径）。
* **固件基础：**`firmware_base/` 把五个节点共用的每个文件只保存一次（网络、设置和用户、网页面板服务器和登录、HTTPS 证书、日志、带 PIN 配对的蓝牙、签名更新检查；继电器和 Zigbee 仅限具备它们的节点）；`tools/sync_firmware_base.py` 把它写入每个节点并检查没有副本偏离（[指南](docs/FIRMWARE_BASE.md)，[签名固件](docs/SIGNED_FIRMWARE.md)）。
* **共享启动器：**`tools/armor_project_tool.py` 为家族的每个仓库提供相同的 `build`、`build-test` 和 `run` 流程，`tools/armor_ci_validate.py` 提供相同的 CI 检查。
* **共享节点基础中可选的与代理的 TLS 连接:** `firmware_base` 包含 `mqtt.tls` 开关和 `mqtt.ca_pem` 文本(一个 PEM 证书,最大 2 KB,经过校验)、只信任该机构并检查代理名称的连接,以及五个节点共用的主机测试;默认关闭。
* **节点健康与布防配置：** `node_health` 消息（雷达、太阳能、电气、报警或壁挂面板节点发送相同的报告）和 `arm_profile`（布防命令中带有的命名布防方式：哪些分区守护、延时、警笛以及服务器通知的力度）都有自己的模式、一致性向量、生成的 TypeScript 与 Kotlin 类型、OpenAPI 路由，以及生成报告的共享固件代码。
* **历史中的连接事件与系统事件：** 模式 `connection_event`、`system_event` 和 `connection_client`（服务器历史对连接的客户端和系统本身的描述，词汇固定，没有可以放入机密的字段）、其一致性向量、生成的 TypeScript 与 Kotlin 类型，以及列出客户端的 OpenAPI 路由。
* **合同中的诊断与读数质量：** 不干净启动报告、核心转储、设置安全检查、诊断包、雷达事件和只读诊断令牌消息都有各自的模式、一致性向量和生成的类型；电表通道可以携带其读数的时间和错误计数，逆变器消息可以点名节点限制在上限的数值。

## 🧩 在 A.R.M.O.R. 中的角色

ARMOR-COMMON 让整个家族说同一种语言。节点与 [ARMOR-SERVER](https://github.com/JuanenRac/ARMOR-SERVER) 之间的每条消息都在这里只定义一次，并带有每个实现都必须通过的向量；服务器的 HTTP 契约也在这里；五个节点共用的固件（[ARMOR-NODE-RADAR](https://github.com/JuanenRac/ARMOR-NODE-RADAR)、[ARMOR-NODE-SOLAR](https://github.com/JuanenRac/ARMOR-NODE-SOLAR)、[ARMOR-NODE-ELECTRICAL](https://github.com/JuanenRac/ARMOR-NODE-ELECTRICAL)、[ARMOR-NODE-ALARM](https://github.com/JuanenRac/ARMOR-NODE-ALARM)、[ARMOR-NODE-HMI](https://github.com/JuanenRac/ARMOR-NODE-HMI)）只保存一份，由工具复制进去。它不保存任何密钥，也不在生产中运行任何东西。

## 🔄 架构

```mermaid
flowchart LR
    S["JSON Schemas (source of truth)"] --> P["armor_common (Python validator)"]
    S --> G["generated TS + Kotlin types"]
    S --> V["conformance vectors"]
    V --> P
    V --> T["ARMOR-SERVER tests"]
    V --> X["ARMOR-NODE-SOLAR and ARMOR-NODE-ELECTRICAL checks"]
    S --> O["OpenAPI (HTTP contract)"]
```

## 📂 仓库结构

```text
ARMOR-COMMON/
├── src/armor_common/   contracts, schema (validator), envelope, schemas/*.json (the node messages, the alarm, electrical and network ones, the relay, zone-feed, alert and orders ones)
├── conformance/        accepted and rejected payloads shared by every implementation
├── firmware_base/      the firmware that the five nodes share, once (synced into each by tools/sync_firmware_base.py)
├── generated/          TypeScript and Kotlin types (generated, do not edit)
├── openapi/            armor-server.yaml
├── registry/           repositories.json: the one list of the repositories of the family (kind, group, technologies, place on the map, who feeds whom) that the documentation, deployment and update tools read
├── fuzz/               libFuzzer targets for the JSON, Bluetooth-frame and Improv parsers of the nodes, with their corpus and run_fuzz.sh
├── scripts/            armor-project.sh and armor-project.bat: the launcher of armor_project_tool.py
├── tools/              armor_project_tool.py, generate_types.py, generate_rest_types.py, make_conformance.py, sync_firmware_base.py, release_firmware.py, firmware_sign.mjs, voice_cases.py, ci.yml.template and e2e.yml.template (the shared workflows), armor_ci_validate.py + _armor_readme_parity.py (the shared CI checks)
├── tests/              unit tests and conformance runner
└── docs/               CONTRACTS, FIRMWARE_BASE, FUZZING, PROJECT_MANIFEST, SIGNED_FIRMWARE
```

## 🛠️ 开发环境

**环境要求:** Python 3.11+

```powershell
python -m pip install -e .
python -m unittest discover -s tests      # 170 tests, 1225 conformance vectors
python tools/generate_types.py --check    # generated types are current
python tools/generate_rest_types.py --check    # the types of the HTTP contract are current
python tools/make_conformance.py          # regenerate the vectors after editing the case list (--check: they are current)
python tools/sync_firmware_base.py check  # the firmware the node projects share has not drifted (see docs/FIRMWARE_BASE.md)
```

代理主题：`armor/node/{node_id}/telemetry | health | command | info`、`armor/solar/{node_id}/{device}/state`、`armor/electrical/{node_id}/state | command | result`、`armor/alarm/{node_id}/state | command | result` 和 `armor/network/{node_id}/state`。参见[契约指南](docs/CONTRACTS.md)。共享启动器在 ARMOR-SERVER 首次运行时创建被忽略的 `.env`，其中有随机密钥和随机管理员密码；不会打印或提交任何内容。

## 🔗 相关项目

**A.R.M.O.R.**（Autonomous Radar & Multimodal Observation Range）是由若干独立仓库组成的周界安防系统。每个仓库都有自己的版本、测试和 README；家族成员如下：

* **ARMOR-COMMON** (本仓库) - 消息契约、验证器、一致性向量和生成的类型
* **[ARMOR-NODE-RADAR](https://github.com/JuanenRac/ARMOR-NODE-RADAR)** - 适用于 ESP32-S3 的现场节点固件，带三个雷达和自带网页面板
* **[ARMOR-NODE-SOLAR](https://github.com/JuanenRac/ARMOR-NODE-SOLAR)** - 太阳能逆变器与电池的协议，以及网关节点的消息
* **[ARMOR-NODE-ELECTRICAL](https://github.com/JuanenRac/ARMOR-NODE-ELECTRICAL)** - 电气节点：电表、电网读数消息和开关规则
* **[ARMOR-NODE-ALARM](https://github.com/JuanenRac/ARMOR-NODE-ALARM)** - 报警节点与报警主机：防区、布防、延时、警笛和 PIN，有无服务器均可
* **[ARMOR-NODE-HMI](https://github.com/JuanenRac/ARMOR-NODE-HMI)** - 触摸面板：墙面屏幕上的系统状态、布防与确认，以及语音助手的所在
* **[ARMOR-NETWORK](https://github.com/JuanenRac/ARMOR-NETWORK)** - 本地网络：其设备、互联网以及变化
* **[ARMOR-SERVER](https://github.com/JuanenRac/ARMOR-SERVER)** - 中央协调器：遥测、报警、设备、太阳能读数和摄像头
* **[ARMOR-STUDIO](https://github.com/JuanenRac/ARMOR-STUDIO)** - 网页控制台：摄像头、雷达、报警、太阳能和 2D/3D 场地设计器
* **[ARMOR-ANDROID-CONTROL](https://github.com/JuanenRac/ARMOR-ANDROID-CONTROL)** - 带实时 2D/3D 雷达的 Android 操作员客户端
* **[ARMOR-IOS-CONTROL](https://github.com/JuanenRac/ARMOR-IOS-CONTROL)** - iPhone 操作员客户端
* **[ARMOR-SERVER-AI](https://github.com/JuanenRac/ARMOR-SERVER-AI)** - 会解释决策且从不执行动作的视觉推理策略
* **[ARMOR-VISION](https://github.com/JuanenRac/ARMOR-VISION)** - Jetson Orin NX 上的摄像头区域、遮罩与检测规则
* **[ARMOR-VOICE-AI](https://github.com/JuanenRac/ARMOR-VOICE-AI)** - 带无法伪造确认的离线语音意图
* **[ARMOR-HARDWARE](https://github.com/JuanenRac/ARMOR-HARDWARE)** - 外壳、电子器件和台架验收矩阵
* **[ARMOR-DEVOPS](https://github.com/JuanenRac/ARMOR-DEVOPS)** - 部署、CM5 测试台、备份与 TLS
* **[ARMOR-SIMULATOR](https://github.com/JuanenRac/ARMOR-SIMULATOR)** - 带可重复故障的离线遥测模拟器
* **[ARMOR-UPDATER](https://github.com/JuanenRac/ARMOR-UPDATER)** - 发现、安装并更新生态系统自身的仓库
* **[ARMOR-DOCS](https://github.com/JuanenRac/ARMOR-DOCS)** - 架构、安全基线和能力矩阵

## 📚 文档与社区

更多阅读：

* [能力矩阵：哪些已被证实，哪些没有](https://github.com/JuanenRac/ARMOR-DOCS/blob/main/docs/CAPABILITY_MATRIX.md)
* [项目目录：版本以及各仓库之间的依赖](https://github.com/JuanenRac/ARMOR-DOCS/blob/main/docs/PROJECT_CATALOG.md)
* [本仓库的变更记录](CHANGELOG.md)
* [许可证（GPL-3.0-or-later）](LICENSE)
* 问题、想法与反馈：electrohobby3d@gmail.com

## 👤 作者

**JuanenRac (Electro Hobby 3D)** · electrohobby3d@gmail.com

## 📜 许可证

GPL-3.0-or-later - 见 [LICENSE](LICENSE)。
