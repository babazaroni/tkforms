from operator import truediv
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Combobox

from sqlalchemy.sql.sqltypes import NULLTYPE

#from commands import *
from colors import *
from custom import custom_dict
import pandas as pd
from tkinter import messagebox
import ttkbootstrap as tb
import pandas as pd

import traceback
import custom

##rom main import tab_table_map  # this causes circular problems

class SpecialDict(dict):
    def __setitem__(self, key, value):
        if not key in self:
            super(SpecialDict, self).__setitem__(key, value)
        else:
            print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  duplicate key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",key,value)
            return
            raise Exception("Cannot overwrite key!") # You can make your own type here if needed

class TableUI(Frame):
    def __init__(self,root,parent,table_name,custom_dict):
        super().__init__(parent,bg="yellow")

        self.root = root
        self.table_name = table_name
        self.custom = custom_dict
        self.filters = self.custom.get("filter", [])
        self.sort_optional = self.custom.get("sort_optional", [])
        self.sort = self.custom.get("sort",[])
        self.blank_rep = self.custom.get("blank_rep",[])

        self.field_maps = {}

        self.df = glb.tables_dict[table_name]
        #self.df = None
        #self.refresh_df()

        self.selected_df_row = None

        #print("TableUI: custom:")
        #print(self.custom)

        self.master_frame = Frame(self)
        self.master_frame.grid(row = 0, column = 0,padx = 20)

        self.filtersort_frame = Frame(self.master_frame)
        self.filtersort_frame.grid(row = 0, column = 0,sticky = 'w')
        #self.filtersort_frame.pack(pady=10)
        #self.filtersort_frame.pack(side = LEFT,pady=10)
        #self.filtersort_frame.pack(anchor = 'nw',pady=10)

        self.filter_frame = LabelFrame(self.filtersort_frame,text = "Filter",bg = "red")
        self.filter_frame.grid(row=0,column = 0,padx=5,pady=5)
        #self.filter_frame.pack(side = LEFT)
        self.sort_frame = LabelFrame(self.filtersort_frame,text = "Sort",bg = "red")
        self.sort_frame.grid(row = 0,column = 1,padx=5,pady=5)

        #self.sort_frame.pack()
        self.filter_command_frame = LabelFrame(self.filtersort_frame, bg="red")
        self.filter_command_frame.grid(row=0, column=2, padx=5, pady=5)

        self.tree_frame = LabelFrame(self.master_frame,text = table_name,bg = "green")
        self.tree_frame.grid(row = 1,column = 0,sticky = "w",pady=10)

        self.record_frame = LabelFrame(self.master_frame, text = "Record")
        self.record_frame.grid(row = 2, column = 0, sticky = "w",padx=20,pady=20)

        self.button_frame = LabelFrame(self.master_frame, text = "Actions")
        self.button_frame.grid(row = 3, column = 0, sticky = "w",padx=20,pady=20)

        # Create a Treeview Scrollbar
        self.tree_scrolly = Scrollbar(self.tree_frame)  #command=tree.yview
        self.tree_scrolly.pack(side=RIGHT, fill=Y)
        #self.tree_scrolly.bind("<Configure>",self.on_scroll)


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
        self.add_button = Button(self.button_frame, text="Add Record", command=self.append_record_to_df)
        self.remove_one_button = Button(self.button_frame, text="Remove Record", command=self.remove_one)
        self.select_record_button = Button(self.button_frame, text="Clear Record", command=self.clear_entries)

        self.records = []
        self.filter_stack = []
        #self.filter_controls = []

        self.reqwidth = 0
        self.filtered_df = self.df.copy()

    def on_scroll(self):
        print("scrolled")

    def set_tables(self,tables):
        self.tables = tables

    def unique_fix(self,record_num):
        uniques = custom_dict["Tables"].get(self.table_name, {}).get('unique', [])

        print("unique_fix:",self.table_name)

        for fields in uniques:

            print("getting duplicates fields: ",fields)

            duplicates = self.df[fields][self.df[fields].duplicated()]

            print("unique_fix duplicates",duplicates)

            if duplicates.empty:
                continue

            if len(fields) == 1 and self.df[fields[0]].dtype in ['int64']:

                if record_num is None:
                    return True

                column = self.df[fields[0]]
                largest_series = column.nlargest(1)
                largest = largest_series.iloc(0)[0]
                for index,row in duplicates.iterrows():
                    if index == record_num:
                        self.df.loc[record_num,fields[0]] = largest = largest + 1
            else:
                #if pd.api.types.is_string_dtype(self.df[field]):

                    s = duplicates.iloc[0]

                    links = custom_dict["Tables"].get(self.table_name, {}).get('links', [])

                    duplicate_msg = ''
                    for idx, val in s.items():
                        for link in links:
                            if idx == link.source_field:
                                val = link.map_to[val]
                        duplicate_msg += f"{idx}={val} "


                    messagebox.showinfo("Notification",f"Multiple entries for {duplicate_msg}")
                    return False

        return True



    def refresh_df(self):
        if glb.ALCHEMY:
            self.df = pd.read_sql_table(self.table_name, con=glb.engine)
        else:
            self.df = pd.read_sql(f"select * from [{self.table_name}]", glb.cnn)

        self.df.fillna('', inplace=True)
        glb.tables_dict[self.table_name] = self.df

    def save_df(self):

        if glb.ALCHEMY:
            try:
                self.df.to_sql(self.table_name, con=glb.engine, if_exists='replace', index=False)
            except:
                messagebox.showinfo("Access Error","Could not save. Is Access using this table?")
        else:
            #self.df.to_sql(self.table_name, glb.cnn, if_exists='replace', index=False)
            self.df.to_sql("[Project Data]", glb.cnn, if_exists='replace', index=False)


    def create_tree_columns(self):
        global root
        order_map = get_order_map(self.table_name,self.df.columns)

        #columns = [self.df.columns[x] for x in order_map]
        columns = [x for x in order_map]

        self.my_tree['columns'] = tuple(columns)

        column_widths = custom_dict["Tables"].get(self.table_name, {}).get('widths', {})

        self.my_tree.column("#0", width=0, stretch=NO)
        total_width = 0
        for heading in columns:
            column_width = column_widths.get(heading,None)

            if column_width is None:
                cwidth = 140
            else:
                cwidth = column_width

            self.my_tree.column(heading,anchor = W, width = cwidth)

            total_width += cwidth

        self.my_tree.heading("#0", text="", anchor=W)

        self.width = total_width

        #self.root.geometry(f"{total_width+59}x1100")

        for heading in columns:
            self.my_tree.heading(heading, text=heading, anchor=W)

    def get_converted_row(self, index, order_map, ref_row=None, skip_missing=False): #xxx
        row = self.filtered_df.iloc[index]

        values = []
        new_ref_row = []

        for f in order_map:

            if f not in self.filtered_df.columns and skip_missing:
                continue

            if f in self.field_maps.keys():
                link = self.field_maps[f]
                entry = row[link.source_fields].iloc[0] #convert from series
            else:
                #column_index = self.filtered_df.columns.get_loc(f)
                #entry = row[column_index]
                #dtype = str(self.filtered_df[self.filtered_df.columns[column_index]].dtypes)
                entry = row[f]

            if f in self.field_maps.keys():
                link = self.field_maps[f]



                entry = link.map_to.get(entry,entry)



            if isinstance(entry, tuple):
                entry = entry[0]

            if entry is pd.NaT:
                entry = ""

            if isinstance(entry, pd.Timestamp):
                entry = str(entry).split()[0]

            new_ref_row.append(entry)

            if ref_row:
                if f in self.blank_rep:
                    if entry == ref_row[len(values)]:
                        entry = ""

            #print("entry:",type(entry),entry)

            values.append(entry)

        return values,new_ref_row


    def get_converted_row2(self,index,order_map,ref_row=None,skip_missing = False):

        row = self.filtered_df.iloc[index].tolist()
        print("get_converted_row row:",row)

        values = []
        new_ref_row = []

        for f in order_map:

            print("get_converted_row field:",f)

            dtype = None

            if f in self.filtered_df.columns:
                column_index = self.filtered_df.columns.get_loc(f)
                entry = row[column_index]
                dtype = str(self.filtered_df[self.filtered_df.columns[column_index]].dtypes)

            else:
                print("get_converted_row missing:",f,skip_missing)
                if not len(values):
                    print("missing field:",f)
                if skip_missing:
                    continue

                if f in self.field_maps.keys():
                    link = self.field_maps[f]

                    print(f"get_converted_row link({f}):",link)
                    #map_to
                    o = self.filtered_df.columns.get_loc(link.info_field)
                else:
                    values.append("error")
                    continue

            entry = row[o]

            if f in self.field_maps.keys():

                link = self.field_maps[f]
                entry = link.map_to.get(entry,entry)

            if 'datetime' in dtype:
                entry = str(entry).split()[0]
                if entry == "NaT":
                    entry = ""

            new_ref_row.append(entry)

            if ref_row:
                if f in self.blank_rep:
                    if entry == ref_row[len(values)]:
                        entry = ""

            values.append(entry)

        return values,new_ref_row


    def set_tree_body_df(self):

        for item in self.my_tree.get_children():
            self.my_tree.delete(item)

        order_map = get_order_map(self.table_name, self.filtered_df.columns)

        values = None
        ref_row = None

        for index in range(0, len(self.filtered_df)):

            values,ref_row = self.get_converted_row(index,order_map,ref_row = ref_row)

            tp = tuple(values)

            if index % 2 == 0:
                self.my_tree.insert(parent='', index='end', iid=index, text='',
                                    values=tp,
                                    tags=('evenrow',))
            else:
                self.my_tree.insert(parent='', index='end', iid=index, text='',
                                    values=tp,
                                    tags=('oddrow',))

        self.reqwidth = self.my_tree.winfo_reqwidth()

    def control_in_filter_stack(self,control):
        for stack_control,name in self.filter_stack:
            if control == stack_control:
                return True
        return False

    def create_maps(self): #  creates map_to and map_from dictionary xxx
        links = custom_dict["Tables"].get(self.table_name, {}).get('links', [])
        for link in links:
            dest_df = glb.tables_dict[link.dest_table]

            #print("create_maps link table_name:",self.table_name)
            #print("create_maps dest_table",link.dest_table)
            #print("The link:",link)

            match_column = list(dest_df[link.match_fields][::-1].itertuples(index=False, name=None))

            match_column = [x[0] if len(x) == 1 else x for x in match_column]  # convert from tuple

            if link.flags is not None and custom.LINK_NUMERIC_AS_TEXT in link.flags:
                match_column = [str(x) for x in match_column]

            #print("match_column:",type(match_column))
            #print(match_column)

            #print("dest_df:")
            #print(dest_df)

            dest_field_reversed = dest_df[link.dest_field][::-1]

            # the series are reversed so duplicate items will be replaced by items early in list

            link.map_to = dict(zip(match_column,dest_field_reversed))
            link.map_from = dict(zip(dest_field_reversed,match_column))

            #print("the link:")
            #print(link)

            #print("create_maps map_to:",link.map_to)
            #print("create_maps map_from:",link.map_from)

            #if link.dest_field == link.match_field:
            #    link.map_to[''] = ''  # allow blank
            #    link.map_from[''] = ''
            self.field_maps[link.column_name] = link

        #print("exiting create_maps")


    def get_linked_entries(self,filter,unique_entries):
        links = custom_dict["Tables"].get(self.table_name, {}).get('links', [])  #get_linked_entries

        for link in links:

            if filter.field == link.column_name:

                corresponding_values = [link.map_to[key] for key in unique_entries if key in link.map_to]

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

    def filter_changed(self, event, control, filter_name):
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


    def create_filters(self):
        for x,filter in enumerate(self.filters):
            fn_label = tb.Label(self.filter_frame, text=filter.field, style="Custom.TLabel")
            fn_label.grid(row=0, column=x, padx=5, pady=5)
            fn_entry = Combobox(self.filter_frame,justify=LEFT)
            fn_entry.grid(row=1, column=x, padx=5, pady=5)
            fn_entry.bind("<<ComboboxSelected>>",
                          lambda event, combobox_instance=fn_entry,filter_name = filter.field: self.filter_changed(event, combobox_instance, filter_name))
            filter.set_control(fn_entry)

    def create_sorters(self):
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

    def create_filter_buttons(self):
        cnum = len(self.filters) + len(self.sort_optional)

        #if len(self.filter_controls):
        if len(self.filters):
            bt = Button(self.filter_command_frame,text = "Clear",command = self.clear_filters)
            bt.grid(row=1,column=cnum,padx=5,pady=5)
            #bt = Button(self.filter_frame,text = "Debug",command  = self.debug )
            #bt.grid(row=1,column = cnum +1,padx=5,pady=5)

    def create_record_controls(self):

        # Create Striped Row Tags
        self.my_tree.tag_configure('oddrow', background=glb.saved_secondary_color)
        self.my_tree.tag_configure('evenrow', background=glb.saved_primary_color)

        order_map = get_order_map(self.table_name,self.df.columns)
        #columns = [self.df.columns[x] for x in order_map]

        labels = []
        self.entries = []


        for column in order_map:

            try:
                dtype = self.df[column].dtype
            except:
                continue

            fn_label = tb.Label(self.record_frame, text=column,style = "Custom.TLabel",anchor='e')
            labels.append(fn_label)

            #print("create_record_controls:",self.table_name,column)


            if column in self.field_maps.keys():
                fn_entry = Combobox(self.record_frame)
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

            self.entries.append(fn_entry)


        num_cols = 1

        if len(labels) == 2:
            num_cols = 2

        if len(labels) == 4:
            num_cols = 2

        if len(labels) > 4:
            num_cols = 3

        x = 0

        for label,entry in zip(labels,self.entries):
            label.grid(row=int(x / num_cols), column= 2* (x % num_cols), padx=10, pady=5)
            entry.grid(row=int(x / num_cols), column=2 * (x % num_cols) + 1, padx=10, pady=5)
            x += 1

    def dropdowns_init(self):

        order_map = get_order_map(self.table_name,self.df.columns)

        x = 0

        for column in order_map:

            try:
                dtype = self.df[column].dtype
            except:
                continue

            if column in self.field_maps.keys():

                link = self.field_maps[column]

                dropdown_list = list(link.map_from.keys())[::-1]  #reverse the list because it went in the dict reversed

                #print("setting dropdown:",column,dropdown_list)

                self.entries[x]['values'] = tuple(dropdown_list)  #   create_controls dropdown values

            x += 1



    def create_action_buttons(self):
        self.update_button.grid(row=0, column=0, padx=10, pady=10)
        self.add_button.grid(row=0, column=1, padx=10, pady=10)
        self.remove_one_button.grid(row=0, column=3, padx=10, pady=10)
        self.select_record_button.grid(row=0, column=7, padx=10, pady=10)


    def create_controls(self):

        self.my_tree.pack()

        # Configure the Scrollbar
        self.tree_scrolly.config(command=self.my_tree.yview)
        #self.tree_scrollx.config(command=self.my_tree.xview)
        # tree_scroll.config(command=my_tree.xview)

        self.create_filters()
        self.create_sorters()
        self.create_filter_buttons()
        self.create_record_controls()
        self.dropdowns_init()
        self.create_action_buttons()


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
        sd = self.selected_df_row.to_dict()

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
                #formatted_strings.append(f"`{key}` == '{value}'");continue
                formatted_strings.append(f"`{key}` == @pd.Timestamp('{value}')");continue
            if pd.isna(value):
                formatted_strings.append(f"`{key}`.isna()");continue

            formatted_strings.append(f"`{key}` == {value}")

        formatted_string = ' & '.join(formatted_strings)
        #print("formatted_string: ",formatted_string)


        row_exists = self.df.query(formatted_string)
        #print("row_exists type:",type(row_exists))
        #print("row_exists:",row_exists)

        if len(row_exists.index):
            #print("row exists, returning:",row_exists.index[0])
            return row_exists.index[0]

        return None


    def select_record(self,event):

        if self.my_tree.focus() == '':
            print("select_record: no entry selected")
            return

        for record in self.records:
            record.delete(0,END)

        focus = self.tree_focus()

        self.selected_df_row = self.filtered_df.iloc[focus]

        order_map = get_order_map(self.table_name, self.filtered_df.columns)
        values,ref_row = self.get_converted_row(focus, order_map,skip_missing=True)

        for i,record in enumerate(self.records):
            record.insert(0,values[i])

    def blank_check(self,message = None):
        for record in self.records:

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
            try:
                self.my_tree.selection_set(selected)
            except:
                print("selected not present")


    def convert_by_dtype(self,new_value:str,column_dtype):
        #print("convert_by_dtype",self.df[self.df.columns[column]].dtype)

        #column_dtype = self.df[self.df.columns[column]].dtype

        #print("convert_by_dtype;",column_dtype,new_value)
        #print("new value:",new_value,"dtype:",type(new_value))

        if column_dtype == "bool":

            5/0

            if new_value.lower() not in ['true','false','yes','no']:
                5/0  # should do a real exception instead

            if new_value.capitalize() in ['False','No']:
                new_value = ''
            else:
                new_value = 'Truex'

            #print("its a bool")

        #print("type",type(column_dtype))
        if column_dtype == 'float64':
            converted_value = float(new_value)
            #print("its float64")
        else:
            series = pd.Series([new_value])
            #print("series:",series)
            #print("convert by dtype:",new_value,column_dtype)
            #print("astype:",series.astype(column_dtype))
            converted_value = series.astype(column_dtype).iloc[0]

        #
        #print("convert_by_dtype returns:",converted_value,type(converted_value))

        return converted_value

    def get_record_values(self):
        return [record.entry.get() if 'DateEntry' in str(type(record)) else record.get() for record in self.records ]

    def default_value(self,dtype):
        if pd.api.types.is_integer_dtype(dtype):
            return 0
        elif pd.api.types.is_float_dtype(dtype):
            return 0.0
        elif pd.api.types.is_bool_dtype(dtype):
            return False
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return pd.Timestamp(0)
        else:
            return ''  # default for object or string types

    # Create Series with default values


    def create_default_row(self):
        default_series = pd.Series({col: self.default_value(dtype) for col, dtype in self.filtered_df.dtypes.items()})
        return default_series.tolist()

    def convert_record_to_df(self):

        order_map = get_order_map(self.table_name,self.df.columns,remove_alias= True)

        #row_vals = self.selected_df_row.tolist()

        row_vals = self.create_default_row()

        #row_vals = [0] * len(self.records)
        cval = None

        for record,column in zip(self.records,order_map):

            code = 0
            try:
                rval = record.entry.get() if 'DateEntry' in str(type(record)) else record.get()

                #print("record,column:", rval, column)

                if column in self.field_maps.keys():
                    code = 1
                    link = self.field_maps[column]
                    if link.info_field is not None:
                        continue

                    #print("convert_record_to_df link map_from:",link.map_from)

                    if link.flags:

                        if isinstance(rval,str):
                            code = 2

                            if  (rval == '' or rval.isspace()) and custom.LINK_BLANK_ALLOWED in link.flags:
                                rval = ''
                            else:
                                code = 3
                                if custom.LINK_NUMERIC_AS_TEXT in link.flags:
                                    code = 4
                                    #rval = float(rval)
                                    #rval = link.map_from[int(rval)]
                                    rval = link.map_from[rval]
                                else:
                                    code = 5
                                    if custom.LINK_ALLOW_CUSTOM_TEXT not in link.flags:
                                        rval = link.map_from[rval]
                        else:
                            code = 6
                            rval = link.map_from[rval]
                    else:
                        code = 7
                        #print("map_from:",rval,link.map_from)
                        rval = link.map_from[rval]
                else:
                    code = 8

                cval = self.convert_by_dtype(rval, self.df[column].dtype)
                #print(f"df[{column}.dtype:",self.df[column].dtype)
                #print(f"row_vals[{order}] = {cval}")
                row_vals[self.df.columns.get_loc(column)] = cval
            except Exception as e:
                print("get_converted_row_values exception:",e)
                print(traceback.print_exc())
                #messagebox.showinfo("Notification",f"Invalid value for {column}.  Use dropdown values {code} {rval} {cval}")
                messagebox.showinfo("Notification",f"Invalid value for {column}.  Use dropdown values.{cval}")
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

    def append_record_to_df(self):
        if self.blank_check(message = "Record is blank"):
            return

        self.refresh_df()

        df_row_vals = self.convert_record_to_df()

        print("append_record_to_df:",df_row_vals)

        if not df_row_vals:
            return


        if glb.USE_DF:
            self.df.loc[len(self.df)] = df_row_vals

        if glb.USE_PL:
            pass

        if not self.unique_fix(len(self.df)-1):
            return

        self.save_df()

        self.update_display()

        #self.delete_and_replace()

    def update_all_dropdowns(self):

        for table in self.tables:
            table.create_maps()
            table.dropdowns_init()


    def update_display(self):
        self.filtered_df = self.df.copy()
        self.set_filters()
        self.create_filtered_df()
        self.delete_and_replace()
        self.update_all_dropdowns()


    def update_record(self):

        if self.record_check() is None:
            return

        self.refresh_df()
        record_num = self.search_selected_record()

        if record_num is None:
            messagebox.showinfo("Notification", "Cannot find entry")
            return


        row_vals = self.convert_record_to_df()

        if not row_vals:
            return

        last_row_vals = self.df.iloc[record_num]

        if glb.USE_DF:
            self.df.iloc[record_num] = row_vals
        if glb.USE_PL:
            pass

        if not self.unique_fix(record_num):
            self.df.iloc[record_num] = last_row_vals
            return

        self.save_df()

        self.update_display()

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



def get_order_map(table,keys,remove_alias = False):

    default_map = list(keys)

    for field in custom_dict["Tables"][table].get("ignore",[]):
        try:
            default_map.remove(field)
        except:
            pass

    try:
        order = custom_dict["Tables"][table]["order"]

        new_map = []

        for field in order:
            new_map.append(field)

            try:
                default_map.remove(field)
            except:
                pass

        new_map.extend(default_map)

        if remove_alias:
            for link in custom_dict["Tables"][table].get("links", []):
                if link.info_field:
                    new_map.remove(link.source_field)

        #print("get_order_map:",table,new_map)

        return new_map

    except:
        print("---------- get order map error --------",table)
        return default_map

