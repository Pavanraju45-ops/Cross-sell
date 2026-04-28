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

        if not all(col in df.columns for col in required_cols):
            st.error("❌ Required columns missing")
            st.stop()

        df = df[required_cols]

        # ---------------- STRONG CLEANING (CRITICAL FIX) ----------------
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

        # ---------------- SAFE SORT FUNCTION ----------------
        def safe_list(series):
            return sorted(
                series.dropna()
                .astype(str)
                .str.strip()
                .loc[lambda x: x != '']
                .unique()
                .tolist()
            )

        # ---------------- BRANCH LIST ----------------
        branches = safe_list(df['organization'])

        if len(branches) < 1:
            st.error("⚠️ No valid branches found")
            st.stop()

        # ---------------- SIDEBAR ----------------
        st.sidebar.header("🔎 Select Branch")
        selected_branch = st.sidebar.selectbox("🏢 Choose Branch", branches)

        df_all = df
        df_branch = df[df['organization'] == selected_branch]

        # ---------------- SET EXTRACTION ----------------
        def get_sets(data):
            return {
                "Industry": safe_list(data['industry']),
                "Category": safe_list(data['category']),
                "Brand": safe_list(data['brand'])
            }

        sets_all = get_sets(df_all)
        sets_branch = get_sets(df_branch)

        # ---------------- TABLE CREATION ----------------
        def create_comparison_table(all_list, branch_list):
            covered = sorted(set(all_list) & set(branch_list))
            missing = sorted(set(all_list) - set(branch_list))

            max_len = max(len(covered), len(missing))

            covered += [""] * (max_len - len(covered))
            missing += [""] * (max_len - len(missing))

            return pd.DataFrame({
                "🟢 Covered": covered,
                "🔴 Missing": missing
            })

        def simple_table(items):
            return pd.DataFrame({"Items": items}) if items else pd.DataFrame({"Items": ["No Gaps"]})

        # ---------------- MAIN COMPARISON ----------------
        st.markdown("## 📊 Branch vs All India Comparison")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 🏭 Industries")
            st.dataframe(create_comparison_table(sets_all["Industry"], sets_branch["Industry"]))

        with col2:
            st.markdown("### 📦 Categories")
            st.dataframe(create_comparison_table(sets_all["Category"], sets_branch["Category"]))

        with col3:
            st.markdown("### 🏷️ Brands")
            st.dataframe(create_comparison_table(sets_all["Brand"], sets_branch["Brand"]))

        st.divider()

        # ---------------- MISSING ----------------
        missing_industries = sorted(set(sets_all["Industry"]) - set(sets_branch["Industry"]))
        missing_categories = sorted(set(sets_all["Category"]) - set(sets_branch["Category"]))
        missing_brands = sorted(set(sets_all["Brand"]) - set(sets_branch["Brand"]))

        st.markdown("## 🚀 Missing Opportunities")

        col4, col5, col6 = st.columns(3)

        with col4:
            st.markdown("### 🏭 Industries")
            st.dataframe(simple_table(missing_industries))

        with col5:
            st.markdown("### 📦 Categories")
            st.dataframe(simple_table(missing_categories))

        with col6:
            st.markdown("### 🏷️ Brands")
            st.dataframe(simple_table(missing_brands))

        st.divider()

        # ---------------- CROSS SELL ----------------
        st.markdown("## 🎯 Key Cross-Sell Opportunities")

        col7, col8, col9 = st.columns(3)

        with col7:
            st.markdown("### 🏭 Industries")
            st.dataframe(simple_table(missing_industries))

        with col8:
            st.markdown("### 📦 Categories")
            st.dataframe(simple_table(missing_categories))

        with col9:
            st.markdown("### 🏷️ Brands")
            st.dataframe(simple_table(missing_brands))

    except Exception as e:
        st.error(f"🚨 Error: {e}")
