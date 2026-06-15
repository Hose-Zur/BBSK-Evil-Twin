# Prezentacja — Evil Twin, KARMA, MANA: Ataki i Detekcja
## ~15 minut | 16 slajdów | AGH WIEiT

---

### Slajd 1: Tytułowy (0:30)
**Treść:** "Ataki Evil Twin, KARMA i MANA — analiza, detekcja i przeciwdziałanie"
**Autorzy, data, przedmiot**

> Mówca: "Dzień dobry. Przedstawimy wyniki projektu dotyczącego ataków typu Rogue Access Point..."

---

### Slajd 2: Agenda (0:30)
**Treść:** 
1. Czym są rogue AP
2. Trzy typy ataków: Evil Twin → KARMA → MANA
3. Metody detekcji (3 metody)
4. Eksperyment praktyczny (10 cykli)
5. Wnioski i mitygacja

---

### Slajd 3: Evil Twin — jak działa (1:00)
**Grafika:** Schemat: oryginalny AP + Evil Twin + klient
**Tekst:** Duplikat SSID, deauth, przejęcie klienta

> Mówca: "Evil Twin to najprostszy atak — klonujemy SSID i podszywamy się pod legalną sieć..."

---

### Slajd 4: KARMA — atak pasywny (1:00)
**Grafika:** Probe request → KARMA AP odpowiada beaconem
**Tekst:** Nasłuchuje probe requestów, odpowiada z żądanym SSID

> Mówca: "KARMA nie potrzebuje znać SSID — czeka aż klient sam zapyta..."

---

### Slajd 5: MANA — zaawansowany atak (1:00)
**Grafika:** Directed probe → MANA ignoruje BSSID, odpowiada
**Tekst:** Loud Mode, wiele SSID, EAP capture

> Mówca: "MANA to ewolucja KARMY — odpowiada nawet na szyfrowane zapytania..."

---

### Slajd 6: Porównanie 3 ataków (1:00)
**Tabela:** Evil Twin vs KARMA vs MANA
| | Deauth | Cel | Wykrywanie |
|---|---|---|---|
| Evil Twin | ✅ | 1 SSID | Duplikat BSSID |
| KARMA | ❌ | Wszystkie probe | 1 BSSID → wiele SSID |
| MANA | ❌ | Wszystkie + Loud | Loud beacony |

---

### Slajd 7: Środowisko laboratoryjne (0:30)
**Zdjęcia:** Kali VM, 2× TP-Link, telefon jako ofiara
**Tekst:** Sprzęt + oprogramowanie

---

### Slajd 8: Metoda 1 — Fingerprinting IE (1:00)
**Wykres:** Bar chart z prezentacji (oryginał vs Evil Twin)
**Tekst:** Information Elements jako odcisk palca sprzętu

> Mówca: "Każdy AP ma unikalne IE — jak odcisk palca. Porównujemy 6 kluczowych elementów..."

---

### Slajd 9: Metoda 2 — Analiza RSSI (0:45)
**Wykres:** Boxplot RSSI z prezentacji
**Tekst:** Δ = 20 dBm → anomalia

> Mówca: "Dwa AP z tym samym SSID nie powinny mieć aż 20 dBm różnicy..."

---

### Slajd 10: Metoda 3 — Sequence Numbers (1:00)
**Wykres:** Wykres Seq Numbers z górkami
**Tekst:** Dwa niezależne strumienie = dwa urządzenia

> Mówca: "Każda karta Wi-Fi ma 12-bitowy licznik. Dwa strumienie to twardy dowód..."

---

### Slajd 11: Eksperyment — 10 cykli (1:00)
**Wykres:** Pełny wykres 4-panelowy z eksperymentu
**Tekst:** 55k pakietów, 6.8k beaconów, 10 cykli ON/OFF

> Mówca: "Przeprowadziliśmy 10 cykli włącz/wyłącz AP. Wykres pokazuje..."

---

### Slajd 12: Wyniki MANA (1:00)
**Zrzut ekranu:** MANA przechwytujące probe requesty
**Tekst:** Directed probe requests iPhone'a przechwycone

> Mówca: "MANA przechwyciła directed probe requesty od iPhone'a..."

---

### Slajd 13: TLS SNI — podsłuchiwanie domen (0:45)
**Zrzut ekranu:** tcpdump z nazwami domen Apple
**Tekst:** Mimo szyfrowanego DNS, SNI zdradza odwiedzane strony

> Mówca: "Nawet przy DNS-over-HTTPS, nazwy domen są widoczne w TLS Client Hello..."

---

### Slajd 14: Łamanie WPA handshake (0:45)
**Zrzut ekranu:** hashcat z odzyskanym hasłem
**Tekst:** PMKID przechwycony, hasło złamane przez hashcat

---

### Slajd 15: Mitygacja i ochrona (1:00)
**Lista:**
- 802.11w (PMF) — blokuje deauth
- WIDS/WIPS — monitoruje duplikaty SSID
- EAP-TLS — certyfikaty dla AP
- VPN — szyfruje ruch nawet na rogue AP

---

### Slajd 16: Podsumowanie i pytania (0:30)
**Tekst:** 
- ✅ 3 typy ataków przeprowadzone i wykryte
- ✅ 3 metody detekcji zaimplementowane (analyze_pcap.py, beacon_diff.py)
- ✅ Narzędzia open-source na GitHub

> Mówca: "Dziękujemy za uwagę. Pytania?"
