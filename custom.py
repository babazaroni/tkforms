
from classes import *



custom = {"Project Data":
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



