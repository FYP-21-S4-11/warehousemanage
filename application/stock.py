from datetime import datetime

from flask import redirect, url_for, render_template, request, session, flash, json
# kafka stuff
# =======================================
from kafka import KafkaProducer

from application import app
from application import mydb as ksql
from webforms import QuantityForRemove


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

@app.route("/stockmenu/")
def stockmenu():
    if "username" in session:
        username = session["username"]
        return render_template("stockmenu.html")
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))

# view stocks in the warehosue (from warehouse side)
@app.route("/viewstock/", methods=["GET", "POST"])
def viewstock():
    if "username" in session:
        username = session["username"]
        headings = ("ProductSKU", "Supplier Code", "Quantity (In Warehouse)")
        cur = ksql.cursor(buffered=True)
        cur.execute("SELECT ProductSKU, SupplierCode, CurrentQuantity FROM Stock")
        data = cur.fetchall()
        if not data:
            flash("No stocks in the warehouse!")
            return render_template("viewstock.html")
        elif data:
            flash("Stocks in the warehouse!")
            return render_template("viewstock.html", headings=headings, data=data)
        else:
            flash("Error occured!")
            return render_template("viewstock.html")
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))

# =====================
# Supplier Side
# sending stocks from supplier to warehouse
@app.route("/sendstocks/", methods=["POST", "GET"])
def sendstocks():
    if "username" in session:
        form = QuantityForRemove()
        supplierCode = session["username"]
        cur = ksql.cursor()
        cur.execute("SELECT ProductSKU FROM Product WHERE SupplierCode = %s", (supplierCode,))
        skuexist = cur.fetchall()
        cur.close()
        quantity = request.form.get('quantity')

        if request.method == "POST":

            # ProductSKU
            sku = request.form.get("sku")
            # generate stock sku
            stocksku = supplierCode + ":" + sku

            _sku = str(sku)
            _datetime = dtnow()
            _activity = "Stock In"
            _username = str(supplierCode)
            _remark = _sku
            _quantity = str(quantity)
            stockindict = {"User": _username, "Activity": _activity, "Time": _datetime, "Quantity": _quantity,
                           "Product": _sku, "Remark": _remark}


            # check if stock sku
            cur = ksql.cursor()
            cur.execute("SELECT StockSKU FROM Stock WHERE StockSKU = %s", (stocksku,))
            exist = cur.fetchall()
            cur.close()
            d = (0,)
            if int(quantity) <= int(d[0]):
                flash("No negative number!")
                return render_template("sendstocks.html", ID=supplierCode, skuexist=skuexist, form= form)
            # check if stock sku exist
            if exist:
                # check quantity from supplier
                cur = ksql.cursor()
                cur.execute("SELECT CurrentQuantity FROM Stock WHERE StockSKU = %s", (stocksku,))
                dataout = cur.fetchone()

                cur.close()
                if None in dataout:
                    result = quantity
                    cur = ksql.cursor()
                    cur.execute(
                        "Update Stock SET CurrentQuantity = %s WHERE StockSKU = %s",
                        (result, stocksku))
                    ksql.commit()
                    cur.close()
                    flash("Successfully sent stocks to warehouse!")
                    jsonproducer.send("stocktopic", stockindict)
                    return redirect(url_for("supplierhome"))
                else:
                    result = int(dataout[0]) + int(quantity)
                    cur = ksql.cursor()
                    cur.execute(
                        "Update Stock SET CurrentQuantity = %s WHERE StockSKU = %s",
                        (result, stocksku))
                    ksql.commit()
                    cur.close()
                    flash("Successfully sent stocks to warehouse!")
                    jsonproducer.send("stocktopic", stockindict)
                    return redirect(url_for("supplierhome"))
            elif not quantity or not quantity.isnumeric() or int(quantity) <= 0:
                flash("Please enter a valid quantity.")
                return render_template("sendstocks.html", ID=supplierCode, skuexist=skuexist, form= form)
            elif not exist:
                # insert stock sku
                cur = ksql.cursor()
                cur.execute(
                    "INSERT INTO Stock (StockSKU, ProductSKU, SupplierCode, CurrentQuantity) VALUES (%s, %s, %s, %s)",
                    (stocksku, sku, supplierCode, quantity))
                ksql.commit()
                cur.close()
                flash("Successfully sent stocks to warehouse!")
                jsonproducer.send("stocktopic", stockindict)
                return redirect(url_for("supplierhome"))
            else:
                flash("Error Occured!")
                return render_template("sendstocks.html", ID=supplierCode, skuexist=skuexist, form= form)
        return render_template("sendstocks.html", ID=supplierCode, skuexist=skuexist, form= form)
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))

# view stocks inside the warehouse
@app.route("/supplyviewstock/")
def supplyviewstock():
    if "username" in session:

        supplierID = session["username"]

        cur = ksql.cursor()
        cur.execute("SELECT StockSKU, ProductSKU, CurrentQuantity FROM Stock WHERE SupplierCode = %s", (supplierID,))
        items = cur.fetchall()
        cur.close()
        if not items:
            flash("Empty stocks in the warehouse!")
            return render_template("supplyviewstock.html")
        elif items:
            flash("View our stocks in the warehouse!")
            return render_template("supplyviewstock.html", items=items)
        else:
            flash("Error occurred!")
            return render_template("supplyviewstock.html")
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))

#remove because damaged stock
@app.route("/remove", methods=["GET", "POST"])
def remove():
    if "username" in session:
        form = QuantityForRemove()
        username = session["username"]
        # select all productSKU
        cur = ksql.cursor(buffered=True)
        cur.execute("SELECT ProductSKU FROM Stock")
        prod = cur.fetchall()
        cur.close()

        # product sku
        sku = request.form.get("sku")
        quantity = request.form.get("quantity")

        _sku = str(sku)
        _datetime = dtnow()
        _activity = "Stock Damaged"
        _username = str(username)
        _remark = _sku
        _quantity = str(quantity)
        stockDamageddict = {"User": _username, "Activity": _activity, "Time": _datetime, "Quantity": _quantity,
                       "Product": _sku, "Remark": _remark}
        # if low on stock
        _activitynoti = _sku + "Low On Stock"

        notificationdict = {"User": "Notification", "Activity": _activitynoti, "Time": _datetime}

        if request.method == "POST":
            if prod:
                cur = ksql.cursor()
                cur.execute("SELECT CurrentQuantity FROM Stock WHERE ProductSKU = %s", (sku,))
                data = cur.fetchone()
                cur.close()
                print(data)
                d = (0,)
                if int(quantity) > int(data[0]):
                    flash("Not enough stocks in the warehouse!")
                    return render_template("remove.html", prod=prod, form= form)
                elif int(quantity) <= int(d[0]):
                    flash("No negative number!")
                    return render_template("remove.html", prod=prod, form=form)

                elif int(quantity) == int(data[0]):
                    cur = ksql.cursor()
                    cur.execute("DELETE FROM Stock WHERE ProductSKU = %s", (sku,))
                    ksql.commit()
                    cur.close()
                    flash("No more stocks in the warehouse")
                    jsonproducer.send("notificationtopic", notificationdict)
                    jsonproducer.send("stocktopic", stockDamageddict)
                    redirect(url_for("stockmenu"))
                elif int(quantity) < int(data[0]):
                    result = int(data[0]) - int(quantity)
                    cur = ksql.cursor()
                    cur.execute("UPDATE Stock SET CurrentQuantity = %s WHERE ProductSKU = %s", (result, sku,))
                    ksql.commit()
                    cur.close()
                    if int(result) < 100:
                        jsonproducer.send("notificationtopic", notificationdict)
                    flash("Quantity updated!")
                    jsonproducer.send("stocktopic", stockDamageddict)
                    redirect(url_for("stockmenu"))
                else:
                    flash("Please fill in the necessary fields!")
                    return render_template("remove.html", prod=prod, form= form)
        else:
            return render_template("remove.html", prod=prod, form= form)
        return render_template("remove.html", prod=prod, form= form)
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))

#send to store
@app.route("/sendstore", methods=["GET", "POST"])
def sendstore():
    form = QuantityForRemove()
    if "username" in session:
        username = session["username"]
        # select all productSKU
        cur = ksql.cursor(buffered=True)
        cur.execute("SELECT ProductSKU FROM Stock")
        prod = cur.fetchall()
        cur.close()
        cur = ksql.cursor(buffered=True)
        cur.execute("SELECT StoreCode FROM Store")
        scode = cur.fetchall()
        cur.close()

        # product sku
        sku = request.form.get("sku")
        quantity = request.form.get("quantity")
        code = request.form.get("code")
        _sku = str(sku)
        _code = str(code)
        _datetime = dtnow()
        _activity = "Stock Out to Store "+_code
        _username = str(username)
        _remark = _sku
        _quantity = str(quantity)
        stockDamageddict = {"User": _username, "Activity": _activity, "Time": _datetime, "Quantity": _quantity,
                       "Product": _sku, "Remark": _remark}

        # if low on stock
        _activitynoti = _sku + "Low On Stock"

        notificationdict = {"User": "Notification", "Activity": _activitynoti, "Time": _datetime}

        if request.method == "POST":
            if prod:
                cur = ksql.cursor()
                cur.execute("SELECT CurrentQuantity FROM Stock WHERE ProductSKU = %s", (sku,))
                data = cur.fetchone()
                cur.close()
                d = (0,)

                if int(quantity) > int(data[0]):
                    flash("Not enough stocks in the warehouse!")
                    return render_template("tostore.html", prod=prod, code=scode, form= form)
                elif int(quantity) <= int(d[0]):
                    flash("No negative number!")
                    return render_template("tostore.html", prod=prod, form=form)
                elif int(quantity) == int(data[0]):
                    cur = ksql.cursor()
                    cur.execute("DELETE FROM Stock WHERE ProductSKU = %s", (sku,))
                    ksql.commit()
                    cur.close()
                    flash("No more stocks in the warehouse")
                    jsonproducer.send("stocktopic", stockDamageddict)
                    jsonproducer.send("notificationtopic", notificationdict)
                    return redirect(url_for("stockmenu"))
                elif int(quantity) < int(data[0]):
                    result = int(data[0]) - int(quantity)
                    cur = ksql.cursor()
                    cur.execute("UPDATE Stock SET CurrentQuantity = %s WHERE ProductSKU = %s", (result, sku,))
                    ksql.commit()
                    cur.close()
                    if int(result) < 100:
                        jsonproducer.send("notificationtopic", notificationdict)
                    flash("Quantity updated!")
                    jsonproducer.send("stocktopic", stockDamageddict)
                    return redirect(url_for("stockmenu"))
                else:
                    flash("Please fill in the necessary fields!")
                    return render_template("tostore.html", prod=prod, code=scode, form=form)
        else:
            return render_template("tostore.html", prod=prod, code=scode, form= form)
        return render_template("tostore.html", prod=prod, code=scode, form= form)
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))