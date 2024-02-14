import mysql.connector
global_connection = None
hostname = None
username = None
passowrd = None
port = None
db = None

def handle_login(hostname,username , passw , port=3306,db=""):
    try : 
        connection = mysql.connector.connect(host=hostname , user=username , password=passw , port=port ,database=db)
        if isinstance(connection , mysql.connector.connection.MySQLConnection) :
            globals()["global_connection"]= connection
            globals()["hostname"] = hostname
            globals()["username"]= username
            globals()["passowrd"]= passw
            globals()["port" ]= port
            globals()["db"] = db   
            print("succesful connection")
            return True
        else :
            return False
    except mysql.connector.Error as err:
        print(err)
        return False


def show_databases():
    try :
        con_cursor = global_connection.cursor() 
        con_cursor.execute("SHOW DATABASES")
        databases = con_cursor.fetchall()
        con_cursor.reset()
        return databases
    except Exception as err :
        print(err)

def create_database(my_db):
    try :
        con_cursor = global_connection.cursor() 
        con_cursor.execute(f"CREATE DATABASE {my_db}")
        return True
    except Exception as err :
        print(err)
        return False
    
def show_tables(db_name):
    try :
        con_cursor = global_connection.cursor() 
        con_cursor.execute(f"SHOW TABLES FROM {db_name}")
        tables = con_cursor.fetchall()
        con_cursor.reset()
        return tables
    except Exception as err:
        print(err)
