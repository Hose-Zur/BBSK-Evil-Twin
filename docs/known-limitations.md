# Znane ograniczenia projektu

## Ograniczenia skryptu analyze_pcap.py

### 1. Tylko ramki Beacon

Skrypt analizuje wyłącznie ramki Beacon (subtype 8). Nie analizuje:

- Probe Requests / Probe Responses (potencjalne źródło fingerprintingu)
- Association / Authentication frames
- Data frames
- Action frames

**Wpływ:** Nie można wykryć Evil Twin, który nie emituje Beacon (rzadkie, ale możliwe w zaawansowanych atakach).

### 2. Ograniczona mapa OUI

Twardo zakodowana mapa OUI w liniach 94-102 zawiera tylko ~7 producentów:

```python
known = {
    "0050F2": "Microsoft/WPS",
    "00904C": "Epigram",
    "001018": "Broadcom",
    "000C03": "Apple",
    "00037F": "Atheros",
    "0017F2": "Apple",
    "00037F": "Atheros/Qualcomm",
}
```

**Wpływ:** Nowi producenci wyświetlani jako `OUI:XXXXXXXX` — konieczna ręczna identyfikacja.

**Obejście:** Rozszerzyć słownik o brakujące OUI przed uruchomieniem na docelowej sieci.

### 3. Brak obsługi 5 GHz i WiFi 6/6E (802.11ax/be)

Skrypt i procedura laboratoryjna są zaprojektowane dla pasma 2.4 GHz. Nie testowano:

- 5 GHz (kanały 36-165)
- WiFi 6 (802.11ax) — zmodyfikowana struktura IE
- WiFi 7 (802.11be) — nowe pola

**Wpływ:** Niekompatybilność z nowszymi standardami.

### 4. Brak obsługi PMF (802.11w)

Skrypt nie wykrywa obecności ani braku Protected Management Frames. Ramki Beacon z PMF mają flagę w Capabilities, ale skrypt jej nie ekstrahuje.

**Wpływ:** Nie można stwierdzić, czy atak byłby możliwy przy włączonym PMF.

### 5. Single-thread

Skrypt działa sekwencyjnie. Duże pliki .pcap (>500 MB) mogą być przetwarzane wolno.

### 6. Brak detekcji BSSID spoofingu

Skrypt identyfikuje AP po BSSID (MAC adresie). Zaawansowany atakujący może spoofować BSSID oryginalnego AP. W takim przypadku Sequence Number analysis nie zadziała (jeden strumień seq dla dwóch urządzeń).

**Wpływ:** Fałszywie negatywny wynik.

**Obejście:** Wykrywanie na podstawie różnych IE (Supported Rates, Vendor Specific) wciąż działa.

---

## Ograniczenia metody laboratoryjnej

### 7. Tylko WPA2-Personal

Procedura laboratoryjna korzysta z WPA2-Personal. W środowisku korporacyjnym z WPA2-Enterprise / EAP-TLS atak Evil Twin jest znacznie trudniejszy (wymagany fałszywy RADIUS).

### 8. Fizyczne rozmieszczenie

Analiza RSSI jest wrażliwa na fizyczne rozmieszczenie urządzeń:
- Telefon A zbyt blisko karty atakującego → podobny RSSI, utrudniona detekcja
- Ruch osoby między urządzeniami → tłumienie sygnału, artefakty na wykresie

### 9. Brak automatyzacji

Przygotowanie środowiska i wykonanie ataku wymaga ręcznego wykonania ~15 kroków. Proces nie jest zautomatyzowany (brak skryptu "one-click attack").

---

## Ograniczenia dokumentacji

### 10. DOCX jako główny dokument

Opracowanie wstępne jest w formacie `.docx` — binarnym, nieczytelnym dla `git diff`, `grep` i narzędzi CI/CD.

**Obejście:** Używać Markdown jako formatu podstawowego, a .docx tylko do dystrybucji (generowany z .md przez pandoc).

### 11. Brak obrazów/zdjęć

Dokumentacja nie zawiera zdjęć rzeczywistego setupu laboratoryjnego, screenshotów Wireshark ani przykładowych wykresów. Po przeprowadzeniu sesji praktycznej należy uzupełnić.

---

## Planowane ulepszenia (do rozważenia)

| Ulepszenie | Priorytet | Nakład pracy |
|---|---|---|
| Dynamiczna mapa OUI (JSON/csv) | Wysoki | 2 godz. |
| Analiza PMF (802.11w) | Średni | 3 godz. |
| Wsparcie dla 5 GHz | Średni | 4 godz. |
| Detekcja BSSID spoofingu (korelacja seq + IE) | Wysoki | 8 godz. |
| Automatyzacja ataku (skrypt bash) | Niski | 2 godz. |
| Generowanie DOCX z Markdown przez pandoc | Niski | 1 godz. |
| GitHub Actions CI | Niski | 2 godz. |
