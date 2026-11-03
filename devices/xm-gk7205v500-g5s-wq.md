# Xiongmai (XM) GK7205V500 PTZ Wi-Fi camera, `IPC_GK7205V500_G5S-WQ`

Unbranded indoor PTZ camera bought on AliExpress. Examined 2026-11-03 on an OPNsense-routed home LAN. Everything below was read off the device or the router unless marked *assumed*.

## Identity

| Field | Value | How obtained |
|---|---|---|
| Platform / firmware vendor | **Xiongmai (XM, Hangzhou Xiongmai / JF Tech)** | Web UI `pluginVersion.js` points at `ocx.jftechws.com` (JF Tech = Xiongmai's cloud brand); firmware string format; port 34567 |
| SoC | **Goke GK7205V500** | ONVIF model string |
| Wi-Fi chip | AltoBeam (OUI `4C:2F:7B`) | MAC OUI lookup (nmap) |
| ONVIF `Manufacturer` | `H264` (placeholder; XM firmware does not set a real vendor) | ONVIF `GetDeviceInformation` |
| ONVIF `Model` | `IPC_GK7205V500_G5S-WQ` | same |
| Firmware | `V5.10.R02.000889TV.10010.141128.S.ONVIF 21.06` | same |
| Hardware ID | `00001` | same |
| Serial number | 16 hex chars. **Redacted**: on XM devices this doubles as the cloud/P2P device ID used to reach the camera through the vendor cloud | same |
| ONVIF scope | `location/country/china`, `name/NVT`, `Profile/Streaming` | ONVIF `GetScopes` |
| Wired interface | `eth0`, unconfigured, MAC `00:12:34:…` (placeholder MAC, unplugged), reports `192.168.1.10` | ONVIF `GetNetworkInterfaces` |
| Web UI | `<title>Web Viewer`, wants an ActiveX/`VideoPlayToolSetup.exe` plug-in from `ocx.jftechws.com` | HTTP GET `/` |
| Marketing name / AliExpress listing | *to fill in* | owner |
| Phone app | *to fill in* (XM devices use XMEye, iCSee or a rebrand) | owner |

## Media

- RTSP `rtsp://<user>:<pw>@<cam>/stream1`: **HEVC 2880x1616 + G.711 A-law audio**. The path is ignored (every path returns the main stream); no substream.
- Works with Frigate/go2rtc (transcode to H.264 for browser WebRTC).

## Listening services (LAN side)

| Port | Service | Notes |
|---|---|---|
| 80/tcp | HTTP "Web Viewer" | |
| 554/tcp | RTSP | Digest auth |
| 8899/tcp | ONVIF device service (`/onvif/device_service`) | WS-Security digest auth; same account as RTSP |
| 34567/tcp | XM "DVRIP"/NetSurveillance binary control protocol | The protocol behind XMEye/CMS clients; historically weak (see References) |
| 3702/udp | WS-Discovery (ONVIF) | open\|filtered |
| 5353/udp | mDNS | open\|filtered |
| 8765/udp | XM cloud/P2P | also used outbound, see forensics |
| 32100/udp | **PPPP / CS2-style P2P** | the classic peer-to-peer UID protocol family |
| 23/tcp | telnet | closed on this firmware |

## Configuration found on the device

- DNS: from DHCP (the local resolver), **plus `8.8.8.8` in second place**. In practice it also queries **`1.1.1.1` directly**, bypassing the LAN resolver (see forensics).
- NTP: manual, `time.windows.com`.
- The camera's own account: the owner's account had silently changed at some point (the NVR's old `admin` login was first seen getting `401` on 2026-10-18; the working account is the one set in the phone app). *Assumed*: re-pairing or an app-side reset changed it.

## References

- SEC Consult, "Millions of Xiongmai video surveillance devices can be hacked via cloud feature (XMEye P2P Cloud)", 2018.
- CISA ICSA-18-282-06 (CVE-2018-17915 to CVE-2018-17919), XMEye P2P cloud and default credentials. Not tested against this device.
- Paul Marrapese, "Abusing P2P to hack 3 million cameras" (CS2/iLnkP2P PPPP, 2019) for the 32100/udp protocol family.
