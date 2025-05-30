import streamlit as st
import sqlite3
import datetime
from dateutil.relativedelta import relativedelta
import datetime

class Database(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Database, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.con = sqlite3.connect("revisions.db")
        self.cur = self.con.cursor()

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS technicians (
            idname VARCHAR(45) NOT NULL,
            frendly_name VARCHAR(45) NOT NULL,
            PRIMARY KEY (idname)
        )
        """)

        self.cur.execute("""
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
        )""")

    def get_all_technicians(self):
        return self.cur.execute("SELECT * FROM technicians").fetchall()

    def get_filtered_revisions(self, tier, date_range, technician, unprocesed):
        if unprocesed: 
            if len(date_range) > 1:
                return self.cur.execute("SELECT *  FROM revisions WHERE tier = (:tier) AND service_date BETWEEN (:date_range_1) AND (:date_range_2) AND technician = (:technician) AND procesed = 0", {'tier': 1 if tier == "I" else 2, 'date_range_1': date_range[0], 'date_range_2': date_range[1] + relativedelta(days=1), 'technician': technician}).fetchall()
            else:
                return self.cur.execute("SELECT *  FROM revisions WHERE tier = (:tier) AND service_date BETWEEN (:date_range_1) AND (:date_range_2) AND technician = (:technician) AND procesed = 0", {'tier': 1 if tier == "I" else 2, 'date_range_1': date_range[0], 'date_range_2': date_range[0] + relativedelta(days=1), 'technician': technician}).fetchall()
        else:
            if len(date_range) > 1:
                return self.cur.execute("SELECT *  FROM revisions WHERE tier = (:tier) AND service_date BETWEEN (:date_range_1) AND (:date_range_2) AND technician = (:technician)", {'tier': 1 if tier == "I" else 2, 'date_range_1': date_range[0], 'date_range_2': date_range[1] + relativedelta(days=1), 'technician': technician}).fetchall()
            else:
                return self.cur.execute("SELECT *  FROM revisions WHERE tier = (:tier) AND service_date BETWEEN (:date_range_1) AND (:date_range_2) AND technician = (:technician)", {'tier': 1 if tier == "I" else 2, 'date_range_1': date_range[0], 'date_range_2': date_range[0] + relativedelta(days=1), 'technician': technician}).fetchall()


    def get_latest_revisions(self, technician):
        return self.cur.execute(f"SELECT *  FROM revisions WHERE technician = (:technician) ORDER BY service_date DESC LIMIT 10 ", {'technician': technician}).fetchall()


    def add_new_revision(self, device_name, service_datetime, tier, project, building, state, technician, location, ground_lead_current, isolation_resistance, leakage_current, procesed):
        self.cur.execute(
            """INSERT OR REPLACE INTO revisions VALUES (
                :device_name, 
                :service_datetime, 
                :tier, :project, 
                :building, 
                :state, 
                :technician, 
                :next_service, 
                :location, 
                :ground_lead_current, 
                :isolation_resistance, 
                :leakage_current, 
                :procesed
            )""", 
            {'device_name': device_name, 
                    'service_datetime': service_datetime.strftime("%Y-%m-%d %H:%M:00"), 
                    'tier': tier, 
                    'project': project, 
                    'building': building, 
                    'state': state, 
                    'technician': technician, 
                    'next_service': service_datetime + relativedelta(years=2), 
                    'location': location, 
                    'ground_lead_current': ground_lead_current if ground_lead_current else 0, 
                    'isolation_resistance': isolation_resistance, 
                    'leakage_current': leakage_current, 
                    'procesed': procesed
            })
        self.con.commit()

    def edit_technicians(self, technicians):
        self.cur.execute("DELETE FROM technicians")
        for i in technicians:
            if i[0] != None and i[1] != None:
                self.cur.execute("INSERT INTO technicians VALUES (:idname, :friendlyname)", {'idname': i[0], 'friendlyname': i[1]})
                self.con.commit()

    def mark_as_completed(self, table):
        for i in table:
            self.cur.execute("UPDATE revisions SET procesed = 1 WHERE device_name = (:name) AND service_date = (:date)", {'name': i[3], 'date': i[6]})
            self.con.commit()
