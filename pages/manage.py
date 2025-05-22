import streamlit as st
from database import Database
from main import nav_bar
import pandas as pd

nav_bar()

database = Database()

st.title('Správá techniků')

technicians = database.get_all_technicians()

df = pd.DataFrame(columns=["Identifikátor", "Jméno Technika"])

for i in technicians:
    new_row = pd.DataFrame([
        [
            i[0],   # Jméno Technika
            i[1]    # Identifikátor
        ]
    ], columns=df.columns)

    df = pd.concat([df, new_row])

df = df.reset_index(drop=True)
edited_df = st.data_editor(df, num_rows="dynamic")

safe = st.button("Uložit", disabled=not all(all(element is not None for element in row) for row in edited_df.values.tolist()))

st.write()

if safe:
    database.edit_technicians(edited_df.values.tolist())