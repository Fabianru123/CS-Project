# =============================================================================
# Profile Page
# Displays the user's profile, compares their variable scores with other users,
# shows score evolution over time, and manages exam results.
# =============================================================================

import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go

from databases_sql import init_db, get_or_create_user, get_exam_results_by_user, add_exam_result, delete_exam_result

# Initialize the database before using any stored data.
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



# =============================================================================
# Sidebar: User Login
# =============================================================================

with st.sidebar:

    username = st.text_input("User Name")                    
    if st.button("Login"):
        if username.strip() == "":
            st.warning("Bitte gib einen User Name ein.")
        else:
            # Create a new user or retrieve the existing user ID.
            user_id = get_or_create_user(username)

            # Store the login information in the session state.
            st.session_state["user_id"] = user_id
            st.session_state["username"] = username

    if "user_id" in st.session_state:
        st.success(f"Erfolgreich eingeloggt als {st.session_state['username']}.")


# =============================================================================
# Page Layout
# =============================================================================

st.title("Profil")

st.divider()

st.write("Ein Überblick über deinen aktuellen Stand im Vergleich zu anderen sowie die Entwicklung deiner Performance über die Zeit.")

st.divider()


# =============================================================================
# Login Check
# =============================================================================

if "user_id" not in st.session_state:
    st.warning("Bitte logge dich zuerst ein, um deine Entwicklung zu verfolgen. ")
    st.stop()

user_id = st.session_state["user_id"]

# Load all stored input data from the database.
DB = sqlite3.connect("predicted_inputs.db")
df = pd.read_sql("SELECT * FROM input", DB)
DB.close()


# =============================================================================
# DataFrames
# =============================================================================

# Separate the current user's data from the data of all other users.
df_user = df[df["user_id"] == user_id]
df_others = df[df["user_id"] != user_id]


# =============================================================================
# Dashboard Overview
# =============================================================================

if df_user.empty:
    st.info("Noch keine Daten vorhanden. Fülle zuerst deine Angaben aus.")
else:
    # Sort the user's entries chronologically and select the latest one.
    df_user_sorted = df_user.sort_values("created_at")
    last_entry = df_user_sorted.iloc[-1]

    # Extract the latest available age and study program values.
    age_values = df_user_sorted["age"].dropna()
    studien_values = df_user_sorted["studien"].replace("", pd.NA).dropna()

    if age_values.empty:
        current_age = "-"
    else:
        current_age = int(age_values.iloc[-1])
    
    if studien_values.empty:
        current_studien = "-"
    else:
        current_studien = studien_values.iloc[-1]

    st.markdown("#### Persönliche Übersicht")

    st.markdown(f"Willkommen zurück {st.session_state['username']}!")

    # Display the main profile metrics.
    col1, col2, col3 = st.columns(3)
    col1.metric("Alter", current_age)
    col2.metric("Studiengang", current_studien)
    col3.metric("Letzter Score", f"{last_entry['score']:.1f}")
    
st.divider()


# =============================================================================
# Visualization 1: User Scores Compared with Other Users
# =============================================================================

# Calculate the user's average score for each variable.
mean_user_schlaf = df_user["pschlaf"].mean()
mean_user_lernzeit = df_user["plernzeit"].mean()
mean_user_stress = df_user["pstress"].mean()
mean_user_bild = df_user["pbild"].mean()
mean_user_gesund = df_user["pgesund"].mean()
mean_user_hilfe = df_user["philfe"].mean()
mean_user_pausen = df_user["ppausen"].mean()
mean_user_fail = df_user["pfail"].mean()
mean_user_freetime = df_user["pfreetime"].mean()
mean_user_goout = df_user["pgoout"].mean()
mean_user_pendel = df_user["ppendel"].mean()
mean_user_food = df_user["pfood"].mean()
mean_user_sport = df_user["psport"].mean()

# Calculate the average score of all other users for each variable.
mean_others_schlaf = df_others["pschlaf"].mean()
mean_others_lernzeit = df_others["plernzeit"].mean()
mean_others_stress = df_others["pstress"].mean()
mean_others_bild = df_others["pbild"].mean()
mean_others_gesund = df_others["pgesund"].mean()
mean_others_hilfe = df_others["philfe"].mean()
mean_others_pausen = df_others["ppausen"].mean()
mean_others_fail = df_others["pfail"].mean()
mean_others_freetime = df_others["pfreetime"].mean()
mean_others_goout = df_others["pgoout"].mean()
mean_others_pendel = df_others["ppendel"].mean()
mean_others_food = df_others["pfood"].mean()
mean_others_sport = df_others["psport"].mean()

# Store the calculated mean values for the chart.
values_user = [mean_user_schlaf, mean_user_lernzeit, mean_user_stress, mean_user_bild, mean_user_gesund, mean_user_hilfe, mean_user_pausen, mean_user_fail, mean_user_freetime, mean_user_goout, mean_user_pendel, mean_user_food, mean_user_sport]
values_others = [mean_others_schlaf, mean_others_lernzeit, mean_others_stress, mean_others_bild, mean_others_gesund, mean_others_hilfe, mean_others_pausen, mean_others_fail, mean_others_freetime, mean_others_goout, mean_others_pendel, mean_others_food, mean_others_sport]

# Define the variable names displayed on the x-axis.
variables_x = ["Schlaf", "Lernzeit", "Stress", "Bildschirmzeit", "Gesundheitszustand", "Nachhilfe", "Pausen", "Nicht bestandene Fächer", "Freizeit", "Ausgang", "Pendelzeit", "Ernährung", "Sport"]

# Source: ChatGPT for the structure.
fig1 = go.Figure()

# Add the user's scores as a bar chart.
fig1.add_trace(
    go.Bar(
        x = variables_x, 
        y = values_user, 
        name="Deine Daten",
        marker=dict(color="#0d4200")
        )
)

# Add the other users' scores as a line chart with markers.
fig1.add_trace(
    go.Scatter(
        x = variables_x, 
        y = values_others, 
        mode="lines+markers", 
        name="Andere",
        line=dict(color="#8a9a8b"),
        marker=dict(color="#8a9a8b")
        )
)

fig1.update_layout(
    title="Dein Vergleich mit anderen Nutzern",
    xaxis_title="Variablen",
    yaxis_title="Score"
    paper_bgcolor="#faf9f9",
    plot_bgcolor="#faf9f9",
    font=dict(
        family="serif",
        color="#22313f"
    )
)

st.plotly_chart(fig1)


# =============================================================================
# Visualization 2: Score Evolution over Time
# =============================================================================

fig2 = go.Figure()

# Sort the user's entries by creation date.
df_user_sorted = df_user.sort_values("created_at")

# Convert the timestamp to the local timezone and format it for display.
df_user_sorted["created_at"] = pd.to_datetime(df_user_sorted["created_at"])
df_user_sorted["created_at"] = df_user_sorted["created_at"].dt.tz_localize("UTC")
df_user_sorted["created_at"] = df_user_sorted["created_at"].dt.tz_convert("Europe/Zurich")
df_user_sorted["date_clean"] = df_user_sorted["created_at"].dt.strftime("%-d. %B %Y %H:%M")

# Add the user's score evolution as a line chart.
fig2.add_trace(
    go.Scatter(
        x = df_user_sorted["date_clean"],
        y = df_user_sorted["score"],
        mode = "lines+markers",
        marker=dict(color="#0d4200")
    )
)

fig2.update_layout(
    title="Entwicklung deines Scores über die Zeit",
    xaxis_title="Zeit",
    yaxis_title="Score"
    paper_bgcolor="#faf9f9",
    plot_bgcolor="#faf9f9",
    font=dict(
        family="serif",
        color="#22313f"
    )
)

st.plotly_chart(fig2)


# =============================================================================
# Exam Results
# =============================================================================

st.subheader("Prüfungsergebnisse")

st.write("Du kannst hier deine Ergebnisse eingeben, um deine Fortschritte zu verfolgen.")

# Input fields for a new exam result.
exam_name = st.text_input("Name der Prüfung")

grade = st.number_input("Deine Note", step=0.25)

ects = st.number_input("ECTS", step=0.25)

# Save the exam result after validating the input fields.
if st.button("Bestätigen"):
    if exam_name.strip() == "":
        st.warning("Bitte gib den Namen der Prüfung und die Note ein.")
    elif grade == 0:
        st.warning("Bitte gib die Note ein.")
    elif ects == 0:
        st.warning("Bitte gib die ECTS ein.")
    else:
        add_exam_result(st.session_state["user_id"], exam_name, grade, ects)
        st.success("Ergebnis gespeichert.")    

if "user_id" in st.session_state:
    # Load all exam results for the logged-in user.
    exam_data = get_exam_results_by_user(st.session_state["user_id"])

    if len(exam_data) == 0:
        st.info("Noch keine Ergebnisse vorhanden.")
    else:

        # Convert the exam results into a DataFrame.
        exam_df = pd.DataFrame(
            exam_data,
            columns=["exam_id", "user_id", "created_at", "exam_name", "grade", "ects"]
        )

        # Sort and format the exam result timestamps.
        exam_df = exam_df.sort_values("created_at")
        exam_df["created_at"] = pd.to_datetime(exam_df["created_at"])
        exam_df["created_at"] = exam_df["created_at"].dt.tz_localize("UTC")
        exam_df["created_at"] = exam_df["created_at"].dt.tz_convert("Europe/Zurich")
        exam_df["date_clean"] = exam_df["created_at"].dt.strftime("%-d. %B %Y %H:%M")

        # Calculate key exam statistics.
        nb_lines = len(exam_df)
        weighted_mean = (exam_df["grade"] * exam_df["ects"]).sum() / exam_df["ects"].sum()
        rounded_mean = round(weighted_mean, 2)
        last_grade = exam_df["grade"].iloc[-1]

        # Display the main exam result metrics.
        col1, col2, col3 = st.columns(3)
        col1.metric("Anzahl Prüfungen", nb_lines)
        col2.metric("Durchschnitt", rounded_mean)
        col3.metric("Letzte Note", last_grade)

        # ---------------------------------------------------------------------
        # Visualization 3: Exam Grades
        # ---------------------------------------------------------------------

        # Rename columns for clearer display in the chart and result list.
        exam_df = exam_df.rename(columns={
            "exam_name": "Prüfung",
            "grade": "Note",
            "date_clean": "Datum",
            "ects": "ECTS"
        })

        fig3 = go.Figure()

        # Add the exam grades as a horizontal bar chart.
        fig3.add_trace(
            go.Bar(
                x = exam_df["Note"],
                y = exam_df["Prüfung"],
                orientation = 'h',
                marker=dict(color="#8a9a8b"),
                name="Deine Noten"
            )
        )

        # Add a vertical reference line for the weighted average grade.
        fig3.add_vline(
            x=rounded_mean,
            line_dash="dash",
            line_color="#0d4200",
            annotation_text="Dein Durchschnitt",
            annotation_position="top"
        )

        fig3.update_layout(
            title = "Deine Prüfungsergebnisse im Überblick",
            xaxis_title="Note",
            yaxis_title="Prüfung",
            paper_bgcolor="#faf9f9",
            plot_bgcolor="#faf9f9",
            font=dict(
                family="serif",
                color="#22313f"
            )
        )

        st.plotly_chart(fig3)

        st.subheader("Gespeicherte Ergebnisse")
    
        # Display each saved exam result with a delete button.
        for index, row in exam_df.iterrows():
    
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
            col1.write(f"**{row['Prüfung']}**")
            col2.write(f"{row['Note']}")
            col3.write(f"{row['ECTS']} ECTS")
        
            with col4:
                if st.button("Löschen", key=f"delete_exam_{row['exam_id']}"):
                    delete_exam_result(row["exam_id"])
                    st.rerun()

else:
    st.info("Bitte logge dich zuerst ein.")
