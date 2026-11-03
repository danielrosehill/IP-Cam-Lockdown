# Live remote view through the app: what actually leaves the house (2026-11-03)

Setup: phone on mobile data (Wi-Fi off), IPCee app, live view of the camera for ~1-2 minutes with PTZ moves. Observed two ways: `pf` state-table snapshots every ~20 s during the session, and a packet capture on the LAN bridge (`host <cam> and not port 554`, i.e. everything except the local NVR's RTSP pull). The capture covered ~42 s of the live session (1.26 MB camera → relay).

> Capture trap: the OPNsense packet-capture "host" field rejected the expression `<cam> and not <lan>/24` silently. The job ran but wrote an empty pcap (24-byte header). A plain host plus a port exclusion (`port_not=1`, `port=554`) works.

## Session sequence (state table)

| Step | Flow | Owner (whois) | Reading |
|---|---|---|---|
| Idle, always | UDP → `119.8.169.218:8765`, every ~13 s | Huawei Cloud Singapore | Registration keep-alive. **Payload carries the device serial / cloud ID in plain ASCII** (16 hex chars at offset 8 of a 33-byte datagram) |
| Idle, always | TCP → `101.46.63.186:6510` (persistent) + short 6502/6615 sessions | Huawei Cloud | Control channel |
| App opens | TCP → `8.219.179.52:8386` (short) | Alibaba Cloud Singapore | *Assumed*: session broker / relay assignment |
| App opens | UDP → `159.138.53.135:30000`, one 72-byte datagram, **no reply** | Huawei Cloud Hong Kong | P2P hole-punch attempt (payload looks encrypted/random). It got no answer, so the session fell back to relay |
| Streaming | TCP → `<relay>:6611`, several relays in turn: `165.154.147.68` (UCloud MY, ~700 KB), `152.32.218.226` (UCloud SG), `154.81.14.115` / `154.81.14.90` (UCloud HK) | UCloud (HK) Ltd | **The video and audio are relayed through UCloud servers**, not sent peer-to-peer to the phone |

No connection to the phone's own (mobile carrier) IP appeared: the media path was relay-only on this network.

## What is inside the relay stream

The payload on TCP 6611 is Xiongmai's own media framing (the DVRIP/NetSurveillance format), not TLS:

| XM frame header | Meaning | Count in 42 s | Content |
|---|---|---|---|
| `00 00 01 FA` | audio | 1042 | `0E` = G.711 A-law, 320-byte frames. **Raw A-law samples in the clear**: the `0x55`/`0xD5` runs are A-law silence. Room audio is readable by anyone on the path |
| `00 00 01 FD` | P-frame | 484 | Followed directly by an HEVC NAL start code `00 00 00 01 02 01` (TRAIL_R). **Inter-frames in the clear** |
| `00 00 01 FC` | I-frame | 10 | The bytes after the header are *not* a VPS/SPS start code. *Assumed*: keyframes are scrambled or encrypted, the only protected part |
| `00 00 01 F9` | info | 0 | |

So the relay operator, or anyone on the path, gets the audio outright, and the video only needs the keyframes recovered. *Not tested*: decoding.

## DNS

No DNS queries fell inside the capture window: the camera had already resolved its servers. The idle state table shows it uses `1.1.1.1:53` directly. The names stay unknown; they would need a capture across a reboot. To do before the block, or skip.

## Volume

~1.26 MB in ~42 s camera → relay (~240 kbit/s) for a 2880x1616 HEVC stream. The app gets a reduced-bitrate stream, not the main RTSP one. *Assumed*: substream or re-encoded.
