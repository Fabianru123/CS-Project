import streamlit as st

homepage = st.Page("ordner visual /homepage.py", title="Homepage", icon="🎓")
profil = st.Page("ordner visual /pages/profil.py", title="Dein Profil", icon="👤")
lernplan = st.Page("ordner visual /pages/lernplan.py", title="Dein Lernplan", icon="📚")

pages = st.navigation([homepage, profil, lernplan], position="sidebar")
pages.run()
