#code Claire: Variablen, Berechnung des Scores und Darstellung als Spiderweb und als Passprobability 

from database_inputs import add_input #added by Helena

import streamlit as st

with st.sidebar:
    st.write("Score")

st.title("PredictEd")

st.divider()

st.header("Berechnung des Scores")

st.divider ()

st.subheader("Deine persönlichen Angaben")

name = st.text_input("Name")                            #modified by H.
age = st.number_input("Alter", 0, None, None, 1)        #modified by H.
studien = st.text_input("Studiengang")                  #modified by H.

st.divider ()

st.subheader("Deine Variablen")
st.caption("Alle Fragen sind mit Durchschnitten über eine längere Periode zu beantworten")


if "punkte" not in st.session_state:
    st.session_state.punkte = 0


pschlaf = 0
schlaf = st.slider("Schlaf *(in Stunden pro Nacht)*",0, 10)


plernzeit = 0
lernzeit = st.slider("Lernzeit *(in Stunden pro Woche)*", 0, 50)


pstress1 = 0
stress = st.selectbox ("Akademischer Stress", ("Wählen", "Tief", "Mittel", "Hoch"))


pbild = 0
bild = st.slider("Bildschirmzeit *(in Stunden pro Tag)*", 0, 24)


pgesund = 0
gesund = st.selectbox("Gesundheitszustand", ("Wählen", "Sehr gut", "Gut", "Schlecht"))


philfe= 0
hilfe = st.slider("Nachhilfe *(in Stunden pro Woche)*", 0, 20)


ppausen = 0
pausen = st.slider("Pausen *(in Prozent der Lernzeit)*", 0, 100)


pfail = 0
fail = st.slider("Anzahl nicht bestandener Fächer", 0, 10)


pfreetime = 0
freetime = st.slider("Freizeit und Aktivitäten *(in Stunden pro Woche)*", 0, 50)


pgoout= 0
goout = st.selectbox("Wie fühlst du dich nach dem Ausgang", ("Wählen", "Lernen ist gut möglich", "Lernen ist schwierig", "Lernen ist unmöglich"))


ppendel = 0
pendel = st.slider("Pendelzeit zwischen der Uni und der Wohnung *(in Stunden pro Tag)*", 0, 6)


pfood = 0
food = st.selectbox("Ernähung", ("Wählen", "Sehr gesund", "Kommt drauf an", "Überhaupt nicht gesund"))


psport = 0
sport = st.slider("Sport *(in Stunden pro Woche)*", 0, 40)


if st.button("Bestätigen", key = "button"):
    if schlaf >= 8:
       pschlaf = 4
    elif schlaf > 6 and schlaf < 8:
        pschlaf = 2
    else:
       pschlaf = 0
    
    if lernzeit >= 21:
        plernzeit = 4
    elif 11 <= lernzeit <= 20:
        plernzeit = 2

    if stress == "Tief":
        pstress1 = 4
    elif stress == "Mittel":
        pstress1 = 2

    if 0 <= bild <= 1:
        pbild = 4
    elif 1 < bild:
        pbild = 2

    if gesund == "Sehr gut":
        pgesund = 4
    elif gesund == "Gut":
        pgesund = 2                    #modified by H. was written pbild = 2, probably pgesund

    if hilfe >= 2:
        philfe = 4
    elif 1 <= hilfe < 2:
        philfe = 2

    if 15 <= pausen <= 25:
        ppausen = 4
    elif 25 < pausen <= 40:
        ppausen = 2


    if fail == 0:
        pfail = 2
    elif 1 <= fail <= 2:
        pfail = 1

    if 12 >= freetime >= 8:
        pfreetime = 2
    elif 12 < freetime <= 20:
        pfreetime = 1

    if goout == "Lernen ist gut möglich":
        pgoout = 2
    elif goout == "Lernen ist schwierig":
        pfail = 1

    if 0 <= pendel <= 1:
        ppendel = 2
    elif 1 < pendel <= 3:
        ppendel = 1

    if food == "Sehr gesund":
        pfood = 2
    elif food == "Kommt drauf an":
        pfood = 1

    if 6 <= sport <= 10 :
        psport = 2
    elif 3 <= sport <= 5:
        psport = 1


st.session_state.punkte += pschlaf + plernzeit + pstress1 + pbild + pgesund + philfe + ppausen + pfail + pfreetime + pgoout + ppendel + pfood + psport 




st.write("Punkte =", st.session_state.punkte)

st.divider ()



st.subheader("Dein Score")     

score = 2.5 * st.session_state.punkte 
# 2.5 = 100 / 40 = Score / Anzhal max Punkte nach der aktuellen Variablen 
# 100 = max Score und entspricht der maximalen Wahrscheinlichkeit 

st.write(score)

#Quelle: ChatGPT für die Struktur 

col1, col2 = st.columns(2) 

with col1: 

    import plotly.graph_objects as go

    categories = ['Schlaf', 'Lernzeit', 'Stress', 'Bildschirmzeit', 'Gesundheitszustand', 'Nachhilfe', "Pausen",
                "Nicht bestandener Fächer", "Freizeit", "Alkohol", "Pendelzeit", "Ernähung", "Sport"]
    values = [pschlaf, plernzeit, pstress1, pbild, pgesund, philfe, ppausen, 2*pfail, 2*pfreetime, 2*pgoout,  2*ppendel, 2*pfood, 2*psport]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself'))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0,4])),
        showlegend=False)

    st.plotly_chart(fig_radar)


#Quelle ChatGPT für die Struktur 

with col2: 

    import plotly.graph_objects as go

    pass_probability = score 

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pass_probability,
        number={'suffix': "%"},
        gauge={'axis': {'range': [0,100]},
            'bar': {'color': "blue"},
            'bgcolor': "lightgray"}))

    st.plotly_chart(fig_gauge)





