import mysql.connector
import pandas as pd
import os
import shutil
from collections import Counter
import subprocess

global_connection = None
hostname = None
username = None
password = None
port = None
db = None

def handle_login(hostname,username , passw , port=3306,db=None):
    try : 
        connection = mysql.connector.connect(host=hostname , user=username , password=passw , port=port ,database=db, auth_plugin='mysql_native_password')
        if isinstance(connection , mysql.connector.connection.MySQLConnection) :
            globals()["global_connection"]= connection
            globals()["hostname"] = hostname
            globals()["username"]= username
            globals()["password"]= passw
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
        return databases
    except Exception as err :
        print(err)

def create_database(my_db):
    try :
        con_cursor = global_connection.cursor() 
        con_cursor.execute(f"CREATE DATABASE {my_db}")
        global_connection.commit()
        return True
    except Exception as err :
        return err
    finally :
        con_cursor.close()

def show_tables(db_name):
    try :
        con_cursor = global_connection.cursor() 
        con_cursor.execute(f"SHOW TABLES FROM {db_name}")
        tables = con_cursor.fetchall()
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

def show_search_records(table_col_couple , term):
    try :
        table , column = table_col_couple  
        con_cursor = global_connection.cursor()
        con_cursor.execute(f"SELECT * FROM {table} WHERE {column} = '{term}';")
        rows = con_cursor.fetchall()
        columns = [i[0] for i in con_cursor.description]
        return columns,rows,get_prim_keys(con_cursor,table)
    except Exception as err :
        print(err) 
        
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

        tables_to_check = get_foreign_keys(foreign_keys_list,db_name)

        
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
        
def exec_query(query):
    try:
        con_cursor = global_connection.cursor()
        con_cursor.execute(query)
        
        # Check if the query is a SELECT query or not
        is_data_query = con_cursor.description is not None
        
        if is_data_query:
            result = con_cursor.fetchall()
            headers = [i[0] for i in con_cursor.description]
            return headers, result
        else:
            global_connection.commit()  # Commit changes for INSERT, UPDATE, DELETE, etc.
            return True  # Query executed successfully
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


def search_database(database, term_to_search ):
    try : 
        cursor = global_connection.cursor()
        make_db_search_queries = f"""
        SELECT CONCAT(
            'SELECT ''', TABLE_NAME, ''' AS table_name, ''', COLUMN_NAME, ''' AS value FROM ',
            TABLE_NAME, ' WHERE ', '`', COLUMN_NAME, '`', ' LIKE ''{term_to_search}'''
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
            select_statement = row[0].strip(" \" ") + ";"
            print(select_statement)
            # Execute the SELECT statement
            cursor.execute(select_statement)
            # Fetch and print the results of the SELECT statement
            select_results = cursor.fetchall()

            item_counter.update(select_results)

        return list(item_counter.items())
    except Exception as err :
        print(err)

def search_table(term_to_search , database , table):
    rows = []
    cursor = global_connection.cursor()
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

def sql_dump(path , table=None, *args):
        # Start building the command with basic arguments
    command = ['mysqldump', '-h', hostname, '-u', username, f'-p{password}']

    # Add optional options based on the specified arguments
    for arg in args[0]:
        command.append(arg)

    # Append the database name at the end
    command.append(db)

    if table :
        command.append(table)

    try:
        # Open the output file in write mode
        with open(path, 'w') as output_file:
            # Open MySQL shell using subprocess
            mysql_process = subprocess.Popen(
                command,
                stdout=output_file,  # Redirect stdout to the output file
                stderr=subprocess.PIPE,  # Capture stderr for error handling
                universal_newlines=True
            )

            # Wait for the process to finish and get the stderr output
            _, error = mysql_process.communicate()

            if error:
                return error


    except Exception as e:
        return e

def sql_import(path):
    try:
        con_cursor = global_connection.cursor()
        # Read SQL file content
        with open(path, 'r') as sql_file:
            sql_script = sql_file.read()
    
        # Execute the SQL script
        con_cursor.execute(sql_script , multi=True)
        con_cursor.commit()

    except Exception as err:
        return err
    
def copy_db(db_name,*args):
    # CREATE
    existent_databases = show_databases()
    if args[1] == 1 and not any(db_name in db_tuple for db_tuple in existent_databases):
        create_database(db_name)

    command = ['mysqldump', '-h', hostname, '-u', username, f'-p{password}']

    #append args
    for arg in args[0]:
        command.append(arg)

    # Append the database name at the end
    command.append(db)

    try :
        mysql_process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,  # Capture stdout
            stderr=subprocess.PIPE,  # Capture stderr (for error handling after)
            universal_newlines=True
        )

        # store the output in a variable
        query, error = mysql_process.communicate()

        cmd = f"mysql -h {hostname} -u {username} -p{password} {db_name}"
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        process.communicate(input=query)

    except Exception as err:
        return err

def rename_table(table , new_name):
    try : 
        cursor = global_connection.cursor()
        cursor.execute(f"ALTER TABLE {table} RENAME TO {new_name};")
        global_connection.commit()
    except Exception as err :
        return err
    
def empty_table(table):
    try : 
        cursor = global_connection.cursor()
        cursor.execute(f"DELETE FROM {table};")
        global_connection.commit()
    except Exception as err :
        return err

def delete_table(table):
    try : 
        cursor = global_connection.cursor()
        cursor.execute(f"DROP TABLE {table};")
        global_connection.commit()
    except Exception as err :
        return err

"""Rename Database"""
def rename_database(db_name , new_name):
    ...

"""Insert row into table"""
def insert_into_table(db_name,table , new_values , columns):
    try :
        new_values = [f"'{i}'" if  i is not None else 'NULL' for i in new_values]
        con_cursor = global_connection.cursor()
        insert_column= ', '.join([f"{column}" for column in columns])
        insert_values= ', '.join([f"{value}" for value in new_values])

        insert_query = f"INSERT INTO {table} ({insert_column}) VALUES ({insert_values});"
        print(insert_query)
        con_cursor.execute(insert_query)
        global_connection.commit()
    except Exception as err :
        print(err)

"""Get the Foreign keys in a table (the columns)"""
def fk_in_table(db_name , table):
    con_cursor = global_connection.cursor()
    # to get the foreign keys in a table (the one to whom the record belongs) 
    con_cursor.execute(f"SELECT COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA = '{db_name}' AND TABLE_NAME = '{table}';") 
    foreign_keys_list = con_cursor.fetchall()
    return foreign_keys_list

"""Get the Values of the foreign key"""
def get_foreign_keys_values(db_name , table):
    con_cursor = global_connection.cursor()
    foreign_keys_list = fk_in_table(db_name , table)

    for table , column in get_foreign_keys(foreign_keys_list ,db_name).items():
        con_cursor.execute(f"SELECT {column} FROM {table};")
        results = con_cursor.fetchall()
    if results : return results

"""To get the tables and columns where a key is used as foreign key"""
def get_foreign_keys(foreign_keys_list , db_name):
    con_cursor = global_connection.cursor()
    tables_to_check = {}
    # to get the the tables and the columns where the foreign keys are primary
    for foreign_key in foreign_keys_list :
        con_cursor.execute(f"SELECT REFERENCED_TABLE_NAME , REFERENCED_COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA = '{db_name}' AND REFERENCED_COLUMN_NAME IN ('{foreign_key[0]}');")
        tab_col_couple = con_cursor.fetchall()
        tables_to_check[tab_col_couple[0][0]] = tab_col_couple[0][1]
    return tables_to_check

#for user priveleges , i need to work on it in the copied database and the user priveleges of databases   
# mysql.user 
# SELECT CONCAT('SHOW GRANTS FOR ''', user, '''@''', host, ''';') AS SQLStatement
# FROM mysql.user
# WHERE user != 'root' AND host != 'localhost';

#for the delete table and empty table and delete row , delete column
# ALTER TABLE child_table
# ADD CONSTRAINT fk_parent_id
# FOREIGN KEY (parent_id)
# REFERENCES parent_table(parent_id)
# ON DELETE CASCADE;
    
