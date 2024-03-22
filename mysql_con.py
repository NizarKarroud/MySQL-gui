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
        
        # to get where the primary key of a table is a foreign key ( the table name , and column name) so that i can implement some sort of UPDATE ON CASCADE
        ref_clause = ", ".join([f"'{column[0]}'" for column in key_val_couple])
        con_cursor.execute(f"SELECT TABLE_NAME, COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA = '{db_name}' AND REFERENCED_COLUMN_NAME IN ({ref_clause});")
        foreign_relations = con_cursor.fetchall()

        # to get the foreign keys in a table (the one to whom the record belongs) 
        con_cursor.execute(f"SELECT COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA = '{db_name}' AND TABLE_NAME = '{table}';") 
        foreign_keys_list = con_cursor.fetchall()

        tables_to_check = {}
        # to get the the tables and the columns where the foreign keys are primary
        for foreign_key in foreign_keys_list :
            con_cursor.execute(f"SELECT REFERENCED_TABLE_NAME , REFERENCED_COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA = '{db_name}' AND REFERENCED_COLUMN_NAME IN ('{foreign_key[0]}');")
            tab_col_couple = con_cursor.fetchall()
            tables_to_check[tab_col_couple[0][0]] = tab_col_couple[0][1]

        
        if tables_to_check :
        #check if the updated value of the the foreign keys exist in the records of their tables
            for foreign_table , column in tables_to_check.items():
                value = dict(zip(columns, values))[column]
                con_cursor.execute(f"SELECT COUNT(*) FROM {foreign_table} WHERE {column} = {value};")
                result = con_cursor.fetchall()[0]
                print(result)
                if result[0] > 0  :
                    set_clause = ', '.join([f"{column} = {value}" for column, value in zip(columns, values)])

                    where_clause = ' AND '.join([f"{key} = '{value}'" for key,value in key_val_couple])

                    query_update = f"UPDATE {table} SET {set_clause} WHERE {where_clause};"
                    print(query_update) 
                    con_cursor.execute(query_update)

                    set_clause_keys = {key : value for key , value in zip(columns , values) if any(key == key_couple[0] for key_couple in key_val_couple)}
                    ref_set_clause = ','.join([f"{column} = {value}" for column , value in set_clause_keys.items()])
                    for relation in foreign_relations :
                        print(f"UPDATE {relation[0]} SET {ref_set_clause} WHERE {where_clause};")
                        con_cursor.execute(f"UPDATE {relation[0]} SET {ref_set_clause} WHERE {where_clause};")

                    con_cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

                    global_connection.commit()
        else : 
            set_clause = ', '.join([f"{column} = {value}" for column, value in zip(columns, values)])

            where_clause = ' AND '.join([f"{key} = '{value}'" for key,value in key_val_couple])

            query_update = f"UPDATE {table} SET {set_clause} WHERE {where_clause};"
            print(query_update) 
            con_cursor.execute(query_update)


            set_clause_keys = {key : value for key , value in zip(columns , values) if any(key == key_couple[0] for key_couple in key_val_couple)}
            ref_set_clause = ','.join([f"{column} = {value}" for column , value in set_clause_keys.items()])
            for relation in foreign_relations :
                print(f"UPDATE {relation[0]} SET {ref_set_clause} WHERE {where_clause};")
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