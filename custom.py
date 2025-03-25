


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

class Link():
    def __init__(self,source_field,dest_table,match_field,dest_field):
        self.source_field = source_field
        self.dest_table = dest_table
        self.match_field = match_field
        self.dest_field = dest_field
        self.map_to = None
        self.map_from = None



custom_dict ={
    "TableOrder":["Project Data","Client ID","PM ID","Solas Architects","Solas Architect Rates","Financials"],
    "Tables":
        {"Project Data":
              { "order": ["Client ID","Project ID","Project Title","Completed","Solas Primary"],
                "filter": [ComboBoxC("Client ID"), ComboBoxC("Project ID"), ComboBoxC("Project Title"),ComboBoxC("Solas Primary")],
                "sort_optional" : [DateSortC("Update Date")],
                "links" :  [Link("Client ID","Client ID","ID","Clients")],
                "width": 2200
               },
          "Client ID":
                        {"order": [],
                         "filters": [],
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
                "width": 1740
               },
          "PM ID":
              {"order": [],
               "filters": [],
                #"links": [Link("Client ID", "Client ID", "ID", "Clients")],
                "width": 1930
               },
          "Solas Architect Rates":
              {"order": [],
               "filters": [],
               "ignore": [],
               "links": [Link("Architect", "Solas Architects", "ID", "Architects")],
                "width": 1740
               },
          "Solas Architects":
              {"order": [],
               "filters": [],
               "unique": ["ID"],
                "width": 1100
               },
         "Fees":
             {
                 "order": ["Client ID", "Project ID", "Project Title", "Fee Phase"],
                 "filter": [ComboBoxC("Client ID"), ComboBoxC("Project ID"), ComboBoxC("Project Title")],
                 "ignore": ["IDx"],
                 "unique": ["ID"],
                 "links": [Link("Client ID", "Client ID", "ID", "Clients")],
              "width": 2200
              },
         "Choices":
             {"order": [],
              "filters": [],
              "width": 1100
              },

        }}



