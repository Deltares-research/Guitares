# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 16:44:30 2022

@author: ormondt
"""

def add_elements(element_list, parent):
    
    for element in element_list:

        if element["style"] == "tabpanel":

            from pyqt5.tabpanel import TabPanel
            TabPanel(element, parent)

            for tab in element["tab"]:
                # And now add the elements in this tab
                if tab["element"]:
                    add_elements(tab["element"],
                                      tab["widget"])

        elif element["style"] == "panel":

            # Add frame
            from pyqt5.frame import Frame
            Frame(element, parent)

            # And now add the elements in this frame
            if "element" in element:
                add_elements(element["element"],
                             element["widget"])

        else:

            # Add push-buttons etc.
            if element["style"] == "pushbutton":
                from pyqt5.pushbutton import PushButton
                element["widget_group"] = PushButton(element, parent)

            elif element["style"] == "edit":
                from pyqt5.edit import Edit
                element["widget_group"] = Edit(element, parent)

            elif element["style"] == "datetimeedit":
                from pyqt5.date_edit import DateEdit
                element["widget_group"] = DateEdit(element, parent)

            elif element["style"] == "popupmenu":
                from pyqt5.popupmenu import PopupMenu
                element["widget_group"] = PopupMenu(element, parent)

            elif element["style"] == "olmap":
                from pyqt5.olmap import OlMap
                element["widget_group"] = OlMap(element, parent)
                                
            # And set the values    
            if "widget_group" in element:
                element["widget_group"].set()
