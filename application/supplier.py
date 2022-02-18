from datetime import datetime

from flask import redirect, url_for, render_template, request, session, flash, json
# kafka stuff
# =======================================
from kafka import KafkaProducer

from application import app
from application import mydb as ksql
from webforms import SupplierAddForm


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

# Supplier Home
@app.route("/supplierhome/")
def supplierhome():
    if "username" in session:
        supplierID = session["username"]
        return render_template("supplierhome.html", user=supplierID)
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))

# Supplier Menu
@app.route("/suppliermenu/")
def suppliermenu():
    if "username" in session:
        username = session["username"]
        return render_template("suppliermenu.html")
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))

# Supplier Add
@app.route("/supplieradd/", methods=["GET", "POST"])
def supplieradd():
    if "username" in session:
        username = session["username"]
        form = SupplierAddForm()
        if form.validate_on_submit():
            code = request.form["code"]
            name = request.form["name"]
            password = request.form["password"]
            phone = request.form["phone"]
            address = request.form["address"]
            _code = str(code)
            _datetime = dtnow()
            _activity = "Added supplier "+_code
            _username = str(username)
            addsupplierdict = {"User": _username, "Activity": _activity, "Time": _datetime}
            cur = ksql.cursor()
            cur.execute("SELECT SupplierCode FROM Supplier WHERE SupplierCode = %s", (code,))
            exist = cur.fetchall()
            if not exist:
                cur.execute("INSERT INTO Supplier (SupplierCode, SupplierName, SupplierPhone, SupplierAddress, SupplierPassword) VALUES (%s, %s, %s, %s, %s)", (code,name, phone, address, password))
                ksql.commit()
                flash("Supplier added!")
                jsonproducer.send("suppliermanagementtopic", addsupplierdict)
                return redirect(url_for("suppliermenu"))
            else:
                flash("Duplicate data! Please enter another supplier code.")
                return redirect(url_for("supplieradd"))
        return render_template("supplieradd.html", form = form)
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))


# Supplier Delete
@app.route("/supplierdelete/", methods=["GET", "POST"])
def supplierdelete():
    if "username" in session:
        username = session["username"]
        code = request.form.get("code")
        _code = str(code)
        _datetime = dtnow()
        _activity = "Deleted supplier " + _code
        _username = str(username)
        deletesupplierdict = {"User": _username, "Activity": _activity, "Time": _datetime}
        cur = ksql.cursor()
        cur.execute("SELECT SupplierCode FROM Supplier")
        exist = cur.fetchall()
        # form = SupplierDeleteForm()
        if exist:
            if request.method == "POST":
                cur.execute("DELETE FROM Supplier WHERE SupplierCode = %s", (code,))
                ksql.commit()
                flash("Supplier deleted!")
                jsonproducer.send("suppliermanagementtopic", deletesupplierdict)
                return redirect(url_for("suppliermenu"))
            return render_template("supplierdelete.html", exist=exist)
        else:
            flash("No supplier record to delete!")
            return redirect(url_for("suppliermenu"))
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))

# Supplier View
@app.route("/supplierview/", methods=["GET", "POST"])
def supplierview():
    if "username" in session:
        username = session["username"]

        headings = ("Supplier Code", "Supplier Name", "Supplier Password", "Supplier Phone", "Supplier Address")
        cur = ksql.cursor(buffered=True)
        cur.execute("SELECT * FROM Supplier LIMIT 1")
        exist = cur.fetchall()
        if not exist:
            flash("No suppliers saved!")
            return render_template("supplierview.html")
        else:
            cur.execute(
                "SELECT SupplierCode, SupplierName, SupplierPassword, SupplierPhone, SupplierAddress FROM Supplier")
            data = cur.fetchall()
            return render_template("supplierview.html", headings=headings, data=data)
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))

# Supplier Update
@app.route("/supplierupdate/",  methods=["GET", "POST"])
def supplierupdate():
    if "username" in session:
        form = SupplierAddForm()
        username = session["username"]
        code = request.form.get("code")
        name = request.form.get("name")
        password = request.form.get("password")
        phone = request.form.get("phone")
        address = request.form.get("address")
        _code = str(code)
        _datetime = dtnow()
        _activity = "Updated supplier " + _code
        _username = str(username)
        updatesupplierdict = {"User": _username, "Activity": _activity, "Time": _datetime}
        cur = ksql.cursor()
        cur.execute("SELECT SupplierCode FROM Supplier")
        exist = cur.fetchall()
        if exist:
            if request.method == "POST":
                cur.execute("UPDATE Supplier SET SupplierName = %s, SupplierPhone = %s, SupplierAddress = %s, SupplierPassword = %s WHERE SupplierCode = %s", (name, phone, address, password, code))
                ksql.commit()
                flash("Supplier updated!")
                jsonproducer.send("suppliermanagementtopic", updatesupplierdict)
                return redirect(url_for("suppliermenu"))
            return render_template("supplierupdate.html", exist=exist, form = form)
        else:
            flash("No supplier record to update!")
            return redirect(url_for("suppliermenu"))
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))

# Supplier Profile
@app.route("/supplierprofile/")
def supplierprofile():
    if "username" in session:
        supplierID = session["username"]
        cur = ksql.cursor()
        cur.execute(
            "SELECT * FROM Supplier WHERE SupplierCode = %s"
            , (supplierID,))
        found_user = cur.fetchone()
        cur.close()
        return render_template("supplierprofile.html", user=found_user)
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))