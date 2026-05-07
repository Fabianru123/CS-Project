#==========
# HOMEPAGE
#==========


#==================================
# IMPORT AND DATABASE INITILIZATION
#==================================

from databases_sql import add_input, init_db, get_or_create_user #added by Helena
init_db()

import streamlit as st

st.set_page_config(layout = "centered")

#=========
#SIDEBAR
#=========
with st.sidebar:

    st.subheader("Deine persönlichen Angaben")

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

    age = st.number_input("Alter", 0, None, None, 1)       
    studien = st.text_input("Studiengang")

#================
# WELCOME SECTION
#================

col11, col12, col13 = st.columns(3)

with col13:
    st.image("https://i.pinimg.com/736x/d7/f1/5a/d7f15a31e2e076bc50fcc6e7db787f81.jpg", width = 200)
with col12:    
    st.image("https://i.pinimg.com/736x/d6/54/d5/d654d55c67c2a30031a97728373afa97.jpg", width = 350) 
with col11:
    st.image("https://i.pinimg.com/736x/22/7a/ad/227aad25b9446c9b65f5b62412a3ea0b.jpg", width = 180)    

st.title("Willkommen bei PredictEd")
st.write("Hier kannst deinen Score entdecken und personalisierte Tipps bekommen, um deinen Lernerfolg zu steigern! 🎓")

st.divider ()


#====================
# SCORE INPUT SECTION
#====================

st.subheader("Die Berechnung deines Scores")
# The following phrase uses the function markdown and not st.write, as it was too instabil 
st.markdown("Gib hier deine Variablen ein, damit du deinen Score entdecken kannst <br><i> (Alle Fragen sind mit Durchschnitten über eine längere Periode zu beantworten)</i>",
            unsafe_allow_html = True)
st.write("")


#=========================
# INITIALIZE SESSION STATE
# The points are used for the graphics and need to be saved for the score 
#=========================

if "punkte" not in st.session_state:
    st.session_state.punkte = 0


#=====================
# USER INPUT VARIABLES
# Display of the variables only — no calculations are performed at this stage
# This section simply allows users to enter their variables
#=====================

col31, col32 = st.columns(2)    

pschlaf = 0
with col31: 
    schlaf = st.slider("Schlaf *(in Stunden pro Nacht)*",0, 10)


plernzeit = 0
with col32: 
    lernzeit = st.slider("Lernzeit *(in Stunden pro Woche)*", 0, 50)


pstress1 = 0
stress = st.selectbox ("Akademischer Stress", ("Wählen", "Tief", "Mittel", "Hoch"))

col41, col42 = st.columns(2)

pbild = 0
with col41:
    bild = st.slider("Bildschirmzeit *(in Stunden pro Tag)*", 0, 24)


pgesund = 0
gesund = st.selectbox("Gesundheitszustand", ("Wählen", "Sehr gut", "Gut", "Schlecht"))


philfe= 0
with col42:
    hilfe = st.slider("Nachhilfe *(in Stunden pro Woche)*", 0, 20)


col51, col52 = st.columns(2)

ppausen = 0
with col51:
    pausen = st.slider("Pausen *(in Prozent der Lernzeit)*", 0, 100)


pfail = 0
with col52:
    fail = st.slider("Anzahl nicht bestandener Fächer", 0, 10)

pfood = 0
food = st.selectbox("Ernähung", ("Wählen", "Sehr gesund", "Kommt drauf an", "Überhaupt nicht gesund"))

col61, col62 = st.columns(2)

pfreetime = 0
with col61:
    freetime = st.slider("Freizeit und Aktivitäten *(in Stunden pro Woche)*", 0, 50)


ppendel = 0
with col62:
    pendel = st.slider("Pendelzeit zwischen der Uni und der Wohnung *(in Stunden pro Tag)*", 0, 6)

pgoout= 0
goout = st.selectbox("Wie fühlst du dich nach dem Ausgang", ("Wählen", "Lernen ist gut möglich", "Lernen ist schwierig", "Lernen ist unmöglich", "Ich gehe nicht in Ausgang"))    


psport = 0
sport = st.slider("Sport *(in Stunden pro Woche)*", 0, 40)

# The button ensures that the points are not lost during the session
# and prevents them from being added multiple times when the user modifies their inputs.


#========================
# SCORE CALCULATION RULES
# The same logic was applied throughout the scoring system:
# each variable contributes a specific number of points depending on the range in which it falls.

# Example:
# More than 8 hours of sleep per night: 4 points (low risk)
# Between 6 and 8 hours of sleep per night: 2 points (medium risk)
# Less than 6 hours of sleep per night: 1 point (high risk)

# "Low risk" represents the optimal condition for the score,
# meaning that the variable could not realistically be improved further.
# All variables are based on academic studies and on a student performance database.

# Database source:
# https://archive.ics.uci.edu/dataset/320/student+performance

# Variables taken from the database:
# - studytime: study duration
# - health: health condition
# - schoolsupport: tutoring/support classes
# - failures: failed subjects
# - freetime: leisure time and activities
# - goout: social outings
# - traveltime: commuting time

# Variables derived from academic studies:
# - Schlaf
# - Stress
# - Pausen
# - Bildschirmzeit
# - Ernährung
# - Sport

# Note:
# The database was initially intended for the machine learning model
# and was not directly used to calculate the final score.
# The first score is therefore based on the variables, which give points based on ranges 
# For more information, please refer to the calculation rules below and to the file ml_model.py 

# The variables were divided into two categories:
# 1. Major variables
# 2. Secondary variables

# Major variables contribute:
# - 4 / 2 / 1 points

# Secondary variables contribute:
# - 2 / 1 / 0.5 points

# Major variables:
# - Schlaf
# - Lernzeit
# - Akademischer Stress
# - Bildschirmzeit
# - Gesundheitszustand
# - Nachhilfe
# - Pausen

# Secondary variables:
# - Nicht bestandener Fächer
# - Freizeit und Aktivitäten
# - Ausgang
# - Pendelzeit zwischen der Uni und der Wohnung
# - Ernährung
# - Sport
#========================

#============================
# SAVE USER INPUT TO DATABASE
#============================

if st.button("Bestätigen", key = "button"):
    if schlaf >= 8:
       pschlaf = 4
    elif schlaf > 6 and schlaf < 8:
        pschlaf = 2
    else:
       pschlaf = 1
    
    if lernzeit >= 21:
        plernzeit = 4
    elif 11 <= lernzeit <= 20:
        plernzeit = 2
    else:
        plernzeit = 1

    if stress == "Tief":
        pstress1 = 4
    elif stress == "Mittel":
        pstress1 = 2
    else: 
        pstress1 = 1    

    if 0 <= bild <= 1:
        pbild = 4
    elif 1 < bild:
        pbild = 2
    else:
        pbild = 1   

    if gesund == "Sehr gut":
        pgesund = 4
    elif gesund == "Gut":
        pgesund = 2 
    else:
        pgesund = 1                      

    if hilfe >= 2:
        philfe = 4
    elif 1 <= hilfe < 2:
        philfe = 2
    else:
        philfe = 1

    if 15 <= pausen <= 25:
        ppausen = 4
    elif 25 < pausen <= 40:
        ppausen = 2
    else: 
        ppausen = 1


    if fail == 0:
        pfail = 2
    elif 1 <= fail <= 2:
        pfail = 1
    else:
        pfail = 0.5     

    if 12 >= freetime >= 8:
        pfreetime = 2
    elif 12 < freetime <= 20:
        pfreetime = 1
    else:
        pfreetime = 0.5    

    if goout == "Lernen ist gut möglich":
        pgoout = 2
    elif goout == "Ich gehe nicht in Ausgang":
        pgoout = 2
    elif goout == "Lernen ist schwierig":
        pgoout = 1 
    else:
        pgoout = 0.5                                  

    if 0 <= pendel <= 1:
        ppendel = 2
    elif 1 < pendel <= 3:
        ppendel = 1
    else:
        pgoout = 0.5    

    if food == "Sehr gesund":
        pfood = 2
    elif food == "Kommt drauf an":
        pfood = 1
    else:
        pfood = 0.5    

    if 6 <= sport <= 10 :
        psport = 2
    elif 3 <= sport <= 5:
        psport = 1
    else:
        psport = 0.5    

    st.session_state.punkte = pschlaf + plernzeit + pstress1 + pbild + pgesund + philfe + ppausen + pfail + pfreetime + pgoout + ppendel + pfood + psport 

    score = 2.5 * st.session_state.punkte 
    # 2.5 = 100 / 40 = Max Score / Anzhal max Punkte nach der aktuellen Variablen 
    # 100 = max Score und entspricht der maximalen Wahrscheinlichkeit 

    if "user_id" not in st.session_state:
        st.warning("Bitte logge dich zuerst ein.")
    else:
        add_input(
            st.session_state["user_id"], age, studien, pschlaf, plernzeit, pstress1, pbild, pgesund, philfe, ppausen, pfail, pfreetime, pgoout, ppendel, pfood, psport, score
        )
        st.success ("Daten gespeichert.")

st.divider ()


#=========================================================================
# RESULTS SECTION
# The score is first displayed as a spider web / radar chart,
# allowing the user to identify which variables are already performing well
# and which areas could still be improved.
# The overall score is then presented as a pass probability.
#=========================================================================

st.subheader("Deine Ergebnisse")   
st.write("Hier erkennst du auf einen Blick, was bereits gut läuft und wo du dich noch verbessern kannst:")

score = 2.5 * st.session_state.punkte 
    #====================================================================================
    # 2.5 = 100 / 40 = maximum score divided by the maximum possible number of points
    # based on the current variable weighting system.
    # 100 represents the maximum score and therefore the highest possible pass probability.
    #=====================================================================================

with st.sidebar: 
    st.write("Dein Score:", score)

col21, col22 = st.columns(2) 


#=========================
# RADAR CHAT VISUALIZATION
# Source: ChatGPT for the structure
#=========================


with col21: 


    import plotly.graph_objects as go

    categories = ['Schlaf', 'Lernzeit', 'Stress', 'Bildschirmzeit', 'Gesundheitszustand', 'Nachhilfe', "Pausen",
                "Fails", "Freizeit", "Ausgang", "Pendelzeit", "Ernähung", "Sport"]
    values = [pschlaf, plernzeit, pstress1, pbild, pgesund, philfe, ppausen, 2*pfail, 2*pfreetime, 2*pgoout,  2*ppendel, 2*pfood, 2*psport]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor="#d3dbd1",   
        line=dict(color="#0d4200")))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0,4])),
        showlegend=False)
    fig_radar.update_layout(height = 420)

    st.plotly_chart(fig_radar)


#=====================================
# PASS PROBABILITY GAUGE
# Source: ChatGPT for the structure
#=====================================
 

with col22: 

    import plotly.graph_objects as go

    pass_probability = score 

    if 0 <= pass_probability <= 34:
        color = "#e57373"
    elif 35 <= pass_probability <= 70:
        color = "#ffd54f"
    else: 
        color = "#81c784"
  
 # 0-34 = red = high risk, 35-70 = yellow = moderate risk, 71-100 = green = low risk.    

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pass_probability,
        number={'suffix': "%"},
        gauge={'axis': {'range': [0,100]},
            'bar': {"color": color},
            'bgcolor': "lightgray"}))
    
    fig_gauge.update_layout(height = 350)

    st.plotly_chart(fig_gauge)
    st.write("Du hast eine Pass Probability von", score,"%")


#=========================================================================
# PERSONALIZED RECOMMENDATIONS
# The tips are displayed in this section.
# They are based on academic studies referenced below.
# For each variable, one out of three possible tips is shown,
# depending on the number of points achieved.
# The tips are first stored in a list
# to simplify the visualization process in Python.
# As a result, each user receives a personalized list of recommendations
# based on their individual variables and scores.
#=========================================================================

 

st.divider()
st.subheader("Deine personalisierten Tipps")
st.caption("Hier sind unsere Empfehlungen, um die Effizienz deines Lernens zu verbessern:")


tipps = [] 


if pschlaf == 4:
    tipps.append("Du ruhst dich optimal aus. Nutze deine Energie am Vormittag, direkt für anspruchsvolle Aufgaben, solange deine Konzentration hoch ist")
elif pschlaf == 2:
    tipps.append("Versuche heute Abend schon 30 Minuten früher ins Bett zu gehen und auf Bildschirmzeit  zu verzichten, damit sich dein Körper optimal erholen kann")
elif pschlaf == 1:
    tipps.append("Gönne deinem Körper heute die nötige Erholung. Versuche, dich mit einem 15-minütigen Powernap zu erholen und gehe deutlich früher Schlafen, um dein Schlafdefizit abzubauen")
# Source: Okano, K., Kaczmarzyk, J. R., Dave, N., Gabrieli, J. D. E., & Grossman, J. C. (2019).
# Sleep quality, duration, and consistency are associated with better academic performance in college students. 
# npj Science of Learning, 4(1), Artikel 16. https://doi.org/10.1038/s41539-019-0055-z

if plernzeit == 4:
    tipps.append("Weiter so! Nutze deine Lernzeit möglichst effizient, indem du sie gezielt einsetzt, damit du deine Energie optimal nutzen kannst")
elif plernzeit == 2:
    tipps.append("Mit nur 30 Minuten zusätzlicher Lernzeit und einem klaren Fokus, kannst du deine Lernziele künftig effizienter und entspannter erreichen.")
elif plernzeit == 1:
    tipps.append("Beginne heute mit einer kleinen, aber fokussierten Lerneinheit in einer ruhigen Umgebung. So findest du wieder zu deinem Lernrhythmus und kommst deinen Lernzielen einen grossen Schritt näher")
# Source: Bensberg, G., & Messer, J. (2014). Zeitmanagement. In Survivalguide Bachelor (S. 109–119). 
# Springer Berlin Heidelberg. https://doi.org/10.1007/978-3-642-39027-2_14

if pstress1 == 4:
    tipps.append("Du scheinst alles im Griff zu haben, nutze deine Ruhe um bei einem schwierigen Thema voranzukommen")
elif pstress1 == 2: 
    tipps.append("Du fühlst dich etwas überwältigt, priorisiere heute nur die drei wichtigsten Aufgaben und lass dir von uns ein Lernplan erstellen")
elif pstress1 == 1:
    tipps.append("Du fühlst dich überbelastet, streiche unnötige To-dos und fokussiere dich auf die wichtigsten Lernziele")
# Source: Deng, Y., Cherian, J., Khan, N. U. Z., Kumari, K., Ali, N. M., Sial, M. S., Comite, U., & Aldushari, F.
# (2022). Family and academic stress and their impact on students’ depression level and academic performance. 
# Frontiers in Psychiatry, 13, Artikel 869337. https://doi.org/10.3389/fpsyt.2022.869337

if pbild == 4: 
    tipps.append("Behalte die niedrige Bildschirmzeit, sie hilft dir komplexe Lerninhalte schneller zu verarbeiten")
elif  pbild == 2:
    tipps.append("Du hast eine erhöhte Bildschirmzeit,  versuche deshalb 30min vor dem Schlafen und in deinen Lenrpausen bewusst auf dein Handy zu verzichten")
elif pbild == 1:
    tipps.append("Du benötigst ein digital Detox, schalte beim Lernen alle Benachtitigungen aus und lege dein Handy ausser Sichtweite")
# Source: Chen, J., & Li, H. (2025). 
# A meta-analysis of the impact of technology related factors on students' academic performance.
# Frontiers in Psychology, 16, Artikel 1524645. https://doi.org/10.3389/fpsyg.2025.1524645

if pgesund == 4:
    tipps.append("Du bist körperlich in einer guten Verfassung. Dies gibt dir eine gute Basis für dein Lernen. Weiter so!")
elif pgesund == 2:
    tipps.append("Du fühlst dich etwas angeschlagen? Probiere in deinen Lernpausen progressive Muskelentspannung. Bei dieser spannst du eine bestimmte Muskelgruppe kurz an und lässt sie nach 10 Sekunden wieder los.")       
elif pgesund == 1:
    tipps.append("Dein körperlicher Zustand beeinflusst deine Leistungsfähigkeit stark. Gönne dir morgen einen Ruhetag, um Energie für die nächsten Tage zu sammeln.")
# Source: Raskind, I. G., Haardörfer, R., & Berg, C. J. (2019). 
# Food insecurity, psychosocial health and academic performance among college and university students in Georgia, USA.
# Public Health Nutrition, 22(3), 476–485. https://doi.org/10.1017/S1368980018003439


if philfe == 4:
    tipps.append("Du hast ein solides Verständnis, festige dein Wissen indem du deinen Mitstudenten den Inhalt erklärst oder Altklausuren löst")
elif philfe == 2:
    tipps.append("Fülle wenn möglich Altklausuren aus, und prüfe welche Lücken du selber schliessen kannst und für welche Themen du Nachhilfe benötigst") 
elif philfe == 1:
    tipps.append("Wenn du das Gefühl hast, dass du bestimmte Themen nicht selbst erarbeiten kannst, hole dir rechtzeitig Hilfe in einem Tutorium oder von einer Nachhilfelehrkraft")
# Source: Weydenhammer, N. (2015). Wirksamkeitsfacetten von Nachhilfe in Deutschland und den USA: 
# Eine Ländervergleichende Studie. ProQuest Dissertations & Theses. 
# https://epub.uni-bayreuth.de/id/eprint/2141/1/Dissertation_finale%20Version.pdf

if ppausen == 4:
    tipps.append("Du hast das optimale Balance zwischen  Lernen und Pausen. Nutze deine Pausen  um an die frische Luft zu gehen und neue Energie zu tanken")
elif ppausen == 2:
    tipps.append("Du arbeitest zu lange am Stück, probiere die Pomodero-Technik aus ( 25min lernen und 5min Pause)")   
elif ppausen == 1:
    tipps.append("Pausen sind esentiell für dein Gehirn, gönne dir heute noch eine  30-60min handyfreie Pause.")
# Source: Biwer, F., Menko, R., Groeneveld, S., & de Bruin, A. (2025). 
# Investigating the effectiveness of self-regulated, Pomodoro, and Flowtime break-taking techniques among students.
# Behavioral Sciences, 15(7), Artikel 861. https://doi.org/10.3390/bs15070861

if pfail == 2: 
    tipps.append("Deine Lernstrategie scheint gut zu funktionieren und lass dir einen Lernplan von uns erstellen um dich möglichst effizient vorzubereiten")
elif pfail == 1: 
    tipps.append("Analysiere deine Fehlerquelle, suche dir rechtzeitig eine Lerngruppe  und tausche dich mit anderen aus")
elif pfail == 1:
    tipps.append("Hole dir Hilfe von der Studienberatung oder einem Mentor um das Semster erfolgreich abzuschliessen")  
# Source: Petri, P. S. (2020). Das Individuum im Fokus: 
# Was wissen wir eigentlich über individuelle Gelingensbedingungen für ein Studium? 
# Ergebnisse empirischer Primärstudien und Metaanalyse zu Studienerfolg und Studienabbruch.
# https://www.researchgate.net/publication/343344251_Petri_P_S_2020_Das_Individuum_im_Fokus_Was_wissen_wir_eigentlich_uber_individuelle_Gelingensbedingungen_fur_ein_Studium_Ergebnisse_empirischer_Primarstudien_und_Metaanalysen_zu_Studienerfolg_und_Studi

if pfreetime == 2:
    tipps.append("Du hast eine gute Balance zwischen deinem Uni und deinem Privatleben. Das erhöht deine kognitive Leistungsfähigkeit. Weiter so!")
elif pfreetime == 1:
    tipps.append("Gönne dir etwas Abwechslung vom lernen, plane dieses Wochenende bewusst eine Aktivität ein die nichts mit der Uni zu tun hat.")
elif pfreetime == 0.5:
    tipps.append("Es fehlt dir an der nötigen Balance zwischen Uni und Privatleben. Triff dich in den nächsten Tagen mit Freunden oder nimm dir heute Abend etwas Zeit für dich")  
# Source: Bensberg, G., & Messer, J. (2014). Zeitmanagement. In Survivalguide Bachelor 
# (S. 109–119). Springer Berlin Heidelberg. https://doi.org/10.1007/978-3-642-39027-2_14

if pgoout == 2:
    tipps.append("Du hast eine gute  Balance gefunden. Achte weiterhin darauf dir deine Lernphasen und Ausgangsabende klar einzuteilen.")
elif pgoout == 1:
    tipps.append("Achte auf dein Zeitmanagement . Plane nach dem Ausgehen einen Puffer-Tag für leichtere Aufgaben ein und versucht,  nicht mehr als zweimal pro Woche auszugehen.")
elif pgoout == 0.5:
    tipps.append("Häufiges Feiern wirkt sich negativ auf deinen Lernrhytmus aus. Versuche klare Prioritäten zu setzen und gehe nur in den Aufgang wenn du deine Lernziele für die Woche erreicht hast.")        
# Source: Gries, B. (2018, January 24). The effects of partying on academics. 
# The Equinox. https://kscequinox.com/2018/01/the-effects-of-partying-on-academics/

if ppendel == 2: 
    tipps.append("Du hast Glück mit deinem kurzen Fahrtweg, dies gibt dir mehr Zeit für Schlaf oder Freizeitaktivitäten.")
elif ppendel == 1:
    tipps.append("Nutze die Fahrt um mit Karteikarten zu lernen oder für ein kurzes Quiz.") 
elif ppendel == 0.5: 
    tipps.append("Du hast einen langen Fahrtweg, lass dich von dem nicht stressen. Nutze die Zeit bewusst für ein Quiz oder ein fachbezogenes Hörbuch")  
# Source: Bensberg, G., & Messer, J. (2014). Zeitmanagement. 
# In Survivalguide Bachelor (S. 109–119). Springer Berlin Heidelberg. https://doi.org/10.1007/978-3-642-39027-2_14

if pfood == 2:
    tipps.append("Du ernährst dich ideal.Behalte deine Routine bei und achte auch eine ausreichende Hydrierung.")
elif pfood == 1:
    tipps.append("Eine gesunde Ernährung wirkt sich auf deinen Lernerfolg aus nutze Brainfood wie Nüsse oder Obst zwischen in den Lernpausen")
elif pfood == 0.5:
    tipps.append("Ohne eine ausgewogene Ernährung, hat dein Körper nicht die benötigte Energie, iss 3 feste Mahlzeiten mit Früchten/Gemüse")
# Source: López-Gil, J. F., García-Hermoso, A., Smith, L., Firth, 
# J., Trott, M., Mesas, A. E., Jimenez-Lopez, E., Gutierrez-Espinoza, H., Tárraga-López, P. J., 
# & Victoria-Montesinos, D. (2022). Association between eating habits and perceived school performance: 
# A cross-sectional study among 46,455 adolescents from 42 countries. Frontiers in Nutrition, 9, Artikel 797415.
#  https://doi.org/10.3389/fnut.2022.797415

if psport == 2:
    tipps.append("Behalte die regelmässige Bewegung bei, sie fördert deine Durchblutung und hilft dir die Lerninhalte optimal aufzunehmen und konzentriert zu bleiben.")
elif psport == 1:
    tipps.append("Mit Hilfe eines kurzen Spaziergangs oder einem 15-Minütigen Workout kannst du deine Konzentration weiter steigern und noch effizienter lernen.")
elif psport == 0.5:
    tipps.append("Regelmässige Bewegung ist ein wichtiger Faktor für deinen Lernerfolg. Sie hilft dir, konzentriert zu bleiben. Versuche es heute mit einem 30-minütigen Spaziergang oder einem Workout")    
#Source: Wang, F., & Zhang, L. (2023). Exercise makes better mind: A data mining study. 
# Frontiers in Psychology, 14, Artikel 1271431. https://doi.org/10.3389/fpsyg.2023.1271431


#===================================
# DISPLAY RECOMMENDATIONS IN COLUMNS
# The tips are displayed in two columns to improve readability and user experience
# Source: ChatGPT for the function "zip"
#===================================

var_tipps = ["Schlaf", "Lernzeit", "Stress", "Bildschirmzeit", "Gesundheitszustand", "Nachhilfe", "Pausen", "Nicht bestandener Fächer", "Freizeit", "Ausgang", "Pendelzeit", "Ernähung", "Sport"]


cols = st.columns(2)
for i, (tipp, var_tipp) in enumerate(zip(tipps, var_tipps)):
    with cols[i%2]:
        st.write("")
        st.success(f"**{var_tipp}**: {tipp}")


st.divider() 
st.write("")

#======================
# FINAL SUCCESS MESSAGE
#======================


st.write("Du kannst jederzeit deine Variablen anpassen, um deinen Score zu verbessern und neue personalisierte Tipps zu erhalten. Du kannst auch einen eigenen Lernplan erstellen lassen, um deine Lernzeit optimal zu nutzen.")
st.page_link("profil.py", label = "Hier geht's zu deinem Profil", icon = "👤") 
st.page_link("lernplan.py", label = "Hier kannst du deinen Lernplan erstellen", icon = "🗓️")

st.subheader("Wir wünschen dir ganz viel Erfolg!")
