import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Page setup
st.set_page_config(page_title="Growth MidSet", layout="wide")
st.title("🌱 Growth MidSet")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization!")

# File uploader
uploaded_files = st.file_uploader(
    "📁 Upload your files (CSV or Excel):", 
    type=["csv", "xlsx"], 
    accept_multiple_files=True
)

# Initialize session state for tracking converted files
if 'converted_files' not in st.session_state:
    st.session_state.converted_files = set()

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Load file
        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"❌ Unsupported file type: {file_ext}")
            continue

        # Show basic info
        st.markdown(f"### 📄 File: {file.name}")
        st.write(f"**Size:** {len(file.getvalue()) / 1024:.2f} KB")
        st.write("#### 🔍 Preview")
        st.dataframe(df.head())

        # Data Cleaning Options
        st.subheader("🧹 Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"🧽 Remove Duplicates - {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.success("✅ Duplicates Removed!")

            with col2:
                if st.button(f"🧴 Fill Missing Values - {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.success("✅ Missing values filled!")

        # Column selection
        st.subheader("📌 Select Columns to Convert")
        selected_columns = st.multiselect(f"Columns to keep from {file.name}", df.columns, default=df.columns)
        df = df[selected_columns]

        # Conversion options
        st.subheader("🔄 Convert File Format")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)

        if st.button(f"🚀 Convert {file.name}"):
            buffer = BytesIO()

            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                output_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            else:
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False)
                output_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            buffer.seek(0)

            st.download_button(
                label=f"⬇️ Download {output_name}",
                data=buffer,
                file_name=output_name,
                mime=mime_type
            )

            st.session_state.converted_files.add(file.name)
            st.success(f"✅ {file.name} has been successfully converted!")

    # ✅ Final Success Message (ONLY if all files are converted)
    if len(st.session_state.converted_files) == len(uploaded_files):
        st.success("🎉 ✅ All files processed!")

    # Optional: Reset Button
    if st.button("🔄 Reset"):
        st.session_state.converted_files.clear()
        st.experimental_rerun()



