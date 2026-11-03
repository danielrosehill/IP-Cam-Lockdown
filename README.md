# IP-Cam-Lockdown

Forensics and a repeatable playbook for using cheap AliExpress-style IP cameras **locally only**: keep RTSP/ONVIF for your own NVR (Frigate, Home Assistant), and cut the vendor cloud.

Each camera gets a dossier (what it is, how to identify it) and a forensics record of how it reaches the internet, captured *before* blocking it, because once the firewall rule is in you can no longer see what it was doing.

## Contents

| Path | What |
|---|---|
| [`playbook.md`](playbook.md) | Pin, identify, observe, block, verify. Router examples are OPNsense |
| [`devices/`](devices/) | One file per camera model: identity, firmware, ports, media |
| [`forensics/`](forensics/) | Dated egress investigations: flows, owners, method, open questions |

## Cameras so far

| Model | Platform | Cloud path seen | Status |
|---|---|---|---|
| [`IPC_GK7205V500_G5S-WQ`](devices/xm-gk7205v500-g5s-wq.md) | Xiongmai firmware on Goke GK7205V500, AltoBeam Wi-Fi | UDP 8765 + TCP 6510/6615/6502/443 to Huawei Cloud (SG/SA); hard-coded 1.1.1.1 DNS; ICMP to 8.8.8.8 and 114.114.114.114 ([findings](forensics/2026-11-03-xm-gk7205v500/findings.md)) | Capture in progress; not yet blocked |

## What is not published

Serial numbers that double as cloud/P2P IDs, credentials, full MAC addresses, the home's public IP and internal layout. Placeholders like `<cam>` and `<lan>` stand in.

## Licence

CC BY 4.0 for the documentation.
