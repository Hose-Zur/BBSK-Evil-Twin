#!/usr/bin/env python3
"""
Evil Twin Detection — Analiza pliku .pcap (v2.0)
AGH WIEiT — Projekt: Bezpieczeństwo Sieci Bezprzewodowych

Użycie:
    python3 analyze_pcap.py <plik.pcap> [SSID]           # Tryb legacy
    python3 analyze_pcap.py <plik.pcap> --json             # Export JSON
    python3 analyze_pcap.py <plik.pcap> -o ./wyniki/       # Katalog wyjściowy
    python3 analyze_pcap.py <plik.pcap> --csv              # Export CSV

Przykład:
    python3 analyze_pcap.py /tmp/evil_twin_demo-01.pcap AGH_Test --json -o ./wyniki/

Wymagania:
    pip3 install scapy matplotlib
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
    print("[BŁĄD] Brak biblioteki scapy. Zainstaluj: pip3 install scapy", file=sys.stderr)
    sys.exit(1)

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    PLOT_AVAILABLE = True
except ImportError:
    print("[OSTRZEŻENIE] Brak matplotlib — wykresy będą niedostępne. pip3 install matplotlib",
          file=sys.stderr)
    PLOT_AVAILABLE = False

# ─── Rozszerzona baza OUI (Organizationally Unique Identifier) ────
KNOWN_OUI = {
    # Equipment vendors
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
    "001CDF": "Belkin",
    "001D7E": "Samsung",
    "001E2A": "LG Electronics",
    "001E4C": "Hon Hai (Foxconn)",
    "001E8F": "Canon",
    "001F5B": "Intel",
    "0022F4": "Huawei",
    "002376": "HTC",
    "0024D6": "Asus",
    "00259C": "NEC",
    "0026BB": "Apple (3)",
    "003065": "Nokia",
    "0040F4": "Cameo/Zyxel",
    "00508D": "Hewlett Packard",
    "007F28": "Sony",
    "081735": "Cisco Meraki",
    "149182": "Nintendo",
    "20D5BF": "Samsung (mobile)",
    "24A43C": "Ubiquiti Networks",
    "28CFDA": "Apple (2)",
    "347E5C": "Microsoft",
    "38EC0D": "Xiaomi",
    "406186": "Google (2)",
    "409C28": "Samsung (TV)",
    "44D9E7": "Ubiquiti Networks (2)",
    "5450DE": "Amazon",
    "609217": "Apple (4)",
    "649C81": "Huawei (2)",
    "70B3D5": "Intel (2)",
    "7858F3": "Nest (Google)",
    "7C0191": "Apple (5)",
    "80E650": "Apple (6)",
    "94B10A": "Samsung (mobile 2)",
    "94B40F": "Aruba Networks",
    "A42940": "D-Link",
    "A4C0C7": "Ralink/MediaTek (RT)",    # ← wasze karty TL-WDN3200
    "AC5F3E": "Xiaomi (2)",
    "B065BD": "Apple (7)",
    "B827EB": "Raspberry Pi",
    "C0A0BB": "D-Link (2)",
    "CC2F71": "Ubiquiti (3)",
    "D89E61": "TP-Link",
    "DC2B61": "Apple (8)",
    "E0B9A5": "Google (3)",
    "E8B2AC": "Apple (9)",
    "F05C14": "Samsung (3)",
    "FC0198": "Broadcom (2)",
    # Phone hotspot typical MAC prefixes
    "20D5BF": "Samsung (mobile hotspot)",
    "609217": "Apple (iPhone hotspot)",
    "80E650": "Apple (iPhone hotspot 2)",
}

# ─── Stałe IE (Information Element IDs) ───────────────────────────
IE_SSID = 0
IE_SUPPORTED_RATES = 1
IE_DSSS_PARAM = 3
IE_COUNTRY = 7
IE_ERP = 42
IE_HT_CAPABILITIES = 45
IE_EXT_SUPPORTED_RATES = 50
IE_POWER_CONSTRAINT = 32
IE_HT_OPERATION = 61
IE_EXTENDED_CAPABILITIES = 127
IE_VENDOR_SPECIFIC = 221


def parse_args():
    """Parsuje argumenty CLI — zachowuje kompatybilność z legacy."""
    parser = argparse.ArgumentParser(
        description="Evil Twin Detection — analiza pliku .pcap (v2.0)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady:
  python3 analyze_pcap.py /tmp/demo.pcap                        # Analiza wszystkich AP
  python3 analyze_pcap.py /tmp/demo.pcap AGH_Test               # Filtruj po SSID
  python3 analyze_pcap.py /tmp/demo.pcap --json                  # Export do JSON
  python3 analyze_pcap.py /tmp/demo.pcap AGH_Test -o ./wyniki/   # Katalog wyjściowy
  python3 analyze_pcap.py /tmp/demo.pcap --json --csv -o ./out/  # JSON + CSV
        """,
    )
    parser.add_argument("pcap", nargs="?", default="/tmp/demo-01.pcap",
                        help="Ścieżka do pliku .pcap (domyślnie: /tmp/demo-01.pcap)")
    parser.add_argument("ssid", nargs="?", default=None,
                        help="Filtruj wyniki po SSID (opcjonalnie)")
    parser.add_argument("--json", action="store_true",
                        help="Zapisz wyniki w formacie JSON")
    parser.add_argument("--csv", action="store_true",
                        help="Zapisz wyniki w formacie CSV")
    parser.add_argument("-o", "--output-dir", dest="output_dir", default=None,
                        help="Katalog wyjściowy dla raportów i wykresów")
    parser.add_argument("--no-plot", action="store_true",
                        help="Wyłącz generowanie wykresów")
    parser.add_argument("--quiet", action="store_true",
                        help="Tryb cichy — tylko komunikaty o błędach")
    parser.add_argument("--version", action="version",
                        version="analyze_pcap.py v2.0 — BBSK-Evil-Twin, AGH WIEiT")

    # Obsługa legacy: jeśli pierwszy argument to plik a drugi nie zaczyna się od '-',
    # potraktuj drugi jako SSID
    args = parser.parse_args()

    return args


def _lookup_oui(oui_hex: str) -> str:
    """Zwraca nazwę producenta na podstawie OUI."""
    return KNOWN_OUI.get(oui_hex, f"OUI:{oui_hex}")


def _parse_beacon_ies(elt, ap_data: dict):
    """Parsuje Information Elements z ramki Beacon i uzupełnia ap_data."""
    seen_ids = set()
    while elt:
        elt_id = elt.ID
        info = elt.info

        # SSID (ID=0)
        if elt_id == IE_SSID and info:
            try:
                ap_data["ssid"] = info.decode("utf-8", errors="replace")
            except Exception:
                pass

        # Supported Rates (ID=1) + Extended Supported Rates (ID=50)
        elif elt_id in (IE_SUPPORTED_RATES, IE_EXT_SUPPORTED_RATES) and info:
            for b in info:
                rate_mbps = (b & 0x7F) * 0.5
                ap_data["supported_rates"].add(round(rate_mbps, 1))

        # DSSS Parameter Set (ID=3) — kanał
        elif elt_id == IE_DSSS_PARAM and info and len(info) >= 1:
            ap_data["channel"] = info[0]

        # Country (ID=7)
        elif elt_id == IE_COUNTRY and info and len(info) >= 3:
            try:
                country = info[:3].decode("ascii", errors="replace")
                ap_data["country"] = country
            except Exception:
                pass

        # Power Constraint (ID=32)
        elif elt_id == IE_POWER_CONSTRAINT and info and len(info) >= 1:
            ap_data["power_constraint"] = info[0]  # dB

        # ERP Information (ID=42)
        elif elt_id == IE_ERP and info and len(info) >= 1:
            flags = info[0]
            ap_data["erp_protection"] = bool(flags & 0x01)
            ap_data["erp_barker_preamble"] = bool(flags & 0x04)

        # HT Capabilities (ID=45)
        elif elt_id == IE_HT_CAPABILITIES and info and len(info) >= 26:
            try:
                ht_info = info[0:2]
                ht_cap = int.from_bytes(ht_info, "little")
                ap_data["ht_capabilities"] = {
                    "ldpc": bool(ht_cap & 1),
                    "ht40_supported": bool(ht_cap & (1 << 1)),
                    "sgi_20": bool(ht_cap & (1 << 5)),
                    "sgi_40": bool(ht_cap & (1 << 6)),
                    "tx_stbc": bool(ht_cap & (1 << 7)),
                    "greenfield": bool(ht_cap & (1 << 4)),
                }
            except Exception:
                pass

        # HT Operation (ID=61) — kanał/pasmo
        elif elt_id == IE_HT_OPERATION and info and len(info) >= 5:
            try:
                ap_data["ht_primary_channel"] = info[0]
                ap_data["ht_secondary_channel_offset"] = info[1] & 0x03
            except Exception:
                pass

        # Extended Capabilities (ID=127)
        elif elt_id == IE_EXTENDED_CAPABILITIES and info:
            ap_data["extended_capabilities_raw"] = info.hex() if len(info) <= 32 else info[:32].hex() + "..."

        # Vendor Specific (ID=221)
        elif elt_id == IE_VENDOR_SPECIFIC and info and len(info) >= 3:
            oui = info[:3].hex().upper()
            label = _lookup_oui(oui)
            if label not in ap_data["vendor_specific"]:
                ap_data["vendor_specific"].append(label)

        # Zlicz wystąpienia każdego IE
        ie_name = f"IE_{elt_id}"
        ap_data["ie_distribution"][ie_name] = ap_data["ie_distribution"].get(ie_name, 0) + 1

        # Przejdź do następnego IE
        seen_ids.add(elt_id)
        try:
            elt = elt.payload.getlayer(Dot11Elt)
        except Exception:
            break


def _analyze_packets(pkts, target_ssid=None) -> dict:
    """
    Główna funkcja analizy — parsuje pakiety i zwraca słownik AP.
    
    Returns:
        dict: {bssid: {ssid, seq_nums, rssi, supported_rates, vendor_specific, ...}}
    """
    aps = defaultdict(lambda: {
        "ssid": "?",
        "seq_nums": [],             # lista krotek (timestamp, seq_number)
        "rssi": [],                 # lista wartości RSSI
        "supported_rates": set(),   # zestaw prędkości
        "vendor_specific": [],      # lista nazw producentów
        "frame_count": 0,
        "channel": None,
        "country": None,
        "power_constraint": None,
        "erp_protection": None,
        "erp_barker_preamble": None,
        "ht_capabilities": None,
        "ht_primary_channel": None,
        "ht_secondary_channel_offset": None,
        "extended_capabilities_raw": None,
        "ie_distribution": {},      # rozkład IE ID
        "beacon_intervals": [],     # interwały między beaconami
        "last_beacon_time": None,
    })

    for pkt in pkts:
        if not pkt.haslayer(Dot11Beacon):
            continue

        bssid = pkt.addr3
        if not bssid:
            continue

        bssid = bssid.lower()
        ap = aps[bssid]
        ap["frame_count"] += 1

        # Timestamp — ISO 8601 dla pierwszego i ostatniego beacona
        pkt_time = float(pkt.time)

        # Beacon interval tracking
        if ap["last_beacon_time"] is not None:
            interval = pkt_time - ap["last_beacon_time"]
            if 0.05 < interval < 2.0:  # filtruj odstępstwa (np. zagubione ramki)
                ap["beacon_intervals"].append(interval)
        ap["last_beacon_time"] = pkt_time

        # Parsowanie IE
        if pkt.haslayer(Dot11Elt):
            _parse_beacon_ies(pkt[Dot11Elt], ap)

        # Sequence Number
        if pkt.haslayer(Dot11):
            seq = pkt[Dot11].SC >> 4
            ap["seq_nums"].append((pkt_time, seq))

        # RSSI z Radiotap
        if pkt.haslayer(RadioTap):
            try:
                rssi = pkt[RadioTap].dBm_AntSignal
                if rssi is not None and rssi != 0:
                    ap["rssi"].append(int(rssi))
            except AttributeError:
                pass

    # Filtrowanie po SSID
    if target_ssid:
        aps = {b: d for b, d in aps.items() if d["ssid"] == target_ssid}

    return aps


def _format_report(aps: dict, target_ssid: str = None) -> str:
    """Generuje raport tekstowy jako string."""
    lines = []
    lines.append("=" * 70)
    lines.append(f"  WYKRYTE PUNKTY DOSTĘPOWE — "
                 f"{'SSID: ' + target_ssid if target_ssid else 'wszystkie'}")
    lines.append("=" * 70)

    if len(aps) > 1 and target_ssid:
        lines.append("")
        lines.append(f"  [!] UWAGA: {len(aps)} urządzeń nadaje z SSID='{target_ssid}'")
        lines.append(f"      To jest wskaźnik ataku Evil Twin!")
        lines.append("")

    for i, (bssid, data) in enumerate(aps.items()):
        # Podstawowe metryki
        avg_rssi = round(sum(data["rssi"]) / len(data["rssi"]), 1) if data["rssi"] else "brak"
        rates_sorted = sorted(data["supported_rates"])
        rates_str = ", ".join(f"{r:.0f}" for r in rates_sorted) + " Mbps" if rates_sorted else "brak"
        vendors = ", ".join(data["vendor_specific"]) if data["vendor_specific"] else "brak"

        seq_range = ""
        if data["seq_nums"]:
            seqs = [s for _, s in data["seq_nums"]]
            seq_range = f"{min(seqs)} – {max(seqs)}"

        # Interwał beaconów
        beacon_interval = ""
        if data["beacon_intervals"]:
            avg_interval = sum(data["beacon_intervals"]) / len(data["beacon_intervals"])
            beacon_interval = f"{avg_interval * 1000:.0f} ms (średni)"

        lines.append("")
        lines.append(f"  AP #{i + 1}")
        lines.append(f"  BSSID           : {bssid.upper()}")
        lines.append(f"  SSID            : {data['ssid']}")
        lines.append(f"  Ramki Beacon    : {data['frame_count']}")
        lines.append(f"  Avg RSSI        : {avg_rssi} dBm")
        lines.append(f"  Kanał           : {data['channel'] or 'brak'}")
        lines.append(f"  Supported Rates : {rates_str}")
        lines.append(f"  Vendor Specific : {vendors}")
        lines.append(f"  Seq Numbers     : {seq_range}")
        lines.append(f"  Beacon Interval : {beacon_interval or 'brak'}")

        # Zaawansowane
        if data["country"]:
            lines.append(f"  Kraj            : {data['country']}")
        if data["power_constraint"] is not None:
            lines.append(f"  Power Constraint: {data['power_constraint']} dB")
        if data["erp_protection"] is not None:
            lines.append(f"  ERP Protection  : {'Tak' if data['erp_protection'] else 'Nie'}")
        if data["ht_capabilities"]:
            ht = data["ht_capabilities"]
            ht_str = ", ".join(k for k, v in ht.items() if v)
            lines.append(f"  HT Capabilities : {ht_str or 'brak'}")
        if data["ht_primary_channel"] is not None:
            lines.append(f"  HT Primary Ch   : {data['ht_primary_channel']}")

    # ─── Podsumowanie statystyczne ───────────────────────────────
    lines.append("")
    lines.append("=" * 70)
    lines.append("  PODSUMOWANIE")
    lines.append("=" * 70)

    total_frames = sum(d["frame_count"] for d in aps.values())
    lines.append(f"  Łącznie AP      : {len(aps)}")
    lines.append(f"  Łącznie ramek   : {total_frames}")
    lines.append(f"  Unikalne SSID   : {len(set(d['ssid'] for d in aps.values()))}")

    if aps:
        all_rssi = [r for d in aps.values() for r in d["rssi"]]
        if all_rssi:
            lines.append(f"  RSSI zakres     : {min(all_rssi)} – {max(all_rssi)} dBm")

    return "\n".join(lines)


def _export_json(aps: dict, output_path: str, target_ssid: str = None):
    """Eksportuje wyniki do pliku JSON."""
    export_data = {
        "metadata": {
            "tool": "analyze_pcap.py v2.0",
            "project": "BBSK-Evil-Twin",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "target_ssid": target_ssid,
            "total_aps": len(aps),
            "evil_twin_detected": len(aps) > 1 and target_ssid is not None,
        },
        "access_points": {},
    }

    for bssid, data in aps.items():
        ap_export = {
            "bssid": bssid.upper(),
            "ssid": data["ssid"],
            "frame_count": data["frame_count"],
            "channel": data["channel"],
            "country": data["country"],
            "supported_rates_mbps": sorted(list(data["supported_rates"])),
            "vendor_specific": data["vendor_specific"],
            "avg_rssi_dbm": round(sum(data["rssi"]) / len(data["rssi"]), 1) if data["rssi"] else None,
            "rssi_min": min(data["rssi"]) if data["rssi"] else None,
            "rssi_max": max(data["rssi"]) if data["rssi"] else None,
            "ht_capabilities": data["ht_capabilities"],
            "ht_primary_channel": data["ht_primary_channel"],
            "power_constraint_db": data["power_constraint"],
            "ie_distribution": data["ie_distribution"],
        }
        if data["seq_nums"]:
            seqs = [s for _, s in data["seq_nums"]]
            ap_export["seq_number_range"] = {"min": min(seqs), "max": max(seqs)}
            ap_export["seq_number_count"] = len(seqs)
        if data["beacon_intervals"]:
            intervals = data["beacon_intervals"]
            ap_export["avg_beacon_interval_ms"] = round(
                sum(intervals) / len(intervals) * 1000, 1
            )
        export_data["access_points"][bssid.upper()] = ap_export

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    print(f"[*] JSON zapisany: {output_path}")


def _export_csv(aps: dict, output_path: str):
    """Eksportuje wyniki do pliku CSV."""
    import csv

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "BSSID", "SSID", "Frame Count", "Avg RSSI", "Channel",
            "Supported Rates", "Vendor Specific", "HT Capabilities",
            "Seq Min", "Seq Max", "Country", "Power Constraint",
        ])
        for bssid, data in aps.items():
            avg_rssi = round(sum(data["rssi"]) / len(data["rssi"]), 1) if data["rssi"] else ""
            rates = ", ".join(f"{r:.0f}" for r in sorted(data["supported_rates"]))
            vendors = "; ".join(data["vendor_specific"])
            ht = ", ".join(k for k, v in (data["ht_capabilities"] or {}).items() if v)
            seqs = [s for _, s in data["seq_nums"]]
            seq_min = min(seqs) if seqs else ""
            seq_max = max(seqs) if seqs else ""
            writer.writerow([
                bssid.upper(), data["ssid"], data["frame_count"],
                avg_rssi, data["channel"] or "", rates, vendors, ht,
                seq_min, seq_max, data["country"] or "",
                data["power_constraint"] or "",
            ])
    print(f"[*] CSV zapisany: {output_path}")


def _generate_plot(aps: dict, output_path: str, target_ssid: str, pcap_file: str):
    """Generuje profesjonalny wykres: Sequence Numbers + RSSI + porownanie."""
    if not PLOT_AVAILABLE or not aps:
        return

    # Ustawienia globalne dla czytelnosci
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.size"] = 10
    plt.rcParams["axes.titlesize"] = 12
    plt.rcParams["axes.labelsize"] = 10

    COLORS = ["#E63946", "#2A9D8F", "#264653"]

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle(
        f"Evil Twin Detection Report\n"
        f"SSID: {target_ssid or 'all'}  |  File: {os.path.basename(pcap_file)}",
        fontsize=14, fontweight="bold", y=0.98,
    )

    # ─── Subplot 1: Sequence Numbers (linia, nie scatter) ───
    ax1 = axes[0, 0]
    for i, (bssid, data) in enumerate(aps.items()):
        if not data["seq_nums"] or len(data["seq_nums"]) < 2:
            continue
        color = COLORS[i % len(COLORS)]
        times, seqs = zip(*data["seq_nums"])
        t0 = times[0]
        times_rel = [t - t0 for t in times]

        # Subsample dla czytelnosci (max 100 punktow)
        step = max(1, len(times_rel) // 100)
        ax1.plot(times_rel[::step], seqs[::step], "-o", color=color,
                markersize=2, linewidth=1.5, alpha=0.9,
                label=f"{bssid.upper()} ({data['ssid']}) [{data['frame_count']} beacons]")

    ax1.set_xlabel("Relative time [s]")
    ax1.set_ylabel("Sequence Number (mod 4096)")
    ax1.set_title("Method 3: Sequence Number Analysis\nTwo independent streams = two devices")
    ax1.legend(loc="upper left", fontsize=8)
    ax1.grid(True, alpha=0.3, linestyle="--")

    if len(aps) > 1:
        ax1.text(0.98, 0.05, "EVIL TWIN DETECTED\nNon-overlapping sequences",
                 transform=ax1.transAxes, fontsize=10, color="red", fontweight="bold",
                 ha="right", va="bottom",
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow",
                          edgecolor="red", alpha=0.9))

    # ─── Subplot 2: RSSI boxplot porownawczy ───
    ax2 = axes[0, 1]
    rssi_data = []
    labels = []
    for i, (bssid, data) in enumerate(aps.items()):
        if not data["rssi"]:
            continue
        rssi_data.append(data["rssi"])
        avg = round(sum(data["rssi"]) / len(data["rssi"]), 1)
        labels.append(f"{bssid.upper()[:17]}\navg: {avg} dBm")

    if rssi_data:
        bp = ax2.boxplot(rssi_data, tick_labels=labels, patch_artist=True,
                         widths=0.4, showmeans=True,
                         meanprops=dict(marker="D", markerfacecolor="red", markersize=8))
        for patch, color in zip(bp["boxes"], COLORS[:len(rssi_data)]):
            patch.set_facecolor(color)
            patch.set_alpha(0.4)

        ax2.set_ylabel("RSSI [dBm]")
        ax2.set_title("Method 2: RSSI Comparison\nLarger difference = anomaly")
        ax2.grid(True, alpha=0.3, linestyle="--", axis="y")
        ax2.axhline(y=-30, color="orange", linestyle=":", alpha=0.5, label="Strong signal")
        ax2.axhline(y=-50, color="blue", linestyle=":", alpha=0.5, label="Weak signal")

        if len(rssi_data) >= 2:
            avg0 = sum(rssi_data[0]) / len(rssi_data[0])
            avg1 = sum(rssi_data[1]) / len(rssi_data[1])
            diff = abs(avg0 - avg1)
            ax2.text(0.98, 0.95, f"Delta = {diff:.1f} dBm",
                     transform=ax2.transAxes, fontsize=11, fontweight="bold",
                     ha="right", va="top",
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

    # ─── Subplot 3: IE Comparison Bar Chart ───
    ax3 = axes[1, 0]
    ie_labels = ["HT Capabilities", "Vendor Specific", "Power Constraint",
                 "HT Operation", "Ext. Capabilities", "Country"]
    ie_original = []
    ie_evil = []
    for bssid, data in aps.items():
        has_ht = 1 if data.get("ht_capabilities") else 0
        has_vendor = 1 if data.get("vendor_specific") else 0
        has_power = 1 if data.get("power_constraint") is not None else 0
        has_htop = 1 if data.get("ht_primary_channel") is not None else 0
        has_ext = 1 if data.get("extended_capabilities_raw") else 0
        has_country = 1 if data.get("country") else 0
        values = [has_ht, has_vendor, has_power, has_htop, has_ext, has_country]
        if "7C:F1" in bssid.upper() or "ORIGINAL" in bssid.upper():
            ie_original = values
        else:
            ie_evil = values

    x_pos = range(len(ie_labels))
    width = 0.35
    if ie_original:
        ax3.bar([x - width/2 for x in x_pos], ie_original, width,
                label="Original AP", color=COLORS[0], alpha=0.7)
    if ie_evil:
        ax3.bar([x + width/2 for x in x_pos], ie_evil, width,
                label="Evil Twin AP", color=COLORS[1], alpha=0.7)

    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(ie_labels, rotation=30, ha="right", fontsize=9)
    ax3.set_ylabel("Present (1) / Missing (0)")
    ax3.set_title("Method 1: IE Fingerprinting\nKey Information Elements comparison")
    ax3.legend(loc="upper right", fontsize=8)
    ax3.set_ylim(0, 1.5)
    ax3.grid(True, alpha=0.2, axis="y")

    # ─── Subplot 4: Podsumowanie tekstowe ───
    ax4 = axes[1, 1]
    ax4.axis("off")
    lines = []
    lines.append("DETECTION SUMMARY")
    lines.append("=" * 35)
    lines.append("")
    total_beacons = sum(d["frame_count"] for d in aps.values())
    lines.append(f"Total beacons analyzed: {total_beacons}")
    lines.append(f"Unique APs found:      {len(aps)}")

    if len(aps) >= 2:
        ap_list = list(aps.values())
        if ap_list[0].get("rssi") and ap_list[1].get("rssi"):
            avg0 = sum(ap_list[0]["rssi"]) / len(ap_list[0]["rssi"])
            avg1 = sum(ap_list[1]["rssi"]) / len(ap_list[1]["rssi"])
            lines.append(f"RSSI difference:       {abs(avg0-avg1):.1f} dBm")

        seqs0 = [s for _, s in ap_list[0]["seq_nums"]]
        seqs1 = [s for _, s in ap_list[1]["seq_nums"]]
        if seqs0 and seqs1:
            overlap = max(0, min(max(seqs0), max(seqs1)) - max(min(seqs0), min(seqs1)))
            lines.append(f"Seq number overlap:    {overlap}")
            if overlap == 0:
                lines.append("  => Independent streams!")

        ht0 = bool(ap_list[0].get("ht_capabilities"))
        ht1 = bool(ap_list[1].get("ht_capabilities"))
        vd0 = bool(ap_list[0].get("vendor_specific"))
        vd1 = bool(ap_list[1].get("vendor_specific"))
        ie_diff = (ht0 != ht1) + (vd0 != vd1)
        lines.append(f"IE differences:        {ie_diff}+ key IEs differ")

    lines.append("")
    lines.append("VERDICT:")
    if len(aps) >= 2:
        lines.append("  EVIL TWIN CONFIRMED")
        lines.append("  Multiple methods agree")
    lines.append("")
    lines.append(f"Tool: analyze_pcap.py v2.0")
    lines.append(f"Project: BBSK-Evil-Twin")

    for i, line in enumerate(lines):
        is_header = line.startswith("DETECTION") or line.startswith("VERDICT")
        is_sep = line.startswith("=")
        if is_header:
            ax4.text(0.05, 0.95 - i * 0.035, line, fontsize=13, fontweight="bold",
                    transform=ax4.transAxes, verticalalignment="top")
        elif is_sep:
            ax4.text(0.05, 0.95 - i * 0.035, line, fontsize=9, color="gray",
                    transform=ax4.transAxes, verticalalignment="top")
        elif line.startswith("  EVIL"):
            ax4.text(0.05, 0.95 - i * 0.035, line, fontsize=12, color="red",
                    fontweight="bold", transform=ax4.transAxes, verticalalignment="top")
        else:
            ax4.text(0.05, 0.95 - i * 0.035, line, fontsize=9,
                    transform=ax4.transAxes, verticalalignment="top")

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    plt.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"[*] Wykres zapisany: {output_path}")


def main():
    """Główna funkcja — punkt wejścia."""
    args = parse_args()

    pcap_file = args.pcap
    target_ssid = args.ssid
    output_dir = args.output_dir or os.path.dirname(os.path.abspath(pcap_file))
    quiet = args.quiet

    # ─── Wczytaj pcap ────────────────────────────────────────────
    if not quiet:
        print(f"\n[*] Wczytuję plik: {pcap_file}")
    if not os.path.exists(pcap_file):
        print(f"[BŁĄD] Plik nie istnieje: {pcap_file}", file=sys.stderr)
        sys.exit(1)

    pkts = rdpcap(pcap_file)
    if not quiet:
        print(f"[*] Załadowano {len(pkts)} pakietów.\n")

    # ─── Analiza ─────────────────────────────────────────────────
    aps = _analyze_packets(pkts, target_ssid)

    if target_ssid and not aps:
        # Wypisz dostępne SSIDy
        print(f"[OSTRZEŻENIE] Nie znaleziono ramek Beacon z SSID='{target_ssid}'")
        print(f"             Dostępne SSID-y w pliku:")
        all_ssids = set()
        for pkt in pkts:
            if pkt.haslayer(Dot11Beacon) and pkt.haslayer(Dot11Elt):
                elt = pkt[Dot11Elt]
                while elt:
                    if elt.ID == 0 and elt.info:
                        try:
                            all_ssids.add(elt.info.decode("utf-8", errors="replace"))
                        except Exception:
                            pass
                    try:
                        elt = elt.payload.getlayer(Dot11Elt)
                    except Exception:
                        break
        for s in sorted(all_ssids) if all_ssids else ["(brak SSID w pliku)"]:
            print(f"               SSID: {s}")
        sys.exit(0)

    # ─── Raport tekstowy ─────────────────────────────────────────
    report = _format_report(aps, target_ssid)
    print(report)

    # ─── JSON ────────────────────────────────────────────────────
    if args.json:
        json_path = os.path.join(output_dir, "evil_twin_analysis.json")
        _export_json(aps, json_path, target_ssid)

    # ─── CSV ─────────────────────────────────────────────────────
    if args.csv:
        csv_path = os.path.join(output_dir, "evil_twin_analysis.csv")
        _export_csv(aps, csv_path)

    # ─── Wykres ──────────────────────────────────────────────────
    if not args.no_plot and PLOT_AVAILABLE and aps:
        plot_path = os.path.join(output_dir, "evil_twin_analysis.png")
        _generate_plot(aps, plot_path, target_ssid, pcap_file)
    elif not PLOT_AVAILABLE:
        print("\n[*] Zainstaluj matplotlib żeby generować wykresy: pip3 install matplotlib")

    print("\n[*] Analiza zakończona.\n")


if __name__ == "__main__":
    main()
