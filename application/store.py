from datetime import datetime

from flask import redirect, url_for, render_template, request, session, flash, json
# kafka stuff
# =======================================
from kafka import KafkaProducer

from application import app
from application import mydb as ksql
from webforms import StoreAddForm, StoreUpdateForm


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

# Store Menu
@app.route("/storemenu/")
def storemenu():
    if "username" in session:
        username = session["username"]
        return render_template("storemenu.html")
    else:
        return redirect(url_for("login"))

# ===========================
# Store Add
@app.route("/storeadd/", methods=["GET", "POST"])
def storeadd():
    if "username" in session:
        username = session["username"]
        form = StoreAddForm()
        if form.validate_on_submit():
            code = request.form["code"]
            name = request.form["name"]
            location = request.form["location"]
            address = request.form["address"]
            _code = str(code)
            _datetime = dtnow()
            _activity = "Added store " + _code
            _username = str(username)
            addstoredict = {"User": _username, "Activity": _activity, "Time": _datetime}
            cur = ksql.cursor()
            cur.execute("SELECT StoreCode FROM Store WHERE StoreCode = %s",(code,))
            exist = cur.fetchall()
            if not exist:
                cur.execute("INSERT INTO Store (StoreCode, StoreName, Location, Address) VALUES (%s, %s, %s, %s)",(code, name, location, address))
                ksql.commit()
                flash("Store added!")
                jsonproducer.send("storemanagementtopic", addstoredict)
                return redirect(url_for("storemenu"))
            else:
                flash("Duplicate data! Please enter another store code.")
                return redirect(url_for("storeadd"))
        return render_template("storeadd.html", form=form)
    else:
        return redirect(url_for("login"))

# Store Delete
@app.route("/storedelete/", methods=["GET", "POST"])
def storedelete():
    if "username" in session:
        username = session["username"]
        code = request.form.get("code")
        _code = str(code)
        _datetime = dtnow()
        _activity = "Deleted store " + _code
        _username = str(username)
        deletestoredict = {"User": _username, "Activity": _activity, "Time": _datetime}
        cur = ksql.cursor()
        cur.execute("SELECT StoreCode FROM Store")
        exist = cur.fetchall()
        if request.method == "POST":
            cur.execute("DELETE FROM Store WHERE StoreCode = %s",(code,))
            ksql.commit()
            flash("Store deleted!")
            jsonproducer.send("storemanagementtopic", deletestoredict)
            return redirect(url_for("storemenu"))

        return render_template("storedelete.html", exist = exist)
    else:
        return redirect(url_for("login"))

# Store View
@app.route("/storeview/", methods=["GET", "POST"])
def storeview():
    if "username" in session:
        username = session["username"]
        headings = ("StoreCode", "Store Name","Store Location" , "Store Address")
        cur = ksql.cursor(buffered=True)
        cur.execute("SELECT * FROM Store LIMIT 1")
        exist = cur.fetchall()
        if not exist:
            flash("No stores saved!")
            return render_template("storeview.html")
        else:
            cur.execute("SELECT StoreCode, StoreName, Location, Address FROM Store")
            data = cur.fetchall()
            return render_template("storeview.html", headings=headings, data=data)
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))

# Store Update
@app.route("/storeupdate/",  methods=["GET", "POST"])
def storeupdate():
    if "username" in session:
        username = session["username"]
        code = request.form.get("code")
        name = request.form.get("name")
        location = request.form.get("location")
        address = request.form.get("address")
        _code = str(code)
        _datetime = dtnow()
        _activity = "Updated store " + _code
        _username = str(username)
        updatestoredict = {"User": _username, "Activity": _activity, "Time": _datetime}
        form = StoreUpdateForm()

        cur = ksql.cursor()
        cur.execute("SELECT StoreCode FROM Store")
        exist = cur.fetchall()
        if request.method == "POST":
            cur.execute(
                "UPDATE Store SET StoreName = %s, Location = %s, Address = %s WHERE StoreCode = %s",
                (name, location, address, code))
            ksql.commit()
            flash("Store updated!")
            jsonproducer.send("storemanagementtopic", updatestoredict)
            return redirect(url_for("storemenu"))
        return render_template("storeupdate.html", form=form, exist = exist)
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))



