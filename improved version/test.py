import tkinter as tk

# Create the main application window
root = tk.Tk()
root.title("Welcome to MySQL Manager")
root.geometry("600x600")

# Function to simulate hyperlink clicks
def show_message(message):
    tk.messagebox.showinfo("Information", message)

# Create a scrollable frame
canvas = tk.Canvas(root)
scroll_y = tk.Scrollbar(root, orient="vertical", command=canvas.yview)

frame = tk.Frame(canvas)
frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=frame, anchor="nw")
canvas.configure(yscrollcommand=scroll_y.set)

# Header
header_label = tk.Label(frame, text="Welcome to MySQL Manager", font=("Helvetica", 16, "bold"))
header_label.pack(pady=10)

subheader_label = tk.Label(frame, text="Manage Your MySQL Databases with Ease", font=("Helvetica", 12))
subheader_label.pack()

welcome_text = tk.Label(
    frame,
    text=(
        "Welcome to MySQL Manager, your ultimate solution for efficiently managing and navigating "
        "your MySQL databases. Our application provides you with all the tools you need to connect, "
        "create, and manage databases seamlessly."
    ),
    font=("Helvetica", 10),
    wraplength=550,
    justify="left"
)
welcome_text.pack(pady=10)

# Key Features
features_label = tk.Label(frame, text="Key Features:", font=("Helvetica", 12, "bold"))
features_label.pack(anchor="w", padx=10)

features_text = """
- Database Management: Create, drop, rename databases, create triggers, and view database tables.
- Search Functionality: Search for terms within databases or tables.
- SQL Query Execution: Execute custom SQL queries and view the results.
- Table Operations: View records, drop columns, create, rename, drop, and empty tables.
- Data Manipulation: Insert, update, and delete records within tables.
- Export and Import Data: Export databases/tables to CSV/HTML files or SQL dump files, and import data from SQL dump files.
- Copy Database: Copy entire databases easily.
- Visualize Column Data: Graph column data for better insights.
- Customizable Themes: Choose from multiple themes to customize the interface to your preference.
"""
features_text_label = tk.Label(frame, text=features_text, font=("Helvetica", 10), justify="left")
features_text_label.pack(anchor="w", padx=10)

# User Guide
guide_frame = tk.Frame(frame)
guide_frame.pack(pady=10)

guide_label = tk.Label(guide_frame, text="New Here?", font=("Helvetica", 12, "bold"))
guide_label.pack(anchor="w", padx=10)

guide_text = tk.Label(
    guide_frame,
    text="Check out our User Guide to get started and make the most out of MySQL Manager.",
    font=("Helvetica", 10),
    fg="blue",
    cursor="hand2"
)
guide_text.pack(anchor="w", padx=10)
guide_text.bind("<Button-1>", lambda e: show_message("User Guide"))

# Add scrollbar to the canvas
canvas.pack(side="left", fill="both", expand=True)
scroll_y.pack(side="right", fill="y")

# Run the application
root.mainloop()
