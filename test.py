
import mysql.connector

connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password="root",
    database="etudiant",
    auth_plugin='mysql_native_password'
)

cursor = connection.cursor()

#not the best
query = """
SELECT CONCAT('SELECT * FROM ', table_name, ' WHERE ', column_name, ' LIKE ''nizar''') FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'etudiant'; 
"""

search_table_query = """
SELECT CONCAT('SELECT * FROM ', table_name, ' WHERE ', column_name, ' LIKE ''nizar''')
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'etudiant' AND TABLE_NAME = 'etu';

"""

#query to create queries that check each table if it has this value , give back the name of table , and column , the number of rows given indicates the numbers of occurences
make_db_search_queries = """
SELECT CONCAT(
    'SELECT ''', TABLE_NAME, '.', COLUMN_NAME, ''' AS table_column, ''', COLUMN_NAME, ''' AS value, ''', TABLE_NAME, ''' AS table_name FROM ',
    TABLE_NAME, ' WHERE ', COLUMN_NAME, ' LIKE ''nizar'' UNION'
)
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'etudiant';
"""
cursor.execute(search_table_query)

results = cursor.fetchall() 

# for row in results :
#     print(row[0].rstrip(" \" ") + ";")   
# for row in results:
#     # Extract the SELECT statement from the row
#     select_statement = row[0].rstrip(" \" ") + ";"
#     # Execute the SELECT statement
#     cursor.execute(select_statement)
#     # Fetch and print the results of the SELECT statement
#     select_results = cursor.fetchall()
#     i = True
#     for result in select_results:
#         if result: 
#             if i == True :
#                 headers = [i[0] for i in cursor.description]
#                 print(headers)
#                 i = False
#             print(result)

cursor.close()
connection.close()

