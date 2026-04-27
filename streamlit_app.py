import streamlit as st
import pandas as pd

st.set_page_config(page_title="Branch Cross-Sell Analyzer", layout="wide")

st.title("🤝 Branch Cross-Sell Opportunity Analyzer")

uploaded_file = st.file_uploader("Upload Sales Data", type=["xlsx", "csv"])

if uploaded_file:

    # Read file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file, engine="openpyxl")

    required_cols = [
        'Organization',
        'Industry of customer',
        'Product Category',
        'Product Brand'
    ]

    if not all(col in df.columns for col in required_cols):
        st.error("Missing required columns!")
        st.stop()

    df = df[required_cols].drop_duplicates()

    # Sidebar filters
    st.sidebar.header("Select Branches")

    branch_a = st.sidebar.selectbox(
        "Select Your Branch",
        sorted(df['Organization'].unique())
    )

    branch_b = st.sidebar.selectbox(
        "Select Other Branch",
        sorted(df['Organization'].unique())
    )

    # Filter data
    df_a = df[df['Organization'] == branch_a]
    df_b = df[df['Organization'] == branch_b]

    # Helper function
    def extract_sets(data):
        return {
            "Industry": set(data['Industry of customer']),
            "Category": set(data['Product Category']),
            "Brand": set(data['Product Brand'])
        }

    sets_a = extract_sets(df_a)
    sets_b = extract_sets(df_b)

    # Layout
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

    # Overlap
    st.subheader("🔗 Common Areas (Overlap)")

    st.write("**Industries:**", list(sets_a["Industry"] & sets_b["Industry"]))
    st.write("**Categories:**", list(sets_a["Category"] & sets_b["Category"]))
    st.write("**Brands:**", list(sets_a["Brand"] & sets_b["Brand"]))

    st.divider()

    # Opportunities
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
