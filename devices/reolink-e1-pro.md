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

## Local-only operation: what Reolink documents (researched 2026-11-03)

The question: can it run with no Reolink cloud, using RTSP/ONVIF and the app on the LAN? **Reolink says yes, with limits.** Below, *documented* means Reolink's own pages, *reported* means user reports, and *untested* means we have not tried it on this unit yet. The post-block test settles the untested items.

| Question | Answer | Basis |
|---|---|---|
| Does it work without internet? | Yes, "but the camera's functions are limited": local app access, live view, playback and SD recording keep working. Remote access, push, email alerts and auto-upgrade stop | Documented: [Reolink support](https://support.reolink.com/hc/en-us/articles/360007170094-Can-Reolink-WiFi-Cameras-Work-Without-WiFi-or-Internet-Connection/) |
| Does Home Assistant keep working when blocked? | "Reolink cameras can operate fully locally"; the integration keeps working with internet blocked. The E1 Pro is listed as tested. The integration needs HTTP or HTTPS enabled, and both are **closed on this unit**, so it would have to be switched on in Server Settings first; plain RTSP/ONVIF (Frigate, go2rtc) does not need it | Documented: [HA integration docs](https://www.home-assistant.io/integrations/reolink/) |
| Can the app/Client reach it on the LAN by IP? | Yes, both can add a device by IP address | Documented: [app](https://support.reolink.com/hc/en-us/articles/900000535486), [Client](https://support.reolink.com/hc/en-us/articles/900003586646) |
| Can the first setup be done offline? | Reolink advises internet for both phone and camera at first Wi-Fi setup. Whether an account is required is not documented | Documented (internet); account: unknown |
| Can P2P/cloud be switched off? | On powered cameras that have a UID switch, in the **desktop Client** (Device Settings → Network → Advanced), not the phone app. Whether the E1 Pro has the switch is not stated | Documented (general); E1 Pro: untested |
| Are RTSP/ONVIF on by default? | "For some models" they are off by default and switchable in Server Settings. On this unit 554 and 8000 were open | Documented (general); tested on this unit |
| RTSP authentication | Digest (`realm="BC Streaming Media"`); unauthenticated `DESCRIBE` returns 401. RTSP media itself is unencrypted on the LAN, as with any plain RTSP | Tested 2026-11-03 |
| NTP to a local server | Unknown. One Home Assistant report (E1 Outdoor SE PoE, a different model) says Reolink rejects an IP address as the NTP server | Reported, other model |

Not claimed: that it *does* keep streaming once blocked on this unit (to test), and anything about CVEs for the E1 series. None were found in a search on 2026-11-03; the Talos 2021-22 Reolink CVEs are for the RLC-410W and were patched.

## Score

Provisional **C (60/100)**, ceiling A. See [`scoring.md`](../scoring.md).
