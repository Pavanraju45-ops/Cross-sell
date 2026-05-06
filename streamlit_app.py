import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="All India vs Branch Analyzer", layout="wide")

st.title("🇮🇳 All India vs Branch Cross-Sell Analyzer")
st.markdown("### Identify gaps and cross-sell opportunities across branches and sales representatives")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("📂 Upload Sales Data", type=["xlsx", "csv"])

if uploaded_file:

    try:
        # ---------------- LOAD FILE ----------------
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, engine="openpyxl")

        # ---------------- CLEAN COLUMN NAMES ----------------
        df.columns = df.columns.str.strip().str.lower()

        # ---------------- AUTO MAP ----------------
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

            elif col in ['sales representative', 'sales rep', 'sales engineer']:
                column_mapping[col] = 'sales_rep'

        df = df.rename(columns=column_mapping)

        required_cols = [
            'organization',
            'industry',
            'category',
            'brand',
            'sales_rep'
        ]

        if not all(col in df.columns for col in required_cols):
            st.error("❌ Required columns missing")
            st.stop()

        df = df[required_cols]

        # ---------------- CLEAN DATA ----------------
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

        # ---------------- SAFE LIST ----------------
        def safe_list(series):
            return sorted(
                series.dropna()
                .astype(str)
                .str.strip()
                .loc[lambda x: x != '']
                .unique()
                .tolist()
            )

        # ---------------- SIDEBAR ----------------
        st.sidebar.header("🔎 Selection Filters")

        # Branch Selection
        branches = safe_list(df['organization'])

        selected_branch = st.sidebar.selectbox(
            "🏢 Choose Branch",
            branches
        )

        # Filter branch data
        branch_df = df[df['organization'] == selected_branch]

        # Sales Rep Selection
        sales_reps = ["All Sales Representatives"] + safe_list(branch_df['sales_rep'])

        selected_rep = st.sidebar.selectbox(
            "👤 Choose Sales Representative",
            sales_reps
        )

        # ---------------- FINAL FILTER ----------------
        if selected_rep == "All Sales Representatives":
            filtered_df = branch_df
            entity_name = selected_branch
        else:
            filtered_df = branch_df[
                branch_df['sales_rep'] == selected_rep
            ]
            entity_name = f"{selected_branch} → {selected_rep}"

        # ---------------- ALL INDIA DATA ----------------
        df_all = df

        # ---------------- SET EXTRACTION ----------------
        def get_sets(data):
            return {
                "Industry": safe_list(data['industry']),
                "Category": safe_list(data['category']),
                "Brand": safe_list(data['brand'])
            }

        sets_all = get_sets(df_all)
        sets_filtered = get_sets(filtered_df)

        # ---------------- TABLE FUNCTIONS ----------------
        def create_comparison_table(all_list, filtered_list):

            covered = sorted(set(all_list) & set(filtered_list))
            missing = sorted(set(all_list) - set(filtered_list))

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
        st.markdown(f"## 📊 Comparison: All India vs {entity_name}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 🏭 Industries")
            st.dataframe(
                create_comparison_table(
                    sets_all["Industry"],
                    sets_filtered["Industry"]
                ),
                use_container_width=True
            )

        with col2:
            st.markdown("### 📦 Categories")
            st.dataframe(
                create_comparison_table(
                    sets_all["Category"],
                    sets_filtered["Category"]
                ),
                use_container_width=True
            )

        with col3:
            st.markdown("### 🏷️ Brands")
            st.dataframe(
                create_comparison_table(
                    sets_all["Brand"],
                    sets_filtered["Brand"]
                ),
                use_container_width=True
            )

        st.divider()

        # ---------------- MISSING ----------------
        missing_industries = sorted(
            set(sets_all["Industry"]) - set(sets_filtered["Industry"])
        )

        missing_categories = sorted(
            set(sets_all["Category"]) - set(sets_filtered["Category"])
        )

        missing_brands = sorted(
            set(sets_all["Brand"]) - set(sets_filtered["Brand"])
        )

        st.markdown("## 🚀 Missing Opportunities")

        col4, col5, col6 = st.columns(3)

        with col4:
            st.markdown("### 🏭 Industries")
            st.dataframe(simple_table(missing_industries), use_container_width=True)

        with col5:
            st.markdown("### 📦 Categories")
            st.dataframe(simple_table(missing_categories), use_container_width=True)

        with col6:
            st.markdown("### 🏷️ Brands")
            st.dataframe(simple_table(missing_brands), use_container_width=True)

        st.divider()

        # ---------------- CROSS SELL ----------------
        st.markdown("## 🎯 Key Cross-Sell Opportunities")

        col7, col8, col9 = st.columns(3)

        with col7:
            st.markdown("### 🏭 Industries")
            st.dataframe(simple_table(missing_industries), use_container_width=True)

        with col8:
            st.markdown("### 📦 Categories")
            st.dataframe(simple_table(missing_categories), use_container_width=True)

        with col9:
            st.markdown("### 🏷️ Brands")
            st.dataframe(simple_table(missing_brands), use_container_width=True)

    except Exception as e:
        st.error(f"🚨 Error: {e}")
