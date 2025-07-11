import streamlit as st
import pandas as pd
import os

# Set folder path
FOLDER_PATH = r"C:\Users\uddes\OneDrive\Desktop\Mapping Automation"

st.set_page_config(page_title="AR Mapping App", layout="wide")
st.title("🧾 AR Mapping App")
st.write("Upload your files and map payments against invoices.")

# File uploader
ar_file = st.file_uploader("Upload AR File", type=["xlsx"])
bank_file = st.file_uploader("Upload Bank Statement", type=["xlsx"])

# Normalize column headers
def normalize_columns(df):
    df.columns = (
        df.columns.str.strip()
                  .str.lower()
                  .str.replace(" ", "_")
    )
    return df

if ar_file and bank_file:
    # Load and normalize
    ar_df = pd.read_excel(ar_file)
    bank_df = pd.read_excel(bank_file)
    ar_df = normalize_columns(ar_df)
    bank_df = normalize_columns(bank_df)

    # Required columns
    required_ar_cols = ['invoice_no', 'invoice_date', 'invoice_amount', 'customer', 'segment', 'sub_segment', 'category']
    required_bank_cols = ['date', 'payment_received', 'particular']

    missing_ar = [col for col in required_ar_cols if col not in ar_df.columns]
    missing_bank = [col for col in required_bank_cols if col not in bank_df.columns]

    if missing_ar or missing_bank:
        st.error(f"❌ Missing required column(s):\n- AR file: {missing_ar or 'None'}\n- Bank file: {missing_bank or 'None'}")
        st.stop()

    # Display previews
    st.subheader("📄 AR File Preview")
    st.dataframe(ar_df.head())

    st.subheader("🏦 Bank Statement Preview")
    st.dataframe(bank_df.head())

    st.subheader("🔍 Bank Transactions to Map")
    st.write("Map each payment to a customer and payment type.")

    mapping_data = []

    for index, row in bank_df.iterrows():
        with st.expander(f"{row['date']} - ₹{row['payment_received']} - {row['particular']}"):
            customer = st.selectbox(
                f"Select Customer for Row {index+1}",
                ar_df['customer'].unique(),
                key=f"cust_{index}"
            )
            payment_type = st.selectbox(
                "Select Payment Type",
                ["Against Invoice", "Advance", "FIFO"],
                key=f"type_{index}"
            )

            cust_rows = ar_df[ar_df['customer'] == customer]
            if not cust_rows.empty:
                cust_data = cust_rows.iloc[0]
                st.markdown("##### 📋 Autofilled Info")
                st.write({
                    "Sub Segment": cust_data.get("sub_segment", ""),
                    "Segment": cust_data.get("segment", ""),
                    "Category": cust_data.get("category", "")
                })

                mapping_data.append({
                    "Date": row['date'],
                    "Amount": row['payment_received'],
                    "Narration": row['particular'],
                    "Customer": customer,
                    "Payment Type": payment_type,
                    "Sub Segment": cust_data.get("sub_segment", ""),
                    "Segment": cust_data.get("segment", ""),
                    "Category": cust_data.get("category", "")
                })
            else:
                st.warning("⚠️ Customer not found in AR file. Skipping.")

    if st.button("✅ Save Mapping"):
        mapped_df = pd.DataFrame(mapping_data)
        mapped_path = os.path.join(FOLDER_PATH, "mapped_collections.csv")
        updated_ar_path = os.path.join(FOLDER_PATH, "updated_ar_file.xlsx")

        mapped_df.to_csv(mapped_path, index=False)
        ar_df.to_excel(updated_ar_path, index=False)

        st.success(f"✅ Mapping saved to:\n- {mapped_path}\n- {updated_ar_path}")
        st.download_button("📥 Download Mapped CSV", mapped_df.to_csv(index=False), "mapped_collections.csv", "text/csv")
