import mysql.connector
import pandas as pd
import os
import shutil
from collections import Counter

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
    # handle diff extension of queries ( SELECT IS THE ONLY ONE THAT RETURNS )
    except Exception as err:
        return err


def export_database(db_name ,table_list, path, extension):
    tables = table_list[:]

    # checking if the folder where the archive is going to be located exists
    if os.path.exists(path):
        new_folder_path = os.path.join(path, db_name)

        # Check if the folder already exists within the parent path
        if not os.path.exists(new_folder_path):
            try:
                # Create the folder within the parent path
                os.makedirs(new_folder_path)
            except OSError as e:
                return f"Error creating folder at {new_folder_path}: {e}"
    
        export_errors = []  # List to store export errors for each table
        for table in tables:
            columns , rows , prim = tuple(show_table_records(table))
            try :
                df = pd.DataFrame(rows , columns=columns)
                table_file_path = os.path.join(new_folder_path, f"{table}.{extension}")
                if extension == 'csv' : 
                    df.to_csv(table_file_path ,index=False)

                else :
                    df.to_html(f"{table_file_path}" , index=False)

            except Exception as err :
                export_errors.append(f"Error exporting {table} to {extension} {err}")
        if export_errors:
            # If there were export errors return the errors
            return export_errors
        
        # Archive the folder
        try:
            shutil.make_archive(new_folder_path, 'zip', new_folder_path)
            # Remove the original folder after archiving
            shutil.rmtree(new_folder_path)
            return f"Exported and archived data successfully at {new_folder_path}.zip"
        
        except Exception as e:
                return f"Error archiving folder at {new_folder_path}: {e}"
    
    else:
        return f"Parent path '{path}' does not exist."

"""
ALTER TABLE current_table_name
RENAME TO new_table_name;
"""
def search_database(cursor ,database, term_to_search ):
    make_db_search_queries = f"""
    SELECT CONCAT(
        'SELECT ''', TABLE_NAME, '.', COLUMN_NAME, ''' AS table_column, ''', COLUMN_NAME, ''' AS value, ''', TABLE_NAME, ''' AS table_name FROM ',
        TABLE_NAME, ' WHERE ', COLUMN_NAME, ' LIKE ''{term_to_search}'''
    )
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = '{database}';
    """
    cursor.execute(make_db_search_queries)

    results = cursor.fetchall() 

    final_result = []
    item_counter = Counter()

    for row in results:
        # Extract the SELECT statement from the row
        select_statement = row[0].rstrip(" \" ") + ";"
        # Execute the SELECT statement
        cursor.execute(select_statement)
        # Fetch and print the results of the SELECT statement
        select_results = cursor.fetchall()

        item_counter.update(select_results)

    return list(item_counter.items())

def search_table(cursor , term_to_search , database , table):
    rows = []
    search_table_query = f"""
        SELECT CONCAT('SELECT * FROM ', table_name, ' WHERE ', column_name, ' LIKE ''{term_to_search}''')
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{database}' AND TABLE_NAME = '{table}';
        """
    cursor.execute(search_table_query)

    results = cursor.fetchall()  
    printed_header = False
    for row in results:
    # Extract the SELECT statement from the row
        select_statement = row[0].rstrip(" \" ") + ";"
        
        # Execute the SELECT statement
        cursor.execute(select_statement)

        # Fetch and print the results of the SELECT statement
        select_results = cursor.fetchall()
        
        # Print headers only once
        if not printed_header:
            headers = [i[0] for i in cursor.description]
            header = headers
            printed_header = True

        for result in select_results:
            if result:
                rows.append(result)

    return(header , rows)
    cursor.close()    