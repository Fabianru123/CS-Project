# profile page including diagram variable_score/other users + 
# diagram "Scoreverlauf" score/time

import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go

from databases_sql import init_db, get_or_create_user
init_db()

# TEMPORARY LOGIN
username = st.text_input("User Name")                    #modified by H.
if st.button("Login"):
    if username.strip() == "":
        st.warning("Bitte gib einen User Name ein.")
    else:
        user_id = get_or_create_user(username)
        st.session_state["user_id"] = user_id
        st.session_state["username"] = username
        st.success(f"Eingeloggt als {username}")   



if "user_id" not in st.session_state:
    st.warning("Bitte logge dich zuerst ein, um deine Entwicklung zu verfolgen. ")
    st.stop()
user_id = st.session_state["user_id"]

DB = sqlite3.connect("predicted_inputs.db")
df = pd.read_sql("SELECT * FROM input", DB)
DB.close()

#---------------------------------------
#VISUALIZATION USER VS OTHERS (Figure 1)
#---------------------------------------

#create DataFrames
df_user = df[df["user_id"] == user_id]
df_others = df[df["user_id"] != user_id]


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

#Source: ChatGPT für die Struktur
fig1 = go.Figure()
#add bars
fig1.add_trace(
    go.Bar(x = variables_x, y = values_user, name="Deine Daten")
)
#add dots
fig1.add_trace(
    go.Scatter(x = variables_x, y = values_others, mode="markers", name="Andere")
)

fig1.update_layout(
    title="Dein Vergleich mit anderen Nutzern",
    xaxis_title="Variablen",
    yaxis_title="Score"
)

st.plotly_chart(fig1)


#---------------------------------------
#VISUALIZATION "SCOREVERLAUF" (Figure 2)
#---------------------------------------

fig2 = go.Figure()

df_user_sorted = df_user.sort_values("created_at")

fig2.add_trace(
    go.Scatter(
        x = df_user_sorted["created_at"],
        y = df_user_sorted["score"],
        mode = "lines+markers"
    )
)

fig2.update_layout(
    title="Entwicklung deines Scores über die Zeit",
    xaxis_title="Zeit",
    yaxis_title="Score"
)

st.plotly_chart(fig2)
