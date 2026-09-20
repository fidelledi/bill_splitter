import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="B27 L16 Bill Manager", layout="wide")

# --- GOOGLE SHEETS CONNECTION ---
# Replace this with your actual Google Sheet URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/105OsVZ5GgD3QxlSP0oqLWU1zrutPPg57Xd0f1eBeNr0/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(spreadsheet=SHEET_URL, usecols=[0,1,2,3,4,5])

# --- UI STYLING ---
st.title("🏠 Family Bill Manager")
st.info("Logic: Palisa pays submetered electricity + ₱500 water. Rillon pays the remainder.")

tab1, tab2 = st.tabs(["🧮 Calculator", "📜 History Log"])

with tab1:
    col_input, col_result = st.columns([1, 1], gap="large")

    with col_input:
        st.subheader("📋 Input Monthly Data")
        billing_month = st.date_input("Billing Month", value=datetime.now()).strftime("%B %Y")
        
        with st.expander("⚡ Electricity Details", expanded=True):
            total_elec_bill = st.number_input("Total Meralco Bill (₱)", min_value=0.0)
            meralco_rate = st.number_input("Meralco Rate (₱/kWh)", min_value=0.0, value=12.0)
            prev_reading = st.number_input("Palisa: Previous Submeter", min_value=0.0)
            curr_reading = st.number_input("Palisa: Current Submeter", min_value=0.0)

        with st.expander("💧 Water Details", expanded=True):
            total_water_bill = st.number_input("Total Water Bill (₱)", min_value=0.0)
            fixed_water_a = 500.0

    # --- CALCULATIONS ---
    kwh_used_a = curr_reading - prev_reading
    elec_share_a = kwh_used_a * meralco_rate
    elec_share_b = max(0.0, total_elec_bill - elec_share_a)
    
    water_share_a = fixed_water_a
    water_share_b = max(0.0, total_water_bill - fixed_water_a)

    total_a = elec_share_a + water_share_a
    total_b = elec_share_b + water_share_b

    with col_result:
        st.subheader(f"📊 Summary for {billing_month}")
        
        st.success(f"**Palisa Total: ₱{total_a:,.2f}**")
        st.caption(f"(Elec: ₱{elec_share_a:,.2f} + Water: ₱{water_share_a:,.2f})")
        
        st.warning(f"**Rillon Total: ₱{total_b:,.2f}**")
        st.caption(f"(Elec: ₱{elec_share_b:,.2f} + Water: ₱{water_share_b:,.2f})")

        if st.button("💾 Save to Google Sheets", use_container_width=True):
            try:
                # Prepare new data
                new_row = pd.DataFrame([{
                    "Month": billing_month,
                    "Total_Elec": total_elec_bill,
                    "Total_Water": total_water_bill,
                    "Fam_A_Total": total_a,
                    "Fam_B_Total": total_b,
                    "Fam_A_kWh": kwh_used_a
                }])
                
                # Fetch existing data and append
                existing_data = load_data()
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                
                # Write back to sheet
                conn.update(spreadsheet=SHEET_URL, data=updated_df)
                st.balloons()
                st.success("Saved to Google Sheets!")
            except Exception as e:
                st.error(f"Error saving: {e}")

with tab2:
    st.subheader("Past Bills")
    try:
        history_df = load_data()
        st.dataframe(history_df.dropna(how='all'), use_container_width=True)
    except:
        st.write("Connect your Google Sheet to see history.")