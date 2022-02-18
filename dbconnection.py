import mysql.connector
class dbcon:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="kafka123@",
        port="3306",
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