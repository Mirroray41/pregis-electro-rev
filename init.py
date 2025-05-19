import streamlit as st
import datetime
from dateutil.relativedelta import relativedelta

st.title('Import')

tier = st.segmented_control(
    "Třída", ("I", "II"), default="I", key=0
)
with st.form("import"):
    technician = st.text_input("Jméno technika")
    device_name = st.text_input("Identifikace spotřebiče")

    isolation_resistance = st.segmented_control(
        "Izolační odpor", ("<200MOhm", "\>200MOhm"), default="\>200MOhm"
    )

    leakage_current = st.number_input("Náhradní unikající proud v mA")

    if tier == "I":
        ground_lead_current = st.number_input("Ochraný vodič v mA")

    submitted = st.form_submit_button("Vložit")

with st.sidebar:
    st.title('Export')

    with st.form("export"):
        tier = st.segmented_control(
            "Třída", ("I", "II"), default="I", key=1
        )
        technician = st.text_input("Jméno technika")
        
        date_range = st.date_input(
            "Časový rozsah",
            (datetime.datetime.now() + relativedelta(months=-1), datetime.datetime.now()),
            format="DD.MM.YYYY",
        )

        submitted = st.form_submit_button("Stáhnout tabulku")
