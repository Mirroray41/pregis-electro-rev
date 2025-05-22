import streamlit as st
from database import Database
import datetime
from dateutil.relativedelta import relativedelta
from main import nav_bar
import pandas as pd
from io import BytesIO

nav_bar()

database = Database()

st.title('Export')

tier = st.segmented_control(
    "Třída", ("I", "II"), default="I", key=1
)

technicians = database.get_all_technicians()
technician = st.selectbox("Výběr technika", [f"{i[1]} - {i[0]}" for i in technicians])

date_range = st.date_input(
    "Časový rozsah",
    (datetime.datetime.now() + relativedelta(months=-1), datetime.datetime.now()),
    format="DD.MM.YYYY",
)

technician = technician.split("-")[1].lstrip()

def create_excel_data(df):
    """Convert DataFrame to Excel bytes with proper error handling"""
    try:
        output = BytesIO()
        df.to_excel(output, index=False)
        return output.getvalue()
    except Exception as e:
        st.error(f"Failed to convert DataFrame to Excel: {str(e)}")
        return None


df = pd.DataFrame(columns=[
    "Projekt", "Budova", "Tag spotřebiče", 
    "Název spotřebiče/zařízení", "Stav", "Uživatel",
    "Datum provedení revize", "Datum příští revize", 
    "Umístění", "Aktivita", "Komentář", "Kód opravy",
    "Prohlídka", "Izolační odpor - sonda", 
    "Náhradní unikající proud - sonda", "Ochranný vodič",
    "Izolační odpor", "Náhradní unikající proud"
])

data = database.get_filtered_revisions(tier, date_range, technician)

for i in data:
    new_row = pd.DataFrame([
        [
            i[3],                                                                                                       # Projekt
            i[4],                                                                                                       # Budova
            "",                                                                                                         # Tag spotřebiče
            i[0],                                                                                                       # Název spotřebiče/zařízení
            "Vyhovuje" if bool(i[5]) else "Nevyhovuje",                                                                 # Stav
            i[6],                                                                                                       # Uživatel
            i[1],                                                                                                       # Datum provedení revize
            i[7],                                                                                                       # Datum příští revize
            i[8],                                                                                                       # Umístění
            "",                                                                                                         # Aktivita
            "",                                                                                                         # Komentář
            "",                                                                                                         # Kód opravy
            "Vyhovuje" if (bool(i[5]) and float(i[11]) < 0.3 and bool(i[10]) and float(i[9]) < 3.5) else "Nevyhovuje",  # Prohlídka
            f"{i[11]}Ohm Vyhovuje" if float(i[11]) < 0.3 else  f"{i[11]}Ohm Nevyhovuje",                                # Izolační odpor - sonda
            ">200MOhm Vyhovuje" if bool(i[10]) else "<200MOhm Nevyhovuje",                                              # Náhradní unikající proud - sonda
            f"{i[9]}mA Vyhovuje" if float(i[9]) < 3.5 else  f"{i[9]}mA Nevyhovuje",                                     # Ochranný vodič
            f"{i[11]}Ohm Vyhovuje" if float(i[11]) < 0.3 else  f"{i[11]}Ohm Nevyhovuje",                                # Izolační odpor
            ">200MOhm Vyhovuje" if bool(i[10]) else "<200MOhm Nevyhovuje",                                              # Náhradní unikající proud
        ]
    ], columns=df.columns)

    df = pd.concat([df, new_row])

df = df.reset_index(drop=True)
st.dataframe(df)


if df.empty:
    st.error("DataFrame is empty!")
else:
    excel_data = create_excel_data(df)

st.download_button(
    label="Stáhnout tabulku",
    data=excel_data,
    file_name="data.xlsx",
    mime="application/vnd.openxmlformats-offenticated.spreadsheetml.sheet",
    icon=":material/download:",
)