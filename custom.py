
LINK_BLANK_ALLOWED  = 1
LINK_NUMERIC_AS_TEXT = 2
LINK_ALLOW_CUSTOM_TEXT = 3

class ComboBoxC():
    def __init__(self,field):
        self.field = field
    def set_control(self,control):
        self.control = control
    def get(self):
        return self.control.get()

class DateSortC():
    def __init__(self,field):
        self.field = field
        self.ivar = None
        self.control = None
    def set_control(self,control):
        self.control = control
    def get(self):
        return self.control.get()

    def set_ivar(self,ivar):
        self.ivar = ivar

    def get_ivar(self):
        return self.ivar

class NumSort():
    def __init__(self,field):
        self.field = field
    def get_ivar(self):
        return True

class Link():
    def __init__(self,column_name,source_fields,dest_table,match_fields,dest_field,flags = None,info_field = None):
        self.column_name = column_name
        self.source_fields = source_fields
        self.dest_table = dest_table
        self.match_fields = match_fields
        self.dest_field = dest_field
        self.map_to = None
        self.map_from = None
        self.flags = flags
        self.info_field = info_field

    def __str__(self):
        s = "Link:\n"
        s+= f"column_name({self.column_name})\n"
        s+= f"source_fields({self.source_fields})\n"
        s+= f"dest_table({self.dest_table})\n"
        s+= f"match_fields({self.match_fields})\n"
        s+= f"dest_field({self.dest_field})\n"
        s+= f"map_to({self.map_to})\n"
        s+= f"map_from({self.map_from})\n"
        s+= f"flags({self.flags})\n"
        s+= f"info_field({self.info_field})\n"

        return s






custom_dict ={
    "TableOrder":["Project Data","Client ID","PM ID","Solas Architects","Solas Architect Rates","Fees","Dropdowns"],
    #"TableIgnore": ["Client ID", "PM ID", "Solas Architects", "Solas Architect Rates","Fees","Dropdowns"],
    "TableIgnore": ["Financials"],
    "Tables":
        {"Project Data":
              { "order": ["Client ID","Project ID","Project Title","Completed %","Completed or Cancelled","Solas Primary","Solas 2nd"],
                "filter": [ComboBoxC("Client ID"), ComboBoxC("Project ID"), ComboBoxC("Project Title"),ComboBoxC("Solas Primary")],
                "sort_optional" : [DateSortC("Update Date")],
                "links" :  [Link("Client ID",["Client ID"],"Client ID",["ID"],"Clients"),
                            Link("PM ID", ["PM ID"], "PM ID", ["PM ID"], "Project Manager"),
                            Link("Solas Primary", ["Solas Primary"], "Solas Architects", ["ID"],"ArchitectsShort", [LINK_BLANK_ALLOWED]),
                            Link("Solas 2nd", ["Solas 2nd"], "Solas Architects", ["ID"], "ArchitectsShort",[LINK_BLANK_ALLOWED]),
                            Link("Current Stage",["Current Stage"], "Dropdowns", ["Fee Phase"], "Fee Phase", [LINK_ALLOW_CUSTOM_TEXT]),
                            Link("Completed or Cancelled", ["Completed or Cancelled"],"Dropdowns", ["YesNo"], "YesNo", [LINK_ALLOW_CUSTOM_TEXT]),
                            ],
                "widths": {"Project Title": 300, "Client ID": 75,"PM ID":300,"Current Stage":300,"Notes":400},
                "ignore": ["ID"],
                "unique": [["Client ID","Project ID"]],
                "width": 2200,
                "force_numeric": ["Solas Primary","Solas 2nd"],
               },
          "Client ID":
                        {"widths": {"ID":50,"Clients":200},
                         "order": [],
                         "filters": [],
                         "unique": [["ID"]],
                         "width": 1050
                         },
          "Financials":
              {"order": ["ID","Client ID","Project ID","Project Title","Task","Source","Description"],
               "filter": [ComboBoxC("Client ID"), ComboBoxC("Project ID"), ComboBoxC("Project Title"),ComboBoxC("Task")],
               "links": [Link("Client ID", ["Client ID"],"Client ID", ["ID"], "Clients")],
               #"sort": ["Client ID","Project ID","Project Title","Task","Source","Description"],
               "sort": [ "Client ID","Project ID","Project Title","Task","Source"],
                "blank_rep": ["Client ID","Project ID","Project Title","Task","Source"],
               "ignore": ["ID"],
               "unique": [["ID"]],
                "width": 1740
               },
          "PM ID":
              {
                "order": [],
               "filter": [],
                "links": [Link("Client ID", ["Client ID"],"Client ID", ["ID"], "Clients",[LINK_NUMERIC_AS_TEXT])],
                #"links": [Link("Client ID", "Client ID", "ID", "Clients")],
               "unique": [["PM ID"]],
                "ignore": ["PM ID"],
                "widths": {"PM ID": 70,"Project Manager":300,"Email":400,"Cell Num":170,"Alternate Phone Num":170},
                "sort":["PM ID"],
                "width": 2300
               },
          "Solas Architect Rates":
              {"order": [],
               "filter": [ComboBoxC("Architect")],
               "sort_optional": [DateSortC("Rate Start Date")],
               "links": [Link("Architect", ["Architect"],"Solas Architects", ["ID"], "Architects")],
               "unique": [["ID"]],
               "ignore": ["ID"],
                "width": 1740
               },
          "Solas Architects":
              {
                "widths": {"ID":50,"Architects":250},
                "order": [],
               "filters": [],
               "unique": [["ID"]],
                "width": 1100
               },
         "Fees":
             {
                 #"order": ["Client ID", "Project ID","Project Title","Fee Phase"],
                 "order": ["Client ID","Project ID","Project Title","Fee Phase","Consultants","Contract Signed"],
                 "filter": [ComboBoxC("Client ID"), ComboBoxC("Project ID")],
                 "ignore": ["ID"],
                 "unique": [["ID"]],
                 "links": [Link("Client ID", ["Client ID"],"Client ID", ["ID"], "Clients"),
                           #Link("Project ID",["Project ID"],"Project Data",["ID"],"Project ID"),
                           Link("Project Title", ["Client ID","Project ID"],"Project Data", ["Client ID","Project ID"], "Project Title",info_field = "Project Title"),
                           Link("Fee Phase", ["Fee Phase"],"Dropdowns", ["Fee Phase"], "Fee Phase", [LINK_ALLOW_CUSTOM_TEXT]),
                           Link("Contract Signed", ["Contract Signed"],"Dropdowns", ["YesNo"], "YesNo", [LINK_ALLOW_CUSTOM_TEXT]),
                           Link("Consultants",["Consultants"],"Dropdowns",["Consultants"],"Consultants")],
                 "sort": ["Client ID", "Project ID", "Fee Phase"],
                 "blank_rep": ["Client ID", "Project ID", "Project Title", "Fee Phase"],
                "widths": {"Project Title": 300,"Client ID":75,"Fee Phase":250,"Type":200},
              "width": 2200
              },
         "Dropdowns":
             {
            "order": ["Fee Phase","Consultants"],
            "widths": {"ID": 50,"Fee Phase":400},
            "filters": [],
            "unique": [["ID"]],
            "ignore": ["ID"],
            "width": 1100
              },

        }}



