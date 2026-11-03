# Boot capture: what the camera contacts on power-up (2026-11-03)

Camera power-cycled during a LAN-bridge capture (`host <cam>`, RTSP excluded). Back on the network ~10 s after power returned; full sequence within ~40 s. The app happened to be open, so a relay session also appears.

## DNS (all sent to 1.1.1.1 directly, plain UDP 53)

Only three names, all under **`secu100.net`**, Xiongmai's XMEye/"secu100" cloud domain:

| Name | Answer (2026-11-03) | Used for |
|---|---|---|
| `secu100.net` | 7 A records: `159.138.44.71`, `159.138.0.23`, `159.138.6.141`, `159.138.155.81`, `159.138.3.44`, `119.8.97.250`, `119.13.90.42` (Huawei Cloud) | Cloud entry point; TCP 8186 to the first answer right after boot |
| `pub-cfg.secu100.net` | `8.218.146.108` (Alibaba Cloud) | HTTPS (TLS on 443). *Assumed*: config/capabilities fetch; the ~117 KB 443 session in the idle snapshot |
| `caps.secu100.net` | `101.46.63.202` (Huawei Cloud) | UDP 7999 |

## Contacted by hard-coded IP (no DNS lookup seen)

`101.46.63.186` (TCP 6510 control, 6502/6615), `101.46.63.83:6615`, `119.8.169.218` and `159.138.1.83` (UDP 8765 keep-alive), **`172.105.219.177` / `172.105.219.197` UDP 8765 (Akamai/Linode)**, `159.138.53.135` UDP 30000 (P2P), `8.222.211.59:8386` (Alibaba Cloud, relay broker). Plus ICMP to `114.114.114.114`, `8.8.8.8` and `119.8.169.218`.

**So blocking `secu100.net` in DNS is not enough**: most of the cloud plumbing is reached by IP, and the camera ignores the LAN resolver anyway.

## Boot order (first packet of each new flow)

1. ICMP → 114.114.114.114 (connectivity check)
2. DNS → 1.1.1.1 (`secu100.net` names)
3. TCP → `secu100.net` host :8186
4. TCP → Alibaba :8386 (relay broker)
5. WS-Discovery multicast (ONVIF, LAN)
6. NTP → `time.windows.com` (Microsoft, NTPv3)
7. UDP → `caps.secu100.net`:7999
8. ICMP → 8.8.8.8
9. TLS → `pub-cfg.secu100.net`:443
10. TCP → Huawei :6615, then UDP 8765 keep-alives to Huawei **and Akamai/Linode**, ICMP → 119.8.169.218
11. TCP → Huawei :6510 (persistent control)
12. UDP → Huawei HK :30000 (P2P), then TCP :6611 to UCloud relays (because the app was open)

## Not seen

- **No plaintext HTTP** at boot: no unencrypted firmware-update check in this window. *Assumed*: the update check rides the 443 or the control channel, or runs later.
- No DHCP in the capture (filter was on the camera's IP; DHCP happens before it has one).
