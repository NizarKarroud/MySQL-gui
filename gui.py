from customtkinter import CTkScrollableFrame
import mysql_con
from tkinter import ttk , messagebox
import tkinter as tk
import ttkbootstrap

frame_to_destroy = []

""" The Login Logic"""
def login_success(frame , hostname  ,port ,username , password ) :
    connection = mysql_con.handle_login(hostname= 'localhost',username='root',passw= 'root' , port="3306") 
        # hostname= hostname ,username= username ,passw= password , port=port 
    if connection == True :
        frame.destroy()
        app.unbind("<Return>")
        database_menu()
    else : 
        messagebox.showerror(title='Error' , message=connection )

"""To create a Database"""
def db_create(db_create_entry):
    db_creation = mysql_con.create_database(db_create_entry)
    if db_creation == True :
        database_menu()
    else :
        messagebox.showerror(title='Error' , message=db_creation )

"""Returns the Tables in a specific Database """
def show_db_tables(db_name):
    connection = mysql_con.handle_login(hostname= mysql_con.hostname ,username= mysql_con.username,passw=mysql_con.passowrd , port=mysql_con.port , db=db_name) 
    if connection == True :
        return mysql_con.show_tables(db_name)
    else : 
        messagebox.showerror(title='Error' , message=connection )

""" Function to Drop database"""
def drop_db(frame,db_name):
    dropped = mysql_con.drop_db(db_name)
    if dropped ==True :
        frame.destroy()
        database_menu()
    else : 
        messagebox.showerror(title='Error' , message=dropped )

"""Transition from database to specific table"""
def db_to_tb(db_name , notebook ,table):
    notebook.destroy()
    table_tabs(db_name , table)

""" For the Sql Query Tab"""
def sql_query(query):
    mysql_con.exec_query(query)
    # work on the query in th mysql_con file

""" What happens when you click on a row (Record) """
def click_on_row(db_name , frame,primary_keys,table ,headers , selected_row):
    row_data = list(zip(headers,selected_row))


    keys_values_couples = []
    for couple in row_data :
        for key in primary_keys :
            if couple[0] == key :
                keys_values_couples.append(couple)

    update_row_window(db_name , frame ,table , headers , selected_row ,keys_values_couples)

""" The Login Page """
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

    def on_enter(event):
        login_success(frame, hostname.get(), port.get(), username.get(), password.get())

    app.bind("<Return>", on_enter)
    
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
    databases_buttons = [ttk.Button(menu_frame,text=database , command=lambda db=database: tables_frame(db[0])).pack(fill='both',side="top", pady=10) for database in databases]

""" Frame that contains the tabs for database Operations and Tables """
def tables_frame(db_name):
    for frame in frame_to_destroy :
        frame.destroy()

    #Creating tabs
    notebook = ttk.Notebook(app)
    notebook.grid(row=0, column=1 , sticky="nswe" , padx=10 , pady=10)
    app.grid_columnconfigure(1, weight=1) 
    app.grid_rowconfigure(0, weight=1)

    table_frame = tk.Canvas(master=notebook)
    table_frame.pack(fill="both" , expand=True)

    y_Scrollbar = ttk.Scrollbar(table_frame , orient="vertical")
    y_Scrollbar.pack(side="right",fill="y")

    table_frame.config(yscrollcommand=y_Scrollbar.set)
    y_Scrollbar.config(command=table_frame.yview)

    inner_frame = tk.Frame(table_frame , highlightbackground="black", highlightthickness=2  )
    table_frame.create_window((0, 0) , window=inner_frame, anchor='nw')
    # inner_frame.pack(expand=True , fill="both")

    tables = show_db_tables(db_name)
    tables_buttons = [ttk.Button(inner_frame,text=table, command=lambda table=table[0] : db_to_tb(db_name ,notebook,table)).pack(side='top',anchor='center',fill='x',pady=10 ) for table in tables]

    inner_frame.update_idletasks()
    table_frame.config(scrollregion=table_frame.bbox("all"))


    # Bind the canvas scrolling to mousewheel events
    def _on_mousewheel(event):
        table_frame.yview_scroll(int(-1 * (event.delta / 120)), "units")

    table_frame.bind_all("<MouseWheel>", _on_mousewheel)
    notebook.add(table_frame , text='Tables')

    sql_frame = ttk.Frame(notebook)
    sql_frame.pack(fill="both" , expand=True)

    text_box = tk.Text(sql_frame)
    text_box.pack(padx=20 , pady= (20,10) ,fill='both' , expand=True)

    exec_button = ttk.Button(sql_frame, text='Execute' , command= lambda : sql_query(text_box.get(1.0, "end-1c")))
    exec_button.pack(pady=(10,30),padx=20 , side='right')
    notebook.add(sql_frame , text='SQL')

    operations_frame = ttk.Frame(notebook)
    operations_frame.pack(fill="both" , expand=True)
    notebook.add(operations_frame , text='Operations')

    copy_frame = ttk.Frame(notebook)
    copy_frame.pack(fill="both" , expand=True)
    notebook.add(copy_frame , text='Search')

    migrate_frame = ttk.Frame(notebook)
    migrate_frame.pack(fill="both" , expand=True)
    notebook.add(migrate_frame , text='Copy Database')


    priv_frame = ttk.Frame(notebook)
    priv_frame.pack(fill="both" , expand=True)
    notebook.add(priv_frame , text='User Privileges')

    export_frame = ttk.Frame(notebook )
    export_frame.pack(fill="both" , expand=True , padx=30 , pady= 30)

    export_label = ttk.Label(export_frame , text="Export Database's Tables" , font=("Helvetica",20))
    export_label.grid(row=0 , column=0 , padx=240 , pady=30)

    path_label = ttk.Label(export_frame , text="Path : ")
    path_label.grid(row= 1 , column=0 , sticky="w" , padx=80 , pady=80 )
    
    path_var = tk.StringVar()
    path_entry = ttk.Entry(export_frame , textvariable=path_var , width=60)
    path_entry.grid(row= 1 , column=0 , sticky="w" , padx=(150,50) , pady=80)

    table_list_box = tk.Listbox(export_frame, selectmode=tk.MULTIPLE , height=25 , width=40)

    export_options = ['csv' , 'html']
    type_var = tk.StringVar()
    type_var.set(export_options[0])

    export_type = ttk.Combobox(export_frame , textvariable=type_var , values=export_options , state='readonly')
    export_type.grid(row= 1 , column=0 , sticky="e" , padx=(110,), pady=80)

    export_button = ttk.Button(export_frame , text='export' ,command=lambda : mysql_con.export_database(db_name,table_list=[table_list_box.get(idx) for idx in table_list_box.curselection()], path=rf"{path_var.get()}" , extension=type_var.get()))
    export_button.grid(row= 1 , column=0 , sticky="e" , padx=(40,), pady=80)

    for option in mysql_con.show_tables(db_name):
        table_list_box.insert(tk.END, option[0])
    table_list_box.grid(row=2 , column=0 ,sticky="w", padx=80)

    def select_all():
        deselect_checkbox.deselect()
        table_list_box.selection_set(0, tk.END)

    def deselect_all():
        select_checkbox.deselect()
        table_list_box.selection_clear(0, tk.END)

    deselect_checkbox = tk.Checkbutton(export_frame, text="Deselect all tables", command=lambda : deselect_all())
    deselect_checkbox.grid(row=2 , column=0 ,sticky="e", padx=(30 ,180) , pady=(10,320))
    select_checkbox = tk.Checkbutton(export_frame, text="Select all tables", command=lambda : select_all())
    select_checkbox.grid(row=2, column=0 ,sticky="e", padx=(30,315) ,pady=(10 ,320))

    notebook.add(export_frame , text='Export')

    migrate_frame = ttk.Frame(notebook)
    migrate_frame.pack(fill="both" , expand=True)
    notebook.add(migrate_frame , text='Database migration')
    
    # text_box = tk.Text(export_frame)
    # text_box.pack(padx=20 , pady= (20,10) ,fill='both' , expand=True)

    # exec_button = ttk.Button(export_frame, text='Execute' , command= lambda : ...))
    # exec_button.pack(pady=(10,30),padx=20 , side='right')




    # # button to get to the table creation page
    # create_table_button =ttk.Button(table_frame , text="Create new Table" , command=lambda:table_create_page(table_frame))
    # create_table_button.pack(anchor="ne" ,padx=10 , pady=15)

    # # Button to drop the database
    # drop_db_button = ttk.Button(table_frame , text="Drop database" , command=lambda: drop_db(table_frame,db_name))
    # drop_db_button.pack(anchor="ne" ,padx=10 , pady=15)

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

""" TABLE Tabs """
def table_tabs(db_name , table):
    notebook = ttk.Notebook(app)
    notebook.grid(row=0, column=1 , sticky="nswe" , padx=10 , pady=10)
    app.grid_columnconfigure(1, weight=1) 
    app.grid_rowconfigure(0, weight=1)   
    
    treeframe = ttk.Frame(notebook)
    treeframe.grid(column= 0  , row=0 , sticky = "nswe")
    notebook.grid_rowconfigure(0, weight=1) 
    notebook.grid_columnconfigure(0, weight=1) 

    columns , rows , primary_key = mysql_con.show_table_records(table)

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


    treeview.bind('<Double-1>', lambda event , headers=columns: click_on_row(db_name , treeframe,primary_key ,table , headers , treeview.item(treeview.selection())['values']))

    frame_to_destroy.append(treeframe) 

    notebook.add(child=treeframe ,text='Records')


""" UPDATE row values """

def update_row_window(db_name , frame ,table , columns, selected_row , key_val_cpl):    
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
    submit_button = ttk.Button(inner_frame, text="Update", command=lambda : get_values(db_name , table))
    submit_button.pack(padx=10, pady=20)

    # Bind the canvas scrolling to mousewheel events
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # Function to get the values from the entry widgets
    def get_values(db_name  ,table):
        new_values = [entry.get() for entry in entries]
        window.destroy()
        frame.destroy()
      
        mysql_con.alter_table(db_name,table , new_values , columns ,key_val_cpl)
        table_tabs(db_name , table)

app = tk.Tk()
app.geometry("1024x768")

style = ttkbootstrap.Style(theme="darkly")
style.theme_use()

create_login_page()
app.mainloop()



