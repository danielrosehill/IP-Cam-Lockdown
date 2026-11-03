# Playbook: lock a cheap IP camera to the LAN

For generic AliExpress/Amazon cameras (Xiongmai, CS2/iLnkP2P, Tuya-style and rebrands) that you want to use **only locally**, e.g. through Frigate, Home Assistant or another NVR, with no vendor cloud. Router examples use OPNsense; the ideas carry to any stateful firewall.

**Order matters: document and capture before you block.** Once the rule is in, the interesting traffic stops.

## 1. Pin and identify

1. Give the camera a **DHCP reservation** (by MAC). Every later rule keys on its IP.
2. Get the camera's local credentials working (RTSP/ONVIF). Many apps silently change the device password when you pair or re-pair.
3. Identify the platform:
   - MAC OUI (nmap prints it). This is usually the Wi-Fi chip vendor, not the camera maker.
   - ONVIF `GetDeviceInformation` (port 80, 8899 or 8000). Model strings like `IPC_GK7205V500_...` name the SoC; firmware strings like `V5.10.R02...` are Xiongmai.
   - Port scan: 34567/tcp = Xiongmai DVRIP; 32100/32108 udp = CS2 PPPP P2P; 6668/udp = Tuya; 8899 = XM ONVIF.
   - Fetch the web UI's JS and look for cloud hostnames.
4. Record it in `devices/<platform-model>.md` (template: any file in `devices/`). Redact the serial if it is also the cloud/P2P ID.

## 2. Observe (before blocking)

1. Snapshot the state table for the camera IP (OPNsense: Firewall → Diagnostics → States, or `POST /api/diagnostics/firewall/query_states` with `searchPhrase`).
2. Start a packet capture on the LAN interface, filter `host <cam> and not net <lan>`. Leave it 30-60 minutes. During it: open the app **on mobile data**, view live, move PTZ, then close the app.
3. `whois` every remote IP. Read DNS names and TLS SNI out of the capture (`tcpdump -r cap.pcap -n port 53`, `tshark -r cap.pcap -Y tls.handshake.extensions_server_name -T fields -e tls.handshake.extensions_server_name`).
4. Write `forensics/<date>-<model>/findings.md`: flows, owners, ports, what is assumed.

## 3. Block

On the camera's interface, top of the rule list, in this order:

| # | Action | Source | Destination | Why |
|---|---|---|---|---|
| 1 | Pass | camera | LAN net | replies to the NVR, ONVIF discovery |
| 2 | Pass | camera | firewall: UDP 123 | NTP (point the camera's NTP at the router; otherwise timestamps drift) |
| 3 | Pass (optional) | camera | firewall: 53 | local DNS only. Skip it to make it fully dark |
| 4 | **Block + log** | camera | any | the cloud, hard-coded DNS (1.1.1.1, 8.8.8.8, 114.114.114.114), ICMP checks, firmware calls |

Also:
- **IPv6**: if the LAN has IPv6, block the camera's v6 too (by MAC alias or by disabling v6 on its VLAN), or it walks around a v4-only rule.
- **UPnP/NAT-PMP**: disable, or at least deny the camera. P2P stacks ask for port maps.
- Better long term: put cameras in an **IoT VLAN with no default route to WAN**, and only the NVR allowed in.
- In the app/web UI, switch off "cloud", "P2P" and "remote access" if offered. Treat this as cosmetic: the firewall is the control.

## 4. Verify

1. Clear the camera's states (OPNsense: Diagnostics → States → filter → kill). Old sessions survive a new rule until they are killed.
2. After ten minutes, the state table for the camera should show only LAN flows. The firewall log should show the rule-4 blocks: that log *is* the ongoing record of what it tries.
3. The NVR still streams, and the app no longer connects off-LAN.
4. Record the result and the date in the device's forensics folder.

## 5. Keep it that way

- Firmware updates are usually pulled from the cloud, so they stop. That is the trade-off; check the vendor site for a manual image only if there is a known fix.
- Re-check after any router change (new VLAN, IPv6 enablement, rule reorder).
