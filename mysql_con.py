import mysql.connector
import pandas


global_connection = None
hostname = None
username = None
passowrd = None
port = None
db = None

def handle_login(hostname,username , passw , port=3306,db=None):
    try : 
        connection = mysql.connector.connect(host=hostname , user=username , password=passw , port=port ,database=db, auth_plugin='mysql_native_password')
        if isinstance(connection , mysql.connector.connection.MySQLConnection) :
            globals()["global_connection"]= connection
            globals()["hostname"] = hostname
            globals()["username"]= username
            globals()["passowrd"]= passw
            globals()["port" ]= port
            globals()["db"] = db   
            return True
        else :
            return False
    except mysql.connector.Error as err:
        return err


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

def drop_db(db_name):
    try :
        con_cursor = global_connection.cursor()
        con_cursor.execute(f"DROP DATABASE {db_name}")
        return True
    except Exception as err:
        print(err)


def show_table_records(table):
    try :
        con_cursor = global_connection.cursor()
        con_cursor.execute(f"SELECT * FROM {table}")
        rows = con_cursor.fetchall()
        columns = [i[0] for i in con_cursor.description]
        return columns,rows,get_prim_key(con_cursor,table)
    except Exception as err:
        print(err)
        return None

def get_prim_key(con_cursor,table):
    try :
        con_cursor.execute(f"SHOW KEYS FROM {table} WHERE Key_name = 'PRIMARY';")
        rows = con_cursor.fetchall()
        if len(rows) == 1 :
            return rows[0][4] 
        elif len(rows) > 1 :
            ... #it's a composite key 

    except Exception as err:
        print(err)
        return None


def alter_table(table, values , columns,primary_key, primary_key_old_value):
    try :
        values = [f"'{i}'" if isinstance(i, str) else i if i is not None else 'NULL' for i in values]
        con_cursor = global_connection.cursor()


        set_clause = ', '.join([f"{column} = {value}" for column, value in zip(columns, values)])

        query_update = f"UPDATE {table} SET {set_clause} WHERE {primary_key} = {primary_key_old_value};" 
        print(query_update)  
        con_cursor.execute(query_update)

        global_connection.commit()

    except Exception as err:
        print(err)

# think about migration (sqlalchemy )