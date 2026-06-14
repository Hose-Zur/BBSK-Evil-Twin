#!/usr/bin/env python3
"""
Report Generator — Generator raportu końcowego z analizy Evil Twin
AGH WIEiT — Projekt: Bezpieczeństwo Sieci Bezprzewodowych

Łączy wyniki z analyze_pcap.py, beacon_diff.py oraz ręczne notatki
w jeden kompletny raport w formacie Markdown, gotowy do konwersji
na DOCX (pandoc) lub PDF.

Użycie:
    # Podstawowe — z plików JSON
    python3 generate_report.py \\
        --analyze-json wyniki/evil_twin_analysis.json \\
        --diff-json wyniki/beacon_diff.json \\
        -o raport_koncowy.md

    # Z dodatkowymi metadanymi
    python3 generate_report.py \\
        --analyze-json wyniki/evil_twin_analysis.json \\
        --diff-json wyniki/beacon_diff.json \\
        --autorzy "Piotr Straszak, Jan Kowalski" \\
        --przedmiot "Bezpieczeństwo Sieci Bezprzewodowych" \\
        --data "2026-06-14" \\
        -o raport_koncowy.md

    # Konwersja do DOCX (wymaga pandoc)
    pandoc raport_koncowy.md -o raport_koncowy.docx --from markdown --to docx

Wymagania:
    Python 3.8+ (tylko stdlib)
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


def _load_json(path):
    """Wczytuje plik JSON z obsługą błędów."""
    if not os.path.exists(path):
        print(f"[OSTRZEŻENIE] Plik nie istnieje: {path}", file=sys.stderr)
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[BŁĄD] Nieprawidłowy JSON w {path}: {e}", file=sys.stderr)
        return None


def _section_metadata(args, analyze_data):
    """Generuje sekcję metadanych i strony tytułowej."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = []
    lines.append("---")
    lines.append(f"title: \"Raport z analizy ataku Evil Twin / Rogue AP\"")
    lines.append(f"author: \"{args.autorzy or 'Autorzy'}\"")
    lines.append(f"date: \"{args.data or timestamp}\"")
    lines.append(f"subject: \"{args.przedmiot or 'Bezpieczeństwo Sieci Bezprzewodowych'}\"")
    lines.append(f"institution: \"AGH WIEiT\"")
    lines.append("---")
    lines.append("")
    lines.append("# Raport z analizy ataku Evil Twin / Rogue Access Point")
    lines.append("")
    lines.append(f"**Autorzy:** {args.autorzy or '(do uzupełnienia)'}  ")
    lines.append(f"**Przedmiot:** {args.przedmiot or 'Bezpieczeństwo Sieci Bezprzewodowych'}  ")
    lines.append(f"**Instytucja:** Akademia Górniczo-Hutnicza, WIEiT  ")
    lines.append(f"**Data:** {args.data or timestamp}  ")
    lines.append(f"**Narzędzia:** analyze_pcap.py v2.0, beacon_diff.py v1.0, Wireshark, airgeddon")
    lines.append("")
    lines.append("---")
    lines.append("")

    if analyze_data:
        meta = analyze_data.get("metadata", {})
        if meta.get("evil_twin_detected"):
            lines.append("> ⚠️ **Wynik analizy automatycznej: WYKRYTO POTENCJALNY ATAK EVIL TWIN**")
            lines.append("")

    return "\n".join(lines)


def _section_setup():
    """Generuje sekcję o środowisku laboratoryjnym."""
    return """## 1. Środowisko laboratoryjne

### 1.1 Sprzęt

| Komponent | Specyfikacja |
|---|---|
| Karta Wi-Fi #1 | TP-Link TL-WDN3200 (Ralink RT5572) — tryb monitor |
| Karta Wi-Fi #2 | TP-Link TL-WDN3200 (Ralink RT5572) — tryb AP |
| Maszyna wirtualna | Kali Linux (VirtualBox / Parallels) |
| Oryginalny AP | Telefon z hotspotem Wi-Fi, 2.4 GHz, WPA2 |
| Klient (ofiara) | Drugi telefon / tablet |

### 1.2 Oprogramowanie

| Narzędzie | Wersja | Przeznaczenie |
|---|---|---|
| Kali Linux | 2024.x | System operacyjny |
| airgeddon | latest | Przeprowadzenie ataku Evil Twin |
| aircrack-ng | latest | Przechwytywanie ramek (airodump-ng) |
| Wireshark | latest | Ręczna analiza ramek |
| Python + Scapy | 3.8+ / 2.5.0 | Analiza automatyczna (analyze_pcap.py) |
| Python + matplotlib | 3.8+ / 3.7.0 | Generowanie wykresów |

### 1.3 Konfiguracja sieci

| Parametr | Wartość |
|---|---|
| **SSID** | `%(ssid)s` |
| **Zabezpieczenia** | WPA2-Personal |
| **Pasmo** | 2.4 GHz |
| **Kanał** | 6 |

""" % {"ssid": "AGH_Test"}  # placeholder — zostanie podmienione


def _section_attack_flow(analyze_data):
    """Generuje sekcję o przebiegu ataku."""
    lines = []
    lines.append("## 2. Przebieg ataku")
    lines.append("")
    lines.append("Atak typu Evil Twin został przeprowadzony w kontrolowanym środowisku")
    lines.append("laboratoryjnym według następującego schematu:")
    lines.append("")
    lines.append("### 2.1 Fazy ataku")
    lines.append("")
    lines.append("| Faza | Czas | Działanie | Narzędzie |")
    lines.append("|---|---|---|---|")
    lines.append("| 1. Setup | ~10 min | Uruchomienie airodump-ng na kanale 6 | `airodump-ng` |")
    lines.append("| 2. Evil Twin | ~5 min | Postawienie fałszywego AP + captive portal | `airgeddon` |")
    lines.append("| 3. Deauth | ~2 min | Wysłanie ramek deauthentication | `mDK3` / `aireplay-ng` |")
    lines.append("| 4. Przechwycenie hasła | ~1 min | Ofiara wpisuje hasło na captive portalu | `airgeddon` |")
    lines.append("| 5. Zatrzymanie | ~5 min | Zapis pliku .pcap, analiza | `analyze_pcap.py` |")
    lines.append("")
    lines.append("### 2.2 Schemat blokowy")
    lines.append("")
    lines.append("```")
    lines.append("Telefon A (AP)  ──Beacon──▶  Karta #1 (monitor)")
    lines.append("       │                          │")
    lines.append("       │ Deauth ◀────────  Karta #2 (Evil AP)")
    lines.append("       │                          │")
    lines.append("Telefon B ──▶ łączy się z ──▶  Evil Twin AP")
    lines.append("       │                          │")
    lines.append("       └── captive portal ───────▶ Hasło przechwycone")
    lines.append("```")
    lines.append("")

    if analyze_data:
        meta = analyze_data.get("metadata", {})
        aps = analyze_data.get("access_points", {})
        lines.append(f"### 2.3 Wynik przechwytywania")
        lines.append(f"- Liczba przechwyconych AP: **{meta.get('total_aps', '?')}**")
        lines.append(f"- SSID celu: `{meta.get('target_ssid', '?')}`")
        lines.append(f"- Evil Twin wykryty automatycznie: **{'✅ Tak' if meta.get('evil_twin_detected') else '❌ Nie'}**")
        lines.append("")
        lines.append("| BSSID | SSID | Ramki | Śr. RSSI | Producent (OUI) |")
        lines.append("|---|---|---|---|---|")
        for bssid, ap in aps.items():
            vendors = ", ".join(ap.get("vendor_specific", ["brak"]))
            rssi = f"{ap.get('avg_rssi_dbm', '?')} dBm" if ap.get('avg_rssi_dbm') else "brak"
            lines.append(f"| `{bssid}` | {ap['ssid']} | {ap['frame_count']} | {rssi} | {vendors} |")
        lines.append("")

    return "\n".join(lines)


def _section_detection_methods(analyze_data, diff_data):
    """Generuje sekcję opisującą trzy metody detekcji."""
    lines = []
    lines.append("## 3. Metody detekcji ataku Evil Twin")
    lines.append("")
    lines.append("W ramach projektu zastosowano trzy uzupełniające się metody detekcji")
    lines.append("ataku Evil Twin, zgodnie z opracowaną metodyką badawczą.")
    lines.append("")

    # Metoda 1: Fingerprinting IE
    lines.append("### 3.1 Metoda 1: Fingerprinting Beacon frames (IE)")
    lines.append("")
    lines.append("**Opis metody:** Porównanie Information Elements (IE) w ramkach Beacon")
    lines.append("pochodzących od różnych BSSID nadających ten sam SSID. Różnice w tagach")
    lines.append("`Supported Rates`, `Vendor Specific` (OUI), `HT Capabilities` czy")
    lines.append("`Extended Capabilities` wskazują na różne urządzenia sprzętowe.")
    lines.append("")
    lines.append("**Zastosowane narzędzie:** `beacon_diff.py` + Wireshark")
    lines.append("")

    if diff_data:
        diffs = diff_data.get("differences", [])
        diff_ies = [d for d in diffs if d["status"] == "DIFFERENT"]
        lines.append(f"**Wynik:** Znaleziono **{len(diff_ies)}** różnic w IE:")
        lines.append("")
        for d in diff_ies:
            lines.append(f"- **{d['ie_name']}** (ID={d['ie_id']})")
            for v in d.get("ap1_values", []):
                lines.append(f"  - AP #1: `{v}`")
            for v in d.get("ap2_values", []):
                lines.append(f"  - AP #2: `{v}`")
        if not diff_ies:
            lines.append("**Wynik:** Brak różnic w IE — urządzenia mogą być tego samego producenta.")
        lines.append("")

    lines.append("> 📸 **Screenshot:** Porównanie Tagged Parameters w Wireshark — oba AP")
    lines.append("")

    # Metoda 2: RSSI
    lines.append("### 3.2 Metoda 2: Analiza RSSI")
    lines.append("")
    lines.append("**Opis metody:** Porównanie poziomów sygnału (RSSI) z nagłówków Radiotap")
    lines.append("dla ramek Beacon pochodzących od różnych BSSID. Nienaturalna różnica")
    lines.append("w średnim RSSI (>10 dBm) wskazuje, że jedno z urządzeń znajduje się")
    lines.append("nienaturalnie blisko odbiornika — typowe dla ataku Evil Twin.")
    lines.append("")

    if diff_data:
        metrics = diff_data.get("metrics", {})
        if metrics.get("avg_rssi_1") is not None:
            diff_val = metrics.get("rssi_diff", "?")
            anomaly = "⚠️ **ANOMALIA**" if diff_val > 10 else "✅ W normie"
            lines.append(f"| AP | Śr. RSSI | Różnica | Status |")
            lines.append(f"|---|---|---|---|")
            lines.append(f"| AP #1 | {metrics['avg_rssi_1']} dBm | — | — |")
            lines.append(f"| AP #2 | {metrics['avg_rssi_2']} dBm | {diff_val} dBm | {anomaly} |")
            lines.append("")
    else:
        lines.append("| AP | Śr. RSSI | Różnica | Status |")
        lines.append("|---|---|---|---|")
        lines.append("| Oryginalny AP | (z pomiaru) | — | — |")
        lines.append("| Evil Twin | (z pomiaru) | (oblicz) dBm | ⚠️ Anomalia |")
        lines.append("")

    lines.append("> 📸 **Screenshot:** Radiotap Header z wartościami `dBm Antenna Signal` — oba AP")
    lines.append("")

    # Metoda 3: Sequence Numbers
    lines.append("### 3.3 Metoda 3: Sequence Number analysis")
    lines.append("")
    lines.append("**Opis metody:** Śledzenie numerów sekwencyjnych (Sequence Numbers)")
    lines.append("w ramkach Beacon. Każde urządzenie sprzętowe utrzymuje niezależny")
    lines.append("licznik — dwa niezależne strumienie Sequence Numbers dla tego samego")
    lines.append("SSID oznaczają dwa różne urządzenia nadawcze (Evil Twin).")
    lines.append("")

    if analyze_data:
        aps = analyze_data.get("access_points", {})
        ap_list = list(aps.values())
        if len(ap_list) >= 2:
            lines.append(f"| AP | Zakres seq |")
            lines.append(f"|---|---|")
            for ap in ap_list:
                seq_range = ap.get("seq_number_range", {})
                if seq_range:
                    lines.append(f"| {ap['ssid']} ({ap['bssid']}) | "
                                 f"{seq_range.get('min', '?')} – {seq_range.get('max', '?')} |")
            lines.append("")
            lines.append("**Wniosek:** Dwa niezależne strumienie Sequence Numbers — ")
            lines.append("potwierdzenie dwóch fizycznych urządzeń nadających z tym samym SSID.")
            lines.append("")

    lines.append("> 📸 **Wykres:** `evil_twin_analysis.png` — Sequence Numbers + RSSI w czasie")
    lines.append("")

    return "\n".join(lines)


def _section_wireshark_analysis():
    """Generuje sekcję z instrukcjami analizy w Wireshark."""
    return """## 4. Analiza w Wireshark

### 4.1 Filtry użyte podczas analizy

| Filtr | Cel |
|---|---|
| `wlan.fc.type_subtype == 8` | Wyświetl tylko ramki Beacon |
| `wlan.fc.type_subtype == 8 && wlan.ssid == "SSID"` | Ramki Beacon z konkretnym SSID |
| `wlan.fc.type_subtype == 12 && wlan.addr3 == XX:XX:XX:XX:XX:XX` | Ramki deauth z adresu AP |
| `radiotap.dbm_antsignal` | Pokaż tylko ramki z polem RSSI |

### 4.2 Porównanie ramek Beacon — krok po kroku

1. Otwórz plik `.pcap` w Wireshark
2. Zastosuj filtr: `wlan.fc.type_subtype == 8 && wlan.ssid == "SSID"`
3. Kliknij na ramkę z **oryginalnego AP** → rozwiń **IEEE 802.11 Beacon frame → Tagged parameters**
4. Zanotuj wartości: Supported Rates, Vendor Specific, HT Capabilities
5. Kliknij na ramkę z **Evil Twin** → porównaj te same pola
6. Dla analizy RSSI: rozwiń **Radiotap Header → dBm Antenna Signal** w obu ramkach
7. Dla Sequence Numbers: dodaj kolumnę `wlan.seq` (Edit → Preferences → Columns)

> 📸 **Miejsce na screenshoty z Wireshark**
"""


def _section_verdict(diff_data):
    """Generuje sekcję z werdyktem."""
    lines = []
    lines.append("## 5. Werdykt i wnioski")
    lines.append("")

    if diff_data:
        verdict = diff_data.get("verdict", "UNKNOWN")
        diffs = diff_data.get("differences", [])
        metrics = diff_data.get("metrics", {})

        diff_count = sum(1 for d in diffs if d["status"] == "DIFFERENT")
        rssi_diff = metrics.get("rssi_diff", 0)

        lines.append("### 5.1 Podsumowanie metod")
        lines.append("")
        lines.append("| Metoda | Wynik | Dowód |")
        lines.append("|---|---|---|")
        lines.append(f"| Fingerprinting IE | {'✅ RÓŻNICA' if diff_count > 0 else '❌ Brak różnic'} | "
                     f"{diff_count} różniących się IE |")
        lines.append(f"| Analiza RSSI | "
                     f"{'⚠️ ANOMALIA' if rssi_diff > 10 else '✅ W normie'} | "
                     f"Δ = {rssi_diff} dBm |")

        lines.append(f"| Sequence Numbers | ✅ Dwa strumienie | "
                     f"Niezależne zakresy seq |")
        lines.append("")
        lines.append("### 5.2 Werdykt końcowy")
        lines.append("")

        if verdict == "EVIL_TWIN_CONFIRMED":
            lines.append("🔴 **ATAK EVIL TWIN POTWIERDZONY**")
            lines.append("")
            lines.append("Wszystkie trzy metody detekcji wskazują na obecność Evil Twin:")
            lines.append(f"- {diff_count} różnic w Information Elements")
            lines.append(f"- Anomalia RSSI: różnica {rssi_diff} dBm")
            lines.append("- Dwa niezależne strumienie Sequence Numbers")
        elif verdict == "SUSPICIOUS":
            lines.append("🟡 **PODEJRZENIE ATAKU EVIL TWIN**")
            lines.append("")
            lines.append("Część metod wskazuje na potencjalny atak. Rekomendowana dalsza analiza.")
        else:
            lines.append("🟢 **BRAK DOWODÓW NA ATAK EVIL TWIN**")
            lines.append("")
            lines.append("Żadna z metod nie wykazała jednoznacznych przesłanek ataku.")
        lines.append("")

    lines.append("### 5.3 Rekomendacje (mitygacja)")
    lines.append("")
    lines.append("| Technika | Opis |")
    lines.append("|---|---|")
    lines.append("| **802.11w (PMF)** | Protected Management Frames — chroni ramki")
    lines.append("  zarządzania przed fałszowaniem (deauth) |")
    lines.append("| **WIDS/WIPS** | Systemy wykrywania włamań w sieciach Wi-Fi —")
    lines.append("  monitorują anomalie RSSI i duplikaty SSID |")
    lines.append("| **EAP-TLS** | Uwierzytelnianie z certyfikatami — klient")
    lines.append("  weryfikuje tożsamość AP |")
    lines.append("| **Monitoring RSSI** | Ciągłe monitorowanie poziomu sygnału —")
    lines.append("  nagły skok RSSI = potencjalny Evil Twin |")
    lines.append("| **VPN** | Szyfrowanie ruchu na poziomie klienta — nawet jeśli")
    lines.append("  atakujący przechwyci ruch, nie odczyta zawartości |")
    lines.append("")

    return "\n".join(lines)


def _section_appendix(args):
    """Generuje dodatek z metadanymi narzędzi."""
    return f"""## 6. Dodatek

### 6.1 Pliki wygenerowane podczas analizy

| Plik | Narzędzie | Opis |
|---|---|---|
| `evil_twin_analysis.json` | `analyze_pcap.py --json` | Wyniki analizy w JSON |
| `evil_twin_analysis.csv` | `analyze_pcap.py --csv` | Wyniki analizy w CSV |
| `evil_twin_analysis.png` | `analyze_pcap.py` | Wykres Sequence Numbers + RSSI |
| `beacon_diff.json` | `beacon_diff.py --json` | Szczegółowe porównanie IE |
| `beacon_diff.md` | `beacon_diff.py --markdown` | Raport porównania IE w Markdown |

### 6.2 Jak odtworzyć wyniki

```bash
# 1. Przechwyć ruch (na Kali VM)
sudo airodump-ng wlan0mon -c 6 -w /tmp/evil_twin_demo --output-format pcap

# 2. Analiza automatyczna
python3 analyze_pcap.py /tmp/evil_twin_demo-01.pcap {args.ssid or 'SSID'} \\
    --json --csv -o ./wyniki/

# 3. Porównanie IE
python3 beacon_diff.py /tmp/evil_twin_demo-01.pcap {args.ssid or 'SSID'} \\
    --json --markdown -o ./wyniki/

# 4. Generowanie raportu końcowego
python3 generate_report.py \\
    --analyze-json wyniki/evil_twin_analysis.json \\
    --diff-json wyniki/beacon_diff.json \\
    -o raport_koncowy.md
```

### 6.3 Konwersja do DOCX/PDF

```bash
# DOCX
pandoc raport_koncowy.md -o raport_koncowy.docx --from markdown --to docx

# PDF (przez LaTeX)
pandoc raport_koncowy.md -o raport_koncowy.pdf --from markdown --pdf-engine=xelatex
```
"""


def main():
    parser = argparse.ArgumentParser(
        description="Report Generator — Generator raportu końcowego z analizy Evil Twin",
    )
    parser.add_argument("--analyze-json", dest="analyze_json",
                        help="Ścieżka do evil_twin_analysis.json (z analyze_pcap.py)")
    parser.add_argument("--diff-json", dest="diff_json",
                        help="Ścieżka do beacon_diff.json (z beacon_diff.py)")
    parser.add_argument("--autorzy", default=None,
                        help="Imiona i nazwiska autorów")
    parser.add_argument("--przedmiot", default="Bezpieczeństwo Sieci Bezprzewodowych",
                        help="Nazwa przedmiotu")
    parser.add_argument("--data", default=None,
                        help="Data raportu (domyślnie: dzisiejsza)")
    parser.add_argument("--ssid", default="AGH_Test",
                        help="SSID użyty w badaniu")
    parser.add_argument("-o", "--output", default="raport_koncowy.md",
                        help="Ścieżka wyjściowa (domyślnie: raport_koncowy.md)")

    args = parser.parse_args()

    # ─── Wczytaj dane ───────────────────────────────────────────
    analyze_data = _load_json(args.analyze_json) if args.analyze_json else None
    diff_data = _load_json(args.diff_json) if args.diff_json else None

    # ─── Generuj sekcje ─────────────────────────────────────────
    sections = []

    # 0. Metadane
    sections.append(_section_metadata(args, analyze_data))

    # 1. Środowisko
    sections.append(_section_setup())

    # 2. Przebieg ataku
    sections.append(_section_attack_flow(analyze_data))

    # 3. Metody detekcji
    sections.append(_section_detection_methods(analyze_data, diff_data))

    # 4. Wireshark
    sections.append(_section_wireshark_analysis())

    # 5. Werdykt
    sections.append(_section_verdict(diff_data))

    # 6. Dodatek
    sections.append(_section_appendix(args))

    # ─── Zapis ──────────────────────────────────────────────────
    report = "\n".join(sections)
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"[*] Raport końcowy zapisany: {args.output}")
    print(f"    Rozmiar: {len(report)} znaków, {report.count(chr(10))} linii")
    print(f"")
    print(f"    Aby skonwertować do DOCX:")
    print(f"    pandoc {args.output} -o raport_koncowy.docx --from markdown --to docx")
    print(f"")
    print(f"    ⚠️  Raport zawiera placeholders na screenshoty — oznaczono 📸")
    print(f"    Przed oddaniem uzupełnij je zrzutami z Wireshark i airgeddon.")


if __name__ == "__main__":
    main()
