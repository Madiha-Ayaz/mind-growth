
import streamlit as st
import pandas as pd
from io import BytesIO

# Page configuration
st.set_page_config(page_title="File Converter and Cleaner", page_icon="✨", layout="wide")

st.title("📂 File Converter and Cleaner")
st.write("Upload your CSV or Excel files to clean and convert formats effortlessly.")

# File uploader
files = st.file_uploader("Upload your file(s)", type=["csv", "xlsx"], accept_multiple_files=True)

if files:
    for file in files:
        ext = file.name.split(".")[-1].lower()
        
        # Read file based on extension
        try:
            df = pd.read_csv(file) if ext == "csv" else pd.read_excel(file)
        except Exception as e:
            st.error(f"Error reading {file.name}: {e}")
            continue

        st.subheader(f"🔍 {file.name} - Preview")
        st.dataframe(df.head())

        # Option to fill missing values
        if st.checkbox(f"Fill missing values in {file.name}"):
            df.fillna(df.select_dtypes(include=["number"]).mean(), inplace=True)
            st.success("Missing values filled with column mean.")
            st.dataframe(df.head())

        # Column selection
        selected_columns = st.multiselect(
            f"Select columns to keep from {file.name}",
            options=df.columns.tolist(),
            default=df.columns.tolist()
        )

        df = df[selected_columns]
        st.dataframe(df.head())

        # Optional chart
        if st.checkbox(f"Show chart for {file.name}"):
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            if numeric_cols:
                chart_col = st.selectbox(f"Select a numeric column to plot from {file.name}", numeric_cols)
                st.line_chart(df[chart_col])
            else:
                st.warning("No numeric columns available for charting.")

        # File download section
        st.markdown("### 📥 Download Cleaned File")
        output_format = st.radio(f"Choose output format for {file.name}", ["CSV", "Excel"], key=file.name)

        def convert_df_to_bytes(dataframe, format):
            output = BytesIO()
            if format == "CSV":
                output.write(dataframe.to_csv(index=False).encode('utf-8'))
            else:
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    dataframe.to_excel(writer, index=False, sheet_name='Sheet1')
            output.seek(0)
            return output

        cleaned_data = convert_df_to_bytes(df, output_format)
        st.download_button(
            label=f"Download {file.name} as {output_format}",
            data=cleaned_data,
            file_name=f"cleaned_{file.name.split('.')[0]}.{output_format.lower()}",
            mime="application/octet-stream"
        )

