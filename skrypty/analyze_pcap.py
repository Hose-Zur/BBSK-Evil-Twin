#!/usr/bin/env python3
"""
Evil Twin Detection — Analiza pliku .pcap
AGH WIEiT — Projekt: Bezpieczeństwo Sieci Bezprzewodowych

Użycie:
    python3 analyze_pcap.py <plik.pcap> [SSID]

Przykład:
    python3 analyze_pcap.py /tmp/demo-01.pcap AGH_WirelessLab

Wymagania:
    pip3 install scapy matplotlib
"""

import sys
import os
from collections import defaultdict

try:
    from scapy.all import rdpcap, Dot11Beacon, Dot11, Dot11Elt, RadioTap
except ImportError:
    print("[BŁĄD] Brak biblioteki scapy. Zainstaluj: pip3 install scapy")
    sys.exit(1)

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    PLOT_AVAILABLE = True
except ImportError:
    print("[OSTRZEŻENIE] Brak matplotlib — wykresy niedostępne. pip3 install matplotlib")
    PLOT_AVAILABLE = False


# ─── Konfiguracja ────────────────────────────────────────────────
PCAP_FILE   = sys.argv[1] if len(sys.argv) > 1 else "/tmp/demo-01.pcap"
TARGET_SSID = sys.argv[2] if len(sys.argv) > 2 else None   # None = wszystkie SSIDy
OUTPUT_DIR  = os.path.dirname(os.path.abspath(PCAP_FILE))

COLORS = ["#E63946", "#2A9D8F", "#E9C46A", "#264653", "#A8DADC"]


# ─── Wczytaj pcap ────────────────────────────────────────────────
print(f"\n[*] Wczytuję plik: {PCAP_FILE}")
if not os.path.exists(PCAP_FILE):
    print(f"[BŁĄD] Plik nie istnieje: {PCAP_FILE}")
    sys.exit(1)

pkts = rdpcap(PCAP_FILE)
print(f"[*] Załadowano {len(pkts)} pakietów.\n")


# ─── Zbieranie danych z ramek Beacon ─────────────────────────────
# Struktura: {bssid: {ssid, seq_nums: [(time, seq)], rssi: [int], rates: set, vendor: str}}
aps = defaultdict(lambda: {
    "ssid": "?",
    "seq_nums": [],
    "rssi": [],
    "supported_rates": set(),
    "vendor_specific": [],
    "frame_count": 0,
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

    # SSID
    if pkt.haslayer(Dot11Elt):
        elt = pkt[Dot11Elt]
        while elt:
            if elt.ID == 0 and elt.info:
                try:
                    ssid = elt.info.decode("utf-8", errors="replace")
                    ap["ssid"] = ssid
                except Exception:
                    pass
            # Supported Rates (ID=1) i Extended Supported Rates (ID=50)
            if elt.ID in (1, 50) and elt.info:
                for b in elt.info:
                    rate_mbps = (b & 0x7F) * 0.5
                    ap["supported_rates"].add(rate_mbps)
            # Vendor Specific (ID=221)
            if elt.ID == 221 and elt.info and len(elt.info) >= 3:
                oui = elt.info[:3].hex().upper()
                known = {
                    "0050F2": "Microsoft/WPS",
                    "00904C": "Epigram",
                    "001018": "Broadcom",
                    "000C03": "Apple",
                    "00037F": "Atheros",
                    "0017F2": "Apple",
                    "00037F": "Atheros/Qualcomm",
                }
                label = known.get(oui, f"OUI:{oui}")
                if label not in ap["vendor_specific"]:
                    ap["vendor_specific"].append(label)

            try:
                elt = elt.payload.getlayer(Dot11Elt)
            except Exception:
                break

    # Sequence Number
    if pkt.haslayer(Dot11):
        seq = pkt[Dot11].SC >> 4
        ap["seq_nums"].append((float(pkt.time), seq))

    # RSSI z nagłówka Radiotap
    if pkt.haslayer(RadioTap):
        try:
            rssi = pkt[RadioTap].dBm_AntSignal
            if rssi is not None and rssi != 0:
                ap["rssi"].append(int(rssi))
        except AttributeError:
            pass


# ─── Filtruj po SSID jeśli podano ────────────────────────────────
if TARGET_SSID:
    aps = {b: d for b, d in aps.items() if d["ssid"] == TARGET_SSID}
    if not aps:
        print(f"[OSTRZEŻENIE] Nie znaleziono ramek Beacon z SSID='{TARGET_SSID}'")
        print(f"             Dostępne SSID-y w pliku:")
        all_aps = defaultdict(lambda: {"ssid": "?", "seq_nums": [], "rssi": [], "supported_rates": set(), "vendor_specific": [], "frame_count": 0})
        for pkt in pkts:
            if pkt.haslayer(Dot11Beacon) and pkt.haslayer(Dot11Elt):
                elt = pkt[Dot11Elt]
                bssid = (pkt.addr3 or "?").lower()
                while elt:
                    if elt.ID == 0 and elt.info:
                        try:
                            print(f"               SSID: {elt.info.decode('utf-8', errors='replace')}  BSSID: {bssid}")
                        except:
                            pass
                    try:
                        elt = elt.payload.getlayer(Dot11Elt)
                    except:
                        break
        sys.exit(0)


# ─── Raport tekstowy ─────────────────────────────────────────────
print("=" * 70)
print(f"  WYKRYTE PUNKTY DOSTĘPOWE — {f'SSID: {TARGET_SSID}' if TARGET_SSID else 'wszystkie'}")
print("=" * 70)

if len(aps) > 1 and TARGET_SSID:
    print(f"\n  [!] UWAGA: {len(aps)} urządzeń nadaje z SSID='{TARGET_SSID}'")
    print(f"      To jest wskaźnik ataku Evil Twin!\n")

for i, (bssid, data) in enumerate(aps.items()):
    avg_rssi = round(sum(data["rssi"]) / len(data["rssi"]), 1) if data["rssi"] else "brak"
    rates_sorted = sorted(data["supported_rates"])
    rates_str = ", ".join(f"{r:.0f}" for r in rates_sorted) + " Mbps" if rates_sorted else "brak danych"
    vendors = ", ".join(data["vendor_specific"]) if data["vendor_specific"] else "brak (lub brak Vendor Specific IE)"

    print(f"\n  AP #{i+1}")
    print(f"  BSSID           : {bssid.upper()}")
    print(f"  SSID            : {data['ssid']}")
    print(f"  Ramki Beacon    : {data['frame_count']}")
    print(f"  Avg RSSI        : {avg_rssi} dBm")
    print(f"  Supported Rates : {rates_str}")
    print(f"  Vendor Specific : {vendors}")
    seq_range = ""
    if data["seq_nums"]:
        seqs = [s for _, s in data["seq_nums"]]
        seq_range = f"{min(seqs)} – {max(seqs)}"
    print(f"  Seq Numbers     : {seq_range}")


# ─── Wykres Sequence Numbers ─────────────────────────────────────
if PLOT_AVAILABLE and aps:
    fig, axes = plt.subplots(2, 1, figsize=(14, 8))
    fig.suptitle(
        f"Evil Twin Detection — AP Fingerprinting\n"
        f"SSID: {TARGET_SSID or 'wszystkie'}   |   Plik: {os.path.basename(PCAP_FILE)}",
        fontsize=13, fontweight="bold", y=0.98
    )

    # --- Subplot 1: Sequence Numbers ---
    ax1 = axes[0]
    patches = []
    for i, (bssid, data) in enumerate(aps.items()):
        if not data["seq_nums"]:
            continue
        color = COLORS[i % len(COLORS)]
        times, seqs = zip(*data["seq_nums"])
        t0 = times[0]
        times_rel = [t - t0 for t in times]

        ax1.scatter(times_rel, seqs, s=3, color=color, alpha=0.8)
        label = f"{bssid.upper()} | SSID: {data['ssid']} | {data['frame_count']} ramek"
        patches.append(mpatches.Patch(color=color, label=label))

    ax1.set_xlabel("Czas relatywny [s]", fontsize=10)
    ax1.set_ylabel("Sequence Number", fontsize=10)
    ax1.set_title("Sequence Numbers — rozwidlenie = dwa różne urządzenia sprzętowe (Evil Twin)", fontsize=11)
    ax1.legend(handles=patches, loc="upper left", fontsize=8)
    ax1.grid(True, alpha=0.3)
    if len(aps) > 1:
        ax1.annotate(
            "ANOMALIA: dwa strumienie\ndla tego samego SSID",
            xy=(0.02, 0.92), xycoords="axes fraction",
            fontsize=9, color="red",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", edgecolor="red")
        )

    # --- Subplot 2: RSSI w czasie ---
    ax2 = axes[1]
    patches2 = []
    for i, (bssid, data) in enumerate(aps.items()):
        if not data["rssi"] or not data["seq_nums"]:
            continue
        color = COLORS[i % len(COLORS)]
        # Pobierz timestampy z seq_nums (mamy je jako pary)
        times = [t for t, _ in data["seq_nums"]]
        t0 = min(times)
        # RSSI może mieć inną długość — użyj minimum
        n = min(len(times), len(data["rssi"]))
        times_rel = [t - t0 for t in times[:n]]
        rssi_vals = data["rssi"][:n]

        ax2.scatter(times_rel, rssi_vals, s=3, color=color, alpha=0.6)
        avg = round(sum(rssi_vals) / len(rssi_vals), 1)
        label = f"{bssid.upper()} | avg RSSI: {avg} dBm"
        patches2.append(mpatches.Patch(color=color, label=label))

    ax2.set_xlabel("Czas relatywny [s]", fontsize=10)
    ax2.set_ylabel("RSSI [dBm]", fontsize=10)
    ax2.set_title("RSSI w czasie — nienaturalny skok sygnału wskazuje na Evil Twin", fontsize=11)
    ax2.legend(handles=patches2, loc="upper left", fontsize=8)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out_path = os.path.join(OUTPUT_DIR, "evil_twin_analysis.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\n[*] Wykres zapisany: {out_path}")
    plt.show()

else:
    if not PLOT_AVAILABLE:
        print("\n[*] Zainstaluj matplotlib żeby generować wykresy: pip3 install matplotlib")

print("\n[*] Analiza zakończona.\n")
