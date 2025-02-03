from tkinter import *
from tkinter import ttk
from tkinter.ttk import Combobox

#from commands import *
from colors import *
from custom import custom_dict
import pandas as pd
from tkinter import messagebox
import ttkbootstrap as tb

import traceback


class TableUI(Frame):
    def __init__(self,parent,table_name,custom_dict):
        super().__init__(parent,bg="yellow")

        self.table_name = table_name
        self.custom = custom_dict
        self.filters = self.custom.get("filter", [])
        self.sort_optional = self.custom.get("sort_optional", [])
        self.sort = self.custom.get("sort",[])

        self.field_maps = {}

        self.df = glb.tables_dict[table_name]
        #self.df = None
        #self.refresh_df()

        self.selected_record = None

        #print("TableUI: custom:")
        #print(self.custom)

        self.filtersort_frame = Frame(self)
        self.filtersort_frame.pack(pady=10)
        self.filter_frame = LabelFrame(self.filtersort_frame,text = "Filter",bg = "red")
        self.filter_frame.grid(row=0,column = 0,padx=5,pady=5)
        self.sort_frame = LabelFrame(self.filtersort_frame,text = "Sort",bg = "red")
        self.sort_frame.grid(row = 0,column = 1,padx=5,pady=5)
        self.filter_command_frame = LabelFrame(self.filtersort_frame, bg="red")
        self.filter_command_frame.grid(row=0, column=2, padx=5, pady=5)

        self.tree_frame = LabelFrame(self,text = table_name,bg = "green")
        self.tree_frame.pack(pady=10)

        self.record_frame = LabelFrame(self, text = "Record")
        self.record_frame.pack(fill="x", expand=True, padx=20)

        self.button_frame = LabelFrame(self, text = "Actions")
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

 # Change font family and size here

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
        self.filtered_df = self.df.copy()

    def refresh_df(self):
        if glb.ALCHEMY:
            self.df = pd.read_sql_table(self.table_name, con=glb.engine)
        else:
            self.df = pd.read_sql(f"select * from [{self.table_name}]", glb.cnn)

        self.df.fillna('', inplace=True)
        glb.tables_dict[self.table_name] = self.df

    def save_df(self):
        if glb.ALCHEMY:
            self.df.to_sql(self.table_name, con=glb.engine, if_exists='replace', index=False)
        else:
            #self.df.to_sql(self.table_name, glb.cnn, if_exists='replace', index=False)
            self.df.to_sql("[Project Data]", glb.cnn, if_exists='replace', index=False)


    def set_tree_columns(self):
        order_map = get_order_map(self.table_name,self.df.columns)

        columns = [self.df.columns[x] for x in order_map]

        self.my_tree['columns'] = tuple(columns)

        #print("xxxxxxxxxxxxxxxxxxxxxxx   set_tree_columns",columns,order_map)

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
            index = self.filtered_df.iloc[count].name
            #print("set_tree_body_df:",count,index)
            #debug_row = self.df.iloc[index].tolist()
            #print("debug_row:",debug_row)

            values = []

            for o in order_map:
                entry = row[o]
                column = self.df.columns[o]
                if column in self.field_maps.keys():
                    link = self.field_maps[column]
                    entry = link.map_to[entry]

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

    def create_maps(self):
        links = custom_dict["Tables"].get(self.table_name, {}).get('links', [])
        for link in links:
            print("link:",link)
            dest_df = glb.tables_dict[link.dest_table]
            print("dest_df:",dest_df)
            link.map_to = dict(zip(dest_df[link.match_field],dest_df[link.dest_field]))
            link.map_from = dict(zip(dest_df[link.dest_field],dest_df[link.match_field]))
            self.field_maps[link.source_field] = link


    def get_linked_entries(self,filter,unique_entries):
        links = custom_dict["Tables"].get(self.table_name, {}).get('links', [])
        #print("get_linked_entries:",self.table_name)
        #print(links)
        for link in links:
            #print("link",filter.field,link.source_field)
            if filter.field == link.source_field:
                #print("get_linked_entries:",link.dest_table)
                dest_df = glb.tables_dict[link.dest_table]
                #corresponding_values = dest_df[dest_df[link.match_field].isin(unique_entries)][link.dest_field].tolist()
                corresponding_values = [link.map_to[key] for key in unique_entries if key in link.map_to]
                #print("corresponding values:",corresponding_values)

                return sorted(corresponding_values)

        return unique_entries

    def set_filters(self):
        #print("set_filters:")
        #print("len:",len(self.filters),len(self.filters))
        for filter in self.filters:
            #print("filter:",filter)
            if not self.control_in_filter_stack(filter.control):
                #print("set_filters:",filter)
                #print("set_filters",self.filtered_df[filter.field])

                #print("self.filtered:",self.filtered_df[filter.field])
                #print("filtered_df:",filter.field)
                unique_entries = sorted(self.filtered_df[filter.field].unique())

                unique_entries = self.get_linked_entries(filter,unique_entries)


                #print("unique:",unique_entries)
                filter.control['values'] = tuple(unique_entries)

    def sort_filtered_df_optional(self):
        for x,sorter in enumerate(self.sort_optional):
            #print("sort_filtered_df:",sorter.ivar.get())
            if sorter.ivar.get():
                self.filtered_df = self.filtered_df.sort_values(by=sorter.field)

    def sort_filtered_df(self):
        self.filtered_df = self.filtered_df.sort_values(by=self.sort)

    def create_filtered_df(self):
        #print("create_filtered_df")
        self.filtered_df =self.df.copy()
       # print("create_filtered_df start:",len(self.filtered_df))


        for control,name in self.filter_stack:
            print("filter:",name,control.get(),self.filtered_df[name].dtype,type(control.get()))
            control_val = control.get()

            print("create filtered df",name,self.field_maps.keys())
            if name in self.field_maps.keys():
                link = self.field_maps[name]
                control_val = link.map_from[control_val]

            converted_value = self.convert_by_dtype(control_val,self.df[name].dtype)
            self.filtered_df = self.filtered_df[(self.filtered_df[name] == converted_value)]
            #print("filter_df",len(self.filtered_df))

        self.sort_filtered_df_optional()

        self.sort_filtered_df()

        #print("create_filtered_df end:",len(self.filtered_df))

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
            fn_label = tb.Label(self.filter_frame, text=filter.field, style="Custom.TLabel")
            fn_label.grid(row=0, column=x, padx=5, pady=5)
            fn_entry = Combobox(self.filter_frame,justify=LEFT)
            fn_entry.grid(row=1, column=x, padx=5, pady=5)
            fn_entry.bind("<<ComboboxSelected>>",
                lambda event, combobox_instance=fn_entry,filter_name = filter.field: self.combobox_changed(event,combobox_instance,filter_name))
            filter.set_control(fn_entry)

        cnum = len(self.filters)

        self.toggle_vars = []

        for x,sorter in enumerate(self.sort_optional):
            ivar = IntVar()
            self.toggle_vars.append(ivar)
            sorter.set_ivar(ivar)

            fn_label = tb.Label(self.sort_frame, text=sorter.field,style ="Custom.TLabel" )
            fn_label.grid(row=0, column=x, padx=5, pady=5)
            fn_check = tb.Checkbutton(self.sort_frame,variable=self.toggle_vars[-1],onvalue=1,offvalue= 0,command = self.sorter_changed)
            sorter.set_control(fn_check)
            #fn_check.bind("<Button-1>",
            #    lambda event, checkbox_instance=fn_check,sort_name = sorter.field: self.sorter_changed(event,checkbox_instance,sort_name))
            fn_check.grid(row=1,column = x)

        cnum += len(self.sort_optional)

        #if len(self.filter_controls):
        if len(self.filters):
            bt = Button(self.filter_command_frame,text = "Clear",command = self.clear_filters)
            bt.grid(row=1,column=cnum,padx=5,pady=5)
            #bt = Button(self.filter_frame,text = "Debug",command  = self.debug )
            #bt.grid(row=1,column = cnum +1,padx=5,pady=5)


        order_map = get_order_map(self.table_name,self.df.columns)
        columns = [self.df.columns[x] for x in order_map]

        num_cols = 3
        # create record frame entries
        for x,column in enumerate(columns):


            fn_label = tb.Label(self.record_frame, text=column,style = "Custom.TLabel",anchor='e')
            fn_label.grid(row=int(x / num_cols), column= 2* (x % num_cols), padx=10, pady=5)

            dtype = self.df[column].dtype

            if column in self.field_maps.keys():
                link = self.field_maps[column]
                fn_entry = Combobox(self.record_frame)
                fn_entry['values'] = tuple(list(link.map_from.keys()))
            else:
                fn_entry = Entry(self.record_frame)

            if 'datetime' in str(dtype):
                dateformat = "%Y-%m-%d %H:%M:%S"
                dateformat = "%Y-%m-%d"
                fn_entry = tb.DateEntry(self.record_frame, bootstyle="dark",dateformat = dateformat)
                fn_entry.entry.delete(0, END)
                self.records.append(fn_entry.entry)
            else:
                self.records.append(fn_entry)


            fn_entry.grid(row=int(x / num_cols), column=2 * (x % num_cols) + 1, padx=10, pady=5)



        self.update_button.grid(row=0, column=0, padx=10, pady=10)
        self.add_button.grid(row=0, column=1, padx=10, pady=10)
        self.remove_one_button.grid(row=0, column=3, padx=10, pady=10)
        self.select_record_button.grid(row=0, column=7, padx=10, pady=10)


        # Add Record Entry Boxes
        pass

    def sorter_changed(self):
        print("sorter_changed")


        self.create_filtered_df()

        self.delete_and_replace()

    def clear_filters(self):
        print("clear_filters")
        self.filter_stack = []
        for filter in self.filters:
            filter.control.set("")

        for sorter in self.sort_optional:
            sorter.ivar.set(0)

        self.filtered_df = self.df.copy()
        self.set_filters()
        self.create_filtered_df()
        self.delete_and_replace()
        self.clear_entries()

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

    def search_selected_record(self):
        sd = self.selected_record.to_dict()

        formatted_strings = []

        keys = []
        x = 0

        for key, value in sd.items():

            keys.append(key)
            f = f"@keys[{x}]"
            x = x+1

            if isinstance(value, str):
                formatted_strings.append(f"`{key}` == \"{value}\"");continue
            if isinstance(value,pd.Timestamp):
                formatted_strings.append(f"`{key}` == '{value}'");continue
            if pd.isna(value):
                formatted_strings.append(f"`{key}`.isna()");continue

            formatted_strings.append(f"`{key}` == {value}")

        formatted_string = ' & '.join(formatted_strings)
        print("formatted_string: ",formatted_string)


        row_exists = self.df.query(formatted_string)
        print("row_exists type:",type(row_exists))
        print("row_exists:",row_exists)

        if len(row_exists.index):
            print("row exists, returning:",row_exists.index[0])
            return row_exists.index[0]

        return None


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
        print("selected:-----------------------------------",self.tree_focus())
        focus = self.tree_focus()
        print(self.filtered_df.iloc[focus])
        self.selected_record = self.filtered_df.iloc[focus]

        #print("search selected:",self.search_selected_record())


        # Grab record values
        values = self.my_tree.item(self.tree_focus(), 'values')

        for i,record in enumerate(self.records):
            #if 'DateEntry' in str(type(record)):
            #    record.insert(0,values[i]) #xxx
            #else:
            record.insert(0,values[i])

    def blank_check(self,message = None):
        for record in self.records:
            print("blank check:",record.get())
            if record.get() != "":
                return False

        if message:
            messagebox.showinfo("Notification", message)

        return True

    def delete_and_replace(self):
        selected = self.tree_focus()
        self.my_tree.delete(*self.my_tree.get_children())

        if glb.USE_DF:
            self.set_tree_body_df()
        if glb.USE_PL:
            self.set_tree_body_pl()
        if selected:
            self.my_tree.selection_set(selected)

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

        print("type",type(column_dtype))
        if column_dtype == 'float64':
            converted_value = float(new_value)
            print("its float64")
        else:
            series = pd.Series([new_value])
            print("series:",series)
            print("convert by dtype:",new_value,column_dtype)
            print("astype:",series.astype(column_dtype))
            converted_value = series.astype(column_dtype).iloc[0]

        #
        print("convert_by_dtype returns:",converted_value,type(converted_value))

        return converted_value

    def get_converted_row_values(self):

        order_map = get_order_map(self.table_name,self.df.columns)

        row_vals = [0] * len(self.records)
        for record,order in zip(self.records,order_map):
            try:
                rval = record.entry.get() if 'DateEntry' in str(type(record)) else record.get()

                column = self.df.columns[order]
                if column in self.field_maps.keys():
                    link = self.field_maps[column]
                    rval = link.map_from[rval]

                print("get_converted_row_vals:",rval,column,self.df[column].dtype)
                cval = self.convert_by_dtype(rval, self.df[column].dtype)
                print("cval:",cval)
                row_vals[order] = cval
            except Exception as e:
                print("get_converted_row_values exception:",e)
                print(traceback.print_exc())
                messagebox.showinfo("Notification",f"Invalid format for {self.df.columns[order]}")

                return None

        return row_vals

    def record_check(self):

        if self.blank_check(message = "Record is blank"):

            return

        selected = self.tree_focus()
        if selected is None:
            messagebox.showinfo("Notification", "No entry selected")
            return

        return True

    def add_record(self):
        if self.blank_check(message = "Record is blank"):
            return

        self.refresh_df()

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

        self.save_df()

        self.update_display()

        #self.delete_and_replace()




    def update_display(self):
        self.filtered_df = self.df.copy()
        self.set_filters()
        self.create_filtered_df()
        self.delete_and_replace()


    def update_record(self):

        if self.record_check() is None:
            return

        self.refresh_df()
        record_num = self.search_selected_record()

        if record_num is None:
            messagebox.showinfo("Notification", "Cannot find entry")
            return


        row_vals = self.get_converted_row_values()

        if not row_vals:
            return

        #print("update_record", self.tree_focus())
        #index = self.filtered_df.iloc[self.tree_focus()].name

        if glb.USE_DF:
            self.df.iloc[record_num] = row_vals
        if glb.USE_PL:
            pass

        self.save_df()


        self.update_display()


        print("update_record")
        pass

    def remove_one(self):
        if self.blank_check():
            return


        selected = self.tree_focus()
        print("remove one",selected)
        if not selected:
            messagebox.showinfo("Notification", "No entry selected")
            return

        self.refresh_df()
        record_num = self.search_selected_record()

        if record_num is None:
            messagebox.showinfo("Notification", "Cannot find entry")
            return
        print("remove drop:",self.df.iloc[record_num])
        self.df.drop(record_num,inplace=True)

        self.save_df()

        self.update_display()

        self.clear_entries()

        print("remove_one")

    def clear_entries(self):
        print("clear_entries")
        for record in self.records:
            record.delete(0,END)

        #self.my_tree.focus("")  # does not work
        self.my_tree.selection_set()

    def debug(self):
        print("focus:",self.tree_focus(),type(self.tree_focus()))
        pass

    def tree_focus(self):
        focus = self.my_tree.focus()
        #print("len tree_focus",len(focus),focus)
        if focus == "":
            return None
        return int(focus)



def get_order_map(table,keys):
    columns = list(keys)

    default_map = [i for i in range(len(keys))]

    for field in custom_dict["Tables"][table].get("ignore",[]):
        try:
            index = columns.index(field)
            default_map.remove(index)
        except:
            pass

    try:
        order = custom_dict["Tables"][table]["order"]

        new_map = []

        for field in order:
            index = columns.index(field)
            new_map.append(index)
            default_map.remove(index)
        new_map.extend(default_map)
        return new_map
    except:
        print("---------- get order map error --------",table)
        return default_map
