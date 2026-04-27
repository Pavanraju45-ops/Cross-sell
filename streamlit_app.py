import streamlit as st
import pandas as pd

st.set_page_config(page_title="Branch Cross-Sell Analyzer", layout="wide")

st.title("🤝 Branch Cross-Sell Opportunity Analyzer")

uploaded_file = st.file_uploader("Upload Sales Data", type=["xlsx", "csv"])

if uploaded_file:

    try:
        # ---------------- READ FILE ----------------
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, engine="openpyxl")

        # ---------------- CLEAN COLUMN NAMES ----------------
        df.columns = df.columns.str.strip().str.lower()

        st.write("📌 Detected Columns:", df.columns.tolist())

        # ---------------- AUTO MAP COLUMNS ----------------
        column_mapping = {}

        for col in df.columns:
            if col in ['organization', 'organisation', 'branch', 'location']:
                column_mapping[col] = 'organization'
            elif col in ['industry of customer', 'industry', 'customer industry']:
                column_mapping[col] = 'industry'
            elif col in ['product category', 'category']:
                column_mapping[col] = 'category'
            elif col in ['product brand', 'brand']:
                column_mapping[col] = 'brand'

        df = df.rename(columns=column_mapping)

        # ---------------- CHECK REQUIRED COLUMNS ----------------
        required_cols = ['organization', 'industry', 'category', 'brand']

        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            st.error(f"❌ Missing required columns: {missing_cols}")
            st.stop()

        # ---------------- CLEAN DATA ----------------
        df = df[required_cols].drop_duplicates()

        st.success("✅ File uploaded and processed successfully")

        # ---------------- SIDEBAR ----------------
        st.sidebar.header("Select Branches")

        branches = sorted(df['organization'].dropna().unique())

        branch_a = st.sidebar.selectbox("Select Your Branch", branches)
        branch_b = st.sidebar.selectbox("Select Other Branch", branches)

        # ---------------- FILTER DATA ----------------
        df_a = df[df['organization'] == branch_a]
        df_b = df[df['organization'] == branch_b]

        # ---------------- EXTRACT SETS ----------------
        def extract_sets(data):
            return {
                "Industry": set(data['industry']),
                "Category": set(data['category']),
                "Brand": set(data['brand'])
            }

        sets_a = extract_sets(df_a)
        sets_b = extract_sets(df_b)

        # ---------------- DISPLAY ----------------
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"📍 {branch_a} Portfolio")
            st.write("**Industries:**", list(sets_a["Industry"]))
            st.write("**Categories:**", list(sets_a["Category"]))
            st.write("**Brands:**", list(sets_a["Brand"]))

        with col2:
            st.subheader(f"📍 {branch_b} Portfolio")
            st.write("**Industries:**", list(sets_b["Industry"]))
            st.write("**Categories:**", list(sets_b["Category"]))
            st.write("**Brands:**", list(sets_b["Brand"]))

        st.divider()

        # ---------------- COMMON ----------------
        st.subheader("🔗 Common Areas (Overlap)")

        st.write("**Industries:**", list(sets_a["Industry"] & sets_b["Industry"]))
        st.write("**Categories:**", list(sets_a["Category"] & sets_b["Category"]))
        st.write("**Brands:**", list(sets_a["Brand"] & sets_b["Brand"]))

        st.divider()

        # ---------------- OPPORTUNITIES ----------------
        st.subheader("🚀 Cross-Sell Opportunities")

        col3, col4 = st.columns(2)

        with col3:
            st.markdown(f"### What {branch_a} Can Learn from {branch_b}")
            st.write("**New Industries:**", list(sets_b["Industry"] - sets_a["Industry"]))
            st.write("**New Categories:**", list(sets_b["Category"] - sets_a["Category"]))
            st.write("**New Brands:**", list(sets_b["Brand"] - sets_a["Brand"]))

        with col4:
            st.markdown(f"### What {branch_b} Can Learn from {branch_a}")
            st.write("**New Industries:**", list(sets_a["Industry"] - sets_b["Industry"]))
            st.write("**New Categories:**", list(sets_a["Category"] - sets_b["Category"]))
            st.write("**New Brands:**", list(sets_a["Brand"] - sets_b["Brand"]))

    except Exception as e:
        st.error(f"🚨 Error: {e}")
