import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Palisa Bill Manager", layout="wide")

# --- GOOGLE SHEETS CONNECTION ---
# Replace this with your actual Google Sheet URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/105OsVZ5GgD3QxlSP0oqLWU1zrutPPg57Xd0f1eBeNr0/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        return conn.read(spreadsheet=SHEET_URL)
    except:
        return pd.DataFrame()

# --- UI STYLING ---
st.title("🏠 BLK 27 L16 Bill Splitter")
st.markdown("---")

tab1, tab2 = st.tabs(["🧮 Calculator", "📜 History Log"])

with tab1:
    col_input, col_result = st.columns([1, 1.2], gap="large")

    with col_input:
        st.subheader("📋 Monthly Inputs")
        billing_month = st.date_input("Billing Month", value=datetime.now()).strftime("%B %Y")
        
        with st.expander("⚡ Electricity (Meralco)", expanded=True):
            total_elec_bill = st.number_input("Total Meralco Bill (₱)", min_value=0.0)
            meralco_rate = st.number_input("Meralco Rate (₱/kWh)", min_value=0.0, value=12.0)
            prev_reading = st.number_input("Palisa: Previous Submeter", min_value=0.0)
            curr_reading = st.number_input("Palisa: Current Submeter", min_value=0.0)

        with st.expander("💧 Water & Others", expanded=True):
            total_water_bill = st.number_input("Total Water Bill (₱)", min_value=0.0)
            st.info("Fixed Fees Applied:\n- Water (Palisa): ₱500\n- HOA (Palisa): ₱35\n- Internet: ₱1,499 (Split 50/50)")

    # --- CALCULATIONS ---
    # 1. Electricity
    kwh_used_palisa = curr_reading - prev_reading
    elec_palisa = kwh_used_palisa * meralco_rate
    elec_fam_b = max(0.0, total_elec_bill - elec_palisa)
    
    # 2. Water
    water_palisa = 500.0
    water_fam_b = max(0.0, total_water_bill - water_palisa)
    
    # 3. HOA & Internet
    hoa_palisa = 35.0
    internet_total = 1499.0
    internet_share = internet_total / 2

    # 4. Final Totals
    total_palisa = elec_palisa + water_palisa + hoa_palisa + internet_share
    total_fam_b = elec_fam_b + water_fam_b + internet_share

    with col_result:
        st.subheader(f"📊 Summary for {billing_month}")
        
        # Display Palisa's Column
        res_a, res_b = st.columns(2)
        
        with res_a:
            st.success("### 👤 Palisa")
            st.write(f"⚡ Elec ({kwh_used_palisa:.1f} kWh): **₱{elec_palisa:,.2f}**")
            st.write(f"💧 Water (Fixed): **₱{water_palisa:,.2f}**")
            st.write(f"🏠 HOA (UDHAI): **₱{hoa_palisa:,.2f}**")
            st.write(f"🌐 Internet (50%): **₱{internet_share:,.2f}**")
            st.markdown(f"## **Total: ₱{total_palisa:,.2f}**")
        
        with res_b:
            st.warning("### 👥 Rillon")
            st.write(f"⚡ Elec (Remainder): **₱{elec_fam_b:,.2f}**")
            st.write(f"💧 Water (Remainder): **₱{water_fam_b:,.2f}**")
            st.write(f"🏠 HOA: **₱0.00**")
            st.write(f"🌐 Internet (50%): **₱{internet_share:,.2f}**")
            st.markdown(f"## **Total: ₱{total_fam_b:,.2f}**")

        st.divider()
        if st.button("💾 Save Monthly Record to Google Sheets", use_container_width=True):
            try:
                new_row = pd.DataFrame([{
                    "Month": billing_month,
                    "Total_Elec": total_elec_bill,
                    "Total_Water": total_water_bill,
                    "Palisa_Total": total_palisa,
                    "Rillon_Total": total_fam_b,
                    "Palisa_kWh": kwh_used_palisa,
                    "Internet_Total": internet_total,
                    "HOA": hoa_palisa
                }])
                
                existing_data = load_data()
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, data=updated_df)
                st.balloons()
                st.success("Record saved successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

with tab2:
    st.subheader("History")
    history_df = load_data()
    if not history_df.empty:
        st.dataframe(history_df.dropna(how='all'), use_container_width=True)
    else:
        st.info("No records found.")