"""
pages/lernplan.py – Lernplan-Seite (Studyscore)
Design: identisch zu app.py (DM Sans, #b5cc18, #f2f2f0, ss-card)
Inhalt: Prüfungen verwalten, Woche planen, visueller Pomodoro-Kalender
"""

import streamlit as st
from datetime import date, timedelta

from database import pruefung_eintragen, alle_pruefungen_laden, pruefung_loeschen

# ── Seiten-Konfiguration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Lernplan – Studyscore",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS: exakt gleich wie app.py ───────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

  :root {
    --bg: #f2f2f0; --surface: #ffffff; --dark: #1a1a1a; --mid: #888880;
    --border: #e0e0dc; --accent: #b5cc18; --accent-dark: #96ad00;
    --accent-light: #eef3c2; --radius: 12px;
  }

  html, body, [data-testid="stAppViewContainer"] {
    font-family: 'DM Sans', sans-serif !important;
    background: #f2f2f0 !important;
  }
  [data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e0e0dc !important;
  }
  .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }

  /* Karten */
  .ss-card {
    background: #fff; border-radius: 16px;
    border: 1px solid #e0e0dc; padding: 24px 28px; margin-bottom: 16px;
  }
  .ss-card-title { font-size: 16px; font-weight: 600; color: #1a1a1a; margin-bottom: 4px; }
  .ss-card-desc  { font-size: 13px; color: #888880; line-height: 1.5; margin-bottom: 16px; }

  /* Buttons */
  .stButton > button {
    background: #b5cc18 !important; color: #1a1a1a !important;
    font-weight: 600 !important; border: none !important;
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
    padding: 0.55rem 1.4rem !important; transition: all 0.2s !important;
  }
  .stButton > button:hover { background: #96ad00 !important; transform: translateY(-1px) !important; }

  /* Tab-Unterstrich */
  .stTabs [data-baseweb="tab-highlight"] { background-color: #b5cc18 !important; }
  .stTabs [data-baseweb="tab"]:hover     { color: #96ad00 !important; }

  /* Metric-Kacheln */
  .metric-tile {
    background: #f2f2f0; border: 1.5px solid #e0e0dc;
    border-radius: 12px; padding: 14px 16px; text-align: center;
  }
  .metric-tile .label {
    font-size: 10px; font-family: 'DM Mono', monospace;
    letter-spacing: 0.08em; text-transform: uppercase; color: #888880; margin-bottom: 6px;
  }
  .metric-tile .value {
    font-size: 22px; font-weight: 700; font-family: 'DM Mono', monospace;
    color: #1a1a1a; line-height: 1;
  }

  /* Pill-Badges */
  .pill { display:inline-flex; align-items:center; gap:5px; background:#f2f2f0;
    border:1.5px solid #e0e0dc; border-radius:999px; padding:4px 12px;
    font-size:12px; color:#888880; margin:2px; }
  .pill-green  { background:#eef3c2; border-color:#b5cc18; color:#96ad00; }
  .pill-red    { background:#fdecea; border-color:#f44336; color:#f44336; }
  .pill-orange { background:#fff8e1; border-color:#f59e0b; color:#f59e0b; }

  #MainMenu, footer, header { visibility: hidden; }

  /* Remove white empty space above tabs */
  .stTabs { margin-top: 0 !important; padding-top: 0 !important; }
  div[data-testid="stVerticalBlock"] > div:empty { display: none !important; }
  .stMarkdown:empty { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Konstanten ─────────────────────────────────────────────────────────────────
WOCHENTAGE = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"]
BLOCK_TYPEN = ["Vorlesung", "Sport", "Nachhilfe", "Privat", "Frei"]

# Aktivitäts-Farben: (Hintergrund, Rand, Text, Emoji)
AKTIVITAET_FARBEN: dict[str, tuple] = {
    "Vorlesung": ("#1565C0", "#0D47A1", "#ffffff", "🎓"),
    "Sport":     ("#BF360C", "#8D2509", "#ffffff", "🏃"),
    "Nachhilfe": ("#E65100", "#BF360C", "#ffffff", "👨‍🏫"),
    "Privat":    ("#546E7A", "#37474F", "#ffffff", "🔒"),
    "Frei":      ("#AD1457", "#880E4F", "#ffffff", "🌙"),
    "Pendeln":   ("#00695C", "#004D40", "#ffffff", "🚇"),
    "Pause":     ("#F9A825", "#F57F17", "#333333", "☕"),
}

# Je Fach eine eigene Farbe (keine Blau-/Rottöne – Kontrast zu Aktivitäten)
FACH_PALETTE = [
    ("#2E7D32", "#1B5E20", "#ffffff"),  # Waldgrün
    ("#7B1FA2", "#4A148C", "#ffffff"),  # Tiefviolett
    ("#00838F", "#006064", "#ffffff"),  # Cyan
    ("#6D4C41", "#4E342E", "#ffffff"),  # Braun
    ("#C62828", "#B71C1C", "#ffffff"),  # Scharlachrot
    ("#4527A0", "#311B92", "#ffffff"),  # Indigo
    ("#558B2F", "#33691E", "#ffffff"),  # Olivgrün
    ("#00796B", "#004D40", "#ffffff"),  # Türkis
]

PRIORITAET_GEWICHT = {"Hoch": 3, "Mittel": 2, "Tief": 1}
KALENDER_START_H = 8
KALENDER_ENDE_H  = 22
PX_PRO_MIN       = 1.5

# ── Session-State ──────────────────────────────────────────────────────────────
if "wochen_bloecke" not in st.session_state:
    st.session_state.wochen_bloecke: dict = {t: [] for t in WOCHENTAGE}
if "fach_farb_map" not in st.session_state:
    st.session_state.fach_farb_map: dict[str, int] = {}
if "pendelzeit_min" not in st.session_state:
    st.session_state.pendelzeit_min: int = 0

# ── Hilfsfunktionen ────────────────────────────────────────────────────────────

def zeit_zu_min(s: str) -> int:
    h, m = map(int, s.split(":"))
    return h * 60 + m

def min_zu_zeit(m: int) -> str:
    return f"{m//60:02d}:{m%60:02d}"

def fach_farbe(fach: str) -> tuple:
    if fach not in st.session_state.fach_farb_map:
        idx = len(st.session_state.fach_farb_map) % len(FACH_PALETTE)
        st.session_state.fach_farb_map[fach] = idx
    return FACH_PALETTE[st.session_state.fach_farb_map[fach]]

def freie_slots(bloecke: list[dict]) -> list[tuple[int, int]]:
    start, ende = KALENDER_START_H * 60, KALENDER_ENDE_H * 60
    belegt = sorted([
        (max(zeit_zu_min(b["von"]), start), min(zeit_zu_min(b["bis"]), ende))
        for b in bloecke
        if min(zeit_zu_min(b["bis"]), ende) > max(zeit_zu_min(b["von"]), start)
    ])
    frei, zeiger = [], start
    for von, bis in belegt:
        if von > zeiger:
            frei.append((zeiger, von))
        zeiger = max(zeiger, bis)
    if zeiger < ende:
        frei.append((zeiger, ende))
    return frei

def pendelzeit_einplanen(slots, pendel_min):
    if pendel_min <= 0:
        return [], slots
    pendel_bloecke, neue_slots, rest = [], [], pendel_min
    for von, bis in slots:
        if rest <= 0:
            neue_slots.append((von, bis))
            continue
        genutzt = min(rest, bis - von)
        pendel_bloecke.append({"typ":"Pendeln","von":min_zu_zeit(von),
                                "bis":min_zu_zeit(von+genutzt),"label":"Pendeln"})
        rest -= genutzt
        if von + genutzt < bis:
            neue_slots.append((von + genutzt, bis))
    return pendel_bloecke, neue_slots

def slots_mit_lernbloecken_fuellen(slots, fach_minuten, max_block=90, pause=20):
    """Pomodoro: max. max_block Min. pro Fach, danach pause Min. Pflichtpause, Fächer abwechseln."""
    bloecke = []
    fach_queue = [dict(f) for f in fach_minuten]
    letztes_id = None
    for slot_von, slot_bis in slots:
        cursor = slot_von
        while cursor < slot_bis:
            verfuegbar = slot_bis - cursor
            offen = [f for f in fach_queue if f["minuten_offen"] >= 30]
            if not offen or verfuegbar < 30:
                break
            andere = [f for f in offen if f["id"] != letztes_id]
            naechstes = (andere if andere else offen)[0]
            block_len = min(verfuegbar, max_block, naechstes["minuten_offen"])
            if block_len < 30:
                rest_offen = [f for f in offen if f["id"] != naechstes["id"]]
                if not rest_offen:
                    break
                naechstes = rest_offen[0]
                block_len = min(verfuegbar, max_block, naechstes["minuten_offen"])
                if block_len < 30:
                    break
            bloecke.append({"typ":"Lernen","von":min_zu_zeit(cursor),
                             "bis":min_zu_zeit(cursor+block_len),
                             "label":naechstes["fach"],"fach_id":naechstes["id"]})
            naechstes["minuten_offen"] -= block_len
            letztes_id = naechstes["id"]
            cursor += block_len
            if block_len >= max_block and cursor + pause + 30 <= slot_bis:
                bloecke.append({"typ":"Pause","von":min_zu_zeit(cursor),
                                 "bis":min_zu_zeit(cursor+pause),"label":"Pause"})
                cursor += pause
            fach_queue = [f for f in fach_queue if f["minuten_offen"] >= 30]
            if not fach_queue:
                break
    return bloecke

def lernplan_generieren(pruefungen, wochen_bloecke, pendelzeit_min, max_block=90, pause=20):
    """Verteilt Lernblöcke für 7 Tage: Priorität × Dringlichkeit, Pomodoro-Rotation."""
    heute = date.today()
    kommende = [p for p in pruefungen if date.fromisoformat(p["datum"]) >= heute]
    bedarf = {}
    for p in kommende:
        tage_bis = max(1, (date.fromisoformat(p["datum"]) - heute).days)
        bedarf[p["id"]] = PRIORITAET_GEWICHT.get(p["prioritaet"], 1) * (10.0 / tage_bis)
    gesamt_bedarf = sum(bedarf.values()) or 1.0
    result = {}
    for offset in range(7):
        tag_datum = heute + timedelta(days=offset)
        wochentag = WOCHENTAGE[tag_datum.weekday()]
        nutzer_bloecke = list(wochen_bloecke.get(wochentag, []))
        if not kommende:
            result[wochentag] = nutzer_bloecke
            continue
        frei = freie_slots(nutzer_bloecke)
        pendel_bloecke, lern_slots = pendelzeit_einplanen(frei, pendelzeit_min)
        freie_min = sum(b - a for a, b in lern_slots)
        fach_minuten = []
        for p in sorted(kommende, key=lambda x: bedarf[x["id"]], reverse=True):
            ziel_min = int(bedarf[p["id"]] / gesamt_bedarf * freie_min)
            if ziel_min >= 30:
                fach_minuten.append({"id":p["id"],"fach":p["fach"],"minuten_offen":ziel_min})
        for fm in fach_minuten:
            fach_farbe(fm["fach"])
        result[wochentag] = nutzer_bloecke + pendel_bloecke + slots_mit_lernbloecken_fuellen(
            lern_slots, fach_minuten, max_block, pause)
    return result

def kalender_als_html(tages_daten, heute):
    """Visueller Wochenkalender: Spalten = Tage, farbige Blöcke proportional zur Dauer."""
    gesamt_px = (KALENDER_ENDE_H - KALENDER_START_H) * 60 * PX_PRO_MIN

    zeit_html = "".join(
        f'<div style="position:absolute;top:{(h-KALENDER_START_H)*60*PX_PRO_MIN:.0f}px;'
        f'right:4px;font-size:10px;color:#888880;font-family:\'DM Mono\',monospace;'
        f'line-height:1;transform:translateY(-50%);">{h:02d}:00</div>'
        for h in range(KALENDER_START_H, KALENDER_ENDE_H + 1)
    )

    header_html = ""
    spalten_html = ""

    for offset in range(7):
        tag_datum = heute + timedelta(days=offset)
        wochentag = WOCHENTAGE[tag_datum.weekday()]
        ist_heute = (offset == 0)

        kopf_farbe = "#96ad00" if ist_heute else "#888880"
        kopf_bg    = "#eef3c2" if ist_heute else "transparent"
        header_html += (
            f'<div style="flex:1;text-align:center;padding:6px 4px;min-width:85px;'
            f'background:{kopf_bg};border-radius:8px 8px 0 0;">'
            f'<div style="font-weight:600;color:{kopf_farbe};font-size:13px;'
            f'font-family:\'DM Sans\',sans-serif;">{wochentag[:2]}</div>'
            f'<div style="color:#888880;font-size:11px;font-family:\'DM Mono\',monospace;">'
            f'{tag_datum.strftime("%d.%m")}</div></div>'
        )

        # Stündliche Hintergrundstreifen
        streifen = "".join(
            f'<div style="position:absolute;top:{(h-KALENDER_START_H)*60*PX_PRO_MIN:.0f}px;'
            f'left:0;right:0;height:{60*PX_PRO_MIN:.0f}px;'
            f'background:{"#ffffff" if h%2==0 else "#fafaf8"};'
            f'border-top:1px solid #e0e0dc;"></div>'
            for h in range(KALENDER_START_H, KALENDER_ENDE_H)
        )

        # Blöcke
        bloecke_html = ""
        for block in tages_daten.get(wochentag, []):
            von_min = zeit_zu_min(block["von"])
            bis_min = zeit_zu_min(block["bis"])
            if bis_min <= KALENDER_START_H*60 or von_min >= KALENDER_ENDE_H*60:
                continue
            von_c = max(von_min, KALENDER_START_H * 60)
            bis_c = min(bis_min, KALENDER_ENDE_H  * 60)
            top   = (von_c - KALENDER_START_H * 60) * PX_PRO_MIN
            hoehe = max(8, (bis_c - von_c) * PX_PRO_MIN - 2)

            if block["typ"] == "Lernen":
                bg, _, txt = fach_farbe(block.get("label", ""))
                em = "📖"
            else:
                bg, _, txt, em = AKTIVITAET_FARBEN.get(block["typ"], AKTIVITAET_FARBEN["Privat"])

            anzeige = block.get("label", block["typ"])
            bloecke_html += (
                f'<div style="position:absolute;top:{top:.0f}px;left:3px;right:3px;'
                f'height:{hoehe:.0f}px;background:{bg};border-radius:6px;'
                f'padding:2px 6px;font-size:10px;color:{txt};font-weight:500;'
                f'font-family:\'DM Sans\',sans-serif;overflow:hidden;'
                f'white-space:nowrap;text-overflow:ellipsis;box-sizing:border-box;'
                f'box-shadow:0 1px 3px rgba(0,0,0,0.12);" '
                f'title="{em} {anzeige}  {block["von"]}–{block["bis"]}">'
                f'{em} {anzeige}</div>'
            )

        spalten_html += (
            f'<div style="flex:1;position:relative;height:{gesamt_px:.0f}px;'
            f'min-width:85px;border-left:1px solid #e0e0dc;">'
            f'{streifen}{bloecke_html}</div>'
        )

    return (
        f'<div style="background:#ffffff;border-radius:16px;border:1px solid #e0e0dc;'
        f'padding:20px;overflow-x:auto;">'
        f'<div style="display:flex;margin-left:46px;border-bottom:2px solid #b5cc18;'
        f'padding-bottom:4px;margin-bottom:4px;">{header_html}</div>'
        f'<div style="display:flex;">'
        f'<div style="width:46px;position:relative;height:{gesamt_px:.0f}px;flex-shrink:0;">'
        f'{zeit_html}</div>'
        f'<div style="display:flex;flex:1;">{spalten_html}</div>'
        f'</div></div>'
    )


# ══════════════════════════════════════════════════════════════════════════════
# SEITE
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("## 📅 Lernplan")
st.markdown(
    '<p style="color:#888880;font-size:14px;margin-top:-12px;margin-bottom:28px;">'
    'Trage deine Prüfungen und Wochenaktivitäten ein – der Algorithmus plant '
    '<strong>Pomodoro-Lernblöcke</strong> mit Fächer-Rotation automatisch ein.</p>',
    unsafe_allow_html=True,
)

tab_pruefungen, tab_woche, tab_kalender = st.tabs([
    "📋  Prüfungen", "⚙️  Woche planen", "🗓️  Kalender"
])

# ── TAB 1: PRÜFUNGEN ──────────────────────────────────────────────────────────
with tab_pruefungen:
    col_form, col_liste = st.columns([1, 1], gap="large")

    with col_form:
        st.markdown('<div class="ss-card">', unsafe_allow_html=True)
        st.markdown('<div class="ss-card-title">➕ Prüfung eintragen</div>'
                    '<div class="ss-card-desc">Fach, Datum und Priorität festlegen.</div>',
                    unsafe_allow_html=True)

        with st.form("formular_pruefung", clear_on_submit=True):
            fach       = st.text_input("Fach", placeholder="z. B. Statistik, Mikroökonomie …")
            datum      = st.date_input("Prüfungsdatum", min_value=date.today(),
                                       value=date.today() + timedelta(days=14))
            prioritaet = st.selectbox("Priorität", ["Hoch", "Mittel", "Tief"],
                                      help="Hoch = mehr Lernzeit einplanen")
            speichern  = st.form_submit_button("💾  Speichern", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

        if speichern:
            if not fach.strip():
                st.warning("Bitte einen Fachnamen eingeben.")
            else:
                pruefung_eintragen(fach.strip(), datum.isoformat(), prioritaet)
                fach_farbe(fach.strip())
                st.success(f"✅  **{fach}** am {datum.strftime('%d.%m.%Y')} gespeichert!")
                st.rerun()

    with col_liste:
        st.markdown('<div class="ss-card">', unsafe_allow_html=True)
        st.markdown('<div class="ss-card-title">📋 Eingetragene Prüfungen</div>',
                    unsafe_allow_html=True)

        pruefungen = alle_pruefungen_laden()
        if not pruefungen:
            st.markdown('<p style="color:#888880;font-size:14px;">Noch keine Prüfungen eingetragen.</p>',
                        unsafe_allow_html=True)
        else:
            for p in pruefungen:
                p_datum   = date.fromisoformat(p["datum"])
                tage_noch = (p_datum - date.today()).days
                prio_em   = {"Hoch":"🔴","Mittel":"🟡","Tief":"🟢"}.get(p["prioritaet"],"⚪")
                fach_farbe(p["fach"])
                cls   = "pill-red" if tage_noch < 14 else "pill-orange" if tage_noch < 28 else "pill-green"

                z, b = st.columns([5, 1])
                with z:
                    st.markdown(
                        f'{prio_em} <strong>{p["fach"]}</strong>'
                        f' – {p_datum.strftime("%d.%m.%Y")}'
                        f' <span class="pill {cls}" style="margin-left:6px;">in {tage_noch}d</span>',
                        unsafe_allow_html=True,
                    )
                with b:
                    if st.button("✕", key=f"del_{p['id']}"):
                        pruefung_loeschen(p["id"])
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# ── TAB 2: WOCHE PLANEN ───────────────────────────────────────────────────────
with tab_woche:

    # Globale Einstellungen
    st.markdown('<div class="ss-card">', unsafe_allow_html=True)
    st.markdown('<div class="ss-card-title">⚙️  Globale Einstellungen</div>'
                '<div class="ss-card-desc">Diese Werte gelten für alle Tage.</div>',
                unsafe_allow_html=True)

    gs1, gs2, gs3 = st.columns(3)
    with gs1:
        neu_pendel = st.number_input("🚇  Pendelzeit pro Tag (Min.)",
                                     min_value=0, max_value=180,
                                     value=st.session_state.pendelzeit_min, step=5)
        if neu_pendel != st.session_state.pendelzeit_min:
            st.session_state.pendelzeit_min = neu_pendel
    with gs2:
        max_block_min = st.number_input("⏱️  Max. Lernblock (Min.)",
                                        min_value=30, max_value=120, value=90, step=15)
    with gs3:
        pflicht_pause = st.number_input("☕  Pflichtpause nach vollem Block (Min.)",
                                        min_value=5, max_value=30, value=20, step=5)
    st.markdown('</div>', unsafe_allow_html=True)

    # Aktivitäten-Legende
    legende = " &nbsp; ".join(
        f'<span style="background:{bg};border-radius:6px;padding:3px 10px;'
        f'font-size:12px;color:{tx};font-weight:500;">{em} {typ}</span>'
        for typ, (bg, _, tx, em) in AKTIVITAET_FARBEN.items()
        if typ not in ("Pause", "Pendeln")
    )
    st.markdown(f'<div style="margin-bottom:16px;">{legende}</div>', unsafe_allow_html=True)

    # Tages-Tabs
    tag_tabs = st.tabs(WOCHENTAGE)
    for tag, tag_tab in zip(WOCHENTAGE, tag_tabs):
        with tag_tab:
            bloecke = st.session_state.wochen_bloecke[tag]

            if not bloecke:
                st.markdown('<p style="color:#888880;font-size:13px;">Noch keine Aktivitäten.</p>',
                            unsafe_allow_html=True)
            else:
                for i, blk in enumerate(bloecke):
                    bg, rd, tx, em = AKTIVITAET_FARBEN.get(blk["typ"], AKTIVITAET_FARBEN["Privat"])
                    bc, dc = st.columns([5, 1])
                    with bc:
                        st.markdown(
                            f'<div style="background:{bg};border-left:3px solid {rd};'
                            f'padding:8px 12px;border-radius:8px;color:{tx};margin-bottom:6px;'
                            f'font-family:\'DM Sans\',sans-serif;font-size:13px;">'
                            f'{em} <strong>{blk["typ"]}</strong>'
                            f'{"  –  " + blk["label"] if blk.get("label") else ""}'
                            f'  ·  <span style="font-family:\'DM Mono\',monospace;">'
                            f'{blk["von"]} – {blk["bis"]}</span></div>',
                            unsafe_allow_html=True,
                        )
                    with dc:
                        if st.button("✕", key=f"del_{tag}_{i}"):
                            st.session_state.wochen_bloecke[tag].pop(i)
                            st.rerun()

            with st.form(f"bf_{tag}", clear_on_submit=True):
                st.markdown("**Aktivität hinzufügen**")
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
                    lbl = st.text_input("Bezeichnung (optional)",
                                        placeholder="z. B. Statistik-VL …", key=f"l_{tag}")
                hinzu = st.form_submit_button("➕  Hinzufügen", use_container_width=True)

            if hinzu:
                try:
                    vm, bm = zeit_zu_min(von_s.strip()), zeit_zu_min(bis_s.strip())
                    if bm <= vm:
                        raise ValueError("Endzeit muss nach Startzeit liegen.")
                    st.session_state.wochen_bloecke[tag].append({
                        "typ": typ, "von": von_s.strip(), "bis": bis_s.strip(),
                        "label": lbl.strip() if lbl.strip() else typ,
                    })
                    st.rerun()
                except Exception as exc:
                    st.error(f"Ungültige Zeit: {exc}  (Format: HH:MM)")

# ── TAB 3: KALENDER ───────────────────────────────────────────────────────────
with tab_kalender:
    pruefungen_aktuell = alle_pruefungen_laden()

    # Metriken (im ss-card Stil)
    st.markdown('<div class="ss-card">', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.markdown(f'<div class="metric-tile"><div class="label">Prüfungen</div>'
                f'<div class="value">{len(pruefungen_aktuell)}</div></div>',
                unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-tile"><div class="label">Aktivitäts-Blöcke</div>'
                f'<div class="value">'
                f'{sum(len(v) for v in st.session_state.wochen_bloecke.values())}'
                f'</div></div>', unsafe_allow_html=True)

    if pruefungen_aktuell:
        naechste = min(pruefungen_aktuell, key=lambda p: p["datum"])
        tage_n   = (date.fromisoformat(naechste["datum"]) - date.today()).days
        farbe_n  = "#f44336" if tage_n < 14 else "#f59e0b" if tage_n < 28 else "#96ad00"
        m3.markdown(
            f'<div class="metric-tile"><div class="label">Nächste Prüfung</div>'
            f'<div class="value" style="font-size:14px;">{naechste["fach"]}</div>'
            f'<div style="font-size:12px;color:{farbe_n};font-family:\'DM Mono\',monospace;'
            f'margin-top:4px;">in {tage_n} Tagen</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    if not pruefungen_aktuell:
        st.markdown(
            '<div class="ss-card" style="text-align:center;padding:40px;">'
            '<div style="font-size:32px;">📋</div>'
            '<div style="font-size:15px;font-weight:600;color:#1a1a1a;margin:8px 0 4px;">Keine Prüfungen</div>'
            '<div style="font-size:13px;color:#888880;">Trage zuerst eine Prüfung im Tab <strong>Prüfungen</strong> ein.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        tages_daten = lernplan_generieren(
            pruefungen_aktuell,
            st.session_state.wochen_bloecke,
            st.session_state.pendelzeit_min,
            max_block=max_block_min,
            pause=pflicht_pause,
        )

        # Tages-Zusammenfassung (7 Kacheln)
        heute_datum = date.today()
        summary_cols = st.columns(7)
        for offset, col in enumerate(summary_cols):
            tag_datum   = heute_datum + timedelta(days=offset)
            wochentag   = WOCHENTAGE[tag_datum.weekday()]
            lern_min    = sum(
                zeit_zu_min(b["bis"]) - zeit_zu_min(b["von"])
                for b in tages_daten.get(wochentag, []) if b["typ"] == "Lernen"
            )
            lern_std    = lern_min / 60
            ist_heute   = (offset == 0)
            bg_karte    = "#eef3c2" if ist_heute else "#ffffff"
            rand_karte  = "#b5cc18" if ist_heute else "#e0e0dc"
            txt_farbe   = "#96ad00" if ist_heute else "#888880"
            col.markdown(
                f'<div style="background:{bg_karte};border:2px solid {rand_karte};'
                f'border-radius:12px;padding:12px 6px;text-align:center;">'
                f'<div style="font-size:11px;font-family:\'DM Mono\',monospace;'
                f'letter-spacing:0.06em;color:{txt_farbe};text-transform:uppercase;">'
                f'{wochentag[:2]}</div>'
                f'<div style="font-size:22px;font-weight:700;font-family:\'DM Mono\',monospace;'
                f'color:#1a1a1a;line-height:1.2;">{lern_std:.1f}</div>'
                f'<div style="font-size:10px;color:#888880;">Std.</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Kalender
        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        st.markdown(kalender_als_html(tages_daten, heute_datum), unsafe_allow_html=True)

        # Legende
        akt_leg = " &nbsp; ".join(
            f'<span style="background:{bg};border-radius:6px;padding:3px 9px;'
            f'font-size:11px;color:{tx};font-weight:500;">{em} {typ}</span>'
            for typ, (bg, _, tx, em) in AKTIVITAET_FARBEN.items()
        )
        fach_leg = " &nbsp; ".join(
            f'<span style="background:{FACH_PALETTE[idx][0]};border-radius:6px;'
            f'padding:3px 9px;font-size:11px;color:{FACH_PALETTE[idx][2]};font-weight:500;">'
            f'📖 {fach}</span>'
            for fach, idx in st.session_state.fach_farb_map.items()
        )
        st.markdown(
            f'<div style="background:#ffffff;border:1px solid #e0e0dc;border-radius:12px;'
            f'padding:12px 16px;margin-top:12px;">'
            f'<div style="font-size:10px;font-family:\'DM Mono\',monospace;'
            f'letter-spacing:0.08em;text-transform:uppercase;color:#888880;margin-bottom:8px;">Legende</div>'
            f'<div>{akt_leg}</div>'
            f'<div style="margin-top:6px;">{fach_leg}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        total_lern = sum(
            zeit_zu_min(b["bis"]) - zeit_zu_min(b["von"])
            for v in tages_daten.values() for b in v if b["typ"] == "Lernen"
        )
        if total_lern == 0:
            st.warning("Keine freie Lernzeit gefunden. Prüfe die Aktivitäts-Blöcke im Tab **Woche planen**.")

# ── Fußzeile ──────────────────────────────────────────────────────────────────
st.divider()
st.caption("Studyscore · Lernplan · Powered by Streamlit & SQLite")
