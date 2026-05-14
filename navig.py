import streamlit as st

homepage = st.Page("homepage.py", title="Homepage", icon="🎓")
profil = st.Page("profil.py", title="Dein Profil", icon="👤")
lernplan = st.Page("lernplan.py", title="Dein Lernplan", icon="🗓️")

pages = st.navigation([homepage, profil, lernplan], position="sidebar")
pages.run()
