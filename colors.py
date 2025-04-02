import globals as glb


def color_init(parser):

    (glb.saved_primary_color, glb.saved_secondary_color, glb.saved_highlight_color) = get_colors(parser)
    #print("get_colors: ",glb.saved_highlight_color,glb.saved_secondary_color,glb.saved_primary_color)

def primary_color():
    # Pick Color
    primary_color = colorchooser.askcolor()[1]

    # Update Treeview Color
    if primary_color:
        # Create Striped Row Tags
        my_tree.tag_configure('evenrow', background=primary_color)

        # Config file
        parser = ConfigParser()
        parser.read("treebase.ini")
        # Set the color change
        parser.set('colors', 'primary_color', primary_color)
        # Save the config file
        with open('treebase.ini', 'w') as configfile:
            parser.write(configfile)


def secondary_color():
    # Pick Color
    secondary_color = colorchooser.askcolor()[1]

    # Update Treeview Color
    if secondary_color:
        # Create Striped Row Tags
        my_tree.tag_configure('oddrow', background=secondary_color)

        # Config file
        parser = ConfigParser()
        parser.read("treebase.ini")
        # Set the color change
        parser.set('colors', 'secondary_color', secondary_color)
        # Save the config file
        with open('treebase.ini', 'w') as configfile:
            parser.write(configfile)


def highlight_color():
    # Pick Color
    highlight_color = colorchooser.askcolor()[1]

    # Update Treeview Color
    # Change Selected Color
    if highlight_color:
        style.map('Treeview',
                  background=[('selected', highlight_color)])

        # Config file
        parser = ConfigParser()
        parser.read("treebase.ini")
        # Set the color change
        parser.set('colors', 'highlight_color', highlight_color)
        # Save the config file
        with open('treebase.ini', 'w') as configfile:
            parser.write(configfile)


def reset_colors():
    # Save original colors to config file
    parser = ConfigParser()
    parser.read('treebase.ini')
    parser.set('colors', 'primary_color', 'lightblue')
    parser.set('colors', 'secondary_color', 'white')
    parser.set('colors', 'highlight_color', '#347083')
    with open('treebase.ini', 'w') as configfile:
        parser.write(configfile)
    # Reset the colors
    my_tree.tag_configure('oddrow', background='white')
    my_tree.tag_configure('evenrow', background='lightblue')
    style.map('Treeview',
              background=[('selected', '#347083')])

def get_colors(parser):
    return  (None,None,None)
    saved_primary_color = parser.get('colors', 'primary_color')
    saved_secondary_color = parser.get('colors', 'secondary_color')
    saved_highlight_color = parser.get('colors', 'highlight_color')
    return (saved_primary_color,saved_secondary_color,saved_highlight_color)

