import sqlite3

con = sqlite3.connect("revisions.db")
cur = con.cursor()

print("Connected to the database")

cur.execute("""CREATE TABLE IF NOT EXISTS revisions(
device_name VARCHAR(5) NOT NULL,
  service_date DATETIME NOT NULL,
  tier INT NOT NULL,
  project VARCHAR(45) NOT NULL,
  building VARCHAR(45) NOT NULL,
  state BOOLEAN NOT NULL,
  technician VARCHAR(45) NOT NULL,
  next_service DATETIME NULL,
  location VARCHAR(45) NOT NULL,
  isolation_resistance_probe INT NULL,
  leakage_current_probe INT NULL,
  ground_lead INT NULL,
  isolation_resistance INT NULL,
  leakage_current INT NULL,
  procesed BOOLEAN NULL,
  PRIMARY KEY (device_name, service_date)
)""")

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()

if tables:
    print("Tables in the database", tables)
else:
    print("No tables found")
