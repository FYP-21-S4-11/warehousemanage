from datetime import datetime

from flask import redirect, url_for, render_template, request, session, flash, json
# kafka stuff
# =======================================
from kafka import KafkaProducer

from application import app
from application import mydb as ksql
from webforms import LoginForm


def json_serializer(data):
    return json.dumps(data).encode("utf-8")
producer = KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=json_serializer)
jsonproducer = KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=lambda x: json.dumps(x).encode('utf-8'))

#date time for json
def dtnow():
    dt = datetime.now()
    str_now = str(dt)
    str_now = str_now[:-6]
    return str_now
#========================================

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # request username and password
        username = request.form["username"]
        password = request.form["password"]
        usertype = request.form["type"]
        _datetime = dtnow()
        _activity = "Logged in"
        _username = str(username)
        logindict = {"User": _username, "Activity": _activity, "Time": _datetime}
        _activitynoti = _username +" "+ _activity
        notificationdict = {"User": "Notification", "Activity": _activitynoti, "Time": _datetime}
        # check if username and password exists in database User
        cur = ksql.cursor()
        cur.execute("SELECT UserType, Username FROM User WHERE Username = %s AND UserPW = %s AND UserType = %s",
                    (username, password, usertype,))
        record = cur.fetchone()
        # print(record, username, password, usertype)
        if "Admin" in str(record):
            session["loggedin"] = True
            session["username"] = record[1]
            session["usertype"] = record[0]
            print(usertype)
            flash("Logged in successfully! Welcome, " + username)
            jsonproducer.send("logintopic", logindict)
            jsonproducer.send("notificationtopic", notificationdict)
            return redirect(url_for("adminhome"))
        elif "Staff" in str(record):
            session["loggedin"] = True
            session["username"] = record[1]
            session["usertype"] = record[0]
            flash("Logged in successfully! Welcome, " + username)
            print(usertype)
            jsonproducer.send("logintopic", logindict)
            jsonproducer.send("notificationtopic", notificationdict)
            return redirect(url_for("staffhome"))
        elif not username or not password or not type:
            flash("Incorrect Username/Password! Please Try Again.")
            return render_template("login.html", form=form)
        elif "Supplier" in usertype:
            cur = ksql.cursor()
            cur.execute(
                "SELECT * FROM Supplier WHERE SupplierCode = %s AND SupplierPassword = %s"
                , (username, password))
            found_user = cur.fetchone()
            cur.close()
            if found_user:
                session["username"] = found_user[0]
                username = found_user[1]
                flash("Logged in successfully! Welcome, " + username )
                jsonproducer.send("logintopic", logindict)
                jsonproducer.send("notificationtopic", notificationdict)
                return redirect(url_for("supplierhome"))
            else:
                flash("Incorrect Username/Password! Please Try Again.")
                return render_template("login.html", form=form)
        else:
            flash("Login Error")
            return render_template("login.html", form=form)
    return render_template("login.html", form=form)

# Logout
@app.route("/logout/")
def logout():
    if "username" in session:
        username = session["username"]
        _datetime = dtnow()
        _activity = "Logged out"
        _username = str(username)
        logoutdict = {"User": _username, "Activity": _activity, "Time": _datetime}
        _activitynoti = _username + " " + _activity
        notificationdict = {"User": "Notification", "Activity": _activitynoti, "Time": _datetime}
        session.pop("loggedin", None)
        session.pop("username",None)
        flash("Logged Out successfully!")
        jsonproducer.send("logintopic", logoutdict)
        jsonproducer.send("notificationtopic", notificationdict)
        return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))