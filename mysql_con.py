import mysql.connector
global_connection = None

def handle_login(hostname,username , passw):
    try : 
        connection = mysql.connector.connect(host=hostname , user=username , password=passw)
        if isinstance(connection , mysql.connector.connection.MySQLConnection) :
            globals()["global_connection"]= connection
            return "succesful"
        else :
            ...
            # implement the error handling
    except mysql.connector.Error as err:
        return ""


