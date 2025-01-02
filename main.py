import pyodbc as pyo
from sqlalchemy import create_engine
from sqlalchemy import create_engine,inspect

from sqlalchemy.ext.automap import automap_base

import pandas as pd
import sqlalchemy as sa

from sqlalchemy.orm import sessionmaker

def get_sqlalchemy_engine(access_db_path):
    print("starting Alchemy")
    connection_string = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"DBQ={access_db_path};"
        r"ExtendedAnsiSQL=1;")
    connection_url = sa.engine.URL.create(
        "access+pyodbc",
        query={"odbc_connect": connection_string}
    )
    print("connection_string:", connection_string)
    print("connection_url:", connection_url)

    engine = sa.create_engine(connection_url)
    return engine

def start_odbc(db_path):

    print("starting PYODBC")
    dbq_string = "DBQ={}".format(db_path)
    driver_string = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
    cnn_string = driver_string + dbq_string
    print("accessdb:", cnn_string)
    cnn = pyo.connect(cnn_string)
    cursor = cnn.cursor()
    tables_list = [t.table_name for t in cursor.tables(tableType='TABLE')]
    print(tables_list)

#start(r"C:\Users\babaz\OneDrive\Desktop\Solas\Database Updated 2024-V1m.accdb")

access_db_path = r"C:\Users\babaz\OneDrive\Desktop\Solas\Database Updated 2024-V1m.accdb"


engine = get_sqlalchemy_engine(access_db_path)

inspector = inspect(engine)
tables = inspector.get_table_names()
print(tables)

#Base = sa.ext.declarative.declarative_base()
#metadata.reflect(engine)


#write df to db
#df = pd.DataFrame([(1, "foo2"), (2, "bar")], columns=["id", "txt"])
#df.to_sql("my_table", engine, index=False, if_exists="append")

Base = automap_base()
Base.prepare(engine, reflect=True)
tables = Base.metadata.tables.keys()
print("metadata tables:",tables)



# 3. Get the class corresponding to a specific table
# Assuming you have a table named 'example_table'
ClientIDTable = Base.classes.get('Client ID')

columns = ClientIDTable.__table__.columns

# 6. Print the list of column names (fields)
for column in columns:
    print(column.name)



Session = sessionmaker(bind=engine)
session = Session()

# Query to verify
results = session.query(ClientIDTable).all()

for row in results:
    print(vars(row))

