import mysql.connector
import os
class dbcon:

    db_connectionname = os.environ.get
    mydb = mysql.connector.connect(
        host="34.125.123.226",
        user="root",
        password="root",
        database="fypdatabase",
        auth_plugin="mysql_native_password",
        autocommit=True)
    mycursor = mydb.cursor()

    def checkdbconnet(self):
        if self.mydb:
            print("Connection Successful")
        else:
            print("Connection Unsuccessful")

    def checkstore(self):
        self.mycursor.execute("SELECT StoreCode FROM Store")
        result = self.mycursor.fetchall()
        for res in result:
            print(res)

object = dbcon()
#object.checkdbconnet()
#object.checkstore()