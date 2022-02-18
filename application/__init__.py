from flask_principal import Principal, RoleNeed, Permission
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

principals = Principal(app)

admin_permission = Permission(RoleNeed('admin'))
staff_permission = Permission(RoleNeed('staff'))

from application import user