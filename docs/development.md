# Development Workflow

## Konfiguracja środowiska deweloperskiego

### Lokalne (na macOS/Linux)

```bash
# Sklonuj repozytorium
git clone <repo-url>
cd BBSK-Evil-Twin

# Utwórz środowisko wirtualne
python3 -m venv venv
source venv/bin/activate

# Zainstaluj zależności
pip install -r requirements.txt

# (Opcjonalnie) Zainstaluj zależności developerskie
pip install pytest black flake8
```

### Edytor (VS Code)

Rekomendowane rozszerzenia:

| Rozszerzenie | ID | Cel |
|---|---|---|
| Python | ms-python.python | Intellisense, debug |
| Pylance | ms-python.vscode-pylance | Type checking |
| Black Formatter | ms-python.black-formatter | Formatowanie |
| Python Docstring | njpwerner.autodocstring | Docstringi |

---

## Struktura kodu

```
skrypty/
├── analyze_pcap.py     # Główny skrypt analityczny

tests/
├── test_analyze_pcap.py # Testy jednostkowe
```

### Konwencje kodowania

| Aspekt | Reguła |
|---|---|
| **Język** | Polski (nazwy zmiennych/funkcji — angielski w kodzie, komentarze — polski) |
| **Formatowanie** | Black (linia: 100 znaków) |
| **Importy** | Stdlib → Scapy → matplotlib → własne |
| **Docstring** | Google style |
| **Type hints** | Tam, gdzie poprawiają czytelność (PEP 484) |
| **Nazwy funkcji** | `snake_case()` |
| **Nazwy stałych** | `UPPER_CASE` |

---

## Uruchamianie testów

```bash
# Aktywuj środowisko
source venv/bin/activate

# Uruchom wszystkie testy
python3 -m pytest tests/ -v

# Uruchom z pokryciem
python3 -m pytest tests/ --cov=skrypty -v

# Uruchom konkretny test
python3 -m pytest tests/test_analyze_pcap.py -v -k "test_nazwa"
```

---

## Linting i formatowanie

```bash
# Formatowanie Black
black skrypty/ tests/

# Sprawdzenie składni
python3 -m py_compile skrypty/analyze_pcap.py

# Flake8 (jeśli zainstalowany)
flake8 skrypty/
```

---

## Workflow zmian (Git)

### Branche

| Branch | Cel |
|---|---|
| `main` | Stabilna, przetestowana wersja |
| `feature/*` | Nowe funkcjonalności |
| `fix/*` | Poprawki błędów |
| `docs/*` | Zmiany w dokumentacji |

### Commit message

Format: `[polski]` lub `[english]` + krótki opis (≤ 50 znaków):

```
[docs] Dodaj threat model i security considerations
[feat] Rozszerz mapowanie OUI o 10 producentów
[fix] Obsłuż brak nagłówka RadioTap
[test] Dodaj test dla filtrowania po SSID
```

### Pull request checklist

Przed mergem do `main`:

- [ ] Testy przechodzą (`pytest tests/ -v`)
- [ ] Kod sformatowany (`black .`)
- [ ] Zmiany udokumentowane
- [ ] `analyze_pcap.py` działa na przykładowym pliku .pcap
- [ ] Brak tajnych danych w commitach (MAC adresy, hasła SSID)

---

## Dodawanie nowych metod detekcji

1. **Dodaj funkcję w `analyze_pcap.py`**
2. **Dodaj ekstrakcję danych w pętli głównej**
3. **Dodaj raportowanie w sekcji raportu**
4. **Dodaj wykres (jeśli dotyczy)**
5. **Dodaj test w `tests/test_analyze_pcap.py`**
6. **Zaktualizuj dokumentację w `docs/`**

---

## CI/CD (przyszłość)

Obecnie projekt nie ma skonfigurowanego CI/CD. Rekomendowana konfiguracja GitHub Actions:

```yaml
# .github/workflows/test.yml (do dodania)
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pip install pytest
      - run: python3 -m pytest tests/ -v
```
