# IP-Cam-Lockdown

Forensics and a repeatable playbook for using cheap AliExpress-style IP cameras **locally only**: keep RTSP/ONVIF for your own NVR (Frigate, Home Assistant), and cut the vendor cloud.

Each camera gets a dossier (what it is, how to identify it) and a forensics record of how it reaches the internet, captured *before* blocking it, because once the firewall rule is in you can no longer see what it was doing.

## Contents

| Path | What |
|---|---|
| [`playbook.md`](playbook.md) | Pin, identify, observe, block, verify. Router examples are OPNsense |
| [`devices/`](devices/) | One file per camera model: identity, firmware, ports, media |
| [`forensics/`](forensics/) | Dated egress investigations: flows, owners, method, open questions; `post-block.md` once blocked |
| [`scoring.md`](scoring.md), [`scores/`](scores/) | Security rating per camera (Local-Only Security Rubric): can it run cut off, and what it exposes while connected |

## Tooling: the Network Forensics plugin

The method here is packaged as agent skills in the [Network Forensics plugin](https://github.com/danielrosehill/Network-Forensics-Plugin) (Claude Code), used for these investigations:

| Skill | Used for |
|---|---|
| `lockdown-iot-device` | Probe (OUI, ports, ONVIF, RTSP), capture idle / live-view / boot windows, attribute flows, document. Includes the OPNsense API calls for the state table, packet capture, state kills, rules and firewall log (`references/opnsense-api.md`) |
| `verify-iot-lockdown` | Apply the block on the router, then record what happened afterwards. RTSP/ONVIF/NVR recording and clock at 10 min, 1 h and 24 h, the vendor app on and off the LAN, what the camera keeps trying, a reboot while blocked |
| `score-device-security` | The scoring rubric and `score.py` behind [`scoring.md`](scoring.md) |

Router examples are OPNsense; the method carries to any stateful firewall.

## Cameras so far

| Model | Platform | Cloud path seen | Score | Status |
|---|---|---|---|---|
| [`IPC_GK7205V500_G5S-WQ`](devices/xm-gk7205v500-g5s-wq.md) (AliExpress, TPTEK Official Store, "8MP 4K IP Camera WiFi") | Xiongmai firmware on Goke GK7205V500, AltoBeam Wi-Fi | UDP 8765 + TCP 6510/6615/6502/443 to Huawei Cloud (SG/SA); `secu100.net` cloud (boot), live view relayed via UCloud TCP 6611 with cleartext audio; hard-coded 1.1.1.1 DNS; ICMP to 8.8.8.8 and 114.114.114.114 ([findings](forensics/2026-11-03-xm-gk7205v500/findings.md)) | **F** (12.5), provisional; capped at D by cleartext media | Capture done; not yet blocked |
| [`E1 Pro`](devices/reolink-e1-pro.md) (Reolink, branded comparison) | Reolink firmware v3.1.0 | `p2p.reolink.com` (Oracle US) registration; relay via Oracle Cloud Sweden UDP; LAN DNS only; media with no cleartext codec data (*inferred* encrypted) ([findings](forensics/2026-11-03-reolink-e1-pro/findings.md)); Reolink documents LAN-only use ([dossier](devices/reolink-e1-pro.md#local-only-operation-what-reolink-documents-researched-2026-11-03)) | **C** (60), provisional, ceiling A | Capture done; not yet blocked |

## What is not published

Serial numbers that double as cloud/P2P IDs, credentials, full MAC addresses, the home's public IP and internal layout. Placeholders like `<cam>` and `<lan>` stand in.

## Licence

CC BY 4.0 for the documentation.
