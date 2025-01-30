#import pandas as pd
#import polars as pl
import platform

# To create executable, run pyinstaller main.py --onefile --windowed

DEV = False

dev_path = None

if platform.system() == 'Windows':
    PYODBC = False
    ACCESS_PARSER = False
    MDB_PARSER = False
    ALCHEMY = True
    if DEV:
        dev_path = r"C:\Users\babaz\OneDrive\Desktop\Solas\Database Updated 2024-V1m.accdb"
else:
    PYODBC = False
    ACCESS_PARSER = False
    MDB_PARSER = True
    if DEV:
        dev_path = "/home/cc/Solas/data/Database Updated 2024-6.accdb"

USE_DF = True
USE_PL = False


db = None
app = None

project_file = " "
timesheet_file = " "

cnn = None
engine = None
search_term = None
project_titles = None
project_titles_filtered = None
#project_df = pl.DataFrame()
architects = None
architect_rates = None
#timesheet_df = pd.DataFrame()
#financial_df = pd.DataFrame()
#timesheet_df = pl.DataFrame()
#financial_df = pl.DataFrame()
tables_db = None
tables_list = None
table_selected = None
tables_dict = None
start_date = None
end_date = None
timesheet_dict= None
financials_dict = None
ref_iframe = None

saved_primary_color = None
saved_secondary_color = None
saved_highlight_color = None

#dbgs_df = pl.DataFrame()

def global_clear():
    pass