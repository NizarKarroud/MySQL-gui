import subprocess

def build_mysqldump_command(hostname, user, password,database, *args):
    # Start building the command with basic arguments
    command = ['mysqldump', '-h', hostname, '-u', user, f'-p{password}']

    # Add optional options based on the specified arguments
    for arg in args:
        command.append(arg)

    # Append the database name at the end
    command.append(database)

    return command

def execute_mysql_dump(path, command):
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
                print(f"Error executing mysqldump: {error}")
            else:
                print("MySQL dump completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

"""
--no-data : just structure
--no-create-info :  just data
--add-drop-table : drop table if exist
--routines 
--events 
"""

command = build_mysqldump_command("localhost" , "root" , "root" , "etudiant"  ,"--events", )
print(*command)
# Call the function to execute mysqldump
execute_mysql_dump(r"C:\Users\Nizar\Documents\mysql_gui\dump.sql"  , command)
