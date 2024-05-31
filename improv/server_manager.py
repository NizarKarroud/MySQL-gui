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

 #mysql_native_password

class MySQL_connection:

    def __init__(self, hostname, username, pwd, port, auth_plugin , db=None):
        self.__hostname = hostname
        self.__username = username
        self.__pwd = pwd
        self.__db = db
        if port == "":
            self.__port = 3306
        else :
            self.__port = port
        if auth_plugin == "":
            self.__auth_plugin = ''
        else :
            self.__auth_plugin = auth_plugin
        self.connect()
        self.mysql_cursor()

    def connect(self) :
        try : 
            self.__connection = mysql.connector.connect(
                host=self.__hostname ,
                user=self.__username ,
                password=self.__pwd  , 
                port=self.__port ,
                database=self.__db, 
                auth_plugin=self.__auth_plugin)   
            self.__connected = True
        except Exception as err:
            messagebox.showerror(title='Error' , message=err)
            self.__connected = False

    def mysql_cursor(self):
        try :
            if self.__connected :
                self.__cursor = self.__connection.cursor()
        except Exception as err : 
            pass

    def close_connection(self) :
        if self.__connection :
            self.__connection.close()
    
    def close_cursor(self):
        if self.__cursor:
            self.__cursor.close()

    @property
    def connection(self):
        return self.__connection

    @property
    def cursor(self):
        return self.__cursor
    
    @property
    def hostname(self):
        return self.__hostname

    @property
    def username(self):
        return self.__username

    @property
    def pwd(self):
        return self.__pwd

    @property
    def port(self):
        return self.__port

    @property
    def db(self):
        return self.__db

    @property
    def auth_plugin(self):
        return self.__auth_plugin
    @property
    def connected(self):
        return self.__connected
    
class MySQL_Manager:
    def __init__(self, connection , cursor) :
        self.__connection = connection 
        self.__cursor = cursor 

    def exec_sql_fetch(self,sql):
        try:
            self.__cursor.execute(sql)
            return self.__cursor.fetchall()
        except Exception as err:
            messagebox.showerror(title='Error', message=err)

    def exec_sql_commit(self,sql , **kwargs):
        try :
            self.__cursor.execute(sql , kwargs)
            self.__connection.commit()
            return True
        except Exception as err :
            messagebox.showerror(title='Error' , message=err) 
            return False

    def show_databases(self):
        sql = "SHOW DATABASES"
        return  self.exec_sql_fetch(sql)
     
    def create_database(self,database):
        sql = f"CREATE DATABASE {database}"
        return self.exec_sql_commit(sql)            

    def show_tables(self , database):
        sql = f"SHOW TABLES FROM {database}"
        return  self.exec_sql_fetch(sql)

    def drop_db(self , database):
        sql = f"DROP DATABASE {database}"            
        return self.exec_sql_commit(sql)

    def show_search_records(self , table_col_couple , term):
            table , column = table_col_couple  
            sql = f"SELECT * FROM {table} WHERE {column} = '{term}';"
            rows =  self.exec_sql_fetch(sql)
            columns = [i[0] for i in self.__cursor.description]
            return columns,rows,self.get_prim_keys(table)

    def show_table_records(self , table):
        sql = f"SELECT * FROM {table}"
        rows =  self.exec_sql_fetch(sql)
        columns = [i[0] for i in self.__cursor.description]
        return columns,rows,self.get_prim_keys(table)
    
    def get_prim_keys(self,table):
        sql = f"SHOW KEYS FROM {table} WHERE Key_name = 'PRIMARY';"
        rows =  self.exec_sql_fetch(sql)
        return [row[4] for i,row in enumerate(rows)]

    def exec_query(self,query):
        try : 
            self.__cursor.execute(query)
            
            # Check if the query is a SELECT query or not
            is_data_query = self.__cursor.description is not None
            
            if is_data_query:
                result = self.__cursor.fetchall()
                headers = [i[0] for i in self.__cursor.description]
                return headers, result
            else:
                self.__connection.commit()  # Commit changes for INSERT, UPDATE, DELETE, etc.
                return True 
            
        except Exception as err :
            messagebox.showerror(title='Error' , message=err) 
            return False

    def export_database(self , database ,table_list, path, extension):
        tables = table_list[:]

        # checking if the folder where the archive is going to be located exists
        if os.path.exists(path):
            new_folder_path = os.path.join(path, database)

            # Check if the folder already exists within the parent path
            if not os.path.exists(new_folder_path):
                try:
                    # Create the folder within the parent path
                    os.makedirs(new_folder_path)
                except OSError as e:
                    return f"Error creating folder at {new_folder_path}: {e}"
        
            export_errors = []  # List to store export errors for each table
            for table in tables:
                columns , rows , prim = tuple(self.show_table_records(table))
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

    def search_database(self,database, term_to_search ):
        make_db_search_queries = f"""
        SELECT CONCAT(
            'SELECT ''', TABLE_NAME, ''' AS table_name, ''', COLUMN_NAME, ''' AS value FROM ',
            TABLE_NAME, ' WHERE ', '`', COLUMN_NAME, '`', ' LIKE ''{term_to_search}'''
        )
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{database}';

        """
        results = self.exec_sql_fetch(make_db_search_queries)

        final_result = []
        item_counter = Counter()

        for row in results:
            select_statement = row[0].strip(" \" ") + ";"

            select_results = self.exec_sql_fetch(make_db_search_queries)
            item_counter.update(select_results)
        return list(item_counter.items())

    def search_table(self , term_to_search , database , table):
        rows = []
        search_table_query = f"""
            SELECT CONCAT('SELECT * FROM ', table_name, ' WHERE ', column_name, ' LIKE ''{term_to_search}''')
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{database}' AND TABLE_NAME = '{table}';
            """

        results = self.exec_sql_fetch(search_table_query)
        printed_header = False
        for row in results:
        # Extract the SELECT statement from the row
            select_statement = row[0].rstrip(" \" ") + ";"
            

            select_results = self.exec_sql_fetch(select_statement)
            
            if not printed_header:
                headers = [i[0] for i in self.__cursor.description]
                header = headers
                printed_header = True

            for result in select_results:
                if result:
                    rows.append(result)

        return(header , rows)

    # def sql_dump(self , path , table=None, *args):
    #         # Start building the command with basic arguments
    #     command = ['mysqldump', '-h', hostname, '-u', username, f'-p{password}']

    #     # Add optional options based on the specified arguments
    #     for arg in args[0]:
    #         command.append(arg)

    #     # Append the database name at the end
    #     command.append(db)

    #     if table :
    #         command.append(table)

    #     try:
    #         # Open the output file in write mode
    #         with open(path, 'w') as output_file:
    #             # Open MySQL shell using subprocess
    #             mysql_process = subprocess.Popen(
    #                 command,
    #                 stdout=output_file,  # Redirect stdout to the output file
    #                 stderr=subprocess.PIPE,  # Capture stderr for error handling
    #                 universal_newlines=True
    #             )

    #             # Wait for the process to finish and get the stderr output
    #             _, error = mysql_process.communicate()

    #             if error:
    #                 return error

    #     except Exception as err:
    #         messagebox.showerror(title='Error' , message=err) 


    # def sql_import(self , path):
        try:
            # Read SQL file content
            with open(path, 'r') as sql_file:
                sql_script = sql_file.read()
        
            # Execute the SQL script
            self.exec_sql_commit(sql_script , multi=True)

        except Exception as err:
            messagebox.showerror(title='Error' , message=err) 

    def copy_db(self, database , current_db,hostname,username,password,*args):
        # CREATE
        existent_databases = self.show_databases()
        if args[1] == 1 and not any(database in db_tuple for db_tuple in existent_databases):
            self.create_database(database)

        command = ['mysqldump', '-h', hostname, '-u', username, f'-p{password}']

        #append args
        for arg in args[0]:
            command.append(arg)

        # Append the database name at the end
        command.append(current_db)

        try :
            mysql_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,  # Capture stdout
                stderr=subprocess.PIPE,  # Capture stderr (for error handling after)
                universal_newlines=True
            )

            # store the output in a variable
            query, error = mysql_process.communicate()

            cmd = f"mysql -h {hostname} -u {username} -p{password} {database}"
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            process.communicate(input=query)

        except Exception as err:
            messagebox.showerror(title='Error' , message=err) 

    def rename_table(self,table , new_name):
        sql = f"ALTER TABLE {table} RENAME TO {new_name};"
        self.exec_sql_commit(sql)
    
    def empty_table(self,table):
        sql = f"DELETE FROM {table};"
        self.exec_sql_commit(sql)            

    def delete_table(self , table):
        sql = f"DROP TABLE {table};"
        self.exec_sql_commit(sql)
    
    """Rename Database"""
    def rename_database(self , database ,hostname,username,password, new_name):
        try :
            self.create_database(new_name)
            command = ['mysqldump', '-h', hostname, '-u', username, f'-p{password}' , database]
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
            self.drop_db(database)
        except Exception as err:
            messagebox.showerror(title='Error' , message=err) 

    """Insert row into table"""
    def insert_into_table(self ,table , new_values , columns):
        new_values = [f"'{i}'" if  i is not None else 'NULL' for i in new_values]
        insert_column= ', '.join([f"{column}" for column in columns])
        insert_values= ', '.join([f"{value}" for value in new_values])

        insert_query = f"INSERT INTO {table} ({insert_column}) VALUES ({insert_values});"
        self.exec_sql_commit(insert_query)

    """Get the Foreign keys in a table (the columns)"""
    def fk_in_table(self ,database , table):
        # to get the foreign keys in a table (the one to whom the record belongs) 
        return self.exec_sql_fetch(f"SELECT COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA = '{database}' AND TABLE_NAME = '{table}';") 

    """Get the Values of the foreign key"""
    def get_foreign_keys_values(self ,database , table):
        foreign_keys_list = self.fk_in_table(database , table)

        for table , column in self.get_foreign_keys(foreign_keys_list ,database).items():
            results = self.exec_sql_fetch(f"SELECT {column} FROM {table};")
        if results : return results

    """To get the tables and columns where a key is used as foreign key"""
    def get_foreign_keys(self ,foreign_keys_list , database):
        tables_to_check = {}
        # to get the the tables and the columns where the foreign keys are primary
        for foreign_key in foreign_keys_list :
            tab_col_couple =  self.exec_sql_fetch(f"SELECT REFERENCED_TABLE_NAME , REFERENCED_COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE REFERENCED_TABLE_SCHEMA = '{database}' AND REFERENCED_COLUMN_NAME IN ('{foreign_key[0]}');")
            tables_to_check[tab_col_couple[0][0]] = tab_col_couple[0][1]
        return tables_to_check

    """Create a Trigger"""
    def trigger(self ,trigger_name,time,event,table_name,logic):
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
        self.exec_sql_commit(trigger_syntax)

    def delete_row(self,table , key_val_couple):
            where_clause = ' AND '.join([f"{key} = '{value}'" for key,value in key_val_couple])
            delete_query = f"DELETE FROM {table} WHERE {where_clause}"
            self.exec_sql_commit(delete_query)

    def drop_column(self , table , column) :
        drop_column_query = f"ALTER TABLE {table} DROP COLUMN {column};"
        self.exec_sql_commit(drop_column_query)

    def create_table(self , table_name , columns_list):
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

            self.exec_sql_commit(query)

    def create_dataframe_from_mysql( self, table):
        try : 
            query = f'SELECT * FROM {table}'
            df = pd.read_sql_query(query , self.__connection)
            return df
        except Exception as err :
            messagebox.showerror(title='Error' , message=err) 
    
    def get_possible_plots(self ,table , column):
        try : 
            df = self.create_dataframe_from_mysql(table)
            data_type = df[column].dtype
            plot_list = [plot_type for data_types, data_plots in data_structure.items() if str(data_type) in data_types for plot_type in data_plots.keys()]
            return (str(data_type),plot_list , df[column])
        except Exception as err :
            messagebox.showerror(title='Error' , message=err) 
    
    def get_possible_measures(self, plot_type , data_type):
        return data_structure[data_type][plot_type]

    def generate_plot(self ,df, plot_type, measure):
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
