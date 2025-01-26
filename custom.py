


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


custom_dict = {"Project Data":
              { "order": ["Client ID","Project ID","Project Title","Solas Primary"],
                "filter": [ComboBoxC("Client ID"), ComboBoxC("Project ID"), ComboBoxC("Project Title"),ComboBoxC("Solas Primary")],
                "sort" : [DateSortC("Update Date")],
                "width": 2200
               },
          "Client ID":
                        {"order": [],
                         "filters": [],
                         "width": 1050
                         },
          "Financials":
              {"order": [],
               "filters": [],
                "width": 1740
               },
          "PM ID":
              {"order": [],
               "filters": [],
                "width": 1930
               },
          "Solas Architect Rates":
              {"order": [],
               "filters": [],
                "width": 1740
               },
          "Solas Architects":
              {"order": [],
               "filters": [],
                "width": 1100
               },

        }



