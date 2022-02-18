from flask_principal import Principal, RoleNeed, Permission
import pymysql.cursors
from flask import Flask


unix_socket = '/cloudsql/{}'.format("numeric-asset-341503:us-west4:fypdatabase")
conn = pymysql.Connect(user="root",
                       password="kafka123@",
                       unix_socket=unix_socket,
                       db="fypdatabase",
                       cursorclass=pymysql.cursors.DictCursor)

if conn.connect():
    print("connect")
elif conn.cursor():
    print("cursor")
else:
    print("None")

app = Flask(__name__)
app.config["SECRET_KEY"] = "1234"

principals = Principal(app)

admin_permission = Permission(RoleNeed('admin'))
staff_permission = Permission(RoleNeed('staff'))

from application import user