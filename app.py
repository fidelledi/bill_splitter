import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION ---
CSV_FILE = "bill_history.csv"

st.set_page_config(page_title="Blk 27 Lot 16 Bill Organizer", layout="wide")

# --- DATA FUNCTIONS ---
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame(columns=["Month", "Palisa_Total", "Rillon_Total", "Elec_Total", "Water_Total", "Palisa_kWh"])

def save_data(new_row):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
    return df

# --- UI ---
st.title("🏠 Blk 27 Lot 16 Bill Organizer")
st.markdown("Divide utility bills.")

tab1, tab2 = st.tabs(["🧮 Calculator", "📜 History Log"])

with tab1:
    col_in, col_out = st.columns([1, 1.2], gap="large")

    with col_in:
        st.subheader("📋 Monthly Inputs")
        month = st.date_input("Billing Month", value=datetime.now()).strftime("%B %Y")
        
        with st.expander("⚡ Electricity (Meralco)", expanded=True):
            total_elec = st.number_input("Total Meralco Bill (₱)", min_value=0.0, step=100.0)
            rate = st.number_input("Meralco Rate (₱/kWh)", min_value=0.0, value=12.0, step=0.1)
            prev = st.number_input("Palisa: Previous Reading", min_value=0.0)
            curr = st.number_input("Palisa: Current Reading", min_value=0.0)

        with st.expander("💧 Water & Others", expanded=True):
            total_water = st.number_input("Total Water Bill (₱)", min_value=0.0, step=50.0)
            st.info("Fixed: Palisa Water (₱500) | HOA (₱35) | Internet (₱1499 Split)")

    # --- CALCULATIONS ---
    # Electricity
    p_kwh = curr - prev
    p_elec = p_kwh * rate
    b_elec = max(0.0, total_elec - p_elec)
    
    # Water
    p_water = 500.0
    b_water = max(0.0, total_water - p_water)
    
    # Fixed Fees
    p_hoa = 35.0
    net_share = 1499.0 / 2

    # Totals
    total_p = p_elec + p_water + p_hoa + net_share
    total_b = b_elec + b_water + net_share

    with col_out:
        st.subheader(f"📊 Summary: {month}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.success("### 👤 Palisa")
            st.write(f"Elec: **₱{p_elec:,.2f}**")
            st.write(f"Water: **₱{p_water:,.2f}**")
            st.write(f"HOA: **₱{p_hoa:,.2f}**")
            st.write(f"Net: **₱{net_share:,.2f}**")
            st.markdown(f"#### Total: ₱{total_p:,.2f}")
            
        with c2:
            st.warning("### 👥 Rillon")
            st.write(f"Elec: **₱{b_elec:,.2f}**")
            st.write(f"Water: **₱{b_water:,.2f}**")
            st.write(f"HOA: **₱0.00**")
            st.write(f"Net: **₱{net_share:,.2f}**")
            st.markdown(f"#### Total: ₱{total_b:,.2f}")

        st.divider()
        if st.button("💾 Save to History", use_container_width=True):
            row = {
                "Month": month, "Palisa_Total": total_p, "Rillon_Total": total_b,
                "Elec_Total": total_elec, "Water_Total": total_water, "Palisa_kWh": p_kwh
            }
            save_data(row)
            st.success("Saved to internal list!")

with tab2:
    st.subheader("📜 Saved Records")
    history_df = load_data()
    st.dataframe(history_df, use_container_width=True)
    
    if not history_df.empty:
        # Download button is essential for CSV version on GitHub
        csv = history_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV Backup",
            data=csv,
            file_name=f"bill_history_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.caption("⚠️ Note: Since this is hosted on GitHub, please download a backup after saving to keep your records permanently.")