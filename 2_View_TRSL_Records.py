# pages/2_View_TRSL_Records.py
import streamlit as st
import pyodbc
import configparser
import pandas as pd
from datetime import datetime

# Read the connection information from an ini file
config = configparser.ConfigParser()
config.read('connection.ini')

# Custom CSS
st.markdown("""
<style>
    .stDataFrame {
        font-family: Arial, sans-serif;
        font-size: 14px;
    }
    
    .filter-section {
        background-color: #f2f2f2;
        padding: 10px;
        margin-bottom: 20px;
        border-radius: 4px;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 24px;
    }
</style>
""", unsafe_allow_html=True)

def create_connection():
    server = config.get('connection', 'server')
    database = config.get('connection', 'database')
    username = config.get('connection', 'username')
    password = config.get('connection', 'password')

    conn_str = f'DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password}'
    conn = pyodbc.connect(conn_str)
    return conn

def view_TRSL():
    try:
        conn = create_connection()
        
        view_query = '''
            SELECT 
                BDR, 
                DAT, 
                DUR, 
                EMP, 
                STS, 
                URS, 
                USR_MOD, 
                CONVERT(VARCHAR, DATEADD(DAY, DAT - 2, '1900-01-01'), 103) AS Today_Date,
                CASE 
                    WHEN DUR > 60 THEN DUR - 60 
                    ELSE 0 
                END AS Extra_Minutes
            FROM 
                TRSL 
            WHERE 
                USR_MOD = 'LOGI' 
        '''
                #AND DAT = DATEDIFF(day, '1899-12-30', CAST(GETDATE() AS DATE))-1;
        
        
        df = pd.read_sql(view_query, conn)
        return df

    except Exception as e:
        st.error(f"Query Execution Error: {str(e)}")
        return None

    finally:
        if 'conn' in locals():
            conn.close()

def highlight_duration(df):
    """
    Highlight durations based on conditions
    """
    styles = []
    for idx in range(len(df)):
        row_style = []
        for col in df.columns:
            if col == 'DUR':
                duration = df.iloc[idx]['DUR']
                if duration > 60:
                    row_style.append('background-color: red; color: white')
                else:
                    row_style.append('background-color: green; color: white')
            elif col == 'Extra_Minutes':
                extra = df.iloc[idx]['Extra_Minutes']
                if extra > 0:
                    row_style.append('background-color: red; color: white')
                else:
                    row_style.append('background-color: green; color: white')
            else:
                row_style.append('')
        styles.append(row_style)
    
    return pd.DataFrame(styles, columns=df.columns, index=df.index)

def main():
    st.title("View TRSL Records")
    
    # Filter section
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("Show All", type="primary"):
            st.session_state.duration_filter = False
            st.session_state.emp_filter = ""
    
    with col2:
        emp_filter = st.text_input("Filter by Employee ID (EMP)", 
                                 value=st.session_state.get('emp_filter', ""))
        st.session_state.emp_filter = emp_filter
    
    with col3:
        duration_filter = st.checkbox("Show DUR > 60 min only", 
                                    value=st.session_state.get('duration_filter', False))
        st.session_state.duration_filter = duration_filter
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Get and filter data
    if 'data' not in st.session_state or st.button("Refresh Data"):
        st.session_state.data = view_TRSL()
    
    if st.session_state.data is not None:
        filtered_df = st.session_state.data.copy()
        
        # Apply filters
        if st.session_state.emp_filter:
            filtered_df = filtered_df[filtered_df['EMP'].astype(str).str.contains(st.session_state.emp_filter, case=False)]
        
        if st.session_state.duration_filter:
            filtered_df = filtered_df[filtered_df['DUR'] > 60]
        
        # Apply styling
        styled_df = filtered_df.style.apply(highlight_duration, axis=None)
        
        # Display the styled dataframe
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Summary section
        st.subheader("Summary Statistics")
        cols = st.columns(4)
        with cols[0]:
            st.metric("Total Records", len(filtered_df))
        with cols[1]:
            st.metric("Average Duration", f"{filtered_df['DUR'].mean():.1f} min")
        with cols[2]:
            st.metric("Records > 60 min", len(filtered_df[filtered_df['DUR'] > 60]))
        with cols[3]:
            st.metric("Unique Employees", len(filtered_df['EMP'].unique()))
        
        # Download section
        st.download_button(
            "Download as CSV",
            filtered_df.to_csv(index=False).encode('utf-8'),
            "TRSL_records.csv",
            "text/csv",
            key='download-csv'
        )

if __name__ == "__main__":
    main()