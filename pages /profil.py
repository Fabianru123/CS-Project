#=============================================================
# Profile Page: Comparison of Variable Scores with Other Users 
# + Score Evolution over Time
#=============================================================

import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go

from databases_sql import init_db, get_or_create_user, get_exam_results_by_user, add_exam_result
init_db()


#=========
# Sidebar
#=========

with st.sidebar:

    username = st.text_input("User Name")                    
    if st.button("Login"):
        if username.strip() == "":
            st.warning("Bitte gib einen User Name ein.")
        else:
            user_id = get_or_create_user(username)
            st.session_state["user_id"] = user_id
            st.session_state["username"] = username
    if "user_id" in st.session_state:
        st.success(f"Erfolgreich eingeloggt als {st.session_state['username']}.")


#======================
# Layout "Profil" page
#======================

st.title("Profil")

st.divider()

st.write("Ein Überblick über deinen aktuellen Stand im Vergleich zu anderen sowie die Entwicklung deiner Performance über die Zeit.")

st.divider ()


#============================
# Check if user is logged in
#============================

if "user_id" not in st.session_state:
    st.warning("Bitte logge dich zuerst ein, um deine Entwicklung zu verfolgen. ")
    st.stop()
user_id = st.session_state["user_id"]

DB = sqlite3.connect("predicted_inputs.db")
df = pd.read_sql("SELECT * FROM input", DB)
DB.close()



#===========
# DATAFRAMES
#===========

#create DataFrames
df_user = df[df["user_id"] == user_id]
df_others = df[df["user_id"] != user_id]



#===========
# DASHBOARD
#===========

if df_user.empty:
    st.info("Noch keine Daten vorhanden. Fülle zuerst deine Angaben aus.")
else:
    df_user_sorted = df_user.sort_values("created_at")
    last_entry = df_user_sorted.iloc[-1]

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

    col1, col2, col3 = st.columns(3)
    col1.metric("Alter", current_age)
    col2.metric("Studiengang", current_studien)
    col3.metric("Letzter Score", last_entry['score'])

st.divider()



#========================================
# VISUALIZATION USER VS OTHERS (Figure 1)
#========================================

#mean for every variable
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

#create y-values
values_user = [mean_user_schlaf, mean_user_lernzeit, mean_user_stress, mean_user_bild, mean_user_gesund, mean_user_hilfe, mean_user_pausen, mean_user_fail, mean_user_freetime, mean_user_goout, mean_user_pendel, mean_user_food, mean_user_sport]
values_others = [mean_others_schlaf, mean_others_lernzeit, mean_others_stress, mean_others_bild, mean_others_gesund, mean_others_hilfe, mean_others_pausen, mean_others_fail, mean_others_freetime, mean_others_goout, mean_others_pendel, mean_others_food, mean_others_sport]

#create x-values
variables_x = ["Schlaf", "Lernzeit", "Stress", "Bildschirmzeit", "Gesundheitszustand", "Nachhilfe", "Pausen", "Nicht bestandene Fächer", "Freizeit", "Ausgang", "Pendelzeit", "Ernährung", "Sport"]

#Source: ChatGPT for the structure
fig1 = go.Figure()
#add bars
fig1.add_trace(
    go.Bar(
        x = variables_x, 
        y = values_user, 
        name="Deine Daten",
        marker=dict(color="#0d4200")
        )
)
#add dots
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
)

st.plotly_chart(fig1)


#========================================
# VISUALIZATION "SCOREVERLAUF" (Figure 2)
#========================================
fig2 = go.Figure()

df_user_sorted = df_user.sort_values("created_at")
df_user_sorted["created_at"] = pd.to_datetime(df_user_sorted["created_at"])
df_user_sorted["created_at"] = df_user_sorted["created_at"].dt.tz_localize("UTC")
df_user_sorted["created_at"] = df_user_sorted["created_at"].dt.tz_convert("Europe/Zurich")
df_user_sorted["date_clean"] = df_user_sorted["created_at"].dt.strftime("%-d. %B %Y %H:%M")

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
)

st.plotly_chart(fig2)



#==============
# EXAM RESULTS
#==============

st.subheader("Prüfungsergebnisse")

st.write("Du kannst hier deine Ergebnisse eingeben, um deine Fortschritte zu verfolgen.")

exam_name = st.text_input("Name der Prüfung")

grade = st.number_input("Deine Note")

ects = st.number_input("ECTS")

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
    exam_data = get_exam_results_by_user(st.session_state["user_id"])
    if len(exam_data) == 0:
        st.info("Noch keine Ergebnisse vorhanden.")
    else:

        exam_df = pd.DataFrame(
            exam_data,
            columns=["exam_id", "user_id", "created_at", "exam_name", "grade", "ects"]
        )
        exam_df = exam_df.sort_values("created_at")
        exam_df["created_at"] = pd.to_datetime(exam_df["created_at"])
        exam_df["created_at"] = exam_df["created_at"].dt.tz_localize("UTC")
        exam_df["created_at"] = exam_df["created_at"].dt.tz_convert("Europe/Zurich")
        exam_df["date_clean"] = exam_df["created_at"].dt.strftime("%-d. %B %Y %H:%M")

        nb_lines = len(exam_df)
        weighted_mean = (exam_df["grade"] * exam_df["ects"]).sum() / exam_df["ects"].sum()
        rounded_mean = round(weighted_mean, 2)
        last_grade = exam_df["grade"].iloc[-1]

        col1, col2, col3 = st.columns(3)
        col1.metric("Anzahl Prüfungen", nb_lines)
        col2.metric("Durchschnitt", rounded_mean)
        col3.metric("Letzte Note", last_grade)

        #----------------
        # FIGURE 3: NOTES
        #----------------

        exam_df = exam_df.rename(columns={
            "exam_name": "Prüfung",
            "grade": "Note",
            "date_clean": "Datum",
            "ects": "ECTS"
        })

        fig3 = go.Figure()
        fig3.add_trace(
            go.Bar(
                x = exam_df["Note"],
                y = exam_df["Prüfung"],
                orientation = 'h',
                marker=dict(color="#8a9a8b"),
                name="Deine Noten"
            )
        )

        # The user can see the mean of his grades
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
        )

        st.plotly_chart(fig3)

else:
    st.info("Bitte logge dich zuerst ein.")
