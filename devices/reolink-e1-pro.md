# Reolink E1 Pro (indoor Wi-Fi PTZ)

Branded comparison point for the generic cameras. Examined 2026-11-03 on the same network as the [XM GK7205V500](xm-gk7205v500-g5s-wq.md).

| Field | Value | How obtained |
|---|---|---|
| Vendor | Reolink | ONVIF |
| Model | `E1 Pro` | ONVIF `GetDeviceInformation` (port 8000) |
| Firmware | `v3.1.0.3149_2401092478` | same |
| Wi-Fi chip | Hui Zhou Gaoshengda Technology (OUI `24:3F:75`) | nmap |
| Phone app | Reolink | owner |
| DNS | **From DHCP only** (uses the LAN resolver) | ONVIF `GetDNS` + resolver query log |
| NTP | `pool.ntp.org` | ONVIF `GetNTP` |
| Media | RTSP `h264Preview_01_main`: H.264 2560x1440 + AAC 16 kHz; two-way audio backchannel (PCMU) | ffprobe / go2rtc |

## Listening services

| Port | Service |
|---|---|
| 554/tcp | RTSP |
| 8000/tcp | ONVIF |
| 9000/tcp | Reolink "Baichuan" native protocol (app/client) |
| 2000/udp | Reolink P2P / LAN discovery (open\|filtered) |
| 3702/udp | WS-Discovery |
| 80, 443 | closed (web UI and HTTP API disabled on this unit) |
