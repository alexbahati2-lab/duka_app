import sqlite3

conn = sqlite3.connect("database/stock.db")
c = conn.cursor()

# Add missing columns safely
try:
    c.execute("ALTER TABLE sales ADD COLUMN attendant TEXT")
except sqlite3.OperationalError:
    pass  # Column already exists

try:
    c.execute("ALTER TABLE sales ADD COLUMN receipt_no TEXT")
except sqlite3.OperationalError:
    pass  # Column already exists

conn.commit()
conn.close()
print("Sales table updated successfully")
