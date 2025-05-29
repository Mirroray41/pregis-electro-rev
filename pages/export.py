import streamlit as st
from database import Database
import datetime
from dateutil.relativedelta import relativedelta
from main import nav_bar
import pandas as pd
from io import BytesIO, StringIO


nav_bar()

database = Database()

st.title('Export')

tier = st.segmented_control(
    "Třída", ("I", "II"), default="I", key=1
)

unprocesed = st.segmented_control(
    "Stav", ("Nezpracováno", "Vše"), default="Nezpracováno", key=6
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

def database_to_df():
    df = pd.DataFrame(columns=[
        "Projekt", "Budova", "Tag spotřebiče", 
        "Název spotřebiče/zařízení", "Stav", "Uživatel",
        "Datum provedení revize", "Datum příští revize", 
        "Umístění", "Aktivita", "Komentář", "Kód opravy",
        "Prohlídka", "Izolační odpor - sonda", 
        "Náhradní unikající proud - sonda", "Ochranný vodič",
        "Izolační odpor", "Náhradní unikající proud"
    ])
    data = database.get_filtered_revisions(tier, date_range, technician, unprocesed == "Nezpracováno")

    for i in data:
        new_row = pd.DataFrame([
            [
                i[3],                                                                                                                                                                           # Projekt
                i[4],                                                                                                                                                                           # Budova
                "",                                                                                                                                                                             # Tag spotřebiče
                i[0],                                                                                                                                                                           # Název spotřebiče/zařízení
                "Vyhovuje" if bool(i[5]) else "Nevyhovuje",                                                                                                                                     # Stav
                i[6],                                                                                                                                                                           # Uživatel
                i[1],                                                                                                                                                                           # Datum provedení revize
                i[7],                                                                                                                                                                           # Datum příští revize
                i[8],                                                                                                                                                                           # Umístění
                "",                                                                                                                                                                             # Aktivita
                "",                                                                                                                                                                             # Komentář
                "",                                                                                                                                                                             # Kód opravy
                "Vyhovuje" if (bool(i[5]) and float(i[11]) < settings.get("leakage_current_max") and bool(i[10]) and float(i[9]) < settings.get("ground_lead_current_max")) else "Nevyhovuje",  # Prohlídka
                (f"{i[11]}Ohm Vyhovuje" if float(i[11]) < settings.get("leakage_current_max") else  f"{i[11]}Ohm Nevyhovuje") if int(i[2]) == 1 else "",                                        # Izolační odpor - sonda
                (">200MOhm Vyhovuje" if bool(i[10]) else "<200MOhm Nevyhovuje") if int(i[2]) == 1 else "",                                                                                      # Náhradní unikající proud - sonda
                f"{i[9]}mA Vyhovuje" if float(i[9]) < settings.get("ground_lead_current_max") else  f"{i[9]}mA Nevyhovuje",                                                                     # Ochranný vodič
                (f"{i[11]}Ohm Vyhovuje" if float(i[11]) < settings.get("leakage_current_max") else  f"{i[11]}Ohm Nevyhovuje") if int(i[2]) == 2 else "",                                        # Izolační odpor
                (">200MOhm Vyhovuje" if bool(i[10]) else "<200MOhm Nevyhovuje") if int(i[2]) == 2 else "",                                                                                      # Náhradní unikající proud
            ]
        ], columns=df.columns)

        df = pd.concat([df, new_row])

    return df.reset_index(drop=True)

df = database_to_df()
table = st.dataframe(df)

excel_data = create_excel_data(df)

st.download_button(
    label="Stáhnout tabulku",
    data=excel_data,
    file_name="Elektro_revize.xlsx",
    mime="application/vnd.openxmlformats-offenticated.spreadsheetml.sheet",
    icon=":material/download:",
)

st.markdown("-----")

uploaded_file = st.file_uploader("Označit revize z tabulky za zpracované")

if uploaded_file is not None:

    bytes_data = uploaded_file.getvalue()

    dataframe = pd.read_excel(uploaded_file)
    st.dataframe(dataframe)
    if st.button("Označit za zpracované"):
        database.mark_as_completed(df.values.tolist())
        st.success("Uspěšně zpracováno")
        df = database_to_df()

