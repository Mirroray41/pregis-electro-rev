import sqlite3

con = sqlite3.connect("revisions.db")
cur = con.cursor()

cur.execute("CREATE TABLE revisions(device_name)")

res = cur.execute("SELECT name FROM sqlite_master")
res.fetchone()