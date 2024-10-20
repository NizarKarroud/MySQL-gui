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

        self.__create_database_button = ttk.Button(self.__menu_frame,text="Create a new Database" ,command=lambda:(self.__menu_frame.destroy(), self.Databases_Menu())  if self.__manager.create_database(self.__new_db.get()) else None)
        self.__create_database_button.pack(side="top", pady=(10,40))

        self.__databases = self.__manager.show_databases()
        self.__databases_buttons = [ttk.Button(self.__menu_frame,text=database ,command=lambda db=database: self.databases_notebook(db[0])).pack(fill='both',side="top", pady=10) for database in self.__databases]

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

        self.__exec_button = ttk.Button(self.__nte.tabs["SQL"], text='Execute' , command= lambda : self.sql_query(self.__text_box.get(1.0, "end-1c") ))
        self.__exec_button.pack(pady=(10,30),padx=20 , side='right')

        self.__nte.add_tab("Operations","Frame")

        self.__create_table_operation = Operation(self.__nte.tabs["Operations"] , "Label" ,title ="Create new Table Page : " , padx=10, pady=(30,0) , ipady=60 , type_padx=100 , type_pady=30 , bt_title="Create new Table" , bt_padx =100  , but_pady=30 )

        self.__rename_operation = Operation(self.__nte.tabs["Operations"] , "Entry" ,padx=10, pady=(30,0) , ipady=60 , type_padx=60 ,type_pady=30, bt_title="Rename Database" , bt_padx =50  , but_pady= 30 )
        self.__rename_operation.set_button_command(lambda : (self.__menu_frame.destroy(), self.Databases_Menu()) if self.__manager.rename_database(db ,self.__con.hostname ,self.__con.username ,self.__con.pwd , self.__rename_operation.var.get()) else None)

        self.__drop_database_operation = Operation(self.__nte.tabs["Operations"] , "Label" ,title ="Drop the Database " ,padx=10, pady=(30,0) , ipady=60 , type_padx=100 , type_pady=30 , bt_title="Drop" , bt_padx =100  , but_pady= 30 )
        self.__drop_database_operation.set_button_command(lambda: (self.__menu_frame.destroy(), self.Databases_Menu()) if self.__manager.drop_db(db) else None)

        self.__nte.add_tab("Search","Frame")
        self.__db_search = Search_Page(self.__app, self.__manager ,"Database" ,db , self.__nte.tabs["Search"])

        self.__nte.add_tab("Copy Database","Frame")
        self.__copy_label = ttk.Label(self.__nte.tabs["Copy Database"] , text='Copy Database' ,  font=("Helvetica",20))
        self.__copy_label.grid(row=0 , column=0 , padx=240 , pady=30,sticky='w')

        self.__db_copy_label = ttk.Label(self.__nte.tabs["Copy Database"] , text='Database : ' ,  font=("Helvetica",14))
        self.__db_copy_label.grid(row=1, column=0 , padx=100 , pady=60 ,sticky='w')

        self.__db_copy_to = tk.StringVar()
        self.__db_copy_entry = ttk.Entry(self.__nte.tabs["Copy Database"] , textvariable=self.__db_copy_to , width=40)
        self.__db_copy_entry.grid(row=1, column=0 , padx=220 , pady=60,sticky='w')


        self.__copy_button = ttk.Button(
            self.__nte.tabs["Copy Database"] ,
            text='copy' ,
            command= lambda :(
                (self.__menu_frame.destroy(), self.Databases_Menu())  if self.__manager.copy_db(
                    self.__db_copy_to.get() ,db , self.__con.hostname , self.__con.username , self.__con.pwd,
                    get_args(self.__cp_struct.get() ,self.__cp_data.get()) ,self.__create_before.get() )
                    else None)
                    )

        self.__copy_button.grid(row=1, column=0 , padx=550, pady=60, sticky='w')

        def deselect_when_selected(*args):
            for arg in args :
                arg.deselect()

        self.__cp_struct = tk.IntVar()
        self.__cp_data = tk.IntVar()
        self.__create_before = tk.IntVar()

        def get_args(cp_struct, cp_data ):
            options = []
            if cp_struct == 1:
                options.append("--no-data")
            if cp_data == 1:
                options.append("--no-create-info")

            return options

        self.__cp_struct_data = tk.Checkbutton(self.__nte.tabs["Copy Database"], text="Structure and data" , command=lambda : deselect_when_selected(self.__cp_struct_only , self.__cp_data_only))
        self.__cp_struct_data.grid(row=2 , column=0 , padx=100, pady=(10,10), sticky='w')

        self.__cp_struct_only = tk.Checkbutton(self.__nte.tabs["Copy Database"] , text="Structure only", variable=self.__cp_struct, command=lambda : deselect_when_selected(self.__cp_struct_data , self.__cp_data_only))
        self.__cp_struct_only.grid(row=2 , column=0 , padx=100, pady=(60,10), sticky='w')

        self.__cp_data_only = tk.Checkbutton(self.__nte.tabs["Copy Database"], text="Data Only",variable=self.__cp_data,command=lambda :deselect_when_selected(self.__cp_struct_data,self.__cp_struct_only))
        self.__cp_data_only.grid(row=2 , column=0 , padx=100, pady=(130 ,35), sticky='w')

        self.__create_before_button = tk.Checkbutton(self.__nte.tabs["Copy Database"], variable=self.__create_before ,text="CREATE DATABASE before copying")
        self.__create_before_button.grid(row=2 , column=0 , padx=100, pady=(170,35), sticky='w')

        self.__nte.add_tab("Export","Frame")

        self.__export_label = ttk.Label(self.__nte.tabs["Export"] , text="Export Database's Tables" , font=("Helvetica",20))
        self.__export_label.grid(row=0, column=0, padx=10, pady=50, sticky="n")
        self.__nte.tabs["Export"].grid_rowconfigure(0, weight=1)
        self.__nte.tabs["Export"].grid_columnconfigure(0, weight=1)

        self.__path_label = ttk.Label(self.__nte.tabs["Export"] , text="Path : " ,font=("Helvetica",14))
        self.__path_label.grid(row=0, column=0, padx=50, pady=150, sticky="nw")

        self.__path_var = tk.StringVar()
        self.__path_entry = ttk.Entry(self.__nte.tabs["Export"] , textvariable=self.__path_var , width=45)
        self.__path_entry.grid(row=0, column=0, padx=(5,160), pady=150, sticky="n")

        self.__table_list_box = tk.Listbox(self.__nte.tabs["Export"], selectmode=tk.MULTIPLE , height=80 , width=40)

        self.__export_options = ['csv' , 'html']
        self.__type_var = tk.StringVar()
        self.__type_var.set(self.__export_options[0])

        self.__export_type = ttk.Combobox(self.__nte.tabs["Export"] , textvariable=self.__type_var , values=self.__export_options , state='readonly')
        self.__export_type.grid(row=0, column=0, padx=140, pady=150, sticky="ne")

        self.__export_button = ttk.Button(self.__nte.tabs["Export"] , text='export' ,command=lambda :self.__manager.export_database(db , table_list=[self.__table_list_box.get(idx) for idx in self.__table_list_box.curselection()], path=rf"{self.__path_var.get()}" , extension=self.__type_var.get()))
        self.__export_button.grid(row=0, column=0, padx=60, pady=150, sticky="ne")

        for option in self.__tables:
            self.__table_list_box.insert(tk.END, option[0])
            self.__table_list_box.grid(row=0 , column=0 ,sticky="w", padx=80 , pady=250)

        def select_all():
            self.__deselect_checkbox.deselect()
            self.__table_list_box.selection_set(0, tk.END)

        def deselect_all():
            self.__select_checkbox.deselect()
            self.__table_list_box.selection_clear(0, tk.END)

        self.__deselect_checkbox = tk.Checkbutton(self.__nte.tabs["Export"], text="Deselect all tables", command=lambda : deselect_all())
        self.__deselect_checkbox.grid(row=0 , column=0 ,sticky="e", padx=(30 ,180) , pady=(200 ,320))
        self.__select_checkbox = tk.Checkbutton(self.__nte.tabs["Export"], text="Select all tables", command=lambda : select_all())
        self.__select_checkbox.grid(row=0, column=0 ,sticky="e", padx=(30,315) ,pady=(200 ,320))

        self.__nte.add_tab("SQL Dump","Frame")
        self.__dump_db_page = SQL_Dump_Page(self.__nte.tabs["SQL Dump"] ,"Database", self.__manager , db ,self.__con.hostname, self.__con.username,self.__con.pwd )

        self.__nte.add_tab("Import","Frame")

        self.__import_title = ttk.Label(self.__nte.tabs["Import"] , text=f'Import into Database' , font=("Helvetica",24))
        self.__import_title.grid(row=0, column=0, padx=10, pady=50, sticky="n")

        self.__nte.tabs["Import"].grid_rowconfigure(0, weight=1)
        self.__nte.tabs["Import"].grid_columnconfigure(0, weight=1)

        self.__path_label = ttk.Label(self.__nte.tabs["Import"], text='Path : ', font=("Helvetica", 13))
        self.__path_label.grid(row=0, column=0, padx=40, pady=300, sticky="nw")

        self.__import_path = tk.StringVar()
        self.__import_entry = ttk.Entry(self.__nte.tabs["Import"], textvariable=self.__import_path, width=45 , justify='center')
        self.__import_entry.grid(row=0, column=0, padx=(10,150), pady=300, sticky="n")

        self.__import_button = ttk.Button(self.__nte.tabs["Import"], text='Import' , command=lambda: self.__manager.sql_import(self.__import_path.get()))
        self.__import_button.grid(row=0, column=0,padx=60, pady=300, sticky="ne")

        def browse_file():
            file_selected = tk.filedialog.askopenfilename()
            self.__import_path.set(file_selected)

        self.__browse_button = ttk.Button(self.__nte.tabs["Import"], text="Browse", command=browse_file )
        self.__browse_button.grid(row=0, column=0, padx=150, pady=300, sticky="ne")

        self.__nte.add_tab("Triggers","Frame")

        parent_frame = ttk.Frame(self.__nte.tabs["Triggers"])
        parent_frame.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')

        self.__nte.tabs["Triggers"].grid_rowconfigure(0, weight=1)
        self.__nte.tabs["Triggers"].grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(1, weight=1)

        trigger_name_label = ttk.Label(parent_frame, text='Trigger name:', font=("Helvetica", 14))
        trigger_name_label.grid(row=0, column=0, sticky='e', pady=20, padx=(100, 20))

        self.__trigger_name = tk.StringVar()
        self.__trigger_name_entry = ttk.Entry(parent_frame, textvariable=self.__trigger_name, width=35)
        self.__trigger_name_entry.grid(row=0, column=1, padx=(20, 100), pady=20, sticky='w')

        self.__table_label = ttk.Label(parent_frame, text='Table:', font=("Helvetica", 14))
        self.__table_label.grid(row=1, column=0, sticky='e', pady=20, padx=(100, 20))

        self.__table_choice = tk.StringVar()
        self.__trigger_tables = ttk.Combobox(parent_frame, textvariable=self.__table_choice, values=[table[0] for table in self.__tables], state='readonly', width=27)
        self.__trigger_tables.grid(row=1, column=1, padx=10, pady=5, sticky='w')

        self.__time_label = ttk.Label(parent_frame, text='Time:', font=("Helvetica", 14))
        self.__time_label.grid(row=2, column=0, sticky='e', pady=20, padx=(100, 20))

        self.__time = tk.StringVar()
        self.__time_choice = ttk.Combobox(parent_frame, textvariable=self.__time, values=['BEFORE', 'AFTER'], state='readonly', width=27)
        self.__time_choice.grid(row=2, column=1, padx=10, pady=5, sticky='w')

        self.__event_label = ttk.Label(parent_frame, text='Event:', font=("Helvetica", 14))
        self.__event_label.grid(row=3, column=0, sticky='e', pady=20, padx=(100, 20))

        self.__event = tk.StringVar()
        self.__event_choice = ttk.Combobox(parent_frame, textvariable=self.__event, values=['INSERT', 'UPDATE', 'DELETE'], state='readonly', width=27)
        self.__event_choice.grid(row=3, column=1, padx=10, pady=5, sticky='w')

        self.__definition_label = ttk.Label(parent_frame, text='Definition:', font=("Helvetica", 14))
        self.__definition_label.grid(row=4, column=0, sticky='ne', pady=60, padx=(100, 20))

        self.__definition_text = tk.Text(parent_frame, height=20, width=60)
        self.__definition_text.grid(row=4, column=1, padx=10, pady=10, sticky='nw')

        self.__create_trigger = ttk.Button(parent_frame, text='Create', command=lambda: self.__manager.trigger(self.__trigger_name.get(), self.__time.get(), self.__event.get(), self.__table_choice.get(), self.__definition_text.get(1.0, "end-1c")))
        self.__create_trigger.grid(row=5, column=1, sticky='e', padx=10, pady=20)

        # Add extra rows and columns to the parent frame for spacing
        for i in range(6):
            parent_frame.grid_rowconfigure(i, weight=1)
        parent_frame.grid_columnconfigure(2, weight=1)

    def sql_query(self, query):
        self.__result = self.__manager.exec_query(query)
        if isinstance(self.__result, tuple):  # Check if result is a tuple (indicating data query)
            self.__columns, self.__rows = self.__result
            self.__query_window= Second_window(self.__app ,"800x600" , "View Query Results")

            self.__query_tree = Records(self.__query_window.window , self.__rows , self.__columns , "Table" , manager= self.__manager , table=self._table)
        elif self.__result ==True :
            messagebox.showerror(message="Executed successfully")

    def table_notebook(self , db , table):
        self.__nte =Notebook(self.__app)

        self.__nte.add_tab("Records","Frame")
        self.__columns , self.__rows , self.__prim_keys = self.__manager.show_table_records(table)
        self.__record_tree = Records(self.__nte.tabs["Records"] , self.__rows , self.__columns , "Table" , primary_keys = self.__prim_keys , manager= self.__manager , table = table)

        self.__nte.add_tab("Search","Frame")
        self.__table_search = Search_Page(self.__app, self.__manager ,"Table" ,db , self.__nte.tabs["Search"] , table)

        self.__nte.add_tab("Insert","Frame")
        self.__canvas = tk.Canvas(self.__nte.tabs["Insert"])
        self.__canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar
        self.__scrollbar = ttk.Scrollbar(self.__nte.tabs["Insert"], orient=tk.VERTICAL, command=self.__canvas.yview)
        self.__scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.__canvas.configure(yscrollcommand=self.__scrollbar.set)

        self.__inner_frame = ttk.Frame(self.__canvas)
        self.__inner_frame_id = self.__canvas.create_window((0, 0), window=self.__inner_frame, anchor=tk.NW)

        entries = []
        columns_fk = [item for item in self.__columns for tuple_item in self.__manager.fk_in_table(db, table) if item in tuple_item]

        for i, header in enumerate(self.__columns):
            label = ttk.Label(self.__inner_frame, text=header)
            label.grid(row=i, column=0, padx=20, pady=5, sticky="e")

            if header not in columns_fk:
                entry_var = tk.StringVar()
                entry = ttk.Entry(self.__inner_frame, textvariable=entry_var)
                entry.grid(row=i, column=1, padx=20, pady=5, sticky="w")
                entries.append(entry_var)
            else:
                choice = tk.StringVar()
                foreign_key = ttk.Combobox(self.__inner_frame, textvariable=choice, values=self.__manager.get_foreign_keys_values(db, table), state='readonly')
                foreign_key.grid(row=i, column=1, padx=20, pady=5, sticky="w")
                entries.append(choice)

        # Add a button to submit the changes
        submit_button = ttk.Button(self.__inner_frame, text="Insert", command=lambda: get_inserted_values(table))
        submit_button.grid(row=len(self.__columns), column=0, columnspan=2, pady=20)

        # Function to update canvas scrolling region
        def _configure_scroll_region(event):
            self.__canvas.configure(scrollregion=self.__canvas.bbox("all"))

        self.__inner_frame.bind("<Configure>", _configure_scroll_region)

        # Bind the canvas scrolling to mousewheel events
        def _on_mousewheel(event):
            self.__canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.__canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Function to get the values from the entry widgets
        def get_inserted_values(table):
            new_values = [entry.get() for entry in entries]
            self.__manager.insert_into_table(table, new_values, self.__columns)

        # Center the inner frame in the canvas
        def _center_frame(event):
            canvas_width = event.width
            inner_frame_width = self.__inner_frame.winfo_width()
            self.__canvas.coords(self.__inner_frame_id, (canvas_width / 2 - inner_frame_width / 2, 0))

        self.__canvas.bind("<Configure>", _center_frame)

        self.__nte.add_tab("Operations","Frame")

        self.__rename_table_operation = Operation(self.__nte.tabs["Operations"] , "Entry" ,padx=10, pady=(20,0) , ipady=40 , type_padx=50 ,type_pady=20, bt_title="Rename Table" , bt_padx =50  , but_pady= 20 )
        self.__rename_table_operation.set_button_command(lambda : self.__manager.rename_table(table , self.__rename_table_operation.var.get()))

        self.__empty_table_operation = Operation(self.__nte.tabs["Operations"] , "Label" , title ="Empty Table Records "  ,padx=10, pady=(20,0) , ipady=40 , type_padx=50 ,type_pady=20, bt_title="Delete Records" , bt_padx =50  , but_pady= 20 )
        self.__empty_table_operation.set_button_command(lambda : self.__manager.empty_table(table))

        self.__drop_table_operation = Operation(self.__nte.tabs["Operations"] , "Label" , title ="Drop Table "  ,padx=10, pady=(20,0) , ipady=40 , type_padx=50 ,type_pady=20, bt_title="Delete" , bt_padx =50  , but_pady= 20 )
        self.__drop_table_operation.set_button_command(lambda : self.__manager.delete_table(table))

        self.__drop_column_operation = Operation(self.__nte.tabs["Operations"] , "Combobox" , values =self.__columns  ,padx=10, pady=(20,0) , ipady=40 , type_padx=50 ,type_pady=20, bt_title="Drop Column" , bt_padx =50  , but_pady= 20 )
        self.__drop_column_operation.set_button_command(lambda : self.__manager.drop_column(table , self.__drop_column_operation.var.get()))

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
    def __init__(self , master , rows ,columns , record_type  ,**kwargs ) -> None:
        self.__record_type = record_type
        self.__primary_keys = kwargs.get("primary_keys", None)
        print(self.__primary_keys)
        self.__search_term = kwargs.get("search_term", None)
        self.__table = kwargs.get("table", None)
        self.__master = master
        self.__manager = kwargs.get("manager", None)

        self.__treeframe = ttk.Frame(self.__master)
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
        if self.__record_type =="Search":
            for row in rows :
                inner_tuple, element = row[0], row[1]
                inner_elements = [item for item in inner_tuple]
                values_to_insert = inner_elements + [element]
                self.__treeview.insert("" , tk.END , values=values_to_insert)
        elif self.__record_type =="Table" :
            for row in rows :
                self.__treeview.insert("" , tk.END , values=row)

        self.__tree_y_Scrollbar.config(command=self.__treeview.yview)
        self.__tree_x_Scrollbar.config(command=self.__treeview.xview)
        self.__treeview.bind('<Double-1>', lambda event , headers=columns: self.click_on_row(self.__primary_keys , headers , self.__treeview.item(self.__treeview.selection())['values']))

    def click_on_row(self , primary_keys, headers , selected_row):

        row_data = list(zip(headers,selected_row))

        print(primary_keys)
        keys_values_couples = []

        for couple in row_data :
            for key in primary_keys :
                if couple[0] == key :
                    keys_values_couples.append(couple)

        if self.__record_type =="Table":
            self.__result_table= Second_window(self.__master ,"800x600" , "View Table")
            # Create a scrollable frame inside the window
            scroll_frame = ttk.Frame(self.__result_table.window)
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
            for header, value in zip(headers, selected_row):
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
            update_button = ttk.Button(inner_frame, text="Update", command= lambda :self.__manager.update_row(self.__table ,selected_row , headers,keys_values_couples) )
            update_button.pack(padx=300, pady=10 )

            delete_row_button = ttk.Button(inner_frame, text="Delete row ", command= lambda : self.__manager.delete_row(self.__table ,keys_values_couples))
            delete_row_button.pack(padx=300, pady=10 )

        if self.__record_type == "Search" :
            self.__column_search= Second_window(self.__master ,"800x600" , "View Column")
            table_col_couple = (selected_row[0], selected_row[1])
            columns,rows,prim_key = self.__manager.show_search_records(table_col_couple , self.__search_term)
            self.__column_tree = Records(self.__column_search.window,rows, columns, "Table" ,primary_keys = prim_key ,manager= self.__manager ,table =selected_row[0])


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
        self.__dump_path_entry.grid(row=0, column=0, padx=(10,150), pady=200, sticky="n")

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
        self.__dump_button.grid(row=0, column=0, padx=60, pady=200, sticky="ne")

        def browse_folder():
            folder_selected = tk.filedialog.askdirectory()
            self.__dump_path.set(rf'{folder_selected}')

        self.__browse_button = ttk.Button(self.__master, text="Browse", command=browse_folder )
        self.__browse_button.grid(row=0, column=0, padx=150, pady=200, sticky="ne")


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
            self.__search_tree = Records(self.__search_window.window ,self.__manager.search_database(self.__db, self.__search_term.get()) , ['Table' , 'Column' , 'matches'], "Search" , search_term = self.__search_term.get() , manager=self.__manager)
        else :
            self.__columns , self.__rows = self.__manager.search_table(self.__search_term.get() , self.__db, self.__table)
            self.__primary_keys =self.__manager.get_prim_keys(self.__table)
            self.__search_tree = Records(self.__search_window.window , self.__rows , self.__columns , "Table" , manager= self.__manager , primary_keys = self.__primary_keys , table = self.__table)

class Operation:
    def __init__(self, master , type  , **kwargs) -> None:
        self.__frame = ttk.Frame(master, borderwidth=10, relief="solid", height=60)
        self.__frame.pack(fill='x', padx=kwargs["padx"], pady=kwargs["pady"] , ipady=kwargs["ipady"])
        self.__var = tk.StringVar()

        if type == "Label":
            self.__label = ttk.Label(self.__frame, text=kwargs["title"] , font=('Helvetica' , 12))
            self.__label.pack(side='left',pady=kwargs["type_pady"] , padx =kwargs["type_padx"])
        elif type == "Entry":
            self.__entry = ttk.Entry(self.__frame, textvariable=self.__var, width=60)
            self.__entry.pack(side='left', pady=kwargs["type_pady"], padx=kwargs["type_padx"])
        elif type == "Combobox" :
            self.__combobox = ttk.Combobox(self.__frame, textvariable=self.__var,  values=kwargs["values"] , width=30 , state='readonly')
            self.__combobox.pack(side='left',pady=kwargs["type_pady"] , padx =kwargs["type_padx"])

        self.__button = ttk.Button(self.__frame, text=kwargs["bt_title"] ,width=50)
        self.__button.pack(side='right', padx=kwargs["bt_padx"] , pady=kwargs["but_pady"])

    def set_button_command(self, command):
        self.__button.configure(command=command)
    @property
    def var(self) :
        return self.__var
App()
