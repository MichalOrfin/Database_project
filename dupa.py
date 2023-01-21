import flask
import sqlite3

connection = sqlite3.connect('fpl_v2.db')
cursor = connection.cursor()
cursor.execute('select * from merged_gw limit 10')
result = cursor.fetchall()
print(result)