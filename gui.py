from customtkinter import CTkScrollableFrame
import mysql_con
from tkinter import ttk , messagebox
import tkinter as tk
import ttkbootstrap
import json
import webbrowser


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
    result = mysql_con.exec_query(query)
    if isinstance(result, tuple):  # Check if result is a tuple (indicating data query)
        columns, rows = result
        window = tk.Toplevel(app)
        window.geometry("800x600")
        window.title("View Search Results")

        treeframe = ttk.Frame(window)
        treeframe.pack(expand=True , fill='both')

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

    elif result ==True :
        messagebox.showerror(message="Executed successfully")
    else:
        messagebox.showerror(title='Error' , message=result )

    # if headers ==None and rows ==none
def click_on_search_row(db_name , term , table_col_couple):
    table_col_couple.pop()
    columns , rows , primary_key = mysql_con.show_search_records(table_col_couple, term )
    
    window = tk.Toplevel(app)
    window.geometry("800x600")
    window.title("View Search Results")

    treeframe = ttk.Frame(window)
    treeframe.pack(expand=True , fill='both')

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


    treeview.bind('<Double-1>', lambda event , headers=columns: click_on_row(db_name , treeframe,primary_key ,table_col_couple[0] , headers , treeview.item(treeview.selection())['values']))
    
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
    
    def theme_button(button_name , title , padding ) :
        button_name = ttk.Button(master=frame, text=title , style="Hyperlink.TButton" , command= lambda : save_theme_settings(title.split()[0].lower()) )
        button_name.pack(anchor='w' , side='left' , pady=(150,10) , padx=padding)

    theme_button('darkly_label' , "Darkly Theme" , 5)
    theme_button('solar_label' , "Solar Theme" , 5)
    theme_button('superhero_label' , "Superhero Theme" , 5)
    theme_button('Cyborg_label' , "Cyborg Theme" , 5)
    theme_button('Vapor_label' , "Vapor Theme" , 5)
    theme_button('solar_label' , "Morph Theme" , 5)

    doc_button = ttk.Button(master=frame, text="Documentation" , style="Hyperlink.TButton" , command=lambda : webbrowser.open('https://github.com/Baragsen/MySQL-gui'))
    doc_button.pack(anchor='e' , side='right' , pady=(150,10) , padx=5)


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

    table_frame = tk.Canvas(master=notebook )
    table_frame.pack(fill="both" , expand=True)

    y_Scrollbar = ttk.Scrollbar(table_frame , orient="vertical")
    y_Scrollbar.pack(side="right",fill="y")

    table_frame.config(yscrollcommand=y_Scrollbar.set)
    y_Scrollbar.config(command=table_frame.yview)

    inner_frame = tk.Frame(table_frame )
    table_frame.create_window((0, 0) , window=inner_frame, anchor='center' )


    tables = show_db_tables(db_name)
    tables_buttons = [ttk.Button(inner_frame,text=table, command=lambda table=table[0] : db_to_tb(db_name ,notebook,table)).pack(side='top',anchor='center' , fill='x', padx=220, pady=10 ) for table in tables]

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

    operations_tab = ttk.Frame(notebook)
    operations_tab.pack(fill="both" , expand=True)

    operations_frame = ttk.Frame(operations_tab , height=20)
    operations_frame.pack(fill='x' ,expand=True)

    table_name_entry =ttk.Label(operations_frame , text='Create new Table Page' ,font=('Helvetica', 14))
    table_name_entry.pack(side='left' ,padx=(100,20), pady=(10,600))

    # button to get to the table creation page
    create_table_button =ttk.Button(operations_frame , text="Create new Table : " , command=lambda:table_create_page(table_frame))
    create_table_button.pack(side='left' ,padx=100, pady=(10,600))

    notebook.add(operations_tab , text='Operations')

    search_frame = ttk.Frame(notebook)
    search_frame.pack(fill="both" , expand=True)

    search_title_label = ttk.Label(search_frame , text='Search in Database' , font=("Helvetica",24))
    search_title_label.grid(row=0 , column=0 , padx=250 , pady=50)
    
    search_label = ttk.Label(search_frame , text='Value to search for : ', font=("Helvetica",12))
    search_label.grid(row=1 , column=0 , pady=60 ,padx=40 , sticky='w')

    search_term = tk.StringVar()
    search_entry = ttk.Entry(search_frame , textvariable=search_term , width=40)
    search_entry.grid(row=1 , column=0 , pady=60 ,padx=200 , sticky='w')
    
    search_button = ttk.Button(search_frame , text='Search' ,width=25, command=lambda : search_database(db_name, search_term.get()))
    search_button.grid(row=1 , column=0 , pady=60 ,padx=100 , sticky='e')

    def search_database(db_name , term_to_search ):
        search_frame.destroy()

        result_frame = ttk.Frame(notebook)
        result_frame.pack(fill="both" , expand=True)
        search_result = mysql_con.search_database(db_name , term_to_search)
        result_columns = ['Table' , 'Column' , 'matches']
    # Add vertical scrollbar
        tree_y_Scrollbar = ttk.Scrollbar(result_frame , orient="vertical")
        tree_y_Scrollbar.pack(side="right",fill="y")

        tree_x_Scrollbar = ttk.Scrollbar(result_frame , orient='horizontal')
        tree_x_Scrollbar.pack(side='bottom',fill="x")
        
        # Create a Treeview widget
        treeview = ttk.Treeview(result_frame,show='headings',xscrollcommand= tree_x_Scrollbar.set, yscrollcommand= tree_y_Scrollbar.set,  columns=result_columns,height=len(search_result))
        treeview.pack()

        # add the columns as Headers
        for column in result_columns :
            treeview.column(column, anchor="center")
            treeview.heading(column , text=column)


        # Insert data into the treeview
        for row in search_result :
            inner_tuple, element = row[0], row[1]
            inner_elements = [item for item in inner_tuple]
            values_to_insert = inner_elements + [element]
            treeview.insert("" , tk.END , values=values_to_insert)

        tree_y_Scrollbar.config(command=treeview.yview)    
        tree_x_Scrollbar.config(command=treeview.xview)    

        treeview.bind('<Double-1>', lambda event : click_on_search_row(db_name ,term_to_search ,treeview.item(treeview.selection())['values']))


    notebook.add(search_frame , text='Search')

    copy_db = ttk.Frame(notebook)
    copy_db.pack(fill="both" , expand=True)

    copy_label = ttk.Label(copy_db , text='Copy Database' ,  font=("Helvetica",20))
    copy_label.grid(row=0 , column=0 , padx=240 , pady=30,sticky='w')

    db_copy_label = ttk.Label(copy_db , text='Database : ' ,  font=("Helvetica",14))
    db_copy_label.grid(row=1, column=0 , padx=100 , pady=60 ,sticky='w')

    db_copy_to = tk.StringVar()
    db_copy_entry = ttk.Entry(copy_db , textvariable=db_copy_to , width=40)
    db_copy_entry.grid(row=1, column=0 , padx=220 , pady=60,sticky='w')

    copy_button = ttk.Button(copy_db , text='copy' ,command=lambda :mysql_con.copy_db(db_copy_to.get() , get_args(cp_struct.get() ,cp_data.get()) ,create_before.get()))
    copy_button.grid(row=1, column=0 , padx=550, pady=60, sticky='w')

    cp_struct = tk.IntVar()
    cp_data = tk.IntVar()
    create_before = tk.IntVar()

    def get_args(cp_struct, cp_data ):
        options = []
        if cp_struct == 1:
            options.append("--no-data") 
        if cp_data == 1:
            options.append("--no-create-info") 

        return options

    cp_struct_data = tk.Checkbutton(copy_db, text="Structure and data" , command=lambda : deselect_when_selected(cp_struct_only , cp_data_only))
    cp_struct_data.grid(row=2 , column=0 , padx=100, pady=(10,10), sticky='w')

    cp_struct_only = tk.Checkbutton(copy_db , text="Structure only", variable=cp_struct, command=lambda : deselect_when_selected(cp_struct_data , cp_data_only))
    cp_struct_only.grid(row=2 , column=0 , padx=100, pady=(60,10), sticky='w')

    cp_data_only = tk.Checkbutton(copy_db, text="Data Only",variable=cp_data,command=lambda :deselect_when_selected(cp_struct_data,cp_struct_only))
    cp_data_only.grid(row=2 , column=0 , padx=100, pady=(130 ,35), sticky='w')

    create_before_button = tk.Checkbutton(copy_db, variable=create_before ,text="CREATE DATABASE before copying")
    create_before_button.grid(row=2 , column=0 , padx=100, pady=(170,35), sticky='w')

    notebook.add(copy_db , text='Copy Database')

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

    sql_dump_frame = ttk.Frame(notebook)
    sql_dump_frame.pack(expand=True ,fill='both')

    sql_dump_title = ttk.Label(sql_dump_frame , text='Dump Database' ,  font=("Helvetica",20))
    sql_dump_title.grid(row=0 , column=0 , padx=240 , pady=30,sticky='w')

    dump_path_label = ttk.Label(sql_dump_frame , text='Path : ' ,  font=("Helvetica",14))
    dump_path_label.grid(row=1, column=0 , padx=100 , pady=60 ,sticky='w')

    dump_path= tk.StringVar()
    dump_path_entry = ttk.Entry(sql_dump_frame , textvariable=dump_path , width=40)
    dump_path_entry.grid(row=1, column=0 , padx=220 , pady=60,sticky='w')

    dump_button = ttk.Button(sql_dump_frame , text='dump' ,command=lambda : mysql_con.sql_dump(dump_path.get() , dump_arg(var_struct_only, var_data_only, var_add_routines , var_add_events) ))
    dump_button.grid(row=1, column=0 , padx=550, pady=60, sticky='w')

    var_struct_data = tk.IntVar()
    var_struct_only = tk.IntVar()
    var_data_only = tk.IntVar()
    var_add_routines = tk.IntVar()
    var_add_events = tk.IntVar()

    def dump_arg(var_struct_only, var_data_only, var_add_routines , var_add_events):
        options = []
        if var_struct_only.get() == 1:
            options.append("--no-data") 
        if var_data_only.get() == 1:
            options.append("--no-create-info") 
        if var_add_routines.get() == 1:
            options.append("--routines")
        if var_add_events.get() == 1:
            options.append("--events")  

        return options

    def deselect_when_selected(*args):
        for arg in args :
            arg.deselect()

    struct_data = tk.Checkbutton(sql_dump_frame, text="Structure and data" ,variable=var_struct_data, command=lambda : deselect_when_selected(struct_only , data_only))
    struct_data.grid(row=2 , column=0 , padx=100, pady=(10,10), sticky='w')

    struct_only = tk.Checkbutton(sql_dump_frame , text="Structure only", variable=var_struct_only, command=lambda : deselect_when_selected(struct_data , data_only))
    struct_only.grid(row=2 , column=0 , padx=100, pady=(60,10), sticky='w')

    data_only = tk.Checkbutton(sql_dump_frame, text="Data Only",variable=var_data_only,command=lambda : deselect_when_selected(struct_data , struct_only))
    data_only.grid(row=2 , column=0 , padx=100, pady=(130 ,35), sticky='w')

    add_routines = tk.Checkbutton(sql_dump_frame,variable=var_add_routines, text="Add Routines")
    add_routines.grid(row=2 , column=0 , padx=100, pady=(180,10), sticky='w')

    add_events = tk.Checkbutton(sql_dump_frame,variable=var_add_events, text="Add Events")
    add_events.grid(row=2 , column=0 , padx=100, pady=(220, 10), sticky='w')

    notebook.add(child=sql_dump_frame ,text='SQL Dump')

    db_import = ttk.Frame(notebook )
    db_import.pack(fill="both" , expand=True )

    sql_import = ttk.Label(db_import , text='Import Database' ,  font=("Helvetica",30))
    sql_import.grid(row=0 , column=0 , padx=230 , pady=30,sticky='w')

    sql_import_label = ttk.Label(db_import , text='Path : ' ,  font=("Helvetica",14))
    sql_import_label.grid(row=1, column=0 , padx=100 , pady=60 ,sticky='w')

    import_path= tk.StringVar()
    import_path_label = ttk.Entry(db_import , textvariable=import_path , width=40)
    import_path_label.grid(row=1, column=0 , padx=220 , pady=60,sticky='w')

    import_button = ttk.Button(db_import , text='import' ,command=lambda : mysql_con.sql_import(import_path.get()))
    import_button.grid(row=1, column=0 , padx=550, pady=60, sticky='w')

    notebook.add(db_import , text='Import')

    triggers_frame = ttk.Frame(notebook)
    triggers_frame.pack(fill="both" , expand=True)
    notebook.add(triggers_frame , text='Triggers')
    

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

    search_frame = ttk.Frame(notebook)
    search_frame.pack(expand=True ,fill='both')



    search_title_label = ttk.Label(search_frame , text='Search in Table' , font=("Helvetica",24))
    search_title_label.grid(row=0 , column=0 , padx=250 , pady=50)
    
    search_label = ttk.Label(search_frame , text='Value to search for : ', font=("Helvetica",12))
    search_label.grid(row=1 , column=0 , pady=60 ,padx=40 , sticky='w')

    search_term = tk.StringVar()
    search_entry = ttk.Entry(search_frame , textvariable=search_term , width=40)
    search_entry.grid(row=1 , column=0 , pady=60 ,padx=200 , sticky='w')
    
    search_button = ttk.Button(search_frame , text='Search' ,width=25, command=lambda : search_table(table ,db_name, search_term.get()))
    search_button.grid(row=1 , column=0 , pady=60 ,padx=80, sticky='e')

    def search_table(table ,db_name , term_to_search ):
        search_frame.destroy()

        result_frame = ttk.Frame(notebook)
        result_frame.pack(fill="both" , expand=True)
        headers , rows = mysql_con.search_table(term_to_search, db_name , table)
        
         # Add vertical scrollbar
        tree_y_Scrollbar = ttk.Scrollbar(result_frame , orient="vertical")
        tree_y_Scrollbar.pack(side="right",fill="y")

        tree_x_Scrollbar = ttk.Scrollbar(result_frame , orient='horizontal')
        tree_x_Scrollbar.pack(side='bottom',fill="x")
        
        # Create a Treeview widget
        treeview = ttk.Treeview(result_frame,show='headings',xscrollcommand= tree_x_Scrollbar.set, yscrollcommand= tree_y_Scrollbar.set,  columns=headers,height=len(rows))
        treeview.pack()

        # add the columns as Headers
        for column in headers :
            treeview.column(column, anchor="center")
            treeview.heading(column , text=column)


        # Insert data into the treeview
        for row in rows :
            treeview.insert("" , tk.END , values=row)

        tree_y_Scrollbar.config(command=treeview.yview)    
        tree_x_Scrollbar.config(command=treeview.xview) 
         
    notebook.add(child=search_frame ,text='Search')

    insert_frame = ttk.Frame(notebook)
    insert_frame.pack(expand=True ,fill='both')
    notebook.add(child=insert_frame ,text='Insert')

    drop_table_frame = ttk.Frame(notebook)
    drop_table_frame.pack(expand=True ,fill='both')
    notebook.add(child=drop_table_frame ,text='Drop Table')
    
    rename_table_frame = ttk.Frame(notebook)
    rename_table_frame.pack(expand=True ,fill='both')
    notebook.add(child=rename_table_frame ,text='Rename Table')

    empty_table_frame = ttk.Frame(notebook)
    empty_table_frame.pack(expand=True ,fill='both')
    notebook.add(child=empty_table_frame ,text='Empty Table')

    priv_table_frame = ttk.Frame(notebook)
    priv_table_frame.pack(expand=True ,fill='both')
    notebook.add(child=priv_table_frame ,text='Priveleges')

    
    sql_dump_frame = ttk.Frame(notebook)
    sql_dump_frame.pack(expand=True ,fill='both')
    notebook.add(child=sql_dump_frame ,text='SQL Dump')

    data_vis_frame = ttk.Frame(notebook)
    data_vis_frame.pack(expand=True ,fill='both')
    notebook.add(child=data_vis_frame ,text='Visualize Data')

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


def save_theme_settings(theme_name):
    with open('theme_settings.json', 'w') as file:
        json.dump({'theme': theme_name}, file)

def load_theme_settings():
    try:
        with open('theme_settings.json', 'r') as file:
            settings = json.load(file)
            return settings['theme']
    except FileNotFoundError:
        return None
    
app = tk.Tk()
app.geometry("1024x768")

saved_theme = load_theme_settings()
if saved_theme:
    style = ttkbootstrap.Style(theme=saved_theme)
else:
    style = ttkbootstrap.Style(theme="darkly")
style.theme_use()
create_login_page()
app.mainloop()



