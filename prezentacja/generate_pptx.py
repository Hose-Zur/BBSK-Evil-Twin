#!/usr/bin/env python3
"""Generuje prezentację BBSK-Evil-Twin w stylistyce AGH."""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
import os

COLS = {
    "agh_red": RGBColor(0xD4, 0x19, 0x20),
    "white": RGBColor(0xFF, 0xFF, 0xFF),
    "black": RGBColor(0x00, 0x00, 0x00),
    "dark": RGBColor(0x1A, 0x1A, 0x2E),
    "gray": RGBColor(0x66, 0x66, 0x66),
    "light": RGBColor(0xF5, 0xF5, 0xF5),
    "green": RGBColor(0x2A, 0x9D, 0x8F),
}

DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.join(DIR, "media")
WYNIKI = os.path.join(DIR, "..", "wyniki")

prs = Presentation()
prs.slide_width = Inches(13.33)
prs.slide_height = Inches(7.5)

def add_bg(slide, color=COLS["white"]):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_rect(slide, left, top, width, height, color=COLS["agh_red"]):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape

def add_text(slide, left, top, width, height, text, size=18, bold=False, color=COLS["black"], align=PP_ALIGN.LEFT, name="Calibri"):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.alignment = align
    return txBox

def add_img(slide, path, left, top, width=None, height=None):
    if os.path.exists(path):
        if width and height:
            return slide.shapes.add_picture(path, left, top, width, height)
        else:
            return slide.shapes.add_picture(path, left, top)
    return None

# ============================================================
# SLAJD 1: TYTUŁOWY
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, COLS["dark"])
add_rect(slide, Inches(0), Inches(2.5), Inches(13.33), Inches(3.5), COLS["agh_red"])
add_text(slide, Inches(1), Inches(2.7), Inches(11.33), Inches(1.5),
         "Ataki Evil Twin, KARMA i MANA", size=40, bold=True, color=COLS["white"], align=PP_ALIGN.CENTER)
add_text(slide, Inches(1), Inches(4.2), Inches(11.33), Inches(1),
         "Analiza, detekcja i przeciwdziałanie atakom Rogue Access Point", size=20, color=COLS["white"], align=PP_ALIGN.CENTER)
add_text(slide, Inches(1), Inches(6.2), Inches(11.33), Inches(1),
         "Bezpieczeństwo Sieci Bezprzewodowych  |  AGH WIEiT  |  2026", size=16, color=COLS["gray"], align=PP_ALIGN.CENTER)

# ============================================================
# SLAJD 2: AGENDA
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_rect(slide, Inches(0), Inches(0), Inches(13.33), Inches(0.8), COLS["agh_red"])
add_text(slide, Inches(0.5), Inches(0.1), Inches(12), Inches(0.6),
         "Agenda", size=28, bold=True, color=COLS["white"])

items = [
    ("Czym jest Rogue AP?", "Definicja, zagrożenia, schemat ataku"),
    ("Atak Evil Twin", "Klonowanie SSID, deauth, przejęcie klienta"),
    ("Atak KARMA", "Pasywne przechwytywanie probe requestów"),
    ("Atak MANA", "Zaawansowany atak (Loud Mode, directed probes)"),
    ("3 metody detekcji", "Fingerprinting IE, Analiza RSSI, Sequence Numbers"),
    ("Eksperyment praktyczny", "10 cykli ON/OFF – wyniki i wnioski"),
    ("WiFiSlayer – narzędzie pomocnicze", "Captive portal i automatyzacja"),
    ("Mitygacja i ochrona", "802.11w, WIDS, EAP-TLS, VPN"),
]
for i, (t, d) in enumerate(items):
    y = 1.2 + i * 0.72
    add_text(slide, Inches(0.8), Inches(y), Inches(6), Inches(0.4),
             f"{i+1}. {t}", size=18, bold=True)
    add_text(slide, Inches(2), Inches(y + 0.35), Inches(10), Inches(0.3),
             d, size=12, color=COLS["gray"])

# ============================================================
# SLAJD 3: CZYM JEST ROGUE AP?
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_rect(slide, Inches(0), Inches(0), Inches(13.33), Inches(0.8), COLS["agh_red"])
add_text(slide, Inches(0.5), Inches(0.1), Inches(12), Inches(0.6),
         "Czym jest Rogue Access Point?", size=28, bold=True, color=COLS["white"])

add_text(slide, Inches(0.8), Inches(1.2), Inches(11), Inches(0.5),
         "Nieautoryzowany punkt dostepowy podszywajacy sie pod legalna siec WiFi", size=16, bold=True)
add_text(slide, Inches(0.8), Inches(2), Inches(5.5), Inches(3),
         "Standard 802.11 nie weryfikuje tozsamosci AP.\n"
         "Klient nie widzi roznicy miedzy oryginalnym AP\n"
         "a Evil Twin. Atakujacy moze przechwycic haslo,\n"
         "ruch sieciowy i dane logowania.", size=14)

add_text(slide, Inches(7), Inches(1.8), Inches(5.5), Inches(3.5),
         "Rodzaje atakow:\n\n"
         "  Evil Twin - klonowanie konkretnego SSID\n"
         "  KARMA - odpowiedz na wszystkie probe requesty\n"
         "  MANA - directed probes + Loud Mode\n\n"
         "Metody detekcji:\n\n"
         "  IE Fingerprinting (15/18 roznic)\n"
         "  Analiza RSSI (delta 20 dBm)\n"
         "  Sequence Numbers (2 strumienie)", size=13)

# ============================================================
# SLAJD 4: EVIL TWIN
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_rect(slide, Inches(0), Inches(0), Inches(13.33), Inches(0.8), COLS["agh_red"])
add_text(slide, Inches(0.5), Inches(0.1), Inches(12), Inches(0.6),
         "Atak Evil Twin", size=28, bold=True, color=COLS["white"])

add_text(slide, Inches(0.8), Inches(1.2), Inches(6), Inches(4.5),
         "Mechanizm:\n\n"
         "1. Klonujemy konkretny SSID (np. 601A)\n"
         "2. Wysylamy ramki deauth do klientow\n"
         "3. Klient traci polaczenie z oryginalem\n"
         "4. Klient laczy sie z naszym AP\n"
         "5. Captive portal przechwytuje haslo\n\n"
         "Nasze wyniki:\n\n"
         "  Urzadzenie: TP-Link TL-WDN3200 (RT5572)\n"
         "  Ofiara: iPhone (BA:A1:0E:08:E0:35)\n"
         "  55.490 pakietow przechwyconych\n"
         "  6.810 beaconow (2928 Evil + 3882 oryginal)", size=13)

add_text(slide, Inches(7.5), Inches(1.2), Inches(5.5), Inches(5),
         "Roznice miedzy AP:\n\n"
         "  Oryginal: 7C:F1:7E:C1:7B:95\n"
         "  Evil Twin: 64:70:02:18:B9:22\n\n"
         "  Oryginal: RSSI -42.1 dBm (daleko)\n"
         "  Evil Twin: RSSI -22.8 dBm (blisko)\n\n"
         "  Delta RSSI: 20.3 dBm (anomalia!)\n\n"
         "  Oryginal: HT Capabilities TAK\n"
         "  Evil Twin: HT Capabilities NIE\n\n"
         "  Oryginal: Vendor: Microsoft WPS\n"
         "  Evil Twin: Vendor: brak (karta USB)", size=13)

# ============================================================
# SLAJD 5: KARMA
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_rect(slide, Inches(0), Inches(0), Inches(13.33), Inches(0.8), COLS["agh_red"])
add_text(slide, Inches(0.5), Inches(0.1), Inches(12), Inches(0.6),
         "Atak KARMA (Karma Attacks Radio Machines Automatically)", size=24, bold=True, color=COLS["white"])

add_text(slide, Inches(0.8), Inches(1.2), Inches(6), Inches(5),
         "Mechanizm:\n\n"
         "1. Rogue AP nasluchuje probe requestow\n"
         "2. Kazdy klient wysyla zapytania o znane sieci\n"
         "3. KARMA odpowiada beaconem z zadanym SSID\n"
         "4. Klient moze polaczyc sie automatycznie\n\n"
         "Roznica w stosunku do Evil Twin:\n\n"
         "  Evil Twin: wiele BSSID -> 1 SSID\n"
         "  KARMA: 1 BSSID -> wiele SSID\n\n"
         "Nasze wyniki:\n\n"
         "  hostapd-mana (enable_mana=0)\n"
         "  Przechwycone probe requesty iPhone'a:\n"
         "  Probe Request (601A), RSSI -34 dBm\n"
         "  iPhone aktywnie szuka sieci 601A", size=13)

add_rect(slide, Inches(7.5), Inches(1.5), Inches(5), Inches(4.5), COLS["light"])
add_text(slide, Inches(7.8), Inches(1.7), Inches(4.5), Inches(4),
         "Ograniczenia KARMY:\n\n"
         "  Nowe systemy (iOS 10+, Android 8+)\n"
         "  uzywaja pasywnego skanowania -\n"
         "  nie wysylaja probe requestow.\n\n"
         "  Directed probe requests -\n"
         "  klient szuka konkretnego BSSID,\n"
         "  nie broadcastu.\n\n"
         "  KARMA nie wymusza rozlaczenia -\n"
         "  klient sam decyduje czy sie polaczyc.", size=12)

# ============================================================
# SLAJD 6: MANA
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_rect(slide, Inches(0), Inches(0), Inches(13.33), Inches(0.8), COLS["agh_red"])
add_text(slide, Inches(0.5), Inches(0.1), Inches(12), Inches(0.6),
         "Atak MANA (SensePost, Defcon 22)", size=28, bold=True, color=COLS["white"])

add_text(slide, Inches(0.8), Inches(1.2), Inches(6), Inches(5),
         "Ulepszenia KARMY:\n\n"
         "- Odpowiada na directed probe requests\n"
         "  (ignoruje docelowy BSSID)\n\n"
         "- Loud Mode: emituje popularne SSID co ~10s\n\n"
         "- EAP Capture: przechwytuje handshake\n"
         "  dla sieci Enterprise (eduroam itp.)\n\n"
         "- Multiple BSSID: jeden interfejs,\n"
         "  wiele wirtualnych AP", size=14)

add_rect(slide, Inches(7.5), Inches(1.5), Inches(5), Inches(4.5), RGBColor(0xFF, 0xF0, 0xF0))
add_text(slide, Inches(7.8), Inches(1.7), Inches(4.5), Inches(4),
         "Nasze wyniki:\n\n"
         "  hostapd-mana (enable_mana=1)\n\n"
         "  MANA przechwycil directed probe\n"
         "  requesty iPhone'a:\n\n"
         "  \"MANA - Directed probe request\n"
         "   for SSID 601A from ba:a1:...\"\n\n"
         "UWAGA:\n"
         "  MANA nie wymusza rozlaczenia.\n"
         "  To atak pasywny - czeka az\n"
         "  klient sam przejdzie do naszego AP.\n"
         "  Captive Portal iOS nas zablokowal.", size=12, color=COLS["agh_red"])

# ============================================================
# SLAJD 7: 3 METODY DETEKCJI
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_rect(slide, Inches(0), Inches(0), Inches(13.33), Inches(0.8), COLS["agh_red"])
add_text(slide, Inches(0.5), Inches(0.1), Inches(12), Inches(0.6),
         "Trzy metody detekcji Evil Twin", size=28, bold=True, color=COLS["white"])

add_text(slide, Inches(0.5), Inches(1.2), Inches(4), Inches(2),
         "1. Fingerprinting IE\n\n"
         "Porownanie Information Elements\n"
         "w ramkach Beacon:\n"
         "- HT Capabilities\n"
         "- Vendor Specific (OUI)\n"
         "- Power Constraint\n"
         "- Extended Capabilities", size=13)
add_text(slide, Inches(4.7), Inches(1.2), Inches(4), Inches(2),
         "2. Analiza RSSI\n\n"
         "Porownanie poziomu sygnalu:\n"
         "- Evil Twin: -22.8 dBm\n"
         "- Oryginal: -42.1 dBm\n"
         "- Delta: 20.3 dBm (anomalia)", size=13)
add_text(slide, Inches(8.9), Inches(1.2), Inches(4), Inches(2),
         "3. Sequence Numbers\n\n"
         "Dwa niezalezne strumienie:\n"
         "- Oryginal: 0-4095\n"
         "- Evil Twin: 0-2045\n"
         "- Brak nakladania sie zakresow", size=13)

add_text(slide, Inches(0.5), Inches(4.2), Inches(12.33), Inches(2.8),
         "Wszystkie trzy metody lacznie daja 100% pewnosc wykrycia Evil Twin.\n"
         "Zadna z metod pojedynczo nie wystarczy, ale kombinacja wszystkich trzech\n"
         "stanowi niepodwazalny dowod na obecnosc nieautoryzowanego AP.", size=14, color=COLS["gray"])

# ============================================================
# SLAJD 8: METODA 1 - IE FINGERPRINTING (wykres)
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_rect(slide, Inches(0), Inches(0), Inches(13.33), Inches(0.8), COLS["agh_red"])
add_text(slide, Inches(0.5), Inches(0.1), Inches(12), Inches(0.6),
         "Metoda 1: Fingerprinting IE - roznice sprzetowe", size=28, bold=True, color=COLS["white"])

# Wklej wykres (jeśli istnieje) - wycinamy tylko gorny-prawy panel (IE bar chart) z zupelnego wykresu
img_path = os.path.join(WYNIKI, "experiment", "evil_twin_analysis.png")
if os.path.exists(img_path):
    add_img(slide, img_path, Inches(0.5), Inches(1), Inches(8), Inches(5.5))

add_text(slide, Inches(9), Inches(1.2), Inches(4), Inches(5.5),
         "Co widac na wykresie:\n\n"
         "Oryginalny AP (czerwone slupki)\n"
         "ma WSZYSTKIE zaawansowane\n"
         "funkcje:\n"
         "- Szybkie WiFi 802.11n\n"
         "- Producent (Microsoft WPS)\n"
         "- Ograniczenie mocy\n"
         "- Szeroki kanal 40MHz\n\n"
         "Nasz Evil Twin (zielone slupki)\n"
         "nie ma NICZEGO - to prosta\n"
         "karta USB Ralink RT5572.\n\n"
         "Wynik: 15/18 IE rozniacych sie\n"
         "certyfikat sprzetowej roznicy!", size=13)

# ============================================================
# SLAJD 9: METODA 2 - RSSI
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_rect(slide, Inches(0), Inches(0), Inches(13.33), Inches(0.8), COLS["agh_red"])
add_text(slide, Inches(0.5), Inches(0.1), Inches(12), Inches(0.6),
         "Metoda 2: Analiza RSSI - anomalia sygnalu", size=28, bold=True, color=COLS["white"])

add_text(slide, Inches(0.8), Inches(1.2), Inches(6), Inches(5),
         "Wyniki pomiarow RSSI:\n\n"
         "  Oryginalny AP (7C:F1:7E:C1:7B:95)\n"
         "  Srednia: -42.1 dBm (odlegly router)\n\n"
         "  Evil Twin AP (64:70:02:18:B9:22)\n"
         "  Srednia: -22.8 dBm (karta obok)\n\n"
         "  Delta: 20.3 dBm\n\n"
         "Interpretacja:\n\n"
         "Dwa AP z tym samym SSID nie powinny\n"
         "miec tak roznego sygnalu. Roznica\n"
         "20 dBm oznacza, ze jeden AP jest\n"
         "ok. 10 razy blizej niz drugi.\n\n"
         "To klasyczna anomalia dla ataku\n"
         "Evil Twin - atakujacy umieszcza\n"
         "karte blisko ofiary.", size=14)

add_rect(slide, Inches(7.5), Inches(1.5), Inches(5), Inches(4.5), COLS["light"])
add_text(slide, Inches(7.8), Inches(1.7), Inches(4.5), Inches(4),
         "Jak to wykorzystac w detekcji?\n\n"
         "Regularnie monitoruj RSSI wszystkich\n"
         "AP z tym samym SSID. Jesli zauwazysz\n"
         "nagle pojawienie sie drugiego AP\n"
         "z roznica sygnalu >10 dBm - alarm!\n\n"
         "Ograniczenie:\n"
         "Doswiadczony atakujacy moze\n"
         "dostosowac moc nadawania.\n\n"
         "Zaleta:\n"
         "Nie wymaga dodatkowego sprzetu -\n"
         "wystarczy karta w trybie monitor.", size=12)

# ============================================================
# SLAJD 10: METODA 3 - SEQUENCE NUMBERS
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_rect(slide, Inches(0), Inches(0), Inches(13.33), Inches(0.8), COLS["agh_red"])
add_text(slide, Inches(0.5), Inches(0.1), Inches(12), Inches(0.6),
         "Metoda 3: Sequence Numbers - dwa niezalezne strumienie", size=24, bold=True, color=COLS["white"])

add_text(slide, Inches(0.8), Inches(1.2), Inches(6), Inches(5.5),
         "Jak to dziala:\n\n"
         "Kazda karta Wi-Fi ma 12-bitowy\n"
         "sprzetowy licznik ramek (0-4095).\n\n"
         "Jesli dwa AP nadaja ten sam SSID,\n"
         "kazdy ma wlasny niezalezny licznik.\n\n"
         "Na wykresie widac DWA strumienie\n"
         "numerow sekwencyjnych - to dowod\n"
         "ze nadaja dwa rozne urzadzenia.\n\n"
         "Wyniki z eksperymentu:\n\n"
         "  Oryginal: seq 0 - 4095 (pelny cykl)\n"
         "  Evil Twin: seq 0 - 2045\n"
         "  Brak nakladania sie zakresow\n\n"
         "Zaleta: licznik jest w hardware -\n"
         "nie da sie zmanipulowac.", size=13)

img_path2 = os.path.join(WYNIKI, "experiment", "evil_twin_analysis.png")
if os.path.exists(img_path2):
    add_img(slide, img_path2, Inches(7), Inches(1.2), Inches(5.5), Inches(5))

# ============================================================
# SLAJD 11: EKSPERYMENT 10 CYKLI
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_rect(slide, Inches(0), Inches(0), Inches(13.33), Inches(0.8), COLS["agh_red"])
add_text(slide, Inches(0.5), Inches(0.1), Inches(12), Inches(0.6),
         "Eksperyment: 10 cykli ON/OFF Evil Twin", size=28, bold=True, color=COLS["white"])

add_text(slide, Inches(0.8), Inches(1.2), Inches(6), Inches(5.5),
         "Przebieg eksperymentu:\n\n"
         "1. iPhone na Evil Twin AP\n"
         "2. Wylaczenie AP (pkill hostapd)\n"
         "3. iPhone traci polaczenie (~5s)\n"
         "4. Wlaczenie AP (create_ap)\n"
         "5. iPhone reconnectuje (~6s)\n"
         "6. Powtorzono 10 razy\n\n"
         "Wyniki:\n\n"
         "  Pakiety: 55 490\n"
         "  Beacony: 6 810\n"
         "  Sukces reconnectu: 10/10 (100%)\n"
         "  Sredni czas: ~6s\n\n"
         "Wykres Seq Numbers pokazuje\n"
         "wyraznie 10 cykli - \"gorzki\"\n"
         "widoczne na zielonej linii.", size=14)

add_rect(slide, Inches(7.5), Inches(1.5), Inches(5), Inches(4.5), COLS["light"])
add_text(slide, Inches(7.8), Inches(1.7), Inches(4.5), Inches(4),
         "Co udowodnilismy:\n\n"
         "1. Evil Twin moze byc skutecznie\n"
         "   uzywany do przejmowania klientow\n\n"
         "2. iPhone przechodzi miedzy AP\n"
         "   automatycznie - bez interwencji\n"
         "   uzytkownika\n\n"
         "3. Czas reconnectu to ~6s -\n"
         "   wystarczajaco szybko zeby\n"
         "   uzytkownik nie zauwazyl\n\n"
         "4. Sequence Numbers jednoznacznie\n"
         "   potwierdzaja 2 urzadzenia", size=12)

# ============================================================
# SLAJD 12: POROWNANIE METOD ATAKU
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_rect(slide, Inches(0), Inches(0), Inches(13.33), Inches(0.8), COLS["agh_red"])
add_text(slide, Inches(0.5), Inches(0.1), Inches(12), Inches(0.6),
         "Porownanie trzech typow atakow", size=28, bold=True, color=COLS["white"])

add_text(slide, Inches(0.8), Inches(1.2), Inches(11.5), Inches(5.5),
         "  Cecha                      | Evil Twin            | KARMA                 | MANA\n\n"
         "  Mechanizm                 | Klonowanie SSID      | Odpowiada na          | Directed probes\n"
         "                            | + deauth             | probe requesty        | + Loud Mode\n\n"
         "  Wymusza rozlaczenie?      | TAK (deauth)         | NIE                   | NIE\n\n"
         "  Zna SSID ofiary?          | TAK                  | NIE                   | NIE\n\n"
         "  BSSID vs SSID             | Wiele -> 1 SSID      | 1 BSSID -> wiele      | 1 BSSID -> wiele\n\n"
         "  Skutecznosc               | WYSOKA               | SREDNIA               | BARDZO WYSOKA\n\n"
         "  Wykrywanie                | Duplikat SSID        | Anomalia 1 BSSID      | Loud beacony\n"
         "                            |                      | wiele SSID            |\n\n"
         "  Ochrona przed atakiem     | 802.11w (PMF)        | Pasywne skanowanie    | WIDS/WIPS\n"
         "                            |                      | iOS/Android            |",
         size=13)

# ============================================================
# SLAJD 13: WIFISLAYER
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_rect(slide, Inches(0), Inches(0), Inches(13.33), Inches(0.8), COLS["agh_red"])
add_text(slide, Inches(0.5), Inches(0.1), Inches(12), Inches(0.6),
         "WiFiSlayer - narzedzie pomocnicze", size=28, bold=True, color=COLS["white"])

add_text(slide, Inches(0.8), Inches(1.2), Inches(5.5), Inches(5.5),
         "Co to jest?\n\n"
         "WiFiSlayer (github.com/waheeb71/WiFiSlayer)\n"
         "to framework do audytu sieci WiFi.\n\n"
         "Funkcjonalnosci:\n"
         "- Evil Twin z captive portalem\n"
         "- WPA/WPA2 Handshake capture\n"
         "- PMKID attack (bez klienta)\n"
         "- Deauth flooding\n"
         "- Beacon flooding\n"
         "- WPS exploitation\n"
         "- Auto-Pwn (wszystko automatycznie)\n"
         "- MAC spoofing\n\n"
         "Licencja: open source", size=13)

add_rect(slide, Inches(7), Inches(1.5), Inches(5.5), Inches(5), COLS["light"])
add_text(slide, Inches(7.3), Inches(1.7), Inches(5), Inches(4.5),
         "Nasze doswiadczenia:\n\n"
         "WiFiSlayer Captive Portal:\n"
         "- Uruchomiony na naszym Evil Twin AP\n"
         "- DNS redirect (#/192.168.200.1)\n"
         "- Strona \"Router Firmware Update\"\n"
         "- Przechwycone haslo: mama1234\n\n"
         "Screenshot strony logowania\n"
         "znajduje sie w folderze media/.\n\n"
         "WiFiSlayer potwierdza, ze zewnetrzne\n"
         "narzedzia moga byc uzywane do atakow\n"
         "Evil Twin - nasze wlasne skrypty\n"
         "sluza do DETEKCJI (analyze_pcap.py,\n"
         "beacon_diff.py).", size=12)

# ============================================================
# SLAJD 14: MITYGACJA
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_rect(slide, Inches(0), Inches(0), Inches(13.33), Inches(0.8), COLS["agh_red"])
add_text(slide, Inches(0.5), Inches(0.1), Inches(12), Inches(0.6),
         "Mitygacja - jak sie chronic?", size=28, bold=True, color=COLS["white"])

add_text(slide, Inches(0.8), Inches(1.2), Inches(5.5), Inches(5.5),
         "Dla administratorow sieci:\n\n"
         "  802.11w (PMF) - Protected Management\n"
         "  Frames - szyfruje ramki zarzadzania,\n"
         "  blokuje ataki deauth.\n\n"
         "  WIDS/WIPS - systemy detekcji\n"
         "  monitorujace duplikaty SSID\n"
         "  i anomalie RSSI.\n\n"
         "  EAP-TLS - certyfikaty dla AP -\n"
         "  klient weryfikuje tozsamosc AP.\n\n"
         "  Regularne skanowanie eteru\n"
         "  w poszukiwaniu nieznanych AP.", size=14)

add_text(slide, Inches(7), Inches(1.2), Inches(5.5), Inches(5.5),
         "Dla uzytkownikow:\n\n"
         "  VPN - szyfruje caly ruch,\n"
         "  nawet na rogue AP dane sa\n"
         "  bezpieczne.\n\n"
         "  Unikanie otwartych, nieznanych\n"
         "  sieci WiFi.\n\n"
         "  Sprawdzanie certyfikatow HTTPS\n"
         "  (zielona klodka).\n\n"
         "  Wylaczenie auto-join dla\n"
         "  zapisanych sieci.\n\n"
         "  Uzywanie DNS-over-HTTPS\n"
         "  (chroni przed podslychem DNS).", size=14)

# ============================================================
# SLAJD 15: PODSUMOWANIE
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, COLS["dark"])
add_rect(slide, Inches(0), Inches(2.8), Inches(13.33), Inches(3), COLS["agh_red"])
add_text(slide, Inches(0.5), Inches(0.2), Inches(12), Inches(0.6),
         "Podsumowanie", size=28, bold=True, color=COLS["white"])

add_text(slide, Inches(0.5), Inches(1), Inches(3.5), Inches(1.5),
         "Przeprowadzone ataki\n\n3 typy\nEvil Twin, KARMA, MANA", size=16, color=COLS["white"])
add_text(slide, Inches(4.7), Inches(1), Inches(3.5), Inches(1.5),
         "Metody detekcji\n\n3 metody\nIE + RSSI + Seq Numbers", size=16, color=COLS["white"])
add_text(slide, Inches(8.9), Inches(1), Inches(3.5), Inches(1.5),
         "Dane eksperymentalne\n\n55k+ pakietow\n10 cykli ON/OFF", size=16, color=COLS["white"])

add_text(slide, Inches(0.5), Inches(6), Inches(12), Inches(1),
         "Narzedzia open source: analyze_pcap.py  |  beacon_diff.py  |  github.com/Hose-Zur/BBSK-Evil-Twin",
         size=14, color=COLS["gray"], align=PP_ALIGN.CENTER)

# ============================================================
# SLAJD 16: DZIEKUJE
# ============================================================
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, COLS["dark"])
add_text(slide, Inches(1), Inches(2), Inches(11.33), Inches(1.5),
         "Dziekujemy za uwage!", size=40, bold=True, color=COLS["white"], align=PP_ALIGN.CENTER)
add_text(slide, Inches(1), Inches(4), Inches(11.33), Inches(1),
         "Pytania?", size=24, color=COLS["gray"], align=PP_ALIGN.CENTER)
add_text(slide, Inches(1), Inches(5.5), Inches(11.33), Inches(1),
         "github.com/Hose-Zur/BBSK-Evil-Twin", size=16, color=COLS["gray"], align=PP_ALIGN.CENTER)

# ============================================================
# ZAPIS
# ============================================================
output = os.path.join(DIR, "..", "wyniki", "prezentacja_agh.pptx")
prs.save(output)
print(f"Prezentacja zapisana: {output}")
print(f"Liczba slajdow: {len(prs.slides)}")
