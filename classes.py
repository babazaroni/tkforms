from tkinter import *
from tkinter import ttk
from commands import *
from colors import *
from custom import *
import pandas as pd
from tkinter import messagebox
import ttkbootstrap as tb


class TableUI(Frame):
    def __init__(self,parent,table_name):
        super().__init__(parent,bg="yellow")

        self.table_name = table_name

        self.filter_frame = LabelFrame(self,text = "Filter",bg = "red")
        self.filter_frame.pack(fill="x", expand=True, padx=20)

        self.tree_frame = LabelFrame(self,text = table_name,bg = "green")
        self.tree_frame.pack(pady=10)

        self.record_frame = LabelFrame(self, text = "Record")
        self.record_frame.pack(fill="x", expand=True, padx=20)

        self.button_frame = LabelFrame(self, text = "Commands")
        self.button_frame.pack(fill="x", expand=True, padx=20)

        # Create a Treeview Scrollbar
        self.tree_scrolly = Scrollbar(self.tree_frame)
        self.tree_scrolly.pack(side=RIGHT, fill=Y)
        #self.tree_scrollx = Scrollbar(self.tree_frame)
        #self.tree_scrollx.pack(side=BOTTOM, fill=Y)

        # Create The Treeview
        #self.my_tree = ttk.Treeview(self.tree_frame, yscrollcommand=self.tree_scrolly.set,
        #                            #xscrollcommand=self.tree_scrollx.set,
        #                            selectmode="extended")

        self.my_tree = tb.Treeview(self.tree_frame,style='info.Treeview')

        #self.my_tree.grid(row = 0, column = 0)

        self.my_tree.bind("<ButtonRelease-1>", self.select_record)
        self.my_tree.bind("<Configure>", self.on_treeview_scroll)



        #fn_label = Label(data_frame, text="First Name")
        #fn_label.grid(row=0, column=0, padx=10, pady=10)
        #fn_entry = Entry(data_frame)
        #fn_entry.grid(row=0, column=1, padx=10, pady=10)

        self.update_button = Button(self.button_frame, text="Update Record", command=self.update_record)
        #self.update_button.pack()
        self.add_button = Button(self.button_frame, text="Add Record", command=self.add_record)
        self.remove_one_button = Button(self.button_frame, text="Remove Record", command=self.remove_one)
        self.select_record_button = Button(self.button_frame, text="Clear Record", command=self.clear_entries)

        self.records = []
        self.selected = 0
        self.df = None

        print("------------------------------- setting req width -----------------------------")
        self.reqwidth = 0


    def set_tree_columns(self,df):
        order_map = get_order_map(self.table_name,df.columns)

        columns = [df.columns[x] for x in order_map]

        self.my_tree['columns'] = tuple(columns)

        print(columns)

        self.my_tree.column("#0", width=0, stretch=NO)
        for heading in columns:
            self.my_tree.column(heading,anchor = W, width = 140)

        self.my_tree.heading("#0", text="", anchor=W)


        for heading in columns:
            self.my_tree.heading(heading, text=heading, anchor=W)

    def set_tree_body_df(self):

        order_map = get_order_map(self.table_name, self.df.columns)

        for count in range(0, len(self.df)):

            row = self.df.iloc[count].tolist()

            values = []

            for o in order_map:
                entry = row[o]
                print('addd:', self.df.columns[o], self.df[self.df.columns[o]].dtypes)
                if 'datetime' in str(self.df[self.df.columns[o]].dtypes):
                    entry = str(entry).split()[0]
                    values.append(entry)
                else:
                    values.append(entry)

            #values = [row[o] for o in order_map]

            tp = tuple(values)

            if count % 2 == 0:
                self.my_tree.insert(parent='', index='end', iid=count, text='',
                                    values=tp,
                                    tags=('evenrow',))
            else:
                self.my_tree.insert(parent='', index='end', iid=count, text='',
                                    values=tp,
                                    tags=('oddrow',))

        self.reqwidth = self.my_tree.winfo_reqwidth()

    def set_tree_df(self,df):
        self.df = df

    def set_tree_body_pl(self):
        count = 0

        order_map = get_order_map(self.table_name,self.df.columns)

        dtypes = self.df.columns.d

        for row in self.df.iter_rows():

            values = []

            for o in order_map:
                entry = row[o]
                print('addd:', self.df.columns[o], self.df.columns[o].dtypes)
                if 'datetime' in str(self.df.columns[o].dtypes):
                    entry = entry.split()[0]
                    values.append(entry)
                else:
                    values.append(entry)

            #Wvalues = [row[o] for o in order_map]

            tp = tuple(values)

            if count % 2 == 0:
                self.my_tree.insert(parent='', index='end', iid=count, text='',
                               values=tp,
                               tags=('evenrow',))
            else:
                self.my_tree.insert(parent='', index='end', iid=count, text='',
                               values=tp,
                               tags=('oddrow',))
            # increment counter
            count += 1


    def create_controls(self,table_df,filters):
        # Add Filter Boxes

        #fn_labelx = Label(filter_frame, text="First Name")
        #fn_labelx.grid(row=0, column=0, padx=10, pady=1)
        #fn_entryx = Entry(filter_frame)
        #fn_entryx.grid(row=1, column=0, padx=10, pady=1)

        self.my_tree.pack()

        # Configure the Scrollbar
        self.tree_scrolly.config(command=self.my_tree.yview)
        #self.tree_scrollx.config(command=self.my_tree.xview)
        # tree_scroll.config(command=my_tree.xview)

        # set_tree_columns()

        # Create Striped Row Tags
        self.my_tree.tag_configure('oddrow', background=glb.saved_secondary_color)
        self.my_tree.tag_configure('evenrow', background=glb.saved_primary_color)

        for x,filter_name in enumerate(filters):
            fn_label = Label(self.filter_frame, text=filter_name)
            fn_label.grid(row=0, column=x, padx=5, pady=5)
            fn_entry = Entry(self.filter_frame,justify=LEFT)
            fn_entry.grid(row=1, column=x, padx=5, pady=5)

        order_map = get_order_map(self.table_name,table_df.columns)
        columns = [table_df.columns[x] for x in order_map]

        # create record frame entries
        for x,column in enumerate(columns):
            fn_label = Label(self.record_frame, text=column)
            fn_label.grid(row=int(x/4), column=(2 * x) % 8, padx=10, pady=5)

            dtype = table_df[column].dtype


            fn_entry = Entry(self.record_frame)
            if 'datetime' in str(dtype):
                dateformat = "%Y-%m-%d %H:%M:%S"
                dateformat = "%Y-%m-%d"
                fn_entry = tb.DateEntry(self.record_frame, bootstyle="dark",dateformat = dateformat)
                fn_entry.entry.delete(0, END)
                self.records.append(fn_entry.entry)
            else:
                self.records.append(fn_entry)


            fn_entry.grid(row=int(x/4), column=(2 * x) % 8 + 1, padx=10, pady=5)



        self.update_button.grid(row=0, column=0, padx=10, pady=10)
        self.add_button.grid(row=0, column=1, padx=10, pady=10)
        self.remove_one_button.grid(row=0, column=3, padx=10, pady=10)
        self.select_record_button.grid(row=0, column=7, padx=10, pady=10)


        # Add Record Entry Boxes
        pass

    def on_treeview_scroll(self,event):
        scroll_position = self.my_tree.yview()
        print("Treeview scrolled to position:", scroll_position)

    def get_first_displayed_row(self):
        min_scroll, max_scroll = self.my_tree.yview()

        # Get the total number of items in the treeview
        total_items = self.my_tree.get_children()

        # Calculate the index of the first visible item
        first_visible_index = int(min_scroll * len(total_items))

        print("first_visible_index:",first_visible_index)

        return first_visible_index


    def select_record(self,event):

        if self.my_tree.focus() == '':
            print("select_record: no entry selected")
            return

        for record in self.records:

            #if 'DateEntry' in str(type(record)):
            #    record.entry.delete(0,END)
            #else:
            record.delete(0,END)

        # Grab record Number
        self.selected = int(self.my_tree.focus())
        print("selected:",self.selected)
        # Grab record values
        values = self.my_tree.item(self.selected, 'values')

        for i,record in enumerate(self.records):
            #if 'DateEntry' in str(type(record)):
            #    record.insert(0,values[i]) #xxx
            #else:
            record.insert(0,values[i])

    def blank_check(self):
        for record in self.records:
            print("blank check:",record.get())
            if record.get() != "":
                return False

        return True

    def delete_and_replace(self):
        self.my_tree.delete(*self.my_tree.get_children())

        if glb.USE_DF:
            self.set_tree_body_df()
        if glb.USE_PL:
            self.set_tree_body_pl()

    def convert_by_dtype(self,new_value:str,column):
        #print("convert_by_dtype",self.df[self.df.columns[column]].dtype)

        column_dtype = self.df[self.df.columns[column]].dtype

        print("convert_by_dtype;",column,column_dtype,new_value)
        print("new value:",new_value,"dtype:",type(new_value))

        if column_dtype == "bool":

            if new_value.lower() not in ['true','false','yes','no']:
                5/0  # should do a real exception instead

            if new_value.capitalize() in ['False','No']:
                new_value = ''
            else:
                new_value = 'True'

            print("its a bool")

        series = pd.Series([new_value])
        converted_value = series.astype(column_dtype).iloc[0]

        #print("convert_by_dtype returns:",converted_value,type(converted_value))

        return converted_value

    def get_converted_row_values(self):

        order_map = get_order_map(self.table_name,self.df.columns)

        row_vals = [0] * len(self.records)
        for record,order in zip(self.records,order_map):
            try:
                rval = record.entry.get() if 'DateEntryx' in str(type(record)) else record.get()

                cval = self.convert_by_dtype(rval, order)
                row_vals[order] = cval
            except:
                messagebox.showinfo("Notification",f"Invalid format for {self.df.columns[order]}")
                return None

        return row_vals

    def add_record(self):
        if self.blank_check():
            return

        order_map = get_order_map(self.table_name,self.df.columns)

        row_vals = self.get_converted_row_values()

        if not row_vals:
            return

        try:
            row_vals = [ self.convert_by_dtype(self.records[order].get(),order) for order in order_map]
        except:
            pass

        if glb.USE_DF:
            self.df.loc[len(self.df)] = row_vals
        if glb.USE_PL:
            pass

        self.delete_and_replace()




    def update_record(self):
        if self.blank_check():
            return

        row_vals = self.get_converted_row_values()

        if not row_vals:
            return

        print("update_record",self.selected,type(self.selected))

        if glb.USE_DF:
            self.df.iloc[self.selected] = row_vals
        if glb.USE_PL:
            pass

        self.delete_and_replace()



        print("update_record")
        pass

    def remove_one(self):
        if self.blank_check():
            return

        self.df.drop(self.selected,inplace=True)

        self.delete_and_replace()
        print("remove_one")

    def clear_entries(self):
        print("clear_entries")
        for record in self.records:
            record.delete(0,END)


