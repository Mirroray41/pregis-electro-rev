import streamlit as st
from database import Database
import datetime
from dateutil.relativedelta import relativedelta
from main import nav_bar

nav_bar()

database = Database()

st.title('Import')

tier = st.segmented_control(
    "Třída", ("I", "II"), default="I", key=0
)
with st.form("import"):
    technicians = database.get_all_technicians()
    technician = st.selectbox("Výběr technika", [f"{i[1]} - {i[0]}" for i in technicians])

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

    submitted = st.form_submit_button("Vložit")

    if submitted:
        technician = technician.split("-")[1].lstrip()
        if device_name:
            database.add_new_revision(device_name, service_datetime, tier, project, building, state, technician, location, ground_lead_current, isolation_resistance, leakage_current)
            st.success('Úspěšně přidáno')
        else:
            st.error('Pole: Identifikace spotřebiče, je prázdné')