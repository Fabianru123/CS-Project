# ============================================
# ML MODEL: Logistic Regression
# Claude has been used to help with the structure
# ============================================
 
 
# ============================================
# IMPORTS
# os: To check if the model file already exists
# pandas: To read the CSV and prepare the data
# joblib: To save and load the trained model
# sklearn.linear_model.LogisticRegression: The model itself
# sklearn.model_selection.train_test_split: Split training and test data
# ============================================
 
import os
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
 
 
# ============================================
# Configuration: Dataset, Model-file and Feature Names
# File names and the 7 features our model uses (same as in app.py)
# ============================================
 
DATASET_FILE = "student-por.csv"
MODEL_FILE = "model.pkl"
 
# ============================================
# Variables of the UCI dataset that we use as features in our model
# ============================================
FEATURE_NAMES = [
    "plernzeit",     # Lernzeit         (UCI-Spalte: studytime)
    "pgesund",       # Gesundheit       (UCI-Spalte: health)
    "philfe",        # Nachhilfe        (UCI-Spalte: schoolsup)
    "pfail",         # Misserfolge      (UCI-Spalte: failures)
    "pfreetime",     # Freizeit         (UCI-Spalte: freetime)
    "pgoout",        # Alkohol          (UCI-Spalte: Dalc)
    "ppendel",       # Pendelzeit       (UCI-Spalte: traveltime)
]
 
 
# ============================================
# Helper Functions: Conversion von UCI-Values into points
# ============================================
 
def studytime_to_points(value):
    """Convert UCI studytime value to points.
    UCI: 1 = <2h/Woche, 2 = 2-5h, 3 = 5-10h, 4 = >10h
    """
    if value == 4:
        return 4
    elif value == 3:
        return 2
    else:
        return 1
 
 
def health_to_points(value):
    """Convert UCI health value to points.
    UCI: 1 = very bad ... 5 = very good
    """
    if value >= 4:
        return 4
    elif value == 3:
        return 2
    else:
        return 1
 
 
def schoolsup_to_points(value):
    """Convert UCI schoolsup value to points.
    UCI: "yes" or "no"
    """
    if value == "yes":
        return 4
    else:
        return 1
 
 
def failures_to_points(value):
    """Convert UCI failures value to points.
    UCI: Number of past failed courses (0 to 4)
    """
    if value == 0:
        return 2
    elif value <= 2:
        return 1
    else:
        return 0.5
 
 
def freetime_to_points(value):
    """Convert UCI freetime value to points.
    UCI: 1 = very little ... 5 = very much (3 is optimal)
    """
    if value == 3:
        return 2
    elif value == 4:
        return 1
    else:
        return 0.5
 
 
def dalc_to_points(value):
    """Convert UCI dalc value to points.
    UCI: Weekly alcohol consumption 1 (very little) to 5 (very much)"""
    if value <= 2:
        return 2
    elif value == 3:
        return 1
    else:
        return 0.5
 
 
def traveltime_to_points(value):
    """Convert UCI traveltime value to points.
    UCI: 1 = <15min, 2 = 15-30min, 3 = 30-60min, 4 = >60min
    """
    if value <= 2:
        return 2
    elif value == 3:
        return 1
    else:
        return 0.5
 
 
# ============================================
# STEP 2: Load data and prepare it for the model
# Read CSV and convert values, derive label from final grade
# ============================================
 
def prepare_data():
    """Prepare data for the model.
    Read CSV and convert values, derive label from final grade.
    """
    df = pd.read_csv(DATASET_FILE, sep=";")
 
    # New empty DataFrame for the 7 variables
    X = pd.DataFrame()
    X["plernzeit"] = df["studytime"].apply(studytime_to_points)
    X["pgesund"] = df["health"].apply(health_to_points)
    X["philfe"] = df["schoolsup"].apply(schoolsup_to_points)
    X["pfail"] = df["failures"].apply(failures_to_points)
    X["pfreetime"] = df["freetime"].apply(freetime_to_points)
    X["pgoout"] = df["Dalc"].apply(dalc_to_points)
    X["ppendel"] = df["traveltime"].apply(traveltime_to_points)
 
    # Label (target variable): End Score G3 is 0-20.
    # Passed = 1 if G3 >= 10, otherwise 0.
    y = (df["G3"] >= 10).astype(int)
 
    return X, y
 
 
# ============================================
# STEP 3: Modell training
# Logistic Regression
# ============================================
 
def train_model():
    # Step 1: Data preparation
    X, y = prepare_data()
    print("Anzahl Schüler im Datensatz:", len(X))
    print("Davon bestanden:", y.sum())
 
    # Step 2: Split training and test data (80% Training / 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
 
    # Step 3: Model training
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
 
    # Step 4: Accuracy check
    train_accuracy = model.score(X_train, y_train)
    test_accuracy = model.score(X_test, y_test)
    print("Training Accuracy:", round(train_accuracy, 3))
    print("Test Accuracy:", round(test_accuracy, 3))
 
    # Step 5: Save model as file
    joblib.dump(model, MODEL_FILE)
    print("Modell gespeichert in:", MODEL_FILE)
 
 
# ============================================
# STEP 4: Prediction Functions
# These are imported and called in the app with user inputs
# ============================================
 
def predict_pass_probability(points_dict):
    """If the model file doesn't exist yet (first run), train the model first"""
    if not os.path.exists(MODEL_FILE):
        train_model()
 
    # Model load out of file
    model = joblib.load(MODEL_FILE)
 
    # Points in the correct order for the model (same order as in FEATURE_NAMES)
    features = []
    for name in FEATURE_NAMES:
        features.append(points_dict[name])
 
    # Prediction: Probability for the class "passed" (= 1)
    probability = model.predict_proba([features])[0][1]
 
    # From 0–1 to percentage (0–100)
    return probability * 100
 
 
def get_feature_importance():
    """Load the trained model and return feature importance."""
    if not os.path.exists(MODEL_FILE):
        train_model()
    model = joblib.load(MODEL_FILE)
 
    # Feature Importance: To provide the model coefficients for each feature (higher = more important)
    importance = {}
    for i in range(len(FEATURE_NAMES)):
        importance[FEATURE_NAMES[i]] = model.coef_[0][i]
    return importance
 
 
# ============================================
# RUN: Will only be processed if python ml_model.py is called, not when imported in app.py
# ============================================
 
if __name__ == "__main__":
    train_model()