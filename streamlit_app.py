import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="All India vs Branch Analyzer", layout="wide")

st.title("🇮🇳 All India vs Branch Cross-Sell Analyzer")
st.markdown("### Identify gaps and cross-sell opportunities across branches")

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

        # -------- DATA CLEANING --------
        df = df.dropna(subset=['organization'])

        for col in required_cols:
            df[col] = df[col].astype(str).str.strip()

        for col in required_cols:
            df = df[(df[col] != '') & (df[col].str.lower() != 'nan')]

        df = df.drop_duplicates()

        st.success("✅ File uploaded successfully")

        # -------- BRANCH LIST --------
        branches = sorted(df['organization'].unique().tolist())

        if len(branches) < 1:
            st.error("⚠️ No valid branches found.")
            st.stop()

        # -------- SIDEBAR --------
        st.sidebar.header("🔎 Select Branch")
        selected_branch = st.sidebar.selectbox("🏢 Choose Branch", branches)

        # -------- DATA SPLIT --------
        df_all = df
        df_branch = df[df['organization'] == selected_branch]

        # -------- SAFE SORT --------
        def safe_sorted(series):
            return sorted(series.dropna().astype(str).str.strip().unique())

        # -------- EXTRACT SETS --------
        def extract_sets(data):
            return {
                "Industry": safe_sorted(data['industry']),
                "Category": safe_sorted(data['category']),
                "Brand": safe_sorted(data['brand'])
            }

        sets_all = extract_sets(df_all)
        sets_branch = extract_sets(df_branch)

        # -------- HIGHLIGHT FUNCTION --------
        def highlight_items(list_a, list_b):
            result = []
            for item in list_a:
                if item in list_b:
                    result.append(f"🟢 {item}")
                else:
                    result.append(f"🔴 {item}")
            return ", ".join(result) if result else "No Data"

        # -------- DISPLAY TOP SECTION --------
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🇮🇳 All India")

            st.markdown("**Industries**")
            st.write(", ".join(sets_all["Industry"]))

            st.markdown("**Categories**")
            st.write(", ".join(sets_all["Category"]))

            st.markdown("**Brands**")
            st.write(", ".join(sets_all["Brand"]))

        with col2:
            st.markdown(f"### 📍 {selected_branch}")

            st.markdown("**Industries**")
            st.write(highlight_items(sets_all["Industry"], sets_branch["Industry"]))

            st.markdown("**Categories**")
            st.write(highlight_items(sets_all["Category"], sets_branch["Category"]))

            st.markdown("**Brands**")
            st.write(highlight_items(sets_all["Brand"], sets_branch["Brand"]))

        # -------- LEGEND --------
        st.markdown("""
        ### 🧾 Legend
        🟢 Covered by branch  
        🔴 Missing / Opportunity  
        """)

        st.divider()

        # -------- MISSING CALCULATIONS --------
        missing_industries = sorted(set(sets_all["Industry"]) - set(sets_branch["Industry"]))
        missing_categories = sorted(set(sets_all["Category"]) - set(sets_branch["Category"]))
        missing_brands = sorted(set(sets_all["Brand"]) - set(sets_branch["Brand"]))

        def format_list(items):
            return ", ".join([f"🔴 {i}" for i in items]) if items else "No Gaps"

        # -------- MISSING OPPORTUNITIES --------
        st.markdown("## 🚀 Missing Opportunities (Branch vs All India)")

        col3, col4, col5 = st.columns(3)

        with col3:
            st.markdown("### 🏭 Industries")
            st.write(format_list(missing_industries))

        with col4:
            st.markdown("### 📦 Categories")
            st.write(format_list(missing_categories))

        with col5:
            st.markdown("### 🏷️ Brands")
            st.write(format_list(missing_brands))

        st.divider()

        # -------- CROSS SELL --------
        st.markdown("## 🎯 Key Cross-Sell Opportunities")

        col6, col7, col8 = st.columns(3)

        with col6:
            st.markdown("### 🏭 Industries")
            st.write(format_list(missing_industries))

        with col7:
            st.markdown("### 📦 Categories")
            st.write(format_list(missing_categories))

        with col8:
            st.markdown("### 🏷️ Brands")
            st.write(format_list(missing_brands))

    except Exception as e:
        st.error(f"🚨 Error: {e}")
