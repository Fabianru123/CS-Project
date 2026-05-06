#==========
# HOMEPAGE
#==========


#==================================
# IMPORT AND DATABASE INITILIZATION
#==================================
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from databases_sql import add_input, init_db, get_or_create_user #added by Helena
from ml_model import predict_pass_probability
init_db()

import streamlit as st

st.set_page_config(layout = "centered")


#=======================
# SIDEBAR AND USER LOGIN
#=======================

with st.sidebar:
    st.write("Score")

    st.subheader("Deine persönlichen Angaben")

    username = st.text_input("User Name")                    
    if st.button("Login"):
        if username.strip() == "":
            st.warning("Bitte gib einen User Name ein.")
        else:
            user_id = get_or_create_user(username)
            st.session_state["user_id"] = user_id
            st.session_state["username"] = username
            st.success(f"Eingeloggt als {username}")                           #modified by H.
    age = st.number_input("Alter", 0, None, None, 1)        #modified by H.
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
#Der folgende Satz wurde mit st.markdown statt mit st.write geschrieben, weil st.write unstabil war 
st.markdown("Gib hier deine Variablen ein, damit du deinen Score entdecken kannst <br><i> (Alle Fragen sind mit Durchschnitten über eine längere Periode zu beantworten)</i>",
            unsafe_allow_html = True)
st.write("")


#=========================
# INITIALIZE SESSION STATE
#=========================

#Initialisierung der Punkte, sie werden für die Graphiken gespeichert (aber nicht die einzelnen Punkte)
if "punkte" not in st.session_state:
    st.session_state.punkte = 0


#=====================
# USER INPUT VARIABLES
#=====================

#Darstellung der Variablen, keine Berechnung erfolgt an dieser Stelle (es geht nur darum, dass die Users ihre Variablen eingeben können)

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

#der Button wird verwendet, damit die Punkte nicht wegen der Session verloren gehen 
# und um zu vermeiden, dass die Punkte mehrmals addiert werden, wenn der User seine Einträge ändert 


#========================
# SCORE CALCULATION RULES
#========================

#Hier wurde immer die gleiche Idee angewandt: eine bestimmte Variable gibt eine bestimmte Anzahl an Punkten, wenn sie sich in einem bestimmten Bereich befindet
#Beispiel: mehr als 8 Stunden Schlaf pro Nacht: 4 Punkte (low risk), von 6 bis 8 Stunden Schlaf pro Nacht: 2 Punkte (medium risk), weniger als 6 Stunden: 1 Punkt (high risk)
#Low risk entspricht dem bestem Mass für den Score, d.h. dass man es nicht besser machen könnte
#Alle Variablen basieren auf Studien und auf eine Database 
#Hier ist der Link zur Database: https://archive.ics.uci.edu/dataset/320/student+performance 
#Variablen aus der Database: studytime für die Lernzeit, health für den Gesundheitszustand, schoolsupport für die Nachhilfestunden,
#failures für die nicht bestandener Fächer, freetime für die Freizeit und Aktivitäten, gooout für den Ausgang, traveltime für die Pendelzeit 
#Variablen, die aus Studien kommen: Schlaf, Stress, Pausen, Bildschirmzeit, Ernähung, Sport 
#Bemerkung: Die Database wurde erst für das Machine Learning Modell verwendet und nicht direkt für die Berechnung des Scores 
#Da wir kein Regressionsmodell bilden konnten, um sehr genau zu berechnen, welche Variablen genau wie viele Punkte geben sollten, haben wir unseres Modell vereinfacht. 
#Wir haben die Variablen in 2 Kategorien geteilt: die wichtigsten Variablen und die weniger wichtigten 
#die wichtigten Variablen geben 4, 2 oder 1 Punkte
#die weniger wichtigten Variablen geben 2, 1 oder 0.5 Punkte
#die wichtigsten Variablen sind die folgenden: Schlaf, Lernzeit, akademischer Stress, Bildschirmzeit, Gesundheitszustand, Nachhilfe und Pausen
#die weniger wichtigen Variablen sind die folgenden:
# Anzahl nicht bestandener Fächer in der Vergangenheit, Freizeit und Aktivitäten, Ausgang und Zustand nach dem Ausgang, Pendelzeit zwischen der Wohnung und der Uni, 
#Ernähung und Sport 


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

#Hier wird der Score dargestellt, zuerst in einem Spider Web / Radar Chart, damit der User sehen kann, welche Variablen bei ihm gut laufen und welche er noch verbessern kann 
#Danach wird der Score als Pass Probability gezeigt

st.divider ()


# ==================================================
# ML Pass Probalitly calculation in Regression Model
# ==================================================

    
points_dict = {"pschlaf": pschlaf, "plernzeit": plernzeit, "pstress": pstress1, "pbild": pbild, "pgesund": pgesund, "philfe": philfe, "ppausen": ppausen, "pfail": pfail, "pfreetime": pfreetime, "pgoout": pgoout, "ppendel": ppendel, "pfood": pfood, "psport": psport}
st.session_state["pass_probability"] = predict_pass_probability(points_dict)



#================
# RESULTS SECTION
#================

st.subheader("Deine Ergebnisse")   
st.write("Hier erkennst du auf einen Blick, was bereits gut läuft und wo du dich noch verbessern kannst:")

score = 2.5 * st.session_state.punkte 
    # 2.5 = 100 / 40 = Max Score / Anzhal max Punkte nach der aktuellen Variablen 
    # 100 = max Score und entspricht der maximalen Wahrscheinlichkeit 

with st.sidebar: 
    st.write("Dein Score:", score)

col21, col22 = st.columns(2) 


#=========================
# RADAR CHAT VISUALIZATION
#=========================

#Quelle: ChatGPT für die Struktur 

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


#=======================
# PASS PROBABILITY GAUGE
#=======================

#Quelle ChatGPT für die Struktur 

with col22: 

    import plotly.graph_objects as go

    pass_probability = score 

    if 0 <= pass_probability <= 34:
        color = "#e57373"
    elif 35 <= pass_probability <= 70:
        color = "#ffd54f"
    else: 
        color = "#81c784"

 #Die Farben entsprechen mehr oder weniger den Dritteln von 100        

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


#=============================
# PERSONALIZED RECOMMENDATIONS
#=============================

#Hier werden die Tipps angezeigt 
#Die Tipps basieren sich auf Studien, die unten erwähnt werden 
#Es wird immer eins von drei Tipps für jede Variable gezeigt, je nach erreichten Punkten 
#Die Tipps werden zuerst in einer Liste zusammengefasst, damit die Visualisierung dann einfacher für Python ist 
#Jeder User erhält also eine eigene Liste je nach seinen Variablen 

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
#Quelle Schlaf Tipps: Okano, K., Kaczmarzyk, J. R., Dave, N., Gabrieli, J. D. E., & Grossman, J. C. (2019). Sleep quality, duration, and consistency are associated with better academic performance in college students. npj Science of Learning, 4(1), Artikel 16. https://doi.org/10.1038/s41539-019-0055-z

if plernzeit == 4:
    tipps.append("Weiter so! Nutze deine Lernzeit möglichst effizient, indem du sie gezielt einsetzt, damit du deine Energie optimal nutzen kannst")
elif plernzeit == 2:
    tipps.append("Mit nur 30 Minuten zusätzlicher Lernzeit und einem klaren Fokus, kannst du deine Lernziele künftig effizienter und entspannter erreichen.")
elif plernzeit == 1:
    tipps.append("Beginne heute mit einer kleinen, aber fokussierten Lerneinheit in einer ruhigen Umgebung. So findest du wieder zu deinem Lernrhythmus und kommst deinen Lernzielen einen grossen Schritt näher")
#Quelle Lernzeit Tipps: Bensberg, G., & Messer, J. (2014). Zeitmanagement. In Survivalguide Bachelor (S. 109–119). Springer Berlin Heidelberg. https://doi.org/10.1007/978-3-642-39027-2_14$

if pstress1 == 4:
    tipps.append("Du scheinst alles im Griff zu haben, nutze deine Ruhe um bei einem schwierigen Thema voranzukommen")
elif pstress1 == 2: 
    tipps.append("Du fühlst dich etwas überwältigt, priorisiere heute nur die drei wichtigsten Aufgaben und lass dir von uns ein Lernplan erstellen")
elif pstress1 == 1:
    tipps.append("Du fühlst dich überbelastet, streiche unnötige To-dos und fokussiere dich auf die wichtigsten Lernziele")
#Quelle Stress Tipps:Deng, Y., Cherian, J., Khan, N. U. Z., Kumari, K., Ali, N. M., Sial, M. S., Comite, U., & Aldushari, F. (2022). Family and academic stress and their impact on students’ depression level and academic performance. Frontiers in Psychiatry, 13, Artikel 869337. https://doi.org/10.3389/fpsyt.2022.869337


if pbild == 4: 
    tipps.append("Behalte die niedrige Bildschirmzeit, sie hilft dir komplexe Lerninhalte schneller zu verarbeiten")
elif  pbild == 2:
    tipps.append("Du hast eine erhöhte Bildschirmzeit,  versuche deshalb 30min vor dem Schlafen und in deinen Lenrpausen bewusst auf dein Handy zu verzichten")
elif pbild == 1:
    tipps.append("Du benötigst ein digital Detox, schalte beim Lernen alle Benachtitigungen aus und lege dein Handy ausser Sichtweite")
#Quelle Bildschirmzeit Tipps:Chen, J., & Li, H. (2025). A meta-analysis of the impact of technology related factors on students' academic performance. Frontiers in Psychology, 16, Artikel 1524645. https://doi.org/10.3389/fpsyg.2025.1524645

if philfe == 4:
    tipps.append("Du hast ein solides Verständnis, festige dein Wissen indem du deinen Mitstudenten den Inhalt erklärst oder Altklausuren löst")
elif philfe == 2:
    tipps.append("Fülle wenn möglich Altklausuren aus, und prüfe welche Lücken du selber schliessen kannst und für welche Themen du Nachhilfe benötigst") 
elif philfe == 1:
    tipps.append("Wenn du das Gefühl hast, dass du bestimmte Themen nicht selbst erarbeiten kannst, hole dir rechtzeitig Hilfe in einem Tutorium oder von einer Nachhilfelehrkraft")
#Quelle Nachhilfe Tipps:  Weydenhammer, N. (2015). Wirksamkeitsfacetten von Nachhilfe in Deutschland und den USA: Eine Ländervergleichende Studie. ProQuest Dissertations & Theses.https://epub.uni-bayreuth.de/id/eprint/2141/1/Dissertation_finale%20Version.pdf

if ppausen == 4:
    tipps.append("Du hast das optimale Balance zwischen  Lernen und Pausen. Nutze deine Pausen  um an die frische Luft zu gehen und neue Energie zu tanken")
elif ppausen == 2:
    tipps.append("Du arbeitest zu lange am Stück, probiere die Pomodero-Technik aus ( 25min lernen und 5min Pause)")   
elif ppausen == 1:
    tipps.append("Pausen sind esentiell für dein Gehirn, gönne dir heute noch eine  30-60min handyfreie Pause.")
#Quelle Pausen Tipps: Biwer, F., Menko, R., Groeneveld, S., & de Bruin, A. (2025). Investigating the effectiveness of self-regulated, Pomodoro, and Flowtime break-taking techniques among students. Behavioral Sciences, 15(7), Artikel 861. https://doi.org/10.3390/bs15070861

if pfail == 2: 
    tipps.append("Deine Lernstrategie scheint gut zu funktionieren und lass dir einen Lernplan von uns erstellen um dich möglichst effizient vorzubereiten")
elif pfail == 1: 
    tipps.append("Analysiere deine Fehlerquelle, suche dir rechtzeitig eine Lerngruppe  und tausche dich mit anderen aus")
elif pfail == 1:
    tipps.append("Hole dir Hilfe von der Studienberatung oder einem Mentor um das Semster erfolgreich abzuschliessen")  
#Quelle Nicht bestandene Fächer:Petri.P.S(2020). Das Individuum im Fokus: Was wissen wir eigentlich über individuelle Gelingensbedingungen für ein Studium? Ergebnisse empirischer Primärstudien und Metaanalyse zu Studienerfolg und Studienabbruch. https://www.researchgate.net/publication/343344251_Petri_P_S_2020_Das_Individuum_im_Fokus_Was_wissen_wir_eigentlich_uber_individuelle_Gelingensbedingungen_fur_ein_Studium_Ergebnisse_empirischer_Primarstudien_und_Metaanalysen_zu_Studienerfolg_und_Studi

if pfreetime == 2:
    tipps.append("Du hast eine gute Balance zwischen deinem Uni und deinem Privatleben. Das erhöht deine kognitive Leistungsfähigkeit. Weiter so!")
elif pfreetime == 1:
    tipps.append("Gönne dir etwas Abwechslung vom lernen, plane dieses Wochenende bewusst eine Aktivität ein die nichts mit der Uni zu tun hat.")
elif pfreetime == 0.5:
    tipps.append("Es fehlt dir an der nötigen Balance zwischen Uni und Privatleben. Triff dich in den nächsten Tagen mit Freunden oder nimm dir heute Abend etwas Zeit für dich")    
#Quelle Freizeit Tipps: Bensberg, G., & Messer, J. (2014). Zeitmanagement. In Survivalguide Bachelor (S. 109–119). Springer Berlin Heidelberg. https://doi.org/10.1007/978-3-642-39027-2_14

if ppendel == 2: 
    tipps.append("Du hast Glück mit deinem kurzen Fahrtweg, dies gibt dir mehr Zeit für Schlaf oder Freizeitaktivitäten.")
elif ppendel == 1:
    tipps.append("Nutze die Fahrt um mit Karteikarten zu lernen oder für ein kurzes Quiz.") 
elif ppendel == 0.5: 
    tipps.append("Du hast einen langen Fahrtweg, lass dich von dem nicht stressen. Nutze die Zeit bewusst für ein Quiz oder ein fachbezogenes Hörbuch")                       
#Quelle Pendelzeit Tipps:Bensberg, G., & Messer, J. (2014). Zeitmanagement. In Survivalguide Bachelor (S. 109–119). Springer Berlin Heidelberg. https://doi.org/10.1007/978-3-642-39027-2_14

if pfood == 2:
    tipps.append("Du ernährst dich ideal.Behalte deine Routine bei und achte auch eine ausreichende Hydrierung.")
elif pfood == 1:
    tipps.append("Eine gesunde Ernährung wirkt sich auf deinen Lernerfolg aus nutze Brainfood wie Nüsse oder Obst zwischen in den Lernpausen")
elif pfood == 0.5:
    tipps.append("Ohne eine ausgewogene Ernährung, hat dein Körper nicht die benötigte Energie, iss 3 feste Mahlzeiten mit Früchten/Gemüse")
#Quelle Ernährung Tipps:López-Gil, J. F., García-Hermoso, A., Smith, L., Firth, J., Trott, M., Mesas, A. E., Jimenez-Lopez, E., Gutierrez-Espinoza, H., Tárraga-López, P. J., & Victoria-Montesinos, D. (2022). Association between eating habits and perceived school performance: A cross-sectional study among 46,455 adolescents from 42 countries. Frontiers in Nutrition, 9, Artikel 797415. https://doi.org/10.3389/fnut.2022.797415


if psport == 2:
    tipps.append("Behalte die regelmässige Bewegung bei, sie fördert deine Durchblutung und hilft dir die Lerninhalte optimal aufzunehmen und konzentriert zu bleiben.")
elif psport == 1:
    tipps.append("Mit Hilfe eines kurzen Spaziergangs oder einem 15-Minütigen Workout kannst du deine Konzentration weiter steigern und noch effizienter lernen.")
elif psport == 0.5:
    tipps.append("Regelmässige Bewegung ist ein wichtiger Faktor für deinen Lernerfolg. Sie hilft dir, konzentriert zu bleiben. Versuche es heute mit einem 30-minütigen Spaziergang oder einem Workout")        
#Quelle Sport Tipps: Wang, F., & Zhang, L. (2023). Exercise makes better mind: A data mining study. Frontiers in Psychology, 14, Artikel 1271431. https://doi.org/10.3389/fpsyg.2023.1271431

#===================================
# DISPLAY RECOMMENDATIONS IN COLUMNS
#===================================

#Hier werden die Tipps gemäss der Liste gezeigt 

cols = st.columns(2)
for i, tipp in enumerate(tipps):
    with cols[i%2]:
        st.write("")
        st.success(tipp)

st.divider() 
st.write("")

#======================
# FINAL SUCCESS MESSAGE
#======================

st.subheader("Wir wünschen dir ganz viel Erfolg!") 


   
