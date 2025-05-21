import streamlit as st
import datetime
from dateutil.relativedelta import relativedelta
import sqlite3
import xlsxwriter
import base64
from io import BytesIO, StringIO
import csv

def create_table(technician, date_range, tier):
    output = xlsxwriter.Workbook("revisions.xlsx")
    worksheet = output.add_worksheet()
    template = ("Projekt", "Budova", "Tag spotřebiče", "Název spotřebiče/zařízení", "Stav", "Uživatel", "Datum provedení revize", "Datum příští revize", "Umístění", "Aktivita", "Komentář", "Kód opravy", "Prohlídka", "Izolační odpor - sonda", "Náhradní unikající proud - sonda", "Ochranný vodič", "Izolační odpor", "Náhradní unikající proud")
    for i,x in enumerate(template):
        worksheet.write(0, i, x)
    output.close()

# DATABASE

con = sqlite3.connect("revisions.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS technicians (
  idname VARCHAR(45) NOT NULL,
  frendly_name VARCHAR(45) NOT NULL,
  PRIMARY KEY (idname)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS revisions(
    device_name VARCHAR(5) NOT NULL,
    service_date DATETIME NOT NULL,
    tier INT NOT NULL,
    project VARCHAR(45) NOT NULL,
    building VARCHAR(45) NOT NULL,
    state BOOLEAN NOT NULL,
    technician VARCHAR(45) NOT NULL,
    next_service DATETIME NULL,
    location VARCHAR(45) NOT NULL,
    ground_lead INT NULL,
    isolation_resistance BOOLEAN NULL,
    leakage_current INT NULL,
    procesed BOOLEAN NULL,
    PRIMARY KEY (device_name, service_date)
    FOREIGN KEY (technician) REFERENCES technicians(idname)
)
""")

# STREAMLIT

st.title('Import')

tier = st.segmented_control(
    "Třída", ("I", "II"), default="I", key=0
)
with st.form("import"):
    technicians = cur.execute("SELECT * FROM technicians").fetchall()
    technician = st.selectbox("Výběr technika", [f"{i[1]} - {i[0]}" for i in technicians])

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
    ground_lead_current = None
    if tier == "I":
        ground_lead_current = st.number_input("Ochraný vodič v mA")

    submitted = st.form_submit_button("Vložit")

    if submitted:
        technician = technician.split("-")[1].lstrip()
        if device_name:
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
        {ground_lead_current if ground_lead_current else 0},
        {int(isolation_resistance == "\>200MOhm")},
        {leakage_current},
        {int(False)}
    );"""
            cur.execute(command)
            con.commit()
        else:
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

    def create_csv_data(data_list):
        # Convert data into CSV format
        headers = [ascii("Projekt;Budova;Tag spotřebiče;Název spotřebiče/zařízení;Stav;Uživatel;Datum provedení revize;Datum příští revize;Umístění;Aktivita;Komentář;Kód opravy;Prohlídka;Izolační odpor - sonda;Náhradní unikající proud - sonda;Ochranný vodič;Izolační odpor;Náhradní unikající proud".encode("ascii", "replace"))]
        rows = [";".join(map(str, row)) + "\n" for row in data_list]
        return "".join(headers + rows)

    count = cur.execute("SELECT COUNT(*) FROM revisions")

    data = []

    for row in range(int(count.fetchone()[0])):
        data.append([row])
            
    st.write(cur.execute(f"SELECT WHERE tier IS {1 if tier == "I" else 2} AND WHERE service_date BETWEEN {date_range[0]} and {date_range[1] + relativedelta(days=1)}" + f" AND WHERE technician IS {technician}" if technician else ""))

    st.download_button(
        label="Stáhnout tabulku",
        on_click=create_table(technician, date_range, tier),
        data=create_csv_data(data),
        file_name="data.csv",
        mime="text/cvs",
        icon=":material/download:",
    )

print(f"SELECT WHERE tier IS {1 if tier == "I" else 2} AND WHERE service_date BETWEEN {date_range[0]} and {date_range[1] + relativedelta(days=1)}" + f" AND WHERE technician IS {technician}" if technician else "")
