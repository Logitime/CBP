# Home.py
import streamlit as st
import configparser
import pyodbc
from datetime import datetime
import threading
from PIL import Image
import os

st.set_page_config(
    page_title="LogiTime Tools",
    page_icon="⏰",
    layout="centered"
)

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

def main():
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Layout
    st.title("ENPPI HQ")
    st.subheader(current_datetime)
    
    # Load and display logo
    try:
        image = Image.open("images.jpg")
        st.image(image, width=400)
    except:
        st.warning("Logo image not found")
    
    st.markdown("### LogiTime Tools ver 1.0 2024")
    st.markdown("Welcome to LogiTime Tools. Please use the sidebar to navigate between pages.")
    
    # Footer
    st.markdown("---")
    st.markdown("*LogiTime_Tools ver 1.0 2024*")

if __name__ == "__main__":
    main()