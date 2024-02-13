import customtkinter
import mysql_con

app = customtkinter.CTk()
app.geometry("800x600")

frame = customtkinter.CTkFrame(master=app)
frame.pack(pady=20 , padx=60 , fill="both" , expand=True)

label = customtkinter.CTkLabel(master=frame, text="Login" , font=("Roboto" , 30))
label.pack(padx=20 , pady=22)

host_entry = customtkinter.CTkEntry(frame, placeholder_text="hostname" , height=35)
host_entry.pack(padx=10,pady=22)


username_entry= customtkinter.CTkEntry(frame, placeholder_text="Username" , height=35)
username_entry.pack(padx=10,pady=22)

password_entry= customtkinter.CTkEntry(frame, placeholder_text="Password" , show="*" , height=35)
password_entry.pack(padx=10,pady=22)

login_button= customtkinter.CTkButton(master=frame , text="Login" , command=mysql_con.handle_login(hostname= host_entry.get(),username= username_entry.get(),passw= password_entry.get()))
login_button.pack(padx=10,pady=22 )


app.mainloop()

