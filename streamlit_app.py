import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Branch Cross-Sell Analyzer",
    layout="wide"
)

st.title("🤝 Branch Cross-Sell Opportunity Analyzer")
st.markdown("### Compare branch portfolios and identify cross-sell opportunities")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("📂 Upload Sales Data", type=["xlsx", "csv"])

if uploaded_file:

    try:
        # ---------------- READ FILE ----------------
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, engine="openpyxl")

        # ---------------- CLEAN COLUMN NAMES ----------------
        df.columns = df.columns.str.strip().str.lower()

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
        df = df[required_cols]

        # 🚨 CRITICAL FIX (handles float + string issue)
        df['organization'] = df['organization'].astype(str).str.strip()
        df['industry'] = df['industry'].astype(str).str.strip()
        df['category'] = df['category'].astype(str).str.strip()
        df['brand'] = df['brand'].astype(str).str.strip()

        # Remove invalid rows
        df = df[df['organization'] != 'nan']

        df = df.drop_duplicates()

        st.success("✅ File uploaded successfully")

        # ---------------- SIDEBAR ----------------
        st.sidebar.header("🔎 Select Branches")

        branches = sorted(df['organization'].unique())

        if len(branches) < 2:
            st.error("⚠️ Need at least 2 branches to compare")
            st.stop()

        branch_a = st.sidebar.selectbox("🏢 Your Branch", branches)
        branch_b = st.sidebar.selectbox("🏢 Compare With", branches)

        # ---------------- FILTER DATA ----------------
        df_a = df[df['organization'] == branch_a]
        df_b = df[df['organization'] == branch_b]

        # ---------------- EXTRACT DATA ----------------
        def extract_sets(data):
            return {
                "Industry": sorted(set(data['industry'])),
                "Category": sorted(set(data['category'])),
                "Brand": sorted(set(data['brand']))
            }

        sets_a = extract_sets(df_a)
        sets_b = extract_sets(df_b)

        # ---------------- DISPLAY ----------------
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"### 📍 {branch_a} Portfolio")
            st.write("**Industries:**", ", ".join(sets_a["Industry"]) or "No Data")
            st.write("**Categories:**", ", ".join(sets_a["Category"]) or "No Data")
            st.write("**Brands:**", ", ".join(sets_a["Brand"]) or "No Data")

        with col2:
            st.markdown(f"### 📍 {branch_b} Portfolio")
            st.write("**Industries:**", ", ".join(sets_b["Industry"]) or "No Data")
            st.write("**Categories:**", ", ".join(sets_b["Category"]) or "No Data")
            st.write("**Brands:**", ", ".join(sets_b["Brand"]) or "No Data")

        st.divider()

        # ---------------- COMMON ----------------
        st.markdown("## 🔗 Common Areas")

        col3, col4, col5 = st.columns(3)

        col3.metric("Industries", len(set(sets_a["Industry"]) & set(sets_b["Industry"])))
        col4.metric("Categories", len(set(sets_a["Category"]) & set(sets_b["Category"])))
        col5.metric("Brands", len(set(sets_a["Brand"]) & set(sets_b["Brand"])))

        st.divider()

        # ---------------- OPPORTUNITIES ----------------
        st.markdown("## 🚀 Cross-Sell Opportunities")

        col6, col7 = st.columns(2)

        with col6:
            st.markdown(f"### ➡️ {branch_a} Can Target")
            st.success(", ".join(set(sets_b["Category"]) - set(sets_a["Category"])) or "No Opportunities")

        with col7:
            st.markdown(f"### ➡️ {branch_b} Can Target")
            st.success(", ".join(set(sets_a["Category"]) - set(sets_b["Category"])) or "No Opportunities")

    except Exception as e:
        st.error(f"🚨 Error: {e}")
