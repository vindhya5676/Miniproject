import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from googletrans import Translator
from fpdf import FPDF
import tempfile
import os

# --- Load Data ---
translator = Translator()

@st.cache_data
def load_data():
    df = pd.read_csv("dataset.csv")
    df.columns = df.columns.str.strip().str.lower()
    if "patient_id" in df.columns:
        df["patient_id"] = df["patient_id"].astype(str).str.strip().str.upper()
    if "doctor_id" in df.columns:
        df["doctor_id"] = df["doctor_id"].astype(str).str.strip().str.upper()
    return df

df = load_data()

# --- App Title ---
st.title("Hospital Discharge Summary System")

# --- Doctor Verification ---
st.sidebar.header("🔒 Doctor Verification")
doctor_id_input = st.sidebar.text_input("Enter your Doctor ID:")

if st.sidebar.button("Verify Doctor"):
    if doctor_id_input in df["doctor_id"].unique():
        st.session_state["doctor_verified"] = True
        st.session_state["doctor_id"] = doctor_id_input
        st.sidebar.success("Doctor verified successfully!")
    else:
        st.session_state["doctor_verified"] = False
        st.sidebar.error("Doctor ID not found or not registered.")

# Stop execution until doctor is verified
if "doctor_verified" not in st.session_state or not st.session_state["doctor_verified"]:
    st.warning("Please verify your Doctor ID to access patients.")
    st.stop()

# --- Language Selection ---
language_options = {
   "English": "en","Hindi": "hi","Bengali": "bn","Telugu": "te",
    "Marathi": "mr","Tamil": "ta","Gujarati": "gu","Urdu": "ur",
    "Kannada": "kn","Odia": "or","Malayalam": "ml","Punjabi": "pa",
    "Assamese": "as","Maithili": "mai","Sanskrit": "sa","Tulu": "tcy"
}
selected_lang = st.selectbox("🌐 Select Language:", list(language_options.keys()))
lang_code = language_options[selected_lang]

def tr(text):
    if lang_code == "en":
        return text
    try:
        return translator.translate(text, dest=lang_code).text
    except:
        return text

# --- PDF Generation Function ---
def generate_pdf(patient, recovery_scores, x_labels, summary, meds_df, diet_df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Hospital Discharge Summary", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(5)

    for col in patient.index:
        pdf.multi_cell(0, 8, f"{col.replace('_',' ').title()}: {patient[col]}")

    pdf.ln(5)
    # Recovery Graph
    fig, ax = plt.subplots(figsize=(6,3))
    ax.plot(x_labels, recovery_scores, marker="o", color="blue", linewidth=2)
    ax.set_title(f"Recovery Progress: {patient['first_name']} {patient['last_name']}")
    ax.set_xlabel("Date / Day")
    ax.set_ylabel("Recovery Score (%)")
    ax.set_ylim(0, 110)
    ax.grid(True)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_img_path = os.path.join(tmpdir, "recovery_graph.png")
        fig.savefig(tmp_img_path, format="png")
        plt.close(fig)
        pdf.image(tmp_img_path, x=20, w=170)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Doctor Summary:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, summary)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Medications:", ln=True)
    pdf.set_font("Arial", "", 12)
    for _, row in meds_df.iterrows():
        pdf.multi_cell(0, 8, f"{row['Medicine']} - {row['Dosage']} - {row['Timing']}")

    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Diet Plan:", ln=True)
    pdf.set_font("Arial", "", 12)
    for _, row in diet_df.iterrows():
        pdf.multi_cell(0, 8, f"{row['Meal']} - {row['Quantity']} - {row['Timing']}")

    return pdf.output(dest="S").encode("latin1")

# --- Filter Patients for Logged Doctor ---
doctor_id = st.session_state["doctor_id"]
doctor_patients = df[df["doctor_id"] == doctor_id]

if doctor_patients.empty:
    st.error("No patients assigned to this doctor.")
    st.stop()

# --- Patient Selection ---
patient_ids = doctor_patients["patient_id"].unique().tolist()
patient_id = st.selectbox("Select Patient ID:", patient_ids)

if st.button("Get Summary"):
    patient_idx = doctor_patients[doctor_patients["patient_id"] == patient_id].index[0]
    patient = doctor_patients.loc[patient_idx]

    st.session_state['patient_idx'] = patient_idx
    st.session_state['patient'] = patient

    num_days = 7
    seed = int(''.join([str(ord(c)) for c in patient_id]))
    rng = np.random.default_rng(seed)
    recovery_scores = np.cumsum(rng.integers(5, 15, size=num_days))
    recovery_scores = np.clip(recovery_scores, 0, 100)
    st.session_state['recovery_scores'] = recovery_scores

    try:
        start_date = datetime.strptime(patient['registration_date'], "%Y-%m-%d")
        dates = [start_date + timedelta(days=i) for i in range(num_days)]
        x_labels = [d.strftime("%d-%b") for d in dates]
    except:
        x_labels = list(range(1, num_days+1))
    st.session_state['x_labels'] = x_labels

    # Display patient info
    st.subheader(tr("Patient Discharge Summary"))
    for col in ['first_name','last_name','gender','date_of_birth','age','sex','disease','symptoms_text','lab_summary','address','contact_number','email','registration_date','insurance_provider','insurance_number']:
        if col in patient:
            st.write(f"**{tr(col.replace('_',' ').title())}:** {patient[col]}")

    # Plot recovery
    plt.figure(figsize=(8,4))
    plt.plot(x_labels, recovery_scores, marker="o", color="blue", linewidth=2)
    plt.title(tr(f"Recovery Progress: {patient['first_name']} {patient['last_name']}"))
    plt.xlabel(tr("Date / Day"))
    plt.ylabel(tr("Recovery Score (%)"))
    plt.ylim(0, 110)
    plt.grid(True)
    st.pyplot(plt)

    # AI summary
    st.subheader(tr("AI-generated Summary"))
    last_score = recovery_scores[-1]
    if last_score >= 100:
        ai_summary = f"{patient['first_name']} {patient['last_name']} has fully recovered from {patient['disease']}."
    else:
        remaining = 100 - last_score
        avg_inc = np.mean(np.diff(recovery_scores))
        est_days = int(np.ceil(remaining / avg_inc))
        ai_summary = f"{patient['first_name']} {patient['last_name']} is recovering from {patient['disease']}. Full recovery estimated in {est_days} days."
    st.session_state['edited_summary'] = ai_summary

    # AI Prescribed Medications table
    meds_df = pd.DataFrame({
        "Medicine": ["Paracetamol", "Amoxicillin", "Vitamin C"],
        "Dosage": ["500mg", "250mg", "500mg"],
        "Timing": ["Twice a day", "Once a day", "Once a day"]
    })
    st.session_state['meds_df'] = meds_df

    # AI Prescribed Diet table
    diet_df = pd.DataFrame({
        "Meal": ["Breakfast", "Lunch", "Dinner"],
        "Quantity": ["1 bowl oats", "Rice + Veg", "Soup + Bread"],
        "Timing": ["8:00 AM", "1:00 PM", "7:00 PM"]
    })
    st.session_state['diet_df'] = diet_df

# --- Editable Summary and Tables ---
if 'patient' in st.session_state:
    edited_summary = st.text_area(tr("Edit Summary (Doctor):"), value=st.session_state['edited_summary'], height=120)
    st.session_state['edited_summary'] = edited_summary

    st.subheader("Medications (Editable)")
    st.session_state['meds_df'] = st.data_editor(st.session_state['meds_df'], num_rows="dynamic")

    st.subheader("Diet Plan (Editable)")
    st.session_state['diet_df'] = st.data_editor(st.session_state['diet_df'], num_rows="dynamic")

    if st.button("Save Summary"):
        idx = st.session_state['patient_idx']
        df.loc[idx, "doctor_summary"] = edited_summary
        df.to_csv("merged_patient_data_with_summary.csv", index=False)
        st.success("Summary saved successfully!")

    st.download_button(
        label="Download Complete Discharge Summary PDF",
        data=generate_pdf(
            st.session_state['patient'],
            st.session_state['recovery_scores'],
            st.session_state['x_labels'],
            st.session_state['edited_summary'],
            st.session_state['meds_df'],
            st.session_state['diet_df']
        ),
        file_name=f"{patient_id}_discharge_summary.pdf",
        mime="application/pdf"
    )
