from datetime import datetime

from flask import redirect, url_for, render_template, request, session, flash, json
from kafka import KafkaConsumer
# kafka stuff
# =======================================
from kafka import KafkaProducer

from application import app
from webforms import TopicForm, ReportSelectForm
from application import init_connection_engine

ksql = init_connection_engine()

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

# ===========================
# Admin Home
@app.route("/adminhome/")
def adminhome():
    if "username" in session:
        username = session["username"]
        return render_template("adminhome.html", username=username)
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))

# ===========================
# View Admin Profile
@app.route("/adminprofile/", methods=["GET", "POST"])
def adminprofile():
    if "username" in session:
        username = session["username"]
        usertype = session["usertype"]
        cur = ksql.cursor(buffered=True)
        cur.execute("SELECT Username, FullName, UserPW, UserPhone, UserAddress, UserEmail FROM User WHERE Username = %s and UserType = %s", (username, usertype))
        userfound = cur.fetchone()
        ksql.commit()
        return render_template("adminprofile.html", userfound=userfound)
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))

# topic select
@app.route('/topicselect', methods=['GET', 'POST'])
def topicselect():
    if "username" in session:
        username = session["username"]
        usertype = session["usertype"]

        # list topics and show server status
        consumermain = KafkaConsumer(bootstrap_servers=['localhost:9092'])
        topics = consumermain.topics()
        topic = list(topics)
        if not topics:
            server_status = "server not running"
        else:
            server_status = "Server running"

        form = TopicForm()
        if request.method == "POST":


            return redirect(url_for('topicselect'))
        return render_template("topicselect.html", server_status=server_status, len=len(topic), topic=topic)
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))

# topic select
@app.route('/topicselected', methods=['GET', 'POST'])
def topicselected():
    if "username" in session:
        username = session["username"]
        usertype = session["usertype"]
        if request.method == 'POST':
            topic = request.form.get('topic')
            cur1 = ksql.cursor()
            consumer = KafkaConsumer(topic, bootstrap_servers=["localhost:9092"],
                                     auto_offset_reset="earliest", enable_auto_commit=True,
                                     consumer_timeout_ms=1000,
                                     value_deserializer=lambda m: json.loads(m.decode("utf-8"))
                                     )
            for i in consumer:
                message = i.value
                _message = str(message)
                if "Quantity" in message:
                    msgdct = {"User": message["User"], "Activity": message["Activity"], "Time": message["Time"],
                              "Quantity": message["Quantity"], "Product": message["Product"] , "Remark":message["Remark"] }
                    print("test1: " + _message)
                    cur1.execute("INSERT IGNORE INTO KafkaLog (User, Activity, DateTime, StockName, TopicName, Quantity, Remark) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                                (msgdct["User"], msgdct["Activity"], msgdct["Time"], msgdct["Product"], topic, msgdct["Quantity"], msgdct["Remark"],))
                    ksql.commit()
                else:
                    msgdct = {"User": message["User"], "Activity": message["Activity"], "Time": message["Time"]}
                    print("test2: " + _message)
                    cur1.execute("INSERT IGNORE INTO KafkaLog (User, Activity, DateTime, TopicName) VALUES(%s,%s,%s,%s)",
                                (msgdct["User"], msgdct["Activity"], msgdct["Time"], topic,))
                    ksql.commit()
                    # for the headers in the table

            heading1 = ("User", "Date", "Activity", "Quantity", "Product", "Remark")
            heading = ("User", "Date", "Activity")

            cur = ksql.cursor(buffered=True)
            cur.execute("SELECT quantity FROM KafkaLog WHERE TopicName = %s", (topic,))
            exist = cur.fetchone()
            if "None" in str(exist):
                print(exist)
                cur.execute("SELECT User, DateTime, Activity FROM KafkaLog WHERE TopicName = %s", (topic,))
                record = cur.fetchall()
                return render_template("topicselected.html", record=record, heading=heading)
            else:
                print(exist)
                cur.execute("SELECT User, DateTime, Activity, Quantity, StockName, Remark FROM KafkaLog WHERE TopicName = %s", (topic,))
                record = cur.fetchall()
                return render_template("topicselected.html", record=record, heading=heading1)

        return render_template('topicselected.html')
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))

#notificaion
@app.route('/notification', methods=['GET', 'POST'])
def notification():
    if "username" in session:
        username = session["username"]
        usertype = session["usertype"]

        topic = "notificationtopic"
        cur1 = ksql.cursor()
        consumer = KafkaConsumer(topic, bootstrap_servers=["localhost:9092"],
                                 auto_offset_reset="earliest", enable_auto_commit=True,
                                 consumer_timeout_ms=1000,
                                 value_deserializer=lambda m: json.loads(m.decode("utf-8"))
                                 )
        for i in consumer:
            message = i.value
            _message = str(message)

            msgdct = {"User": message["User"], "Activity": message["Activity"], "Time": message["Time"]}
            print("test2: " + _message)
            cur1.execute("INSERT IGNORE INTO KafkaLog (User, Activity, DateTime, TopicName) VALUES(%s,%s,%s,%s)",
                        (msgdct["User"], msgdct["Activity"], msgdct["Time"], topic,))
            ksql.commit()
            # for the headers in the table

        heading = ("Date", "Activity")

        cur = ksql.cursor(buffered=True)
        cur.execute("SELECT quantity FROM KafkaLog WHERE TopicName = %s ", (topic,))
        exist = cur.fetchone()
        if "None" in str(exist):
            print(exist)
            cur.execute("SELECT DateTime, Activity FROM KafkaLog WHERE TopicName = %s ORDER BY DateTime DESC", (topic,))
            record = cur.fetchall()
            return render_template("notification.html", record=record, heading=heading)

        return render_template('notification.html')

    else:
        flash("Please login again!")
        return redirect(url_for("logout"))

#report
@app.route("/reportselect/")
def reportselect():
    if "username" in session:
        username = session["username"]
        usertype = session["usertype"]
        form = ReportSelectForm()

        topic = "stocktopic"
        cur = ksql.cursor(buffered=True)
        cur.execute("SELECT DISTINCT StockName FROM KafkaLog WHERE TopicName =%s", (topic,))
        stockexist = cur.fetchall()
        cur.close()

        topic = "stocktopic"
        cur1 = ksql.cursor()
        consumer = KafkaConsumer(topic, bootstrap_servers=["localhost:9092"],
                                 auto_offset_reset="earliest", enable_auto_commit=True,
                                 consumer_timeout_ms=1000,
                                 value_deserializer=lambda m: json.loads(m.decode("utf-8"))
                                 )
        for i in consumer:
            message = i.value
            _message = str(message)

            msgdct = {"User": message["User"], "Activity": message["Activity"], "Time": message["Time"],
                      "Quantity": message["Quantity"], "Product": message["Product"], "Remark": message["Remark"]}
            print("test1: " + _message)
            cur1.execute(
                "INSERT IGNORE INTO KafkaLog (User, Activity, DateTime, StockName, TopicName, Quantity, Remark) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                (msgdct["User"], msgdct["Activity"], msgdct["Time"], msgdct["Product"], topic, msgdct["Quantity"],
                 msgdct["Remark"],))
            ksql.commit()
        #====================================================================
        # select all the topic name

        # cur.execute("SELECT QuantityCurrent FROM Inventory")

        if request.method == "POST":
            # name = request.form.get("name")
            return redirect(url_for('reportselect'))
        return render_template("reportselect.html", stockexist=stockexist, form=form)
    else:
        flash("Please login again!")
        return redirect(url_for("logout"))

@app.route('/viewreport', methods=['GET', 'POST'])
def viewreport():
    if "username" in session:
        username = session["username"]
        usertype = session["usertype"]
        #=============================================================

        sku = request.form.get('sku')
        start = request.form.get('start')
        end = request.form.get('end')
        if start < end :
            statementin = "SELECT Quantity, DateTime from KafkaLog WHERE TopicName = 'stocktopic' AND DateTime BETWEEN %s AND %s AND Activity LIKE '%Stock In%' AND StockName = %s"
            statementout = "SELECT Quantity, DateTime from KafkaLog WHERE TopicName = 'stocktopic' AND DateTime BETWEEN %s AND %s AND Activity LIKE '%Stock Out%' AND StockName = %s"
            statementdamage = "SELECT Quantity, DateTime from KafkaLog WHERE TopicName = 'stocktopic' AND DateTime BETWEEN %s AND %s AND Activity LIKE '%Stock Damaged%' AND StockName = %s"

            overallin = "SELECT SUM(quantity) qs from KafkaLog WHERE TopicName = 'stocktopic' AND DateTime BETWEEN %s AND %s AND Activity LIKE '%Stock In%' AND StockName = %s"
            overallout = "SELECT SUM(quantity) qs from KafkaLog WHERE TopicName = 'stocktopic' AND DateTime BETWEEN %s AND %s AND Activity LIKE '%Stock Out%' AND StockName = %s"
            overalldamage = "SELECT SUM(quantity) qs from KafkaLog WHERE TopicName = 'stocktopic' AND DateTime BETWEEN %s AND %s AND Activity LIKE '%Stock Damaged%' AND StockName = %s"

            outstatement = "SELECT SUM(a.Quantity) aq, SUM(b.Quantity) bq, SUM(c.Quantity) cq FROM KafkaLogs"

            statementoverallnodate = ""
            cur = ksql.cursor(buffered=True)
            cur.execute(statementin, (start, end, sku,))
            stockin = cur.fetchall()
            cur.close()
            #stock out
            cur = ksql.cursor(buffered=True)
            cur.execute(statementout, (start, end, sku,))
            stockout = cur.fetchall()
            cur.close()
            #stock Damage
            cur = ksql.cursor(buffered=True)
            cur.execute(statementdamage, (start, end, sku,))
            stockdamage = cur.fetchall()
            cur.close()
            #sum in
            cur = ksql.cursor(buffered=True)
            cur.execute(overallin, (start, end, sku,))
            ttlin = cur.fetchall()
            cur.close()
            # sum out
            cur = ksql.cursor(buffered=True)
            cur.execute(overallout, (start, end, sku,))
            ttlout = cur.fetchall()
            cur.close()
            # sum damage
            cur = ksql.cursor(buffered=True)
            cur.execute(overalldamage, (start, end, sku,))
            ttldamage = cur.fetchall()
            cur.close()

            heading = ("Quantity", "Date")


            return render_template("reportgenerated.html", heading=heading, invenin=stockin, invenout=stockout, stockdamage=stockdamage , sku=sku, ttlin = ttlin, ttlout = ttlout, ttldamage = ttldamage)
        else:
            flash("Start Date can not be later than end date!")
            return redirect(url_for('reportselect'))

    else:
        flash("Please login again!")
        return redirect(url_for("logout"))