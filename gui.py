import customtkinter
import mysql_con
from tkinter import ttk
import tkinter as tk
import ttkbootstrap

def login_success(frame , hostname  ,port ,username , password ) :
    con = mysql_con.handle_login(hostname= 'localhost',username='root',passw= 'root' , port="3306") 
        # hostname= hostname ,username= username ,passw= password , port=port 
    if con == True :
        frame.destroy()
        database_menu()


def db_creation_success(db_create_entry):
    cr = mysql_con.create_database(db_create_entry)
    if cr == True :
        database_menu()

def show_db_tables(db_name):
    con = mysql_con.handle_login(hostname= mysql_con.hostname ,username= mysql_con.username,passw=mysql_con.passowrd , port=mysql_con.port , db=db_name) 
    if con == True :
        return mysql_con.show_tables(db_name)
    

def drop_db(frame,db_name):
    dropped = mysql_con.drop_db(db_name)
    if dropped ==True :
        frame.destroy()
        database_menu()

def show_columns(table_frame,table):
    table_frame.destroy()
    columns_frame(table)

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


def database_menu():
    menu_frame = customtkinter.CTkScrollableFrame(master=app)
    menu_frame.grid(row=0, column=0 , sticky="ns")
    app.grid_rowconfigure(0, weight=1) 

    new_db = tk.StringVar()
    db_create_entry = ttk.Entry(menu_frame, textvariable=new_db )
    db_create_entry.pack(pady=(60,0)) 

    create_database_button = ttk.Button(menu_frame,text="Create a new Database" ,command=lambda:db_creation_success(new_db.get()))
    create_database_button.pack(side="top", pady=(5,50))

    databases = mysql_con.show_databases()
    databases_buttons = [ttk.Button(menu_frame,text=database , command=lambda db=database: tables_frame(db[0])).pack(side="top", pady=10) for database in databases]


def tables_frame(db_name):
    table_frame = customtkinter.CTkScrollableFrame(master=app)
    table_frame.grid(row=0, column=1 , sticky="nswe")
    app.grid_columnconfigure(1, weight=1) 
    app.grid_rowconfigure(0, weight=1)


    drop_button_frame = ttk.Frame(master=table_frame)
    drop_button_frame.pack(anchor="ne", padx=10, pady=10)

    create_table_frame = ttk.Frame(master=table_frame)
    create_table_frame.pack(anchor="ne" ,padx=10 , pady=15)

    create_table_button =ttk.Button(create_table_frame , text="Create new Table" , command=lambda:table_create_page((table_frame , drop_button_frame , create_table_frame)))
    create_table_button.pack()

    drop_db_button = ttk.Button(drop_button_frame , text="Drop database" , command=lambda: drop_db(table_frame,db_name))
    drop_db_button.pack()

    tables = show_db_tables(db_name)

    tables_buttons = [ttk.Button(table_frame,text=table, command=lambda table=table[0] : show_columns(table_frame,table)).pack(side="top", pady=10) for table in tables]

def table_create_page(frames):
    for frame in frames :
        frame.destroy()

    table_name_frame = customtkinter.CTkFrame(app)
    table_name_frame.grid(column= 1  , row=0 , sticky = "nswe")

    app.grid_rowconfigure(0, weight=1) 
    app.grid_columnconfigure(1, weight=1) 

    create_column_frame = customtkinter.CTkFrame(table_name_frame)
    create_column_frame.grid(column= 0  , row=0 , sticky = "ew" , columnspan=2)
    table_name_frame.grid_columnconfigure(0, weight=1)  

    treeframe = ttk.Frame(table_name_frame)
    treeframe.grid(column= 1  , row=2 , sticky = "nswe" , columnspan=2)
    table_name_frame.grid_rowconfigure(2, weight=1)  
    table_name_frame.grid_columnconfigure(1, weight=1)

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

    execute_button = ttk.Button( create_column_frame , text='Execute' , command=...  )
    execute_button.grid(row=0 , column=3 , padx=140)

    tree_y_Scrollbar.config(command=treeview.yview)
    tree_x_Scrollbar.config(command=treeview.xview)


    def add_column():
        column_name = tk.StringVar()
        option = tk.StringVar()
        type_values = ["TINYINT" , "SMALLINT" , "MEDIUMINT" , "BIGINT" , "DECIMAL" , "FLOAT" , "DOUBLE" , "REAL" , "BIT" , "BOOLEAN" , "DATE" , "SERIAL" , "DATETIME" , "TIMESTAMP" , "TIME", "YEAR" , "CHAR" , "VARCHAR" , "TINYTEXT" , "TEXT" , "MEDIUMTEXT" , "LONGTEXT" , "BINARY" , "VARBINARY" , "ENUM" , "SET" , "JSON"]
        
        # incomplete

        row = [ttk.Entry(create_column_frame, textvariable=column_name) , ttk.OptionMenu(create_column_frame, variable=option)]
        treeview.config(height=int(treeview.cget("height"))+1)
        treeview.insert("" , tk.END , values=...)

    table_label = ttk.Label(create_column_frame , text='Table Name : ')
    table_label.grid(row=0 , column=0 , padx=30 , pady=30 )
    table_name = tk.StringVar()
    table_name_entry = ttk.Entry(create_column_frame, textvariable=table_name )
    table_name_entry.grid(row=0 , column=1 , padx=(5,30) , pady=30)

    column_number = ttk.Button(create_column_frame, text="Add column" , command=lambda: add_column())
    column_number.grid(row=0 , column=2 , padx=30 , pady=30)


def columns_frame(table):
    columns , rows = mysql_con.show_table_records(table)
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

    for column in columns :
        treeview.column(column, anchor="center")
        treeview.heading(column , text=column)

    # Insert data into the treeview
    for row in rows :
        treeview.insert("" , tk.END , values=row)

    tree_y_Scrollbar.config(command=treeview.yview)
    tree_x_Scrollbar.config(command=treeview.xview)

    treeview.bind('<Double-1>', lambda event , headers=columns: clicker(headers , treeview.item(treeview.selection())['values']))

def clicker(headers , selected_row):
    window = tk.Toplevel(app)
    window.grab_set()
    window.geometry("800x600")
    print("Headers:", headers)
    print("Selected Row:", selected_row)


app = tk.Tk()
app.geometry("1024x768")
style = ttkbootstrap.Style(theme="darkly")
style.theme_use()



create_login_page()

app.mainloop()



