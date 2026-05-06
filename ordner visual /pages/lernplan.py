#==========
# LERNPLAN
#==========


#==================================
# IMPORT AND DATABASE INITIALIZATION
#==================================

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from datetime import date, timedelta

import streamlit as st

from databases_sql import (
    init_db,
    add_pruefung,
    get_pruefungen,
    delete_pruefung
)

init_db()


#================
# PAGE TITLE
#================

col81, col82 = st.columns(2)

with col81:
    st.image("https://i.pinimg.com/736x/93/e9/2a/93e92aa415afeeb20ba87af61eb98a8d.jpg", width = 300)
with col82:
    st.image("https://i.pinimg.com/736x/2e/a9/26/2ea926c768ccd98cbd60323f204a77bc.jpg", width = 300)

st.title("Lernplan")
st.write("Hier kannst du deine Prüfungen eintragen und deinen Lernplan bis zur Prüfung erstellen.")
st.divider()

#================
# SIDEBAR
#================

with st.sidebar:
    st.write("Viel Erfolg beim Lernen!")


#================
# LOGIN CHECK
#================

if "user_id" not in st.session_state:
    st.warning("Bitte logge dich zuerst auf der Homepage ein.")
    st.stop()

user_id = st.session_state["user_id"]


#=========================
# INITIALIZE SESSION STATE
#=========================

# Progress is saved temporarily while the app is running
if "exam_progress" not in st.session_state:
    st.session_state["exam_progress"] = {}

# Free dates are also saved temporarily
if "freie_daten" not in st.session_state:
    st.session_state["freie_daten"] = []

# This variable saves which day is currently shown
if "study_day_index" not in st.session_state:
    st.session_state["study_day_index"] = 0


#================
# ADD EXAMS
#================

st.subheader("Deine Prüfungen")
st.caption("Trage deine Prüfungen ein. 1 ECTS entspricht ungefähr 30 Stunden Lernaufwand.")

with st.form("exam_form"):

    col1, col2, col3 = st.columns(3)

    with col1:
        fach = st.text_input("Fach")

    with col2:
        datum = st.date_input("Prüfungsdatum", min_value=date.today())

    with col3:
        ects = st.number_input("ECTS", min_value=1, max_value=10, value=3)

    fortschritt = st.selectbox(
        "Wie weit bist du schon?",
        (
            "Noch nicht begonnen",
            "Etwas gemacht",
            "Ungefähr die Hälfte",
            "Fast fertig",
            "Nur noch Wiederholung"
        )
    )

    submitted = st.form_submit_button("Prüfung hinzufügen")

    if submitted:
        if fach.strip() == "":
            st.warning("Bitte gib ein Fach ein.")
        else:
            add_pruefung(user_id, fach, str(datum), ects)

            # Save progress with subject and date as key
            progress_key = f"{fach}_{datum}"
            st.session_state["exam_progress"][progress_key] = fortschritt

            st.success(f"{fach} wurde hinzugefügt!")
            st.rerun()


#================
# LOAD EXAMS
#================

pruefungen = get_pruefungen(user_id)

if not pruefungen:
    st.info("Noch keine Prüfungen eingetragen.")
    st.stop()

today = date.today()

# Sort exams by date
pruefungen_sortiert = sorted(
    pruefungen,
    key=lambda x: date.fromisoformat(x[3])
)

last_exam_date = max(
    date.fromisoformat(p[3])
    for p in pruefungen_sortiert
)


#================
# FREE DATES
#================

st.divider()
st.subheader("Freie Tage")

st.write("Wähle Daten aus, an denen du nicht lernen kannst.")

possible_dates = []
current_day = today

while current_day <= last_exam_date:
    possible_dates.append(current_day)
    current_day = current_day + timedelta(days=1)

freie_daten = st.multiselect(
    "Nicht verfügbare Tage",
    possible_dates,
    default=st.session_state["freie_daten"],
    format_func=lambda x: x.strftime("%d.%m.%Y")
)

st.session_state["freie_daten"] = freie_daten


#================
# EXAM OVERVIEW
#================

st.divider()
st.subheader("Übersicht deiner Prüfungen")

for p in pruefungen_sortiert:

    pruefung_id, uid, fach_name, datum_str, ects_val = p

    exam_date = date.fromisoformat(datum_str)
    days_left = (exam_date - today).days

    progress_key = f"{fach_name}_{exam_date}"

    if progress_key in st.session_state["exam_progress"]:
        progress_text = st.session_state["exam_progress"][progress_key]
    else:
        progress_text = "Noch nicht begonnen"

    # Calculate total hours
    total_hours = ects_val * 30

    # Reduce total hours depending on progress
    if progress_text == "Noch nicht begonnen":
        remaining_hours = total_hours
    elif progress_text == "Etwas gemacht":
        remaining_hours = total_hours * 0.75
    elif progress_text == "Ungefähr die Hälfte":
        remaining_hours = total_hours * 0.5
    elif progress_text == "Fast fertig":
        remaining_hours = total_hours * 0.25
    else:
        remaining_hours = total_hours * 0.1

    remaining_hours = round(remaining_hours, 1)

    col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 1, 1, 2, 1])

    with col1:
        st.write(f"**{fach_name}**")

    with col2:
        st.write(exam_date.strftime("%d.%m.%Y"))

    with col3:
        st.write(f"{days_left} Tage")

    with col4:
        st.write(f"{ects_val} ECTS")

    with col5:
        st.write(f"{remaining_hours} h offen")

    with col6:
        if st.button("Löschen", key=f"delete_{pruefung_id}"):
            delete_pruefung(pruefung_id)
            st.rerun()


#=======================
# STUDY PLAN NAVIGATION
#=======================

st.divider()
st.subheader("Dein Lernplan")

total_days = (last_exam_date - today).days + 1

if total_days <= 0:
    st.success("Alle Prüfungen sind vorbei.")
    st.stop()

if st.session_state["study_day_index"] >= total_days:
    st.session_state["study_day_index"] = total_days - 1

day_index = st.session_state["study_day_index"]
selected_day = today + timedelta(days=day_index)

col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("← Zurück"):
        if day_index > 0:
            st.session_state["study_day_index"] = st.session_state["study_day_index"] - 1
            st.rerun()

with col2:
    st.markdown(
        f"<h3 style='text-align:center;'>Tag {day_index + 1} von {total_days}</h3>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<p style='text-align:center;'>{selected_day.strftime('%d.%m.%Y')}</p>",
        unsafe_allow_html=True
    )

with col3:
    if st.button("Weiter →"):
        if day_index < total_days - 1:
            st.session_state["study_day_index"] = st.session_state["study_day_index"] + 1
            st.rerun()


#================
# DAILY STUDY PLAN
#================

st.divider()

total_hours_today = 0

if selected_day in freie_daten:

    st.info("Dieser Tag ist als freier Tag eingeplant.")

else:

    for p in pruefungen_sortiert:

        pruefung_id, uid, fach_name, datum_str, ects_val = p

        exam_date = date.fromisoformat(datum_str)
        days_left = (exam_date - selected_day).days

        if days_left <= 0:
            continue

        progress_key = f"{fach_name}_{exam_date}"

        if progress_key in st.session_state["exam_progress"]:
            progress_text = st.session_state["exam_progress"][progress_key]
        else:
            progress_text = "Noch nicht begonnen"

        total_hours = ects_val * 30

        # Calculate remaining hours with simple if rules
        if progress_text == "Noch nicht begonnen":
            remaining_hours = total_hours
        elif progress_text == "Etwas gemacht":
            remaining_hours = total_hours * 0.75
        elif progress_text == "Ungefähr die Hälfte":
            remaining_hours = total_hours * 0.5
        elif progress_text == "Fast fertig":
            remaining_hours = total_hours * 0.25
        else:
            remaining_hours = total_hours * 0.1

        remaining_hours = round(remaining_hours, 1)

        # Count available study days until this exam
        available_days = 0
        current_day = selected_day

        while current_day < exam_date:
            if current_day not in freie_daten:
                available_days = available_days + 1

            current_day = current_day + timedelta(days=1)

        if available_days == 0:
            available_days = 1

        daily_hours = remaining_hours / available_days

        # Make the daily learning time more realistic
        if daily_hours < 0.5:
            daily_hours = 0.5
        elif daily_hours > 3:
            daily_hours = 3
        else:
            daily_hours = round(daily_hours, 1)

        total_hours_today = total_hours_today + daily_hours

        with st.container(border=True):

            st.markdown(f"### {fach_name}")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write("**Lernzeit heute**")
                st.write(f"{daily_hours} h")

            with col2:
                st.write("**Prüfung in**")
                st.write(f"{days_left} Tagen")

            with col3:
                st.write("**Offene Stunden**")
                st.write(f"{remaining_hours} h")

            st.caption(f"{available_days} verfügbare Lerntage")


#================
# RECOMMENDATION
#================

st.divider()
st.subheader("Empfehlung")

if selected_day in freie_daten:
    st.success("Heute ist ein freier Tag. Erholung gehört dazu.")

else:
    if total_hours_today <= 2:
        st.info("Heute ist ein leichter Lerntag.")

    elif total_hours_today <= 4:
        st.info("Heute ist ein realistischer Lerntag.")

    elif total_hours_today <= 6:
        st.warning("Heute ist viel eingeplant. Plane genügend Pausen ein.")

    else:
        st.error("Der Plan ist unrealistisch. Du hättest früher beginnen sollen.")


#================
# SUMMARY
#================

st.divider()
st.subheader("Zusammenfassung")

for p in pruefungen_sortiert:

    pruefung_id, uid, fach_name, datum_str, ects_val = p

    exam_date = date.fromisoformat(datum_str)

    progress_key = f"{fach_name}_{exam_date}"

    if progress_key in st.session_state["exam_progress"]:
        progress_text = st.session_state["exam_progress"][progress_key]
    else:
        progress_text = "Noch nicht begonnen"

    total_hours = ects_val * 30

    if progress_text == "Noch nicht begonnen":
        remaining_hours = total_hours
    elif progress_text == "Etwas gemacht":
        remaining_hours = total_hours * 0.75
    elif progress_text == "Ungefähr die Hälfte":
        remaining_hours = total_hours * 0.5
    elif progress_text == "Fast fertig":
        remaining_hours = total_hours * 0.25
    else:
        remaining_hours = total_hours * 0.1

    remaining_hours = round(remaining_hours, 1)

    available_days = 0
    current_day = today

    while current_day < exam_date:
        if current_day not in freie_daten:
            available_days = available_days + 1

        current_day = current_day + timedelta(days=1)

    if available_days == 0:
        available_days = 1

    daily_hours = remaining_hours / available_days

    if daily_hours < 0.5:
        daily_hours = 0.5
    elif daily_hours > 3:
        daily_hours = 3
    else:
        daily_hours = round(daily_hours, 1)

    st.write(f"**{fach_name}**")
    st.caption(
        f"Noch ca. {remaining_hours} Stunden "
        f"auf {available_days} Lerntage verteilt. "
        f"Empfohlen: ca. {daily_hours} h pro Lerntag."
    )
