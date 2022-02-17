import mysql.connector
from flask import Flask, app
import pymysql.cursors
import sqlalchemy
import os
from typing import Generator

from mysql import connector
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

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