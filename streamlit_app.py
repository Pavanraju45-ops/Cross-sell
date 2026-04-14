import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Cross Sell Opportunity Finder",
    layout="wide"
)

st.title("📊 Cross Sell Opportunity Analyzer")
st.markdown("Analyze customer purchasing gaps and identify potential cross-selling opportunities.")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload Sales Data File",
    type=["xlsx", "csv"]
)

if uploaded_file is not None:

    try:
        # READ FILE
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)

        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(
                uploaded_file,
                engine="openpyxl"
            )

        # REQUIRED COLUMNS
        required_cols = [
            'Business Partner',
            'Industry of customer',
            'Product Category',
            'Product Search Key'
        ]

        # CHECK COLUMNS
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            st.error(f"Missing Columns: {missing_cols}")
            st.stop()

        # CLEAN DATA
        df = df[required_cols].drop_duplicates()

        st.success("✅ File Uploaded Successfully")

        # ---------------- SIDEBAR FILTERS ----------------
        st.sidebar.header("Filters")

        selected_industry = st.sidebar.selectbox(
            "Select Industry",
            sorted(df['Industry of customer'].dropna().unique())
        )

        industry_df = df[
            df['Industry of customer'] == selected_industry
        ]

        selected_partner = st.sidebar.selectbox(
            "Select Business Partner",
            sorted(industry_df['Business Partner'].dropna().unique())
        )

        threshold = st.sidebar.slider(
            "Recommendation Threshold %",
            10,
            100,
            40
        ) / 100

        # ---------------- ANALYSIS ----------------
        total_customers = industry_df['Business Partner'].nunique()

        category_counts = industry_df.groupby(
            'Product Category'
        )['Business Partner'].nunique()

        common_categories = category_counts[
            (category_counts / total_customers) >= threshold
        ].index.tolist()

        partner_categories = industry_df[
            industry_df['Business Partner'] == selected_partner
        ]['Product Category'].unique()

        missing_categories = list(
            set(common_categories) - set(partner_categories)
        )

        # ---------------- RESULTS ----------------
        st.subheader(f"Results for: {selected_partner}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Purchased Categories")
            st.write(list(partner_categories))

        with col2:
            st.markdown("### Recommended Cross Sell Categories")

            if missing_categories:
                st.success(missing_categories)
            else:
                st.info("No recommendations found.")

        # ---------------- DOWNLOAD BUTTON ----------------
        output_df = pd.DataFrame({
            "Business Partner": [selected_partner],
            "Industry": [selected_industry],
            "Recommended Categories": [", ".join(missing_categories)]
        })

        st.download_button(
            label="📥 Download Recommendation CSV",
            data=output_df.to_csv(index=False),
            file_name="cross_sell_recommendations.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error Reading File: {e}")
