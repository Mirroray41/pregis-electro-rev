import streamlit as st
from database import Database
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd

st.set_page_config(initial_sidebar_state="collapsed")

def nav_bar():
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Import"):
            st.switch_page("main.py")

    with col2:
        if st.button("Export"):
            st.switch_page("pages/export.py")

    with col3:
        if st.button("Správa techniků"):
            st.switch_page("pages/manage.py")

def main():
    nav_bar()

    database = Database()

    st.title('Import')

    tier = st.segmented_control(
        "Třída", ("I", "II"), default="I", key=0
    )

    technicians = database.get_all_technicians()
    technician = st.selectbox("Výběr technika", [f"{i[1]} - {i[0]}" for i in technicians], key=5)

    device_name = st.text_input("Identifikace spotřebiče", placeholder="X0123")
    with st.expander("Více možností"):
        service_date = st.date_input("Datum servisu", datetime.datetime.now(), format="DD.MM.YYYY")
        service_time = st.time_input("Čas servisu", datetime.datetime.now())

        service_datetime = datetime.datetime(service_date.year, service_date.month, service_date.day, service_time.hour, service_time.minute)

        project = st.text_input("Projekt", "REVIZE")
        building = st.text_input("Budova", "PCL")
        location = st.text_input("Umístění", "pcl")

    state = st.segmented_control(
        "Stav", ("Vyhovuje", "Nevyhovuje"), default="Vyhovuje", key=2
    )

    isolation_resistance = st.segmented_control(
        "Izolační odpor", ("<200MOhm", "&gt;200MOhm"), default="&gt;200MOhm"
    )

    leakage_current = st.number_input("Náhradní unikající proud v mA")
    ground_lead_current = None
    if tier == "I":
        ground_lead_current = st.number_input("Ochraný vodič v mA")

    submitted = st.button("Vložit")

    technician = technician.split("-")[1].lstrip()

    if submitted:
        if device_name:
            database.add_new_revision(device_name, service_datetime, tier, project, building, state, technician, location, ground_lead_current, isolation_resistance, leakage_current)
            st.success('Úspěšně přidáno')
        else:
            st.error('Pole: Identifikace spotřebiče, je prázdné')


    df = pd.DataFrame(columns=[
        "Projekt", "Budova", "Tag spotřebiče", 
        "Název spotřebiče/zařízení", "Stav", "Uživatel",
        "Datum provedení revize", "Datum příští revize", 
        "Umístění", "Aktivita", "Komentář", "Kód opravy",
        "Prohlídka", "Izolační odpor - sonda", 
        "Náhradní unikající proud - sonda", "Ochranný vodič",
        "Izolační odpor", "Náhradní unikající proud"
    ])


    data = database.get_latest_revisions(technician)

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
                (f"{i[11]}Ohm Vyhovuje" if float(i[11]) < 0.3 else  f"{i[11]}Ohm Nevyhovuje") if int(i[2]) == 1 else "",    # Izolační odpor - sonda
                (">200MOhm Vyhovuje" if bool(i[10]) else "<200MOhm Nevyhovuje") if int(i[2]) == 1 else "",                  # Náhradní unikající proud - sonda
                f"{i[9]}mA Vyhovuje" if float(i[9]) < 3.5 else  f"{i[9]}mA Nevyhovuje",                                     # Ochranný vodič
                (f"{i[11]}Ohm Vyhovuje" if float(i[11]) < 0.3 else  f"{i[11]}Ohm Nevyhovuje") if int(i[2]) == 2 else "",    # Izolační odpor
                (">200MOhm Vyhovuje" if bool(i[10]) else "<200MOhm Nevyhovuje") if int(i[2]) == 2 else "",                  # Náhradní unikající proud
            ]
        ], columns=df.columns)

        df = pd.concat([df, new_row])

    df = df.reset_index(drop=True)
    st.dataframe(df)

if __name__ == '__main__':
    main()