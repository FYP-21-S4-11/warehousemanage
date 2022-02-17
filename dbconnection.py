import mysql.connector
import os

#db_user = os.environ["DB_USER"]
#db_pass = os.environ["DB_PASS"]
#db_name = os.environ["DB_NAME"]
#db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
#instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]

class dbcon:

    mydb = mysql.connector.connect(
        host="34.125.123.226",
        username="user",
        password="root",
        port="3306",
        db="fypdatabase",
        auth_plugin="mysql_native_password",
        autocommit=True, 
        query={
        "unix_socket": "{}/{}".format("/cloudsql","numeric-asset-341503:us-west4:fypdatabase")  # i.e "<PROJECT-NAME>:<INSTANCE-REGION>:<INSTANCE-NAME>"
        }
    )
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