import os, sys, inspect

# Ensure root directory is in Python path (works in Streamlit)
current_file = os.path.abspath(inspect.getfile(inspect.currentframe()))
project_root = os.path.abspath(os.path.join(os.path.dirname(current_file), ".."))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now safe to import
from modules.xml_cleaner import clean_xml
from modules.excel_builder import generate_excel_report, save_report_to_excel
import streamlit as st


st.title("🧠 XML Smart Cleaner & Tracker")

uploaded = st.file_uploader("Upload XML", type=["xml"])
mode = st.radio("Choose Mode:", ["Clean XML", "Generate Excel Report"])

if uploaded:
    xml_text = uploaded.read().decode("utf-8")

    if st.button("Run"):
        if mode == "Clean XML":
            cleaned = clean_xml(xml_text)
            st.text_area("Cleaned XML", cleaned, height=350)

        elif mode == "Generate Excel Report":
            cleaned = clean_xml(xml_text)
            df = generate_excel_report(xml_text, cleaned)
            filename, excel_buffer = save_report(df)

            st.success("Report Ready!👇")
            st.download_button("📥 Download Excel", excel_buffer, filename, mime="application/vnd.ms-excel")

