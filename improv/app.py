from customtkinter import CTkScrollableFrame
from server_manager import MySQL_connection , MySQL_Manager
from tkinter import ttk , messagebox
import tkinter as tk
import ttkbootstrap
import json
import webbrowser


frame_to_destroy = []

class App :
    def __init__(self) -> None:
        self.__app = tk.Tk()
        self.__app.geometry("1024x768")
        self.__app.title("MySQL Administration")
        try :
            self.__app.iconbitmap("icon1.ico")
        except Exception:
            pass
        self.__saved_theme = self.load_theme_settings()
        if self.__saved_theme:
            style = ttkbootstrap.Style(theme=self.__saved_theme)
        else:
            style = ttkbootstrap.Style(theme="darkly")
        style.theme_use()
        LoginPage(self.__app)
        self.__app.mainloop()

    def load_theme_settings(self):
        try:
            with open('theme_settings.json', 'r') as file:
                settings = json.load(file)
                return settings['theme']
        except FileNotFoundError:
            return None
class LoginPage:
    def __init__(self,app):
        self.__app = app
        self.login_page()

    def login_page(self):
        self.__frame = ttk.Frame(master=self.__app)
        self.__frame.pack(pady=20 , padx=60 , fill="both" , expand=True)

        self.__label = ttk.Label(master=self.__frame, text="Login" , font=("Roboto" , 30))
        self.__label.pack(padx=20 , pady=22)
        
        self.__host_label = ttk.Label(master=self.__frame, text="Hostname :")
        self.__host_label.pack(pady=10)

        self.__hostname = tk.StringVar()
        self.__host_entry = ttk.Entry(self.__frame, textvariable=self.__hostname)
        self.__host_entry.pack(padx=10, pady=10)

        self.__port_label = ttk.Label(master=self.__frame, text="Port :")
        self.__port_label.pack(pady=10)

        self.__port = tk.StringVar()
        self.__port_entry = ttk.Entry(self.__frame, textvariable=self.__port)
        self.__port_entry.pack(padx=10, pady=10)

        self.__username_label = ttk.Label(master=self.__frame, text="Username :")
        self.__username_label.pack(pady=10)

        self.__username = tk.StringVar()
        self.__username_entry = ttk.Entry(self.__frame, textvariable=self.__username)
        self.__username_entry.pack(padx=10, pady=10)

        self.__password_label = ttk.Label(master=self.__frame, text="Password :")
        self.__password_label.pack(pady=10)

        self.__password = tk.StringVar()
        self.__password_entry = ttk.Entry(self.__frame, textvariable=self.__password, show='*')
        self.__password_entry.pack(padx=10, pady=10)

        self.__auth_label = ttk.Label(master=self.__frame, text="Auth plugin :")
        self.__auth_label.pack(pady=10)

        self.__auth = tk.StringVar()
        self.__auth_entry = ttk.Entry(self.__frame, textvariable=self.__auth )
        self.__auth_entry.pack(padx=10, pady=10)

        self.__login_button = ttk.Button(master=self.__frame, text="Login", command=lambda: self.logging_in())
        self.__login_button.pack(pady=10)

        self.theme_button('darkly_label' , "Darkly Theme" , 5)
        self.theme_button('solar_label' , "Solar Theme" , 5)
        self.theme_button('superhero_label' , "Superhero Theme" , 5)
        self.theme_button('Cyborg_label' , "Cyborg Theme" , 5)
        self.theme_button('Vapor_label' , "Vapor Theme" , 5)
        self.theme_button('solar_label' , "Morph Theme" , 5)

        self.__doc_button = ttk.Button(master=self.__frame, text="Documentation" , style="Hyperlink.TButton" , command=lambda : webbrowser.open('https://github.com/NizarKarroud/MySQL-gui'))
        self.__doc_button.pack(anchor='e' , side='right' , pady=(80,10) , padx=5)

        def on_enter(event):
           self.logging_in()

        self.__app.bind("<Return>", on_enter)
    
    def theme_button(self , button_name , title , padding ) :
        self.__button_name = ttk.Button(master=self.__frame, text=title , style="Hyperlink.TButton" , command= lambda : self.save_theme_settings(title.split()[0].lower()) )
        self.__button_name.pack(anchor='w' , side='left' , pady=(80,10) , padx=padding)

    def save_theme_settings(self ,theme_name):
        with open('theme_settings.json', 'w') as file:
            json.dump({'theme': theme_name}, file)

    def logging_in(self):
        self.__con = MySQL_connection(self.__hostname.get(),self.__username.get(),self.__password.get(), self.__port.get(), self.__auth.get())
        if self.__con.connected == True :
            self.__frame.destroy()
            self.__app.unbind("<Return>")
            main_page(self.__app , self.__con , self.__hostname.get(),self.__username.get(),self.__password.get(), self.__port.get(), self.__auth.get())
            del self 
# mysql_native_password
class main_page:
    def __init__(self,app,con , hostname , username , password , port , auth_pluging) -> None:
        self.__app = app
        self.__con = con
        self.__cursor = con.cursor

        self.__hostname= hostname
        self.__username = username
        self.__password = password
        self.__port = port
        self.__auth = auth_pluging
        self.__manager = MySQL_Manager(self.__con.connection,self.__cursor)
        self.Databases_Menu()

    def Databases_Menu(self) :
        self.__menu_frame = CTkScrollableFrame(master=self.__app)
        self.__menu_frame.grid(row=0, column=0 , sticky="ns")
        self.__app.grid_rowconfigure(0, weight=1) 

        self.__new_db = tk.StringVar()
        self.__db_create_entry = ttk.Entry(self.__menu_frame, textvariable=self.__new_db )
        self.__db_create_entry.pack(pady=(60,0)) 

        self.__create_database_button = ttk.Button(self.__menu_frame,text="Create a new Database" ,command=lambda:(self.__menu_frame.update_idletasks() if self.__manager.create_database(self.__new_db.get()) else None))
        self.__create_database_button.pack(side="top", pady=(10,40))
        
        self.__databases = self.__manager.show_databases()
        self.__databases_buttons = [ttk.Button(self.__menu_frame,text=database ,command=lambda db=database: self.databases_notebook(db[0]) ).pack(fill='both',side="top", pady=10) for database in self.__databases]
#  

    def databases_notebook(self,db):
        self.__nte =Notebook(self.__app)
        self.__con.kill_connection()
        self.__con.kill_cursor()

        self.__con = MySQL_connection(self.__hostname , self.__username , self.__password , self.__port , self.__auth , db)
        self.__cursor = self.__con.cursor

        self.__manager = MySQL_Manager(self.__con.connection,self.__cursor)

        self.__nte.add_tab("Tables","Canvas")
        self.__inner_frame = CTkScrollableFrame(self.__nte.tabs["Tables"] )
        self.__inner_frame.pack(fill="both" , expand=True)

        self.__tables = self.__manager.show_tables(db)
        self.__tables_buttons = [ttk.Button(self.__inner_frame,text=table, command=lambda table=table[0] : self.table_notebook(db ,table)).pack(side='top',anchor='center' , fill='x', padx=220, pady=10 ) for table in self.__tables]
        
    
        self.__nte.add_tab("SQL","Frame")
        self.__text_box = tk.Text(self.__nte.tabs["SQL"])
        self.__text_box.pack(padx=20 , pady= (20,10) ,fill='both' , expand=True)

        self.__exec_button = ttk.Button(self.__nte.tabs["SQL"], text='Execute' , command= lambda : self.sql_query(self.__text_box.get(1.0, "end-1c")))
        self.__exec_button.pack(pady=(10,30),padx=20 , side='right')

        self.__nte.add_tab("Operations","Frame")

        self.__create_table_frame = ttk.Frame(self.__nte.tabs["Operations"], borderwidth=10, relief="solid", height=100)
        self.__create_table_frame.pack(fill='x', padx=10, pady=(30, 0) , ipady=70)

        self.__table_name_label =ttk.Label(self.__create_table_frame , text='Create new Table Page' ,font=('Helvetica', 14))
        self.__table_name_label.pack(side='left' ,padx=100)
        # button to get to the table creation page
        self.__create_table_button =ttk.Button(self.__create_table_frame , text="Create new Table " )
        self.__create_table_button.pack(side='left' ,padx=100)

# , command=lambda:table_create_page()
        self.__rename_frame = ttk.Frame(self.__nte.tabs["Operations"], borderwidth=10, relief="solid", height=100)
        self.__rename_frame.pack(fill='x', padx=10, pady=(30, 0) , ipady=70)

        self.__new_name = tk.StringVar()
        self.__new_name_entry = ttk.Entry(self.__rename_frame, textvariable=self.__new_name, width=60)
        self.__new_name_entry.pack(side='left', padx=50)

        self.__rename_database_button = ttk.Button(self.__rename_frame, text="Rename Database", width=50 ,command=lambda : (self.__menu_frame.destroy(), self.Databases_Menu()) if self.__manager.rename_database(db ,self.__con.hostname ,self.__con.username ,self.__con.pwd , self.__new_name.get()) else None)
        self.__rename_database_button.pack(side='right', padx=50)


        self.__drop_database_frame = ttk.Frame(self.__nte.tabs["Operations"], borderwidth=10, relief="solid", height=100)
        self.__drop_database_frame.pack(fill='x', padx=10, pady=(30, 0),ipady=70)

        self.__drop_label = ttk.Label(self.__drop_database_frame, text="Drop Database " , font=('Helvetica' , 12))
        self.__drop_label.pack(side='left',pady=10 , padx =30)

        self.__drop_database_button = ttk.Button(self.__drop_database_frame, text="Drop Database ", width=40 ,command=lambda: (self.__menu_frame.destroy(), self.Databases_Menu()) if self.__manager.drop_db(db) else None)
        self.__drop_database_button.pack(side='left',pady=10 , padx =60)
        

        self.__nte.add_tab("Search","Frame")
        self.__db_search = Search_Page(self.__app, self.__manager ,"Database" ,db , self.__nte.tabs["Search"])

        self.__nte.add_tab("Copy Database","Frame")
        self.__nte.add_tab("Export","Frame")

        self.__nte.add_tab("SQL Dump","Frame")
        self.__dump_db_page = SQL_Dump_Page(self.__nte.tabs["SQL Dump"] ,"Database", self.__manager , db ,self.__con.hostname, self.__con.username,self.__con.pwd )
    
        self.__nte.add_tab("Import","Frame")
        self.__nte.add_tab("Triggers","Frame")


    def sql_query(self, query):
        self.__result = self.__manager.exec_query(query)
        if isinstance(self.__result, tuple):  # Check if result is a tuple (indicating data query)
            self.__columns, self.__rows = self.__result
            self.__query_window= Second_window(self.__app ,"800x600" , "View Query Results")

            self.__query_tree = Records(self.__query_window.window , self.__rows , self.__columns , "Table")
        elif self.__result ==True :
            messagebox.showerror(message="Executed successfully")

    def table_notebook(self , db , table):
        self.__nte =Notebook(self.__app)

        self.__nte.add_tab("Records","Frame")
        self.__columns , self.__rows , self.__prim_keys = self.__manager.show_table_records(table)
        self.__query_tree = Records(self.__nte.tabs["Records"] , self.__rows , self.__columns , "Table")

        self.__nte.add_tab("Search","Frame")
        self.__db_search = Search_Page(self.__app, self.__manager ,"Table" ,db , self.__nte.tabs["Search"] , table)

        self.__nte.add_tab("Insert","Frame")

        self.__nte.add_tab("Operations","Frame")

        self.__nte.add_tab("SQL Dump","Frame")
        self.__dump_table_page = SQL_Dump_Page(self.__nte.tabs["SQL Dump"] ,"Table", self.__manager , db,self.__con.hostname, self.__con.username,self.__con.pwd ,table)

        self.__nte.add_tab("Visualize Data","Frame")
        self.__visualize_label = ttk.Label(self.__nte.tabs["Visualize Data"] ,text='Visualize Column Data' , font=('Helvetica' , 20))
        self.__visualize_label.pack(side='top' , pady=20 )
    
        self.__visualized_column = tk.StringVar()
        self.__column_list = ttk.Combobox(self.__nte.tabs["Visualize Data"], textvariable=self.__visualized_column , values=self.__columns , width=30 ,state='readonly' )
        self.__column_list.pack(side='top' , pady=20 )
        self.__column_list.bind("<<ComboboxSelected>>" , lambda event : update_plots())

        self.__plots_to_visualize = tk.StringVar()
        self.__plots_combobox = ttk.Combobox(self.__nte.tabs["Visualize Data"],textvariable=self.__plots_to_visualize, width=30 , values=[] , state='readonly')  
        self.__plots_combobox.pack(side='top' , pady=20 )
        self.__plots_combobox.bind("<<ComboboxSelected>>" , lambda event : update_measures())

        self.__statistical_measure = tk.StringVar()
        self.__statistical_measure_combobox = ttk.Combobox(self.__nte.tabs["Visualize Data"],textvariable=self.__statistical_measure, width=30 , values=[] , state='readonly')  
        self.__statistical_measure_combobox.pack(side='top' , pady=20 )

        visualize_button = ttk.Button(self.__nte.tabs["Visualize Data"] , text='Create' , command= lambda :self.__manager.generate_plot(plots[2] ,self.__plots_to_visualize.get(), self.__statistical_measure.get()))
        visualize_button.pack(side='top' , pady=20 )
        
        plots = None
        def update_measures():
            measures = self.__manager.get_possible_measures( self.__plots_to_visualize.get(), plots[0])
            self.__tatistical_measure_combobox.config(values=measures)

        def update_plots():
            nonlocal plots
            plots = self.__manager.get_possible_plots(table , self.__visualized_column.get())
            self.__plots_combobox.config(values=plots[1])
class Second_window:
    def __init__(self, master ,size , title):
        self.__master = master
        self.__size = size 
        self.__title = title
        self.set_window()

    def set_window(self):
        self.__window = tk.Toplevel(self.__master)
        self.__window.geometry(self.__size)
        self.__window.title(self.__title)       
        
    def del_win(self):
        self.__window.destroy()

    @property
    def window(self):
        return self.__window
class Notebook:
    _instances = []

    def __init__(self,master) -> None:
        Notebook.clean()
        self.__master = master
        self.__tabs = {}  # Dictionary to store tabs
        self.__notebook = ttk.Notebook(self.__master)
        self.__notebook.grid(row=0, column=1 , sticky="nswe" , padx=10 , pady=10)
        self.__master.grid_columnconfigure(1, weight=1) 
        self.__master.grid_rowconfigure(0, weight=1)
        Notebook._instances.append(self)

    def add_tab(self,tab_name,frame_type):
        self.__frame = getattr(tk, frame_type, None)
        self.__tabs[tab_name] = self.__frame(self.__notebook)
        self.__tabs[tab_name].pack(fill="both", expand=True)
        self.__notebook.add(self.__tabs[tab_name] , text=tab_name)

    def cleanup_resources(self):
        for tab in self.__tabs.values():
            tab.destroy()
        self.__notebook.destroy()

    @classmethod
    def clean(cls):
        for instance in cls._instances[:]:
            instance.cleanup_resources()
            cls._instances.remove(instance)
            del instance

    @property
    def tabs(self ):
        return self.__tabs

class Records:
    def __init__(self , master , rows ,columns , record_type) -> None:
        self.__treeframe = ttk.Frame(master)
        self.__treeframe.pack(expand=True , fill='both')

        # Add vertical scrollbar
        self.__tree_y_Scrollbar = ttk.Scrollbar(self.__treeframe , orient="vertical")
        self.__tree_y_Scrollbar.pack(side="right",fill="y")

        # Add horizontal scrollbar
        self.__tree_x_Scrollbar = ttk.Scrollbar(self.__treeframe , orient="horizontal")
        self.__tree_x_Scrollbar.pack(fill="x" , side="bottom")
        
        # Create a Treeview widget
        self.__treeview = ttk.Treeview(self.__treeframe,show='headings', xscrollcommand=self.__tree_x_Scrollbar.set ,yscrollcommand= self.__tree_y_Scrollbar.set,  columns=columns ,height=len(rows))
        self.__treeview.pack()

    # add the columnns as Headers
        for column in columns :
            self.__treeview.column(column, anchor="center")
            self.__treeview.heading(column , text=column)

    # Insert data into the treeview
        if record_type =="Search":
            for row in rows :
                inner_tuple, element = row[0], row[1]
                inner_elements = [item for item in inner_tuple]
                values_to_insert = inner_elements + [element]
                self.__treeview.insert("" , tk.END , values=values_to_insert)
        elif record_type =="Table" : 
            for row in rows :
                self.__treeview.insert("" , tk.END , values=row)

        self.__tree_y_Scrollbar.config(command=self.__treeview.yview)
        self.__tree_x_Scrollbar.config(command=self.__treeview.xview)

class SQL_Dump_Page :
    def __init__(self , master,type , manager , db , hostname,username,password , table=None) -> None:
        self.__master = master
        self.__type = type.title()
        self.__manager = manager
        self.__db = db 
        self.__table = table
        self.__hostname = hostname 
        self.__username = username 
        self.__password = password
        self.create_page()

    def create_page(self):
        self.__dump_title = ttk.Label(self.__master , text=f'Dump {self.__type}' ,  font=("Helvetica",20))
        self.__dump_title.grid(row=0, column=0, padx=10, pady=50, sticky="n")
        self.__master.grid_rowconfigure(0, weight=1)
        self.__master.grid_columnconfigure(0, weight=1)

        self.__dump_label = ttk.Label(self.__master , text='Path : ' ,  font=("Helvetica",14))
        self.__dump_label.grid(row=0, column=0, padx=50, pady=200, sticky="nw")

        self.__dump_path= tk.StringVar()
        self.__dump_path_entry = ttk.Entry(self.__master , textvariable=self.__dump_path , width=48)
        self.__dump_path_entry.grid(row=0, column=0, padx=20, pady=200, sticky="n")

        self.__dump_button = ttk.Button(
            self.__master,
            text='dump',
            command=lambda: self.__manager.sql_dump(
                self.__dump_path.get(),
                self.__db,
                self.__table,
                hostname=self.__hostname,
                username=self.__username,
                password=self.__password,
                additional_args=dump_arg(self.__var_struct_only, self.__var_data_only, self.__var_add_routines, self.__var_add_events)
            )
        )
        self.__dump_button.grid(row=0, column=0, padx=20, pady=200, sticky="ne")

        def browse_folder():
            folder_selected = tk.filedialog.askdirectory()
            self.__dump_path.set(folder_selected)
            
        self.__browse_button = ttk.Button(self.__master, text="Browse", command=browse_folder )
        self.__browse_button.grid(row=0, column=0, padx=100, pady=200, sticky="ne") 


        self.__var_struct_data = tk.IntVar()
        self.__var_struct_only = tk.IntVar()
        self.__var_data_only = tk.IntVar()
        self.__var_add_routines = tk.IntVar()
        self.__var_add_events = tk.IntVar()

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

        self.__struct_data = tk.Checkbutton(self.__master , text="Structure and data" ,variable=self.__var_struct_data, command=lambda : deselect_when_selected(self.__struct_only , self.__data_only))
        self.__struct_data.grid(row=0 , column=0 , padx=100, pady=(10,10), sticky='w')

        self.__struct_only = tk.Checkbutton(self.__master  , text="Structure only", variable=self.__var_struct_only, command=lambda : deselect_when_selected(self.__struct_data , self.__data_only))
        self.__struct_only.grid(row=0 , column=0 , padx=100, pady=(60,10), sticky='w')

        self.__data_only = tk.Checkbutton(self.__master , text="Data Only",variable=self.__var_data_only,command=lambda : deselect_when_selected(self.__struct_data , self.__struct_only))
        self.__data_only.grid(row=0 , column=0 , padx=100, pady=(130 ,35), sticky='w')

        self.__add_routines = tk.Checkbutton(self.__master ,variable=self.__var_add_routines, text="Add Routines")
        self.__add_routines.grid(row=0 , column=0 , padx=100, pady=(180,10), sticky='w')

        self.__add_events = tk.Checkbutton(self.__master ,variable=self.__var_add_events, text="Add Events")
        self.__add_events.grid(row=0 , column=0 , padx=100, pady=(220, 10), sticky='w')
class Search_Page:
    def __init__(self ,app ,manager ,type , db ,master ,table=None ) -> None:
        self.__type = type.title() 
        self.__master = master
        self.__manager = manager
        self.__app = app
        self.__db = db
        self.__table = table
        self.create()
    def create(self):
        self.__search_title_label = ttk.Label(self.__master , text=f'Search in {self.__type}' , font=("Helvetica",24))
        self.__search_title_label.grid(row=0, column=0, padx=10, pady=50, sticky="n")
        self.__master.grid_rowconfigure(0, weight=1)
        self.__master.grid_columnconfigure(0, weight=1)

        self.__search_label = ttk.Label(self.__master, text='Value to search for:', font=("Helvetica", 13))
        self.__search_label.grid(row=0, column=0, padx=40, pady=300, sticky="nw")

        self.__search_term = tk.StringVar()
        self.__search_entry = ttk.Entry(self.__master, textvariable=self.__search_term, width=45 , justify='center')
        self.__search_entry.grid(row=0, column=0, padx=10, pady=300, sticky="n")
        self.__search_button = ttk.Button(self.__master, text='Search', width=25, command=lambda: self.search())
        self.__search_button.grid(row=0, column=0, padx=40, pady=300, sticky="ne")
    
    def search(self):
        self.__search_window = Second_window(self.__app, "800x600","View Search Results")
        if self.__type == "Database": 
            self.__search_tree = Records(self.__search_window.window ,self.__manager.search_database(self.__db, self.__search_term.get()) , ['Table' , 'Column' , 'matches'], "Search")
        else :
            self.__columns , self.__rows = self.__manager.search_table(self.__search_term.get() , self.__db, self.__table)
            self.__search_tree = Records(self.__search_window.window , self.__rows , self.__columns , "Table")



App()