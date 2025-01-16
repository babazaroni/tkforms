


custom = {"Project Data":
              { "order": ["Client ID","Project ID","Project Title"],
                "filters": ["Client ID", "Project ID", "Project Title"]
               }
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