from flask import Flask
import pymysql
import sqlalchemy
from flask import Flask
from google.cloud.sql.connector import connector


def getconn() -> pymysql.connections.Connection:
    conn: pymysql.connections.Connection = connector.connect(
        "project:us-west4:fypdatabase",
        "mysql+pymysql",
        user="root",
        password="root",
        db="fypdatabase",
        auth_plugin="mysql_native_password",
        autocommit=True,
    )
    return conn
mydb = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "1234"


from application import admin, supplier, staff, stock, store, user, product