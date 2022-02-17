from flask import Flask, redirect, url_for, render_template, request, session, flash, json
from webforms import StaffAddForm
from application import app
from application import mydb as ksql

#kafka stuff
#=======================================
from kafka import KafkaProducer
from datetime import datetime

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

# Staff Home
@app.route("/staffhome/")
def staffhome():
    if "username" in session:
        username = session["username"]
        return render_template("staffhome.html", username=username)
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))


# Staff Menu
@app.route("/staffmenu/")
def staffmenu():
    if "username" in session:
        username = session["username"]
        return render_template("staffmenu.html", username=username)
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))


# ===========================
# Staff Add
@app.route("/staffadd/", methods=["GET", "POST"])
def staffadd():
    if "username" in session:
        usernameses = session["username"]
        form = StaffAddForm()
        if form.validate_on_submit():
            name = request.form["name"]
            username = request.form["username"]
            password = request.form["password"]
            phone = request.form["phone"]
            email = request.form["email"]
            address = request.form["address"]
            _username = str(username)
            _datetime = dtnow()
            _activity = "Added user "+ _username
            _usernameses = str(usernameses)
            useradddict = {"User": _usernameses, "Activity": _activity, "Time": _datetime}
            type = "Staff"
            cur = ksql.cursor()
            cur.execute("SELECT Username FROM User WHERE Username = %s", (username,))
            exist = cur.fetchall()
            if not exist:
                cur.execute("INSERT INTO User (FullName, Username, UserPW, UserPhone, UserAddress, UserEmail, UserType) VALUES (%s, %s, %s, %s, %s, %s, %s)", (name, username, password, phone, address, email, type))
                ksql.commit()
                flash("Staff account created!")
                jsonproducer.send("usermanagementtopic", useradddict)
                return redirect(url_for("staffmenu"))
            else:
                flash("Username exists! Please enter another username.")
                return redirect(url_for("staffadd"))
        return render_template("staffadd.html", form=form, ID=usernameses)
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))

# Store Delete
@app.route("/staffdelete/", methods=["GET", "POST"])
def staffdelete():
    if "username" in session:
        usernameses = session["username"]

        username = request.form.get("username")
        _username = str(username)
        _datetime = dtnow()
        _activity = "Deleted user " + _username
        _usernameses = str(usernameses)
        userdeletedict = {"User": _usernameses, "Activity": _activity, "Time": _datetime}
        cur = ksql.cursor()
        cur.execute("SELECT Username FROM User WHERE UserType = 'Staff'")
        exist = cur.fetchall()
        if exist:
            if request.method == "POST":
                cur.execute("DELETE FROM User WHERE Username = %s",(username,))
                ksql.commit()
                flash("Staff account deleted!")
                jsonproducer.send("usermanagementtopic", userdeletedict)
                return redirect(url_for("staffmenu"))
            return render_template("staffdelete.html", exist=exist, ID=usernameses)
        else:
            flash("No Staff account to delete!")
            return redirect(url_for("staffmenu"))
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))


# Staff View
@app.route("/staffview/", methods=["GET", "POST"])
def staffview():
    if "username" in session:
        username = session["username"]
        headings = ("Username", "FullName", "Password", "Phone Number", "Home Address", "Email Address")
        cur = ksql.cursor(buffered=True)
        cur.execute("SELECT * FROM User LIMIT 1")
        exist = cur.fetchall()
        if not exist:
            flash("No staff accounts!")
            return render_template("staffview.html")
        else:
            cur.execute("SELECT Username, FullName, UserPW, UserPhone, UserAddress, UserEmail FROM User WHERE UserType = 'Staff'")
            data = cur.fetchall()
            flash("List of Staff details")
            return render_template("staffview.html", headings=headings, data=data, ID=username)
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))


# Staff Update
@app.route("/staffupdate/",  methods=["GET", "POST"])
def staffupdate():
    if "username" in session:
        usernameses = session["username"]
        form = StaffAddForm()
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        phone = request.form.get("phone")
        email = request.form.get("email")
        address = request.form.get("address")
        _username = str(username)
        _datetime = dtnow()
        _activity = "Updated user " + _username
        _usernameses = str(usernameses)
        userupdatedict = {"User": _usernameses, "Activity": _activity, "Time": _datetime}
        cur = ksql.cursor()
        cur.execute("SELECT Username FROM User WHERE UserType = 'Staff'")
        exist = cur.fetchall()
        if request.method == "POST":
            cur.execute("UPDATE User SET FullName = %s, UserPW = %s, UserPhone = %s, UserAddress = %s, UserEmail = %s WHERE Username = %s", (name, password, phone, address, email, username))
            ksql.commit()
            flash("Staff account updated!")
            jsonproducer.send("usermanagementtopic", userupdatedict)
            return redirect(url_for("staffmenu"))
        return render_template("staffupdate.html", exist=exist, ID=usernameses, form=form)
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))

# ===========================
# View Staff Profile
@app.route("/staffprofile/", methods=["GET", "POST"])
def staffprofile():
    if "username" in session:
        username = session["username"]
        usertype = session["usertype"]
        cur = ksql.cursor(buffered=True)
        cur.execute("SELECT Username, FullName, UserPW, UserPhone, UserAddress, UserEmail FROM User WHERE Username = %s and UserType = %s", (username, usertype))
        userfound = cur.fetchone()
        ksql.commit()
        return render_template("staffprofile.html", userfound=userfound, ID=username)
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))
