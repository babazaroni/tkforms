
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
    def __init__(self,source_field,dest_table,match_field,dest_field,flags = None):
        self.source_field = source_field
        self.dest_table = dest_table
        self.match_field = match_field
        self.dest_field = dest_field
        self.map_to = None
        self.map_from = None
        self.flags = flags



custom_dict ={
    "TableOrder":["Project Data","Client ID","PM ID","Solas Architects","Solas Architect Rates","Financials"],
    "Tables":
        {"Project Data":
              { "order": ["Client ID","Project ID","Project Title","Completed","Solas Primary"],
                "filter": [ComboBoxC("Client ID"), ComboBoxC("Project ID"), ComboBoxC("Project Title"),ComboBoxC("Solas Primary")],
                "sort_optional" : [DateSortC("Update Date")],
                "links" :  [Link("Client ID","Client ID","ID","Clients"),
                            Link("PM ID","PM ID","PM ID","Project Manager",[LINK_BLANK_ALLOWED,LINK_NUMERIC_AS_TEXT]),
                            Link("Solas Primary","Solas Architects","Architects","Architects",[LINK_BLANK_ALLOWED]),
                            Link("Solas 2nd","Solas Architects","Architects","Architects",[LINK_BLANK_ALLOWED]),
                            Link("Current Stage", "Choices", "Stages", "Stages", [LINK_ALLOW_CUSTOM_TEXT]),
                            Link("Completed or Cancelled", "Choices", "YesNo", "YesNo", [LINK_ALLOW_CUSTOM_TEXT]),
                            ],
                "width": 2200
               },
          "Client ID":
                        {"widths": {"ID":50,"Clients":200},
                         "order": [],
                         "filters": [],
                         "unique": ["ID"],
                         "width": 1050
                         },
          "Financials":
              {"order": ["ID","Client ID","Project ID","Project Title","Task","Source","Description"],
               "filter": [ComboBoxC("Client ID"), ComboBoxC("Project ID"), ComboBoxC("Project Title"),ComboBoxC("Task")],
               "links": [Link("Client ID", "Client ID", "ID", "Clients")],
               #"sort": ["Client ID","Project ID","Project Title","Task","Source","Description"],
               "sort": [ "Client ID","Project ID","Project Title","Task","Source"],
                "blank_rep": ["Client ID","Project ID","Project Title","Task","Source"],
               "ignore": [],
               "unique": ["ID"],
                "width": 1740
               },
          "PM ID":
              {
                "order": [],
               "filters": [],
                #"links": [Link("Client ID", "Client ID", "ID", "Clients")],
               "unique": ["PM ID"],
                  "widths": {"PM ID": 70,"Project Manager":300,"Email":400,"Cell Num":170,"Alternate Phone Num":170},
                  "sort":["PM ID"],
                "width": 2300
               },
          "Solas Architect Rates":
              {"order": [],
               "filters": [],
               "ignore": [],
               "links": [Link("Architect", "Solas Architects", "ID", "Architects")],
               "unique": ["ID"],
                "width": 1740
               },
          "Solas Architects":
              {
                "widths": {"ID":50,"Architects":250},
                "order": [],
               "filters": [],
               "unique": ["ID"],
                "width": 1100
               },
         "Fees":
             {
                 "order": ["Client ID", "Project ID","Project Title", "Fee Phase"],
                 "filter": [ComboBoxC("Client ID"), ComboBoxC("Project ID")],
                 "ignore": ["ID"],
                 "unique": ["ID"],
                 "links": [Link("Client ID", "Client ID", "ID", "Clients"),
                           Link("Project ID","Project Data","ID","Project ID"),
                           Link("Project Title", "Project Data", "ID", "Project Title"),
                            Link("Fee Phase", "Choices", "Stages", "Stages", [LINK_ALLOW_CUSTOM_TEXT]),
                           Link("Contract Signed", "Choices", "YesNo", "YesNo", [LINK_ALLOW_CUSTOM_TEXT]),
                           Link("Type","Choices","Fee Types","Fee Types")],
              "width": 2200
              },
         "Choices":
             {
            "widths": {"ID": 50,"Stages":400},
            "order": [],
              "filters": [],
              "unique": ["ID"],
            "sort": ["ID"],
              "width": 1100
              },

        }}



