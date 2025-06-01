import globals as glb
#import polars as pl

import pyodbc as pyo

from sqlalchemy import create_engine,inspect

from sqlalchemy.ext.automap import automap_base

import pandas as pd
import sqlalchemy as sa

from sqlalchemy.orm import sessionmaker

from custom import custom_dict



if glb.ACCESS_PARSER:
    # access_parser does not parse the big tables properly.  Misses entries
    from access_parser_c import AccessParser
if glb.MDB_PARSER:
    # mdb_parser uses mdb-tools, which mees a docker file is needed
    # Also does not parse dates into 4 digit years.  Better not have dates from 1900s
    from app.mdb_parser import MDBParser, MDBTable

if glb.PYODBC:
    import pyodbc as pyo

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

def process_db_sqlalchemy(db_path):
    engine = get_sqlalchemy_engine((db_path))
    print("-------------------------process_db_sqlalchemy:-----------------------------------",engine)
    pass

def process_db(db_path):
    if glb.MDB_PARSER:
        print("starting MDB_PARSER")
        glb.db = MDBParser(file_path=db_path)
        glb.tables_list = [e for e in glb.db.tables if not e.startswith('MS') and len(e) < 30]
        glb.table_selected = glb.tables_list[0]

        glb.tables_dict = {}

        for table_name in glb.tables_list:

            table = glb.db.get_table(table_name)

            for column in table.columns:
                print(f"process_db {column}:{column.datatype}")

            #print("count of nans:")
            #print(table.isna().sum())
            table.fillna('',inplace=True)

            #print("--------------------------table--------------------------------: ",table_name)
            #print(table)
            rows = [row for row in table]
            #print("type rows:",type(rows[0][0]))
            #glb.project_df = pd.DataFrame(rows,columns=table.columns)
            if glb.USE_DF:
                glb.tables_dict[table_name] = pd.DataFrame(rows,columns=table.columns)
            if glb.USE_PL:
                glb.tables_dict[table_name] = pl.DataFrame(rows,schema=table.columns,orient="row")

    if glb.PYODBC:
        print("starting PYODBC")
        dbq_string = "DBQ={}".format(db_path)
        driver_string = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
        cnn_string = driver_string + dbq_string
        print("accessdb:", cnn_string)
        glb.cnn = pyo.connect(cnn_string)
        cursor = glb.cnn.cursor()
        #for t in cursor.tables():
            #print("name:",t.table_name)
            ##print("type:",t.table_type)
        glb.tables_list = [t.table_name for t in cursor.tables() if t.table_type == 'TABLE']

        #print("process_db tables:",glb.tables_list)

        glb.tables_dict = {}

        for table_name in glb.tables_list:
            #glb.project_df = create_df_sql("select * from [Project Data]",cnn,table_name)
            df = pd.read_sql(f"select * from [{table_name}]", glb.cnn)
            #df.to_sql(table_name, cnn, if_exists='replace', index=False)
            #print("count of nans:")
            #print(df.isna().sum())
            df.fillna('',inplace=True)
            #print("table schema:")
            glb.tables_dict[table_name] = df

    if glb.ALCHEMY:
        glb.engine = get_sqlalchemy_engine(db_path)
        inspector = inspect(glb.engine)

        # Get list of tables
        table_names = inspector.get_table_names()

        glb.tables_dict = {}

       #print("Tables in the Access database:")
        for table_name in table_names:
            df = read_df(table_name)

            #df = df.convert_dtypes()
            #df.fillna('',inplace=True)  #xxx

            #print("setting glb.tables_dict:",table_name,df)
            glb.tables_dict[table_name] = df
            #glb.tables_dict[table] = None


def read_df(table_name):
    #print("read_df:",table_name)
    df = pd.read_sql_table(table_name, con=glb.engine, coerce_float=True)

    force_calls = custom_dict["Tables"][table_name].get("force_numeric", [])
    for col in force_calls:
        #print("forcing:", col)
        try:
            df[col] = pd.to_numeric(df[col], errors='raise')
        except:
            print(f"Unable to force field {col} in table {table_name} to numeric")
            pass

    #print("after forcing:", df.dtypes)
    return df


def create_df_sql(sql,conn,table_name):
    cursor = conn.cursor()



    cursor.execute(sql)
    rows_tuples = cursor.fetchall()
    rows = [list(t) for t in rows_tuples]

    columns = [column[0] for column in cursor.description]

    if glb.USE_DF:
        glb.tables_dict[table_name] = pd.DataFrame(rows, columns=columns)
    if glb.USE_PL:
        glb.tables_dict[table_name] = pl.DataFrame(rows, schemacolumns, orient="row")


def get_db_sqlalchemy(access_db_path):
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

