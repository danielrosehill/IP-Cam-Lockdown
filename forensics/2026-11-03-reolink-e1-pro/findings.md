# Reolink E1 Pro: how it reaches the internet (2026-11-03)

Same method as the XM camera ([method](../2026-11-03-xm-gk7205v500/findings.md#method)): `pf` state snapshots, a LAN-bridge capture covering idle, a live view with intercom on mobile data, and a reboot, plus the LAN resolver's query log (this camera uses the LAN resolver, so the router capture sees no DNS).

## Summary: a much smaller footprint than the XM camera

| | Reolink E1 Pro | XM GK7205V500 (generic) |
|---|---|---|
| DNS | LAN resolver only | Hard-coded 1.1.1.1 / 8.8.8.8 |
| Names looked up at boot | `p2p.reolink.com`, `pool.ntp.org` | 3 under `secu100.net` + many hard-coded IPs |
| Clouds | Oracle Cloud (US for registration, Sweden for relay) | Huawei, Alibaba, UCloud, Akamai/Linode |
| Idle | One long-lived UDP flow to the relay (~75 bytes/s) | ~7 flows, ICMP "online" checks to 8.8.8.8 and 114.114.114.114 |
| Live view off-LAN | Tries direct P2P to the phone, then relays via Oracle SE | Tries P2P, then relays via UCloud TCP 6611 |
| Media on the wire | **High-entropy payload (7.79 bits/byte)**: encrypted (some framing visible) | **Cleartext G.711 audio and HEVC P-frames** |

## Flows

| When | Flow | Owner | Reading |
|---|---|---|---|
| Boot | DNS `p2p.reolink.com` → `129.159.158.146` | Oracle Corporation (US) | P2P registration server; UDP 9999 right after boot |
| Boot | NTP `pool.ntp.org` | NTP pool | Clock |
| Always | UDP → `82.70.219.66:58200`, one flow alive 65 h at the time of the snapshot | Oracle Svenska AB (SE) | Keep-alive / relay registration |
| App on LAN | UDP → relay :56499 + TCP → relay :9994 (tiny), then a UDP probe to **the home's own public IP** | | Session setup. Hole-punch to the home's own public IP shows the phone is behind the same NAT, and the stream then goes **directly over the LAN** (not visible to the router) |
| App on mobile data | UDP → phone's carrier public IP and CGNAT address, port 10240, **no reply**; then UDP ↔ `82.70.219.66:54039` | Oracle SE | P2P failed against carrier NAT, so it fell back to relay. ~1.2 MB out / 0.5 MB in over 45 s; the inbound share is the intercom audio |

Relay packets start with the 4-byte magics `2a87cf20` / `2a87cf10` (little-endian on the wire: `20cf872a`, `10cf872a`): Reolink's "BcUdp" transport, as documented in the open-source `neolink` project.

## Notes

- Payload entropy 7.79 bits/byte over 1.6 MB, with 63 four-byte `00 00 00 01` sequences, far more than chance. *Assumed*: encrypted media with some cleartext framing or NAL headers. Not decoded.
- No plaintext HTTP at boot; no firmware check seen in the window.
- Unlike the XM camera, blocking by DNS name (`p2p.reolink.com`) would likely cut new sessions, because it resolves through the LAN resolver. The existing relay flow is by IP, so a firewall block plus a state kill is still the reliable method.
