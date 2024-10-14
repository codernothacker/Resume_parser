import streamlit as st
import pandas as pd
import os
import tempfile
from resume_parser import EnhancedResumeParser

parser = EnhancedResumeParser()

st.title("Resume Parser App")

uploaded_files = st.file_uploader("Choose resume files", accept_multiple_files=True, type=['pdf', 'docx'])

if uploaded_files:
    st.write(f"Uploaded {len(uploaded_files)} files")


    with tempfile.TemporaryDirectory() as tmpdirname:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(tmpdirname, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

        output_csv = os.path.join(tmpdirname, "parsed_resumes.csv")
        parser.parse_resumes_to_csv(tmpdirname, output_csv)


        df = pd.read_csv(output_csv)
        st.write("Parsed Resume Data:")
        st.dataframe(df)

        analysis_report = parser.analyze_resumes(output_csv)
        st.text("Analysis Report:")
        st.text(analysis_report)

        na_fields = df.columns[df.eq("NA").any()].tolist()
        if na_fields:
            st.write("Fields with NA values:")
            st.write(", ".join(na_fields))

        additional_fields = set(df.columns) - set(parser.base_fields) - {'file_name', 'exp_years'}
        if additional_fields:
            st.write("Additional fields found:")
            st.write(", ".join(additional_fields))

        st.download_button(
            label="Download parsed data as CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name="parsed_resumes.csv",
            mime="text/csv"
        )

st.sidebar.header("Instructions")
st.sidebar.write("""
1. Upload one or more resume files (PDF or DOCX format).
2. The app will parse the resumes and display the extracted information.
3. An analysis report will be generated with insights about the resumes.
4. You can download the parsed data as a CSV file.
5. Fields with NA values and additional fields found will be displayed.
""")