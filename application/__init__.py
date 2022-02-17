import pymysql.cursors
from flask import Flask


def open_connection():
    unix_socket = '/cloudsql/{}'.format("numeric-asset-341503:us-west4:fypdatabase")
    try:
        conn = pymysql.connect(user="root",
                               password="root",
                               unix_socket=unix_socket,
                               db="fypdatabase",
                               cursorclass=pymysql.cursors.DictCursor)
    except pymysql.MySQLError as e:
        return e
    return conn

app = Flask(__name__)
app.config["SECRET_KEY"] = "1234"

from application import user