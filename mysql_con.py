import mysql.connector
global_connection = None

def handle_login(hostname,username , passw , port=3306):
    try : 
        connection = mysql.connector.connect(host=hostname , user=username , password=passw , port=port)
        if isinstance(connection , mysql.connector.connection.MySQLConnection) :
            globals()["global_connection"]= connection
            print("succesful connection")
            return True

        else :
            return False
    except mysql.connector.Error as err:
        print(err)
        return False


