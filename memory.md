# Project Memory Log

## 2026-06-15 17:12–18:16 - Kompletny redesign + poprawki v1–v7
- *Status*: ✅ Gotowe

## 2026-06-15 18:25 - Poprawka v9: Pre-renderowanie Mermaid do natywnego SVG
- *Prompt*: Mermaid wcześniej wyglądał genialnie, czy da się go przywrócić? (slajd KARMA zepsuty)
- *Przyczyna*: Playwright renderując PDF w Slidev nagminnie ucina bloki Mermaid, ignorując flagę `--wait`
- *Akcja*: 
  1. Napisano skrypt `download_svgs.py` generujący natywne wektory SVG bezpośrednio z silnika mermaid.ink (w trybie dark)
  2. Pobrane SVG zapisano do katalogu `public/diag1.svg`, `diag2.svg`, `diag3.svg`
  3. W `slides.md` zastąpiono bloki ```mermaid``` tagami `<img src="/diagX.svg">`
- *Efekt*: 100% genialny wygląd Mermaid + 100% niezawodny eksport PDF z Playwright (Slidev ładuje SVG jak zwykłe obrazki)
- *Status*: ✅ Gotowe
