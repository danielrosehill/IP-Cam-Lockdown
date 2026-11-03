# How the XM GK7205V500 camera reaches the internet (2026-11-03)

Router: OPNsense 26.7. The camera is on a plain LAN with a DHCP reservation; nothing was port-forwarded to it and UPnP was not used *(assumed: UPnP not enabled on the router; to confirm)*. The phone app could still view it from anywhere. This is how.

## Method

1. `pf` state table for the camera's IP: OPNsense API `POST /api/diagnostics/firewall/query_states` with `searchPhrase=<cam-ip>`. A snapshot of every live flow, with the NAT translation.
2. Packet capture of camera↔internet only, on the LAN bridge: OPNsense API `/api/diagnostics/packet_capture/set` + `start/<id>`, host filter `<cam-ip> and not <lan>/24`, snaplen 1500. Started 2026-11-03; run while opening the app **off Wi-Fi (mobile data)** so the relay/P2P path is exercised. Results: `capture.md` *(pending)*.
3. `whois` on each remote IP.
4. Device-side: ONVIF `GetDNS`, `GetNTP`, `GetNetworkInterfaces`; nmap TCP 1-10000 + chosen UDP ports.

## Outbound flows seen in the state table (snapshot 2026-11-03 ~18:30 IST)

All go out the main WAN with ordinary source NAT. No inbound state or port-forward is involved: the camera dials out and keeps the session open, and the app meets it through the vendor's servers.

| Proto | Destination | Port | State | Owner (whois) | Reading |
|---|---|---|---|---|---|
| UDP | 119.8.169.218 | 8765 | MULTIPLE:MULTIPLE (bidirectional, long-lived) | Huawei Cloud Singapore (`Huawei-SG-Cloud`) | XM cloud P2P/registration keep-alive. Keeps a NAT pinhole open so the app can reach the camera |
| TCP | 101.46.63.186 | 6510 | ESTABLISHED | Huawei Cloud (`Huawei-Cloud-SA`, 101.46.56.0/21) | Persistent control/relay session |
| TCP | 101.46.63.186 | 6615 (x3), 6502 | FIN_WAIT_2 | same | Short sessions to the same host on other ports; *assumed* status/report/relay channels |
| TCP | 101.46.191.2 | 443 | FIN_WAIT_2 | Huawei Cloud (`Huawei-Cloud-SA`, 101.46.184.0/21) | HTTPS; *assumed* cloud API (time, config, firmware or push) |
| UDP | 1.1.1.1 | 53 | SINGLE:MULTIPLE | Cloudflare DNS | **Hard-coded DNS** that bypasses the LAN resolver, so DNS filtering on the LAN does not see or block these lookups |
| ICMP | 8.8.8.8 | echo | | Google DNS | Online check |
| ICMP | 114.114.114.114 | echo | | 114DNS (China) | Online check, China-first default |

## What this means

- **"Not reachable on the LAN but visible in the app" is expected**: the app never talks to the camera's LAN address. Both sides connect out to XM's cloud (here hosted on Huawei Cloud SG/SA), which brokers a P2P (UDP hole-punch) session or relays the stream.
- **DNS blocking alone will not lock it down.** The camera uses `1.1.1.1` and `8.8.8.8` directly, and the servers it talks to are reachable by IP. Blocking must be by source (the camera), at the firewall.
- The ICMP checks to 8.8.8.8 and 114.114.114.114 are how it decides it is "online". If they fail, *assumed*: it retries and stays local-only, which is the desired end state.

## Open questions (fill from the capture)

- DNS names queried (needs the capture; the camera's resolver choice hides them from the LAN DNS logs).
- Whether video ever leaves the house when nobody watches remotely (expected: only keep-alives).
- What goes over 443 (TLS SNI from the capture).
- Behaviour after the block: retry rate, whether local RTSP/ONVIF keep working (expected: yes).
