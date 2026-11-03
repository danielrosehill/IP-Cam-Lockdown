#!/usr/bin/env python3
"""Generate the blog/README schematics for IP-Cam-Lockdown as SVG (stdlib only).

Every label is taken from the forensics files in ../../forensics and ../../scores.
Render to PNG with:  python3 make_diagrams.py && for f in *.svg; do
  inkscape "$f" --export-type=png --export-dpi=144 ; done
"""
import json
import os
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

SANS = "DejaVu Sans, Barlow, Arial, sans-serif"
MONO = "DejaVu Sans Mono, JetBrains Mono, monospace"

C = {
    "red": "#dc2626",      # cleartext media
    "amber": "#d97706",    # cleartext signalling / identifiers
    "green": "#16a34a",    # encrypted (TLS, or random-looking payload)
    "grey": "#64748b",     # proprietary, payload not analysed
    "ink": "#0f172a",
    "muted": "#475569",
    "line": "#cbd5e1",
    "bg": "#ffffff",
    "panel": "#f8fafc",
    "blue": "#2563eb",
}


def t(x, y, s, size=15, weight="normal", fill=None, anchor="start", font=SANS, style=""):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill or C["ink"]}" text-anchor="{anchor}" xml:space="preserve" {style}>'
            f'{escape(s)}</text>')


def rect(x, y, w, h, fill="#fff", stroke=None, sw=1.5, rx=10, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke or C["line"]}" stroke-width="{sw}"{d}/>')


def line(x1, y1, x2, y2, color, sw=3, dash=None, arrow=True):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#a-{color[1:]})"' if arrow else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{sw}"{d}{m}/>')


def defs():
    out = ["<defs>"]
    for col in set(C.values()):
        out.append(
            f'<marker id="a-{col[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
            f'markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{col}"/></marker>')
    out.append("</defs>")
    return "".join(out)


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{defs()}<rect width="{w}" height="{h}" fill="{C["bg"]}"/>{"".join(body)}</svg>')


def legend(x, y, items, gap=300):
    out = []
    for i, (col, label, dash) in enumerate(items):
        xx = x + i * gap
        out.append(line(xx, y, xx + 46, y, col, sw=4, dash=dash, arrow=False))
        out.append(t(xx + 56, y + 5, label, 14, fill=C["muted"]))
    return out


LEGEND = [
    (C["red"], "cleartext media (audio / video)", None),
    (C["amber"], "cleartext signalling or identifiers", None),
    (C["green"], "encrypted (TLS, or random-looking)", None),
    (C["grey"], "proprietary, payload not analysed", "8 5"),
]


def connection_map(fname, title, subtitle, cam_lines, lan_notes, rows, foot, phone=None):
    """Camera -> router -> one row per destination, colour = what was seen in the payload."""
    W = 1600
    top = 150
    rh = 74
    H = top + rh * len(rows) + 190
    b = [t(40, 52, title, 28, "bold"), t(40, 84, subtitle, 16, fill=C["muted"])]

    # home LAN panel
    lan_h = H - top - 150
    b.append(rect(30, top - 20, 530, lan_h, fill=C["panel"], stroke=C["line"], rx=16))
    b.append(t(52, top + 12, "HOME LAN", 14, "bold", fill=C["muted"], style='letter-spacing="2"'))
    cy = top + lan_h / 2 - 90
    b.append(rect(60, cy, 300, 120, fill="#fff", stroke=C["ink"], sw=2.2, rx=14))
    for i, s in enumerate(cam_lines):
        b.append(t(80, cy + 36 + i * 26, s, 20 if i == 0 else 14, "bold" if i == 0 else "normal",
                   fill=C["ink"] if i == 0 else C["muted"]))
    ny = cy + 160
    for i, s in enumerate(lan_notes):
        col = C["red"] if s.startswith("!") else C["muted"]
        b.append(t(62, ny + i * 22, s.lstrip("!"), 13.5, fill=col, font=MONO if s.startswith((" ", "!")) else SANS))

    # router bar
    rx0 = 590
    b.append(rect(rx0, top - 20, 40, lan_h, fill=C["ink"], stroke=C["ink"], rx=8))
    b.append(f'<text transform="translate({rx0 + 26},{top + lan_h / 2 + 90}) rotate(-90)" font-family="{SANS}" '
             f'font-size="15" font-weight="bold" fill="#fff">OPNsense · source NAT · no port-forward</text>')
    b.append(line(360, cy + 60, rx0 - 4, cy + 60, C["ink"], sw=5, arrow=True))

    # destination rows
    bx, bw = 920, 480
    for i, r in enumerate(rows):
        y = top + i * rh
        mid = y + rh / 2 - 6
        col = C[r["c"]]
        dash = "8 5" if r["c"] == "grey" else None
        b.append(line(rx0 + 40, mid, bx - 4, mid, col, sw=5 if r.get("thick") else 3, dash=dash))
        b.append(t(rx0 + 60, mid - 9, r["port"], 14.5, "bold", fill=col, font=MONO))
        if r.get("note"):
            b.append(t(rx0 + 60, mid + 19, r["note"], 12.5, fill=col))
        b.append(rect(bx, y + 4, bw, rh - 16, fill="#fff", stroke=col, sw=2.4 if r.get("thick") else 1.4, rx=10))
        b.append(t(bx + 16, y + 28, r["who"], 15.5, "bold"))
        b.append(t(bx + 16, y + 49, r["ip"], 12.5, fill=C["muted"], font=MONO))
        # when column
        b.append(t(bx + bw + 20, y + 28, r["when"], 13.5, "bold", fill=C["muted"]))
        b.append(t(bx + bw + 20, y + 48, r.get("what", ""), 12.5, fill=C["muted"]))

    if phone:
        pr = phone["row"]
        py = top + pr * rh + rh / 2 - 6
        b.append(t(bx + bw + 20, py + 26, phone["label"], 13.5, "bold", fill=C[phone["c"]]))

    ly = H - 110
    b.extend(legend(40, ly, LEGEND, gap=385))
    for i, s in enumerate(foot):
        b.append(t(40, ly + 44 + i * 22, s, 13.5, fill=C["muted"]))
    write(fname, svg(W, H, b))


def write(name, content):
    p = os.path.join(HERE, name)
    with open(p, "w") as f:
        f.write(content)
    print(p)


# ---------------------------------------------------------------- figure 1
XM_ROWS = [
    dict(c="amber", port="UDP 53 · DNS", note="ignores the LAN resolver", who="Cloudflare DNS",
         ip="1.1.1.1 (hard-coded)", when="Boot", what="3 names, all *.secu100.net"),
    dict(c="amber", port="ICMP echo", note="'am I online?' checks", who="Google DNS · 114DNS (China)",
         ip="8.8.8.8 · 114.114.114.114", when="Boot + always", what="also ICMP to 119.8.169.218"),
    dict(c="amber", port="UDP 123 · NTPv3", who="Microsoft",
         ip="time.windows.com", when="Boot", what="clock"),
    dict(c="amber", port="UDP 8765", note="device cloud ID in plain ASCII", who="Huawei Cloud, Singapore",
         ip="119.8.169.218 · 159.138.1.83", when="Always, every ~13 s", what="registration keep-alive"),
    dict(c="grey", port="UDP 8765", note="payload not inspected", who="Akamai / Linode",
         ip="172.105.219.177 · 172.105.219.197", when="Always", what="keep-alive"),
    dict(c="grey", port="TCP 8186", who="Huawei Cloud  (secu100.net)",
         ip="159.138.44.71 (1 of 7 A records)", when="Boot", what="first cloud contact"),
    dict(c="grey", port="TCP 6510 · 6502 · 6615", note="6510 stays open", who="Huawei Cloud",
         ip="101.46.63.186 · 101.46.63.83", when="Always", what="control channel"),
    dict(c="grey", port="UDP 7999", who="Huawei Cloud  (caps.secu100.net)",
         ip="101.46.63.202", when="Boot", what="capabilities (assumed)"),
    dict(c="green", port="TCP 443 · TLS", who="Alibaba Cloud  (pub-cfg.secu100.net)",
         ip="8.218.146.108", when="Boot", what="config fetch (assumed)"),
    dict(c="green", port="TCP 443 · TLS", note="~117 KB, one session", who="Huawei Cloud",
         ip="101.46.191.2", when="Idle", what="cloud API (assumed)"),
    dict(c="grey", port="TCP 8386", who="Alibaba Cloud, Singapore",
         ip="8.222.211.59 · 8.219.179.52", when="App opens", what="relay broker (assumed)"),
    dict(c="green", port="UDP 30000", note="72 B, random-looking", who="Huawei Cloud, Hong Kong",
         ip="159.138.53.135", when="App opens", what="P2P hole-punch: failed"),
    dict(c="red", thick=True, port="TCP 6611 · no TLS", note="audio + video in clear",
         who="UCloud relays: Malaysia, Singapore, HK",
         ip="165.154.147.68 · 152.32.218.226 · 154.81.14.x", when="Live view", what="~240 kbit/s, relayed"),
]

connection_map(
    "xm-connection-map.svg",
    "XM GK7205V500 (IPCee): every flow seen leaving the house",
    "OPNsense state table + LAN-bridge captures (idle, boot, live view on mobile data), 2026-11-03. "
    "Colour = what was in the payload.",
    ["XM camera", "Goke GK7205V500 · Xiongmai fw", "AltoBeam Wi-Fi · app: IPCee"],
    ["Open on the LAN:", " 80/tcp    HTTP Web Viewer", " 554/tcp   RTSP (Digest)", " 8899/tcp  ONVIF",
     "!34567/tcp XM DVRIP", "!32100/udp PPPP / CS2-style P2P",
     "", "DNS: LAN resolver + 8.8.8.8 configured,", "but queries 1.1.1.1 directly.",
     "4 cloud operators: Huawei, Alibaba,", "UCloud, Akamai/Linode (plus checks", "to Cloudflare, Google, 114DNS, MS)"],
    XM_ROWS,
    ["Only 3 names are ever looked up; everything else is reached by hard-coded IP, so DNS blocking cannot contain it. "
     "Phone side of the live view was not captured.",
     "Whois owners as of 2026-11-03. 'assumed' = purpose inferred from timing and size, not decoded."],
    phone=dict(row=12, c="red", label=""),
)

# ---------------------------------------------------------------- figure 4 (Reolink, same style)
RL_ROWS = [
    dict(c="amber", port="UDP 53 · LAN resolver", note="filterable", who="Home DNS resolver",
         ip="p2p.reolink.com · pool.ntp.org", when="Boot", what="only 2 names"),
    dict(c="amber", port="UDP 123 · NTP", who="NTP pool", ip="pool.ntp.org", when="Boot", what="clock"),
    dict(c="grey", port="UDP 9999", note="BcUdp, obfuscated", who="Oracle Cloud, US  (p2p.reolink.com)",
         ip="129.159.158.146", when="Boot", what="P2P registration"),
    dict(c="grey", port="UDP 58200", note="~75 B/s, one flow 65 h", who="Oracle Cloud, Sweden",
         ip="82.70.219.66", when="Always", what="relay keep-alive"),
    dict(c="grey", port="UDP 56499 · TCP 9994", note="then LAN-direct", who="Oracle Cloud, Sweden",
         ip="82.70.219.66", when="App on LAN", what="session setup"),
    dict(c="grey", port="UDP 10240", note="to phone, no reply", who="Phone's mobile carrier",
         ip="carrier public IP + CGNAT address", when="App on mobile data", what="direct P2P: failed"),
    dict(c="green", thick=True, port="UDP 54039 · BcUdp", note="encrypted (inferred)",
         who="Oracle Cloud, Sweden (relay)", ip="82.70.219.66", when="Live view + intercom", what="1.2 MB out, 0.5 MB in"),
]
connection_map(
    "reolink-connection-map.svg",
    "Reolink E1 Pro: every flow seen leaving the house",
    "Same router, same method, same day (2026-11-03). One cloud operator, LAN DNS only.",
    ["Reolink E1 Pro", "fw v3.1.0.3149", "Gaoshengda Wi-Fi · app: Reolink"],
    ["Open on the LAN:", " 554/tcp   RTSP (Digest)", " 8000/tcp  ONVIF", " 9000/tcp  Baichuan (login)",
     " 2000/udp  P2P / discovery", " 80, 443   closed", "", "DNS: from DHCP only.", "1 cloud: Oracle (US + SE)"],
    RL_ROWS,
    ["Relay packets start with the BcUdp magics 2a87cf20 / 2a87cf10 (as documented by the open-source neolink project).",
     "1.6 MB of relay payload checked: no H.264 NAL headers, no Baichuan media headers, AAC sync at chance level."],
)

# ---------------------------------------------------------------- figure 2: live-view sequence
def sequence():
    W, H = 1600, 1010
    lanes = [("XM camera", "home LAN", 150), ("Huawei Cloud", "SG / SA", 420), ("Alibaba Cloud", "Singapore", 680),
             ("Huawei Cloud", "Hong Kong", 930), ("UCloud relay", "MY / SG / HK", 1180), ("IPCee app", "phone, mobile data", 1440)]
    b = [t(40, 52, "XM live view from outside the house: how the stream reaches the phone", 28, "bold"),
         t(40, 84, "Order of new flows in the state table and capture, 2026-11-03. Nothing is port-forwarded; "
                   "the camera dials out to everything.", 16, fill=C["muted"])]
    for name, sub, x in lanes:
        b.append(rect(x - 105, 112, 210, 62, fill=C["panel"], stroke=C["ink"] if x == 150 else C["line"], sw=1.8))
        b.append(t(x, 138, name, 16, "bold", anchor="middle"))
        b.append(t(x, 160, sub, 13, fill=C["muted"], anchor="middle"))
        b.append(line(x, 176, x, 760, C["line"], sw=2, dash="4 6", arrow=False))
    X = {i: lanes[i][2] for i in range(len(lanes))}
    steps = [
        (0, 1, "amber", "1  UDP 8765 keep-alive every ~13 s, device cloud ID in ASCII", None, False),
        (0, 1, "grey", "2  TCP 6510 control channel, held open", None, False),
        (5, 1, "grey", "3  app asks the XM cloud for the camera (phone side not captured)", "assumed", True),
        (0, 2, "grey", "4  TCP 8386 short session: relay assignment", "assumed", False),
        (0, 3, "green", "5  UDP 30000, one 72-byte datagram: P2P hole-punch", "no reply  ✗", False),
        (0, 4, "red", "6  TCP 6611, no TLS: ~1.26 MB in 42 s (~240 kbit/s)", None, False),
        (4, 5, "red", "7  relayed to the phone (leg not captured)", "assumed", True),
    ]
    y = 225
    for a, z, col, label, tag, dashed in steps:
        x1, x2 = X[a], X[z]
        d = "8 5" if dashed or col == "grey" else None
        sw = 5 if col == "red" and not dashed else 3
        b.append(line(x1 + (6 if x2 > x1 else -6), y, x2 - (8 if x2 > x1 else -8), y, C[col], sw=sw, dash=d))
        lx = min(x1, x2) + 14
        b.append(t(lx, y - 12, label, 14.5, "bold", fill=C[col] if col != "grey" else C["muted"]))
        if tag:
            b.append(t(max(x1, x2) - 10, y + 24, tag, 13, fill=C["muted"], anchor="end", style='font-style="italic"'))
        y += 82
    # payload callout under step 6
    b.append(rect(560, y - 40, 620, 124, fill="#fef2f2", stroke=C["red"], sw=1.6))
    for i, s in enumerate(["Inside the 6611 stream (XM's own framing, not TLS):",
                           "audio   00 00 01 FA  G.711 A-law  1042 frames  CLEAR",
                           "P-frame 00 00 01 FD  HEVC TRAIL_R   484 frames  CLEAR",
                           "I-frame 00 00 01 FC  no VPS/SPS      10 frames  scrambled"]):
        b.append(t(580, y - 12 + i * 25, s, 14 if i else 14.5, "bold" if i == 0 else "normal",
                   fill=C["red"] if "CLEAR" in s else C["ink"], font=MONO if i else SANS))
    b.extend(legend(40, H - 30, LEGEND, gap=385))
    write("xm-live-view-sequence.svg", svg(W, H, b))


sequence()


# ---------------------------------------------------------------- figure 3: relay frame anatomy
def anatomy():
    W, H = 1600, 640
    b = [t(40, 52, "What the relay operator sees: XM media frames on TCP 6611", 28, "bold"),
         t(40, 84, "42 s of live view, 1.26 MB camera → UCloud. Byte values shown are the ones read off the capture; "
                   "grey blocks are header fields not decoded.", 16, fill=C["muted"])]
    rows = [
        ("Audio", "00 00 01 FA", "0E", "G.711 A-law, 320-byte frames", "D5 55 D5 55 D5 55 … (A-law silence)",
         "1042", "CLEAR: room audio playable as-is", "red"),
        ("P-frame", "00 00 01 FD", None, "HEVC NAL start code + type", "00 00 00 01 02 01 … (TRAIL_R slice)",
         "484", "CLEAR: inter-frames decodable", "red"),
        ("I-frame", "00 00 01 FC", None, "no VPS/SPS start code follows", "?? ?? ?? ?? … (no structure)",
         "10", "SCRAMBLED: the only protected part", "green"),
    ]
    y = 140
    for name, magic, sub, desc, payload, count, verdict, col in rows:
        b.append(t(40, y + 46, name, 20, "bold"))
        x = 170
        b.append(rect(x, y + 14, 190, 52, fill="#e0e7ff", stroke=C["blue"], rx=6))
        b.append(t(x + 95, y + 47, magic, 17, "bold", anchor="middle", font=MONO, fill=C["blue"]))
        x += 200
        if sub:
            b.append(rect(x, y + 14, 70, 52, fill="#e0e7ff", stroke=C["blue"], rx=6))
            b.append(t(x + 35, y + 47, sub, 17, "bold", anchor="middle", font=MONO, fill=C["blue"]))
            x += 80
        b.append(rect(x, y + 14, 150, 52, fill="#f1f5f9", stroke=C["line"], rx=6, dash="5 4"))
        b.append(t(x + 75, y + 46, "header (rest)", 14, anchor="middle", fill=C["muted"]))
        x += 160
        fill = "#fef2f2" if col == "red" else "#f0fdf4"
        b.append(rect(x, y + 14, 560, 52, fill=fill, stroke=C[col], sw=2, rx=6))
        b.append(t(x + 16, y + 47, payload, 15.5, font=MONO, fill=C[col] if col == "red" else C["ink"]))
        b.append(t(x, y + 90, desc, 13.5, fill=C["muted"]))
        b.append(t(1420, y + 38, count, 30, "bold", anchor="end"))
        b.append(t(1430, y + 38, "frames", 14, fill=C["muted"]))
        b.append(t(1170, y + 90, verdict, 14, "bold", fill=C[col]))
        y += 140
    b.append(t(40, y + 30, "Transport: plain TCP to the relay, no TLS handshake. Anyone on the path (the relay operator, transit networks) "
                           "gets the audio outright;", 15, fill=C["ink"]))
    b.append(t(40, y + 54, "the video needs only the 10 keyframes recovered. Decoding was not attempted.", 15, fill=C["ink"]))
    write("xm-relay-frames.svg", svg(W, H, b))


anatomy()


# ---------------------------------------------------------------- figure 5: scorecard
def scorecard():
    names = {
        "L1": "Local streams survive an internet block", "L2": "Vendor app works on the LAN while blocked",
        "L3": "Setup without internet or account", "L4": "Cloud/P2P off switch, and egress stops",
        "L5": "Honours LAN DNS and local NTP", "L6": "RTSP + ONVIF without the cloud",
        "L7": "Degrades cleanly when blocked", "E1": "Media leaving the LAN is encrypted",
        "E2": "No identifiers in cleartext egress", "E3": "Cloud reached by name via LAN resolver",
        "E4": "Small cloud footprint (one operator)", "E5": "No media egress when nobody watches",
        "E6": "No legacy or weak local services", "E7": "No known unpatched vulnerabilities",
        "E8": "Offline firmware update path",
    }
    weights = {"L1": 15, "L2": 5, "L3": 5, "L4": 5, "L5": 5, "L6": 5, "L7": 10, "E1": 15,
               "E2": 5, "E3": 5, "E4": 5, "E5": 5, "E6": 5, "E7": 5, "E8": 5}
    xm = json.load(open(os.path.join(ROOT, "scores/xm-gk7205v500-g5s-wq.json")))["criteria"]
    rl = json.load(open(os.path.join(ROOT, "scores/reolink-e1-pro.json")))["criteria"]
    pill = {"pass": (C["green"], "#f0fdf4"), "fail": (C["red"], "#fef2f2"),
            "partial": (C["amber"], "#fffbeb"), "unknown": (C["grey"], "#f8fafc")}
    W, rh = 1300, 44
    H = 200 + rh * 15 + 140
    b = [t(40, 52, "Local-Only Security Rubric v1: both cameras, before the block", 28, "bold"),
         t(40, 84, "Provisional scores, 2026-11-03. Untested criteria score 0 until the post-block test.", 16, fill=C["muted"])]
    cx = {"xm": 860, "rl": 1110}
    b.append(t(cx["xm"], 150, "XM GK7205V500", 17, "bold", anchor="middle"))
    b.append(t(cx["rl"], 150, "Reolink E1 Pro", 17, "bold", anchor="middle"))
    y = 175
    for i, k in enumerate(names):
        if k == "E1":
            b.append(line(40, y - 4, W - 40, y - 4, C["ink"], sw=1.5, arrow=False))
        if i % 2 == 0:
            b.append(rect(40, y, W - 80, rh, fill=C["panel"], stroke=C["panel"], rx=4))
        b.append(t(56, y + 28, k, 15, "bold", font=MONO))
        b.append(t(110, y + 28, names[k], 15))
        b.append(t(640, y + 28, f"{weights[k]} pts", 13, fill=C["muted"]))
        for who, crit in (("xm", xm), ("rl", rl)):
            st = crit[k]["status"]
            ev = crit[k]["evidence"]
            stroke, fill = pill[st]
            b.append(rect(cx[who] - 90, y + 8, 180, 28, fill=fill, stroke=stroke, sw=1.5, rx=14))
            lab = st if st != "unknown" else "untested"
            if ev not in ("none", "tested"):
                lab += f" ({ev[:3]}.)"
            b.append(t(cx[who], y + 27, lab, 13.5, "bold", fill=stroke, anchor="middle"))
        y += rh
    b.append(line(40, y + 6, W - 40, y + 6, C["ink"], sw=1.5, arrow=False))
    b.append(t(110, y + 44, "Score / grade (ceiling if everything untested passes)", 16, "bold"))
    b.append(t(cx["xm"], y + 44, "12.5 · F  (ceiling D)", 17, "bold", fill=C["red"], anchor="middle"))
    b.append(t(cx["rl"], y + 44, "60 · C  (ceiling A)", 17, "bold", fill=C["green"], anchor="middle"))
    b.append(t(110, y + 74, "XM is capped at D whatever the block test shows: cleartext media off the LAN is a red flag.",
               14, fill=C["muted"]))
    b.append(t(110, y + 96, "doc. = vendor documentation, inf. = inferred from the capture; no suffix = tested on our unit.",
               14, fill=C["muted"]))
    write("scorecard.svg", svg(W, H, b))


scorecard()
