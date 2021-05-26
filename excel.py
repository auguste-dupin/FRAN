import pandas as pd
from config import *


def save_excel(pdf, name):
    if name == None:
        name = pdf.name

    writer = pd.ExcelWriter(f'{excel_path}{name}.xlsx', engine = 'xlsxwriter')

    for i, table in enumerate(pdf.merged_tables):
        sheetname = f'Table {i}'
        table.to_excel(writer, sheet_name=sheetname)
    writer.save()
    print(f'Saved {pdf.name} with {len(pdf.merged_tables)} tables')