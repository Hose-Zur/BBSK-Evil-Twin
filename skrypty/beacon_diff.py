#!/usr/bin/env python3
"""
Beacon Frame Diff — Szczegółowe porównanie IE między dwoma AP
AGH WIEiT — Projekt: Bezpieczeństwo Sieci Bezprzewodowych

Narzędzie pobiera dwie grupy ramek Beacon (po BSSID) i porównuje wszystkie
Information Elements. Wynik to raport różnic — kluczowy dowód w detekcji
ataku Evil Twin przez fingerprinting AP.

Użycie:
    # Automatycznie — porównaj dwa pierwsze AP z tym samym SSID
    python3 beacon_diff.py plik.pcap AGH_Test

    # Ręcznie — porównaj konkretne BSSIDy
    python3 beacon_diff.py plik.pcap --bssid1 AA:BB:CC:DD:EE:01 --bssid2 AA:BB:CC:DD:EE:02

    # Eksport do JSON/Markdown
    python3 beacon_diff.py plik.pcap AGH_Test --json -o ./wyniki/
    python3 beacon_diff.py plik.pcap AGH_Test --markdown --json

Wymagania:
    pip3 install scapy
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

try:
    from scapy.all import rdpcap, Dot11Beacon, Dot11, Dot11Elt, RadioTap
except ImportError:
    print("[BŁĄD] Brak scapy. Zainstaluj: pip3 install scapy", file=sys.stderr)
    sys.exit(1)

# ─── Stałe IE ─────────────────────────────────────────────────────
IE_NAMES = {
    0: "SSID",
    1: "Supported Rates",
    2: "FH Parameter Set",
    3: "DSSS Parameter Set",
    4: "CF Parameter Set",
    5: "TIM (Traffic Indication Map)",
    6: "IBSS Parameter Set",
    7: "Country",
    8: "Hopping Pattern Parameters",
    9: "Hopping Pattern Table",
    10: "Request",
    11: "BSS Load",
    12: "EDCA Parameter Set",
    13: "TSPEC",
    14: "TCLAS",
    15: "Schedule",
    16: "Challenge Text",
    32: "Power Constraint",
    33: "Power Capability",
    34: "TPC Request",
    35: "TPC Report",
    36: "Supported Channels",
    37: "Channel Switch Announcement",
    38: "Measurement Request",
    39: "Measurement Report",
    40: "Quiet",
    41: "IBSS DFS",
    42: "ERP Information",
    43: "TS Delay",
    44: "TCLAS Processing",
    45: "HT Capabilities",
    46: "QoS Capability",
    47: "ERP Information (old)",
    48: "RSN Information",
    49: "Extended Rates (old)",
    50: "Extended Supported Rates",
    51: "AP Channel Report",
    52: "Neighbor Report",
    54: "Mobility Domain",
    55: "Fast BSS Transition",
    56: "Timeout Interval",
    57: "RIC Data",
    58: "DSE Registered Location",
    59: "Supported Operating Classes",
    60: "Extended Channel Switch Announcement",
    61: "HT Operation",
    62: "Secondary Channel Offset",
    63: "BSS Average Access Delay",
    64: "Antenna",
    65: "RSNI",
    66: "Measurement Pilot Transmission",
    67: "BSS Available Admission Capacity",
    68: "BSS AC Access Delay",
    69: "WAPI Parameter Set",
    70: "QoS Map Set",
    71: "QBSS Load",
    72: "Interworking",
    73: "Advertisement Protocol",
    74: "Expedited Bandwidth Request",
    75: "QMF Policy",
    76: "Roaming Consortium",
    77: "Emergency Alert Identifier",
    107: "Mesh ID",
    113: "Mesh Configuration",
    114: "Mesh Awake Window",
    117: "Mesh STA Info",
    127: "Extended Capabilities",
    130: "VHT Capabilities",
    131: "VHT Operation",
    191: "VHT Tx Power Envelope",
    192: "MCCAOP Advertisement Overview",
    221: "Vendor Specific",
    255: "Extended (Element ID Extension)",
}

# ─── Baza OUI ─────────────────────────────────────────────────────
KNOWN_OUI = {
    "0050F2": "Microsoft (WPS)",
    "00904C": "Epigram/Intel",
    "001018": "Broadcom",
    "000C03": "Apple",
    "0017F2": "Apple",
    "00037F": "Atheros/Qualcomm",
    "00146C": "Netgear",
    "00156D": "Ubiquiti",
    "001A11": "Google",
    "001C0F": "Cisco",
    "001D7E": "Samsung",
    "0022F4": "Huawei",
    "0024D6": "Asus",
    "0026BB": "Apple",
    "003065": "Nokia",
    "081735": "Cisco Meraki",
    "149182": "Nintendo",
    "24A43C": "Ubiquiti Networks",
    "28CFDA": "Apple",
    "38EC0D": "Xiaomi",
    "409C28": "Samsung",
    "5450DE": "Amazon",
    "78D6B2": "Ralink/MediaTek",
    "94B40F": "Aruba Networks",
    "A42940": "D-Link",
    "A4C0C7": "Ralink/MediaTek (RT5572)",
    "B827EB": "Raspberry Pi",
    "D89E61": "TP-Link",
    "E0B9A5": "Google",
}


def _extract_ies(pkts, target_bssid):
    """
    Ekstraktuje wszystkie Information Elements z ramek Beacon danego BSSID.
    
    Returns:
        dict: {
            "bssid": str,
            "ssid": str,
            "frame_count": int,
            "first_seen": float,
            "last_seen": float,
            "ies": {ie_id: [lista wartości IE]},
            "rssi_values": [int],
            "seq_numbers": [(timestamp, seq)],
            "av
        }
    """
    result = {
        "bssid": target_bssid,
        "ssid": "?",
        "frame_count": 0,
        "first_seen": None,
        "last_seen": None,
        "ies": defaultdict(list),
        "rssi_values": [],
        "seq_numbers": [],
    }

    for pkt in pkts:
        if not pkt.haslayer(Dot11Beacon):
            continue
        bssid = (pkt.addr3 or "").lower()
        if bssid != target_bssid.lower():
            continue

        result["frame_count"] += 1
        pkt_time = float(pkt.time)

        if result["first_seen"] is None:
            result["first_seen"] = pkt_time
        result["last_seen"] = pkt_time

        # Parsuj IE
        if pkt.haslayer(Dot11Elt):
            elt = pkt[Dot11Elt]
            while elt:
                ie_id = elt.ID
                info = bytes(elt.info) if elt.info else b""

                if ie_id == 0:  # SSID
                    try:
                        result["ssid"] = info.decode("utf-8", errors="replace")
                    except Exception:
                        pass
                elif ie_id == 221 and len(info) >= 3:  # Vendor Specific
                    oui = info[:3].hex().upper()
                    vendor_name = KNOWN_OUI.get(oui, f"OUI:{oui}")
                    result["ies"][ie_id].append(f"{vendor_name} | raw:{info.hex()}")
                elif ie_id == 3 and len(info) >= 1:  # DSSS Channel
                    result["ies"][ie_id].append(f"Channel {info[0]}")
                elif ie_id == 7 and len(info) >= 3:  # Country
                    try:
                        country = info[:3].decode("ascii")
                        result["ies"][ie_id].append(country)
                    except Exception:
                        result["ies"][ie_id].append(info.hex())
                elif ie_id == 45 and len(info) >= 2:  # HT Capabilities
                    ht_cap = int.from_bytes(info[0:2], "little")
                    caps = []
                    if ht_cap & 1: caps.append("LDPC")
                    if ht_cap & (1 << 1): caps.append("HT40")
                    if ht_cap & (1 << 4): caps.append("Greenfield")
                    if ht_cap & (1 << 5): caps.append("SGI20")
                    if ht_cap & (1 << 6): caps.append("SGI40")
                    if ht_cap & (1 << 7): caps.append("Tx-STBC")
                    if ht_cap & (1 << 8): caps.append("Rx-STBC(1)")
                    if ht_cap & (1 << 9): caps.append("Rx-STBC(2)")
                    if ht_cap & (1 << 10): caps.append("Rx-STBC(3)")
                    if ht_cap & (1 << 11): caps.append("DelayedBA")
                    if ht_cap & (1 << 12): caps.append("MaxAMSDU-7935")
                    if ht_cap & (1 << 14): caps.append("HT40-SGI")
                    if ht_cap & (1 << 15): caps.append("HT40-intolerant")
                    cap_str = ", ".join(caps) if caps else f"raw:{info[:2].hex()}"
                    result["ies"][ie_id].append(cap_str)
                elif ie_id == 42 and len(info) >= 1:  # ERP
                    flags = info[0]
                    erp_parts = []
                    if flags & 0x01: erp_parts.append("NonERP_Present")
                    if flags & 0x02: erp_parts.append("Use_Protection")
                    if flags & 0x04: erp_parts.append("Barker_Preamble")
                    result["ies"][ie_id].append(", ".join(erp_parts) if erp_parts else "None")
                elif ie_id == 48 and len(info) >= 2:  # RSN
                    result["ies"][ie_id].append(f"RSN (ver {info[0]}, len {len(info)}B)")
                elif ie_id == 61 and len(info) >= 5:  # HT Operation
                    result["ies"][ie_id].append(
                        f"PrimaryCh={info[0]}, SecOffset={info[1] & 0x03}, ChWidth={'40MHz' if info[2] else '20MHz'}"
                    )
                elif ie_id == 127:  # Extended Capabilities
                    result["ies"][ie_id].append(f"len={len(info)}B, raw:{info[:16].hex()}")
                else:
                    # Ogólna reprezentacja
                    if len(info) <= 32:
                        result["ies"][ie_id].append(info.hex() if info else "(empty)")
                    else:
                        result["ies"][ie_id].append(info[:32].hex() + f"... ({len(info)}B)")

                try:
                    elt = elt.payload.getlayer(Dot11Elt)
                except Exception:
                    break

        # Sequence Number
        if pkt.haslayer(Dot11):
            seq = pkt[Dot11].SC >> 4
            result["seq_numbers"].append((pkt_time, seq))

        # RSSI
        if pkt.haslayer(RadioTap):
            try:
                rssi = pkt[RadioTap].dBm_AntSignal
                if rssi is not None and rssi != 0:
                    result["rssi_values"].append(int(rssi))
            except AttributeError:
                pass

    return result


def _compare_aps(ap1, ap2):
    """Porównuje dwa AP i zwraca listę różnic."""
    diffs = []
    all_ie_ids = set(ap1["ies"].keys()) | set(ap2["ies"].keys())

    for ie_id in sorted(all_ie_ids):
        ie_name = IE_NAMES.get(ie_id, f"IE {ie_id}")

        vals1 = ap1["ies"].get(ie_id, [])
        vals2 = ap2["ies"].get(ie_id, [])

        # Unikalność wartości
        set1 = set(vals1)
        set2 = set(vals2)

        common = set1 & set2
        only_in_1 = set1 - set2
        only_in_2 = set2 - set1

        if only_in_1 or only_in_2:
            diffs.append({
                "ie_id": ie_id,
                "ie_name": ie_name,
                "status": "DIFFERENT",
                "ap1_values": list(only_in_1) if only_in_1 else ["(brak unikalnych)"],
                "ap2_values": list(only_in_2) if only_in_2 else ["(brak unikalnych)"],
                "common_values": list(common) if common else [],
            })
        elif not vals1 and not vals2:
            continue  # Obie nie mają tego IE
        else:
            diffs.append({
                "ie_id": ie_id,
                "ie_name": ie_name,
                "status": "IDENTICAL",
                "ap1_values": list(set1),
                "ap2_values": list(set2),
                "common_values": list(set1),
            })

    # Metryki ogólne
    metrics = {
        "ssid_match": ap1["ssid"] == ap2["ssid"],
        "rssi_diff": None,
        "frame_count_diff": abs(ap1["frame_count"] - ap2["frame_count"]),
        "seq_range_1": None,
        "seq_range_2": None,
        "seq_overlap": None,
    }

    if ap1["rssi_values"] and ap2["rssi_values"]:
        avg1 = sum(ap1["rssi_values"]) / len(ap1["rssi_values"])
        avg2 = sum(ap2["rssi_values"]) / len(ap2["rssi_values"])
        metrics["rssi_diff"] = round(abs(avg1 - avg2), 1)
        metrics["avg_rssi_1"] = round(avg1, 1)
        metrics["avg_rssi_2"] = round(avg2, 1)

    if ap1["seq_numbers"] and ap2["seq_numbers"]:
        seqs1 = [s for _, s in ap1["seq_numbers"]]
        seqs2 = [s for _, s in ap2["seq_numbers"]]
        metrics["seq_range_1"] = f"{min(seqs1)}–{max(seqs1)}"
        metrics["seq_range_2"] = f"{min(seqs2)}–{max(seqs2)}"
        # Nakładanie zakresów
        overlap_start = max(min(seqs1), min(seqs2))
        overlap_end = min(max(seqs1), max(seqs2))
        metrics["seq_overlap"] = max(0, overlap_end - overlap_start + 1)

    return diffs, metrics


def _format_diff_report(ap1, ap2, diffs, metrics):
    """Formatuje czytelny raport różnic."""
    lines = []
    lines.append("=" * 72)
    lines.append("  BEACON FRAME DIFF — Porównanie fingerprintów AP")
    lines.append("=" * 72)
    lines.append("")

    # Nagłówki AP
    lines.append(f"  AP #1 (BSSID: {ap1['bssid'].upper()})")
    lines.append(f"  ├─ SSID          : {ap1['ssid']}")
    lines.append(f"  ├─ Ramki Beacon  : {ap1['frame_count']}")
    lines.append(f"  └─ Czas          : {ap1['first_seen']:.1f}s – {ap1['last_seen']:.1f}s")
    lines.append("")
    lines.append(f"  AP #2 (BSSID: {ap2['bssid'].upper()})")
    lines.append(f"  ├─ SSID          : {ap2['ssid']}")
    lines.append(f"  ├─ Ramki Beacon  : {ap2['frame_count']}")
    lines.append(f"  └─ Czas          : {ap2['first_seen']:.1f}s – {ap2['last_seen']:.1f}s")
    lines.append("")

    # Metryki
    lines.append("─" * 72)
    lines.append("  METRYKI OGÓLNE")
    lines.append("─" * 72)
    lines.append(f"  SSID zgodne            : {'✅ Tak' if metrics['ssid_match'] else '❌ Nie'}")
    if metrics.get("avg_rssi_1") is not None:
        lines.append(f"  Śr. RSSI AP#1          : {metrics['avg_rssi_1']} dBm")
        lines.append(f"  Śr. RSSI AP#2          : {metrics['avg_rssi_2']} dBm")
        lines.append(f"  Różnica RSSI           : {metrics['rssi_diff']} dBm"
                     f"{' ⚠️ Anomalia!' if metrics['rssi_diff'] > 10 else ''}")
    if metrics["seq_range_1"]:
        lines.append(f"  Zakres seq AP#1        : {metrics['seq_range_1']}")
        lines.append(f"  Zakres seq AP#2        : {metrics['seq_range_2']}")
        if metrics["seq_overlap"] is not None and metrics["seq_overlap"] == 0:
            lines.append(f"  Nakładanie seq         : BRAK ⚠️ — dwa niezależne strumienie!")
        else:
            lines.append(f"  Nakładanie seq         : {metrics['seq_overlap']}")

    # Różnice IE
    lines.append("")
    lines.append("─" * 72)
    lines.append("  PORÓWNANIE INFORMATION ELEMENTS")
    lines.append("─" * 72)

    diff_count = 0
    identical_count = 0
    for d in diffs:
        if d["status"] == "DIFFERENT":
            diff_count += 1
            lines.append(f"\n  [{d['ie_name']}] — ❌ RÓŻNICA")
            if d["ap1_values"]:
                for v in d["ap1_values"]:
                    lines.append(f"    AP #1 → {v}")
            if d["ap2_values"]:
                for v in d["ap2_values"]:
                    lines.append(f"    AP #2 → {v}")
        else:
            identical_count += 1
            vals = d["common_values"]
            val_str = ", ".join(vals[:3])
            if len(vals) > 3:
                val_str += f", ... ({len(vals)} total)"
            lines.append(f"\n  [{d['ie_name']}] — ✅ IDENTYCZNE: {val_str}")

    # Podsumowanie
    lines.append("")
    lines.append("=" * 72)
    lines.append("  WERDYKT")
    lines.append("=" * 72)
    total_ie = diff_count + identical_count
    lines.append(f"  Łącznie IE        : {total_ie}")
    lines.append(f"  Identyczne        : {identical_count}")
    lines.append(f"  Różne             : {diff_count}")

    if diff_count >= 2 and metrics.get("rssi_diff", 0) > 10:
        lines.append("")
        lines.append("  🔴 WERDYKT: EVIL TWIN POTWIERDZONY")
        lines.append("     (≥2 różne IE + anomalia RSSI > 10 dBm)")
    elif diff_count >= 1:
        lines.append("")
        lines.append("  🟡 WERDYKT: PODEJRZENIE EVIL TWIN")
        lines.append(f"     ({diff_count} różnica(e) w IE — wymaga dalszej analizy)")
    else:
        lines.append("")
        lines.append("  🟢 WERDYKT: BRAK DOWODÓW NA EVIL TWIN")
        lines.append("     (IE identyczne — urządzenia mogą być tego samego typu)")

    return "\n".join(lines)


def _format_markdown(ap1, ap2, diffs, metrics):
    """Generuje raport w formacie Markdown."""
    lines = []
    lines.append("# Beacon Frame Diff — Porównanie fingerprintów AP")
    lines.append("")
    lines.append(f"**Data:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("")
    lines.append("## AP #1")
    lines.append(f"- **BSSID:** `{ap1['bssid'].upper()}`")
    lines.append(f"- **SSID:** {ap1['ssid']}")
    lines.append(f"- **Ramki Beacon:** {ap1['frame_count']}")
    lines.append("")
    lines.append("## AP #2")
    lines.append(f"- **BSSID:** `{ap2['bssid'].upper()}`")
    lines.append(f"- **SSID:** {ap2['ssid']}")
    lines.append(f"- **Ramki Beacon:** {ap2['frame_count']}")
    lines.append("")
    lines.append("## Metryki")
    lines.append("")
    lines.append("| Metryka | AP #1 | AP #2 | Różnica |")
    lines.append("|---|---|---|---|")
    if metrics.get("avg_rssi_1") is not None:
        lines.append(f"| Śr. RSSI | {metrics['avg_rssi_1']} dBm | "
                     f"{metrics['avg_rssi_2']} dBm | {metrics['rssi_diff']} dBm |")
    if metrics["seq_range_1"]:
        lines.append(f"| Zakres seq | {metrics['seq_range_1']} | "
                     f"{metrics['seq_range_2']} | — |")
    lines.append(f"| Ramki | {ap1['frame_count']} | {ap2['frame_count']} | "
                 f"{metrics['frame_count_diff']} |")
    lines.append("")
    lines.append("## Porównanie IE")
    lines.append("")

    for d in diffs:
        name = d["ie_name"]
        if d["status"] == "DIFFERENT":
            lines.append(f"### ❌ {name} — RÓŻNICA")
            lines.append("")
            if d["ap1_values"]:
                lines.append(f"- **AP #1:** {', '.join(d['ap1_values'])}")
            if d["ap2_values"]:
                lines.append(f"- **AP #2:** {', '.join(d['ap2_values'])}")
        else:
            lines.append(f"### ✅ {name}")
            lines.append(f"Wspólne: {', '.join(d['common_values'][:3])}")
        lines.append("")

    if metrics.get("rssi_diff", 0) > 10 or any(d["status"] == "DIFFERENT" for d in diffs):
        lines.append("## 🔴 WERDYKT: EVIL TWIN POTWIERDZONY")
    else:
        lines.append("## 🟢 WERDYKT: BRAK DOWODÓW")

    return "\n".join(lines)


def _format_json_export(ap1, ap2, diffs, metrics):
    """Eksport do JSON."""
    return {
        "metadata": {
            "tool": "beacon_diff.py v1.0",
            "project": "BBSK-Evil-Twin",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        },
        "ap1": {
            "bssid": ap1["bssid"].upper(),
            "ssid": ap1["ssid"],
            "frame_count": ap1["frame_count"],
            "avg_rssi": round(sum(ap1["rssi_values"]) / len(ap1["rssi_values"]), 1)
            if ap1["rssi_values"] else None,
        },
        "ap2": {
            "bssid": ap2["bssid"].upper(),
            "ssid": ap2["ssid"],
            "frame_count": ap2["frame_count"],
            "avg_rssi": round(sum(ap2["rssi_values"]) / len(ap2["rssi_values"]), 1)
            if ap2["rssi_values"] else None,
        },
        "metrics": metrics,
        "differences": diffs,
        "verdict": "EVIL_TWIN_CONFIRMED" if metrics.get("rssi_diff", 0) > 10
                   else "SUSPICIOUS" if any(d["status"] == "DIFFERENT" for d in diffs)
                   else "NO_EVIDENCE",
    }


def _find_aps_with_ssid(pkts, target_ssid):
    """Znajduje wszystkie BSSID z podanym SSID."""
    bssids = set()
    for pkt in pkts:
        if not pkt.haslayer(Dot11Beacon) or not pkt.haslayer(Dot11Elt):
            continue
        elt = pkt[Dot11Elt]
        found_ssid = None
        bssid = (pkt.addr3 or "").lower()
        while elt:
            if elt.ID == 0 and elt.info:
                try:
                    found_ssid = elt.info.decode("utf-8", errors="replace")
                except Exception:
                    pass
                break
            try:
                elt = elt.payload.getlayer(Dot11Elt)
            except Exception:
                break
        if found_ssid == target_ssid and bssid:
            bssids.add(bssid)
    return sorted(bssids)


def main():
    parser = argparse.ArgumentParser(
        description="Beacon Frame Diff — Szczegółowe porównanie IE między dwoma AP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady:
  python3 beacon_diff.py /tmp/demo.pcap AGH_Test
  python3 beacon_diff.py /tmp/demo.pcap --bssid1 xx:xx:xx:01 --bssid2 xx:xx:xx:02
  python3 beacon_diff.py /tmp/demo.pcap AGH_Test --json --markdown -o ./wyniki/
        """,
    )
    parser.add_argument("pcap", help="Ścieżka do pliku .pcap")
    parser.add_argument("ssid", nargs="?", default=None,
                        help="SSID do wyszukania (automatyczne wykrycie dwóch BSSID)")
    parser.add_argument("--bssid1", help="BSSID pierwszego AP (ręcznie)")
    parser.add_argument("--bssid2", help="BSSID drugiego AP (ręcznie)")
    parser.add_argument("--json", action="store_true", help="Eksport do JSON")
    parser.add_argument("--markdown", action="store_true", help="Raport w formacie Markdown")
    parser.add_argument("-o", "--output-dir", dest="output_dir", default=None,
                        help="Katalog wyjściowy")
    parser.add_argument("--quiet", action="store_true", help="Tryb cichy")

    args = parser.parse_args()

    if not os.path.exists(args.pcap):
        print(f"[BŁĄD] Plik nie istnieje: {args.pcap}", file=sys.stderr)
        sys.exit(1)

    pkts = rdpcap(args.pcap)
    output_dir = args.output_dir or os.path.dirname(os.path.abspath(args.pcap))

    # ─── Określ BSSIDy ─────────────────────────────────────────
    bssid1 = args.bssid1
    bssid2 = args.bssid2

    if not bssid1 or not bssid2:
        if not args.ssid:
            print("[BŁĄD] Podaj SSID lub oba --bssid1 i --bssid2", file=sys.stderr)
            sys.exit(1)

        found = _find_aps_with_ssid(pkts, args.ssid)
        if len(found) < 2:
            print(f"[BŁĄD] Znaleziono tylko {len(found)} AP z SSID='{args.ssid}' "
                  f"(potrzeba ≥2 do porównania)", file=sys.stderr)
            print(f"       BSSIDy: {[b.upper() for b in found]}")
            sys.exit(1)

        bssid1 = found[0]
        bssid2 = found[1]
        if len(found) > 2:
            print(f"[*] Znaleziono {len(found)} AP z SSID='{args.ssid}'. "
                  f"Porównuję dwa pierwsze.")

    # ─── Analiza ───────────────────────────────────────────────
    ap1 = _extract_ies(pkts, bssid1)
    ap2 = _extract_ies(pkts, bssid2)

    if ap1["frame_count"] == 0:
        print(f"[BŁĄD] Brak ramek Beacon dla BSSID={bssid1}", file=sys.stderr)
        sys.exit(1)
    if ap2["frame_count"] == 0:
        print(f"[BŁĄD] Brak ramek Beacon dla BSSID={bssid2}", file=sys.stderr)
        sys.exit(1)

    diffs, metrics = _compare_aps(ap1, ap2)

    # ─── Raport tekstowy ───────────────────────────────────────
    if not args.quiet:
        print(_format_diff_report(ap1, ap2, diffs, metrics))

    # ─── JSON ──────────────────────────────────────────────────
    if args.json:
        json_data = _format_json_export(ap1, ap2, diffs, metrics)
        json_path = os.path.join(output_dir, "beacon_diff.json")
        os.makedirs(os.path.dirname(json_path) or ".", exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print(f"[*] JSON zapisany: {json_path}")

    # ─── Markdown ──────────────────────────────────────────────
    if args.markdown:
        md_content = _format_markdown(ap1, ap2, diffs, metrics)
        md_path = os.path.join(output_dir, "beacon_diff.md")
        os.makedirs(os.path.dirname(md_path) or ".", exist_ok=True)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"[*] Markdown zapisany: {md_path}")


if __name__ == "__main__":
    main()
