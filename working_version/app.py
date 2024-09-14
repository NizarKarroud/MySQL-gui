from customtkinter import CTkScrollableFrame
import mysql_con
from tkinter import ttk , messagebox
import tkinter as tk
import ttkbootstrap
import json
import webbrowser


frame_to_destroy = []

""" The Login Logic"""
def login_success(frame , hostname  ,port ,username , password , auth_plugin ) :
    connection = mysql_con.handle_login(hostname= hostname ,username= username ,passw= password , port=port , auth_plugin=auth_plugin) 
    if connection == True :
        frame.destroy()
        app.unbind("<Return>")
        database_menu()


"""To create a Database"""
def db_create(menu_frame , db_create_entry):
    db_creation = mysql_con.create_database(db_create_entry)
    if db_creation == True :
        menu_frame.destroy()
        database_menu()

"""Returns the Tables in a specific Database """
def show_db_tables(db_name):
    connection = mysql_con.handle_login(hostname= mysql_con.hostname ,username= mysql_con.username,passw=mysql_con.password , port=mysql_con.port , db=db_name ,auth_plugin=mysql_con.auth_plugin) 
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

    operations_on_row(db_name , frame ,table , headers , selected_row ,keys_values_couples)

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

    auth_label = ttk.Label(master=frame, text="Auth plugin :")
    auth_label.pack(pady=10)

    auth = tk.StringVar()
    auth_entry = ttk.Entry(frame, textvariable=auth )
    auth_entry.pack(padx=10, pady=10)

    login_button = ttk.Button(master=frame, text="Login", command=lambda: login_success(frame, hostname.get(), port.get(), username.get(), password.get() , auth.get()))
    login_button.pack(pady=10)

    def on_enter(event):
        login_success(frame, hostname.get(), port.get(), username.get(), password.get() , auth.get())

    app.bind("<Return>", on_enter)
    
    def theme_button(button_name , title , padding ) :
        button_name = ttk.Button(master=frame, text=title , style="Hyperlink.TButton" , command= lambda : save_theme_settings(title.split()[0].lower()) )
        button_name.pack(anchor='w' , side='left' , pady=(80,10) , padx=padding)

    theme_button('darkly_label' , "Darkly Theme" , 5)
    theme_button('solar_label' , "Solar Theme" , 5)
    theme_button('superhero_label' , "Superhero Theme" , 5)
    theme_button('Cyborg_label' , "Cyborg Theme" , 5)
    theme_button('Vapor_label' , "Vapor Theme" , 5)
    theme_button('solar_label' , "Morph Theme" , 5)

    doc_button = ttk.Button(master=frame, text="Documentation" , style="Hyperlink.TButton" , command=lambda : webbrowser.open('https://github.com/NizarKarroud/MySQL-gui'))
    doc_button.pack(anchor='e' , side='right' , pady=(80,10) , padx=5)

""" The Database Menu and Create new Database functionality """
def database_menu():
    menu_frame = CTkScrollableFrame(master=app)
    menu_frame.grid(row=0, column=0 , sticky="ns")
    app.grid_rowconfigure(0, weight=1) 

    new_db = tk.StringVar()
    db_create_entry = ttk.Entry(menu_frame, textvariable=new_db )
    db_create_entry.pack(pady=(60,0)) 

    create_database_button = ttk.Button(menu_frame,text="Create a new Database" ,command=lambda:db_create(menu_frame,new_db.get()))
    create_database_button.pack(side="top", pady=(10,40))
    
    databases = mysql_con.show_databases()
    databases_buttons = [ttk.Button(menu_frame,text=database , command=lambda db=database: tables_frame(menu_frame,db[0])).pack(fill='both',side="top", pady=10) for database in databases]


""" Frame that contains the tabs for database Operations and Tables """
def tables_frame(menu_frame , db_name):
    for frame in frame_to_destroy :
        frame.destroy()

    #Creating tabs
    notebook = ttk.Notebook(app)
    notebook.grid(row=0, column=1 , sticky="nswe" , padx=10 , pady=10)
    app.grid_columnconfigure(1, weight=1) 
    app.grid_rowconfigure(0, weight=1)

    table_frame = tk.Canvas(master=notebook )
    table_frame.pack(fill="both" , expand=True)

    # y_Scrollbar = ttk.Scrollbar(table_frame , orient="vertical")
    # y_Scrollbar.pack(side="right",fill="y")

    # table_frame.config(yscrollcommand=y_Scrollbar.set)
    # y_Scrollbar.config(command=table_frame.yview)

    inner_frame = CTkScrollableFrame(table_frame )
    inner_frame.pack(fill="both" , expand=True)

    # table_frame.create_window((0, 0) , window=inner_frame, anchor='center' )


    tables = show_db_tables(db_name)
    tables_buttons = [ttk.Button(inner_frame,text=table, command=lambda table=table[0] : db_to_tb(db_name ,notebook,table)).pack(side='top',anchor='center' , fill='x', padx=220, pady=10 ) for table in tables]

    # inner_frame.update_idletasks()
    # table_frame.config(scrollregion=table_frame.bbox("all"))

    # # Bind the canvas scrolling to mousewheel events
    # def _on_mousewheel(event):
    #     table_frame.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # table_frame.bind_all("<MouseWheel>", _on_mousewheel)
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

    create_table_frame = ttk.Frame(operations_frame, borderwidth=10, relief="solid", height=100)
    create_table_frame.pack(fill='x', padx=10, pady=(30, 0) , ipady=70)

    table_name_entry =ttk.Label(create_table_frame , text='Create new Table Page' ,font=('Helvetica', 14))
    table_name_entry.pack(side='left' ,padx=100)

    # button to get to the table creation page
    create_table_button =ttk.Button(create_table_frame , text="Create new Table " , command=lambda:table_create_page())
    create_table_button.pack(side='left' ,padx=100)

    rename_frame = ttk.Frame(operations_frame, borderwidth=10, relief="solid", height=100)
    rename_frame.pack(fill='x', padx=10, pady=(30, 0) , ipady=70)

    new_name = tk.StringVar()
    new_name_entry = ttk.Entry(rename_frame, textvariable=new_name, width=60)
    new_name_entry.pack(side='left', padx=50)

    rename_database_button = ttk.Button(rename_frame, text="Rename Database", width=50, command=lambda : mysql_con.rename_database(db_name , new_name.get()))
    rename_database_button.pack(side='right', padx=50)

    drop_database_frame = ttk.Frame(operations_frame, borderwidth=10, relief="solid", height=100)
    drop_database_frame.pack(fill='x', padx=10, pady=(30, 0),ipady=70)

    drop_label = ttk.Label(drop_database_frame, text="Drop Database " , font=('Helvetica' , 12))
    drop_label.pack(side='left',pady=10 , padx =30)

    drop_database_button = ttk.Button(drop_database_frame, text="Drop ", width=40, command= lambda : drop_db(menu_frame , db_name))
    drop_database_button.pack(side='left',pady=10 , padx =60)

    notebook.add(operations_frame , text='Operations')

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

    def copy_function():
        mysql_con.copy_db(db_copy_to.get() , get_args(cp_struct.get() ,cp_data.get()) ,create_before.get())
        menu_frame.destroy()
        database_menu()

    copy_button = ttk.Button(copy_db , text='copy' ,command= lambda : copy_function())
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

    # priv_frame = ttk.Frame(notebook)
    # priv_frame.pack(fill="both" , expand=True)
    # notebook.add(priv_frame , text='User Privileges')

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
    def browse_folder():
        folder_selected = tk.filedialog.askdirectory()
        dump_path.set(folder_selected)
        
    browse_button = tk.Button(sql_dump_frame, text="Browse", command=browse_folder)
    browse_button.grid(row=1, column=0 , padx=550, pady=60, sticky='w')


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

    sql_import = ttk.Label(db_import , text='Import Into Database' ,  font=("Helvetica",30))
    sql_import.grid(row=0 , column=0 , padx=230 , pady=30,sticky='w')

    sql_import_label = ttk.Label(db_import , text='Path : ' ,  font=("Helvetica",14))
    sql_import_label.grid(row=1, column=0 , padx=100 , pady=60 ,sticky='w')

    import_path= tk.StringVar()
    import_path_label = ttk.Entry(db_import , textvariable=import_path , width=40)
    import_path_label.grid(row=1, column=0 , padx=220 , pady=60,sticky='w')

    import_button = ttk.Button(db_import , text='import' ,command=lambda : mysql_con.sql_import(import_path.get()))
    import_button.grid(row=1, column=0 , padx=550, pady=60, sticky='w')

    notebook.add(db_import , text='Import')

    triggers_frame = ttk.Frame(notebook ,borderwidth=10, relief="solid" )
    triggers_frame.pack(fill="both" , expand=True, padx=30 , pady=30)

    trigger_name_label = ttk.Label(triggers_frame, text='Trigger name :' , font=("Helvetica",14))
    trigger_name_label.grid(row=0, column=0, sticky='w' ,pady=20, padx=(100,20))

    trigger_name = tk.StringVar()
    trigger_name_entry = ttk.Entry(triggers_frame ,textvariable=trigger_name, width=35)
    trigger_name_entry.grid(row=0, column=1, padx=(20,100), pady=20)

    table_label = ttk.Label(triggers_frame, text='Table :' , font=("Helvetica",14))
    table_label.grid(row=1, column=0, sticky='w', pady=20, padx=(100,20))
    
    table_choice = tk.StringVar()
    trigger_tables = ttk.Combobox(triggers_frame, textvariable=table_choice, values=[table[0] for table in tables], state='readonly' ,width=27)
    trigger_tables.grid(row=1, column=1, padx=10, pady=5)

    time_label = ttk.Label(triggers_frame, text='Time :' , font=("Helvetica",14))
    time_label.grid(row=2, column=0, sticky='w' ,pady=20, padx=(100,20))

    time = tk.StringVar()
    time_choice = ttk.Combobox(triggers_frame, textvariable=time, values=['BEFORE', 'AFTER'], state='readonly', width=27)
    time_choice.grid(row=2, column=1, padx=10, pady=5)

    event_label = ttk.Label(triggers_frame, text='Event :' , font=("Helvetica",14))
    event_label.grid(row=3, column=0, sticky='w',pady=20, padx=(100,20))
    
    event = tk.StringVar()
    event_choice = ttk.Combobox(triggers_frame, textvariable=event, values=['INSERT', 'UPDATE', 'DELETE'], state='readonly', width=27)
    event_choice.grid(row=3, column=1, padx=10, pady=5)

    definition_label = ttk.Label(triggers_frame, text='Definition :', font=("Helvetica",14))
    definition_label.grid(row=4, column=0, sticky='nw' , pady=60 , padx=(100,20))

    definition_text = tk.Text(triggers_frame, height=20, width=60)
    definition_text.grid(row=4, column=1, padx=10, pady=10, sticky='nw')

    create_trigger = ttk.Button(triggers_frame , text='Create' , command= lambda :mysql_con.trigger(trigger_name.get() ,time.get() , event.get() , table_choice.get() , definition_text.get(1.0, "end-1c")))
    create_trigger.grid(row=5 , column=3 , sticky='se' , padx=10 , pady=20)

    notebook.add(triggers_frame , text='Triggers')
     
""" TABLE CREATION PAGE """
def table_create_page():

    window = tk.Toplevel(app)
    window.geometry("800x600")
    window.title("Create Table Window")

    # main frame
    table_name_frame = ttk.Frame(window)
    table_name_frame.grid(column= 1  , row=0 , sticky = "nswe")
    window.grid_rowconfigure(0, weight=1) 
    window.grid_columnconfigure(1, weight=1) 

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

    columns = ["Name" , "Type" , "Length/Values" , "Null", "Index" , "Reference", 'A_I' ] 
    # Create a Treeview widget
    treeview = ttk.Treeview(treeframe,show='headings', xscrollcommand=tree_x_Scrollbar.set ,yscrollcommand= tree_y_Scrollbar.set,height=1 , columns=columns)
    treeview.pack()

    for column in columns :
        treeview.column(column, anchor="center")
        treeview.heading(column , text=column)

    # the table create button
    execute_button = ttk.Button( create_column_frame , text='Execute' , command= lambda : mysql_con.create_table(table_name.get() ,[treeview.item(row, 'values') for row in treeview.get_children()]) )
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
        root = tk.Toplevel()
        root.title("Column FORM")
        root.geometry("400x300")


        label_name = tk.Label(root, text="Name")
        label_name.grid(row=0, column=0, padx=5, pady=5, sticky='e')

        label_type = tk.Label(root, text="Type")
        label_type.grid(row=1, column=0, padx=5, pady=5, sticky='e')

        label_length = tk.Label(root, text="Length/Values")
        label_length.grid(row=2, column=0, padx=5, pady=5, sticky='e')

        label_index = tk.Label(root, text="Index")
        label_index.grid(row=3, column=0, padx=5, pady=5, sticky='e')

        ref_label = tk.Label(root, text="Reference")

        name_entry = tk.Entry(root)
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        length_values_entry = tk.Entry(root)
        length_values_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        reference_entry = tk.Entry(root)

        type_list = ["TINYINT" , "SMALLINT" , "MEDIUMINT" , "INT", "BIGINT" , "DECIMAL" , "FLOAT" , "DOUBLE" , "REAL" 
        , "BIT" , "BOOLEAN" , 
        "DATE" , "SERIAL" , "DATETIME" , "TIMESTAMP" , "TIME", "YEAR" , 
        "CHAR" , "VARCHAR" , "TINYTEXT" , "TEXT" , "MEDIUMTEXT" , "LONGTEXT" , 
        "BINARY" , "VARBINARY" ,
        "TINYBLOB" , "BLOB" , "MEDIUMBLOB" , "LONGBLOB",
        "ENUM" , "SET" , "JSON"]

        type_column = tk.StringVar()
        type_combobox = ttk.Combobox(root,textvariable=type_column, values=type_list, state='readonly')
        type_combobox.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        type_combobox.current(0)

        index_column = tk.StringVar()
        index_combobox = ttk.Combobox(root, textvariable=index_column, values=["", "PRIMARY KEY", "UNIQUE", "FOREIGN KEY"] , state='readonly')
        index_combobox.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        index_combobox.current(0)
        index_combobox.bind("<<ComboboxSelected>>" , lambda event : references(index_column.get()))


        def references(type_index):
            if type_index =="FOREIGN KEY" :
                reference_entry.grid(row=5, column=1, padx=5, pady=5, sticky='ew')
                ref_label.grid(row=5, column=0, padx=5, pady=5, sticky='e')
                ai_checkbox.grid_forget()
            elif type_index =="PRIMARY KEY" or type_index =="UNIQUE" :
                null_checkbox.grid_forget()
                ai_checkbox.grid(row=6, column=1, padx=5, pady=5, sticky='w')
            else : 
                reference_entry.grid_forget()
                ref_label.grid_forget()
                null_checkbox.grid(row=6, column=2, padx=10, pady=5, sticky='w')
                ai_checkbox.grid_forget()


        null_var = tk.BooleanVar()
        null_checkbox = tk.Checkbutton(root, text="Null", variable=null_var)
        null_checkbox.grid(row=6, column=2, padx=10, pady=5, sticky='w')

        ai_var = tk.BooleanVar()
        ai_checkbox = tk.Checkbutton(root, text="A_I", variable=ai_var)
        ai_checkbox.grid(row=6, column=1, padx=5, pady=5, sticky='w')
        
        def submit_form() : 
            name = name_entry.get()
            data_type = type_combobox.get()
            length_values = length_values_entry.get()
            null_value = null_var.get()
            index_value = index_combobox.get()
            reference = reference_entry.get()
            ai_value = ai_var.get()


            treeview.config(height=int(treeview.cget("height"))+1)
            treeview.insert("" , tk.END , values=[name , data_type , length_values , null_value , index_value , reference , ai_value])  
            
            name_entry.delete(0, 'end')
            type_combobox.set('')
            length_values_entry.delete(0, 'end')
            index_combobox.set('')
            reference_entry.delete(0, 'end')
            null_var.set(False)
            ai_var.set(False)


        submit_button = tk.Button(root, text="Submit", command=lambda : submit_form())
        submit_button.grid(row=7, column=0, columnspan=2, padx=5, pady=10)

        root.grid_rowconfigure(8, weight=1)
        root.grid_columnconfigure(2, weight=1)

        root.mainloop()


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

    # Add a canvas to make the frame scrollable
    canvas = tk.Canvas(insert_frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Add a scrollbar
    scrollbar = ttk.Scrollbar(insert_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    inner_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor=tk.NW)

    entries = []
    columns_fk = [item for item in columns for tuple_item in mysql_con.fk_in_table(db_name, table) if item in tuple_item]
    for header in columns:
        label = ttk.Label(inner_frame, text=header)
        label.pack(padx=300, pady=5)
        if header not in columns_fk :
            entry_var = tk.StringVar()
            entry = ttk.Entry(inner_frame, textvariable=entry_var)
            entry.pack(padx=300, pady=5 )
            entries.append(entry_var)

        else :
            choice = tk.StringVar()
            foreign_key = ttk.Combobox(inner_frame , textvariable=choice , values=mysql_con.get_foreign_keys_values(db_name , table) , state='readonly')
            foreign_key.pack(padx=300, pady=5 )
            entries.append(choice)

    # Function to update canvas scrolling region
    def _configure_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    inner_frame.bind("<Configure>", _configure_scroll_region)

    # Add a button to submit the changes
    submit_button = ttk.Button(inner_frame, text="Insert", command=lambda : get_inserted_values(db_name , table))
    submit_button.pack(padx=10, pady=20)

    # Bind the canvas scrolling to mousewheel events
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # Function to get the values from the entry widgets
    def get_inserted_values(db_name  ,table):
        new_values = [entry.get() for entry in entries]
        
        mysql_con.insert_into_table(db_name,table , new_values , columns)


    notebook.add(child=insert_frame ,text='Insert')

    operations_frame = ttk.Frame(notebook)
    operations_frame.pack(expand=True ,fill='both')

    rename_frame = ttk.Frame(operations_frame, borderwidth=10, relief="solid", height=60)
    rename_frame.pack(fill='x', padx=10, pady=(20, 0) , ipady=40)

    new_name = tk.StringVar()
    new_name_entry = ttk.Entry(rename_frame, textvariable=new_name, width=60)
    new_name_entry.pack(side='left', padx=50)

    rename_table_button = ttk.Button(rename_frame, text="Rename Table", width=50, command=lambda : mysql_con.rename_table(table , new_name.get()))
    rename_table_button.pack(side='right', padx=50)

    empty_table = ttk.Frame(operations_frame, borderwidth=10, relief="solid", height=60)
    empty_table.pack(fill='x', padx=10, pady=(30, 0) , ipady=40)

    empty_label = ttk.Label(empty_table, text="Empty Table Records " , font=('Helvetica' , 12))
    empty_label.pack(side='left',pady=10 , padx =30 )

    empty_table_button = ttk.Button(empty_table, text="Delete Records", width=40, command=lambda :mysql_con.empty_table(table))
    empty_table_button.pack(side='left',pady=10 , padx =60)

    drop_table_frame = ttk.Frame(operations_frame, borderwidth=10, relief="solid", height=60)
    drop_table_frame.pack(fill='x', padx=10, pady=(30, 0),ipady=40)

    drop_label = ttk.Label(drop_table_frame, text="Delete Table " , font=('Helvetica' , 12))
    drop_label.pack(side='left',pady=10 , padx =30)

    drop_table_button = ttk.Button(drop_table_frame, text="Drop Table", width=40, command=lambda: mysql_con.delete_table(table))
    drop_table_button.pack(side='left',pady=10 , padx =60) 

    drop_column_frame = ttk.Frame(operations_frame, borderwidth=10, relief="solid", height=60)
    drop_column_frame.pack(fill='x', padx=10, pady=(30, 0),ipady=40)

    dropped_column = tk.StringVar()
    drop_column_label = ttk.Combobox(drop_column_frame, textvariable=dropped_column,  values=columns , width=30 , state='readonly')
    drop_column_label.pack(side='left',pady=10 , padx =30)

    drop_column_button  = ttk.Button(drop_column_frame, text="Drop Column", width=40, command=lambda: mysql_con.drop_column(table , dropped_column.get()))
    drop_column_button.pack(side='left',pady=10 , padx =60) 
    
    notebook.add(child=operations_frame ,text='Operations')

    sql_dump_frame = ttk.Frame(notebook)
    sql_dump_frame.pack(expand=True ,fill='both')

    sql_dump_title = ttk.Label(sql_dump_frame , text='Dump Table' ,  font=("Helvetica",20))
    sql_dump_title.grid(row=0 , column=0 , padx=240 , pady=30,sticky='w')

    dump_path_label = ttk.Label(sql_dump_frame , text='Path : ' ,  font=("Helvetica",14))
    dump_path_label.grid(row=1, column=0 , padx=100 , pady=60 ,sticky='w')

    dump_path= tk.StringVar()
    dump_path_entry = ttk.Entry(sql_dump_frame , textvariable=dump_path , width=40)
    dump_path_entry.grid(row=1, column=0 , padx=220 , pady=60,sticky='w')

    dump_button = ttk.Button(sql_dump_frame , text='dump' ,command=lambda : mysql_con.sql_dump(dump_path.get() ,table, dump_arg(var_struct_only, var_data_only, var_add_routines , var_add_events) ))
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

    data_vis_frame = ttk.Frame(notebook)
    data_vis_frame.pack(expand=True ,fill='both')

    vis_label = ttk.Label(data_vis_frame ,text='Visualize Column Data' , font=('Helvetica' , 20))
    vis_label.pack(side='top' , pady=20 )
    
    visualized_column = tk.StringVar()
    vis_column_list = ttk.Combobox(data_vis_frame, textvariable=visualized_column , values=columns , width=30 ,state='readonly' )
    vis_column_list.pack(side='top' , pady=20 )
    vis_column_list.bind("<<ComboboxSelected>>" , lambda event : update_plots())

    plots_to_visualize = tk.StringVar()
    plots_combobox = ttk.Combobox(data_vis_frame,textvariable=plots_to_visualize, width=30 , values=[] , state='readonly')  
    plots_combobox.pack(side='top' , pady=20 )
    plots_combobox.bind("<<ComboboxSelected>>" , lambda event : update_measures())

    statistical_measure = tk.StringVar()
    statistical_measure_combobox = ttk.Combobox(data_vis_frame,textvariable=statistical_measure, width=30 , values=[] , state='readonly')  
    statistical_measure_combobox.pack(side='top' , pady=20 )

    visualize_button = ttk.Button(data_vis_frame , text='Create' , command= lambda : mysql_con.generate_plot(plots[2] ,plots_to_visualize.get(), statistical_measure.get()))
    visualize_button.pack(side='top' , pady=20 )
    
    plots = None
    def update_measures():
        measures = mysql_con.get_possible_measures( plots_to_visualize.get(), plots[0])
        statistical_measure_combobox.config(values=measures)

    def update_plots():
        nonlocal plots
        plots = mysql_con.get_possible_plots(table , visualized_column.get())
        plots_combobox.config(values=plots[1])


    notebook.add(child=data_vis_frame ,text='Visualize Data')

""" UPDATE row values """
def operations_on_row(db_name , frame ,table , columns, selected_row , key_val_cpl):    
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
    submit_button = ttk.Button(inner_frame, text="Update", command=lambda :update_row(db_name , table) )
    submit_button.pack(padx=10, pady=20)

    delete_row_button = ttk.Button(inner_frame, text="Delete row ", command=lambda :delete_row(db_name , table , key_val_cpl) )
    delete_row_button.pack(padx=10, pady=20)


    # Bind the canvas scrolling to mousewheel events
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # Function to get the values from the entry widgets
    def get_values(db_name  ,table):
        new_values = [entry.get() for entry in entries]
        window.destroy()
        frame.destroy()
        return new_values
    
    def update_row(db_name , table): 
        new_values = get_values(db_name , table)
        mysql_con.alter_table(db_name,table , new_values , columns ,key_val_cpl)
        table_tabs(db_name , table)

    def delete_row(db_name , table , key_val_cpl):
        window.destroy()
        frame.destroy()
        mysql_con.delete_row(table , key_val_cpl)
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
app.title("MySQL Administration")
try :
    app.iconbitmap("icon1.ico")
except Exception:
    pass


saved_theme = load_theme_settings()
if saved_theme:
    style = ttkbootstrap.Style(theme=saved_theme)
else:
    style = ttkbootstrap.Style(theme="darkly")
style.theme_use()
create_login_page()
app.mainloop()



