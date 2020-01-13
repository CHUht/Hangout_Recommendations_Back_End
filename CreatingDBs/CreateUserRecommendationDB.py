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
sql_command = """CREATE TABLE UserRecommendations (  
user_id INTEGER, 
event_id INTEGER, 
score FLOAT(8)
);"""

# execute the statement
crsr.execute(sql_command)

# SQL command to insert the data in the table
sql_command = """INSERT INTO UserRating VALUES (0, 1, 2.3);"""
crsr.execute(sql_command)

# To save the changes in the files. Never skip this.
# If we skip this, nothing will be saved in the database.
connection.commit()


sql_command = """
    SELECT *
    FROM Labels
"""

crsr.execute(sql_command)
ans = crsr.fetchall()

for i in ans:
    print(i)

connection.close()
