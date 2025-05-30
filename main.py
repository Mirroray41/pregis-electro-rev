import streamlit as st
from database import Database
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import re
import yaml

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

    logo_sidebar = 'img/logo_pregis.png'
    main_body_logo = 'img/logo_pregis.png'

    st.logo(logo_sidebar, icon_image=main_body_logo)

def main():
    nav_bar()

    database = Database()

    with open('settings.yml', 'r') as f:
        settings = yaml.load(f, Loader=yaml.SafeLoader)

    st.title('Import')

    tier = st.segmented_control(
        "Třída", ("I", "II"), default="I", key=0
    )

    technicians = database.get_all_technicians()
    technician = st.selectbox("Výběr technika", [f"{i[1]} - {i[0]}" for i in technicians], key=5)
    device_name = st.text_input("Identifikace spotřebiče", placeholder="X01234")
    

    name_check = re.search(r"^[a-zA-Z]\d{4}$", device_name)
    
    

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

    leakage_current = st.number_input(f"Náhradní unikající proud v mA (Přechodový), max: {settings.get("leakage_current_max")}mA")

    isolation_resistance = st.segmented_control(
        f"Izolační odpor, min: {settings.get("isolation_resistance_min")}MOhm", ("<200MOhm", "&gt;200MOhm"), default="&gt;200MOhm"
    )

    ground_lead_current = None
    if tier == "I":
        ground_lead_current = st.number_input(f"Ochraný vodič v mA (Proud ochranou), max: {settings.get("ground_lead_current_max")}mA")

    submitted = st.button("Vložit", disabled= ((not name_check) and (isolation_resistance==None or state==None)))

    try:
        technician = technician.split("-")[1].lstrip()
    except AttributeError:
        st.error("Nejdříve musíte přidat alespoň jednoho technika")
    
    if submitted:
        if device_name and name_check:
            database.add_new_revision(device_name.upper(), service_datetime.date(), 1 if tier == "I" else 2, project, building, int(state == "Vyhovuje"), technician, location, ground_lead_current, int(isolation_resistance == "&gt;200MOhm"), leakage_current, 0)
            st.success('Úspěšně přidáno')
        else:
            st.error('Pole: Identifikace spotřebiče, je prázdné nebo chybně zadané')

    st.markdown("-----")

    st.write("Posledních 10 revizí")

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


        data = database.get_latest_revisions(technician)

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
    st.dataframe(df)

    st.markdown("-----")

    uploaded_file = st.file_uploader("Nahrát tabulku do databáze")

    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()

        dataframe = pd.read_excel(uploaded_file)
        st.dataframe(dataframe)
        col1, col2 = st.columns(2)
        with col1:
            add = st.button("Přidat do databáze")
        with col2:
            add_and_mark = st.button("Přidat a označit za zpracované")
        if add or add_and_mark:
            for i in dataframe.values.tolist():
                date_part, time_part = str(i[6]).split(" ")
                date_part = date_part.split("-")
                time_part = time_part.split(":")
                service_date = datetime.datetime(year=int(date_part[0]), month=int(date_part[1]), day=int(date_part[2]), hour=int(time_part[0]), minute=int(time_part[1]), second=int(time_part[2]))
                if str(i[15]) != "nan":
                    database.add_new_revision(i[3], service_date, 2, i[0], i[1], i[4], i[5], i[8], float(i[15].split(" ")[0][:-2]), float(i[13].split(" ")[0][:-3]), int(i[14].split(" ")[1]=="Vyhovuje"), int(add_and_mark))
                else:
                    database.add_new_revision(i[3], service_date, 1, i[0], i[1], i[4], i[5], i[8], None, int(i[16].split(" ")[1]=="Vyhovuje"), float(i[17].split(" ")[0][:-3]), int(add_and_mark))
            st.success("Uspěšně zpracováno")

if __name__ == '__main__':
    main()