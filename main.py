import streamlit as st
from database import Database
import os

st.set_page_config(initial_sidebar_state="collapsed")

def nav_bar():
    rev_import, rev_export, manage = st.columns(3)
    
    with rev_import:
        st.page_link("pages/import.py", label="Import")

    with rev_export:
        st.page_link("pages/export.py", label="Export")

    with manage:
        st.page_link("pages/manage.py", label="Manage")

nav_bar()

#st.switch_page("pages/import.py")

database = Database()


    

