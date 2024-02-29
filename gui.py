import customtkinter
import mysql_con
from tkinter import ttk
import tkinter as tk
import ttkbootstrap
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

def show_columns(table_frame,table):
    table_frame.destroy()
    columns_frame(table)

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


    drop_button_frame = customtkinter.CTkFrame(master=table_frame)
    drop_button_frame.pack(anchor="ne", padx=10, pady=10)

    create_table_frame = customtkinter.CTkFrame(master=table_frame)
    create_table_frame.pack(anchor="ne" ,padx=10 , pady=15)

    create_table_button =customtkinter.CTkButton(create_table_frame , text="Create new Table" , fg_color="#ff0000" , command=lambda:table_create_page(table_frame))
    create_table_button.pack()
    drop_db_button = customtkinter.CTkButton(drop_button_frame , text="Drop database" , fg_color="#ff0000"  , command=lambda: drop_db(table_frame,db_name))
    drop_db_button.pack()

    tables = show_db_tables(db_name)
    tables_buttons = [customtkinter.CTkButton(table_frame,text=table, fg_color="#1929E6" , command=lambda : show_columns(table_frame,table[0])).pack(side="top", pady=10) for table in tables]
 
    # there is a bug here i think the table var that is being sent isnt correct 

def table_create_page(frame):
    frame.destroy()
    newtb_create_frame = customtkinter.CTkScrollableFrame(master=app)


def columns_frame(table):
    columns , rows = mysql_con.show_table_records(table)
    style = ttkbootstrap.Style(theme="darkly")
    treeframe = ttk.Frame(app)
    treeframe.grid(column= 1  , row=0 , sticky = "nswe")
    app.grid_rowconfigure(0, weight=1) 
    app.grid_columnconfigure(1, weight=1) 

    style.theme_use()
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

 
app = customtkinter.CTk()
app.geometry("1024x768")


create_login_page()

app.mainloop()



