from tkinter import *
from tkinter import ttk
from tkinter.ttk import Combobox

from commands import *
from colors import *
from custom import *
import pandas as pd
from tkinter import messagebox
import ttkbootstrap as tb

def get_order_map(table,keys):
    old_map = [i for i in range(len(keys))]
    try:
        order = custom[table]["order"]
        new_map = []
        columns = list(keys)
        for field in order:
            index = columns.index(field)
            new_map.append(index)
            old_map.remove(index)
        new_map.extend(old_map)
        #print("get_order_map:",table,new_map)
        return new_map
    except:
        print("---------- get order map error --------",table)
        return old_map



class TableUI(Frame):
    def __init__(self,parent,table_name,df,custom_dict):
        super().__init__(parent,bg="yellow")

        self.table_name = table_name
        self.df = df
        self.custom = custom_dict
        self.filters = self.custom.get("filters", [])

        print("TableUI: custom:")
        print(self.custom)


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
        self.filter_stack = []
        #self.filter_controls = []

        self.reqwidth = 0
        self.filtered_df = df.copy()


    def set_tree_columns(self):
        order_map = get_order_map(self.table_name,self.df.columns)

        columns = [self.df.columns[x] for x in order_map]

        self.my_tree['columns'] = tuple(columns)

        print(columns)

        self.my_tree.column("#0", width=0, stretch=NO)
        for heading in columns:
            self.my_tree.column(heading,anchor = W, width = 140)

        self.my_tree.heading("#0", text="", anchor=W)


        for heading in columns:
            self.my_tree.heading(heading, text=heading, anchor=W)

    def set_tree_body_df(self):

        for item in self.my_tree.get_children():
            self.my_tree.delete(item)

        order_map = get_order_map(self.table_name, self.filtered_df.columns)

        for count in range(0, len(self.filtered_df)):

            row = self.filtered_df.iloc[count].tolist()

            values = []

            for o in order_map:
                entry = row[o]

                if 'datetime' in str(self.filtered_df[self.filtered_df.columns[o]].dtypes):
                    entry = str(entry).split()[0]
                    if entry == "NaT":
                        entry = ""
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


    def set_tree_body_pl(self):
        count = 0

        order_map = get_order_map(self.table_name,self.df.columns)

        dtypes = self.df.columns.d

        for row in self.df.iter_rows():

            values = []

            for o in order_map:
                entry = row[o]

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

    def control_in_filter_stack(self,control):
        for stack_control,name in self.filter_stack:
            if control == stack_control:
                return True
        return False

    def set_filters(self):
        print("set_filters:")
        print("len:",len(self.filters),len(self.filters))
        for filter in self.filters:
            print("filter:",filter)
            if not self.control_in_filter_stack(filter.control):
                print("set_filters:",filter)
                print("set_filters",self.filtered_df[filter.field])
                unique_entries = sorted(self.filtered_df[filter.field].unique())
                print("unique:",unique_entries)
                filter.control['values'] = tuple(unique_entries)

    def create_filtered_df(self):
        print("create_filtered_df")
        self.filtered_df = self.df.copy()
        print("create_filtered_df start:",len(self.filtered_df))


        for control,name in self.filter_stack:
            print("filter:",name,control.get(),self.filtered_df[name].dtype,type(control.get()))
            converted_value = self.convert_by_dtype(control.get(),self.df[name].dtype)
            self.filtered_df = self.filtered_df[(self.filtered_df[name] == converted_value)]
            print("filter_df",len(self.filtered_df))

        print("create_filtered_df end:",len(self.filtered_df))

    def combobox_changed(self,event,control,filter_name):
        print("combo_changed")

        try:
            index = self.filter_stack.index((control,filter_name))
            while index + 1 < len(self.filter_stack):
                last,name = self.filter_stack.pop()
                print("popping",last,name)
                last.set("")
        except:
            self.filter_stack.append((control,filter_name))

        self.create_filtered_df()
        self.set_filters()

        if glb.USE_DF:
            self.set_tree_body_df()
        if glb.USE_PL:
            self.set_tree_body_pl()


    def create_controls(self):
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

        #filters = self.custom.get("filters", [])

        for x,filter in enumerate(self.filters):
            fn_label = Label(self.filter_frame, text=filter.field)
            fn_label.grid(row=0, column=x, padx=5, pady=5)
            fn_entry = Combobox(self.filter_frame,justify=LEFT)
            fn_entry.grid(row=1, column=x, padx=5, pady=5)
            fn_entry.bind("<<ComboboxSelected>>",
                lambda event, combobox_instance=fn_entry,filter_name = filter.field: self.combobox_changed(event,combobox_instance,filter_name))
            filter.set_control(fn_entry)

            #self.filter_controls.append(filter)

        #if len(self.filter_controls):
        if len(self.filters):
            bt = Button(self.filter_frame,text = "Clear",command = self.clear_filters)
            bt.grid(row=1,column=len(self.filters),padx=5,pady=5)
            bt = Button(self.filter_frame,text = "Debug",command  = self.debug )
            bt.grid(row=1,column = len(self.filters)+1,padx=5,pady=5)


        order_map = get_order_map(self.table_name,self.df.columns)
        columns = [self.df.columns[x] for x in order_map]

        # create record frame entries
        for x,column in enumerate(columns):
            fn_label = Label(self.record_frame, text=column)
            fn_label.grid(row=int(x/4), column=(2 * x) % 8, padx=10, pady=5)

            dtype = self.df[column].dtype


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

    def clear_filters(self):
        print("clear_filters")
        self.filter_stack = []
        for control in self.filter_controls:
            control.set("")
        self.filtered_df = self.df.copy()
        self.set_filters()
        self.delete_and_replace()

    def on_treeview_scroll(self,event):
        scroll_position = self.my_tree.yview()


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
        print("selected:",self.tree_focus())
        # Grab record values
        values = self.my_tree.item(self.tree_focus(), 'values')

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

    def convert_by_dtype(self,new_value:str,column_dtype):
        #print("convert_by_dtype",self.df[self.df.columns[column]].dtype)

        #column_dtype = self.df[self.df.columns[column]].dtype

        print("convert_by_dtype;",column_dtype,new_value)
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
        print("convert by dtype:",new_value,column_dtype)
        converted_value = series.astype(column_dtype).iloc[0]

        #print("convert_by_dtype returns:",converted_value,type(converted_value))

        return converted_value

    def get_converted_row_values(self):

        order_map = get_order_map(self.table_name,self.df.columns)

        row_vals = [0] * len(self.records)
        for record,order in zip(self.records,order_map):
            try:
                rval = record.entry.get() if 'DateEntryx' in str(type(record)) else record.get()

                cval = self.convert_by_dtype(rval, self.df[self.df.columns[order]].dtype)
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
            row_vals = [ self.convert_by_dtype(self.records[order].get(),self.df[order].dtype) for order in order_map]
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

        selected = self.tree_focus()
        if not selected:
            messagebox.showinfo("Notification", "No entry selected")
            return

        row_vals = self.get_converted_row_values()

        if not row_vals:
            return

        print("update_record",selected)

        if glb.USE_DF:
            self.df.iloc[selected] = row_vals
        if glb.USE_PL:
            pass

        self.delete_and_replace()



        print("update_record")
        pass

    def remove_one(self):
        if self.blank_check():
            return

        selected = self.tree_focus()
        if not selected:
            messagebox.showinfo("Notification", "No entry selected")
            return


        self.filtered_df.drop(selected,inplace=True)

        self.delete_and_replace()
        print("remove_one")

    def clear_entries(self):
        print("clear_entries")
        for record in self.records:
            record.delete(0,END)

    def debug(self):
        print("focus:",self.tree_focus(),type(self.tree_focus()))
        pass

    def tree_focus(self):
        focus = self.my_tree.focus()
        print("len tree_focus",len(focus))
        if focus == "":
            return None
        return int(focus)


class ComboBoxC():
    def __init__(self,field):
        self.field = field
    def set_control(self,control):
        self.control = control