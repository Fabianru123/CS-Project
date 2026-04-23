"""
pages/lernplan.py – Lernplan-Seite der PredictEd App
Aufbau:
  Tab 1 – Prüfungen:   Prüfungen eintragen und verwalten
  Tab 2 – Woche:       Feste Blöcke pro Tag (Vorlesung, Sport, …) + globale Einstellungen
  Tab 3 – Kalender:    Visueller 7-Tage-Stundenplan mit Pomodoro-Lernblöcken
"""

import streamlit as st
from datetime import date, timedelta

from database import pruefung_eintragen, alle_pruefungen_laden, pruefung_loeschen

# ──────────────────────────────────────────────
# Seiten-Konfiguration
# ──────────────────────────────────────────────
st.set_page_config(page_title="Lernplan – PredictEd", page_icon="📅", layout="wide")

st.markdown("""
<style>
    h1,h2,h3 { color:#2ecc71 !important; }
    .stButton>button[kind="primary"] {
        background-color:#2ecc71; color:#0e1117; border:none; font-weight:bold;
    }
    .stButton>button[kind="primary"]:hover { background-color:#27ae60; }
    .stTabs [data-baseweb="tab-highlight"] { background-color:#2ecc71 !important; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Konstanten
# ──────────────────────────────────────────────

WOCHENTAGE = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"]

# Nutzer-wählbare Blocktypen (Lernblöcke werden automatisch generiert)
BLOCK_TYPEN = ["Vorlesung", "Sport", "Nachhilfe", "Privat", "Frei"]

# Farben für feste Aktivitätstypen: (Hintergrund, Randfarbe, Textfarbe, Emoji)
# Vollständig deckende Farben auf hellem Kalender-Hintergrund.
AKTIVITAET_FARBEN: dict[str, tuple] = {
    "Vorlesung": ("#1565C0", "#0D47A1", "#ffffff", "🎓"),  # kräftiges Königsblau
    "Sport":     ("#BF360C", "#8D2509", "#ffffff", "🏃"),  # Terrakotta/Backsteinrot
    "Nachhilfe": ("#E65100", "#BF360C", "#ffffff", "👨‍🏫"),  # tiefes Orange
    "Privat":    ("#546E7A", "#37474F", "#ffffff", "🔒"),  # Blaugrau
    "Frei":      ("#AD1457", "#880E4F", "#ffffff", "🌙"),  # Karmesinpink
    "Pendeln":   ("#00695C", "#004D40", "#ffffff", "🚇"),  # dunkles Türkis
    "Pause":     ("#F9A825", "#F57F17", "#333333", "☕"),  # Goldgelb (dunkler Text)
}

# Farbpalette für Lernblöcke – je Fach eine eigene, klar unterscheidbare Farbe.
# Bewusst KEINE Blautöne (Vorlesung) oder Rot/Orange (Sport/Nachhilfe).
# (bg, rand, text)
FACH_PALETTE = [
    ("#2E7D32", "#1B5E20", "#ffffff"),  # Waldgrün
    ("#7B1FA2", "#4A148C", "#ffffff"),  # Tiefviolett
    ("#00838F", "#006064", "#ffffff"),  # Cyan-Blaugrün
    ("#6D4C41", "#4E342E", "#ffffff"),  # Braun
    ("#C62828", "#B71C1C", "#ffffff"),  # Scharlachrot
    ("#4527A0", "#311B92", "#ffffff"),  # Indigoblau
    ("#558B2F", "#33691E", "#ffffff"),  # Olivgrün
    ("#00796B", "#004D40", "#ffffff"),  # Mittleres Türkis
]

PRIORITAET_GEWICHT = {"Hoch": 3, "Mittel": 2, "Tief": 1}

KALENDER_START_H = 8    # Frühester sichtbarer Zeitpunkt
KALENDER_ENDE_H  = 22   # Spätester sichtbarer Zeitpunkt
PX_PRO_MIN       = 1.5  # 14h × 60 × 1.5 = 1260 px Gesamthöhe

# ──────────────────────────────────────────────
# Session-State initialisieren
# ──────────────────────────────────────────────
if "wochen_bloecke" not in st.session_state:
    # Nutzer-Blöcke pro Wochentag: {"Montag": [{"typ","von","bis","label"}, ...]}
    st.session_state.wochen_bloecke: dict = {t: [] for t in WOCHENTAGE}

if "fach_farb_map" not in st.session_state:
    # Weist jedem Fachnamen einen Index in FACH_PALETTE zu
    st.session_state.fach_farb_map: dict[str, int] = {}

if "pendelzeit_min" not in st.session_state:
    st.session_state.pendelzeit_min: int = 0

# ──────────────────────────────────────────────
# Hilfsfunktionen
# ──────────────────────────────────────────────

def zeit_zu_min(s: str) -> int:
    """'HH:MM' → Minuten seit Mitternacht."""
    h, m = map(int, s.split(":"))
    return h * 60 + m


def min_zu_zeit(m: int) -> str:
    """Minuten seit Mitternacht → 'HH:MM'."""
    return f"{m//60:02d}:{m%60:02d}"


def fach_farbe(fach: str) -> tuple:
    """Gibt (bg, rand, text) für ein Fach zurück; weist neue Fächer automatisch zu."""
    if fach not in st.session_state.fach_farb_map:
        idx = len(st.session_state.fach_farb_map) % len(FACH_PALETTE)
        st.session_state.fach_farb_map[fach] = idx
    idx = st.session_state.fach_farb_map[fach]
    return FACH_PALETTE[idx]


def freie_slots(bloecke: list[dict]) -> list[tuple[int, int]]:
    """
    Berechnet zusammenhängende freie Zeitfenster (nicht durch Nutzer-Blöcke belegt).
    Rückgabe: sortierte Liste von (von_min, bis_min) innerhalb 08:00–22:00.
    """
    start = KALENDER_START_H * 60
    ende  = KALENDER_ENDE_H  * 60

    belegt: list[tuple[int, int]] = []
    for b in bloecke:
        von = max(zeit_zu_min(b["von"]), start)
        bis = min(zeit_zu_min(b["bis"]), ende)
        if bis > von:
            belegt.append((von, bis))
    belegt.sort()

    frei: list[tuple[int, int]] = []
    zeiger = start
    for von, bis in belegt:
        if von > zeiger:
            frei.append((zeiger, von))
        zeiger = max(zeiger, bis)
    if zeiger < ende:
        frei.append((zeiger, ende))

    return frei


def pendelzeit_einplanen(
    slots: list[tuple[int, int]], pendel_min: int
) -> tuple[list[dict], list[tuple[int, int]]]:
    """
    Belegt die ersten `pendel_min` Minuten des ersten freien Slots als Pendelblock.
    Gibt (pendelblöcke, verbleibende_freie_slots) zurück.
    """
    if pendel_min <= 0:
        return [], slots

    pendel_bloecke: list[dict] = []
    neue_slots: list[tuple[int, int]] = []
    rest = pendel_min

    for von, bis in slots:
        if rest <= 0:
            neue_slots.append((von, bis))
            continue
        genutzt = min(rest, bis - von)
        pendel_bloecke.append({
            "typ": "Pendeln",
            "von": min_zu_zeit(von),
            "bis": min_zu_zeit(von + genutzt),
            "label": "Pendeln",
        })
        rest -= genutzt
        if von + genutzt < bis:
            neue_slots.append((von + genutzt, bis))

    return pendel_bloecke, neue_slots


def slots_mit_lernbloecken_fuellen(
    slots: list[tuple[int, int]],
    fach_minuten: list[dict],   # [{"id", "fach", "minuten_offen"}, …]
    max_block: int = 90,
    pause: int = 20,
) -> list[dict]:
    """
    Pomodoro-Algorithmus: füllt freie Slots mit Lernblöcken und Pausen.

    Regeln:
    - Max max_block Minuten am Stück pro Fach (Standard 90 Min).
    - Nach einem vollen Block: pause Minuten Pflichtpause (Standard 20 Min).
    - Fächer wechseln sich ab – nie zwei volle Blöcke desselben Fachs hintereinander.
    - Mindestblockgröße: 30 Minuten.
    """
    bloecke: list[dict] = []
    fach_queue = [dict(f) for f in fach_minuten]  # Arbeitskopie
    letztes_id: int | None = None

    for slot_von, slot_bis in slots:
        cursor = slot_von

        while cursor < slot_bis:
            verfuegbar = slot_bis - cursor

            # Fächer mit noch ≥ 30 Min Restbedarf
            offen = [f for f in fach_queue if f["minuten_offen"] >= 30]
            if not offen or verfuegbar < 30:
                break

            # Präferiere das Fach mit dem höchsten Bedarf; wechsle wenn möglich
            andere = [f for f in offen if f["id"] != letztes_id]
            naechstes = (andere if andere else offen)[0]

            block_len = min(verfuegbar, max_block, naechstes["minuten_offen"])

            # Falls dieser Fach-Rest < 30 → nächstes Fach versuchen
            if block_len < 30:
                rest_offen = [f for f in offen if f["id"] != naechstes["id"]]
                if not rest_offen:
                    break
                naechstes = rest_offen[0]
                block_len = min(verfuegbar, max_block, naechstes["minuten_offen"])
                if block_len < 30:
                    break

            bloecke.append({
                "typ":     "Lernen",
                "von":     min_zu_zeit(cursor),
                "bis":     min_zu_zeit(cursor + block_len),
                "label":   naechstes["fach"],
                "fach_id": naechstes["id"],
            })
            naechstes["minuten_offen"] -= block_len
            letztes_id = naechstes["id"]
            cursor += block_len

            # Pflichtpause nach vollem Block – nur wenn danach noch genug Zeit
            if block_len >= max_block and cursor + pause + 30 <= slot_bis:
                bloecke.append({
                    "typ":   "Pause",
                    "von":   min_zu_zeit(cursor),
                    "bis":   min_zu_zeit(cursor + pause),
                    "label": "Pause",
                })
                cursor += pause

            # Erschöpfte Fächer aus der Queue entfernen
            fach_queue = [f for f in fach_queue if f["minuten_offen"] >= 30]
            if not fach_queue:
                break

    return bloecke


def lernplan_generieren(
    pruefungen: list[dict],
    wochen_bloecke: dict[str, list[dict]],
    pendelzeit_min: int,
    max_block: int = 90,
    pause: int = 20,
) -> dict[str, list[dict]]:
    """
    Hauptalgorithmus: erzeugt den vollständigen Wochenplan (7 Tage).

    Je Tag:
    1. Nutzerdefinierte Blöcke übernehmen.
    2. Freie Slots berechnen (08:00–22:00).
    3. Pendelzeit als Block an den Tagesanfang setzen.
    4. Verbleibende Zeit proportional auf Prüfungen verteilen
       (Gewicht = Priorität × Dringlichkeit).
    5. Pomodoro-Blöcke mit Fächer-Rotation einplanen.
    """
    heute = date.today()
    kommende = [p for p in pruefungen if date.fromisoformat(p["datum"]) >= heute]

    # Lernbedarf je Prüfung: Priorität × (10 / Tage_bis_Prüfung)
    # → je näher die Prüfung, desto höher der Wert
    bedarf: dict[int, float] = {}
    for p in kommende:
        tage_bis = max(1, (date.fromisoformat(p["datum"]) - heute).days)
        bedarf[p["id"]] = PRIORITAET_GEWICHT.get(p["prioritaet"], 1) * (10.0 / tage_bis)
    gesamt_bedarf = sum(bedarf.values()) or 1.0

    result: dict[str, list[dict]] = {}

    for offset in range(7):
        tag_datum = heute + timedelta(days=offset)
        wochentag = WOCHENTAGE[tag_datum.weekday()]
        nutzer_bloecke = list(wochen_bloecke.get(wochentag, []))

        if not kommende:
            result[wochentag] = nutzer_bloecke
            continue

        # Freie Slots → Pendelzeit abziehen → verbleibende Lernslots
        frei = freie_slots(nutzer_bloecke)
        pendel_bloecke, lern_slots = pendelzeit_einplanen(frei, pendelzeit_min)
        freie_min = sum(b - a for a, b in lern_slots)

        # Proportionalen Lernbedarf pro Fach für diesen Tag berechnen
        fach_minuten: list[dict] = []
        for p in sorted(kommende, key=lambda x: bedarf[x["id"]], reverse=True):
            anteil   = bedarf[p["id"]] / gesamt_bedarf
            ziel_min = int(anteil * freie_min)
            if ziel_min >= 30:
                fach_minuten.append({
                    "id":           p["id"],
                    "fach":         p["fach"],
                    "minuten_offen": ziel_min,
                })

        # Farbzuweisung für neue Fächer (damit der Kalender konsistente Farben hat)
        for fm in fach_minuten:
            fach_farbe(fm["fach"])

        lern_bloecke = slots_mit_lernbloecken_fuellen(
            lern_slots, fach_minuten, max_block, pause
        )

        result[wochentag] = nutzer_bloecke + pendel_bloecke + lern_bloecke

    return result


def kalender_als_html(tages_daten: dict[str, list[dict]], heute: date) -> str:
    """
    Rendert den visuellen 7-Tage-Kalender als HTML.
    Spalten = Wochentage, Blöcke = farbige Rechtecke proportional zur Dauer.
    Lernblöcke bekommen je Fach eine eigene Farbe aus FACH_PALETTE.
    """
    gesamt_min = (KALENDER_ENDE_H - KALENDER_START_H) * 60
    gesamt_px  = gesamt_min * PX_PRO_MIN

    # Zeitachse (links) – dunkle Beschriftung auf hellem Hintergrund
    zeit_html = "".join(
        f'<div style="position:absolute;top:{(h-KALENDER_START_H)*60*PX_PRO_MIN:.0f}px;'
        f'right:4px;font-size:10px;color:#888;line-height:1;transform:translateY(-50%);">'
        f'{h:02d}:00</div>'
        for h in range(KALENDER_START_H, KALENDER_ENDE_H + 1)
    )

    header_html = ""
    spalten_html = ""

    for offset in range(7):
        tag_datum = heute + timedelta(days=offset)
        wochentag = WOCHENTAGE[tag_datum.weekday()]
        ist_heute = (offset == 0)

        # Kopfzeile: Heute hervorgehoben, andere dunkelgrau
        kopf_farbe  = "#1565C0" if ist_heute else "#333333"
        kopf_gewicht = "bold"
        header_html += (
            f'<div style="flex:1;text-align:center;padding:6px 2px;min-width:85px;">'
            f'<div style="font-weight:{kopf_gewicht};color:{kopf_farbe};font-size:13px;">'
            f'{wochentag[:2]}</div>'
            f'<div style="color:#888;font-size:11px;">{tag_datum.strftime("%d.%m")}</div>'
            f'</div>'
        )

        # Stündliche Hintergrundstreifen – helles Weiß/Hellgrau alternierend
        streifen = "".join(
            f'<div style="position:absolute;top:{(h-KALENDER_START_H)*60*PX_PRO_MIN:.0f}px;'
            f'left:0;right:0;height:{60*PX_PRO_MIN:.0f}px;'
            f'background:{"#ffffff" if h%2==0 else "#f7f8fa"};'
            f'border-top:1px solid #e0e4e8;"></div>'
            for h in range(KALENDER_START_H, KALENDER_ENDE_H)
        )

        # Aktivitätsblöcke
        bloecke_html = ""
        for block in tages_daten.get(wochentag, []):
            von_min = zeit_zu_min(block["von"])
            bis_min = zeit_zu_min(block["bis"])
            if bis_min <= KALENDER_START_H * 60 or von_min >= KALENDER_ENDE_H * 60:
                continue

            von_c = max(von_min, KALENDER_START_H * 60)
            bis_c = min(bis_min, KALENDER_ENDE_H  * 60)
            top   = (von_c - KALENDER_START_H * 60) * PX_PRO_MIN
            hoehe = max(20, (bis_c - von_c) * PX_PRO_MIN - 2)

            # Lernblöcke: Fach-spezifische Farbe; alle anderen: Aktivitäts-Farbe
            if block["typ"] == "Lernen":
                bg, rand, txt = fach_farbe(block.get("label", ""))
                em = "📖"
            else:
                bg, rand, txt, em = AKTIVITAET_FARBEN.get(block["typ"], AKTIVITAET_FARBEN["Privat"])

            anzeige = block.get("label", block["typ"])
            tooltip = f'{em} {anzeige}  {block["von"]}–{block["bis"]}'

            bloecke_html += (
                f'<div style="position:absolute;top:{top:.0f}px;left:3px;right:3px;'
                f'height:{hoehe:.0f}px;background-color:{bg};'
                f'border-radius:4px;padding:2px 5px;font-size:10px;color:{txt};'
                f'overflow:hidden;white-space:nowrap;text-overflow:ellipsis;'
                f'box-sizing:border-box;cursor:default;font-weight:500;'
                f'box-shadow:0 1px 3px rgba(0,0,0,0.15);" title="{tooltip}">'
                f'{em} {anzeige}</div>'
            )

        spalten_html += (
            f'<div style="flex:1;position:relative;height:{gesamt_px:.0f}px;'
            f'min-width:85px;border-left:1px solid #dde1e6;">'
            f'{streifen}{bloecke_html}</div>'
        )

    return (
        f'<div style="background:#f8f9fa;border-radius:10px;padding:16px;'
        f'overflow-x:auto;border:1px solid #dee2e6;">'
        f'<div style="display:flex;margin-left:46px;border-bottom:2px solid #1565C0;'
        f'padding-bottom:6px;margin-bottom:6px;">{header_html}</div>'
        f'<div style="display:flex;">'
        f'<div style="width:46px;position:relative;height:{gesamt_px:.0f}px;flex-shrink:0;">'
        f'{zeit_html}</div>'
        f'<div style="display:flex;flex:1;">{spalten_html}</div>'
        f'</div></div>'
    )


# ══════════════════════════════════════════════════════════
# SEITE
# ══════════════════════════════════════════════════════════
st.title("📅 Lernplan")
st.markdown(
    "Trage Prüfungen und feste Aktivitäten ein – "
    "der Algorithmus plant **Pomodoro-Lernblöcke** mit Fächer-Rotation automatisch ein."
)
st.divider()

tab_pruefungen, tab_woche, tab_kalender = st.tabs(["📋 Prüfungen", "⚙️ Woche planen", "🗓️ Kalender"])

# ══════════════════════════════════════════════
# TAB 1 – PRÜFUNGEN
# ══════════════════════════════════════════════
with tab_pruefungen:
    col_form, col_liste = st.columns([1, 1], gap="large")

    with col_form:
        st.subheader("➕ Prüfung eintragen")
        with st.form("formular_pruefung", clear_on_submit=True):
            fach      = st.text_input("Fach", placeholder="z. B. Statistik, Informatik …")
            datum     = st.date_input("Prüfungsdatum", min_value=date.today(),
                                      value=date.today() + timedelta(days=14))
            prioritaet = st.selectbox("Priorität", ["Hoch", "Mittel", "Tief"],
                                      help="Hoch = viel Lernzeit, Tief = weniger dringend")
            speichern = st.form_submit_button("💾 Speichern", type="primary", use_container_width=True)

        if speichern:
            if not fach.strip():
                st.error("Bitte einen Fachnamen eingeben.")
            else:
                pruefung_eintragen(fach.strip(), datum.isoformat(), prioritaet)
                # Farbe sofort zuweisen, damit der Kalender konsistent bleibt
                fach_farbe(fach.strip())
                st.success(f"✅ **{fach}** am {datum.strftime('%d.%m.%Y')} gespeichert!")
                st.rerun()

    with col_liste:
        st.subheader("📋 Eingetragene Prüfungen")
        pruefungen = alle_pruefungen_laden()

        if not pruefungen:
            st.info("Noch keine Prüfungen eingetragen.")
        else:
            for p in pruefungen:
                p_datum   = date.fromisoformat(p["datum"])
                tage_noch = (p_datum - date.today()).days
                prio_em   = {"Hoch": "🔴", "Mittel": "🟡", "Tief": "🟢"}.get(p["prioritaet"], "⚪")

                # Fachfarbe als kleines Badge
                fb, fr, ft = fach_farbe(p["fach"])
                badge = (
                    f'<span style="background:{fb};border-left:3px solid {fr};'
                    f'color:{ft};padding:1px 6px;border-radius:3px;font-size:11px;">'
                    f'■</span>'
                )
                z, b = st.columns([5, 1])
                with z:
                    st.markdown(
                        f'{badge} {prio_em} **{p["fach"]}** – {p_datum.strftime("%d.%m.%Y")} '
                        f'_({tage_noch} Tage)_ · {p["prioritaet"]}',
                        unsafe_allow_html=True,
                    )
                with b:
                    if st.button("🗑️", key=f"del_{p['id']}", help="Löschen"):
                        pruefung_loeschen(p["id"])
                        st.rerun()

# ══════════════════════════════════════════════
# TAB 2 – WOCHE PLANEN
# ══════════════════════════════════════════════
with tab_woche:
    st.subheader("⚙️ Globale Einstellungen")

    # ── Globale Parameter ──────────────────────
    gs1, gs2, gs3 = st.columns(3)
    with gs1:
        neu_pendel = st.number_input(
            "🚇 Pendelzeit pro Tag (Minuten)",
            min_value=0, max_value=180,
            value=st.session_state.pendelzeit_min,
            step=5,
            help="Wird als Block am Beginn des ersten freien Slots eingeplant.",
        )
        if neu_pendel != st.session_state.pendelzeit_min:
            st.session_state.pendelzeit_min = neu_pendel
    with gs2:
        max_block_min = st.number_input(
            "⏱️ Max. Lernblock (Minuten)",
            min_value=30, max_value=120,
            value=90, step=15,
            help="Längstes Stück, das am Stück für ein Fach eingeplant wird.",
        )
    with gs3:
        pflicht_pause = st.number_input(
            "☕ Pflichtpause nach vollem Block (Minuten)",
            min_value=5, max_value=30,
            value=20, step=5,
            help="Wird automatisch nach jedem vollen Lernblock eingefügt.",
        )

    st.divider()
    st.subheader("📅 Feste Aktivitäten pro Tag")
    st.markdown(
        "Trage Vorlesungen, Sport und andere feste Termine ein. "
        "Die restliche Zeit (minus Pendelzeit) wird als **Lernzeit** eingeplant."
    )

    # Farb-Legende
    legende = " &nbsp; ".join(
        f'<span style="background:{bg};border-left:3px solid {rd};'
        f'padding:2px 8px;border-radius:3px;font-size:12px;color:{tx};">'
        f'{em} {typ}</span>'
        for typ, (bg, rd, tx, em) in AKTIVITAET_FARBEN.items()
        if typ not in ("Pause", "Pendeln")
    )
    st.markdown(f'<div style="margin-bottom:12px;">{legende}</div>', unsafe_allow_html=True)

    # ── Tages-Tabs ─────────────────────────────
    tag_tabs = st.tabs(WOCHENTAGE)

    for tag, tag_tab in zip(WOCHENTAGE, tag_tabs):
        with tag_tab:

            # Bestehende Blöcke anzeigen
            bloecke = st.session_state.wochen_bloecke[tag]
            if not bloecke:
                st.markdown("_Noch keine festen Aktivitäten._")
            else:
                for i, blk in enumerate(bloecke):
                    bg, rd, tx, em = AKTIVITAET_FARBEN.get(blk["typ"], AKTIVITAET_FARBEN["Privat"])
                    bc, dc = st.columns([5, 1])
                    with bc:
                        st.markdown(
                            f'<div style="background:{bg};border-left:3px solid {rd};'
                            f'padding:5px 10px;border-radius:4px;color:{tx};margin-bottom:4px;">'
                            f'{em} <strong>{blk["typ"]}</strong>'
                            f'{"  –  " + blk["label"] if blk.get("label") else ""}'
                            f'  ·  {blk["von"]} – {blk["bis"]}</div>',
                            unsafe_allow_html=True,
                        )
                    with dc:
                        if st.button("🗑️", key=f"del_{tag}_{i}"):
                            st.session_state.wochen_bloecke[tag].pop(i)
                            st.rerun()

            # Neuen Block hinzufügen
            with st.form(f"bf_{tag}", clear_on_submit=True):
                st.markdown("**Neuen Block hinzufügen**")
                c1, c2, c3, c4 = st.columns([2, 2, 2, 3])
                with c1:
                    typ = st.selectbox("Typ", BLOCK_TYPEN, key=f"t_{tag}")
                with c2:
                    std_von = {"Vorlesung":"08:00","Sport":"18:00","Nachhilfe":"17:00",
                               "Privat":"19:00","Frei":"20:00"}
                    von_s = st.text_input("Von", value=std_von.get(typ,"08:00"), key=f"v_{tag}")
                with c3:
                    std_bis = {"Vorlesung":"10:00","Sport":"19:00","Nachhilfe":"18:00",
                               "Privat":"21:00","Frei":"22:00"}
                    bis_s = st.text_input("Bis", value=std_bis.get(typ,"10:00"), key=f"b_{tag}")
                with c4:
                    lbl = st.text_input(
                        "Bezeichnung (optional)",
                        placeholder="z. B. Statistik-VL, Fussball …",
                        key=f"l_{tag}",
                    )
                hinzu = st.form_submit_button("➕ Hinzufügen", type="primary", use_container_width=True)

            if hinzu:
                try:
                    vm = zeit_zu_min(von_s.strip())
                    bm = zeit_zu_min(bis_s.strip())
                    if bm <= vm:
                        raise ValueError("Endzeit muss nach Startzeit liegen.")
                    st.session_state.wochen_bloecke[tag].append({
                        "typ":   typ,
                        "von":   von_s.strip(),
                        "bis":   bis_s.strip(),
                        "label": lbl.strip() if lbl.strip() else typ,
                    })
                    st.rerun()
                except Exception as exc:
                    st.error(f"Ungültige Zeit: {exc}  (Format HH:MM)")

# ══════════════════════════════════════════════
# TAB 3 – KALENDER
# ══════════════════════════════════════════════
with tab_kalender:
    st.subheader("🗓️ Dein Wochenkalender")

    pruefungen_aktuell = alle_pruefungen_laden()

    # ── Übersichts-Metriken ────────────────────
    m1, m2, m3 = st.columns(3)
    m1.metric("Prüfungen", len(pruefungen_aktuell))
    m2.metric(
        "Aktivitäts-Blöcke (Woche)",
        sum(len(v) for v in st.session_state.wochen_bloecke.values()),
    )
    if pruefungen_aktuell:
        naechste = min(pruefungen_aktuell, key=lambda p: p["datum"])
        tage_n   = (date.fromisoformat(naechste["datum"]) - date.today()).days
        m3.metric("Nächste Prüfung", naechste["fach"], delta=f"in {tage_n} Tagen")

    st.divider()

    if not pruefungen_aktuell:
        st.warning("⚠️ Trage zuerst mindestens eine Prüfung ein (Tab **Prüfungen**).")
    else:
        # Lernplan berechnen (benutzt max_block_min / pflicht_pause aus Tab 2 → Defaults)
        tages_daten = lernplan_generieren(
            pruefungen_aktuell,
            st.session_state.wochen_bloecke,
            st.session_state.pendelzeit_min,
            max_block=max_block_min,
            pause=pflicht_pause,
        )

        # ── Tages-Zusammenfassung ──────────────
        heute_datum = date.today()
        summary_cols = st.columns(7)
        for offset, col in enumerate(summary_cols):
            tag_datum = heute_datum + timedelta(days=offset)
            wochentag = WOCHENTAGE[tag_datum.weekday()]
            bloecke_tag = tages_daten.get(wochentag, [])

            lern_min = sum(
                zeit_zu_min(b["bis"]) - zeit_zu_min(b["von"])
                for b in bloecke_tag if b["typ"] == "Lernen"
            )
            lern_std = lern_min / 60

            ist_heute = (offset == 0)
            farbe = "#2ecc71" if ist_heute else "#aaaaaa"
            rand_farbe = "#1565C0" if ist_heute else "#dee2e6"
            col.markdown(
                f'<div style="text-align:center;padding:6px;border-radius:6px;'
                f'background:#ffffff;border:2px solid {rand_farbe};'
                f'box-shadow:0 1px 4px rgba(0,0,0,0.08);">'
                f'<div style="color:{farbe};font-weight:bold;font-size:12px;">{wochentag[:2]}</div>'
                f'<div style="color:#222;font-size:16px;font-weight:bold;">{lern_std:.1f}h</div>'
                f'<div style="color:#888;font-size:10px;">Lernen</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # ── Kalender ──────────────────────────
        st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
        st.markdown(kalender_als_html(tages_daten, heute_datum), unsafe_allow_html=True)

        # ── Farb-Legende ──────────────────────
        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)

        # Aktivitätstypen – farbige Pillenbadges
        akt_legende = " &nbsp; ".join(
            f'<span style="background:{bg};border-radius:4px;'
            f'padding:3px 9px;font-size:11px;color:{tx};font-weight:500;">'
            f'{em} {typ}</span>'
            for typ, (bg, rd, tx, em) in AKTIVITAET_FARBEN.items()
        )
        # Lern-Fächer mit ihren Farben
        fach_legende = " &nbsp; ".join(
            f'<span style="background:{FACH_PALETTE[idx][0]};border-radius:4px;'
            f'padding:3px 9px;font-size:11px;color:{FACH_PALETTE[idx][2]};font-weight:500;">'
            f'📖 {fach}</span>'
            for fach, idx in st.session_state.fach_farb_map.items()
        )
        st.markdown(
            f'<div style="background:#f8f9fa;border:1px solid #dee2e6;border-radius:8px;'
            f'padding:10px 14px;margin-top:8px;">'
            f'<div style="font-size:11px;color:#888;margin-bottom:6px;">Legende</div>'
            f'<div>{akt_legende}</div>'
            f'<div style="margin-top:6px;">{fach_legende if fach_legende else ""}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Hinweis wenn keine Lernzeit gefunden
        total_lern = sum(
            zeit_zu_min(b["bis"]) - zeit_zu_min(b["von"])
            for v in tages_daten.values() for b in v if b["typ"] == "Lernen"
        )
        if total_lern == 0:
            st.info(
                "Keine freie Lernzeit gefunden. "
                "Prüfe ob die Aktivitäts-Blöcke den ganzen Tag belegen "
                "oder reduziere die Pendelzeit (Tab **Woche planen**)."
            )

# ──────────────────────────────────────────────
# Fußzeile
# ──────────────────────────────────────────────
st.divider()
st.caption("PredictEd · Lernplan · Powered by Streamlit & SQLite")
