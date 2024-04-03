import tkinter as tk
from tkinter import ttk

def get_all_rows(treeview):
    rows = treeview.get_children()
    return rows

# Create the main window
root = tk.Tk()
root.geometry('400x300')

# Create a TreeView widget
treeview = ttk.Treeview(root)
treeview.pack()

# Insert some items into the TreeView
treeview.insert('', 'end', text='Item 1')
treeview.insert('', 'end', text='Item 2')
treeview.insert('', 'end', text='Item 3')

# Get all rows from the TreeView
all_rows = get_all_rows(treeview)
print("All rows:", all_rows)

root.mainloop()
