from fpdf import FPDF
import os

def txt_to_pdf(text, file_name):
    if os.path.exists(file_name):
        os.remove(file_name)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size = 15)
    pdf.cell(200, 10, txt = text,ln = 2, align = 'C')
    pdf.output(file_name)
