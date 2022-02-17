import mysql.connector
from flask import Flask

unix_socket = '/cloudsql/{}'.format("us-west4:fypdatabase")
mydb = mysql.connector.connect(
    user="root",
    password="root",
    database="fypdatabase",
    unix_socket=unix_socket,
    auth_plugin="mysql_native_password",
    autocommit=True)
mycursor = mydb.cursor()

app = Flask(__name__)
app.config["SECRET_KEY"] = "1234"

from application import admin, supplier, staff, stock, store, user, product