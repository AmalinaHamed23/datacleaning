import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Data Cleaning App", page_icon="📎", layout="wide")

# ------------------ CUSTOM CSS (COLORFUL UI) ------------------
st.markdown("""
<style>
.main {
    background-color: #F5FBFF;
}

h1, h2, h3 {
    color: #0F4C81;
}

.stMetric {
    background-color: #E6F6F7;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
}

.stButton>button {
    background-color: #0F4C81;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
}

.stButton>button:hover {
    background-color: #3282B8;
    color: white;
}

.stDownloadButton>button {
    background-color: #1B9C85;
    color: white;
    border-radius: 10px;
}

.stSidebar {
    background-color: #DFF6FF;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 1. TITLE & SUBHEADER
# -------------------------------
st.markdown("""
<h1 style='text-align: center;'>
 📎 A DATA CLEANING TOOL 📎
</h1>
""", unsafe_allow_html=True)



# ------------------ SESSION STATE ------------------
if "df" not in st.session_state:
    st.session_state.df = None

if "original_df" not in st.session_state:
    st.session_state.original_df = None

# ------------------ HOME CARD ------------------
st.markdown("""
<div style='background-color:#E6F6F7; padding:30px; border-radius:15px; text-align:wide;'>
    <h2 style='color:#0F4C81;'>Clean your data easily</h2>
    <p style='font-size:16px;'>This Data Cleaning App helps you clean your dataset easily without writing complex code.
    Simply upload your file and use the interactive tools below:</p>
    <ul style='list-style-position: inside; font-size:16px;'>
        <li>⚠️ Handle missing values</li>
        <li>🔁 Remove duplicate records</li>
        <li>📂 Manage and rename columns</li>
        <li>🔢 Convert data types</li>
        <li>📥 Download cleaned data for analysis</li>
    </ul>
    <p style='font-size:15px;'>Once you're done, you can download your cleaned dataset in just one click.</p>
</div>
""", unsafe_allow_html=True)

# ------------------ SIDEBAR ------------------

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "📊 Overview",
        "⚠️ Missing Values",
        "🔁 Duplicates",
        "📂 Columns",
        "🔢 Data Types",
        "📥 Download"
    ]
)

# ------------------ UPLOAD ------------------
if menu == "🏠 Home":
    st.title("📤 Upload Your Dataset")

    file = st.file_uploader("Upload your dataset", type=["csv", "xlsx", "json"])

    if file is not None:
        file_type = file.name.split(".")[-1]

        if file_type == "csv":
            df = pd.read_csv(file)

        elif file_type == "xlsx":
            df = pd.read_excel(file)

        elif file_type == "json":
            try:
                df = pd.read_json(file)
            except ValueError:
                file.seek(0)
                df = pd.json_normalize(pd.read_json(file))

        else:
            st.error("Unsupported file type")
            df = None
        st.session_state.df = df.copy()
        st.session_state.original_df = df.copy()
        st.success("Dataset uploaded successfully!")
        st.dataframe(df.head())

# ------------------ OVERVIEW ------------------
elif menu == "📊 Overview":
    st.title("📊 Dataset Overview")

    df = st.session_state.df

    if df is not None:
        col1, col2, col3 = st.columns(3)

        col1.metric("Rows", df.shape[0])
        col2.metric("Columns", df.shape[1])
        col3.metric("Missing Values", df.isnull().sum().sum())

        st.subheader("Data Preview")
        st.dataframe(df.head(),use_container_width=True, hide_index=True)

        st.subheader("Data Types")
        dtype_df = df.dtypes.reset_index()
        dtype_df.columns = ["Column", "Data Type"]

        st.dataframe(dtype_df, use_container_width=True, hide_index=True)
    else:
        st.warning("Please upload a dataset first.")

# ------------------ MISSING VALUES ------------------
elif menu == "⚠️ Missing Values":
    st.title("⚠️ Handle Missing Values")

    df = st.session_state.df

    if df is not None:
        st.write("Missing values per column:")
        missing_df = df.isnull().sum().reset_index()
        missing_df.columns = ["Column", "Missing Values"]

        st.dataframe(missing_df, use_container_width=True, hide_index=True)

        col = st.selectbox("Select Column", df.columns)
        method = st.selectbox(
            "Choose Method",
            ["Drop", "Fill Mean", "Fill Median", "Fill Mode", "Custom Value"]
        )

        if st.button("Apply"):
            if method == "Drop":
                df = df.dropna(subset=[col])

            elif method == "Fill Mean":
                df[col].fillna(df[col].mean(), inplace=True)

            elif method == "Fill Median":
                df[col].fillna(df[col].median(), inplace=True)

            elif method == "Fill Mode":
                df[col].fillna(df[col].mode()[0], inplace=True)

            elif method == "Custom Value":
                value = st.text_input("Enter value")
                if value:
                    df[col].fillna(value, inplace=True)

            st.session_state.df = df
            st.success("Operation completed!")
    else:
        st.warning("Upload data first.")

# ------------------ DUPLICATES ------------------
elif menu == "🔁 Duplicates":
    st.title("🔁 Remove Duplicates")

    df = st.session_state.df

    if df is not None:
        dup = df.duplicated().sum()
        st.metric("Duplicate Rows", dup)

        if st.button("Remove Duplicates"):
            df = df.drop_duplicates()
            st.session_state.df = df
            st.success("Duplicates removed!")
    else:
        st.warning("Upload data first.")

# ------------------ COLUMNS ------------------
elif menu == "📂 Columns":
    st.title("📂 Column Management")

    df = st.session_state.df

    if df is not None:
        st.subheader("Drop Columns")
        cols_to_drop = st.multiselect("Select columns", df.columns)

        if st.button("Drop Selected Columns"):
            df = df.drop(columns=cols_to_drop)
            st.session_state.df = df
            st.success("Columns dropped!")

        st.subheader("Rename Column")
        col = st.selectbox("Select column to rename", df.columns)
        new_name = st.text_input("New name")

        if st.button("Rename"):
            df = df.rename(columns={col: new_name})
            st.session_state.df = df
            st.success("Column renamed!")
    else:
        st.warning("Upload data first.")

# ------------------ DATA TYPES ------------------
elif menu == "🔢 Data Types":
    st.title("🔢 Convert Data Types")

    df = st.session_state.df

    if df is not None:
        col = st.selectbox("Select column", df.columns)
        dtype = st.selectbox("Convert to", ["int", "float", "str"])

        if st.button("Convert"):
            try:
                df[col] = df[col].astype(dtype)
                st.session_state.df = df
                st.success("Conversion successful!")
            except:
                st.error("Conversion failed. Check your data.")
    else:
        st.warning("Upload data first.")

# ------------------ DOWNLOAD ------------------
elif menu == "📥 Download":
    st.title("📥 Download Cleaned Data")

    df = st.session_state.df

    if df is not None:
        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download CSV",
            data=csv,
            file_name="cleaned_data.csv",
            mime="text/csv"
        )

        if st.button("Reset Data"):
            st.session_state.df = st.session_state.original_df.copy()
            st.success("Data reset to original!")
    else:
        st.warning("Upload data first.")
