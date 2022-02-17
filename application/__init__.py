import mysql.connector
from flask import Flask
import pymysql.cursors
from google.cloud.sql.connector import connector
import sqlalchemy

def getconn() -> pymysql.connections.Connection:
    conn: pymysql.connections.Connection = connector.connect(
        "numeric-asset-341503:us-west4:fypdatabase",
        "pymysql",
        user="root",
        password="shhh",
        db="fypdatabase"
    )
    return conn

pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)
app = Flask(__name__)
app.config["SECRET_KEY"] = "1234"

from application import admin, supplier, staff, stock, store, user, product