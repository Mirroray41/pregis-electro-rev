import streamlit as st
import datetime
from dateutil.relativedelta import relativedelta
import sqlite3
import base64
from io import BytesIO

# STREAMLIT

st.title('Import')

tier = st.segmented_control(
    "Třída", ("I", "II"), default="I", key=0
)
with st.form("import"):
    technician = st.text_input("Jméno technika", placeholder="Př: NOVAKPE")
    device_name = st.text_input("Identifikace spotřebiče", placeholder="X0123")
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
        "Izolační odpor", ("<200MOhm", "\>200MOhm"), default="\>200MOhm"
    )

    leakage_current = st.number_input("Náhradní unikající proud v mA")

    if tier == "I":
        ground_lead_current = st.number_input("Ochraný vodič v mA")

    submitted = st.form_submit_button("Vložit")

    if submitted:
        if (technician and device_name):
            command = f"""
INSERT INTO revisions 
    VALUES (
        '{device_name}',
        '{service_datetime.strftime("%Y-%m-%d-%H-%M")}',
        {1 if tier == "I" else 2},
        '{project}',
        '{building}',
        {int(state == "Vyhovuje")},
        '{technician}',
        '{service_date + relativedelta(years=2)}',
        '{location}',
        {ground_lead_current},
        {int(isolation_resistance == "\>200MOhm")},
        {leakage_current},
        {int(False)}
    );"""
            cur.execute(command)
            con.commit()
        else:
            if not technician:
                st.error('Pole: Jméno technika, je prázdné')
            if not device_name:
                st.error('Pole: Identifikace spotřebiče, je prázdné')
    

with st.sidebar:
    st.title('Export')
    tier = st.segmented_control(
        "Třída", ("I", "II"), default="I", key=1
    )

    technician = st.text_input("Jméno technika", placeholder="Nechte prázdné pro export všech")
    
    date_range = st.date_input(
        "Časový rozsah",
        (datetime.datetime.now() + relativedelta(months=-1), datetime.datetime.now()),
        format="DD.MM.YYYY",
    )

    with open("./requirements.txt") as f:
        data= f.read()

    st.download_button(
        label="Stáhnout tabulku",
        data=data,
        file_name="data.txt",
        mime="text/plain",
        icon=":material/download:",
    )
