# Katalog na screenshoty z części praktycznej

Umieść tutaj zrzuty ekranu z wykonania ataku i analizy.

## Lista wymaganych screenshotów

| # | Nazwa pliku | Zawartość | Źródło |
|---|---|---|---|
| 01 | `01_airodump.png` | Terminal z działającym airodump-ng (widać SSID) | Kali VM — Terminal 1 |
| 02 | `02_airgeddon_haslo.png` | Terminal airgeddon z przechwyconym hasłem | Kali VM — Terminal 2 |
| 03 | `03_captive_portal.png` | Strona captive portala na telefonie ofiary | Telefon B |
| 04 | `04_analiza_tekstowa.png` | Raport tekstowy z analyze_pcap.py (ostrzeżenie Evil Twin) | Terminal Kali |
| 05 | `05_wykres_seq_rssi.png` | Wykres evil_twin_analysis.png — dwa strumienie seq | analyze_pcap.py |
| 06 | `06_beacon_diff.png` | Raport z beacon_diff.py (lista różnic IE) | Terminal Kali |
| 07 | `07_wireshark_ie_oryginal.png` | Wireshark — Tagged parameters oryginalnego AP | Wireshark |
| 08 | `08_wireshark_ie_evil.png` | Wireshark — Tagged parameters Evil Twin (różnice) | Wireshark |
| 09 | `09_wireshark_rssi.png` | Wireshark — Radiotap dBm Antenna Signal (oba AP) | Wireshark |
| 10 | `10_wireshark_seq.png` | Wireshark — kolumna Seq z dwoma strumieniami | Wireshark |
| 11 | `11_wireshark_deauth.png` | Wireshark — ramki deauth (typ 12) | Wireshark |

## Jak zrobić screenshoty

### Na Kali Linux (z terminala)
```bash
# Screenshot całego ekranu
gnome-screenshot -f screenshoty/01_airodump.png

# Screenshot aktywnego okna
gnome-screenshot -w -f screenshoty/02_airgeddon_haslo.png

# Screenshot obszaru
gnome-screenshot -a -f screenshoty/04_analiza_tekstowa.png
```

### Na telefonie (captive portal)
- Android: Power + Volume Down
- iOS: Power + Volume Up

### W Wireshark
- **File → Export Packet Dissections → As PNG**
- lub screenshot okna z zaznaczonymi istotnymi polami

## Instrukcja

1. Przed sesją praktyczną: przygotuj ten katalog (stwórz go jeśli nie istnieje)
2. Podczas sesji: rób screenshoty po każdym istotnym kroku
3. Po sesji: wstaw screenshoty do raportu końcowego w miejscach 📸
4. Alternatywnie: użyj `generate_report.py` który ma wbudowane miejsce na screenshoty
