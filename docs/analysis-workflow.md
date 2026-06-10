# Workflow analizy pcap

Ten dokument opisuje szczegółową procedurę analizy pliku `.pcap` w celu wykrycia ataku Evil Twin, z wykorzystaniem Wireshark i `analyze_pcap.py`.

---

## 1. Analiza automatyczna (analyze_pcap.py)

### Uruchomienie

```bash
python3 skrypty/analyze_pcap.py <ścieżka/do/pliku.pcap> [SSID]
```

### Co robi skrypt

| Krok | Opis |
|---|---|
| 1. Wczytanie | `rdpcap()` — załadowanie pliku .pcap |
| 2. Filtrowanie | Tylko ramki Beacon (Dot11 subtype 8) |
| 3. Ekstrakcja | SSID, Supported Rates, Vendor Specific IE |
| 4. Odczyt | Sequence Number (SC >> 4), RSSI z RadioTap |
| 5. Raport | Tabela AP z metrykami |
| 6. Wykres | Seq num + RSSI w czasie, zapis do .png |

### Interpretacja wyników

**Sygnały ostrzegawcze:**

| Wskaźnik | Interpretacja |
|---|---|
| `[!] UWAGA: N urządzeń nadaje z SSID='...'` | Potencjalny Evil Twin — N ≥ 2 |
| Różne Supported Rates dla tego samego SSID | Różne urządzenia (różni producenci) |
| Różne Vendor Specific OUI | Różni producenci sprzętu |
| Rozwidlenie na wykresie Sequence Numbers | Dwa niezależne liczniki sprzętowe |

---

## 2. Analiza ręczna (Wireshark)

### 2.1 Otwórz plik w Wireshark

```bash
wireshark /tmp/evil_twin_demo-01.pcap
```

### 2.2 Filtr dla ramek Beacon

```
wlan.fc.type_subtype == 8 && wlan.ssid == "AGH_Test"
```

### 2.3 Metoda 1: Fingerprinting IE

1. Kliknij na dowolną ramkę Beacon z oryginalnego AP (telefon)
2. Rozwiń **IEEE 802.11 Beacon frame → Tagged parameters**
3. Zanotuj wartości:

| Pole | AP #1 (telefon) | AP #2 (Evil Twin) | Wniosek |
|---|---|---|---|
| Supported Rates (tag 1) | 6, 12, 24, 36 | 6, 12, 24, 36, 48, 54 | Różne → różne urządzenia |
| Extended Supported Rates (tag 50) | 48, 54 | — | Różne → różne urządzenia |
| Vendor Specific (tag 221) | OUI: 00:0C:03 (Apple) | OUI: 00:03:7F (Atheros) | Inny producent = dowód |
| HT Capabilities (tag 45) | Obecne/brak | Brak/obecne | Różna konfiguracja |

4. Powtórz dla ramki z Evil Twin (drugi BSSID)
5. Zrób **screenshot** z zakładką Tagged parameters dla obu ramek

### 2.4 Metoda 2: Analiza RSSI

1. Wróć do listy pakietów
2. Kliknij na ramkę → rozwiń **Radiotap Header → dBm Antenna Signal**
3. Porównaj wartości RSSI dla ramek z obu BSSID:

| BSSID | RSSI zakres | Średnia | Uwagi |
|---|---|---|---|
| Telefon A (oryginalny) | -35 do -50 dBm | ~-42 dBm | Telefon w pewnej odległości |
| Evil Twin | -25 do -30 dBm | ~-28 dBm | Karta USB blisko |

**Jeśli różnica średnich RSSI > 15 dBm** — nienaturalne, wskazuje na Evil Twin (karta atakującego celowo blisko ofiary).

### 2.5 Metoda 3: Sequence Number analysis

1. Dodaj kolumnę Sequence Number w Wireshark:
   - **Edit → Preferences → Appearance → Columns**
   - Dodaj: `wlan.seq` z tytułem "Seq"
2. Posortuj ramki dla każdego BSSID
3. Zaobserwuj:

- Ramki z BSSID telefonu A: Sequence Numbers rosną od wartości X
- Ramki z BSSID Evil Twin: Sequence Numbers rosną od wartości Y (innej)

**Dwa niezależne strumienie Sequence Numbers** = dwa fizyczne urządzenia nadające z tym samym SSID = Evil Twin.

---

## 3. Synteza wyników

### Matryca decyzyjna

| Metoda | Wynik | Wnioskowanie |
|---|---|---|
| IE fingerprinting | Różne Supported Rates / Vendor Specific | ★★★ Prawie pewny Evil Twin |
| IE fingerprinting | Identyczne IE | Brak przesłanek (mogą być takie same urządzenia) |
| RSSI | Δ średniej > 15 dBm | ★★ Prawdopodobny Evil Twin (podatne na manipulację) |
| RSSI | Δ średniej < 5 dBm | Brak przesłanek |
| Seq numbers | Rozwidlenie na wykresie | ★★★ Pewny Evil Twin (twardy dowód) |
| Seq numbers | Pojedynczy strumień | Brak przesłanek |

### Ostateczna ocena

| Warunek | Werdykt |
|---|---|
| 3/3 metody wskazują | **Evil Twin potwierdzony** |
| 2/3 metody wskazują | **Wysoce prawdopodobny Evil Twin** |
| 1/3 metoda wskazuje | **Podejrzenie — wymaga potwierdzenia** |
| 0/3 metod wskazuje | **Brak dowodów na atak** |

---

## 4. Generowanie dowodów

Dla każdej metody wygeneruj materiał dowodowy do raportu końcowego:

| Metoda | Materiał dowodowy | Narzędzie |
|---|---|---|
| IE fingerprinting | Screenshot Tagged parameters × 2 AP | Wireshark |
| RSSI | Screenshot Radiotap header × kilka ramek | Wireshark |
| Seq numbers | Wykres seq w czasie | `analyze_pcap.py` |
| Captive portal | Screenshot strony logowania | Telefon B / airgeddon |
| Atak | Screenshot airgeddon z przechwyconym hasłem | Terminal |
