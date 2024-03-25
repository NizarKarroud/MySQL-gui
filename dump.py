import subprocess

def execute_mysql_dump(path ,hostname, user , password , database):
    try:
        # Open the output file in write mode
        with open(fr"{path}", 'w') as output_file:
            # Open MySQL shell using subprocess
            mysql_process = subprocess.Popen(
                ['mysqldump', '-h', f'{hostname}', '-u', f'{user}', f'-p{password}', f"{database}"],
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

# Call the function to execute mysqldump
execute_mysql_dump()
