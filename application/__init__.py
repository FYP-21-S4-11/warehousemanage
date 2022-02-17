import mysql.connector
from flask import Flask, Response

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    port="3306",
    database="fypdatabase",
    auth_plugin="mysql_native_password",
    autocommit=True)
mycursor = mydb.cursor()

app = Flask(__name__)
app.config["SECRET_KEY"] = "1234"

from application import admin, supplier, staff, stock, store, user, product