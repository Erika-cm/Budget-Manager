from __future__ import annotations
from typing import Any, TYPE_CHECKING
from enum import Enum

import os
import sys
import json
if TYPE_CHECKING:
    from Visuals import MainMenu, NavigationPanel, RadioButtonMenu, EditBudgetTemplate, VisualFunctions

#program system names
class SystemNames(Enum):
    create_new_system = "CreateNew"
    manage_budget_system = "Manage"

class AppLogic():
    '''
    
    '''
    def __init__(self, parent) -> None:
        
        #ref parent class(main window)
        self.parent = parent

        #variables
        self.nav_map:dict[str, list[Any]] = {}        

        self.default_budget_template = {
                        "Title" : 
                        "Default",
                        "Income" : 
                        {"All Income" : [["Employment", "Rent", "Investments", "Other"], [1,2,1,1]]},
                        "Expenses" : 
                        {"Housing" : [["Rent", "Utilities", "Phone", "Internet", "TV/Streaming Services", "Maintenance", "Home Insurance", "Other"], [1,1,1,1,1,1,2,1]],
                        "Common Living Expenses" : [["Groceries", "Delivery/Take Out", "Coffee/Treats", "Hygeine and Personal Grooming", "Appliances", "Computer Parts", "Entertainment", "Hobbies and Skill Development", "Bank/Credit Card Fees", "Taxes", "Other"], [1,1,1,1,1,1,1,1,1,2,1]],
                        "Transportation" : [["Transit Pass", "Car Share Services", "Fuel", "Insurance", "Maintenance", "Parking", "Other"], [1,1,1,2,1,1,1]],
                        "Clothing" : [["Everyday Use", "Special Occasion", "Other"], [1,1,1]],
                        "Medical" : [["Insurance (life)", "Insurance (Medical)", "Prescription Drugs", "Over the Counter Drugs", "Medical Services", "Paramedical Services", "Dental", "Vision Care", "Skin Care", "Other"], [2,2,1,1,1,1,1,1,1,1]]}
                        }
        
        self.set_template_editor_vars()
        
        
    #METHODS
    def give_logic_program_system_access(self, visual_functions: "VisualFunctions", nav_panel: "NavigationPanel", main_menu: "MainMenu", create_new_template_radiobuttons: "RadioButtonMenu", create_new_template_editor: "EditBudgetTemplate", manage_budget_file_radiobuttons: "RadioButtonMenu"): #this will allow logic to access program systems not included in nav_map dict
        self.visual_functions = visual_functions
        self.nav_panel = nav_panel
        self.main_menu = main_menu
        self.create_new_template_radiobuttons = create_new_template_radiobuttons
        self.create_new_template_editor = create_new_template_editor
        self.manage_budget_file_radiobuttons = manage_budget_file_radiobuttons
        self.gen_context_menu_textbox_dict() #this references the other classes, so has to be initialized after they are
        
    def set_user_files_path(self):
        if sys.executable.endswith("python.exe"): #runnig in dev version from .py
            self.user_files_path = os.getcwd() #NOTE if cwd is altered for any reason this can be replaced by a specific folder ref like below
        else: #running production version from .exe
            self.user_path = os.path.expanduser("~")
            self.user_files_path = os.path.join(self.user_path, "Documents\\Manage Your Money")
        if not os.path.isdir(self.user_files_path):
            os.mkdir(self.user_files_path)

    def set_icon_file_path(self):
        #icon file needs .exe or .py directory
        #specify icon path as cwd (assumes cwd has not been changed)
        exe_path = os.path.dirname(os.path.abspath(sys.executable))
        icon_path = os.path.join(exe_path, "Icon.ico")
        if not os.path.isfile(icon_path): #file not found 
            exe_path = os.getcwd()
            icon_path = os.path.join(exe_path, "Icon.ico")
        return icon_path

    #NAVIGATION PANEL
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

    def system_selection(self, system_name: Enum):
        self.selected_system_pages: list = self.nav_map.get(system_name.value, [])
        self.current_page = 0
        self.visual_functions.raise_panel(self.selected_system_pages[self.current_page])
        self.visual_functions.raise_panel(self.nav_panel)
        if system_name == SystemNames.create_new_system:
            self.display_template_list()
        elif system_name == SystemNames.manage_budget_system:
            self.display_budget_files()

    def nav_panel_continue_button(self):
        if self.current_page < len(self.selected_system_pages) - 1: #not at end of pages, adv current page and raise corresponding page
            self.current_page += 1
            self.visual_functions.raise_panel(self.selected_system_pages[self.current_page])
        if self.current_page == 1: #at radiobutton menu, adv to next page(template editor, budget manager)
            if self.template_displayed == 0: #no template currently dispalyed, display current selection
                self.create_new_template_editor.set_treeview_style_template_editor()
                self.selected_template_title: str = self.create_new_template_radiobuttons.extract_selected_template_string_var()
                self.selected_template_dict = self.store_selected_template_dict(self.selected_template_title)
                self.display_template_and_title(self.selected_template_title, self.selected_template_dict)
            else:
                pass #template already displayed, do nothing
        elif self.current_page == len(self.selected_system_pages) - 1: # at end, continue does nothing
            pass

    def nav_panel_back_button(self):
        if self.current_page == 1: #currently at template editor, return to radiobutton menu #0  
            self.clear_template()
        if self.current_page > 0: #not at first page, go to previous page
            self.visual_functions.raise_panel(self.selected_system_pages[self.current_page - 1])
            self.current_page -= 1  
        elif self.current_page == 0: #currently on radiobutton menu,return to main menu
            self.visual_functions.raise_panel(self.main_menu)

    #RADIOBUTTON MENU
    def display_template_list(self): 
        self.template_list:list[dict] = [self.default_budget_template]
        self.template_title_list:list[str] = [self.default_budget_template.get("Title", str)]
        template_path = os.path.join(self.user_files_path, "budget templates.json")
        try:
            with open(template_path, 'r') as template_import:
                imported_templates = json.load(template_import)
                for user_template in imported_templates:
                    self.template_list.append(user_template)
                    self.template_title_list.append(user_template.get("Title"))
        except FileNotFoundError:
            pass #file is not found, load only default to list 
        self.create_new_template_radiobuttons.create_radiobuttons(self.template_title_list)
    
    #find all sqlite files in cwd, and place them in list - when page is raised
    def display_budget_files(self):
        self.budget_list = []
        self.file_list = os.listdir(self.user_files_path)
        for file in self.file_list:
            if file.endswith(".sqlite") == True:
                self.budget_list.append(file.split(".")[0])
        self.manage_budget_file_radiobuttons.create_radiobuttons(self.budget_list)

    def store_selected_template_dict(self, template_title: str) -> dict | None:
        selected_template_dict: dict = {}
        for template in self.template_list:
            if template.get("Title", str) == template_title:
                selected_template_dict = template
                return selected_template_dict
            
    #TEMPLATE EDITOR
    #template window
    def set_template_editor_vars(self):
        self.template_displayed = 0 #swtich indicating that a template is displayed in the editor
        self.context_menu_text_box_focus = 0 #keep track of text box focus for context menu
    
    def display_template_and_title(self, template_title: str, template: dict| None): 
        self.template_displayed = 1
        self.visual_functions.configure_widget(self.create_new_template_editor.template_title_label, new_text="Selected Template: " + template_title)
        self.income_section = self.visual_functions.insert_into_hierarchy(self.create_new_template_editor.template_editor, "", 0, text_to_insert="Income", display_open=True)
        self.expenses_section = self.visual_functions.insert_into_hierarchy(self.create_new_template_editor.template_editor, "", 2, text_to_insert="Expenses", display_open=True)
        if type(template) == dict:
            self.display_template_income_section(template.get("Income", {}))
            self.display_template_expenses_section(template.get("Expenses", {}))
        else: #no template selected
            pass
        self.visual_functions.raise_panel(self.create_new_template_editor.context_intro_message)
    
    def display_template_income_section(self, income: dict):
        for category in income.keys():
            income_category_id = self.visual_functions.insert_into_hierarchy(self.create_new_template_editor.template_editor, self.income_section, 'end', text_to_insert=category, display_open=False)
            for subcat, monthly in zip(income.get(category, [])[0], income.get(category, [])[1]):
                self.visual_functions.insert_into_hierarchy(self.create_new_template_editor.template_editor, income_category_id, 'end', text_to_insert=subcat, row_values=monthly, display_open=False)

    def display_template_expenses_section(self, expenses: dict):
        for category in expenses.keys():
            expense_category_id = self.visual_functions.insert_into_hierarchy(self.create_new_template_editor.template_editor, self.expenses_section, 'end', text_to_insert=category, display_open=False)
            for subcat, monthly in zip(expenses.get(category, [])[0], expenses.get(category, [])[1]): 
                self.visual_functions.insert_into_hierarchy(self.create_new_template_editor.template_editor, expense_category_id, 'end', text_to_insert=subcat, row_values=monthly, display_open=False)

    def clear_template(self):   
        if self.template_displayed == 1:
            self.visual_functions.delete_hierarchy_item(self.create_new_template_editor.template_editor, self.income_section)
            self.visual_functions.delete_hierarchy_item(self.create_new_template_editor.template_editor, self.expenses_section)
            self.template_displayed = 0 

    #display context menu
    def raise_context_menu(self, event):
        self.template_editor = self.create_new_template_editor.template_editor
        self.current_focused_item = self.visual_functions.get_hierarchy_focus(self.create_new_template_editor.template_editor)
        current_focused_item_text = self.visual_functions.get_hierarchy_content(self.template_editor, self.current_focused_item, 'text')
        current_item_parent_text = self.visual_functions.get_hierarchy_content(self.template_editor, self.visual_functions.get_hierarchy_item_parent(self.template_editor, self.current_focused_item), 'text')
        current_item_grandparent_text = self.visual_functions.get_hierarchy_content(self.template_editor, self.visual_functions.get_hierarchy_item_parent(self.template_editor, self.visual_functions.get_hierarchy_item_parent(self.template_editor, self.current_focused_item)), 'text')
        #income/expense selected
        if current_item_parent_text == "":
            self.visual_functions.raise_panel(self.create_new_template_editor.context_income_expense)
            self.visual_functions.configure_widget(self.create_new_template_editor.income_expense_label, current_focused_item_text + " Selected")
        #category selected
        if current_item_grandparent_text == "" and current_item_parent_text != "":
            self.visual_functions.raise_panel(self.create_new_template_editor.context_category)
            if self.visual_functions.textbox_get(self.create_new_template_editor.category_text_box_in_category_menu, "1.0", "end-1c") != "":
                self.visual_functions.textbox_delete(self.create_new_template_editor.category_text_box_in_category_menu, "0.0", "end")
                self.visual_functions.textbox_markset_insert(self.create_new_template_editor.category_text_box_in_category_menu, "0.0")
            self.visual_functions.textbox_insert(self.create_new_template_editor.category_text_box_in_category_menu, "0.0", current_focused_item_text)
        #subcategory selected
        if current_item_grandparent_text != "":
            self.visual_functions.raise_panel(self.create_new_template_editor.context_subcategory)
            if self.visual_functions.textbox_get(self.create_new_template_editor.subcategory_textbox, "1.0", "end-1c") != "":
                self.visual_functions.textbox_delete(self.create_new_template_editor.subcategory_textbox, "0.0", "end")
                self.visual_functions.textbox_markset_insert(self.create_new_template_editor.subcategory_textbox, "0.0")
            self.visual_functions.textbox_insert(self.create_new_template_editor.subcategory_textbox, "0.0", current_focused_item_text)
            if self.visual_functions.get_hierarchy_content(self.template_editor, self.current_focused_item, "values")[0] == 1:
                self.visual_functions.checkbox_deselect(self.create_new_template_editor.subcategory_annual_checkbox)
            if self.visual_functions.get_hierarchy_content(self.template_editor, self.current_focused_item, "values")[0] == 2:
                self.visual_functions.checkbox_select(self.create_new_template_editor.subcategory_annual_checkbox)

    #context menu methods
    def add_textbox_content_to_template_editor(self, context_menu_textbox, event=""):
        context_menu_textbox_text = self.visual_functions.textbox_get(context_menu_textbox, "1.0", "end-1c")
        current_focused_item_parent = self.visual_functions.get_hierarchy_item_parent(self.template_editor, self.current_focused_item)
        #check if current item is income/expense or category
        monthly_annual = []
        if current_focused_item_parent != "": #item is not income or expense NOTE:does not distinguish btw cat and subcat
            monthly_annual = [1]
        else:
            monthly_annual = []
        #check for textbox content (either black focused textbox, or add cat/subcat)
        if context_menu_textbox_text == "":
            self.visual_functions.textbox_delete(context_menu_textbox, "0.0", "end")
            self.visual_functions.textbox_markset_insert(context_menu_textbox, "0.0")
        if context_menu_textbox_text != "":
            self.visual_functions.get_hierarchy_item(self.template_editor, self.current_focused_item, display_open=True)
            self.visual_functions.insert_into_hierarchy(self.template_editor, self.current_focused_item, "end", text_to_insert=context_menu_textbox_text, row_values=monthly_annual)
            current_focused_item_children = self.visual_functions.get_hierarchy_item_children(self.template_editor, self.current_focused_item)
            self.visual_functions.set_hierarchy_single_selection(self.template_editor, current_focused_item_children[-1])
            self.visual_functions.set_hierarchy_focus(self.template_editor, current_focused_item_children[-1])
            self.visual_functions.textbox_delete(context_menu_textbox, "0.0", "end")
            self.visual_functions.textbox_markset_insert(context_menu_textbox, "0.0")
        return "break"            

    def rename_hierachy_item(self, context_menu_textbox, event=""):
        context_menu_textbox_text = self.visual_functions.textbox_get(context_menu_textbox, "1.0", "end-1c")
        self.visual_functions.get_hierarchy_item(self.template_editor, self.current_focused_item, new_text=context_menu_textbox_text, display_open=True)
        return 'break'
    
    def move_hierarchy_item_up(self):
        current_item_pos = self.visual_functions.get_hierarchy_item_index(self.template_editor, self.current_focused_item)
        self.visual_functions.move_hierarchy_item(self.template_editor, self.current_focused_item, current_item_pos-1)

    def move_hierarchy_item_down(self):
        current_item_pos = self.visual_functions.get_hierarchy_item_index(self.template_editor, self.current_focused_item)
        self.visual_functions.move_hierarchy_item(self.template_editor, self.current_focused_item, current_item_pos+1)
    
    def delete_selected_hierarchy_item(self):
        self.visual_functions.delete_hierarchy_item(self.template_editor, self.current_focused_item)

    def set_monthly_annual_checkbox_status(self):
        self.visual_functions.get_hierarchy_item(self.template_editor, self.current_focused_item, new_values=self.create_new_template_editor.extract_int_var())

    #bind return key to text boxes
    #set up a dict to store context menu textboxes and their respective functions (for focus update method)
    def gen_context_menu_textbox_dict(self):
        self.textbox_dict = {self.create_new_template_editor.category_text_box : lambda event, widget=self.create_new_template_editor.category_text_box : self.add_textbox_content_to_template_editor(widget, event), 
                        self.create_new_template_editor.category_text_box_in_category_menu : lambda event, widget=self.create_new_template_editor.category_text_box_in_category_menu : self.rename_hierachy_item(widget, event),
                        self.create_new_template_editor.subcategory_text_box_in_category_menu : lambda event, widget=self.create_new_template_editor.subcategory_text_box_in_category_menu : self.add_textbox_content_to_template_editor(widget, event),
                        self.create_new_template_editor.subcategory_textbox : lambda event, widget=self.create_new_template_editor.subcategory_textbox : self.rename_hierachy_item(widget, event)}

    def add_context_menu_textbox_focus(self, event, widget):
        if self.context_menu_text_box_focus == 0:
            self.context_menu_text_box_focus = 1
            widget.bind("<Return>", self.textbox_dict.get(widget))
    
    def remove_context_menu_textbox_focus(self, event, widget):
        if self.context_menu_text_box_focus == 1:
            self.context_menu_text_box_focus = 0
            widget.unbind("<Return>")   
    
    #save button
    
#may want to refactor the save window function