from typing import Any

class AppLogic():
    def __init__(self, parent) -> None:
        
        #ref parent class(main window)
        self.parent = parent

        #variables
        self.nav_map:dict[str, list[Any]] = {}
        
    #Methods
    def give_logic_program_system_access(self, nav_panel, main_menu): #this will allow logic to access program systems not included in nav_map dict
        self.nav_panel = nav_panel
        self.main_menu = main_menu

    #Navigation Panel
    def add_to_nav_map(self, system_name: str, page):
        '''adds new system to nav_map used by navigation menu,
        where system is a str (simple descriptor of the system), 
        and page is an instance reference for the class that defines each page of that system'''
        if self.nav_map.get(system_name) != None:
            pass #key already exists, do nothing
        else:
            self.nav_map[system_name] = []
        if page not in self.nav_map.get(system_name, []):
            self.nav_map.get(system_name, []).append(page)
        else:
            pass #page (instance ref) already in list, do nothing

    def system_selection(self, system_name: str):
        self.selected_system_pages = self.nav_map.get(system_name, [])
        self.current_page = 0
        self.selected_system_pages[self.current_page].tkraise()
        self.nav_panel.tkraise()

    def nav_panel_back_button(self):
        if self.current_page == 0: #currently on 1st page,return to main menu
            self.main_menu.tkraise()
        elif self.current_page > 0:
            self.selected_system_pages[self.current_page - 1].tkraise()
            self.current_page -= 1

    def nav_panel_continue_button(self):
        if self.current_page < len(self.selected_system_pages) - 1: #not at end of pages, adv current page and raise corresponding page
            self.current_page += 1
            self.selected_system_pages[self.current_page].tkraise()
        elif self.current_page == len(self.selected_system_pages) - 1: # at end, continue does nothing
            pass

