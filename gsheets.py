import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

SCOPE = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

def connect():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],  # ambil dari Streamlit secrets
        scopes=SCOPE
    )
    return gspread.authorize(creds)

def ws(name):
    gc = connect()
    sh = gc.open("Klasemen eFootball")
    return sh.worksheet(name)
