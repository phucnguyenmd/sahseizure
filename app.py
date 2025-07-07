import streamlit as st
import pandas as pd
import io

# --- 1. Page Configuration & Initial Setup ---

# Configure the Streamlit page with a title, icon, and wide layout for better content spacing.
st.set_page_config(
    page_title="aSAH Seizure Risk Calculator",
    page_icon="🧠",
    layout="wide"
)

# --- 2. Application UI: Title and Sidebar ---

# Main title for the application displayed on the page.
st.title("🧠 aSAH Seizure Risk Calculator")

# A brief explanation of the tool's purpose and usage instructions.
st.markdown("""
This clinical decision support tool calculates the predicted risk of seizure in patients 
with aneurysmal subarachnoid hemorrhage (aSAH). The calculations are based on four distinct
multivariate logistic regression models.

**Instructions:**
1.  Enter the patient's clinical and demographic data in the form on the left sidebar.
2.  Click the "Calculate Risk" button to view the results.
3.  Results for models specific to severe cases (WFNS 4-5) will only appear if the patient meets the criteria.
""")

# Use a sidebar to neatly contain all user input fields.
st.sidebar.header("Patient Input Data")

# --- 3. Input Form ---

# Using st.form() groups input widgets and submits them all with a single button press.
# This prevents the app from re-running on every change to an input widget, improving performance and user experience.
with st.sidebar.form(key="patient_data_form"):
    
    # --- General Input Fields (for all patients) ---
    st.subheader("General Patient Information")

    # WFNS Grade: Numeric input with defined range and help text.
    wfns = st.number_input(
        label="WFNS grade",
        min_value=1, max_value=5, value=1, step=1,
        help="World Federation of Neurological Surgeons grade (1-5)"
    )

    # Modified Fisher Grade: Numeric input with defined range.
    mfisher = st.number_input(
        label="Modified Fisher grade",
        min_value=0, max_value=4, value=0, step=1,
        help="Modified Fisher grade for subarachnoid hemorrhage (0-4)"
    )

    # CRP Level: Floating-point number input.
    crp = st.number_input(
        label="CRP level (mg/L)",
        min_value=0.0, value=10.0, format="%.1f",
        help="C-reactive protein level in mg/L"
    )

    # --- Checkbox Inputs (Boolean variables converted to 1/0) ---
    st.subheader("Clinical Factors (Check if Present)")

    ld = st.checkbox("Lumbar Drain (LD) present")
    clipping = st.checkbox("Surgical Clipping performed (vs. Coiling/None)")
    seizure_early_input = st.checkbox("History of Early Seizure")
    eeg_abnormal = st.checkbox("Abnormal EEG finding")
    hcp = st.checkbox("Chronic Hydrocephalus (HCP) present")
    ich = st.checkbox("Intracerebral Hemorrhage (ICH) present")
    
    # The submit button for the form. When clicked, the code below this block will execute.
    calculate_button = st.form_submit_button(label="Calculate Risk")

# The "Reset" functionality is handled by the user simply changing the inputs and recalculating.
# This is an idiomatic Streamlit approach and avoids complex state management for a simple reset button.

# --- 4. Logic & Output Display ---

# This block executes only when the "Calculate Risk" button inside the form is clicked.
if calculate_button:
    
    # --- Data Conversion ---
    # Convert boolean checkbox values to integers (1 for True, 0 for False) for calculations.
    ld_val = 1 if ld else 0
    clipping_val = 1 if clipping else 0
    seizure_early_val = 1 if seizure_early_input else 0
    eeg_abnormal_val = 1 if eeg_abnormal else 0
    hcp_val = 1 if hcp else 0
    ich_val = 1 if ich else 0

    # --- Model Calculations ---
    
    # Model 1: Early seizure (general model)
    model1_score = (0.62 * wfns) + (0.88 * mfisher) + (0.07 * crp) + (-1.9 * ld_val) + (1.19 * clipping_val)
    
    # Model 2: Late seizure (general model)
    model2_score = (1.75 * wfns) + (1.89 * seizure_early_val)

    # --- Display Header for Results ---
    st.header("Risk Score Results")
    st.info("ℹ️ **Interpretation**: A higher calculated score corresponds to a higher predicted risk of seizure. The Area Under the Curve (AUC) indicates the model's predictive accuracy.")
    
    # Use columns to display results in a clean, organized layout.
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Model 1: Early Seizure (General)")
        st.metric(label="Predicted Risk Score", value=f"{model1_score:.2f}")
        st.text("Model AUC: 0.87")

    with col2:
        st.subheader("Model 2: Late Seizure (General)")
        st.metric(label="Predicted Risk Score", value=f"{model2_score:.2f}")
        st.text("Model AUC: 0.88")

    st.divider() # Visual separator

    # --- Conditional Logic for WFNS 4-5 Group ---
    # Models 3 and 4 are only calculated and displayed if the WFNS grade is 4 or 5.
    
    if wfns >= 4:
        st.subheader("WFNS 4-5 Specific Models")
        
        # Calculate scores for models 3 and 4
        model3_score = (1.47 * wfns) + (1.13 * mfisher) + (1.92 * eeg_abnormal_val)
        model4_score = (2.83 * wfns) + (1.18 * mfisher) + (2.81 * hcp_val) + (1.63 * ich_val) + (1.48 * seizure_early_val)

        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("Model 3: Early Seizure (WFNS 4-5)")
            st.metric(label="Predicted Risk Score", value=f"{model3_score:.2f}")
            st.text("Model AUC: 0.81")

        with col4:
            st.subheader("Model 4: Late Seizure (WFNS 4-5)")
            st.metric(label="Predicted Risk Score", value=f"{model4_score:.2f}")
            st.text("Model AUC: 0.88")
            
        # Store all results for the download feature
        results_data = {
            'Input_WFNS': [wfns], 'Input_mFisher': [mfisher], 'Input_CRP': [crp],
            'Input_LD': [ld_val], 'Input_Clipping': [clipping_val], 'Input_EarlySeizure': [seizure_early_val],
            'Input_EEG_Abnormal': [eeg_abnormal_val], 'Input_HCP': [hcp_val], 'Input_ICH': [ich_val],
            'Model1_Early_General_Score': [f"{model1_score:.2f}"],
            'Model2_Late_General_Score': [f"{model2_score:.2f}"],
            'Model3_Early_WFNS4-5_Score': [f"{model3_score:.2f}"],
            'Model4_Late_WFNS4-5_Score': [f"{model4_score:.2f}"]
        }

    else:
        st.warning("Models 3 and 4 are not applicable as the patient's WFNS grade is less than 4.")
        
        # Store only general model results for the download feature
        results_data = {
            'Input_WFNS': [wfns], 'Input_mFisher': [mfisher], 'Input_CRP': [crp],
            'Input_LD': [ld_val], 'Input_Clipping': [clipping_val], 'Input_EarlySeizure': [seizure_early_val],
            'Input_EEG_Abnormal': [eeg_abnormal_val], 'Input_HCP': [hcp_val], 'Input_ICH': [ich_val],
            'Model1_Early_General_Score': [f"{model1_score:.2f}"],
            'Model2_Late_General_Score': [f"{model2_score:.2f}"],
            'Model3_Early_WFNS4-5_Score': ['N/A'],
            'Model4_Late_WFNS4-5_Score': ['N/A']
        }

    st.divider()

    # --- 5. Optional Feature: Export to CSV ---
    
    # Create a Pandas DataFrame from the results dictionary.
    results_df = pd.DataFrame(results_data)
    
    # Convert DataFrame to a CSV string in memory.
    # The `io.StringIO` is used to treat the string as a file for consistent handling.
    csv_buffer = io.StringIO()
    results_df.to_csv(csv_buffer, index=False)
    csv_string = csv_buffer.getvalue()

    # Provide a download button for the generated CSV file.
    st.download_button(
       label="📥 Download Results as CSV",
       data=csv_string,
       file_name=f"aSAH_risk_results_WFNS_{wfns}.csv",
       mime="text/csv",
    )
