
from tkinter import *
from commands import *
#import customtkinter as ctk

from configparser import ConfigParser
from tkinter import filedialog
from db import *
#import ttkbootstrap as tb

from tkinter import ttk
from tkinter import messagebox

import globals as glb
from colors import *
from classes import *
from commands import *


def set_tablex(table):
    global content_dict
    print("set_table:",table)

    #for item in content_frame.winfo_children():
    #    item.destroy()

    content_dict[table].pack()


def prompt_for_db():
    global root
    global content
    global content_dict
    global notebook

    file_path  = filedialog.askopenfilename(filetypes=[("Access DB","*.accdb")])
    if isinstance(file_path,str):
        print("file_path:",file_path)
        #try:
        process_db(file_path)


        for x,table in enumerate(glb.tables_dict.keys()):
            #Button(table_frame, text=table, command = lambda t=table:set_table(t)).grid(row=0, column=x, padx=10, pady=10)
            tab = ttk.Frame(notebook)
            notebook.add(tab,text = table)
            tableui = TableUI(tab, table)
            tableui.create_controls(glb.tables_dict[table], ["Client ID", "Project ID", "Primary"])
            tableui.set_tree_columns(glb.tables_dict[table])

            tableui.set_tree_df(glb.tables_dict[table])

            if glb.USE_DF:
                tableui.set_tree_body_df()
            if glb.USE_PL:
                tableui.set_tree_body_pl()

            tableui.grid(row=0, column=0,sticky = "w")
            #content.pack()

        #set_table("Project Data")
        #set_table("Client ID")


def get_selected_tab_widget():
    # Get the ID of the selected tab
    selected_tab = notebook.select()

    # Get the widget associated with the selected tab (it will be a frame)
    widget_in_selected_tab = notebook.nametowidget(selected_tab)

    for child in widget_in_selected_tab.winfo_children():
        print(selected_tab,child.reqwidth)
        width = child.reqwidth
        if width < 1000:
            width = 1000

        root.geometry(f"{width+10}x800")

    return widget_in_selected_tab


def on_tab_changed(event):
    # Get the widget in the selected tab and print its type
    widget_in_selected_tab = get_selected_tab_widget()

    print(f"Widget in selected tab: {widget_in_selected_tab} {widget_in_selected_tab.winfo_reqwidth()} ")




no_project_file = "No Project DB Specified"

root = Tk()
#root = tb.Window(themename="superhero")
root.title('Access Forms')
#root.iconbitmap('c:/gui/codemy.ico')

root.geometry("500x100")



#ctk.set_appearance_mode("System")
#ctk.set_default_color_theme("blue")
#ctk.set_appearance_mode("dark")
#ctk.set_default_color_theme("dark-blue")

#root = ctk.CTk()
#root.geometry("500x200")
#root.title("Access Forms")

# Read our config file and get colors
parser = ConfigParser()
parser.read("accessforms.ini")

color_init(parser)

source_frame = LabelFrame(root,text = "Source",bg="blue")
source_frame.pack(fill="x", expand=True, padx=20,pady=5)

bt = Button(source_frame,text = "Open DB",command = prompt_for_db)
bt.grid(row = 0,column = 0)
file_path_project = Label(source_frame,text= glb.dev_path if glb.DEV else no_project_file)
file_path_project.grid(row = 0, column = 1)

#table_frame = LabelFrame(root,text = "Table")
#table_frame.pack(fill="x", expand=True, padx=20,pady=5)

notebook = ttk.Notebook(root)
notebook.pack()

notebook.bind("<<NotebookTabChanged>>", on_tab_changed)


#content_frame = Frame(root)
#content_frame.pack(fill="x", expand=True, padx=20)



root.mainloop()


