import os, shutil, re
import PyPDF2
import camelot
from config import *
from tools import *
from excel import *


i20_i21_texts = ['OUTLETS AND FRANCHISEE INFORMATION', 'FINANCIAL STATEMENTS']
pdfs = []

class PDF:
    def __init__(self, file):
        self.name = file.split('.')[0]
        self.file = file
        self.path = pdf_path+file
        self.readable = self.is_readable()
        pdfs.append(self)

    def is_readable(self):
        pdf_file = PyPDF2.PdfFileReader(self.path)
        page_number = find_i20_i21(pdf_file)
        if page_number:
            self.start_page = page_number[0]
            self.end_page = page_number[1]
            return True
        else:
            self.starting_page = None
            return False
    
    def loading(self, counter, number_of_files):
        print(f'Loaded: {self.name} | {counter}/{number_of_files}')

    def description(self):
        if self.readable:
            print(f'---\nName: {self.name} | Readable: {self.readable} | Pages: {self.start_page}-{self.end_page}')
        else:
            print(f'---\nName: {self.name} | Not readable')

    def load_tables(self, show_by_columns=False, show_by_tables=False):
        if self.readable:
            print('Reading Tables')
            self.tables = camelot.read_pdf(self.path, pages=(f"{self.start_page}-{self.end_page}"))
            # first_row_to_header(self)
            print(f'Found {len(self.tables)} tables')
            self.table_by_columns(show=show_by_columns)
            self.table_with_columns(show=show_by_tables)
        else:
            separator()
            self.tables = []

    def table_by_columns(self, show=False):
        dfs = {}
        new_dfs = {}

        for i in range(50):
            dfs[i] = []

        for counter, table in enumerate(self.tables):
            n = len(table.df.columns)
            dfs[n].append(counter)
        
        for i in range(len(dfs)):
            if dfs[i]:
                new_dfs[i] = dfs[i]
        
        self.dfs = new_dfs

        if show:
            for key in self.dfs:
                print(f'-{key}: {self.dfs[key]}')

    def table_with_columns(self, show):
        dfs = {}
        for i, table in enumerate(self.tables):
            dfs[i] = table.shape[1]
        self.dict_cols = dfs
        if show:
            for key in self.dict_cols:
                print(f'- Table {key}: {self.dict_cols[key]} columns')
        
    def merge_tables(self, show=False):
        new_dfs = {}
        for i, table in enumerate(self.tables):
            last_key = len(new_dfs)-1
            if is_equal_columns(self.dict_cols[i], new_dfs):
                # print(f'new_dfs: {new_dfs}')
                # print(f'only Last key: {last_key}')
                # print(f'Last key: {new_dfs[last_key]}')
                # print(f'Table: {table}')
                # print(f'Table.df: {table.df}')
                new_dfs[last_key] = new_dfs[last_key].append(table.df)
            else:
                new_dfs[last_key+1] = table.df
        
        self.merged_tables = []
        
        for i, table in enumerate(new_dfs):
            self.merged_tables.append(new_dfs[i])
            if show:
                print(f'---\n{i}.\n{new_dfs[i]}')

        remove_repeated_headers(self)

    def move_pdf(self):
        if self.readable:
            shutil.move(self.path, os.path.join(successful_path, self.file))
        else:
            shutil.move(self.path, os.path.join(failed_path, self.file))

    def save(self, name=None):
        if self.readable:
            save_excel(self, name)

def is_equal_columns(columns, dfs):
    last_key = len(dfs)-1
    if last_key < 0:
        return False
    return columns == len(dfs[last_key].columns)

def populate_pdfs(n=None):
    print('Start')
    separator(group='section')
    print('Loading...')

    number_of_files = len(os.listdir(pdf_path))

    if n == None:
        n = number_of_files
    
    for counter, file in enumerate(os.listdir(pdf_path)[:n]):
        pdf = PDF(file)
        pdf.loading(counter+1, n)
    
    print('Finished loading')
    separator(group='section')

def find_i20_i21(pdf):
    page_numbers = []
    n = pdf.getNumPages()
    for i in range(15, n):
        page_text = pdf.getPage(i).extractText()

        for text in i20_i21_texts:
            string_search = re.search(text, page_text)
            if string_search != None:
                page_numbers.append(i)

    if len(page_numbers) == 1:
        end = page_numbers[0] + 20
        page_numbers.append(end)

    if page_numbers:
        return page_numbers
    else:
        return False



def remove_repeated_headers(pdf):
    tables = []
    for table in pdf.merged_tables:
        headers = table.iloc[0]
        table.columns = [headers]
        table.drop(0, axis=0, inplace=True)
        for i, row in enumerate(table):
            if row == headers.values.all():
                table.drop(i, axis=0, inplace=True)
        table.dropna(how='all', axis=0, inplace=True)
        tables.append(table)
    pdf.merged_tables = tables