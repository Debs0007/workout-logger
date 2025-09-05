import streamlit as st
import pandas as pd
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# ==============================
# Google Sheets Setup
# ==============================
SHEET_NAME = "Workout Logs"  # must match the name of your sheet
CREDENTIALS_FILE = "credentials.json"

# Define scope

scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]

# Load credentials from Streamlit secrets
creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1  # first sheet/tab

# ==============================
# Movement Library
# ==============================
movement_library = {
    "Biceps": {
        26: "Barbell Curl",
        27: "Dumbbell Curls",
        28: "Ez-bar Curls",
        29: "Dumbbell Hammer Curls"
    },
    "Back": {
        7: "Pull Ups",
        8: "Landmine Row",
        9: "Lat Pulldown",
        10: "Single Hand Dumbbell Rows",
        11: "Barbell Bentover Row"
    },
    "Legs": {
        12: "Barbell Squat",
        13: "Dumbbell Lunges",
        14: "Bulgarian Split Squat",
        15: "Dumbbell Calves Raises",
        16: "Leg Extension",
        17: "Deadlift",
        18: "Dumbbell Romainan Deadlift"
    },
    "Shoulders": {
        19: "Dumbbell Shrugs",
        20: "Dumbbell Front Raises",
        21: "Dumbbell Rear Delt Flies",
        22: "Dumbbell Lateral Raises",
        23: "Barbell Shrugs",
        24: "Barbell Military Press",
        25: "Dumbbell Military Press"
    },
    "Chest": {
        1: "Flat Barbell Bench Press",
        2: "Flat Dumbbell Bench Press",
        3: "Dips",
        4: "Dumbbell Inclined Bench Press",
        5: "Barbell Inclined Bench Press",
        6: "Flat Dumbbell Flies"
    },
    "Triceps": {
        30: "Dumbbell Triceps Extension",
        31: "Barbell Skull Crusher",
        32: "Ez-bar Skull Crusher",
        33: "Tricep Pushdown"
    },
    "Forearm": {
        34: "Barbell Forearm Curls"
    }
}

st.title("🏋️ Workout Log Entry App")

# Session info
date = st.date_input("Select workout date", datetime.date.today())
time = st.time_input("Workout start time", datetime.time(16, 0))
session_id = st.number_input("Session ID", min_value=1, value=1, step=1)

# Exercise entry
body_part = st.selectbox("Body Part", list(movement_library.keys()))

# Create list of "id - name" options
movement_options = [f"{mid} - {name}" for mid, name in movement_library[body_part].items()]
movement_choice = st.selectbox("Movement", movement_options)

# Split back into ID and Name
movement_id = int(movement_choice.split(" - ")[0])
movement_name = movement_choice.split(" - ")[1]

set_number = st.number_input("Set Number", min_value=1, value=1)
weight = st.number_input("Weight", min_value=0.0, value=0.0, step=0.5)
weight_unit = st.selectbox("Weight Unit", ["kg", "lbs"])
reps = st.number_input("Reps", min_value=1, value=10)
rest_seconds = st.number_input("Rest (seconds)", min_value=0, value=120)
is_pr = st.checkbox("Personal Record (PR)")
workout_minutes = st.number_input("Workout Minutes", min_value=0, value=10)
notes = st.text_area("Notes")

# Store session entries in state
if "workout_data" not in st.session_state:
    st.session_state.workout_data = []

if st.button("➕ Add Exercise"):
    new_entry = {
        "date": datetime.datetime.combine(date, time),
        "session_id": session_id,
        "body_part": body_part,
        "movement_id": movement_id,
        "movement_name": movement_name,
        "set_number": set_number,
        "weight": weight,
        "weight_unit": weight_unit,
        "reps": reps,
        "rest_seconds": rest_seconds,
        "is_pr": int(is_pr),
        "workout_minutes": workout_minutes,
        "notes": notes
    }
    st.session_state.workout_data.append(new_entry)
    st.success(f"Added {movement_name} ✅")

# Show table
df = pd.DataFrame(st.session_state.workout_data)
st.dataframe(df)

# Save to Google Sheets
if st.button("💾 Save Session to Google Sheets"):
    if not df.empty:
        for _, row in df.iterrows():
            sheet.append_row(list(row.values))
        st.success(f"✅ Session saved to Google Sheets: {SHEET_NAME}")
    else:
        st.warning("⚠️ No data to save!")
