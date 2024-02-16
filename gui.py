import customtkinter
import mysql_con

def login_success(frame , host_entry  ,port_entry ,username_entry , password_entry ) :
    con = mysql_con.handle_login(hostname= host_entry.get(),username= username_entry.get(),passw= password_entry.get() , port=port_entry.get())
    if con == True :
        frame.destroy()
        database_menu()


def db_creation_success(db_create_entry):
    cr = mysql_con.create_database(db_create_entry.get())
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


def create_login_page(): 
    frame = customtkinter.CTkFrame(master=app)
    frame.pack(pady=20 , padx=60 , fill="both" , expand=True)

    label = customtkinter.CTkLabel(master=frame, text="Login" , font=("Roboto" , 30))
    label.pack(padx=20 , pady=22)

    host_entry = customtkinter.CTkEntry(frame, placeholder_text="hostname" , height=35)
    host_entry.pack(padx=10,pady=22)

    port_entry = customtkinter.CTkEntry(frame, placeholder_text="port(3306 by default)" , height=35)
    port_entry.pack(padx=10,pady=22)


    username_entry= customtkinter.CTkEntry(frame, placeholder_text="Username" , height=35)
    username_entry.pack(padx=10,pady=22)

    password_entry= customtkinter.CTkEntry(frame, placeholder_text="Password" , show="*" , height=35)
    password_entry.pack(padx=10,pady=22)

    login_button= customtkinter.CTkButton(master=frame , text="Login" , command= lambda:login_success(frame , host_entry , port_entry , username_entry , password_entry))
    login_button.pack(padx=10,pady=22 )

def database_menu():
    menu_frame = customtkinter.CTkScrollableFrame(master=app)
    menu_frame.grid(row=0, column=0 , sticky="ns")
    app.grid_rowconfigure(0, weight=1) 

    db_create_entry = customtkinter.CTkEntry(menu_frame, placeholder_text="New database name" , height=35 )
    db_create_entry.pack(pady=(60,0)) 

    create_database_button = customtkinter.CTkButton(menu_frame,text="Create a new Database" , fg_color="#7019E6",command=lambda:db_creation_success(db_create_entry))
    create_database_button.pack(side="top", pady=(5,50))

    databases = mysql_con.show_databases()
    databases_buttons = [customtkinter.CTkButton(menu_frame,text=database , fg_color="#1929E6", command=lambda db=database: tables_frame(db[0])).pack(side="top", pady=10) for database in databases]


def tables_frame(db_name):
    table_frame = customtkinter.CTkScrollableFrame(master=app)
    table_frame.grid(row=0, column=1 , sticky="nswe")
    app.grid_columnconfigure(1, weight=1) 
    app.grid_rowconfigure(0, weight=1)

    
    button_frame = customtkinter.CTkFrame(master=table_frame)
    button_frame.pack(anchor="ne", padx=10, pady=10)

    drop_db_button = customtkinter.CTkButton(button_frame , text="Drop database" , fg_color="#ff0000"  , command=lambda: drop_db(table_frame,db_name))
    drop_db_button.pack()

    tables = show_db_tables(db_name)
    tables_buttons = [customtkinter.CTkButton(table_frame,text=table, fg_color="#1929E6" , command=lambda : ...).pack(side="top", pady=10) for table in tables]


app = customtkinter.CTk()
app.geometry("1024x768")


create_login_page()

app.mainloop()



