#==========
# LERNPLAN
#==========


#==================================
# IMPORT AND DATABASE INITIALIZATION
#==================================

from datetime import date, timedelta

import streamlit as st

from databases_sql import (
    init_db,
    add_pruefung,
    get_pruefungen,
    delete_pruefung
)

init_db()


# =============================================================================
# Custom CSS theme (ChatGPT)
# =============================================================================

# Originally, the application's theme was configured using the
# `.streamlit/config.toml` file.
# However, because Canvas only allow uploading
# individual files instead of complete folders, the theme settings
# were integrated directly into the Python files using CSS.

st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #faf9f9;
    font-family: serif;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #d3dbd1;
}

/* Global text */
html, body, [class*="css"], p, div, label {
    color: #22313f;
    font-family: serif !important;
}

/* Titles */
h1, h2, h3, h4 {
    color: #0d4200;
    font-family: serif !important;
}

/* Buttons */
.stButton>button {
    background-color: #f0ebe3;
    color: #22313f;
    border-radius: 10px;
    border: 1px solid #d3dbd1;
    font-family: serif;
}

/* Button hover effect */
.stButton>button:hover {
    background-color: #e4ddd2;
    color: #0d4200;
}

/* Input fields */
input, textarea {
    font-family: serif !important;
}

/* Plotly charts */
.js-plotly-plot,
.plotly,
.plot-container {
    background-color: #faf9f9 !important;
    border-radius: 15px;
}

</style>
""", unsafe_allow_html=True)



#================
# PAGE TITLE
#================

col81, col82 = st.columns(2)

with col81:
    st.image("https://i.pinimg.com/736x/93/e9/2a/93e92aa415afeeb20ba87af61eb98a8d.jpg", width=300)

with col82:
    st.image("https://i.pinimg.com/736x/2e/a9/26/2ea926c768ccd98cbd60323f204a77bc.jpg", width=300)

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

if "exam_progress" not in st.session_state:
    st.session_state["exam_progress"] = {}

if "freie_daten" not in st.session_state:
    st.session_state["freie_daten"] = []

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
            st.session_state["exam_progress"][f"{fach}_{datum}"] = fortschritt
            st.success(f"{fach} wurde hinzugefügt!")
            st.rerun()


#================
# LOAD EXAMS
#================

pruefungen = get_pruefungen(user_id)

# If the user has no exams yet the rest of the page cannot be calculated
if not pruefungen:
    st.info("Noch keine Prüfungen eingetragen.")
    st.stop()

today = date.today()

# The date is saved as text in the database so it has to be changed back into a date
def get_exam_date(pruefung):
    return date.fromisoformat(pruefung[3])

# Exams are sorted so that the next exam is shown first
pruefungen_sortiert = sorted(
    pruefungen,
    key=get_exam_date
)

# The last exam date is needed to know how far the learning plan should go
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

# This creates all dates from today until the last exam
while current_day <= last_exam_date:
    possible_dates.append(current_day)
    current_day = current_day + timedelta(days=1)

freie_daten = st.multiselect(
    "Nicht verfügbare Tage",
    possible_dates,
    default=st.session_state["freie_daten"],
    key="freie_tage_auswahl",
    placeholder="Wählen",
    format_func=lambda x: x.strftime("%d.%m.%Y")
)

st.session_state["freie_daten"] = freie_daten


#==================================
# PREPARE EXAM DATA FOR THE PAGE
#==================================

exam_infos = []

# Here the most important information for every exam is prepared once
# This makes the next parts of the page shorter and easier to read
for p in pruefungen_sortiert:

    pruefung_id, uid, fach_name, datum_str, ects_val = p
    exam_date = date.fromisoformat(datum_str)
    days_left = (exam_date - today).days

    progress_key = f"{fach_name}_{exam_date}"

    if progress_key in st.session_state["exam_progress"]:
        progress_text = st.session_state["exam_progress"][progress_key]
    else:
        progress_text = "Noch nicht begonnen"

    # 1 ECTS means 30 hours of work
    # Example: 4 ECTS means 4 * 30 = 120 hours in total
    total_hours = ects_val * 30

    # The remaining hours depend on how much the user has already studied
    # Example: "Noch nicht begonnen" means 100% of the hours are still open
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

    # All important values are saved together in one list
    exam_infos.append([
        pruefung_id,
        fach_name,
        exam_date,
        ects_val,
        days_left,
        remaining_hours
    ])


#================
# EXAM OVERVIEW
#================

st.divider()
st.subheader("Übersicht deiner Prüfungen")

for exam in exam_infos:

    pruefung_id = exam[0]
    fach_name = exam[1]
    exam_date = exam[2]
    ects_val = exam[3]
    days_left = exam[4]

    col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 2])

    with col1:
        st.write(f"**{fach_name}**")

    with col2:
        st.write(exam_date.strftime("%d.%m.%Y"))

    with col3:
        st.write(f"{days_left} Tage")

    with col4:
        st.write(f"{ects_val} ECTS")

    with col5:
        if st.button("Löschen", key=f"delete_{pruefung_id}"):
            delete_pruefung(pruefung_id)
            st.rerun()


#=======================
# STUDY PLAN NAVIGATION
#=======================

st.divider()
st.subheader("Dein Lernplan")

total_days = (last_exam_date - today).days + 1

# If all exams are in the past no future learning plan is needed
if total_days <= 0:
    st.success("Alle Prüfungen sind vorbei.")
    st.stop()

# This prevents the selected day from being outside the learning plan
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

    for exam in exam_infos:

        fach_name = exam[1]
        exam_date = exam[2]
        remaining_hours = exam[5]

        days_left = (exam_date - selected_day).days

        if days_left == 0:
            st.success(f"Viel Glück für deine Prüfung in {fach_name}!")
            continue

        if days_left < 0:
            continue

        # Count the study days from today until this exam
        # This means the plan is calculated once from today and does not get stricter on later shown days
        available_days = 0
        current_day = today

        while current_day < exam_date:
            if current_day not in freie_daten:
                available_days = available_days + 1
            current_day = current_day + timedelta(days=1)

        if available_days == 0:
            available_days = 1

        # The remaining hours are divided by all available study days
        # The result is not limited to 3 hours, so all open hours are covered
        daily_hours = remaining_hours / available_days
        daily_hours = round(daily_hours, 1)

        # Convert decimal hours into hours and minutes.
        # Example: 1.8 hours becomes 1 h 48 min.
        total_minutes = round(daily_hours * 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        daily_time = f"{hours} h {minutes} min"

        total_hours_today = total_hours_today + daily_hours

        with st.container(border=True):

            st.markdown(f"### {fach_name}")

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Lernzeit heute**")
                st.write(daily_time)

            with col2:
                st.write("**Prüfung in**")
                st.write(f"{days_left} Tagen")


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
    elif total_hours_today <= 8:
        st.warning("Heute ist viel eingeplant. Plane genügend Pausen ein.")
    else:
        st.error("Der Plan ist unrealistisch. Du hättest früher beginnen sollen.")


#=====================
# PROGRESS PER EXAM
#=====================

st.divider()
st.subheader("Fortschritt je Prüfung")

for exam in exam_infos:

    fach_name = exam[1]
    exam_date = exam[2]

    # The progress shows how far the selected day is between today and the exam
    total_days_until_exam = (exam_date - today).days
    passed_days = (selected_day - today).days

    if total_days_until_exam <= 0:
        exam_progress = 1
    else:
        exam_progress = passed_days / total_days_until_exam

    if exam_progress < 0:
        exam_progress = 0
    elif exam_progress > 1:
        exam_progress = 1

    st.write(f"**{fach_name}**")
    st.progress(exam_progress)
    st.caption(f"{round(exam_progress * 100)}% bis zur Prüfung")
