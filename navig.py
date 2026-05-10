import streamlit as st

homepage = st.Page("homepage.py", title="Homepage", icon="🎓")
profil = st.Page("pages/profil.py", title="Dein Profil", icon="👤")
lernplan = st.Page("pages/lernplan.py", title="Dein Lernplan", icon="🗓️")

pages = st.navigation([homepage, profil, lernplan], position="sidebar")
pages.run()
