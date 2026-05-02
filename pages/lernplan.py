import streamlit as st
from datetime import date, timedelta, datetime, time
from databases_sql import init_db, add_pruefung, get_pruefungen, delete_pruefung, add_zeitfenster, get_zeitfenster, delete_zeitfenster
import pandas as pd

init_db()

st.title("Lernplan")
st.divider()

# Prüfen ob der Benutzer eingelogggt ist
if "user_id" not in st.session_state:
    st.warning("Bitte logge dich zuerst auf der Score-Seite ein.")
    st.stop()

user_id = st.session_state["user_id"]

# PRÜFUNGEN EINGEBEN
st.subheader("Deine Prüfungen")

with st.form("pruefung_form"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        fach = st.text_input("Fach")
    with col2:
        datum = st.date_input("Datum", min_value=date.today())
    with col3:
        ects = st.number_input("ECTS", min_value=1, max_value=10, value=3)
    with col4:
        # Bereits gelernte Stunden abziehen damit der Plan realistisch ist
        bereits = st.number_input("Bereits gelernte Stunden", min_value=0, max_value=300, value=0)
    submitted = st.form_submit_button("Prüfung hinzufügen")
    if submitted and fach.strip() != "":
        add_pruefung(user_id, fach, str(datum), ects)
        if "bereits_stunden" not in st.session_state:
            st.session_state["bereits_stunden"] = {}
        st.session_state["bereits_stunden"][fach] = bereits
        st.success(f"{fach} wurde hinzugefügt!")
        st.rerun()

# Gespeicherte Prüfungen anzeigen
pruefungen = get_pruefungen(user_id)
if pruefungen:
    if "bereits_stunden" not in st.session_state:
        st.session_state["bereits_stunden"] = {}
    for p in pruefungen:
        pruefung_id, uid, fach_name, datum_str, ects_val = p
        bereits_val = st.session_state["bereits_stunden"].get(fach_name, 0)
        # 1 ECTS = 30 Stunden Lernaufwand
        noch_stunden = max(0, ects_val * 30 - bereits_val)
        col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 2, 1])
        with col1:
            st.write(fach_name)
        with col2:
            st.write(datum_str)
        with col3:
            st.write(f"{ects_val} ECTS")
        with col4:
            st.write(f"Noch {noch_stunden}h zu lernen")
        with col5:
            if st.button("Löschen", key=f"del_p_{pruefung_id}"):
                delete_pruefung(pruefung_id)
                st.rerun()
else:
    st.info("Noch keine Prüfungen eingetragen.")

st.divider()

# ZEITFENSTER EINGEBEN 
st.subheader("Wann kannst du nicht lernen?")
st.caption("z.B. Vorlesungen, Sport, Private Aktivitäten")

wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

with st.form("zeitfenster_form"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        wochentag = st.selectbox("Tag", wochentage)
    with col2:
        von = st.time_input("Von", value=time(8, 0))
    with col3:
        bis = st.time_input("Bis", value=time(10, 0))
    with col4:
        beschreibung = st.text_input("Was? (z.B. Vorlesung)")
    submitted2 = st.form_submit_button("Zeitfenster hinzufügen")
    if submitted2:
        add_zeitfenster(user_id, wochentag, str(von), str(bis), beschreibung)
        st.success("Zeitfenster gespeichert!")
        st.rerun()

# Gespeicherte Zeitfenster anzeigen
zeitfenster = get_zeitfenster(user_id)
if zeitfenster:
    for z in zeitfenster:
        zf_id, uid, tag, von_str, bis_str, beschr = z
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        with col1:
            st.write(tag)
        with col2:
            st.write(f"{von_str} – {bis_str}")
        with col3:
            st.write(beschr if beschr else "—")
        with col4:
            if st.button("Löschen", key=f"del_z_{zf_id}"):
                delete_zeitfenster(zf_id)
                st.rerun()
else:
    st.info("Noch keine Zeitfenster eingetragen.")

st.divider()

# LERNZEITEN FESTLEGEN 
st.subheader("Deine Lernzeiten")
col1, col2 = st.columns(2)
with col1:
    start_uhr = st.time_input("Lernen ab", value=time(8, 0))
with col2:
    end_uhr = st.time_input("Lernen bis", value=time(20, 0))

st.divider()

# HILFSFUNKTION OB EIN ZEITFENSTER GESPERRT IST
def ist_gesperrt(tag_datum, von_uhr, bis_uhr, zeitfenster_liste):
    wochentag_name = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"][tag_datum.weekday()]
    for z in zeitfenster_liste:
        zf_id, uid, tag, zf_von, zf_bis, beschr = z
        if tag == wochentag_name:
            # Zeitstrings in Zeitobjekte umwandeln
            try:
                zf_von_t = datetime.strptime(zf_von, "%H:%M:%S").time()
                zf_bis_t = datetime.strptime(zf_bis, "%H:%M:%S").time()
            except:
                zf_von_t = datetime.strptime(zf_von, "%H:%M").time()
                zf_bis_t = datetime.strptime(zf_bis, "%H:%M").time()
            # Überschneidung prüfen
            if von_uhr < zf_bis_t and bis_uhr > zf_von_t:
                return True
    return False

# HILFSFUNKTION UM NÄCHSTEN FREIEN SLOT ZU FINDEN
def finde_freien_slot(tag_datum, belegte_slots, zeitfenster_liste, start_uhr, end_uhr):
    block_min = 90  # Ein Lernblock = 90 Minuten
    pause_min = 15  # Pause zwischen Blöcken = 15 Minuten
    aktuell = datetime.combine(tag_datum, start_uhr)
    end_dt = datetime.combine(tag_datum, end_uhr)

    while aktuell + timedelta(minutes=block_min) <= end_dt:
        block_ende = aktuell + timedelta(minutes=block_min)

        # Prüfen ob dieser Slot gesperrt ist
        if ist_gesperrt(tag_datum, aktuell.time(), block_ende.time(), zeitfenster_liste):
            aktuell += timedelta(minutes=30)
            continue

        # Prüfen ob dieser Slot schon belegt ist
        konflikt = False
        for bvon, bbis in belegte_slots:
            if aktuell < bbis and block_ende > bvon:
                konflikt = True
                aktuell = bbis + timedelta(minutes=pause_min)
                break

        if not konflikt:
            return aktuell, block_ende

    return None, None

#  LERNPLAN GENERIEREN
if st.button("Lernplan erstellen"):
    pruefungen = get_pruefungen(user_id)
    zeitfenster_liste = get_zeitfenster(user_id)

    if not pruefungen:
        st.warning("Bitte zuerst Prüfungen eintragen.")
        st.stop()

    heute = date.today()

    # Farbe pro Fach damit man sie in der Tabelle unterscheiden kann
    farben = ["#AED6F1", "#A9DFBF", "#F9E79F", "#F5CBA7", "#D2B4DE", "#F1948A"]
    fach_farben = {}
    for idx, p in enumerate(pruefungen):
        fach_farben[p[2]] = farben[idx % len(farben)]

    if "bereits_stunden" not in st.session_state:
        st.session_state["bereits_stunden"] = {}

    # Für jede Prüfung berechnen wie viele Lernblöcke noch nötig sind
    fach_info = {}
    for p in pruefungen:
        pruefung_id, uid, fach_name, datum_str, ects_val = p
        pruefungs_datum = date.fromisoformat(datum_str)
        tage_bis = (pruefungs_datum - heute).days
        if tage_bis <= 0:
            continue
        bereits_val = st.session_state["bereits_stunden"].get(fach_name, 0)
        # 1 ECTS = 30 Stunden, 1 Block = 1.5 Stunden
        noch_stunden = max(0, ects_val * 30 - bereits_val)
        noch_bloecke = round(noch_stunden / 1.5)
        fach_info[fach_name] = {
            "datum": pruefungs_datum,
            "tage_bis": tage_bis,
            "bloecke": noch_bloecke,
            "ects": ects_val
        }

    if not fach_info:
        st.warning("Alle Prüfungsdaten liegen in der Vergangenheit.")
        st.stop()

    # Zusammenfassung anzeigen
    st.markdown("**Zusammenfassung:**")
    for fach_name, info in fach_info.items():
        bereits_val = st.session_state["bereits_stunden"].get(fach_name, 0)
        noch_stunden = max(0, info["ects"] * 30 - bereits_val)
        st.write(f"**{fach_name}**: noch {noch_stunden}h bis {info['datum'].strftime('%d.%m.%Y')} ({info['tage_bis']} Tage)")
    st.write("")

    # Legende: Welche Farbe gehört zu welchem Fach
    st.markdown("**Legende:**")
    leg_cols = st.columns(len(fach_farben))
    for idx, (fn, farbe) in enumerate(fach_farben.items()):
        with leg_cols[idx]:
            st.markdown(f"<span style='background-color:{farbe}; padding:4px 10px; border-radius:5px;'>{fn}</span>", unsafe_allow_html=True)
    st.write("")

    # Plan aufbauen: für jeden Tag bis zur letzten Prüfung
    # verteilen  die Lernblöcke auf die verfügbaren Zeitslots
    letzte_pruefung = max(info["datum"] for info in fach_info.values())
    tage_total = (letzte_pruefung - heute).days
    plan = {}  # plan[datum] = liste von (fach, von, bis, farbe)
    verbleibend = {f: info["bloecke"] for f, info in fach_info.items()}

    for i in range(tage_total):
        lern_tag = heute + timedelta(days=i)
        plan[lern_tag] = []
        belegte_slots = []

        # Fächer mit nahender Prüfung zuerst einplanen
        heutige_faecher = []
        for fach_name, info in fach_info.items():
            tage_bis_pruefung = (info["datum"] - lern_tag).days
            if tage_bis_pruefung <= 0 or verbleibend[fach_name] <= 0:
                continue
            heutige_faecher.append((fach_name, tage_bis_pruefung))
        heutige_faecher.sort(key=lambda x: x[1])

        # Maximal 4 Blöcke pro Tag = ca. 6 Stunden
        max_bloecke = 4
        bloecke_heute = 0

        for fach_name, tage_bis_pruefung in heutige_faecher:
            if bloecke_heute >= max_bloecke:
                break
            if verbleibend[fach_name] <= 0:
                continue

            # Je näher die Prüfung desto mehr Blöcke pro Tag
            if tage_bis_pruefung <= 7:
                bloecke_fach = min(3, verbleibend[fach_name])
            elif tage_bis_pruefung <= 14:
                bloecke_fach = min(2, verbleibend[fach_name])
            else:
                # Weit weg: gleichmässig über die verbleibenden Tage verteilen
                bloecke_fach = min(
                    max(1, round(verbleibend[fach_name] / tage_bis_pruefung)),
                    2, verbleibend[fach_name]
                )

            for _ in range(bloecke_fach):
                if bloecke_heute >= max_bloecke:
                    break
                # Nächsten freien Zeitslot suchen
                von_dt, bis_dt = finde_freien_slot(
                    lern_tag, belegte_slots, zeitfenster_liste, start_uhr, end_uhr
                )
                if von_dt:
                    plan[lern_tag].append((fach_name, von_dt, bis_dt, fach_farben[fach_name]))
                    belegte_slots.append((von_dt, bis_dt))
                    verbleibend[fach_name] -= 1
                    bloecke_heute += 1

    # WOCHENPLAN 
    hat_eintraege = any(plan[t] for t in plan)
    if not hat_eintraege:
        st.info("Keine Lernblöcke gefunden.")
        st.stop()

    alle_tage = sorted(plan.keys())
    woche_start = alle_tage[0] - timedelta(days=alle_tage[0].weekday())
    letzter_tag = alle_tage[-1]

    while woche_start <= letzter_tag:
        woche_tage = [woche_start + timedelta(days=i) for i in range(7)]
        woche_ende = woche_tage[-1]

        hat_woche_eintraege = any(plan.get(t) for t in woche_tage)
        if not hat_woche_eintraege:
            woche_start += timedelta(weeks=1)
            continue

        st.markdown(f"**Woche {woche_start.strftime('%d.%m.')} – {woche_ende.strftime('%d.%m.')}**")

        # Alle Startzeiten sammeln damit die Tabelle nur relevante Zeilen hat
        relevante_zeiten = set()
        for tag in woche_tage:
            for _, von_dt, bis_dt, _ in plan.get(tag, []):
                relevante_zeiten.add(von_dt.time())

        # Volle Stunden immer anzeigen damit die Tabelle lesbar bleibt
        t = datetime.combine(date.today(), start_uhr)
        while t <= datetime.combine(date.today(), end_uhr):
            relevante_zeiten.add(t.time())
            t += timedelta(hours=1)

        zeitslots = sorted(relevante_zeiten)

        # Tabellenkopf
        tagnamen = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        header = ["Zeit"] + [f"{tagnamen[d.weekday()]} {d.strftime('%d.%m.')}" for d in woche_tage]

        # Tabellenzeilen befüllen
        zeilen = []
        for slot in zeitslots:
            zeile = [slot.strftime("%H:%M")]
            hat_inhalt = False
            for tag in woche_tage:
                zelle = ""
                for fach_name, von_dt, bis_dt, farbe in plan.get(tag, []):
                    if von_dt.time() == slot:
                        zelle = f"{fach_name} ({von_dt.strftime('%H:%M')}–{bis_dt.strftime('%H:%M')})"
                        hat_inhalt = True
                zeile.append(zelle)
            # Nur Zeilen anzeigen die Inhalt haben oder volle Stunden sind
            if hat_inhalt or slot.minute == 0:
                zeilen.append(zeile)

        df = pd.DataFrame(zeilen, columns=header)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.write("")

        woche_start += timedelta(weeks=1)
