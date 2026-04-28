import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Branch Cross-Sell Analyzer", layout="wide")

st.title("🇮🇳 All India vs Branch Analyzer")
st.markdown("### Compare branch performance with All India benchmark")

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

        # -------- CLEAN DATA --------
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

        # Add All India option
        branch_options = ["All India"] + branches

        # -------- SIDEBAR --------
        st.sidebar.header("🔎 Select Comparison")

        selected_branch = st.sidebar.selectbox("🏢 Select Branch", branch_options, index=1)

        # -------- DATA SELECTION --------
        df_all_india = df

        if selected_branch == "All India":
            st.warning("⚠️ Please select a specific branch for comparison")
            st.stop()

        df_branch = df[df['organization'] == selected_branch]

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

        sets_all = extract_sets(df_all_india)
        sets_branch = extract_sets(df_branch)

        # -------- HIGHLIGHT --------
        def highlight_items(list_a, list_b):
            highlighted = []
            for item in list_a:
                if item in list_b:
                    highlighted.append(f"🟢 {item}")
                else:
                    highlighted.append(f"🔴 {item}")
            return ", ".join(highlighted) if highlighted else "No Data"

        # -------- DISPLAY --------
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
            st.write(highlight_items(sets_branch["Industry"], sets_all["Industry"]))

            st.markdown("**Categories**")
            st.write(highlight_items(sets_branch["Category"], sets_all["Category"]))

            st.markdown("**Brands**")
            st.write(highlight_items(sets_branch["Brand"], sets_all["Brand"]))

        # -------- LEGEND --------
        st.markdown("""
        ### 🧾 Legend
        🟢 Covered by branch  
        🔴 Missing vs All India (Opportunity)  
        """)

        st.divider()

        # -------- GAP ANALYSIS --------
        st.markdown("## 🚀 Missing Opportunities (Branch vs All India)")

        col3, col4, col5 = st.columns(3)

        col3.metric("Missing Industries", len(set(sets_all["Industry"]) - set(sets_branch["Industry"])))
        col4.metric("Missing Categories", len(set(sets_all["Category"]) - set(sets_branch["Category"])))
        col5.metric("Missing Brands", len(set(sets_all["Brand"]) - set(sets_branch["Brand"])))

        st.divider()

        # -------- OPPORTUNITIES --------
        st.markdown("## 🎯 Key Cross-Sell Opportunities")

        st.success(
            ", ".join(set(sets_all["Category"]) - set(sets_branch["Category"])) or "No Opportunities"
        )

    except Exception as e:
        st.error(f"🚨 Error: {e}")
