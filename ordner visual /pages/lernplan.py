import sys
sys.path.append("../")  # Searches for databases_sql.py in the parent folder

import streamlit as st
from datetime import date, timedelta
from databases_sql import init_db, add_pruefung, get_pruefungen, delete_pruefung

init_db()

st.title("Lernplan")
st.divider()

# ==============================
# LOGIN CHECK
# ==============================

if "user_id" not in st.session_state:
    st.warning("Bitte logge dich zuerst auf der Homepage-Seite ein.")
    st.stop()

user_id = st.session_state["user_id"]

# ==============================
# ENTER EXAMS
# ==============================

st.subheader("Deine Prüfungen")
st.caption("Trage hier deine Prüfungen ein. 1 ECTS = 30 Stunden Lernaufwand.")

with st.form("pruefung_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        fach = st.text_input("Fach")
    with col2:
        datum = st.date_input("Datum", min_value=date.today())
    with col3:
        ects = st.number_input("ECTS", min_value=1, max_value=10, value=3)
    submitted = st.form_submit_button("Prüfung hinzufügen")
    if submitted and fach.strip() != "":
        add_pruefung(user_id, fach, str(datum), ects)
        st.success(f"{fach} wurde hinzugefügt!")
        st.rerun()

# Load exams from database
pruefungen = get_pruefungen(user_id)

if not pruefungen:
    st.info("Noch keine Prüfungen eingetragen.")
    st.stop()

heute = date.today()

# Sort exams by date, most urgent first
pruefungen_sortiert = sorted(pruefungen, key=lambda x: date.fromisoformat(x[3]))

# Show exams with delete button
for p in pruefungen_sortiert:
    pruefung_id, uid, fach_name, datum_str, ects_val = p
    pruefungs_datum = date.fromisoformat(datum_str)
    tage_bis = (pruefungs_datum - heute).days
    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
    with col1:
        st.write(f"**{fach_name}**")
    with col2:
        st.write(pruefungs_datum.strftime("%d.%m.%Y"))
    with col3:
        st.write(f"{tage_bis} Tage")
    with col4:
        if st.button("Löschen", key=f"del_{pruefung_id}"):
            delete_pruefung(pruefung_id)
            st.rerun()

st.divider()

# ==============================
# EXAM OVERVIEW
# ==============================

st.subheader("Übersicht deiner Prüfungen")

def berechne_status(tage_bis):
    """Returns urgency status based on days remaining until exam."""
    if tage_bis <= 0:
        return "Vorbei"
    elif tage_bis <= 7:
        return "Dringend"
    elif tage_bis <= 21:
        return "Bald"
    else:
        return "Gut geplant"

def berechne_farbe(tage_bis):
    """Returns a color based on urgency."""
    if tage_bis <= 0:
        return "gray"
    elif tage_bis <= 7:
        return "red"
    elif tage_bis <= 21:
        return "orange"
    else:
        return "green"

for p in pruefungen_sortiert:
    pruefung_id, uid, fach_name, datum_str, ects_val = p
    pruefungs_datum = date.fromisoformat(datum_str)
    tage_bis = (pruefungs_datum - heute).days
    status = berechne_status(tage_bis)
    farbe = berechne_farbe(tage_bis)

    col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
    with col1:
        st.write(f"**{fach_name}**")
    with col2:
        st.write(pruefungs_datum.strftime("%d.%m.%Y"))
    with col3:
        st.write(f"{tage_bis} Tage")
    with col4:
        st.write(f"{ects_val} ECTS")
    with col5:
        # Show colored status badge
        st.markdown(
            f"<span style='background-color:{farbe}; color:white; padding:3px 8px; border-radius:5px; font-size:12px;'>{status}</span>",
            unsafe_allow_html=True
        )

st.divider()

# ==============================
# DAILY RECOMMENDATION
# ==============================

st.subheader("Was lernst du heute?")
st.write(f"**{heute.strftime('%A, %d.%m.%Y')}**")
st.write("")

def berechne_stunden_heute(noch_stunden, tage_bis):
    """
    Calculates recommended study hours for today.
    Distributes remaining hours evenly across remaining days.
    Minimum 0.5h, maximum 4h per subject per day.
    """
    if tage_bis <= 0:
        return 0
    stunden = round(noch_stunden / tage_bis, 1)
    return max(0.5, min(stunden, 4.0))

hat_empfehlung = False
for p in pruefungen_sortiert:
    pruefung_id, uid, fach_name, datum_str, ects_val = p
    pruefungs_datum = date.fromisoformat(datum_str)
    tage_bis = (pruefungs_datum - heute).days
    if tage_bis <= 0:
        continue

    # 1 ECTS = 30 hours total study time
    noch_stunden = ects_val * 30
    stunden_heute = berechne_stunden_heute(noch_stunden, tage_bis)

    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        st.write(f"**{fach_name}**")
    with col2:
        st.write(f"{stunden_heute}h heute")
    with col3:
        st.write(f"Prüfung in {tage_bis} Tagen")
    hat_empfehlung = True

if hat_empfehlung:
    st.write("")
    st.info("Tipp: Lerne in 90 Minuten Blöcken mit 15 Minuten Pause dazwischen.")
else:
    st.success("Keine anstehenden Prüfungen. Gut gemacht!")

st.divider()

# ==============================
# PROGRESS BARS
# ==============================

st.subheader("Dein Fortschritt")
st.caption("Wie viel Zeit noch bis zu deinen Prüfungen bleibt.")

def motivations_text(tage_bis):
    """Returns a motivating message based on days remaining until exam."""
    if tage_bis <= 0:
        return "Prüfung vorbei"
    elif tage_bis <= 7:
        return f"Nur noch {tage_bis} Tage! Jetzt alles geben."
    elif tage_bis <= 21:
        return f"Noch {tage_bis} Tage. Regelmässig lernen zahlt sich aus."
    else:
        return f"Noch {tage_bis} Tage. Früh anfangen lohnt sich."

for p in pruefungen_sortiert:
    pruefung_id, uid, fach_name, datum_str, ects_val = p
    pruefungs_datum = date.fromisoformat(datum_str)
    tage_bis = (pruefungs_datum - heute).days

    # Progress bar fills up as exam approaches
    # Reference window of 90 days
    referenz_tage = 90
    if tage_bis <= 0:
        fortschritt = 1.0
    else:
        fortschritt = max(0.0, min(1.0, 1 - (tage_bis / referenz_tage)))

    col1, col2 = st.columns([1, 3])
    with col1:
        st.write(f"**{fach_name}**")
        st.write(f"{ects_val} ECTS")
        st.write(f"{tage_bis} Tage noch")
    with col2:
        st.progress(fortschritt)
        st.caption(motivations_text(tage_bis))
