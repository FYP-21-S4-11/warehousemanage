from datetime import datetime

from flask import redirect, url_for, render_template, request, session, flash, json
# kafka stuff
# =======================================
from kafka import KafkaProducer

from application import app
from application import mydb as ksql
from webforms import ProductAddForm


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

# Product Menu
@app.route("/productmenu/")
def productmenu():
    if "username" in session:
        supplierID = session["username"]
        return render_template("productmenu.html")
    else:
        flash("Please login to view the page.")
        return redirect(url_for("login"))



# Product Add
@app.route("/productadd/", methods=["GET", "POST"])
def productadd():
    if "username" in session:
        username = session["username"]
        form = ProductAddForm()
        if form.validate_on_submit():

            name = request.form["name"]
            type = request.form["type"]
            color = request.form["color"]
            size = request.form["size"]
            # generate product sku
            sku = name + ":" + type + ":" + color + ":" + size + ":" + username

            _sku = str(sku)
            _datetime = dtnow()
            _activity = "Added product "+_sku
            _username = str(username)
            addproductdict = {"User": _username, "Activity": _activity, "Time": _datetime}



            cur = ksql.cursor()
            cur.execute("SELECT ProductSKU FROM Product WHERE ProductSKU = %s AND SupplierCode = %s", (sku, username))
            exist = cur.fetchall()
            if not exist:
                cur.execute("INSERT INTO Product (ProductSKU, SupplierCode, ProductName, Type, Color, Size) VALUES (%s, %s, %s, %s, %s, %s)", (sku, username, name, type, color, size))
                ksql.commit()
                flash("Product added!")
                jsonproducer.send("productmanagementtopic", addproductdict)
                return render_template("productmenu.html", form=form, ID=username)
            else:
                flash("Duplicate data! Please enter another product name.")
                return render_template("productadd.html", form=form, ID=username)
        return render_template("productadd.html", form=form, ID=username)
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))

# Product Delete
@app.route("/productdelete/", methods=["GET", "POST"])
def productdelete():
    if "username" in session:
        username = session["username"]
        sku = request.form.get("sku")
        _sku = str(sku)
        _datetime = dtnow()
        _activity = "Deleted product " + _sku
        _username = str(username)
        deleteproductdict = {"User": _username, "Activity": _activity, "Time": _datetime}
        cur = ksql.cursor()
        cur.execute("SELECT ProductSKU FROM Product WHERE SupplierCode = %s", (username,))
        exist = cur.fetchall()
        if exist:
            if request.method == "POST":
                cur.execute("DELETE FROM Product WHERE ProductSKU = %s", (sku,))
                ksql.commit()
                flash("Product deleted!")
                jsonproducer.send("productmanagementtopic", deleteproductdict)
                return redirect(url_for("productmenu"))
            return render_template("productdelete.html", exist=exist)
        else:
            flash("No product to delete!")
            return redirect(url_for("productmenu"))
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))

# Product View
@app.route("/productview/")
def productview():
    if "username" in session:
        supplierID = session["username"]
        cur = ksql.cursor()
        cur.execute("SELECT ProductSKU, ProductName, Type, Color, Size FROM Product WHERE SupplierCode = %s", (supplierID,))
        items = cur.fetchall()
        cur.close()

        if not items:
            flash("Empty")
            return render_template("productview.html")
        elif items:

            return render_template("productview.html", items=items)
        else:
            flash("Error occurred!")
            return render_template("productview.html")
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))