# Use Cases

## UC-1: Badacz bezpieczeństwa analizuje podejrzaną sieć Wi-Fi

| Element | Opis |
|---|---|
| **Aktor** | Badacz bezpieczeństwa / administrator sieci |
| **Cel** | Zweryfikować, czy w okolicy działa Evil Twin podszywający się pod znaną sieć |
| **Warunek wstępny** | Plik .pcap z ramkami Beacon z podejrzanego obszaru |
| **Gwarancja sukcesu** | Raport z jednoznaczną oceną (Evil Twin / brak dowodów) |

**Scenariusz podstawowy:**

1. Badacz uruchamia `analyze_pcap.py` z plikiem .pcap
2. Skrypt wykrywa N urządzeń z tym samym SSID
3. Badacz sprawdza różnice w Supported Rates i Vendor Specific IE
4. Badacz analizuje wykres Sequence Numbers — rozwidlenie potwierdza atak
5. Badacz generuje raport i screenshoty jako materiał dowodowy

**Scenariusz alternatywny (brak skryptu):**
1. Badacz otwiera .pcap w Wireshark
2. Ustawia filtr: `wlan.fc.type_subtype == 8 && wlan.ssid == "SSID"`
3. Ręcznie porównuje Tagged Parameters między ramkami
4. Wyciąga wnioski na podstawie różnic

---

## UC-2: Student odtwarza scenariusz ataku w laboratorium

| Element | Opis |
|---|---|
| **Aktor** | Student |
| **Cel** | Przeprowadzić kontrolowany atak Evil Twin w celach edukacyjnych |
| **Warunek wstępny** | Sprzęt (2 karty Wi-Fi, 2 telefony), Kali VM |
| **Gwarancja sukcesu** | Przechwycony plik .pcap + udana detekcja |

**Scenariusz podstawowy:**

1. Student konfiguruje środowisko według [`setup.md`](setup.md)
2. Student uruchamia airodump-ng na karcie #1
3. Student uruchamia airgeddon na karcie #2 wybierając Evil Twin z captive portalem
4. Ofiara (telefon B) otrzymuje deauth i łączy się z Evil Twin
5. Ofiara wpisuje hasło na captivie portalu
6. Student zatrzymuje airodump i uruchamia `analyze_pcap.py`
7. Student analizuje wyniki i porównuje z obserwacjami z Wireshark

**Scenariusz rozszerzony (porównanie metod):**
1. Student powtarza atak zmieniając parametry (inny kanał, inne SSID)
2. Student testuje z włączonym/wyłączonym PMF (802.11w)
3. Student dokumentuje różnice w skuteczności detekcji

---

## UC-3: Audytor bezpieczeństwa sprawdza sieć firmową

| Element | Opis |
|---|---|
| **Aktor** | Audytor bezpieczeństwa (white hat) |
| **Cel** | Sprawdzić, czy w sieci firmowej są Rogue AP |
| **Warunek wstępny** | Zgoda pisemna od kierownictwa firmy |
| **Gwarancja sukcesu** | Raport z listą wszystkich AP i rekomendacjami |

**Scenariusz podstawowy:**

1. Audytor uzyskuje pisemną zgodę na testy (zakres, czas, metody)
2. Audytor przeprowadza skanowanie pasywne (monitor mode, bez aktywnych ataków)
3. Audytor zbiera ramki Beacon przez minimum 30 minut na każdym kanale
4. Audytor uruchamia `analyze_pcap.py` dla każdego SSID firmowego
5. Audytor identyfikuje AP z nienaturalnymi parametrami (niezgodne z polityką)
6. Audytor przygotowuje raport z rekomendacjami (PMF, WIDS, EAP-TLS)

**Ograniczenia:** Skrypt `analyze_pcap.py` analizuje tylko ramki Beacon — nie wykrywa Evil Twin, który emituje identyczne IE. Wymagana jest korelacja z innymi metodami.

---

## Macierz pokrycia use case

| Use Case | Wymagany sprzęt | Wymagany .pcap | Wymagany skrypt | Wymagana zgoda |
|---|---|---|---|---|
| UC-1 | Tylko PC z Wireshark | ✅ | Opcjonalnie | N/A (analiza offline) |
| UC-2 | 2× karty + 2× telefony + Kali VM | ❌ (generujemy) | ✅ | Laboratorium |
| UC-3 | Karta monitor + PC | ✅ | ✅ | ✅ Zgoda pisemna |
