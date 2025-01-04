# pages/1_Insert_Traversal_Time.py
import streamlit as st
import pyodbc
import configparser
from datetime import datetime
import time

# Read the connection information from an ini file
config = configparser.ConfigParser()
config.read('connection.ini')

def create_connection():
    server = config.get('connection', 'server')
    database = config.get('connection', 'database')
    username = config.get('connection', 'username')
    password = config.get('connection', 'password')

    conn_str = f'DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password}'
    conn = pyodbc.connect(conn_str)
    return conn

def insert_TRSL():
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Get distinct EMP values
        sql_query = 'SELECT DISTINCT EMP FROM OGS_2'
        emp_rows = cursor.execute(sql_query).fetchall()
        total_emps = len(emp_rows)

        # Create a progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Iterate through the distinct EMP values
        for i, emp_row in enumerate(emp_rows):
            emp = emp_row.EMP

            insert_query = '''
                INSERT INTO [dbo].[TRSL]
                    ([BDR], [DAT], [DUR], [EMP], [STS], [URS], [USR_MOD])
                SELECT
                    '1' AS [BDR],
                    [dur_values].[DAT],
                    [dur_values].[DUR],
                    [dur_values].[EMP],
                    1 AS [STS],
                    CASE
                        WHEN [dur_values].[row_num] = 1 THEN '261'
                        WHEN [dur_values].[row_num] = 2 THEN '262'
                        WHEN [dur_values].[row_num] = 3 THEN '263'
                        WHEN [dur_values].[row_num] = 4 THEN '264'
                        WHEN [dur_values].[row_num] = 5 THEN '265'
                    END AS [URS],
                    'LOGI' AS [USR_MOD]
                FROM
                    (
                        SELECT
                            [traveltime] AS [DUR],
                            [DAT],
                            [EMP],
                            ROW_NUMBER() OVER (PARTITION BY [EMP] ORDER BY [traveltime]) AS [row_num]
                        FROM
                            [OGS_3]
                    ) AS [dur_values]
                WHERE
                    [dur_values].[row_num] <= 5
                    AND NOT EXISTS (
                        SELECT 1
                        FROM [dbo].[TRSL] AS [existing]
                        WHERE [existing].[DAT] = [dur_values].[DAT]
                            AND [existing].[EMP] = [dur_values].[EMP]
                            AND [existing].[URS] = CASE
                                                        WHEN [dur_values].[row_num] = 1 THEN '261'
                                                        WHEN [dur_values].[row_num] = 2 THEN '262'
                                                        WHEN [dur_values].[row_num] = 3 THEN '263'
                                                        WHEN [dur_values].[row_num] = 4 THEN '264'
                                                        WHEN [dur_values].[row_num] = 5 THEN '265'
                                                    END
                            AND [existing].[USR_MOD] = 'LOGI'
                    )
            '''

            cursor.execute(insert_query)
            
            # Update progress
            progress = (i + 1) / total_emps
            progress_bar.progress(progress)
            status_text.text(f"Processing: {int(progress * 100)}% complete")
            
        conn.commit()
        st.success("Data insertion completed successfully!")
        
    except Exception as e:
        st.error(f'Query Execution Error: {str(e)}')

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def main():
    st.title("Insert Daily Travel Time For Employees")
    
    if st.button("Start Insertion", type="primary"):
        insert_TRSL()

if __name__ == "__main__":
    main()