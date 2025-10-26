AI-Powered Patient Discharge System


This project is an AI-powered hospital discharge system that helps doctors automatically generate and download patient discharge summaries with recovery progress, medication details, and diet plans.


1.Requirements:
  Before running the project, make sure you have the following installed:

   - Python 3.8 or higher
   - pip (Python package manager)
   - Streamlit


2.Install Required Libraries:
  Open Command Prompt and run this command to install all dependencies:

  pip install streamlit pandas matplotlib numpy googletrans==4.0.0-rc1 fpdf


3.Folder Structure
  Make sure your project files are arranged like this:

   AI_Discharge_System/
   │
   ├── home.py
   ├── dataset.csv
   └── README.txt


4.dataset.csv Format

  Your dataset must contain these columns:

    patient_id, doctor_id, first_name, last_name, gender, date_of_birth, age, sex,
    disease, symptoms_text, lab_summary, address, contact_number, email,
    registration_date, insurance_provider, insurance_number


5.How to Run the App

   Step 1: Open Command Prompt and navigate to your project folder.

     cd path\to\AI_Discharge_System

   Step 2: Run the following command:

     python -m streamlit run home.py


   Step 3: The app will automatically open in your default web browser.


6.How to Use

    1. Enter your Doctor ID in the sidebar and verify.
    2. Choose a Patient ID from the dropdown list.
    3. Click “Get Summary” to generate the AI-powered discharge summary.
    4. Review and edit the AI-generated text, medications, and diet plan.
    5. Click “Save Summary” to update the records.
    6. Download the PDF report with “Download Complete Discharge Summary PDF”.


7.Features

✔ Doctor verification for secure access
✔ Auto-language translation using Google Translate
✔ AI-generated discharge summary with recovery tracking
✔ Editable medication and diet plan tables
✔ Professional PDF report generation
✔ Saves updated data to merged_patient_data_with_summary.csv


8.Troubleshooting

Problem: ModuleNotFoundError  
Solution: Run pip install module_name

Problem: dataset.csv not found  
Solution: Ensure dataset.csv is in the same folder as home.py

Problem: App not opening automatically  
Solution: Open your browser and visit http://localhost:


