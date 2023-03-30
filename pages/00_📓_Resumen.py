import streamlit as st
import base64

def displayPDF(file):
    # Opening file from file path
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="1105" height="900" type="application/pdf">'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)

# Llamada a la función displayPDF con la ruta del archivo pdf

pdf_path = "briefing.pdf"

displayPDF(pdf_path)