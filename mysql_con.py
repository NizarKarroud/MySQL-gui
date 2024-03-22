import mysql.connector
import pandas
import os

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
        return err
    
def show_tables(db_name):
    try :
        con_cursor = global_connection.cursor() 
        con_cursor.execute(f"SHOW TABLES FROM {db_name}")
        tables = con_cursor.fetchall()
        con_cursor.reset()
        return tables
    except Exception as err:
        return err

def drop_db(db_name):
    try :
        con_cursor = global_connection.cursor()
        con_cursor.execute(f"DROP DATABASE {db_name}")
        return True
    except Exception as err:
        return err

def show_table_records(table):
    try :
        con_cursor = global_connection.cursor()
        con_cursor.execute(f"SELECT * FROM {table}")
        rows = con_cursor.fetchall()
        columns = [i[0] for i in con_cursor.description]
        return columns,rows,get_prim_keys(con_cursor,table)
    except Exception as err:
        print(err)
        return None

def get_prim_keys(con_cursor,table):
    try :
        con_cursor.execute(f"SHOW KEYS FROM {table} WHERE Key_name = 'PRIMARY';")
        rows = con_cursor.fetchall()
        
        return [row[4] for i,row in enumerate(rows)]

    except Exception as err:
        print(err)
        return None



def alter_table(db_name , table, values , columns,key_val_couple):
    try :

        values = [f"'{i}'" if  i is not None else 'NULL' for i in values]
        con_cursor = global_connection.cursor()

        con_cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        # to get where the primary key of a table is a foreign key ( the table name , and column name)
        ref_clause = ", ".join([f"'{column[0]}'" for column in key_val_couple])
        con_cursor.execute(f"SELECT TABLE_NAME, COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA = '{db_name}' AND REFERENCED_COLUMN_NAME IN ({ref_clause});")
        foreign_relations = con_cursor.fetchall()

        # to get the foreign keys in a table (the one to whom the record belongs) 
        # SELECT COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA = 'etudiant' AND TABLE_NAME = 'etu'; 
        
        # to get the the table and the column
        con_cursor.execute(f"SELECT REFERENCED_TABLE_NAME , REFERENCED_COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA = '{db_name}' AND REFERENCED_COLUMN_NAME IN ({ref_clause});")
        primary_relations = con_cursor.fetchall()

        


        set_clause = ', '.join([f"{column} = {value}" for column, value in zip(columns, values)])

        where_clause = ' AND '.join([f"{key} = '{value}'" for key,value in key_val_couple])

        query_update = f"UPDATE {table} SET {set_clause} WHERE {where_clause};" 
        con_cursor.execute(query_update)
        print(query_update)

        ref_set_clause = ','.join(set_clause.split(',')[:len(key_val_couple)]) 
        for relation in foreign_relations :
            con_cursor.execute(f"UPDATE {relation[0]} SET {ref_set_clause} WHERE {where_clause};")

        con_cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        global_connection.commit()

    except Exception as err:
        print(err)

# think about migration (sqlalchemy )
        

def exec_query(query) : 
    try :
        con_cursor = global_connection.cursor()
        con_cursor.execute(query)
    # handle diff type of queries ( SELECT IS THE ONLY ONE THAT RETURNS )
    except Exception as err:
        return err


def export_database(db_name , path):
    if os.path.exists(path):
        new_folder_path = os.path.join(path, db_name)
        # Check if the folder already exists within the parent path
        if not os.path.exists(new_folder_path):
            try:
                # Create the folder within the parent path
                os.makedirs(new_folder_path)
            except OSError as e:
                return f"Error creating folder at {new_folder_path}: {e}"
    else:
        return f"Parent path '{path}' does not exist."
    
    #