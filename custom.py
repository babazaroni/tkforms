


custom = {"Project Data":
              { "order": ["Client ID","Project ID","Project Title","Solas Primary"],
                "filters": ["Client ID", "Project ID", "Project Title","Solas Primary"],
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
          "Financials Sorted View":
              {"order": [],
               "filters": [],
                "width": 1705
               },

          }


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