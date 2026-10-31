<p align="center">
  <img src="images/ARMOR_BANNER.svg" alt="ARMOR-COMMON-Banner" width="100%">
</p>

# 🧾 ARMOR-COMMON

<p align="center">
  <a href="README.md">🇺🇸 English</a> |
  <a href="README_spa.md">🇪🇸 Español</a> |
  <a href="README_fra.md">🇫🇷 Français</a> |
  <a href="README_ita.md">🇮🇹 Italiano</a> |
  🇩🇪 <b>Deutsch</b> |
  <a href="README_zho.md">🇨🇳 简体中文</a> |
  <a href="README_jpn.md">🇯🇵 日本語</a> |
  <a href="README_por.md">🇵🇹 Português</a>
</p>

### Nachrichtenverträge, Validierung, die von den Knoten geteilte Firmware-Basis und der gemeinsame Projektstarter

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0--or--later-blue.svg" alt="GPL 3.0 oder neuer">
  <img src="https://img.shields.io/badge/Language-Python%203.11%2B-3776ab.svg" alt="Sprache">
  <img src="https://img.shields.io/badge/Dependencies-none-2ea44f.svg" alt="Dependencies">
  <img src="https://img.shields.io/badge/Vectors-1225-00E5FF.svg" alt="Vectors">
  <img src="https://img.shields.io/badge/Tests-237%20passing-2ea44f.svg" alt="Tests">
  <img src="https://img.shields.io/badge/Version-0.7.9-0f6cbd.svg" alt="Version">
  <img src="https://img.shields.io/badge/Maturity-established-2EA44F.svg" alt="Reifegrad">
</p>

---

**Ehrlichkeitsprüfung - was heute läuft:** Die Schemas (Telemetrie, Zustand, Befehl, Knoteninformation, Solar-Wechselrichter und -Batterie, Elektro, Alarm mit Befehl und Ergebnis sowie Netzwerk), der Python-Validator, die 1225 Konformitätsvektoren, die erzeugten TypeScript- und Kotlin-Typen, die OpenAPI-Datei des Servers (191 Pfade), die von den fünf Knoten geteilte Firmware-Basis und der gemeinsame Projektstarter sind real und getestet (237 Tests). Die Kotlin-Datei wird erzeugt, aber **noch nicht verwendet** von ARMOR-ANDROID-CONTROL (das sein eigenes Parsen behält), und der Befehl `set_thresholds` trägt nur ein Feld `sensitivity`, weil die echten Radarparameter erst definiert sind, wenn Firmware existiert.

---

## 📋 Auf einen Blick

| | |
|---|---|
| Version | `0.7.9` |
| Reifegrad | Etabliert |
| Rolle | Gemeinsame Verträge, Validator und Firmware-Basis der Familie |
| Technik | Python 3.11+, JSON Schema, OpenAPI; Firmware-Basis in C++ (ESP-IDF) |
| Tests | 237 (`python -m unittest discover -s tests`), 1225 Konformitätsvektoren |
| Vertrag | 34 JSON-Schemas, 191 HTTP-Pfade (247 Operationen) |
| Läuft auf | Jeder Computer (Bibliothek und Werkzeuge); die Firmware-Basis läuft in den fünf Knoten |
| Auf echter Hardware | Nur der Radar-Knoten hat die gemeinsame Firmware auf einer Platine ausgeführt; die anderen vier nicht |
| Lizenz | GPL-3.0-or-later |

**Springe zu:** [Überblick](#-überblick) · [Architektur](#-architektur) · [Funktionen](#-funktionen) · [Sicherheit](#-sicherheit-und-schutz) · [Schnittstellen](#-schnittstellen) · [Konfiguration](#-konfiguration) · [Schnellstart](#-schnellstart) · [Tests](#-tests) · [Probleme](#-fehlerbehebung) · [Struktur](#-struktur-des-repositorys) · [Verwandte](#-verwandte-projekte)

## 🚦 Projektstatus

Jede Zeile ist ein Teil dieses Repositorys, und die Ampel sagt, wie weit er heute ist. Sie beruht auf dem, was das Repository zeigen kann (Tests, Builds, Läufe), nicht auf dem, was geplant ist.

🟢 Fertig und überprüft · 🟡 Funktioniert, mit bekannten Grenzen · 🟠 Teilweise fertig oder noch nicht überprüft · 🔴 Nicht gemacht oder funktioniert nicht

| Bereich | Stand | Was das hier bedeutet |
|---|---|---|
| Software | 🟢 | Die Schemas, der Python-Validator, die erzeugten TypeScript- und Kotlin-Typen, die OpenAPI-Datei des Servers und die von den fünf Knoten gemeinsam genutzte Firmware-Basis sind vorhanden. |
| Tests | 🟢 | 237 Tests und 1225 Konformitätsvektoren bestehen; die JSON-, Bluetooth- und Improv-Parser der Firmware werden außerdem mit libFuzzer gefuzzt. |
| Protokolle und Daten | 🟡 | Nur die Nachrichten des Radar-Knotens werden täglich mit einer echten Platine und dem Server genutzt; die der anderen Knoten werden gegen Nachbildungen geprüft. |
| Integration | 🟡 | Es wird geprüft, dass die Firmware-Basis in jedem Knoten identisch ist; die Kotlin-Typen sind erzeugt, werden von der Android-App aber noch nicht genutzt, sie behält ihr eigenes Parsing. |
| Hardware | 🟠 | Nur der Radar-Knoten hat diese gemeinsame Firmware auf einer Platine ausgeführt; die anderen vier Knoten nicht. |
| Sicherheit | 🟡 | Die Prüfung der Firmware-Signatur und die Ableitung der Bluetooth-PIN sind auf dem Host getestet; es gab keine unabhängige Prüfung. |
| Dokumentation | 🟢 | Acht Sprachen, die OpenAPI-Datei, der Konformitätsleitfaden und das Änderungsprotokoll sind aktuell. |

## 🎯 Überblick

**ARMOR-COMMON** besitzt die Bedeutung jeder A.R.M.O.R.-Nachricht. Radarknoten, Solar-Gateway-Knoten und der Simulator erzeugen diese Nachrichten; der Server, die visuelle KI und der Sprachdienst verbrauchen sie. Wenn zwei Projekte über ein Feld uneins sind, entscheidet dieses Repository.

* **Eine einzige Quelle der Wahrheit:** JSON-Schemas in `src/armor_common/schemas/` für Telemetrie, Zustand, Befehl, Knoteninformation, die beiden Solar-Nachrichten (Wechselrichter, Batterie mit Zellen und Kapazitäten), die Elektro-Nachrichten (Messwerte, Befehl, Ergebnis), die Alarmnachrichten (Zustand, Befehl, Ergebnis) und die Netzwerknachricht. Unbekannte Felder und unmögliche Kombinationen werden abgelehnt.
* **Ein Validator, der keine Regel überspringen kann:** er interpretiert das Schema direkt und lehnt ein Schema ab, das ein nicht implementiertes Schlüsselwort verwendet.
* **Konformitätsvektoren:** 1225 akzeptierte und abgelehnte Nutzlasten, von jeder Implementierung ausgeführt (hier Python, TypeScript in ARMOR-SERVER, die Prüfungen der Firmware-Repositories), sodass eine Abweichung einen Build scheitern lässt.
* **Erzeugte Clients:** TypeScript- und Kotlin-Typen entstehen aus den Schemas (`tools/generate_types.py --check` hält sie aktuell).
* **HTTP-Vertrag:** `openapi/armor-server.yaml` beschreibt jede Route des Servers (191 Pfade, 247 Operationen), ihre Zugriffsregel und ein benanntes Schema für jeden Anfragekörper, jede Antwort und jeden Fehler, und ein Test prüft, dass die vom Server registrierten Routen genau die beschriebenen sind (Methode und Pfad).
* **Firmware-Basis:** `firmware_base/` hält jede von den fünf Knoten geteilte Datei einmal (Netzwerk, Einstellungen und Benutzer, Panel-Server und Login, HTTPS-Zertifikat, Log, Bluetooth mit PIN-Kopplung, Prüfung signierter Updates; Relais und Zigbee in den Knoten, die sie haben); `tools/sync_firmware_base.py` schreibt sie in jeden Knoten und prüft, dass keine Kopie abweicht ([die Anleitung](docs/FIRMWARE_BASE.md), [signierte Firmware](docs/SIGNED_FIRMWARE.md)).
* **Gemeinsamer Starter:** `tools/armor_project_tool.py` gibt jedem Repository der Familie denselben Ablauf `build`, `build-test` und `run`, und `tools/armor_ci_validate.py` dieselben CI-Prüfungen.
* **Optionale TLS-Verbindung zum Broker in der gemeinsamen Knotenbasis:** `firmware_base` enthält den Schalter `mqtt.tls` und den Text `mqtt.ca_pem` (ein PEM-Zertifikat, höchstens 2 KB, geprüft), die Verbindung, die nur dieser Stelle vertraut und den Namen des Brokers prüft, und die Host-Tests, die sich die fünf Knoten teilen; standardmäßig aus.
* **Zustand der Knoten und Scharfschaltprofile:** Die Nachricht `node_health` (derselbe Bericht von einem Radar-, Solar-, Elektro-, Alarm- oder Wandpanel-Knoten) und das `arm_profile` (eine benannte Art des Scharfschaltens: welche Zonen überwachen, die Verzögerungen, die Sirene und wie nachdrücklich der Server informiert, im Scharfschaltbefehl) haben ihre Schemas, Konformitätsvektoren, erzeugte TypeScript- und Kotlin-Typen, OpenAPI-Routen und den gemeinsamen Firmware-Code, der den Bericht baut.
* **Verbindungs- und Systemereignisse des Verlaufs:** die Schemas `connection_event`, `system_event` und `connection_client` (was der Verlauf des Servers über die sich verbindenden Clients und über das System selbst sagt, mit festem Vokabular und ohne Feld, in dem ein Geheimnis stehen könnte), ihre Konformitätsvektoren, die erzeugten TypeScript- und Kotlin-Typen und die OpenAPI-Route, die die Clients auflistet.
* **Diagnose und Messqualität im Vertrag:** Der Bericht über unsaubere Starts, das Core-Dump, die Sicherheitsprüfung der Einstellungen, das Diagnosepaket, die Radar-Ereignisse und die Nachrichten des schreibgeschützten Diagnose-Tokens haben ihre Schemas, Konformitätsvektoren und generierten Typen; ein Zählerkanal kann das Alter seiner Messung und seinen Fehlerzähler tragen, und eine Wechselrichter-Nachricht kann die Werte nennen, die der Knoten an einer Grenze festgehalten hat.

## 🧩 Rolle in A.R.M.O.R.

ARMOR-COMMON sorgt dafür, dass die Familie dieselbe Sprache spricht. Jede Nachricht zwischen einem Knoten und [ARMOR-SERVER](https://github.com/JuanenRac/ARMOR-SERVER) ist hier einmal definiert, mit den Vektoren, die jede Implementierung bestehen muss; hier lebt auch der HTTP-Vertrag des Servers; und die Firmware, die die fünf Knoten teilen ([ARMOR-NODE-RADAR](https://github.com/JuanenRac/ARMOR-NODE-RADAR), [ARMOR-NODE-SOLAR](https://github.com/JuanenRac/ARMOR-NODE-SOLAR), [ARMOR-NODE-ELECTRICAL](https://github.com/JuanenRac/ARMOR-NODE-ELECTRICAL), [ARMOR-NODE-ALARM](https://github.com/JuanenRac/ARMOR-NODE-ALARM), [ARMOR-NODE-HMI](https://github.com/JuanenRac/ARMOR-NODE-HMI)), wird einmal gehalten und von einem Werkzeug in sie kopiert. Es enthält kein Geheimnis und führt nichts in Produktion aus.

| Er spricht mit | Wie | Wozu |
|---|---|---|
| ARMOR-SERVER | führt die Vektoren aus; setzt jede OpenAPI-Route um | Vektoren, OpenAPI |
| ARMOR-STUDIO | hält eine Kopie der erzeugten Typen; ein Test schlägt bei Abweichung fehl | erzeugtes TypeScript |
| ARMOR-ANDROID-CONTROL | hat eigenes Parsing; die Kotlin-Typen werden erzeugt, aber nicht genutzt | erzeugtes Kotlin |
| ARMOR-NODE-RADAR, SOLAR, ELECTRICAL, ALARM, HMI | erhalten firmware_base mit `tools/sync_firmware_base.py` | kopierte Firmware |
| ARMOR-DOCS, ARMOR-DEVOPS, ARMOR-UPDATER | lesen `registry/repositories.json`, die eine Liste der Repositorys | das Register |

## 🏛️ Architektur

<p align="center">
  <img src="images/architecture.svg" alt="ARMOR-COMMON architecture: who uses it, what the repository owns (schemas, vectors, validator, generated types, OpenAPI, firmware base) and who receives it" width="100%">
</p>

<details>
<summary>Textversion des Diagramms (Mermaid)</summary>

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

## ✨ Funktionen

### Eine Nachricht hinzufügen oder ändern

1. Das Schema in `src/armor_common/schemas/` bearbeiten (und `docs/CONTRACTS.md`, wenn sich die Bedeutung ändert).
2. Die Fälle in die Liste eintragen und `python tools/make_conformance.py` ausführen.
3. `python tools/generate_types.py` und `python tools/generate_rest_types.py` ausführen, um die TypeScript- und Kotlin-Typen zu erneuern.
4. `openapi/armor-server.yaml` aktualisieren, wenn eine Route beteiligt ist; `tests/test_openapi.py` vergleicht sie mit den Routen des Servers.
5. Server und Knoten führen dann dieselben Vektoren aus, ein Widerspruch lässt also den Build scheitern.

### Die Firmware-Basis

`firmware_base/` hält jede Datei, die die fünf Knoten teilen, genau einmal: Netzwerk, Einstellungen und Benutzer, den Webpanel-Server samt Anmeldung, das HTTPS-Zertifikat, das Protokoll, Bluetooth mit PIN-Kopplung, die Prüfung eines signierten Updates, den Knotenzustandsbericht, den Wächter, der einen Knoten in Not neu startet, die typisierten Befehle des Servers und, wo vorhanden, Relais und Zigbee. `tools/sync_firmware_base.py` schreibt sie in jeden Knoten und prüft, dass keine Kopie abweicht (siehe [docs/FIRMWARE_BASE.md](docs/FIRMWARE_BASE.md) und [docs/SIGNED_FIRMWARE.md](docs/SIGNED_FIRMWARE.md)). Entscheidungen ohne Hardware stehen in `core/` und werden auf dem Rechner getestet; `main/` liest die echten Werte.

## 🔒 Sicherheit und Schutz

| Bedrohung | Abwehr |
|---|---|
| Ein unbekanntes Feld oder eine unmögliche Kombination | `additionalProperties: false`; der Validator interpretiert das Schema und lehnt eines mit nicht umgesetztem Schlüsselwort ab |
| Telemetrie ohne Obergrenze, die einen Knoten erschöpft | Höchstens 15 Spuren (5 je 3 Sensoren) und Lux 0 bis 200 000 |
| Ein Befehl außerhalb der Liste | Positivliste: `calibrate`, `set_thresholds` (Empfindlichkeit 1 bis 10), `restart`; der Abonnent weist den Rest vor der Hardware ab |
| Ein Topic, das nicht zur Knoten-ID im Inhalt passt | Der Verbraucher weist die Abweichung ab |
| Eine gefälschte Firmware auf GitHub | Das Image muss zu seiner `.sha256` passen und eine Ed25519-Signatur dieses Hashes tragen, geprüft mit dem öffentlichen Schlüssel in `firmware_base/core/fw_trust.hpp`; sonst ändert sich nichts |
| Der private Release-Schlüssel gelangt nach außen | Sie liegt außerhalb jedes Repositorys, der CI und der Releases (PKCS#8, Modus 0600); `release_firmware.py` veröffentlicht nicht, wenn der Schlüssel nicht der ist, dem die Firmware vertraut |
| Knotenpasswörter und Bluetooth-PIN | Passwörter: PBKDF2-HMAC-SHA256, 10 000 Runden. PIN: aus MAC und Flottengeheimnis abgeleitet (`CONFIG_ARMOR_FLEET_SECRET`, in öffentlicher Firmware leer) |
| Offene Parser (JSON, Bluetooth-Frames, Improv) | Fuzzing mit libFuzzer, AddressSanitizer und UndefinedBehaviorSanitizer (`fuzz/run_fuzz.sh`, Linux mit clang) |
| Die Kopie eines Knotens weicht von der gemeinsamen ab | `tools/sync_firmware_base.py check` schlägt fehl, wenn die fünf Knoten nicht identisch sind |

**Was es nicht abdeckt.** Eine von Hand durch einen Administrator hochgeladene Firmware wird nicht geprüft. Ein Knoten mit einer Firmware vor dieser Prüfung installiert das erste signierte Release allein anhand des Hashes. Der Schlüssel schützt Releases, nicht Platinen: Mit physischem Zugriff kann jeder alles flashen. Geht der Schlüssel verloren, ist der GitHub-Updater blockiert, bis der öffentliche Schlüssel per manuellem Upload oder Kabel ersetzt wird. Die Signaturprüfung und die PIN sind auf dem Rechner getestet; eine unabhängige Prüfung gab es nicht. Mehr in [docs/SIGNED_FIRMWARE.md](docs/SIGNED_FIRMWARE.md).

## 🔌 Schnittstellen

### Broker-Topics

| Topic | Was es trägt |
|---|---|
| `armor/node/{node_id}/telemetry`  `health`  `command`  `info` | ein Radar-Knoten: Spuren, Zustand, Befehle und Information |
| `armor/solar/{node_id}/{device}/state` | ein Wechselrichter oder eine Batterie eines Solar-Knotens |
| `armor/electrical/{node_id}/state`  `command`  `result` | der Elektro-Knoten: Messwerte, Befehl, Ergebnis |
| `armor/alarm/{node_id}/state`  `command`  `result` | der Alarm-Knoten (auch `zigbee` und `policy` vom Server) |
| `armor/network/{node_id}/state` | was ein Knoten im Netz sieht |
| `armor/health/{node_id}` | der Zustandsbericht jedes Knotens und sein Letzter Wille |
| `armor/control/{node_id}/command`  `result`  `maintenance`  and `armor/control/all/command` | typisierte Befehle an einen oder alle Knoten, ihr Ergebnis und das Wartungssignal |
| `armor/device/{node_id}/{relay}/set`  `state`  `availability` | ein Relais eines Knotens |
| `armor/radar/{node_id}/events`  and  `armor/server/alert` | Radar-Ereignisse; Alarme, die der Server an die Panels sendet |

### Schemas, Vektoren und OpenAPI

* **34 JSON-Schemas** in `src/armor_common/schemas/`: Telemetrie, Zustand, Befehl, Knoteninformation, Knotenzustand, Knotensteuerung (Befehl und Ergebnis), Knotenwartung, Solar-Wechselrichter und -Batterie (mit Befehlen und Ergebnissen), Elektro (mit Befehl und Ergebnis), Alarm (Zustand, Befehl, Ergebnis, Richtlinie und Zonen), Netzwerk (mit Aufträgen), Verbindungs- und Systemereignisse, Radar-Ereignisse, Server-Alarm, Scharfschaltprofil, Gerätezustand, Diagnose-Token und der Sprachturn.
* **1225 Konformitätsvektoren** in `conformance/` (34 Dateien, eine je Nachricht), ausgeführt von diesem Repository, von ARMOR-SERVER und von den Prüfungen der Firmware-Repositorys.
* **OpenAPI** `openapi/armor-server.yaml`: 191 Pfade und 247 Operationen, jeweils mit Zugriffsregel und einem benannten Schema für jeden Inhalt, jede Antwort und jeden Fehler. Ein Test prüft, dass die vom Server registrierten Routen genau die beschriebenen sind. Der Sprachturn wird als Bytes übertragen (siehe [docs/CONTRACTS.md](docs/CONTRACTS.md)).

### Kommandozeilen-Werkzeuge

| Werkzeug | Was es tut |
|---|---|
| `tools/armor_project_tool.py` | der gemeinsame Ablauf `build`, `build-test` und `run` |
| `tools/generate_types.py [--check]`  `generate_rest_types.py [--check]` | TypeScript- und Kotlin-Typen und die des HTTP-Vertrags |
| `tools/make_conformance.py [--check]` | schreibt die Konformitätsvektoren aus der Fallliste |
| `tools/sync_firmware_base.py` (`check`, `sync`, `import`) | schreibt `firmware_base` in die fünf Knoten oder prüft, dass sie nicht abgewichen sind |
| `tools/release_firmware.py`  `tools/firmware_sign.mjs` | signiert und veröffentlicht ein Firmware-Release |
| `tools/voice_cases.py` | die mit ARMOR-VOICE-AI geteilten Sprachfälle |
| `tools/make_architecture.py`  `tools/make_structure.py`  `tools/universal_readme_check.py` | die Bilder und die Layout-Prüfung der READMEs |

## ⚙️ Konfiguration

### Build-Optionen der Firmware (Kconfig)

| Einstellung | Standard | Was sie tut |
|---|---|---|
| `CONFIG_ARMOR_NODE_ID` | "" | der Name des Knotens am Broker |
| `CONFIG_ARMOR_SETUP_CODE` | "" | der Code, der die Einrichtung öffnet |
| `CONFIG_ARMOR_FLEET_SECRET` | "" | Flottengeheimnis für die Bluetooth-PIN; in öffentlicher Firmware leer |
| `CONFIG_ARMOR_BLE_SETUP_MINUTES` | 10 (1 to 120) | wie lange die Bluetooth-Einrichtung offen bleibt |
| `CONFIG_ARMOR_ETH_SPI_HOST` | 1 (1 to 2) | SPI-Host des Ethernet-Chips |
| `CONFIG_ARMOR_ETH_MOSI` `MISO` `SCLK` `CS` `INT` `RST` | 11, 12, 13, 14, 10, 9 | Pins der Ethernet-Platine (Profil `s3-eth`) |
| `CONFIG_ARMOR_ETH_SPI_MHZ` | 20 (1 to 40) | SPI-Takt des Ethernet-Chips |
| `CONFIG_ARMOR_MQTT_URI` `USERNAME` `PASSWORD` | "" | erste Broker-Adresse und Zugangsdaten |
| `CONFIG_ARMOR_BOOT_FACTORY_RESET` | y | erlaubt das Zurücksetzen beim Start |
| `CONFIG_ARMOR_NTP_SERVER` | pool.ntp.org | Zeitserver |
| `CONFIG_ARMOR_HEARTBEAT_S` | 10 (2 to 300) | Sekunden zwischen Herzschlägen |
| `CONFIG_ARMOR_BOARD_S3_WIFI`  `CONFIG_ARMOR_BOARD_S3_ETH` | S3_WIFI | das Platinenprofil des Images (`tools/build_node.sh NODE BOARD`) |

Die TLS-Verbindung des Knotens zum Broker ist eine Einstellung des Knotens (nicht des Builds): `mqtt.tls` (standardmäßig aus) und `mqtt.ca_pem` (ein PEM-Zertifikat, höchstens 2 KB, geprüft); die Verbindung vertraut nur dieser Stelle und prüft den Namen des Brokers. Die Python-Bibliothek hat keine eigenen Umgebungsvariablen; der gemeinsame Starter legt beim ersten ARMOR-SERVER-Start eine ignorierte `.env` mit zufälligen Geheimnissen und einem zufälligen Administratorpasswort an und gibt oder versioniert nichts.

## 🚀 Schnellstart

**Voraussetzungen:** Python 3.11+ (kein weiteres Paket). Zur Prüfung der Firmware-Basis müssen die fünf Knoten-Repositorys neben diesem liegen.

```powershell
python -m pip install -e .                   # die Bibliothek installieren
python -m unittest discover -s tests         # 237 Tests, 1225 Vektoren
python tools/generate_types.py --check       # die erzeugten Typen sind aktuell
python tools/generate_rest_types.py --check  # die Typen des HTTP-Vertrags sind aktuell
python tools/make_conformance.py             # Vektoren nach Änderung der Fallliste neu erzeugen (--check: aktuell)
python tools/sync_firmware_base.py check     # die geteilte Firmware ist nicht abgewichen
```

## 🧪 Tests

```powershell
python -m unittest discover -s tests  # 237 Tests
python -I tools/armor_ci_validate.py
```

| Testdatei | Tests | Was sie abdeckt |
|---|---|---|
| `test_contracts.py` | 68 | jede Nachricht, jedes Topic und jeder Zerleger, mit den Konformitätsvektoren |
| `test_task_safety_check.py` | 23 | der Scan, der die unverzichtbaren Tasks eines Knotens findet |
| `test_universal_readme_check.py`, `test_readme_tools.py` | 36 | die Layout-Prüfung und die Bilder der READMEs |
| `test_firmware_base.py` | 13 | die geteilte Firmware-Basis und ihr Abgleich |
| `test_openapi.py` | 13 | die OpenAPI-Datei gegen die Routen des Servers |
| `test_release_firmware.py` | 12 | Signatur und Veröffentlichung der Firmware |
| `test_pretty_run.py`, `test_build_scripts.py` | 11 | das Live-Panel der Skripte |
| `test_generated_types.py`, `test_repository_registry.py`, `test_voice_turn.py` | 21 | die erzeugten Typen, die Repository-Liste und der Sprachturn |
| `test_alarm_codes.py`, `test_collect_errors.py`, `test_project_manifest_doc.py`, `test_firmware_fuzz.py`, `test_fuzz_validator.py` | 17 | Alarmcode-Wörter, Fehlersammlung, Manifest-Leitfaden und Fuzz-Gerüst |

Die Host-Tests der gemeinsamen Firmware liegen in `firmware_base/tests/` (C++, ohne ESP-IDF) und laufen in den Prüfungen der Knoten-Repositorys. `python tools/sync_firmware_base.py check` braucht die fünf Knoten-Repositorys neben diesem. GitHub Actions führt bei jedem Push und Pull Request die A.R.M.O.R.-Basis aus: die Prüfung von Manifest, Version, Änderungsprotokoll und README-Parität, dann den eigenen Build und die eigenen Tests des Projekts.

## 🏗️ Build und Veröffentlichung

Es ist reines Python und eine Reihe von Werkzeugen: Es gibt nichts zu kompilieren. Die Version steht in `pyproject.toml`, in `armor.project.json` und im README-Badge (aus dem Manifest gelesen); jede Version hat ihren Eintrag in [CHANGELOG.md](CHANGELOG.md). Releases werden auf GitHub veröffentlicht. Das Firmware-Release-Werkzeug (`tools/release_firmware.py`) signiert und veröffentlicht die Images der Knoten; der nötige Schlüssel liegt nie in einem Repository.

## 🩺 Fehlerbehebung

| Du siehst | Weil | Tu |
|---|---|---|
| `FIRMWARE_BASE=FAIL ... copies drifted` | ein Knoten hat eine geteilte Datei von Hand geändert | die Änderung in `firmware_base/` machen und `sync` ausführen; oder `import`, um die Dateien der Knoten zu übernehmen |
| `ARMOR-NODE-HMI: main/secret_vault.cpp is missing` | die Knoten-Repositorys liegen nicht neben ARMOR-COMMON | nebeneinander klonen |
| `generated types are out of date` | ein Schema oder die OpenAPI-Datei hat sich geändert | `generate_types.py` und `generate_rest_types.py` ohne `--check` ausführen |
| `TASK_SAFETY=FAIL no task found: the scan is broken` | der Scan der Knoten-Quellen fand nichts | prüfen, dass die Knoten-Repositorys neben diesem liegen |
| `no_signature`, `bad_signature`, `checksum_mismatch`, `wrong_firmware` | der Knoten lehnte ein Release ab: Signatur, Hash oder Platine fehlt oder falsch | mit `tools/release_firmware.py` und dem Schlüssel veröffentlichen, dem die Firmware vertraut |

## 📂 Struktur des Repositorys

<p align="center">
  <img src="images/repository-structure.svg" alt="Repository structure of ARMOR-COMMON" width="100%">
</p>

<details>
<summary>Textversion des Baums</summary>

```text
ARMOR-COMMON/
├── src/armor_common/
│   ├── contracts.py               Topics und Validatoren
│   ├── schema.py                  der Schema-Interpreter
│   ├── envelope.py                der gemeinsame Umschlag
│   ├── voice.py                   der Sprachvertrag
│   ├── schemas/                   34 JSON-Schemas
│   ├── alarm_codes.json           Wörter je Alarmcode
│   └── battery_ops.json           Batterieoperationen
├── firmware_base/                 die Firmware, die die fünf Knoten teilen, nur einmal
├── conformance/                   1225 gültige und ungültige Nachrichten
├── generated/                     TypeScript- und Kotlin-Typen (erzeugt, nicht bearbeiten)
├── openapi/                       armor-server.yaml, HTTP-Vertrag
├── registry/                      repositories.json, Familienliste
├── fuzz/                          libFuzzer-Ziele
├── scripts/                       armor-project-Starter
├── tools/                         Generatoren, Firmware-Abgleich und -Release, Starter, CI-Prüfungen
├── tests/                         237 Tests
├── docs/                          Verträge, Firmware, Fuzzing
├── images/                        Banner, Symbol und die Bilder des READMEs
├── .github/                       CI-Workflow, Dashboard-Hinweis, Vorlagen für Issues und Pull Requests
├── armor.project.json             Manifest: Version, Rolle, Reife
├── pyproject.toml                 Paket-Metadaten, Einstiege
├── CHANGELOG.md                   was sich in jeder Version geändert hat
├── run.sh run.bat                 Start, gemeinsamer Ablauf
├── build.sh build.bat             Bauen und Testen, gemeinsamer Ablauf
├── build-test.sh build-test.bat   Bauen, Testen und Verpacken
├── test.sh test.bat               nur die Tests, nie die Version
└── SECURITY.md SUPPORT.md CONTRIBUTING.md CODE_OF_CONDUCT.md LICENSE
```

</details>

## 🗺️ Roadmap und bekannte Grenzen

**Bekannte Grenzen heute**

* Die Kotlin-Typen werden erzeugt, aber von ARMOR-ANDROID-CONTROL **noch nicht genutzt**; die App behält ihr eigenes Parsing.
* Der Befehl `set_thresholds` hat nur ein Feld `sensitivity`: Die echten Radar-Parameter werden erst definiert, wenn die Firmware existiert.
* Nur der Radar-Knoten hat die gemeinsame Firmware auf einer Platine ausgeführt; die anderen vier nicht.
* Keine unabhängige Sicherheitsprüfung.

**Als Nächstes**

* Die Android-App soll die erzeugten Kotlin-Typen nutzen.
* Die echten Radar-Parameter von `set_thresholds` festlegen.
* Die gemeinsame Firmware auf den Platinen der anderen vier Knoten ausführen.

## 🌍 Sprachen

README und Texte gibt es auf Englisch, Spanisch, Französisch, Italienisch, Deutsch, Chinesisch, Japanisch und europäischem Portugiesisch.

## 🔗 Verwandte Projekte

**A.R.M.O.R.** (Autonomous Radar & Multimodal Observation Range) ist ein Perimeter-Sicherheitssystem aus unabhängigen Repositorys. Jedes hat eine eigene Version, eigene Tests und ein eigenes README; hier ist die Familie:

* **ARMOR-COMMON** (dieses Repository) - Nachrichtenverträge, Validierer, Konformitätsvektoren und generierte Typen
* **[ARMOR-NODE-RADAR](https://github.com/JuanenRac/ARMOR-NODE-RADAR)** - Feldknoten-Firmware für ESP32-S3 mit drei Radaren und eigenem Web-Panel
* **[ARMOR-NODE-SOLAR](https://github.com/JuanenRac/ARMOR-NODE-SOLAR)** - Protokolle für Solar-Wechselrichter und -Batterien und die Nachrichten eines Gateway-Knotens
* **[ARMOR-NODE-ELECTRICAL](https://github.com/JuanenRac/ARMOR-NODE-ELECTRICAL)** - Elektroknoten: Zähler, die Nachricht der Netzmesswerte und die Regeln fürs Schalten
* **[ARMOR-NODE-ALARM](https://github.com/JuanenRac/ARMOR-NODE-ALARM)** - Alarmknoten und Alarmzentrale: Zonen, Scharfschalten, Verzögerungen, Sirene und PIN, mit dem Server oder ohne ihn
* **[ARMOR-NODE-HMI](https://github.com/JuanenRac/ARMOR-NODE-HMI)** - Touch-Panel: der Systemzustand auf einem Wandbildschirm, Scharf- und Quittieren sowie das Zuhause des Sprachassistenten
* **[ARMOR-NETWORK](https://github.com/JuanenRac/ARMOR-NETWORK)** - Das lokale Netzwerk: seine Geräte, das Internet und was sich ändert
* **[ARMOR-SERVER](https://github.com/JuanenRac/ARMOR-SERVER)** - Zentraler Koordinator: Telemetrie, Alarme, Geräte, Solarmesswerte und Kameras
* **[ARMOR-STUDIO](https://github.com/JuanenRac/ARMOR-STUDIO)** - Web-Konsole: Kameras, Radar, Alarme, Solarenergie und 2D/3D-Standortdesigner
* **[ARMOR-ANDROID-CONTROL](https://github.com/JuanenRac/ARMOR-ANDROID-CONTROL)** - Android-Bedienclient mit Live-Radar in 2D/3D
* **[ARMOR-IOS-CONTROL](https://github.com/JuanenRac/ARMOR-IOS-CONTROL)** - iPhone-Bedienclient
* **[ARMOR-SERVER-AI](https://github.com/JuanenRac/ARMOR-SERVER-AI)** - Visuelle Inferenzrichtlinie, die ihre Entscheidungen erklärt und nie handelt
* **[ARMOR-VISION](https://github.com/JuanenRac/ARMOR-VISION)** - Kamerazonen, Masken und Erkennungsregeln für den Jetson Orin NX
* **[ARMOR-VOICE-AI](https://github.com/JuanenRac/ARMOR-VOICE-AI)** - Offline-Sprachabsichten mit einer nicht fälschbaren Bestätigung
* **[ARMOR-HARDWARE](https://github.com/JuanenRac/ARMOR-HARDWARE)** - Gehäuse, Elektronik und die Abnahmematrix am Prüfstand
* **[ARMOR-DEVOPS](https://github.com/JuanenRac/ARMOR-DEVOPS)** - Bereitstellung, CM5-Prüfstand, Backup und TLS
* **[ARMOR-SIMULATOR](https://github.com/JuanenRac/ARMOR-SIMULATOR)** - Offline-Telemetriesimulator mit wiederholbaren Fehlern
* **[ARMOR-UPDATER](https://github.com/JuanenRac/ARMOR-UPDATER)** - Erkennt, installiert und aktualisiert die eigenen Repositorys des Ökosystems
* **[ARMOR-DOCS](https://github.com/JuanenRac/ARMOR-DOCS)** - Architektur, Sicherheitsgrundlage und die Fähigkeitsmatrix

## 📚 Dokumentation

* [Verträge](docs/CONTRACTS.md): jede Nachricht, jedes Topic und wie man einen Vertrag ändert
* [Firmware-Basis](docs/FIRMWARE_BASE.md): was die fünf Knoten teilen und wie es abgeglichen wird
* [Signierte Firmware](docs/SIGNED_FIRMWARE.md): die Signatur der Releases und was sie nicht abdeckt
* [Fuzzing](docs/FUZZING.md): die drei Parser-Ziele und wie man sie ausführt
* [Projekt-Manifest](docs/PROJECT_MANIFEST.md): die `armor.project.json` jedes Repositorys
* [Die Bilder der READMEs](docs/README_PICTURES.md): wie Architektur und Repository-Struktur gezeichnet werden
* [Fähigkeitsmatrix: was belegt ist und was nicht](https://github.com/JuanenRac/ARMOR-DOCS/blob/main/docs/CAPABILITY_MATRIX.md)
* [Projektkatalog: Versionen und wie die Repositorys voneinander abhängen](https://github.com/JuanenRac/ARMOR-DOCS/blob/main/docs/PROJECT_CATALOG.md)
* [Änderungsverlauf dieses Repositorys](CHANGELOG.md)

## 🤝 Mitwirken und Community

* Führe vor einem Pull Request `python -I tools/armor_ci_validate.py` und die Tests aus: Beide müssen bestehen. Siehe [CONTRIBUTING.md](CONTRIBUTING.md) und den [Verhaltenskodex](CODE_OF_CONDUCT.md).
* Das README gibt es in acht Sprachen, und es wird aus den Quellen in ARMOR-DOCS erzeugt: Eine Textänderung erfolgt dort.
* Eine Änderung an einer Nachricht zwischen Komponenten beginnt in ARMOR-COMMON.
* Beschreibe nichts als auf einer Platine funktionierend, was nur gebaut wurde.
* Melde eine Schwachstelle privat: [SECURITY.md](SECURITY.md). Fragen, Ideen und Meldungen: electrohobby3d@gmail.com ([SUPPORT.md](SUPPORT.md)).

## 👤 AUTOR

**JuanenRac (Electro Hobby 3D)** · electrohobby3d@gmail.com

## 📜 LIZENZ

GPL-3.0-or-later - siehe [LICENSE](LICENSE).
