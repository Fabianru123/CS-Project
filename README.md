# 📊 Studyscore – HSG Bachelor-Projekt

Eine Python-App mit Streamlit, die Studierenden hilft, ihren Studienerfolg zu tracken.

## Features

| Screen | Funktion |
|---|---|
| 🏠 **Onboarding** | Name, Lernstunden, Schlaf, Motivation eingeben |
| ✅ **Weekly Check-in** | 4-Fragen-Quiz → neuer Score wird berechnet |
| 📅 **Exam Planner** | Prüfungen eintragen + automatischer Lernplan |
| 💡 **Tipps** | Personalisierte Empfehlungen basierend auf deinen Angaben |
| 📊 **Dashboard** | Radar-Chart, Donut-Score, Score-Verlauf, Verbesserungsmassnahmen |

## Setup

### 1. Python installieren
Stelle sicher, dass Python 3.9+ installiert ist:
```bash
python --version
```

### 2. Virtuelle Umgebung erstellen (empfohlen)
```bash
python -m venv venv

# macOS / Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 4. App starten
```bash
streamlit run app.py
```

Die App öffnet sich automatisch im Browser unter `http://localhost:8501`.

## Projektstruktur

```
studyscore/
├── app.py              # Hauptdatei (komplette App)
├── requirements.txt    # Python-Abhängigkeiten
└── README.md           # Diese Datei
```

## Score-Formel

Der Studyscore (Pass Probability) wird berechnet aus:

```
score = base + (lernstunden − 5) × 2.5
              − fehlstunden × 0.8
              + (schlaf − 7) × 1.5
              + (motivation − 3) × 1.0
```

Begrenzt auf den Bereich **10–99**.

## Technologien

- **Python 3.12**
- **Streamlit** – Web-App-Framework
- **Plotly** – Interaktive Charts (Radar, Donut, Line)

---
*HSG Bachelor-Projekt – Studyscore*
