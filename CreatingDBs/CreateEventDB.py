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
sql_command = """CREATE TABLE Events (  
event_id INTEGER PRIMARY KEY,  
title VARCHAR(50),  
category VARCHAR(50),
price VARCHAR(50),
description VARCHAR(300),
link VARCHAR(50),
telephone VARCHAR(50),
tags VARCHAR(50),
address_street VARCHAR(50),
address_city VARCHAR(50),
address_zipcode VARCHAR(50),
date VARCHAR(50),
date_end VARCHAR(50),
contact_mail VARCHAR(50),
facebook VARCHAR(50),
website VARCHAR(50),
latitude FLOAT(8),
longitude FLOAT(8)
);"""

# execute the statement
crsr.execute(sql_command)

connection.close()
