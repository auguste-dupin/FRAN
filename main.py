from pdf import *
from tools import *


populate_pdfs(5)

for pdf in pdfs:
    pdf.description()
    pdf.load_tables(show_by_tables=False)
    pdf.merge_tables()
    pdf.move_pdf()
    pdf.save()