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

        # ---------------- DISPLAY CLEAN COLUMN LIST ----------------
        with st.expander("📌 Detected Columns (Click to View)"):
            for col in df.columns:
                st.write(f"• {col}")

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

        st.success("✅ File uploaded successfully")

        # ---------------- SIDEBAR FILTERS ----------------
        st.sidebar.header("🔎 Select Branches")

        branches = sorted(df['organization'].dropna().astype(str).unique())

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

        # ---------------- DISPLAY BRANCH DATA ----------------
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"### 📍 {branch_a} Portfolio")
            st.markdown("**Industries**")
            st.write(", ".join(sets_a["Industry"]) if sets_a["Industry"] else "No Data")

            st.markdown("**Categories**")
            st.write(", ".join(sets_a["Category"]) if sets_a["Category"] else "No Data")

            st.markdown("**Brands**")
            st.write(", ".join(sets_a["Brand"]) if sets_a["Brand"] else "No Data")

        with col2:
            st.markdown(f"### 📍 {branch_b} Portfolio")
            st.markdown("**Industries**")
            st.write(", ".join(sets_b["Industry"]) if sets_b["Industry"] else "No Data")

            st.markdown("**Categories**")
            st.write(", ".join(sets_b["Category"]) if sets_b["Category"] else "No Data")

            st.markdown("**Brands**")
            st.write(", ".join(sets_b["Brand"]) if sets_b["Brand"] else "No Data")

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
