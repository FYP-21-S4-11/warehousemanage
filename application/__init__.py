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

def init_connection_engine() -> sqlalchemy.engine.Engine:
    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            "numeric-asset-341503:us-west4:fypdatabase",
            "pymysql",
            user="root",
            password="root",
            db="fypdatabase",
        )
        return conn

    engine = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )
    return engine

app = Flask(__name__)
app.config["SECRET_KEY"] = "1234"


from datetime import datetime

from flask import redirect, url_for, render_template, request, session, flash, json