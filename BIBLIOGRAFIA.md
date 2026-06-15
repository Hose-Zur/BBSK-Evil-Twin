# Bibliografia — Narzędzia i repozytoria wykorzystane w projekcie

## Narzędzia własne (autorskie)

| Narzędzie | Link | Opis |
|---|---|---|
| analyze_pcap.py | [repo](https://github.com/Hose-Zur/BBSK-Evil-Twin) | Automatyczna analiza beacon frames, detekcja Evil Twin |
| beacon_diff.py | [repo](https://github.com/Hose-Zur/BBSK-Evil-Twin) | Szczegółowe porównanie Information Elements między AP |
| generate_report.py | [repo](https://github.com/Hose-Zur/BBSK-Evil-Twin) | Generator raportu końcowego w Markdown |

## Narzędzia zewnętrzne — ofensywne (atak)

| Narzędzie | Link | Typ ataku |
|---|---|---|
| airgeddon | https://github.com/v1s1t0r1sh3r3/airgeddon | Evil Twin + captive portal |
| hostapd-mana | https://github.com/sensepost/hostapd-mana | KARMA / MANA |
| eaphammer | https://github.com/s0lst1c3/eaphammer | Evil Twin przeciwko WPA2-Enterprise |
| create_ap | https://github.com/lakinduakash/linux-wifi-hotspot | Tworzenie AP z NAT |
| WiFiSlayer | https://github.com/waheeb71/WiFiSlayer | Zautomatyzowane ataki Wi-Fi |

## Narzędzia zewnętrzne — defensywne (detekcja)

| Narzędzie | Link | Metoda detekcji |
|---|---|---|
| Snappy | https://github.com/SpiderLabs/snappy | Fingerprinting struktury ramek |
| RogueAP-Detector | https://github.com/anotherik/RogueAP-Detector | Modułowa detekcja (scanner/detector/actuator) |

## Narzędzia standardowe (Kali Linux)

| Narzędzie | Pakiet | Zastosowanie |
|---|---|---|
| airodump-ng | aircrack-ng | Przechwytywanie ramek 802.11 |
| aireplay-ng | aircrack-ng | Wysyłanie ramek deauth |
| aircrack-ng | aircrack-ng | Łamanie WPA handshake |
| mdk4 | mdk4 | Zaawansowany deauth flood |
| hashcat | hashcat | Łamanie PMKID/WPA2 |
| hcxdumptool | hcxtools | Przechwytywanie PMKID |
| tcpdump | tcpdump | Monitoring ruchu sieciowego |
| Wireshark | wireshark | Ręczna analiza ramek |

## Standardy i protokoły

| Standard | Opis |
|---|---|
| IEEE 802.11-2020 | Standard Wi-Fi |
| IEEE 802.11w | Protected Management Frames (PMF) |
| WPA2 (802.11i) | Wi-Fi Protected Access 2 |
| WPA3 | Wi-Fi Protected Access 3 (SAE) |
| EAP-TLS | Extensible Authentication Protocol - TLS |

## Literatura

| Pozycja | Autor | Rok |
|---|---|---|
| KARMA Attack (Defcon) | Dino dai Zovi, Shane Macaulay | 2004 |
| MANA Toolkit (Defcon 22) | SensePost (Dominic White, Ian de Villiers) | 2014 |
| Evil Twin Framework | MITRE ATT&CK T1557.004 | 2021 |

---
*Ostatnia aktualizacja: 2026-06-15*
