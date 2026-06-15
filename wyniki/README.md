# Katalog na wyniki analizy

Ten katalog zawiera automatycznie wygenerowane wyniki z narzędzi projektu.

## Pliki generowane automatycznie

| Plik | Generowany przez | Zawartość |
|---|---|---|
| `evil_twin_analysis.json` | `analyze_pcap.py --json` | Wyniki analizy w formacie JSON |
| `evil_twin_analysis.csv` | `analyze_pcap.py --csv` | Wyniki analizy w formacie CSV |
| `evil_twin_analysis.png` | `analyze_pcap.py` | Wykres Sequence Numbers + RSSI |
| `beacon_diff.json` | `beacon_diff.py --json` | Szczegółowe porównanie IE |
| `beacon_diff.md` | `beacon_diff.py --markdown` | Raport porównania IE w Markdown |

## Jak używać

```bash
# Przejdź do katalogu projektu
cd BBSK-Evil-Twin

# Uruchom analizę z zapisem do tego katalogu
python3 skrypty/analyze_pcap.py /tmp/evil_twin_demo-01.pcap AGH_Test \
    --json --csv -o ./wyniki/

python3 skrypty/beacon_diff.py /tmp/evil_twin_demo-01.pcap AGH_Test \
    --json --markdown -o ./wyniki/

# Wygeneruj raport końcowy korzystając z wyników
python3 skrypty/generate_report.py \
    --analyze-json wyniki/evil_twin_analysis.json \
    --diff-json wyniki/beacon_diff.json \
    -o raport_koncowy.md
```

## Uwaga

Pliki w tym katalogu (oprócz `.gitkeep` i tego README) są w `.gitignore`
— nie są śledzone przez git. To celowe — wyniki mogą zawierać wrażliwe dane
(MAC adresy, SSIDy itp.).
