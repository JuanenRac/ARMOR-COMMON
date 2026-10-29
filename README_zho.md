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
  <img src="https://img.shields.io/badge/License-GPL%203.0--or--later-blue.svg" alt="GPL 3.0 or later">
  <img src="https://img.shields.io/badge/Language-Python%203.11%2B-3776ab.svg" alt="Language">
  <img src="https://img.shields.io/badge/Dependencies-none-2ea44f.svg" alt="Dependencies">
  <img src="https://img.shields.io/badge/Vectors-1225-00E5FF.svg" alt="Vectors">
  <img src="https://img.shields.io/badge/Tests-214%20passing-2ea44f.svg" alt="Tests">
  <img src="https://img.shields.io/badge/Version-0.7.7-0f6cbd.svg" alt="Version">
  <img src="https://img.shields.io/badge/Maturity-established-2EA44F.svg" alt="Maturity">
</p>

---

**诚实性检查 - 今天真正能运行的部分：** 各模式（遥测、健康、命令、节点信息、太阳能逆变器和电池、电气、带命令和结果的报警、网络）、Python 验证器、1225 个一致性向量、生成的 TypeScript 和 Kotlin 类型、服务器的 OpenAPI 文件（191 个路径）、五个节点共用的固件基础以及共享的项目启动器都是真实的并经过测试（214 个测试）。Kotlin 文件已生成，但 ARMOR-ANDROID-CONTROL **尚未使用**（它保留自己的解析），`set_thresholds` 命令只带一个 `sensitivity` 字段，因为真实的雷达参数要等固件存在才能确定。

---

## 📋 速览

| | |
|---|---|
| 版本 | `0.7.7` |
| 成熟度 | 成熟 |
| 角色 | 家族共用的契约、校验器和固件基础 |
| 技术栈 | Python 3.11+、JSON Schema、OpenAPI；C++ 固件基础（ESP-IDF） |
| 测试 | 214 项（`python -m unittest discover -s tests`），1225 个一致性向量 |
| 契约 | 34 个 JSON Schema，191 条 HTTP 路径（247 个操作） |
| 运行位置 | 任意计算机（库和工具）；固件基础运行在五个节点内 |
| 真实硬件 | 只有雷达节点在开发板上运行过共用固件；其他四个没有 |
| 许可证 | GPL-3.0-or-later |

**跳转到：** [概述](#-概述) · [架构](#-架构) · [功能](#-功能) · [安全](#-安全与防护) · [接口](#-接口) · [配置](#-配置) · [快速开始](#-快速开始) · [测试](#-测试) · [故障排除](#-故障排除) · [结构](#-仓库结构) · [相关项目](#-相关项目)

## 🚦 项目状态

每一行是本仓库的一个部分，灯号表示它今天做到了哪一步。内容依据仓库能够展示的证据（测试、构建、运行），而不是计划。

🟢 已完成并验证 · 🟡 可用，有已知限制 · 🟠 部分完成或尚未验证 · 🔴 未完成或不可用

| 领域 | 状态 | 在这里的含义 |
|---|---|---|
| 软件 | 🟢 | 模式、Python 验证器、生成的 TypeScript 和 Kotlin 类型、服务器的 OpenAPI 文件以及五个节点共用的固件基础均已就绪。 |
| 测试 | 🟢 | 214 项测试和 1225 个一致性向量通过；固件的 JSON、蓝牙和 Improv 解析器还用 libFuzzer 做了模糊测试。 |
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
* **HTTP 契约：**`openapi/armor-server.yaml` 描述服务器的每条路由（191 个路径、247 个操作）、其访问规则，以及每个请求体、响应和错误的具名模式；测试会检查服务器注册的路由与其描述的路由完全一致（方法和路径）。
* **固件基础：**`firmware_base/` 把五个节点共用的每个文件只保存一次（网络、设置和用户、网页面板服务器和登录、HTTPS 证书、日志、带 PIN 配对的蓝牙、签名更新检查；继电器和 Zigbee 仅限具备它们的节点）；`tools/sync_firmware_base.py` 把它写入每个节点并检查没有副本偏离（[指南](docs/FIRMWARE_BASE.md)，[签名固件](docs/SIGNED_FIRMWARE.md)）。
* **共享启动器：**`tools/armor_project_tool.py` 为家族的每个仓库提供相同的 `build`、`build-test` 和 `run` 流程，`tools/armor_ci_validate.py` 提供相同的 CI 检查。
* **共享节点基础中可选的与代理的 TLS 连接:** `firmware_base` 包含 `mqtt.tls` 开关和 `mqtt.ca_pem` 文本(一个 PEM 证书,最大 2 KB,经过校验)、只信任该机构并检查代理名称的连接,以及五个节点共用的主机测试;默认关闭。
* **节点健康与布防配置：** `node_health` 消息（雷达、太阳能、电气、报警或壁挂面板节点发送相同的报告）和 `arm_profile`（布防命令中带有的命名布防方式：哪些分区守护、延时、警笛以及服务器通知的力度）都有自己的模式、一致性向量、生成的 TypeScript 与 Kotlin 类型、OpenAPI 路由，以及生成报告的共享固件代码。
* **历史中的连接事件与系统事件：** 模式 `connection_event`、`system_event` 和 `connection_client`（服务器历史对连接的客户端和系统本身的描述，词汇固定，没有可以放入机密的字段）、其一致性向量、生成的 TypeScript 与 Kotlin 类型，以及列出客户端的 OpenAPI 路由。
* **合同中的诊断与读数质量：** 不干净启动报告、核心转储、设置安全检查、诊断包、雷达事件和只读诊断令牌消息都有各自的模式、一致性向量和生成的类型；电表通道可以携带其读数的时间和错误计数，逆变器消息可以点名节点限制在上限的数值。

## 🧩 在 A.R.M.O.R. 中的角色

ARMOR-COMMON 让整个家族说同一种语言。节点与 [ARMOR-SERVER](https://github.com/JuanenRac/ARMOR-SERVER) 之间的每条消息都在这里只定义一次，并带有每个实现都必须通过的向量；服务器的 HTTP 契约也在这里；五个节点共用的固件（[ARMOR-NODE-RADAR](https://github.com/JuanenRac/ARMOR-NODE-RADAR)、[ARMOR-NODE-SOLAR](https://github.com/JuanenRac/ARMOR-NODE-SOLAR)、[ARMOR-NODE-ELECTRICAL](https://github.com/JuanenRac/ARMOR-NODE-ELECTRICAL)、[ARMOR-NODE-ALARM](https://github.com/JuanenRac/ARMOR-NODE-ALARM)、[ARMOR-NODE-HMI](https://github.com/JuanenRac/ARMOR-NODE-HMI)）只保存一份，由工具复制进去。它不保存任何密钥，也不在生产中运行任何东西。

| 对话对象 | 方式 | 用途 |
|---|---|---|
| ARMOR-SERVER | 运行向量；实现每条 OpenAPI 路由 | 向量、OpenAPI |
| ARMOR-STUDIO | 保留生成类型的副本；偏离时测试失败 | 生成的 TypeScript |
| ARMOR-ANDROID-CONTROL | 有自己的解析；Kotlin 类型已生成但未使用 | 生成的 Kotlin |
| ARMOR-NODE-RADAR, SOLAR, ELECTRICAL, ALARM, HMI | 通过 `tools/sync_firmware_base.py` 接收 firmware_base | 复制的固件 |
| ARMOR-DOCS, ARMOR-DEVOPS, ARMOR-UPDATER | 读取唯一的仓库清单 `registry/repositories.json` | 注册表 |

## 🏛️ 架构

<p align="center">
  <img src="images/architecture.svg" alt="ARMOR-COMMON architecture: who uses it, what the repository owns (schemas, vectors, validator, generated types, OpenAPI, firmware base) and who receives it" width="100%">
</p>

<details>
<summary>图表的文本版本（Mermaid）</summary>

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

</details>

## ✨ 功能

### 添加或修改消息

1. 编辑 `src/armor_common/schemas/` 中的模式（含义改变时同时改 `docs/CONTRACTS.md`）。
2. 把用例加入列表并运行 `python tools/make_conformance.py`。
3. 运行 `python tools/generate_types.py` 和 `python tools/generate_rest_types.py` 更新 TypeScript 和 Kotlin 类型。
4. 涉及路由时更新 `openapi/armor-server.yaml`；`tests/test_openapi.py` 会把它与服务器的路由对比。
5. 服务器和节点随后运行同样的向量，因此任何分歧都会使构建失败。

### 固件基础

`firmware_base/` 把五个节点共用的每个文件只保存一份：网络、设置和用户、网页面板服务器及其登录、HTTPS 证书、日志、带 PIN 配对的蓝牙、签名更新的检查、节点健康报告、让异常节点重启的守护、服务器的类型化指令，以及有此功能节点的继电器和 Zigbee。`tools/sync_firmware_base.py` 把它写入每个节点并检查没有副本偏离（见 [docs/FIRMWARE_BASE.md](docs/FIRMWARE_BASE.md) 和 [docs/SIGNED_FIRMWARE.md](docs/SIGNED_FIRMWARE.md)）。无需硬件的判定在 `core/` 中，在电脑上测试；`main/` 读取真实值。

## 🔒 安全与防护

| 威胁 | 防御 |
|---|---|
| 未知字段或不可能的组合 | `additionalProperties: false`；校验器直接解释模式，并拒绝加载使用了未实现关键字的模式 |
| 无上限的遥测耗尽节点 | 最多 15 条轨迹（3 个传感器各 5 条），照度 0 到 200 000 |
| 列表之外的命令 | 允许列表：`calibrate`、`set_thresholds`（灵敏度 1 到 10）、`restart`；订阅方在触及硬件前拒绝其余命令 |
| 主题与消息体中的节点 ID 不一致 | 消费方拒绝不一致 |
| GitHub 上的伪造固件 | 镜像必须与其 `.sha256` 一致，并带有该哈希的 Ed25519 签名，用 `firmware_base/core/fw_trust.hpp` 内置公钥验证；否则不做任何更改 |
| 发布私钥泄露 | 它不在任何仓库、CI 或发布中（PKCS#8，权限 0600）；密钥与固件信任的不一致时 `release_firmware.py` 拒绝发布 |
| 节点密码和蓝牙 PIN | 密码：PBKDF2-HMAC-SHA256，10 000 轮。PIN：由 MAC 和车队密钥派生（`CONFIG_ARMOR_FLEET_SECRET`，公开固件中为空） |
| 暴露的解析器（JSON、蓝牙帧、Improv） | 用 libFuzzer、AddressSanitizer 和 UndefinedBehaviorSanitizer 做模糊测试（`fuzz/run_fuzz.sh`，带 clang 的 Linux） |
| 节点副本与共用版本偏离 | 五个节点不一致时 `tools/sync_firmware_base.py check` 失败 |

**不涵盖的内容。** 管理员手动上传的固件不会被检查。固件早于此检查的节点，只凭哈希安装第一个签名版本。密钥保护的是发布版本而不是开发板：能物理接触的人可以烧录任何东西。密钥丢失后，GitHub 更新程序会被阻止，直到通过手动上传或数据线更换公钥。签名检查和 PIN 已在主机上测试；没有独立审查。详见 [docs/SIGNED_FIRMWARE.md](docs/SIGNED_FIRMWARE.md)。

## 🔌 接口

### 代理主题

| 主题 | 内容 |
|---|---|
| `armor/node/{node_id}/telemetry`  `health`  `command`  `info` | 雷达节点：轨迹、健康、命令和信息 |
| `armor/solar/{node_id}/{device}/state` | 太阳能节点的逆变器或电池 |
| `armor/electrical/{node_id}/state`  `command`  `result` | 电气节点：读数、命令、结果 |
| `armor/alarm/{node_id}/state`  `command`  `result` | 报警节点（还有来自服务器的 `zigbee` 和 `policy`） |
| `armor/network/{node_id}/state` | 节点在网络上看到的内容 |
| `armor/health/{node_id}` | 任意节点的健康报告及其遗嘱 |
| `armor/control/{node_id}/command`  `result`  `maintenance`  and `armor/control/all/command` | 发给一个或全部节点的类型化指令、结果及计划维护信号 |
| `armor/device/{node_id}/{relay}/set`  `state`  `availability` | 节点的继电器 |
| `armor/radar/{node_id}/events`  and  `armor/server/alert` | 雷达事件；服务器发给面板的警报 |

### 模式、向量与 OpenAPI

* **34 个 JSON Schema**（`src/armor_common/schemas/`）：遥测、健康、命令、节点信息、节点健康、节点控制（命令与结果）、节点维护、太阳能逆变器和电池（含命令与结果）、电气（含命令与结果）、报警（状态、命令、结果、策略和区域）、网络（含其指令）、连接与系统事件、雷达事件、服务器警报、布防配置、设备状态、诊断令牌以及语音轮次。
* **1225 个一致性向量**（`conformance/`，34 个文件，每条消息一个），由本仓库、ARMOR-SERVER 和固件仓库的检查运行。
* **OpenAPI** `openapi/armor-server.yaml`：191 条路径、247 个操作，每个都有访问规则，且每个请求体、响应和错误都有命名模式。测试确认服务器注册的路由与描述完全一致。语音轮次以字节传输（见 [docs/CONTRACTS.md](docs/CONTRACTS.md)）。

### 命令行工具

| 工具 | 作用 |
|---|---|
| `tools/armor_project_tool.py` | 共用的 `build`、`build-test` 和 `run` 流程 |
| `tools/generate_types.py [--check]`  `generate_rest_types.py [--check]` | TypeScript 和 Kotlin 类型以及 HTTP 契约的类型 |
| `tools/make_conformance.py [--check]` | 根据用例列表写出一致性向量 |
| `tools/sync_firmware_base.py` (`check`, `sync`, `import`) | 把 `firmware_base` 写入五个节点，或检查是否偏离 |
| `tools/release_firmware.py`  `tools/firmware_sign.mjs` | 签名并发布固件版本 |
| `tools/voice_cases.py` | 与 ARMOR-VOICE-AI 共用的语音用例 |
| `tools/make_architecture.py`  `tools/make_structure.py`  `tools/universal_readme_check.py` | README 的图片和版式检查 |

## ⚙️ 配置

### 固件构建选项（Kconfig）

| 设置 | 默认值 | 作用 |
|---|---|---|
| `CONFIG_ARMOR_NODE_ID` | "" | 节点在代理上的名称 |
| `CONFIG_ARMOR_SETUP_CODE` | "" | 打开设置的代码 |
| `CONFIG_ARMOR_FLEET_SECRET` | "" | 蓝牙 PIN 的车队密钥；公开固件中为空 |
| `CONFIG_ARMOR_BLE_SETUP_MINUTES` | 10 (1 to 120) | 蓝牙设置保持开启的时间 |
| `CONFIG_ARMOR_ETH_SPI_HOST` | 1 (1 to 2) | 以太网芯片的 SPI 主机 |
| `CONFIG_ARMOR_ETH_MOSI` `MISO` `SCLK` `CS` `INT` `RST` | 11, 12, 13, 14, 10, 9 | 以太网板引脚（配置 `s3-eth`） |
| `CONFIG_ARMOR_ETH_SPI_MHZ` | 20 (1 to 40) | 以太网芯片 SPI 时钟 |
| `CONFIG_ARMOR_MQTT_URI` `USERNAME` `PASSWORD` | "" | 初始代理地址和凭据 |
| `CONFIG_ARMOR_BOOT_FACTORY_RESET` | y | 允许启动时恢复出厂设置 |
| `CONFIG_ARMOR_NTP_SERVER` | pool.ntp.org | 时间服务器 |
| `CONFIG_ARMOR_HEARTBEAT_S` | 10 (2 to 300) | 心跳间隔（秒） |
| `CONFIG_ARMOR_BOARD_S3_WIFI`  `CONFIG_ARMOR_BOARD_S3_ETH` | S3_WIFI | 镜像的开发板配置（`tools/build_node.sh NODE BOARD`） |

节点与代理之间的 TLS 链路是节点的设置（而非构建的设置）：`mqtt.tls`（默认关闭）和 `mqtt.ca_pem`（一份 PEM 证书，最大 2 KB，经过校验）；连接只信任该机构并检查代理名称。Python 库本身没有环境变量；共用启动器会在首次运行 ARMOR-SERVER 时创建被忽略的 `.env`，其中是随机密钥和随机管理员密码，不打印也不提交任何内容。

## 🚀 快速开始

**要求：** Python 3.11+（无需其他包）。检查固件基础时，五个节点仓库必须放在本仓库旁边。

```powershell
python -m pip install -e .                   # 安装库
python -m unittest discover -s tests         # 214 项测试、1225 个向量
python tools/generate_types.py --check       # 生成的类型是最新的
python tools/generate_rest_types.py --check  # HTTP 契约的类型是最新的
python tools/make_conformance.py             # 修改用例列表后重新生成向量（--check：检查是否最新）
python tools/sync_firmware_base.py check     # 共用固件没有偏离
```

## 🧪 测试

```powershell
python -m unittest discover -s tests  # 214 项
python -I tools/armor_ci_validate.py
```

| 测试文件 | 测试数 | 覆盖内容 |
|---|---|---|
| `test_contracts.py` | 68 | 每条消息、主题和拆分器及一致性向量 |
| `test_task_safety_check.py` | 23 | 查找节点不可缺少的任务的扫描 |
| `test_universal_readme_check.py`, `test_readme_tools.py` | 36 | README 版式检查与图片 |
| `test_firmware_base.py` | 13 | 共用固件基础及其同步 |
| `test_openapi.py` | 13 | OpenAPI 文件与服务器路由 |
| `test_release_firmware.py` | 12 | 固件的签名与发布 |
| `test_pretty_run.py`, `test_build_scripts.py` | 11 | 脚本的实时面板 |
| `test_generated_types.py`, `test_repository_registry.py`, `test_voice_turn.py` | 21 | 生成类型、仓库清单和语音轮次 |
| `test_alarm_codes.py`, `test_collect_errors.py`, `test_project_manifest_doc.py`, `test_firmware_fuzz.py`, `test_fuzz_validator.py` | 17 | 报警码文字、错误收集、清单指南和模糊测试环境 |

共用固件的主机测试在 `firmware_base/tests/`（C++，无需 ESP-IDF），由各节点仓库自己的检查运行。`python tools/sync_firmware_base.py check` 需要五个节点仓库放在本仓库旁边。GitHub Actions 在每次推送和拉取请求时运行 A.R.M.O.R. 基线：清单、版本、更新日志和 README 一致性的校验，然后是项目自身的构建和测试。

## 🏗️ 构建与发布

这是纯 Python 加一组工具：无需编译。版本记录在 `pyproject.toml`、`armor.project.json` 和 README 徽章中（读取自清单）；每个版本在 [CHANGELOG.md](CHANGELOG.md) 中都有对应条目。发布版本发布在 GitHub 上。固件发布工具（`tools/release_firmware.py`）为节点镜像签名并发布；它所需的密钥从不在仓库里。

## 🩺 故障排除

| 你看到 | 原因 | 处理 |
|---|---|---|
| `FIRMWARE_BASE=FAIL ... copies drifted` | 某节点手动改了共用文件 | 在 `firmware_base/` 中修改并运行 `sync`；或用 `import` 原样采用节点的文件 |
| `ARMOR-NODE-HMI: main/secret_vault.cpp is missing` | 节点仓库不在 ARMOR-COMMON 旁边 | 并排克隆 |
| `generated types are out of date` | 模式或 OpenAPI 文件变了 | 不带 `--check` 运行 `generate_types.py` 和 `generate_rest_types.py` |
| `TASK_SAFETY=FAIL no task found: the scan is broken` | 对节点源码的扫描什么也没找到 | 检查节点仓库是否在本仓库旁边 |
| `no_signature`, `bad_signature`, `checksum_mismatch`, `wrong_firmware` | 节点拒绝了某版本：签名、哈希或开发板缺失或错误 | 用 `tools/release_firmware.py` 和固件信任的发布密钥来发布 |

## 📂 仓库结构

<p align="center">
  <img src="images/repository-structure.svg" alt="Repository structure of ARMOR-COMMON" width="100%">
</p>

<details>
<summary>目录树的文本版本</summary>

```text
ARMOR-COMMON/
├── src/armor_common/
│   ├── contracts.py               主题与校验
│   ├── schema.py                  模式解释器
│   ├── envelope.py                通用信封
│   ├── voice.py                   语音契约
│   ├── schemas/                   34 个 JSON Schema
│   ├── alarm_codes.json           报警码的文字
│   └── battery_ops.json           电池操作
├── firmware_base/                 五个节点共用的固件（只此一份）
├── conformance/                   1225 条有效与无效消息
├── generated/                     TypeScript 和 Kotlin 类型（自动生成，勿编辑）
├── openapi/                       armor-server.yaml（HTTP 契约）
├── registry/                      repositories.json（清单）
├── fuzz/                          libFuzzer 目标
├── scripts/                       armor-project 启动器
├── tools/                         生成器、固件同步与发布、启动器、CI 检查
├── tests/                         214 项测试
├── docs/                          契约、固件、模糊测试
├── images/                        横幅图、图标和 README 的图片
├── .github/                       CI 工作流、仪表板通知、议题和 pull request 模板
├── armor.project.json             清单：版本、角色、成熟度
├── pyproject.toml                 包元数据、入口
├── CHANGELOG.md                   每个版本的变化
├── run.sh run.bat                 启动（共用流程）
├── build.sh build.bat             构建并测试（共用流程）
├── build-test.sh build-test.bat   构建、测试并打包
├── test.sh test.bat               只运行测试，不改版本
└── SECURITY.md SUPPORT.md CONTRIBUTING.md CODE_OF_CONDUCT.md LICENSE
```

</details>

## 🗺️ 路线图与已知限制

**当前已知限制**

* Kotlin 类型已生成，但 ARMOR-ANDROID-CONTROL **尚未使用**，它仍保留自己的解析。
* `set_thresholds` 命令只有一个 `sensitivity` 字段：真实的雷达参数要等固件存在后才会定义。
* 只有雷达节点在开发板上运行过共用固件；其他四个没有。
* 没有独立的安全审查。

**下一步**

* 让 Android 应用使用生成的 Kotlin 类型。
* 定义 `set_thresholds` 的真实雷达参数。
* 在其他四个节点的开发板上运行共用固件。

## 🌍 语言

README 和文本提供英语、西班牙语、法语、意大利语、德语、汉语、日语和欧洲葡萄牙语版本。

## 🔗 相关项目

**A.R.M.O.R.**（Autonomous Radar & Multimodal Observation Range）是一个由相互独立的仓库组成的周界安全系统。每个仓库都有自己的版本、自己的测试和自己的 README；这是整个系列：

* **ARMOR-COMMON**（本仓库） - 消息契约、验证器、一致性向量和生成的类型
* **[ARMOR-NODE-RADAR](https://github.com/JuanenRac/ARMOR-NODE-RADAR)** - 面向 ESP32-S3 的现场节点固件，配三个雷达和自带的网页面板
* **[ARMOR-NODE-SOLAR](https://github.com/JuanenRac/ARMOR-NODE-SOLAR)** - 太阳能逆变器和电池的协议，以及网关节点的消息
* **[ARMOR-NODE-ELECTRICAL](https://github.com/JuanenRac/ARMOR-NODE-ELECTRICAL)** - 电气节点：电表、电网读数的消息和切换规则
* **[ARMOR-NODE-ALARM](https://github.com/JuanenRac/ARMOR-NODE-ALARM)** - 报警节点与面板：防区、布防、延时、警笛和 PIN，可配合服务器也可独立使用
* **[ARMOR-NODE-HMI](https://github.com/JuanenRac/ARMOR-NODE-HMI)** - 触摸面板：壁挂屏幕上的系统状态、布防与确认，以及语音助手的所在
* **[ARMOR-NETWORK](https://github.com/JuanenRac/ARMOR-NETWORK)** - 本地网络：其设备、互联网以及变化
* **[ARMOR-SERVER](https://github.com/JuanenRac/ARMOR-SERVER)** - 中央协调器：遥测、报警、设备、太阳能读数和摄像头
* **[ARMOR-STUDIO](https://github.com/JuanenRac/ARMOR-STUDIO)** - 网页控制台：摄像头、雷达、报警、太阳能以及 2D/3D 场地设计器
* **[ARMOR-ANDROID-CONTROL](https://github.com/JuanenRac/ARMOR-ANDROID-CONTROL)** - 带实时 2D/3D 雷达的 Android 操作员客户端
* **[ARMOR-IOS-CONTROL](https://github.com/JuanenRac/ARMOR-IOS-CONTROL)** - iPhone 操作员客户端
* **[ARMOR-SERVER-AI](https://github.com/JuanenRac/ARMOR-SERVER-AI)** - 视觉推理策略，会解释其决策且从不驱动设备
* **[ARMOR-VISION](https://github.com/JuanenRac/ARMOR-VISION)** - 面向 Jetson Orin NX 的摄像头区域、遮罩和检测规则
* **[ARMOR-VOICE-AI](https://github.com/JuanenRac/ARMOR-VOICE-AI)** - 离线语音意图，附带无法伪造的确认
* **[ARMOR-HARDWARE](https://github.com/JuanenRac/ARMOR-HARDWARE)** - 外壳、电子器件和台架验收矩阵
* **[ARMOR-DEVOPS](https://github.com/JuanenRac/ARMOR-DEVOPS)** - 部署、CM5 测试台、备份和 TLS
* **[ARMOR-SIMULATOR](https://github.com/JuanenRac/ARMOR-SIMULATOR)** - 带可重复故障的离线遥测模拟器
* **[ARMOR-UPDATER](https://github.com/JuanenRac/ARMOR-UPDATER)** - 检测、安装和更新生态系统自身的仓库
* **[ARMOR-DOCS](https://github.com/JuanenRac/ARMOR-DOCS)** - 架构、安全基线和能力矩阵

## 📚 文档

* [契约](docs/CONTRACTS.md)：每条消息、主题以及如何修改契约
* [固件基础](docs/FIRMWARE_BASE.md)：五个节点共用什么以及如何同步
* [签名固件](docs/SIGNED_FIRMWARE.md)：发布版本的签名及其不涵盖的内容
* [模糊测试](docs/FUZZING.md)：三个解析目标及运行方法
* [项目清单](docs/PROJECT_MANIFEST.md)：每个仓库的 `armor.project.json`
* [README 的图片](docs/README_PICTURES.md)：架构图和仓库结构图如何绘制
* [能力矩阵：哪些已被证明，哪些没有](https://github.com/JuanenRac/ARMOR-DOCS/blob/main/docs/CAPABILITY_MATRIX.md)
* [项目目录：版本以及各仓库之间如何相互依赖](https://github.com/JuanenRac/ARMOR-DOCS/blob/main/docs/PROJECT_CATALOG.md)
* [本仓库的更新日志](CHANGELOG.md)

## 🤝 参与贡献与社区

* 提交 pull request 之前，请运行 `python -I tools/armor_ci_validate.py` 和测试：两者都必须通过。请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 和[行为准则](CODE_OF_CONDUCT.md)。
* README 提供八种语言，由 ARMOR-DOCS 中的源文件生成：文本的修改在那里进行。
* 组件之间消息的变更从 ARMOR-COMMON 开始。
* 不要把仅仅构建过的东西描述为已在板子上运行。
* 请私下报告漏洞：[SECURITY.md](SECURITY.md)。问题、想法和报告：electrohobby3d@gmail.com（[SUPPORT.md](SUPPORT.md)）。

## 👤 作者

**JuanenRac (Electro Hobby 3D)** · electrohobby3d@gmail.com

## 📜 许可证

GPL-3.0-or-later - 见 [LICENSE](LICENSE)。
