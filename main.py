
from tkinter import *
from commands import *
#import customtkinter as ctk

from custom import *

from configparser import ConfigParser
from tkinter import filedialog
from db import *
import ttkbootstrap as tb

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

def get_table_order():
    order = []
    source = list(glb.tables_dict.keys())
    for t in custom_dict["TableOrder"]:
        if t in source:
            order.append(t)
            source.remove(t)
    order.extend(source)

    return order


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
        file_path_project["text"] = file_path


        for x,table in enumerate(get_table_order()):
            #Button(table_frame, text=table, command = lambda t=table:set_table(t)).grid(row=0, column=x, padx=10, pady=10)
            tab = ttk.Frame(notebook)
            notebook.add(tab,text = table)


            tableui = TableUI(root,tab, table,custom_dict["Tables"].get(table,{}))

            tab_table_map[tab] = tableui

            tableui.create_maps()  # linkxxx create map when table created
            tableui.create_controls()
            tableui.create_tree_columns()
            tableui.set_filters()
            tableui.create_filtered_df()

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
    selected_index = notebook.index(notebook.select())

    selected_tab_text = notebook.tab(selected_index, "text")

    #width = custom_dict["Tables"].get(selected_tab_text,{}).get('width',1000)

    #root.geometry(f"{width}x960")
    #root.geometry(f"{width}x1100")

    # Get the widget associated with the selected tab (it will be a frame)

    widget_in_selected_tab = notebook.nametowidget(selected_tab)
    max_width = 1000
    for child in widget_in_selected_tab.winfo_children():
        print(selected_tab,child.reqwidth)
        width = child.reqwidth
        if width > max_width:
            max_width = width

    #print("------------------------------------- max_width ----------------------------------",max_width,selected_tab_text)


    #    width = custom[selected_tab]['width']

    #    root.geometry(f"{width+30}x900")

    return widget_in_selected_tab,max_width


def on_tab_changed(event):
    # Get the widget in the selected tab and print its type
    widget_in_selected_tab,max_width = get_selected_tab_widget()
    max_width *= 1.0

    table = tab_table_map[widget_in_selected_tab]

    x = table.master_frame.winfo_height()
    print("height:",x)
    print("pos: y",table.master_frame.winfo_y())
    print("pos: x",table.master_frame.winfo_x())

    root.geometry(f"{max(table.width+100,1000)}x1100")

    #root.geometry(f())


    #'width'

    #root.geometry(f"{int(max_width)}x900")

    #print(f"Widget in selected tab: {widget_in_selected_tab} {widget_in_selected_tab.winfo_reqwidth()} ")




no_project_file = "No Project DB Specified"

#root = Tk()
root = tb.Window(themename="united")  # darkly, flatly, journal, litera, minty, pulse, sandstone,simplex, superhero, cosmo, united
root.title('Access Forms')
#root.iconbitmap('c:/gui/codemy.ico')

root.tk.call('tk', 'scaling', 2.0)  #Works with straight Tk()
#root.option_add('*TButton.font', ('Arial', 24))
root.option_add('*Font', ('Arial', 12, 'bold')) #works with straight Tk() only
#root.geometry("600x140")



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

tab_table_map = {}
notebook = ttk.Notebook(root)
#notebook.pack(fill='both', expand=True)
notebook.pack(padx = 20)

notebook.bind("<<NotebookTabChanged>>", on_tab_changed)
# Configure the font for Notebook tabs
style = tb.Style()
style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'))
style.configure("Custom.TLabel", # has effect
                font=("Arial", 12),
                foreground="#e95420")
style.configure("Treeview", # has effect
                font=("Arial", 12, "bold"))

#ARGB #ffff0000   red
#CMYK 0,255,255,0 red

#ARGB #ffff5500 orange

#content_frame = Frame(root)
#content_frame.pack(fill="x", expand=True, padx=20)


root.mainloop()

