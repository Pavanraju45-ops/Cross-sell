import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Branch Cross-Sell Analyzer", layout="wide")

st.title("🤝 Branch Cross-Sell Opportunity Analyzer")
st.markdown("### Compare branch portfolios and identify cross-sell opportunities")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("📂 Upload Sales Data", type=["xlsx", "csv"])

if uploaded_file:

    try:
        # -------- LOAD FILE --------
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, engine="openpyxl")

        # -------- CLEAN COLUMN NAMES --------
        df.columns = df.columns.str.strip().str.lower()

        # -------- AUTO MAP --------
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

        required_cols = ['organization', 'industry', 'category', 'brand']

        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            st.error(f"❌ Missing columns: {missing_cols}")
            st.stop()

        df = df[required_cols]

        # -------- STRONG CLEANING --------
        df = df.dropna(subset=['organization'])

        for col in required_cols:
            df[col] = df[col].astype(str).str.strip()

        for col in required_cols:
            df = df[
                (df[col] != '') &
                (df[col].str.lower() != 'nan')
            ]

        df = df.drop_duplicates()

        st.success("✅ File uploaded successfully")

        # -------- BRANCH LIST --------
        branches = sorted(df['organization'].unique().tolist())

        if len(branches) < 2:
            st.error("⚠️ Need at least 2 branches to compare.")
            st.stop()

        # -------- SIDEBAR --------
        st.sidebar.header("🔎 Select Branches")

        branch_a = st.sidebar.selectbox("🏢 Your Branch", branches)
        branch_b = st.sidebar.selectbox("🏢 Compare With", branches)

        df_a = df[df['organization'] == branch_a]
        df_b = df[df['organization'] == branch_b]

        # -------- SAFE SORT --------
        def safe_sorted(series):
            return sorted(series.dropna().astype(str).str.strip().unique())

        # -------- EXTRACT --------
        def extract_sets(data):
            return {
                "Industry": safe_sorted(data['industry']),
                "Category": safe_sorted(data['category']),
                "Brand": safe_sorted(data['brand'])
            }

        sets_a = extract_sets(df_a)
        sets_b = extract_sets(df_b)

        # -------- HIGHLIGHT FUNCTION --------
        def highlight_items(list_a, list_b):
            highlighted = []
            for item in list_a:
                if item in list_b:
                    highlighted.append(f"🟢 {item}")
                else:
                    highlighted.append(f"🔵 {item}")
            return ", ".join(highlighted) if highlighted else "No Data"

        # -------- DISPLAY --------
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"### 📍 {branch_a}")

            st.markdown("**Industries**")
            st.write(highlight_items(sets_a["Industry"], sets_b["Industry"]))

            st.markdown("**Categories**")
            st.write(highlight_items(sets_a["Category"], sets_b["Category"]))

            st.markdown("**Brands**")
            st.write(highlight_items(sets_a["Brand"], sets_b["Brand"]))

        with col2:
            st.markdown(f"### 📍 {branch_b}")

            st.markdown("**Industries**")
            st.write(highlight_items(sets_b["Industry"], sets_a["Industry"]))

            st.markdown("**Categories**")
            st.write(highlight_items(sets_b["Category"], sets_a["Category"]))

            st.markdown("**Brands**")
            st.write(highlight_items(sets_b["Brand"], sets_a["Brand"]))

        # -------- LEGEND --------
        st.markdown("""
        ### 🧾 Legend
        🟢 Common across both branches  
        🔵 Unique to that branch  
        """)

        st.divider()

        # -------- COMMON AREAS --------
        st.markdown("## 🔗 Common Areas")

        st.write("**Industries:**", ", ".join(set(sets_a["Industry"]) & set(sets_b["Industry"])) or "None")
        st.write("**Categories:**", ", ".join(set(sets_a["Category"]) & set(sets_b["Category"])) or "None")
        st.write("**Brands:**", ", ".join(set(sets_a["Brand"]) & set(sets_b["Brand"])) or "None")

        st.divider()

        # -------- OPPORTUNITIES --------
        st.markdown("## 🚀 Cross-Sell Opportunities")

        col3, col4 = st.columns(2)

        with col3:
            st.markdown(f"### ➡️ {branch_a} Can Target")
            st.success(", ".join(set(sets_b["Category"]) - set(sets_a["Category"])) or "No Opportunities")

        with col4:
            st.markdown(f"### ➡️ {branch_b} Can Target")
            st.success(", ".join(set(sets_a["Category"]) - set(sets_b["Category"])) or "No Opportunities")

    except Exception as e:
        st.error(f"🚨 Error: {e}")
