import mysql.connector
import os
import shutil
from collections import Counter
import subprocess
import pandas as pd
from tkinter import messagebox
from wordcloud import WordCloud
import matplotlib 
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')


data_structure = {
    'int64': {
        'hist': [ 'mode' , 'value_counts'],
        'box': ["",'value_counts' ],
        'line': ["",'value_counts'],
        'kde': [],
        'bar': ["",'value_counts'],
        "area" : ["","value_counts" , 'cumsum'],
    },
    'float64': {
        'hist': ['value_counts' , "mode"],
        'box': ["",'value_counts'],
        'line': ["",'value_counts'],
        'kde': [],
        'bar': ["",'value_counts'],
        "area" : ["","value_counts" , 'cumsum'],

    },
    'datetime64': {
        'line': ["",'value_counts'],
    },
    'timedelta64': {
        'hist': ["",'value_counts'],
        'line': ["",'value_counts']
    },
    'object': {
        'bar': ['value_counts'],
        'wordcloud': ['wordcloud']
    },
    'category': {
        'bar': ['value_counts']
    },
    'bool': {
        'bar': ['value_counts']
    }
}
global_connection = None
hostname = None
username = None
password = None
port = None
db = None
cursor = None
auth_plugin = None

def handle_login(hostname,username , passw , port=3306,db=None ,auth_plugin='mysql_native_password'):
    try : 
        if port == "" : 
            port = 3306
        if auth_plugin == "" :
            auth_plugin='mysql_native_password' 
        
        connection = mysql.connector.connect(host=hostname , user=username , password=passw , port=port ,database=db, auth_plugin=auth_plugin)
        
        if isinstance(connection , mysql.connector.connection.MySQLConnection) :
            globals()["global_connection"]= connection
            globals()["hostname"] = hostname
            globals()["username"]= username
            globals()["password"]= passw
            globals()["port" ]= port
            globals()["db"] = db  
            globals()["auth_plugin"] = auth_plugin  
            globals()["cursor"] = connection.cursor()
            return True
        else :
            return False
    except mysql.connector.Error as err:
        messagebox.showerror(title='Error' , message=err) 


def show_databases():
    try :
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        return databases
    except Exception as err :
        messagebox.showerror(title='Error' , message=err) 

def create_database(my_db):
    try :
        cursor.execute(f"CREATE DATABASE {my_db}")
        global_connection.commit()
        return True
    except Exception as err :
        messagebox.showerror(title='Error' , message=err) 


def show_tables(db_name):
    try :
        cursor.execute(f"SHOW TABLES FROM {db_name}")
        tables = cursor.fetchall()
        return tables
    except Exception as err:
        messagebox.showerror(title='Error' , message=err) 

def drop_db(db_name):
    try :
        cursor.execute(f"DROP DATABASE {db_name}")
        return True
    except Exception as err:
        messagebox.showerror(title='Error' , message=err) 

def show_search_records(table_col_couple , term):
    try :
        table , column = table_col_couple  
        cursor.execute(f"SELECT * FROM {table} WHERE {column} = '{term}';")
        rows = cursor.fetchall()
        columns = [i[0] for i in cursor.description]
        return columns,rows,get_prim_keys(cursor,table)
    except Exception as err :
        messagebox.showerror(title="Error" , message=err)
       
def show_table_records(table):
    try :
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        columns = [i[0] for i in cursor.description]
        return columns,rows,get_prim_keys(cursor,table)
    except Exception as err:
        messagebox.showerror(title='Error' , message=err) 

def get_prim_keys(cursor,table):
    try :
        cursor.execute(f"SHOW KEYS FROM {table} WHERE Key_name = 'PRIMARY';")
        rows = cursor.fetchall()
        
        return [row[4] for i,row in enumerate(rows)]

    except Exception as err:
        messagebox.showerror(title='Error' , message=err) 


def alter_table(db_name , table, values , columns, key_val_couple ):
    try :

        values = [f"'{i}'" if  i is not None else 'NULL' for i in values]

        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        # to get where the primary key of a table is a foreign key ( the table name , and column name) so that i can implement some sort of UPDATE ON CASCADE
        ref_clause = ", ".join([f"'{column[0]}'" for column in key_val_couple])
        cursor.execute(f"SELECT TABLE_NAME, COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA = '{db_name}' AND REFERENCED_COLUMN_NAME IN ({ref_clause});")
        foreign_relations = cursor.fetchall()

        # to get the foreign keys in a table (the one to whom the record belongs) 
        cursor.execute(f"SELECT COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA = '{db_name}' AND TABLE_NAME = '{table}';") 
        foreign_keys_list = cursor.fetchall()

        tables_to_check = get_foreign_keys(foreign_keys_list,db_name)

        
        if tables_to_check :
        #check if the updated value of the the foreign keys exist in the records of their tables
            for foreign_table , column in tables_to_check.items():
                value = dict(zip(columns, values))[column]
                cursor.execute(f"SELECT COUNT(*) FROM {foreign_table} WHERE {column} = {value};")
                result = cursor.fetchall()[0]
                if result[0] > 0  :
                    set_clause = ', '.join([f"{column} = {value}" for column, value in zip(columns, values)])

                    where_clause = ' AND '.join([f"{key} = '{value}'" for key,value in key_val_couple])

                    query_update = f"UPDATE {table} SET {set_clause} WHERE {where_clause};"
                    cursor.execute(query_update)

                    set_clause_keys = {key : value for key , value in zip(columns , values) if any(key == key_couple[0] for key_couple in key_val_couple)}
                    ref_set_clause = ','.join([f"{column} = {value}" for column , value in set_clause_keys.items()])
                    for relation in foreign_relations :
                        cursor.execute(f"UPDATE {relation[0]} SET {ref_set_clause} WHERE {where_clause};")

                    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

                    global_connection.commit()
        else : 
            set_clause = ', '.join([f"{column} = {value}" for column, value in zip(columns, values)])

            where_clause = ' AND '.join([f"{key} = '{value}'" for key,value in key_val_couple])

            query_update = f"UPDATE {table} SET {set_clause} WHERE {where_clause};"
            cursor.execute(query_update)


            set_clause_keys = {key : value for key , value in zip(columns , values) if any(key == key_couple[0] for key_couple in key_val_couple)}
            ref_set_clause = ','.join([f"{column} = {value}" for column , value in set_clause_keys.items()])
            for relation in foreign_relations :
                cursor.execute(f"UPDATE {relation[0]} SET {ref_set_clause} WHERE {where_clause};")

            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

            global_connection.commit()     
    except Exception as err:
        messagebox.showerror(title='Error' , message=err) 

     
def exec_query(query):
    try:
        cursor.execute(query)
        
        # Check if the query is a SELECT query or not
        is_data_query = cursor.description is not None
        
        if is_data_query:
            result = cursor.fetchall()
            headers = [i[0] for i in cursor.description]
            return headers, result
        else:
            global_connection.commit()  # Commit changes for INSERT, UPDATE, DELETE, etc.
            return True 
    except Exception as err:
        messagebox.showerror(title='Error' , message=err) 
 

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
            select_statement = row[0].strip(" \" ") + ";"
            cursor.execute(select_statement)
            select_results = cursor.fetchall()

            item_counter.update(select_results)

        return list(item_counter.items())
    except Exception as err :
        messagebox.showerror(title='Error' , message=err) 


def search_table(term_to_search , database , table):
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
        
        cursor.execute(select_statement)

        select_results = cursor.fetchall()
        
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

    except Exception as err:
        messagebox.showerror(title='Error' , message=err) 


def sql_import(path):
    try:
        # Read SQL file content
        with open(path, 'r') as sql_file:
            sql_script = sql_file.read()
    
        # Execute the SQL script
        cursor.execute(sql_script , multi=True)
        cursor.commit()

    except Exception as err:
        messagebox.showerror(title='Error' , message=err) 

    
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
        messagebox.showerror(title='Error' , message=err) 


def rename_table(table , new_name):
    try : 
        cursor.execute(f"ALTER TABLE {table} RENAME TO {new_name};")
        global_connection.commit()
    except Exception as err :
        messagebox.showerror(title='Error' , message=err) 

    
def empty_table(table):
    try : 
        cursor.execute(f"DELETE FROM {table};")
        global_connection.commit()
    except Exception as err :
        messagebox.showerror(title='Error' , message=err) 


def delete_table(table):
    try : 
        cursor = global_connection.cursor()
        cursor.execute(f"DROP TABLE {table};")
        global_connection.commit()
    except Exception as err :
        messagebox.showerror(title='Error' , message=err) 


"""Rename Database"""
def rename_database(db_name , new_name):
    try :
        create_database(new_name)
        command = ['mysqldump', '-h', hostname, '-u', username, f'-p{password}' , db_name]
        mysql_process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,  # Capture stdout
            stderr=subprocess.PIPE,  # Capture stderr (for error handling after)
            universal_newlines=True
        )

        # store the output in a variable
        query, error = mysql_process.communicate()

        cmd = f"mysql -h {hostname} -u {username} -p{password} {new_name}"
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        process.communicate(input=query)
        drop_db(db_name)
    except Exception as err:
        messagebox.showerror(title='Error' , message=err) 


"""Insert row into table"""
def insert_into_table(db_name,table , new_values , columns):
    try :
        new_values = [f"'{i}'" if  i is not None else 'NULL' for i in new_values]
        insert_column= ', '.join([f"{column}" for column in columns])
        insert_values= ', '.join([f"{value}" for value in new_values])

        insert_query = f"INSERT INTO {table} ({insert_column}) VALUES ({insert_values});"
        cursor.execute(insert_query)
        global_connection.commit()
    except Exception as err :
        messagebox.showerror(title='Error' , message=err) 


"""Get the Foreign keys in a table (the columns)"""
def fk_in_table(db_name , table):
    # to get the foreign keys in a table (the one to whom the record belongs) 
    cursor.execute(f"SELECT COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA = '{db_name}' AND TABLE_NAME = '{table}';") 
    foreign_keys_list = cursor.fetchall()
    return foreign_keys_list

"""Get the Values of the foreign key"""
def get_foreign_keys_values(db_name , table):
    foreign_keys_list = fk_in_table(db_name , table)

    for table , column in get_foreign_keys(foreign_keys_list ,db_name).items():
        cursor.execute(f"SELECT {column} FROM {table};")
        results = cursor.fetchall()
    if results : return results

"""To get the tables and columns where a key is used as foreign key"""
def get_foreign_keys(foreign_keys_list , db_name):
    tables_to_check = {}
    # to get the the tables and the columns where the foreign keys are primary
    for foreign_key in foreign_keys_list :
        cursor.execute(f"SELECT REFERENCED_TABLE_NAME , REFERENCED_COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA = '{db_name}' AND REFERENCED_COLUMN_NAME IN ('{foreign_key[0]}');")
        tab_col_couple = cursor.fetchall()
        tables_to_check[tab_col_couple[0][0]] = tab_col_couple[0][1]
    return tables_to_check

"""Create a Trigger"""
def trigger(trigger_name,time,event,table_name,logic):
    try :
        trigger_syntax = f"""DELIMITER $$
        CREATE TRIGGER {trigger_name}
        {time} {event}
        ON {table_name}
        FOR EACH ROW
        BEGIN
        {logic}
        END$$
        DELIMITER ;
        """
        cursor.execute(trigger_syntax)
        global_connection.commit()

    except Exception as err :   
        messagebox.showerror(title='Error' , message=err) 


def delete_row(table , key_val_couple):
    try : 
        where_clause = ' AND '.join([f"{key} = '{value}'" for key,value in key_val_couple])

        delete_query = f"DELETE FROM {table} WHERE {where_clause}"
        cursor.execute(delete_query)
        global_connection.commit()
    except Exception as err :
        messagebox.showerror(title='Error' , message=err) 


def drop_column(table , column) :
    try:
        drop_column_query = f"ALTER TABLE {table} DROP COLUMN {column};"
        cursor.execute(drop_column_query)
        global_connection.commit()
    except Exception as err :
        messagebox.showerror(title='Error' , message=err) 


def create_table(table_name , columns_list):
    try :
        query = f"CREATE TABLE {table_name}( "
        for column in columns_list :
            column_name, data_type, size, nullable, index, reference, auto_increment = column
            column_syntax = f"{column_name} {data_type}({size})"
            if index != "" and index != "FOREIGN KEY" :
                column_syntax+= f" {index} "
            if nullable == "True" :
                column_syntax += " NULL "
            else :
                column_syntax += " NOT NULL "
            if auto_increment == "True" :
                column_syntax += " AUTO_INCREMENT "    
            if reference :
                column_syntax += f",\n FOREIGN KEY ({column_name}) REFERENCES {reference}"     
            query += column_syntax + ", "  
        query = query[:-2] + ");"   

        cursor.execute(query)
        global_connection.commit(   ) 
    except Exception as err :
        messagebox.showerror(title='Error' , message=err) 

def create_dataframe_from_mysql( table):
    try : 
        query = f'SELECT * FROM {table}'
        df = pd.read_sql_query(query , global_connection)
        return df
    except Exception as err :
        messagebox.showerror(title='Error' , message=err) 
 
def get_possible_plots(table , column):
    try : 
        df = create_dataframe_from_mysql(table)
        data_type = df[column].dtype
        plot_list = [plot_type for data_types, data_plots in data_structure.items() if str(data_type) in data_types for plot_type in data_plots.keys()]
        return (str(data_type),plot_list , df[column])
    except Exception as err :
        messagebox.showerror(title='Error' , message=err) 
 
def get_possible_measures(plot_type , data_type):
    return data_structure[data_type][plot_type]


def generate_plot(df, plot_type, measure):
    try:
        # Check if no measure is provided
        if not measure:
            df.plot(kind=plot_type)
            plt.title(f'{plot_type} Plot') 
            plt.show()

        # Check if measure is a method of the DataFrame
        elif measure in dir(df) and callable(getattr(df, measure)):
            # Call the measure method and plot the result
            getattr(df, measure)().plot(kind=plot_type)
            plt.ylabel(measure)
            plt.title(f'{measure} {plot_type}')
            plt.show()
        else:
            # Create a word cloud if measure is not a method of the DataFrame
            text_data = ' '.join(df)
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_data)
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('Word Cloud')
            plt.show()


    except Exception as err:
        messagebox.showerror(title='Error', message=err)
