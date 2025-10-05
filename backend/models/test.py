import mysql.connector
# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Devil@11b",
    database="flask_db"
)
cursor = conn.cursor()
# Tables you don't want to truncate
#skip_tables = {"users", "roles"}
skip_tables = {}
# Step 1: Get all table names
cursor.execute("SHOW TABLES;")
tables = cursor.fetchall()
# Step 2: Disable foreign key checks (important!)
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
# Step 3: Truncate all except skipped ones
for (table_name,) in tables:
    if table_name not in skip_tables:
        cursor.execute(f"TRUNCATE TABLE `{table_name}`;")
        cursor.execute(f"DROP DATABASE flask_db;")
        print(f"Truncated {table_name}")
    else:
        print(f"Skipped {table_name}")
# Step 4: Re-enable foreign key checks
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()
cursor.close()
conn.close()
print(":white_check_mark: Refresh completed (except skipped tables).")