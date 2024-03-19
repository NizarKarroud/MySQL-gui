from customtkinter import CTkScrollableFrame
import mysql_con
from tkinter import ttk , messagebox
import tkinter as tk
import ttkbootstrap

def login_success(frame , hostname  ,port ,username , password ) :
    connection = mysql_con.handle_login(hostname= 'localhost',username='root',passw= 'root' , port="3306") 
        # hostname= hostname ,username= username ,passw= password , port=port 
    if connection == True :
        frame.destroy()
        database_menu()
    else : 
        messagebox.showerror(title='Error' , message=connection )

   
def db_create(db_create_entry):
    db_creation = mysql_con.create_database(db_create_entry)
    if db_creation == True :
        database_menu()
    else :
        messagebox.showerror(title='Error' , message=db_creation )


def show_db_tables(db_name):
    connection = mysql_con.handle_login(hostname= mysql_con.hostname ,username= mysql_con.username,passw=mysql_con.passowrd , port=mysql_con.port , db=db_name) 
    if connection == True :
        return mysql_con.show_tables(db_name)
    else : 
        messagebox.showerror(title='Error' , message=connection )

def drop_db(frame,db_name):
    dropped = mysql_con.drop_db(db_name)
    if dropped ==True :
        frame.destroy()
        database_menu()
    else : 
        messagebox.showerror(title='Error' , message=dropped )


def show_columns(table_frame,table):
    table_frame.destroy()
    record_frame(table)

def click_on_row(frame,primary_keys,table ,headers , selected_row):
    row_data = list(zip(headers,selected_row))
    print(primary_keys)
    print(row_data)

    keys_values_couples = []
    for couple in row_data :
        for key in primary_keys :
            if couple[0] == key :
                keys_values_couples.append(couple)

    print(keys_values_couples)
    update_row_window(frame ,table , headers , selected_row ,keys_values_couples)

def create_login_page(): 
    frame = ttk.Frame(master=app)
    frame.pack(pady=20 , padx=60 , fill="both" , expand=True)

    label = ttk.Label(master=frame, text="Login" , font=("Roboto" , 30))
    label.pack(padx=20 , pady=22)
    host_label = ttk.Label(master=frame, text="Hostname :")
    host_label.pack(pady=10)

    hostname = tk.StringVar()
    host_entry = ttk.Entry(frame, textvariable=hostname)
    host_entry.pack(padx=10, pady=10)

    port_label = ttk.Label(master=frame, text="Port :")
    port_label.pack(pady=10)

    port = tk.StringVar()
    port_entry = ttk.Entry(frame, textvariable=port)
    port_entry.pack(padx=10, pady=10)

    username_label = ttk.Label(master=frame, text="Username :")
    username_label.pack(pady=10)

    username = tk.StringVar()
    username_entry = ttk.Entry(frame, textvariable=username)
    username_entry.pack(padx=10, pady=10)

    password_label = ttk.Label(master=frame, text="Password :")
    password_label.pack(pady=10)

    password = tk.StringVar()
    password_entry = ttk.Entry(frame, textvariable=password, show='*')
    password_entry.pack(padx=10, pady=10)

    login_button = ttk.Button(master=frame, text="Login", command=lambda: login_success(frame, hostname.get(), port.get(), username.get(), password.get()))
    login_button.pack(pady=10)

""" The Database Menu and Create new Database functionality """
def database_menu():
    menu_frame = CTkScrollableFrame(master=app)
    menu_frame.grid(row=0, column=0 , sticky="ns")
    app.grid_rowconfigure(0, weight=1) 

    new_db = tk.StringVar()
    db_create_entry = ttk.Entry(menu_frame, textvariable=new_db )
    db_create_entry.pack(pady=(60,0)) 

    create_database_button = ttk.Button(menu_frame,text="Create a new Database" ,command=lambda:db_create(new_db.get()))
    create_database_button.pack(side="top", pady=(10,40))

    databases = mysql_con.show_databases()
    databases_buttons = [ttk.Button(menu_frame,text=database , command=lambda db=database: tables_frame(db[0])).pack(side="top", pady=10) for database in databases]

""" Frame that contains the database Operations and Tables """
def tables_frame(db_name):
    #main frame
    table_frame = CTkScrollableFrame(master=app)
    table_frame.grid(row=0, column=1 , sticky="nswe")
    app.grid_columnconfigure(1, weight=1) 
    app.grid_rowconfigure(0, weight=1)

    # button to get to the table creation page
    create_table_button =ttk.Button(table_frame , text="Create new Table" , command=lambda:table_create_page(table_frame))
    create_table_button.pack(anchor="ne" ,padx=10 , pady=15)

    # Button to drop the database
    drop_db_button = ttk.Button(table_frame , text="Drop database" , command=lambda: drop_db(table_frame,db_name))
    drop_db_button.pack(anchor="ne" ,padx=10 , pady=15)

    # Button to get to the SQL query Page
    sql_button = ttk.Button(table_frame, text='SQL Query' , command= lambda : sql_text_box(db_name)) 
    sql_button.pack(anchor="ne" ,padx=10 , pady=15)

    tables = show_db_tables(db_name)
    tables_buttons = [ttk.Button(table_frame,text=table, command=lambda table=table[0] : show_columns(table_frame,table)).pack(side="top", pady=10) for table in tables]

def sql_text_box(db_name):

    #frame for the text
    sql_frame = ttk.Frame(master=app)
    sql_frame.grid(row=0, column=1 , sticky="nswe")
    app.grid_columnconfigure(1, weight=1) 
    app.grid_rowconfigure(0, weight=1)

    # Text (SQL CODE)
    text_box = tk.Text(sql_frame)
    text_box.pack(padx=20 , pady= (20,10) ,fill='both' , expand=True)

    #button to execute the query
    exec_button = ttk.Button(sql_frame, text='Execute' , command= lambda : sql_query(db_name,text_box.get(1.0, "end-1c")))
    exec_button.pack(pady=(10,30),padx=20 , side='right')

def sql_query(db_name,query):
    print(query)
    print(db_name)
    # work on the query in th mysql_con file

""" TABLE CREATION PAGE """
def table_create_page(table_frame):
    table_frame.destroy()

    # main frame
    table_name_frame = ttk.Frame(app)
    table_name_frame.grid(column= 1  , row=0 , sticky = "nswe")
    app.grid_rowconfigure(0, weight=1) 
    app.grid_columnconfigure(1, weight=1) 

    # frame for the table name and add column button
    create_column_frame = ttk.Frame(table_name_frame)
    create_column_frame.grid(column= 0  , row=0 , sticky = "ew" , columnspan=2)
    table_name_frame.grid_columnconfigure(0, weight=1)  

    # frame for the treeview
    treeframe = ttk.Frame(table_name_frame)
    treeframe.grid(column= 1  , row=2 , sticky = "nswe" , columnspan=2)
    table_name_frame.grid_rowconfigure(2, weight=1)  
    table_name_frame.grid_columnconfigure(1, weight=1)

    # Add Vertical scrollbar
    tree_y_Scrollbar = ttk.Scrollbar(treeframe , orient="vertical")
    tree_y_Scrollbar.pack(side="right",fill="y")

    # Add horizontal scrollbar
    tree_x_Scrollbar = ttk.Scrollbar(treeframe , orient="horizontal")
    tree_x_Scrollbar.pack(fill="x" , side="bottom")

    columns = ["Name" , "Type" , "Length/Values" , "Null" , "Index" , "Reference" ]
    # Create a Treeview widget
    treeview = ttk.Treeview(treeframe,show='headings', xscrollcommand=tree_x_Scrollbar.set ,yscrollcommand= tree_y_Scrollbar.set,height=1 , columns=columns)
    treeview.pack()

    for column in columns :
        treeview.column(column, anchor="center")
        treeview.heading(column , text=column)

    # the table create button
    execute_button = ttk.Button( create_column_frame , text='Execute' , command=...  )
    execute_button.grid(row=0 , column=3 , padx=140)

    tree_y_Scrollbar.config(command=treeview.yview)
    tree_x_Scrollbar.config(command=treeview.xview)


    table_label = ttk.Label(create_column_frame , text='Table Name : ')
    table_label.grid(row=0 , column=0 , padx=30 , pady=30 )

    # New Table's Name
    table_name = tk.StringVar()
    table_name_entry = ttk.Entry(create_column_frame, textvariable=table_name )
    table_name_entry.grid(row=0 , column=1 , padx=(5,30) , pady=30)

    # add column to the new table Button
    add_column_button = ttk.Button(create_column_frame, text="Add column" , command=lambda: add_column())
    add_column_button.grid(row=0 , column=2 , padx=30 , pady=30)


    # adding columns to the new table
    def add_column():
        column_name = tk.StringVar()
        option = tk.StringVar()
        type_values = ["TINYINT" , "SMALLINT" , "MEDIUMINT" , "BIGINT" , "DECIMAL" , "FLOAT" , "DOUBLE" , "REAL" , "BIT" , "BOOLEAN" , "DATE" , "SERIAL" , "DATETIME" , "TIMESTAMP" , "TIME", "YEAR" , "CHAR" , "VARCHAR" , "TINYTEXT" , "TEXT" , "MEDIUMTEXT" , "LONGTEXT" , "BINARY" , "VARBINARY" , "ENUM" , "SET" , "JSON"]
        
        # incomplete

        row = [ttk.Entry(create_column_frame, textvariable=column_name) , ttk.OptionMenu(create_column_frame, variable=option)]
        treeview.config(height=int(treeview.cget("height"))+1)
        treeview.insert("" , tk.END , values=...)

""" Table's Records """

def record_frame(table):
    columns , rows , primary_key = mysql_con.show_table_records(table)
    treeframe = ttk.Frame(app)
    treeframe.grid(column= 1  , row=0 , sticky = "nswe")
    app.grid_rowconfigure(0, weight=1) 
    app.grid_columnconfigure(1, weight=1) 

    # Add vertical scrollbar
    tree_y_Scrollbar = ttk.Scrollbar(treeframe , orient="vertical")
    tree_y_Scrollbar.pack(side="right",fill="y")

    # Add horizontal scrollbar
    tree_x_Scrollbar = ttk.Scrollbar(treeframe , orient="horizontal")
    tree_x_Scrollbar.pack(fill="x" , side="bottom")

    
    # Create a Treeview widget
    treeview = ttk.Treeview(treeframe,show='headings', xscrollcommand=tree_x_Scrollbar.set ,yscrollcommand= tree_y_Scrollbar.set,  columns=columns ,height=len(rows))
    treeview.pack()

    # add the columns as Headers
    for column in columns :
        treeview.column(column, anchor="center")
        treeview.heading(column , text=column)

    # Insert data into the treeview
    for row in rows :
        treeview.insert("" , tk.END , values=row)

    tree_y_Scrollbar.config(command=treeview.yview)
    tree_x_Scrollbar.config(command=treeview.xview)


    treeview.bind('<Double-1>', lambda event , headers=columns: click_on_row(treeframe,primary_key ,table , headers , treeview.item(treeview.selection())['values']))


""" UPDATE row values """

def update_row_window(frame ,table , columns, selected_row , key_val_cpl):    
    window = tk.Toplevel(app)
    window.geometry("800x600")
    window.title("Alter Row")
    
    # Create a scrollable frame inside the window
    scroll_frame = ttk.Frame(window)
    scroll_frame.pack(fill=tk.BOTH, expand=True)

    # Add a canvas to make the frame scrollable
    canvas = tk.Canvas(scroll_frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Add a scrollbar
    scrollbar = ttk.Scrollbar(scroll_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    inner_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor=tk.NW)

    # Populate the inner frame with entry widgets (table columns )
    entries = []
    for header, value in zip(columns, selected_row):
        label = ttk.Label(inner_frame, text=header)
        label.pack(padx=300, pady=5)

        entry_var = tk.StringVar(value=value)
        entry = ttk.Entry(inner_frame, textvariable=entry_var)
        entry.pack(padx=300, pady=5 )

        entries.append(entry_var)

    # Function to update canvas scrolling region
    def _configure_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    inner_frame.bind("<Configure>", _configure_scroll_region)

    # Add a button to submit the changes
    submit_button = ttk.Button(inner_frame, text="Update", command=lambda : get_values(table))
    submit_button.pack(padx=10, pady=20)

    # Bind the canvas scrolling to mousewheel events
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # Function to get the values from the entry widgets
    def get_values(table):
        new_values = [entry.get() for entry in entries]
        print("New Values:", new_values )
        window.destroy()
        frame.destroy()
      
        mysql_con.alter_table(table , new_values , columns ,key_val_cpl)
        record_frame(table)

app = tk.Tk()
app.geometry("1024x768")

style = ttkbootstrap.Style(theme="darkly")
style.theme_use()

create_login_page()
app.mainloop()



