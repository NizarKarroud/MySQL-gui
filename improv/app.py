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
            del self



        
App()