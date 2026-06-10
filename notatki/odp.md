Dobra, przeczytałem wszystko od deski do deski — maile, czaty z Piotrkiem, outline, artykuły, GitHub repo. Mam pełen obraz. Oto co widzę i co bym w waszej sytuacji zrobił.

---

## Ocena sytuacji

**Co macie:**
- 2× TP-Link TL-WDN3200 (chipset Ralink RT5572) — potwierdzone monitor + injection ✅
- Kali VM (VirtualBox/Parallels)
- Teoria gotowa (outline sekcje 1–5)
- **Brakuje:** praktycznego dema i materiału analitycznego

**Co musicie pokazać** wg waszego własnego outline'u — SEKCJA 3 to "Główna część badawcza". Nie atak sam w sobie, tylko **detekcja**: RSSI, Beacon frames, Fingerprinting. Atak jest tylko narzędziem do wygenerowania materiału analitycznego.

---

## Plan na 3 godziny — minimum viable demo

### Faza 1 (30 min) — Setup środowiska

Telefon jako "prawdziwy AP":
- SSID: `AGH_WirelessLab` (cokolwiek)
- WPA2-Personal, kanał **6**, pasmo 2.4GHz
- Podłącz drugi telefon/tablet jako "ofiarę"

Kali VM — upewnij się, że obie karty są passthrough do VM:
```bash
# Sprawdź interfejsy
iw dev
# Powinieneś widzieć dwie karty bezprzewodowe (wlan0, wlan1 lub podobnie)

# Sprawdź AP mode support (dla RT5572 powinno być ok)
iw list | grep -A 10 "Supported interface modes"
```

Zainstaluj jeśli nie ma:
```bash
sudo apt update && sudo apt install airgeddon -y
```

---

### Faza 2 (30 min) — Uruchom capture + atak

**W pierwszym terminalu** — zacznij zbierać pcap na karcie 1:
```bash
sudo airmon-ng start wlan0
sudo airodump-ng wlan0mon -c 6 -w /tmp/demo --output-format pcap
# Zostaw to działające w tle przez CAŁY czas ataku
```

**W drugim terminalu** — Airgeddon na karcie 2:
```bash
sudo airgeddon
# → [9] Evil Twin AP attacks
# → Wybierz swój SSID (AGH_WirelessLab)
# → Captive Portal attack
# → Deauthentication: mDK3 lub aireplay
# → Narzędzie samo postawi DHCP, fake AP, captive portal
```

Poczekaj aż ofiara (drugi telefon) dostanie deauth i połączy się z evil twin. Wpisz hasło na captive portalu. Zatrzymaj airodump (`Ctrl+C`). Masz plik `/tmp/demo-01.pcap`.

---

### Faza 3 (45 min) — Analiza Wireshark — TO jest serce prezentacji

Otwórz plik pcap w Wiresharku. Pokaż kolejno trzy rzeczy:

**1. Beacon frames — fingerprinting przez Information Elements:**
```
Filtr: wlan.fc.type_subtype == 8 && wlan.ssid == "AGH_WirelessLab"
```
Zobaczysz ramki z dwóch źródeł — oryginalny telefon i karta Kali. Kliknij na beacon z Kali → zakładka **Tagged parameters**. Porównaj z telefonem. Różnice:
- Inne **Supported Rates** (obsługiwane prędkości)
- Inny lub brakujący **Vendor Specific** tag (np. Apple/Samsung vs. Ralink)
- Różne **Capabilities** flags

👉 To jest twardy dowód fingerprinting. Zrób screenshot z zaznaczonymi różnicami.

**2. RSSI (Radiotap header) — anomalia sygnału:**
```
Filtr: wlan.fc.type_subtype == 8 && wlan.ssid == "AGH_WirelessLab"
```
Kliknij na dowolną ramkę → rozwiń **Radiotap Header** → `dBm Antenna Signal`. Porównaj wartości dla oryginalnego AP vs. evil twin. Karta USB trzymana blisko = dużo wyższy RSSI niż telefon w drugim kącie pokoju. Nienaturalny skok sygnału = red flag dla WIDS.

**3. Sequence Numbers — fingerprinting urządzenia:**
```
Filtr: wlan.fc.type_subtype == 8 && wlan.bssid == XX:XX:XX:XX:XX:XX
# Wstaw BSSID evil twin (MAC karty Kali)
```
W kolumnie `Seq` (dodaj ją przez **Edit → Preferences → Columns** albo po prostu kliknij na pakiet → `wlan.seq`): zobaczysz że numery sekwencyjne z dwóch urządzeń nadających ten sam BSSID "rozjeżdżają się" — bo dwa różne sprzętowe liczniki inkrementują niezależnie.

---

### Faza 4 (opcjonalna, 30 min) — Skrypt Python/Scapy = "efekt wow"

Jeśli zostanie czas, to **to** robi wrażenie na prowadzącym:

```python
from scapy.all import *
import matplotlib.pyplot as plt

pkts = rdpcap('/tmp/demo-01.pcap')

# WSTAW TUTAJ oba MAC adresy: oryginalny AP i evil twin
macs_of_interest = {
    "ORIGINAL_AP": "XX:XX:XX:XX:XX:XX",  # MAC telefonu (hotspot)
    "EVIL_TWIN":   "YY:YY:YY:YY:YY:YY",  # MAC karty Kali
}

results = {label: {"times": [], "seqs": []} for label in macs_of_interest}

for pkt in pkts:
    if pkt.haslayer(Dot11Beacon):
        src = pkt.addr3.lower() if pkt.addr3 else ""
        for label, mac in macs_of_interest.items():
            if src == mac.lower():
                results[label]["times"].append(float(pkt.time))
                results[label]["seqs"].append(pkt[Dot11].SC >> 4)

plt.figure(figsize=(14, 5))
for label, data in results.items():
    plt.plot(data["times"], data["seqs"], '.', label=label, markersize=3)

plt.xlabel("Czas [s]")
plt.ylabel("Sequence Number")
plt.title("AP Fingerprinting: Sequence Numbers — ten sam SSID, dwa urządzenia")
plt.legend()
plt.tight_layout()
plt.savefig("seq_fingerprint.png", dpi=150)
plt.show()
print("Saved: seq_fingerprint.png")
```

Wykres będzie wyglądał tak: dwie linie rosnące niezależnie dla tego samego BSSID. To jest wizualny dowód że nadają dwa różne urządzenia.

---

## Co pokazać na konsultacjach/prezentacji

Mapując na wasze sekcje z outline'u:

| Sekcja | Materiał dowodowy |
|---|---|
| **Sekcja 2** (mechanika ataku) | Screenshoty z Airgeddon: deauth packets, ofiara reconnecting, captive portal |
| **Sekcja 3a** (RSSI) | Wireshark: Radiotap dBm values, porównanie dwóch AP z tym samym SSID |
| **Sekcja 3b** (Beacon frames) | Wireshark: Tagged Parameters — różnice w Supported Rates i Vendor Specific |
| **Sekcja 3c** (Fingerprinting) | Wykres z Scapy — rozjeżdżające się Sequence Numbers |
| **Sekcja 4** (mitygacja) | Slajd/opis: WIDS, PMF 802.11w, EAP-TLS — to teoria, nie potrzeba dema |

---

## Ważne — TL-WDN3200 specyfika

RT5572 na Kali powinien działać out-of-the-box. Jeden potencjalny problem: jeśli Airgeddon chce użyć **VIF** (virtual interface — jedna karta robi jednocześnie monitor + AP), RT5572 może mieć z tym problem. Na to macie rozwiązanie gotowe: **dwie karty** — jedna w monitor, druga jako evil twin. Airgeddon powinien zapytać o interfejsy oddzielnie, po prostu przypisz każdej karty odpowiednią rolę gdy pyta.

---

Najkrócej: karta 1 → airodump zbiera pcap, karta 2 → Airgeddon robi evil twin. Pcap to wasz materiał badawczy. Wireshark + opcjonalnie scapy = gotowe demo dla wszystkich trzech metod detekcji z sekcji 3. Powodzenia, dasz radę.