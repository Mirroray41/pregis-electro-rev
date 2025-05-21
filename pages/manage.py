import streamlit as st
from database import Database
from main import nav_bar

nav_bar()

database = Database()

st.title('Management')
