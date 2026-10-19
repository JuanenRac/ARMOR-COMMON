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
  <a href="README_zho.md">🇨🇳 简体中文</a> |
  <a href="README_jpn.md">🇯🇵 日本語</a> |
  🇵🇹 <b>Português</b>
</p>

### Contratos de mensagens, validação, a base de firmware que os nós partilham e o lançador de projetos partilhado

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0-blue.svg" alt="GPL 3.0">
  <img src="https://img.shields.io/badge/Language-Python%203.11%2B-3776ab.svg" alt="Language">
  <img src="https://img.shields.io/badge/Dependencies-none-2ea44f.svg" alt="Dependencies">
  <img src="https://img.shields.io/badge/Vectors-685-00E5FF.svg" alt="Vectors">
  <img src="https://img.shields.io/badge/Version-0.6.8-0f6cbd.svg" alt="Version">
  <img src="https://img.shields.io/badge/Maturity-established-2EA44F.svg" alt="Maturity">
</p>

---

**Verificação de honestidade - o que funciona hoje:** Os esquemas (telemetria, saúde, comando, informação do nó, inversor e bateria solares, elétrico, alarme com o seu comando e resultado, e rede), o validador Python, os 685 vetores de conformidade, os tipos TypeScript e Kotlin gerados, o ficheiro OpenAPI do servidor (136 caminhos), a base de firmware partilhada pelos cinco nós e o lançador de projetos partilhado são reais e testados (89 testes). O ficheiro Kotlin é gerado mas **ainda não é consumido** pelo ARMOR-ANDROID-CONTROL (que mantém a sua própria leitura), e o comando `set_thresholds` leva um único campo `sensitivity` porque os parâmetros reais do radar só ficam definidos quando existir firmware.

---

## 📋 Num relance

| | |
|---|---|
| Versão | `0.6.8` |
| Maturidade | Estabelecido |
| Testes | 89 (`python -m unittest discover -s tests`) and 685 conformance vectors |
| Tecnologia | Python 3.11+ / JSON Schema / OpenAPI |
| Em hardware real | Só o nó radar funcionou numa placa: as suas mensagens são as que o servidor do CM5, o Studio e a aplicação Android falam todos os dias; as mensagens dos outros nós são verificadas contra substitutos |

## 🎯 Visão geral

O **ARMOR-COMMON** é dono do que significa cada mensagem do A.R.M.O.R. Os nós de radar, os nós de ligação solares e o simulador produzem estas mensagens; o servidor, a IA visual e o serviço de voz consomem-nas. Se dois projetos discordarem sobre um campo, este repositório decide.

* **Uma única fonte de verdade:** esquemas JSON em `src/armor_common/schemas/` para telemetria, saúde, comando, informação do nó, as duas mensagens solares (inversor, bateria com células e capacidades), as mensagens elétricas (leituras, comando, resultado), as mensagens de alarme (estado, comando, resultado) e a mensagem de rede. Campos desconhecidos e combinações impossíveis são recusados.
* **Um validador que não pode saltar uma regra:** interpreta o esquema diretamente e recusa um esquema que use uma palavra-chave que não implementa.
* **Vetores de conformidade:** 685 cargas aceites e recusadas executadas por cada implementação (Python aqui, TypeScript no ARMOR-SERVER, as verificações dos repositórios de firmware), de modo que um desvio faz falhar uma compilação.
* **Clientes gerados:** os tipos TypeScript e Kotlin saem dos esquemas (`tools/generate_types.py --check` mantém-nos atuais).
* **Contrato HTTP:** `openapi/armor-server.yaml` descreve cada rota do servidor (163 caminhos, 215 operações), a sua regra de acesso e um esquema com nome para cada corpo de pedido, resposta e erro, e um teste verifica que as rotas que o servidor regista são exatamente as que descreve (método e caminho).
* **Base de firmware:** `firmware_base/` guarda uma só vez cada ficheiro que os cinco nós partilham (rede, definições e utilizadores, servidor do painel web e login, certificado HTTPS, registo, Bluetooth com emparelhamento por PIN, verificação de atualizações assinadas; relés e Zigbee nos nós que os têm); `tools/sync_firmware_base.py` escreve-o em cada nó e verifica que nenhuma cópia se desviou ([o guia](docs/FIRMWARE_BASE.md), [firmware assinado](docs/SIGNED_FIRMWARE.md)).
* **Lançador partilhado:** `tools/armor_project_tool.py` dá a cada repositório da família o mesmo fluxo `build`, `build-test` e `run`, e `tools/armor_ci_validate.py` as mesmas verificações de CI.
* **Ligação TLS opcional ao broker na base partilhada dos nós:** `firmware_base` traz o interruptor `mqtt.tls` e o texto `mqtt.ca_pem` (um certificado PEM, no máximo 2 KB, validado), a ligação que confia só nessa autoridade e verifica o nome do broker, e os testes no computador partilhados pelos cinco nós; desativada por predefinição.
* **Saúde dos nós e perfis de armar:** a mensagem `node_health` (o mesmo relatório de um nó de radar, solar, elétrico, de alarme ou de painel de parede) e o `arm_profile` (uma forma com nome de armar: que zonas vigiam, os atrasos, a sirene e com que insistência o servidor avisa, dentro do comando de armar) têm os seus esquemas, vetores de conformidade, tipos TypeScript e Kotlin gerados, rotas OpenAPI e o código de firmware partilhado que constrói o relatório.
* **Eventos de ligação e de sistema do histórico:** os esquemas `connection_event`, `system_event` e `connection_client` (o que o histórico do servidor diz dos clientes que se ligam e do próprio sistema, com um vocabulário fixo e nenhum campo onde possa ir um segredo), os seus vetores de conformidade, os tipos TypeScript e Kotlin gerados e a rota OpenAPI que lista os clientes.

## 🧩 Papel no A.R.M.O.R.

O ARMOR-COMMON é o que mantém a família a falar a mesma língua. Cada mensagem entre um nó e o [ARMOR-SERVER](https://github.com/JuanenRac/ARMOR-SERVER) é definida aqui uma vez, com os vetores que toda a implementação tem de passar; aqui vive também o contrato HTTP do servidor; e o firmware que os cinco nós partilham ([ARMOR-RADAR](https://github.com/JuanenRac/ARMOR-RADAR), [ARMOR-SOLAR](https://github.com/JuanenRac/ARMOR-SOLAR), [ARMOR-ELECTRICAL](https://github.com/JuanenRac/ARMOR-ELECTRICAL), [ARMOR-ALARM](https://github.com/JuanenRac/ARMOR-ALARM), [ARMOR-HMI](https://github.com/JuanenRac/ARMOR-HMI)) é guardado uma vez e copiado para eles por uma ferramenta. Não guarda nenhum segredo e não executa nada em produção.

## 🔄 Arquitetura

```mermaid
flowchart LR
    S["JSON Schemas (source of truth)"] --> P["armor_common (Python validator)"]
    S --> G["generated TS + Kotlin types"]
    S --> V["conformance vectors"]
    V --> P
    V --> T["ARMOR-SERVER tests"]
    V --> X["ARMOR-SOLAR and ARMOR-ELECTRICAL checks"]
    S --> O["OpenAPI (HTTP contract)"]
```

## 📂 Estrutura do repositório

```text
ARMOR-COMMON/
├── src/armor_common/   contracts, schema (validator), envelope, schemas/*.json (the node messages, the alarm, electrical and network ones, the relay, zone-feed, alert and orders ones)
├── conformance/        accepted and rejected payloads shared by every implementation
├── firmware_base/      the firmware that the five nodes share, once (synced into each by tools/sync_firmware_base.py)
├── generated/          TypeScript and Kotlin types (generated, do not edit)
├── openapi/            armor-server.yaml
├── tools/              armor_project_tool.py, generate_types.py, make_conformance.py, sync_firmware_base.py, release_firmware.py, firmware_sign.mjs
├── tests/              unit tests and conformance runner
└── docs/               contracts guide, the shared firmware base
```

## 🛠️ Ambiente de desenvolvimento

**Requisitos:** Python 3.11+

```powershell
python -m pip install -e .
python -m unittest discover -s tests      # 89 tests, 685 conformance vectors
python tools/generate_types.py --check    # generated types are current
python tools/make_conformance.py          # regenerate the vectors after editing the case list (--check: they are current)
python tools/sync_firmware_base.py check  # the firmware the node projects share has not drifted (see docs/FIRMWARE_BASE.md)
```

Tópicos do broker: `armor/node/{node_id}/telemetry | health | command | info`, `armor/solar/{node_id}/{device}/state`, `armor/electrical/{node_id}/state | command | result`, `armor/alarm/{node_id}/state | command | result` e `armor/network/{node_id}/state`. Veja o [guia de contratos](docs/CONTRACTS.md). O lançador partilhado cria um `.env` ignorado na primeira execução do ARMOR-SERVER com segredos aleatórios e uma palavra-passe de administrador aleatória; nada é impresso nem enviado.

## 🔗 Projetos relacionados

O **A.R.M.O.R.** (Autonomous Radar & Multimodal Observation Range) é um sistema de segurança perimetral feito de repositórios independentes. Cada um tem a sua própria versão, os seus próprios testes e o seu próprio README; esta é a família:

* **ARMOR-COMMON** (este repositório) - Contratos de mensagens, validadores, vetores de conformidade e tipos gerados
* **[ARMOR-RADAR](https://github.com/JuanenRac/ARMOR-RADAR)** - Firmware de nó de campo para ESP32-S3 com três radares e o seu próprio painel web
* **[ARMOR-SOLAR](https://github.com/JuanenRac/ARMOR-SOLAR)** - Protocolos de inversores e baterias solares e as mensagens de um nó de ligação
* **[ARMOR-ELECTRICAL](https://github.com/JuanenRac/ARMOR-ELECTRICAL)** - Nó elétrico: contadores, a mensagem das leituras da rede e as regras de comutação
* **[ARMOR-ALARM](https://github.com/JuanenRac/ARMOR-ALARM)** - Nó e central de alarme: zonas, armar, atrasos, sirene e PIN, com o servidor ou sem ele
* **[ARMOR-HMI](https://github.com/JuanenRac/ARMOR-HMI)** - Painel tátil: o estado do sistema num ecrã de parede, armar e reconhecer, e a casa do assistente de voz
* **[ARMOR-NETWORK](https://github.com/JuanenRac/ARMOR-NETWORK)** - A rede local: os seus dispositivos, a internet e o que muda
* **[ARMOR-SERVER](https://github.com/JuanenRac/ARMOR-SERVER)** - Coordenador central: telemetria, alarmes, dispositivos, leituras solares e câmaras
* **[ARMOR-STUDIO](https://github.com/JuanenRac/ARMOR-STUDIO)** - Consola web: câmaras, radar, alarmes, energia solar e o desenhador de local 2D/3D
* **[ARMOR-ANDROID-CONTROL](https://github.com/JuanenRac/ARMOR-ANDROID-CONTROL)** - Cliente Android de operador com um radar 2D/3D em direto
* **[ARMOR-SERVER-AI](https://github.com/JuanenRac/ARMOR-SERVER-AI)** - Política de inferência visual que explica as suas decisões e nunca atua
* **[ARMOR-VISION](https://github.com/JuanenRac/ARMOR-VISION)** - Zonas de câmara, máscaras e regras de deteção para o Jetson Orin NX
* **[ARMOR-VOICE-AI](https://github.com/JuanenRac/ARMOR-VOICE-AI)** - Intenções de voz offline com uma confirmação que não se pode falsificar
* **[ARMOR-HARDWARE](https://github.com/JuanenRac/ARMOR-HARDWARE)** - Caixas, eletrónica e a matriz de aceitação de bancada
* **[ARMOR-DEVOPS](https://github.com/JuanenRac/ARMOR-DEVOPS)** - Implementação, a bancada de testes CM5, cópias de segurança e TLS
* **[ARMOR-SIMULATOR](https://github.com/JuanenRac/ARMOR-SIMULATOR)** - Simulador de telemetria offline com falhas repetíveis
* **[ARMOR-UPDATER](https://github.com/JuanenRac/ARMOR-UPDATER)** - Deteta, instala e atualiza os próprios repositórios do ecossistema
* **[ARMOR-DOCS](https://github.com/JuanenRac/ARMOR-DOCS)** - Arquitetura, linha de base de segurança e a matriz de capacidades

## 📚 Documentação e comunidade

Onde ler mais:

* [Matriz de capacidades: o que está provado e o que não](https://github.com/JuanenRac/ARMOR-DOCS/blob/main/docs/CAPABILITY_MATRIX.md)
* [Catálogo de projetos: versões e como os repositórios dependem uns dos outros](https://github.com/JuanenRac/ARMOR-DOCS/blob/main/docs/PROJECT_CATALOG.md)
* [Registo de alterações deste repositório](CHANGELOG.md)
* [Licença (GPL-3.0-or-later)](LICENSE)
* Perguntas, ideias e relatórios: electrohobby3d@gmail.com

## 👤 AUTOR

**JuanenRac (Electro Hobby 3D)** · electrohobby3d@gmail.com

## 📜 LICENÇA

GPL-3.0-or-later - veja [LICENSE](LICENSE).
