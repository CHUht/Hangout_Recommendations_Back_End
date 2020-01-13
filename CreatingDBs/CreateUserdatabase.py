import sqlite3

# Python code to demonstrate table creation and
# insertions with SQL

# importing module
import sqlite3

# connecting to the database
connection = sqlite3.connect("Database.db")

# cursor
crsr = connection.cursor()

# SQL command to create a table in the database
sql_command = """CREATE TABLE Users (  
user_id INTEGER PRIMARY KEY,  
uname VARCHAR(50),  
pword VARCHAR(50),
address VARCHAR(100),
city VARCHAR(50),
latitude FLOAT(8),
longitude FLOAT(8)
);"""

# execute the statement
crsr.execute(sql_command)


sql_command = """
    SELECT *
    FROM Users
"""

crsr.execute(sql_command)
ans = crsr.fetchall()

for i in ans:
    print(i)

connection.close()
