import subprocess

def execute_mysql_dump(path,file_name ,hostname, user , password , database):
    try:
        # Open the output file in write mode
        with open(fr"{path}\{file_name}.sql", 'w') as output_file:
            # Open MySQL shell using subprocess
            mysql_process = subprocess.Popen(
                ['mysqldump', '-h', f'{hostname}', '-u', f'{user}', f'-p{password}', '--add-drop-table' , f'{database}'],
                stdout=output_file,  # Redirect stdout to the output file
                stderr=subprocess.PIPE,  # Capture stderr for error handling
                universal_newlines=True
            )

            # Wait for the process to finish and get the stderr output
            _, error = mysql_process.communicate()

            if error:
                print(f"Error executing mysqldump: {error}")
            else:
                print("MySQL dump completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

"""
de base struct and data
--no-data : just structure
--no-create-info :  jusr data
--add-drop-table : drop table if exist
 --routines 
 --events 
"""



# Call the function to execute mysqldump
execute_mysql_dump(r"C:\Users\Nizar\Documents\mysql_gui" ,"etu_priv" , "localhost" , "root" , "root" , "etudiant")
