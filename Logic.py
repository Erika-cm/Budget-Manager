from __future__ import annotations
from typing import Any, Literal, Tuple, TYPE_CHECKING
from enum import Enum

import os
import sys
import json
import sqlite3
import datetime
if TYPE_CHECKING:
    from Visuals import MainMenu,NavigationPanel, RadioButtonMenu, EditBudgetTemplate, EditBudget, AccountSelection, VisualFunctions, SaveNameWindow, WarningWindow, ManageBudget, TransactionListWindow, TransactionEditorWindow

#program system names
class SystemNames(Enum):
    create_new_system = "CreateNew"
    manage_budget_system = "Manage"

#save object types
class SaveObjectTypes(Enum):
    template = "Budget Template"
    budget = "Budget"

#text for all warning/error windows
class WarningWindowText(Enum):
    template_exists_title = "Template Already Exists"
    template_exists_message = "A Template with that Name Already Exists. \nDo You Want to Overwrite it?"
    trying_to_replace_default_template_title = "Cannot Replace Default Template"
    trying_to_replace_default_template_message = "The Default Template Cannot be Replaced. \nPlease Enter a Different Title."
    budgetfile_exists_title = "Budget File Already Exists"
    budgetfile_exists_message = "A Budget File with that Name Already Exists. \nDo you want to Overwrite it?"
    budget_save_confirmed_title = "Budget Save Success"
    budget_save_confirmed_message = "Budget Save Confirmed."
    budget_save_not_confirmed_title = "Budget Save Failed"
    budget_save_not_confirmed_message = "Budget Save Could not be Confirmed. \nIf the Issue Persists, Please File a Bug Report (via Github.com)"

#used to tag items in a treeview with their level in the hierarchy
class HierarchyLevel(Enum):
    incexp = "Income or Expenses"
    category = "Category"
    subcategory = "Sub-Category"

#strings indicating transaction status in list window
class TrasactionStatuses(Enum):
    new = " new"
    modified = " modified"
    deleted = " deleted"
    canceled = " canceled" #when new are deleted
    modifiednew = " new (modified)" #when new is modified

#store app fonts as tuples
class Fonts(Enum):
    deleted_radiobutton = ("Calibri", 15, "overstrike")
    
class AppLogic():
    '''
    System List:
    \nMETHODS: general app methods
    \nNAVIGATION PANEL: creates a map of the app, and enables navigation
    \nRADIOBUTTON MENU: creates a list of radiobuttons for files and templates, acts as a file loading system 
    \nTEMPLATE EDITOR: enables editing of the budget template (adding/removing/renaming) (sub)category_data
    \nSAVE WINDOW: creates a window for entering a name and saving a template or a budget
    '''
    def __init__(self, parent) -> None:
        
        #ref parent class(main window)
        self.parent = parent

        #variables
        self.nav_map:dict[str, list[list[Any]]] = {}
        self.page_list: list = []
        self.page_func_list: list = []
        self.budget_list: list = []
        self.template_list: list[dict]= []
        self.template_title_list: list[str] = []
        self.ready_to_continue: bool = True #switch can be turned off, if continue functionality needs to be put on hold to deal with an error

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
        self.set_budget_editor_vars()
        self.set_budget_manager_vars()
        self.get_date_from_system()
        
        
    #GENERAL METHODS
    def give_logic_program_system_access(self, 
                                         visual_functions: "VisualFunctions", 
                                         nav_panel: "NavigationPanel", 
                                         main_menu: "MainMenu", 
                                         create_new_template_radiobuttons: "RadioButtonMenu", 
                                         create_new_template_editor: "EditBudgetTemplate", 
                                         create_new_budget_editor: "EditBudget", 
                                         create_new_account_selection: "AccountSelection",
                                         manage_budget_file_radiobuttons: "RadioButtonMenu",
                                         manage_budget_table: "ManageBudget"): 
        '''this will allow logic to access program systems not included in nav_map dict
        \nit is called in MainWindow, after the system is instantiated'''
        self.visual_functions = visual_functions
        self.nav_panel = nav_panel
        self.main_menu = main_menu
        self.create_new_template_radiobuttons = create_new_template_radiobuttons
        self.create_new_template_editor = create_new_template_editor
        self.create_new_budget_editor = create_new_budget_editor
        self.create_new_account_selection = create_new_account_selection
        self.manage_budget_file_radiobuttons = manage_budget_file_radiobuttons
        self.manage_budget_table = manage_budget_table

    def give_logic_temp_window_acess(self, 
                                     save_window: "SaveNameWindow | None" = None, 
                                     transaction_list_window: "TransactionListWindow | None" = None,
                                     transaction_editor_window: "TransactionEditorWindow | None" = None):
        '''Gives logic access to the members of temporary windows/toplevels
        \nLogic.py requires the class to be imported under TYPECHECKING, and a reference to the class instance added as an optional parameter
        \nA call to this method must appear in the __init__ for the given class, passing self for the appropriate argument'''
        if save_window != None:
            self.save_window = save_window
        if transaction_list_window != None:
            self.transaction_list_window = transaction_list_window
        if transaction_editor_window != None:
            self.transaction_editor_window = transaction_editor_window
    
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
    
    def set_main_window_scaling_factor(self, main_window, main_window_width: int):
        '''create a var storing scaling factor = actual window width / specified window width'''
        self.scaling_factor = self.visual_functions.get_widget_width(main_window) / main_window_width  

    def get_date_from_system(self):
        self.year: int = datetime.datetime.today().year
        self.month: int = datetime.datetime.today().month
        self.day: int = datetime.datetime.today().day
    

    #NAVIGATION PANEL
    def add_to_nav_map(self, system_name: str, page, page_func):
        '''adds new system to nav_map used by navigation menu,
        where 'system' is a str (simple descriptor of the system), 
        'page' is an instance reference for the class that defines each page of that system
        'page_func is the function that is called when each page is raised using self.selected_system_pages[0][self.current_page]
        when the page is raised in the nave button functions you can also call the associated function using self.selected_system_pages[1][self.current_page]'''
        if self.nav_map.get(system_name) != None:
            pass #key already exists, do nothing
        else: #create empty list of lists for new system's pages and funcs
            self.nav_map[system_name] = [[],[]]
        if page not in self.nav_map.get(system_name, [])[0]:
            self.nav_map.get(system_name, [])[0].append(page)
            self.nav_map.get(system_name, [])[1].append(page_func)
        else:
            pass #page (instance ref) already in list, do nothing

    def system_selection(self, system_name: SystemNames): #occurs from main menu
        self.ready_to_continue = True #ensure this is reset when selecting new system from main menu
        self.at_system_end: bool = False
        self.selected_system_name = system_name.name
        self.selected_system_pages: list = self.nav_map.get(system_name.value, [])[0]
        self.selected_system_methods: list = self.nav_map.get(system_name.value, [])[1]
        self.current_page = 0
        self.visual_functions.raise_panel(self.selected_system_pages[self.current_page])
        self.visual_functions.raise_panel(self.nav_panel)
        self.selected_system_methods[self.current_page]() #should call func for first page of selected system
        #clear selection from radiobuttons
        if system_name.name == SystemNames.create_new_system.name:
            self.create_new_template_radiobuttons.clear_selection()
            self.nav_panel.set_radiobutton_buttons_to_inactive()
        elif system_name.name == SystemNames.manage_budget_system.name:
            self.manage_budget_file_radiobuttons.clear_selection()
            self.nav_panel.set_radiobutton_buttons_to_inactive()

    def nav_panel_continue_button(self): 
        #standard page turning logic
        if self.current_page < len(self.selected_system_pages) - 1: #not at end of pages, adv current page, raise corresponding page, call its starting method
            self.current_page += 1
            self.selected_system_methods[self.current_page]()
        elif self.current_page == len(self.selected_system_pages) - 1: # at end, continue does nothing
            self.at_system_end = True
        if self.ready_to_continue == True:
            self.visual_functions.raise_panel(self.selected_system_pages[self.current_page])
        
        #special case logic
        if self.current_page == 1 and self.selected_system_name == SystemNames.manage_budget_system.name: #entering manager, set continue button text to 'Main Menu'
            self.visual_functions.configure_widget(self.nav_panel.button_continue, new_text="Main Menu")
        if self.at_system_end == True and self.selected_system_name == SystemNames.manage_budget_system.name: #at manager, continue btn should raise main menu and clear manager
            self.clear_manager_close_conn()
            self.nav_panel.disable_manager_buttons()
            self.visual_functions.raise_panel(self.main_menu)
            self.visual_functions.configure_widget(self.nav_panel.button_continue, new_text="Continue")            
        if self.at_system_end == True and self.selected_system_name == SystemNames.create_new_system.name: #at account selection,user can return to main or go to manager
            self.account_selection_confirmed()

    def nav_panel_back_button(self): #NOTE, the page if conds should appear in inverse of the continue button (counting down)  
        if self.current_page == 1: #returning to radiobutton menu #0, reload template/budget list  
            self.selected_system_methods[self.current_page - 1]()
            if self.selected_system_name == SystemNames.manage_budget_system.name: #at manager, reconfig nav buttons, and clear treeview
                self.nav_panel.disable_manager_buttons()
                self.visual_functions.configure_widget(self.nav_panel.button_continue, new_text="Continue")
                self.clear_manager_close_conn()
                
        #standard page turning logic
        if self.current_page > 0: #not at first page, go to previous page
            self.visual_functions.raise_panel(self.selected_system_pages[self.current_page - 1])
            self.current_page -= 1  
        elif self.current_page == 0: #currently on radiobutton menu,return to main menu
            self.visual_functions.raise_panel(self.main_menu)

    #RADIOBUTTON MENU 
    def display_template_list(self): #this for example could apply to templates and budget files
        self.template_list = [self.default_budget_template]
        self.template_title_list = [self.default_budget_template.get("Title", str)]
        template_path = os.path.join(self.user_files_path, "budget templates.json")
        try:
            with open(template_path, 'r') as template_import:
                imported_templates = json.load(template_import)
                for user_template in imported_templates:
                    self.template_list.append(user_template)
                    self.template_title_list.append(user_template.get("Title"))
        except FileNotFoundError:
            pass #file is not found, load only default to list 
        self.create_new_template_radiobuttons.destroy_radiobuttons()
        self.create_new_template_radiobuttons.create_radiobuttons(self.template_title_list)
        self.nav_panel.enable_radiobutton_buttons()
        self.initialize_radiobutton_deletion_lists()
    
    def display_budget_files(self): #find all sqlite files in cwd, and place them in list - when page is raised
        self.budget_list = []
        self.file_list = os.listdir(self.user_files_path)
        for file in self.file_list:
            if file.endswith(".sqlite") == True:
                self.budget_list.append(file.split(".")[0])
        self.manage_budget_file_radiobuttons.destroy_radiobuttons() 
        self.manage_budget_file_radiobuttons.create_radiobuttons(self.budget_list)
        self.nav_panel.enable_radiobutton_buttons()
        self.initialize_radiobutton_deletion_lists()

    def store_selected_template_dict(self) -> dict | None: #called by display_template_and_title
        self.selected_template_title: str = self.visual_functions.extract_str_var(self.create_new_template_radiobuttons.selected_object_name_widget_str)
        selected_template_dict: dict = {}
        for template in self.template_list:
            if template.get("Title", str) == self.selected_template_title:
                selected_template_dict = template
                self.nav_panel.disable_radiobutton_buttons()
                return selected_template_dict
        
    def check_and_store_selected_budget(self):
        selected_budget_name: str = self.visual_functions.extract_str_var(self.manage_budget_file_radiobuttons.selected_object_name_widget_str)
        if selected_budget_name == "": #no budget was selected
            self.ready_to_continue = False
            self.current_page -= 1
        elif selected_budget_name != "":
            self.ready_to_continue = True
            self.nav_panel.disable_radiobutton_buttons()
            self.display_budget_management_table(selected_budget_name)

    def initialize_radiobutton_deletion_lists(self): #(re)creates these lists when entering a radiobutton menu
        self.buttons_to_delete: list = []
        self.templates_or_budgets_to_delete: list = []

    def activate_delete_radiobutton_button(self):
        activate_delete_rb: bool = True
        if self.selected_system_name == SystemNames.create_new_system.name: #unique to template editor system...
            default_rb_text: str = self.visual_functions.get_widget_attribute(self.create_new_template_radiobuttons.radiobutton_list[0], 'text')
            selected_rb_text: str = self.visual_functions.extract_str_var(self.create_new_template_radiobuttons.selected_object_name_widget_str)
            if selected_rb_text == default_rb_text: #default was not selected, user can delete
                activate_delete_rb = False
        if activate_delete_rb == True:
            self.visual_functions.configure_widget(self.nav_panel.delete_radiobutton_button, new_state='normal')

    def activate_confirm_radiobutton_button(self):
        self.visual_functions.configure_widget(self.nav_panel.confirm_radiobutton_button, new_state='normal')

    def set_radiobutton_menu_instance(self) -> Tuple[RadioButtonMenu , list]:
        if self.selected_system_name == SystemNames.create_new_system.name: #NOTE: if more than one radiobutton menu is ever added to a system, we can add self.current_page to ID the specific instance to enable unique behaviour for each
            return self.create_new_template_radiobuttons, self.template_list #NOTE: could self.template_title_list be needed? (the indices should match)
        elif self.selected_system_name == SystemNames.manage_budget_system.name:
            return self.manage_budget_file_radiobuttons, self.budget_list #NOTE: this is just the sqlite filenames, may need self.file_list
        else:
            raise ValueError(f"Failed to Assign Radiobutton Menu Instance {self.selected_system_name}")
    
    def delete_radiobutton_selection(self): 
        try:
            radiobutton_menu, self.object_list = self.set_radiobutton_menu_instance()
            self.visual_functions.configure_widget(self.nav_panel.confirm_radiobutton_button, new_state='normal')
            for i, button in enumerate(radiobutton_menu.radiobutton_list):
                buttontext: str = self.visual_functions.get_widget_attribute(button, "text")
                selected_button_text: str = self.visual_functions.extract_str_var(radiobutton_menu.selected_object_name_widget_str)
                if buttontext == selected_button_text: #selected button found, stop looping (uniqueness has been enforced so duplicates should not be possible)
                    self.visual_functions.configure_widget(button, new_font=Fonts.deleted_radiobutton.value)
                    self.buttons_to_delete.append(button)
                    self.templates_or_budgets_to_delete.append([self.object_list[i], i]) 
                    break
        except ValueError as e:
            print(f"Error: {e}")

    def confirm_radiobutton_deletions(self):
        if self.object_list == self.template_list: #deleting templates
            for i, template in enumerate(self.templates_or_budgets_to_delete):
                self.template_list.pop(template[1])
                if i < len(self.templates_or_budgets_to_delete) - 1: #decrement index of template to delete due to change in self.template_list length (only if not at end)
                    template_index = self.templates_or_budgets_to_delete[i+1][1] - 1
                    self.templates_or_budgets_to_delete[i+1][1] = template_index
            deleted_budget_templates_json = json.dumps(self.template_list[1:], indent=4)
            budget_templates_path = os.path.join(self.user_files_path, "budget templates.json")
            with open(budget_templates_path, 'w') as template_export:
                template_export.write(deleted_budget_templates_json)
                self.display_template_list()
        elif self.object_list == self.budget_list: #deleting budgets
            for budget in self.templates_or_budgets_to_delete:
                budget_path = os.path.join(self.user_files_path, budget[0] + ".sqlite")
                if os.path.exists(budget_path):
                    os.remove(budget_path)
                else:
                    raise FileNotFoundError(f"Budget File Could not be Found: {budget_path}")
            self.display_budget_files()
            
    #TEMPLATE EDITOR
    #template window
    def set_template_editor_vars(self):
        self.template_displayed = 0 #swtich indicating that a template is displayed in the editor
        self.context_menu_text_box_focus = 0 #keep track of text box focus for context menu
    
    def display_template_and_title(self): 
        self.selected_template_dict = self.store_selected_template_dict()
        self.template_editor = self.create_new_template_editor.template_editor #create instance var ref of the template editor when tempalte displayed
        if self.template_displayed == 1: #a template is already displayed, remove it before displaying new one
            self.visual_functions.delete_hierarchy_item(self.create_new_template_editor.template_editor, self.template_income_section)
            self.visual_functions.delete_hierarchy_item(self.create_new_template_editor.template_editor, self.template_expenses_section)
            self.template_displayed = 0 
        if self.template_displayed == 0: #no template currently displayed
            self.template_displayed = 1
            self.visual_functions.configure_widget(self.create_new_template_editor.template_title_label, new_text="Selected Template: " + self.selected_template_title)
            self.template_income_section = self.visual_functions.insert_into_hierarchy(self.template_editor, "", 0, text_to_insert="Income", display_open=True)
            self.template_expenses_section = self.visual_functions.insert_into_hierarchy(self.template_editor, "", 2, text_to_insert="Expenses", display_open=True)
            if type(self.selected_template_dict) == dict:
                self.display_template_section(self.selected_template_dict.get("Income", {}), self.template_income_section)
                self.display_template_section(self.selected_template_dict.get("Expenses", {}), self.template_expenses_section)
            else: #no template selected
                pass
            self.visual_functions.raise_panel(self.create_new_template_editor.context_intro_message)
        
    def display_template_section(self, template_section: dict, template_editor_section: str):
        for category in template_section.keys():
            section_category_id = self.visual_functions.insert_into_hierarchy(self.template_editor, template_editor_section, 'end', text_to_insert=category, display_open=False)
            for subcat, monthly in zip(template_section.get(category, [])[0], template_section.get(category, [])[1]):
                self.visual_functions.insert_into_hierarchy(self.template_editor, section_category_id, 'end', text_to_insert=subcat, row_values=monthly, display_open=False)

    #display context menu
    def raise_context_menu(self, event):
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
        self.visual_functions.get_hierarchy_item(self.template_editor, self.current_focused_item, new_values=[self.visual_functions.extract_int_var(self.create_new_template_editor.monthly_annual)])
   
    #SAVE WINDOW
    def clear_title_box(self, entrybox_widget):
            self.visual_functions.entrybox_delete(entrybox_widget, "0", "end")
            self.visual_functions.set_widget_focus(entrybox_widget)

    #change clear button text on hover #004d74
    def on_hover_clear(self, event, widget):
        self.visual_functions.configure_widget(widget, new_text_color="#004d74")

    def on_leave_clear(self, event, widget):
        self.visual_functions.configure_widget(widget, new_text_color="#00aaff")
    
    def call_save_methods(self, save_object_type: SaveObjectTypes):
        if save_object_type == SaveObjectTypes.template:
            self.template_name_check()
        elif save_object_type == SaveObjectTypes.budget:
            self.save_budget_file_check()

    #save object: template
    def template_name_check(self):
        default_rb_text: str = self.visual_functions.get_widget_attribute(self.create_new_template_radiobuttons.radiobutton_list[0], 'text')
        self.template_exists_warning_occured: bool = False
        self.save_budget_template_title: str = self.visual_functions.extract_str_var(self.save_window.object_name_text)
        if self.save_budget_template_title == default_rb_text: #text in save window entry is "Default", spawn special warning
            self.save_window.draw_save_warning_window(self, 1, WarningWindowText.trying_to_replace_default_template_title, WarningWindowText.trying_to_replace_default_template_message)
        elif self.save_budget_template_title in self.template_title_list:
            self.template_exists_warning_occured = True
            self.save_window.draw_save_warning_window(self, 2, WarningWindowText.template_exists_title, WarningWindowText.template_exists_message)
        else:
            self.save_budget_template()

    def save_budget_template(self):    
        if self.template_exists_warning_occured == True:
            template_to_remove: int = self.template_title_list.index(self.save_budget_template_title)
            self.template_title_list.pop(template_to_remove)
            self.template_list.pop(template_to_remove)
        if self.save_budget_template_title == "": #no text entered, do nothing
            pass
        else:
            #extract template from editor and store in dict
            incexp = self.visual_functions.get_hierarchy_item_children(self.create_new_template_editor.template_editor)
            #store income section
            inc_text = self.visual_functions.get_hierarchy_content(self.create_new_template_editor.template_editor, incexp[0], 'text')
            inc_cats = self.visual_functions.get_hierarchy_item_children(self.create_new_template_editor.template_editor, incexp[0])
            inc_dict = {}
            for cat in inc_cats:
                subcat_list = []
                annual_monthly_list = []
                for subcat in self.visual_functions.get_hierarchy_item_children(self.create_new_template_editor.template_editor, cat):
                    subcat_list.append(self.visual_functions.get_hierarchy_content(self.create_new_template_editor.template_editor, subcat, 'text'))
                    annual_monthly_list.append(self.visual_functions.get_hierarchy_content(self.create_new_template_editor.template_editor, subcat, 'values')[0])
                inc_dict[self.visual_functions.get_hierarchy_content(self.create_new_template_editor.template_editor, cat, 'text')] = [subcat_list, annual_monthly_list]
            #store expenses section
            exp_text = self.visual_functions.get_hierarchy_content(self.create_new_template_editor.template_editor, incexp[1], 'text')
            exp_cats = self.visual_functions.get_hierarchy_item_children(self.create_new_template_editor.template_editor, incexp[1])
            exp_dict = {}
            for cat in exp_cats:
                subcat_list = []
                annual_monthly_list = []
                for subcat in self.visual_functions.get_hierarchy_item_children(self.create_new_template_editor.template_editor, cat):
                    subcat_list.append(self.visual_functions.get_hierarchy_content(self.create_new_template_editor.template_editor, subcat, 'text'))
                    annual_monthly_list.append(self.visual_functions.get_hierarchy_content(self.create_new_template_editor.template_editor, subcat, 'values')[0])
                exp_dict[self.visual_functions.get_hierarchy_content(self.create_new_template_editor.template_editor, cat, 'text')] = [subcat_list, annual_monthly_list]
            #combine sections into dict, and append to list of templates
            new_template = {"Title": self.save_budget_template_title, inc_text: inc_dict, exp_text: exp_dict}
            self.template_title_list.append(self.save_budget_template_title)
            self.template_list.append(new_template)
            #export new list of templates (ignoring default), overwriting current file
            budget_templates_json = json.dumps(self.template_list[1:], indent=4)
            budget_templates_path = os.path.join(self.user_files_path, "budget templates.json")
            with open(budget_templates_path, 'w') as template_export:
                template_export.write(budget_templates_json)
            self.visual_functions.destroy_widget(self.save_window)

    #save object: budget 
    def save_budget_file_check(self):
        self.file_exists_warning_occured: bool = False
        budget_title: str = self.visual_functions.get_entrybox_content(self.save_window.object_title_box)
        if budget_title == "":
            pass #no text in budget title box, do nothing
        elif budget_title != "":
            self.budget_file_path = os.path.join(self.user_files_path, budget_title + ".sqlite")
            file_exists = os.path.isfile(self.budget_file_path)
            if file_exists == True:
                self.file_exists_warning_occured = True
                self.save_window.draw_save_warning_window(self, 2, WarningWindowText.budgetfile_exists_title, WarningWindowText.budgetfile_exists_message)
            if file_exists == False:
                self.build_budget_db_structure()

    def build_budget_db_structure(self):
        if self.file_exists_warning_occured == True:
            os.remove(self.budget_file_path) #BUG could raise permission error if connection not properly closed (and two budgets with same name created in single session)
        self.create_new_conn = sqlite3.connect(self.budget_file_path)
        self.create_new_cur = self.create_new_conn.cursor()

        self.create_new_cur.executescript('''
        CREATE TABLE IF NOT EXISTS Transactions (
                          id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                          Entity_id integer,
                          Amount DECIMAL(15,2),
                          Category_id integer,
                          Sub_Category_id integer,
                          Account_Type_id integer, 
                          Month integer,
                          Day integer
            );

        create table if not exists Entity (
                          id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                          Description text unique
            );

        create table if not exists [Category Name] (
                          id integer not null primary key autoincrement unique,
                          Category text unique,
                          Income_expense_id integer                 
            );
                        
        create table if not exists [Sub-Category Name] (
                          id integer not null primary key autoincrement unique,
                          [Sub-Category] text,
                          Category_Name_id integer,
                          Monthly_annual_id integer
            );
                        
        create table if not exists [Budget Amounts] (
                          id integer not null primary key autoincrement unique,
                          Amount DECIMAL(15,2), 
                          Sub_Category_id integer,
                          Category_id integer
            );   

        create table if not exists [Income Expense] (
                          id integer not null primary key autoincrement unique,
                          [Income/Expense] bit unique
            );

        create table if not exists [Monthly Annual] (
                          id integer not null primary key autoincrement unique, 
                          [Monthly/Annual] bit unique
            );

        create table if not exists Accounts (
                          id integer not null primary key autoincrement unique,
                          [Account Name] text
            )

        ''')

        self.create_new_cur.execute('''INSERT OR IGNORE INTO [Monthly Annual] ([Monthly/Annual]) Values ('Monthly'), ('Annual'); ''')
        self.create_new_cur.execute('''INSERT OR IGNORE INTO [Income Expense] ([Income/Expense]) Values ('Income'), ('Expenses');''')
        self.create_new_conn.commit()
        self.save_budget_data_to_db(1, self.budget_income_section)
        self.save_budget_data_to_db(2, self.budget_expenses_section)
        self.add_accounts_to_db()
        self.confirm_budget_saved()

    def save_budget_data_to_db(self, income_expense_id: int, budget_section: str):
        for cat in self.visual_functions.get_hierarchy_item_children(self.budget_table, budget_section):
            budget_category = self.visual_functions.get_hierarchy_content(self.budget_table, cat, 'values')[0]
            self.create_new_cur.execute('''INSERT OR IGNORE INTO [Category Name] ([Category], Income_expense_id) Values (?, ?)''', (budget_category, income_expense_id))
            self.create_new_conn.commit()
            self.create_new_cur.execute('''SELECT id FROM [Category Name] WHERE Category = ?''', (budget_category,))
            cat_id = self.create_new_cur.fetchone()[0]
            for subcat in self.visual_functions.get_hierarchy_item_children(self.budget_table, cat):
                budget_subcategory_name = self.visual_functions.get_hierarchy_content(self.budget_table, subcat, 'values')[0]
                budget_subcategory_annual_monthly = self.visual_functions.get_hierarchy_content(self.budget_table, subcat, 'tags')[0]
                budget_subcategory_amount = 0
                if budget_subcategory_annual_monthly == 1: #subcat is monthly
                    budget_subcategory_amount = self.visual_functions.get_hierarchy_content(self.budget_table, subcat, 'values')[2]
                elif budget_subcategory_annual_monthly == 2: #subcat is annual
                    budget_subcategory_amount = self.visual_functions.get_hierarchy_content(self.budget_table, subcat, 'values')[1]
                self.create_new_cur.execute('''INSERT OR IGNORE INTO [Sub-Category Name] ([Sub-Category], [Category_Name_id], [Monthly_annual_id]) VALUES (?, ?, ?)''', (budget_subcategory_name, cat_id, budget_subcategory_annual_monthly))
                self.create_new_conn.commit()
                self.create_new_cur.execute('''SELECT id FROM [Sub-Category Name] WHERE ([Sub-Category], [Category_Name_id]) = (?, ?)''', (budget_subcategory_name, cat_id))
                subcat_id = self.create_new_cur.fetchone()[0]
                self.create_new_cur.execute('''INSERT INTO [Budget Amounts] (Amount, [Sub_Category_id], [Category_id]) VALUES (?, ?, ?)''', (budget_subcategory_amount, subcat_id, cat_id))
        self.create_new_conn.commit()

    def add_accounts_to_db(self):
        for account in self.selected_accounts:
            self.create_new_cur.execute('''INSERT OR IGNORE INTO Accounts ([Account Name]) VALUES (?)''', (account, ))
        self.create_new_conn.commit()
        self.create_new_conn.close()

    def confirm_budget_saved(self):
        budget_confirmed = os.path.isfile(self.budget_file_path)
        if budget_confirmed == False:
            self.save_window.draw_save_warning_window(self, 1, WarningWindowText.budget_save_not_confirmed_title, WarningWindowText.budget_save_not_confirmed_message)
        else:
            self.save_window.draw_save_warning_window(self, 2, WarningWindowText.budget_save_confirmed_title, WarningWindowText.budget_save_confirmed_message)
    
    #this is needed because the save window is the parent of the warning window
    #this is called by the warning window, so user acknowledgement of failed confirmation, or cannot replace default should close only the warning window
    def destroy_warning_and_save_windows(self, warning_window: WarningWindow): 
        self.visual_functions.destroy_widget(warning_window)
        #self.visual_functions.destroy_widget(self.save_window) #if we decide that both should close de-comment this

    def return_to_mainmenu(self):
        self.visual_functions.destroy_widget(self.save_window)
        self.visual_functions.raise_panel(self.main_menu)

    def manage_new_budget(self):
        self.visual_functions.destroy_widget(self.save_window)
        self.system_selection(SystemNames.manage_budget_system)

    #BUDGET CREATOR
    def set_budget_editor_vars(self):
        self.budget_displayed = 0

    def display_budget_table(self):
        self.budget_table = self.create_new_budget_editor.budget_table
        if self.budget_displayed == 1: #budget already displayed, remove and replace
            for inc_exp in self.visual_functions.get_hierarchy_item_children(self.budget_table):
                self.visual_functions.delete_hierarchy_item(self.budget_table, inc_exp)
            self.budget_displayed = 0
        if self.budget_displayed == 0:
            self.visual_functions.configure_hierarchy_values(self.budget_table, "incexpfont", "Calibri", 18, 'underline')
            self.visual_functions.configure_hierarchy_values(self.budget_table, "catfont", "Calibri", 18, "bold")
            self.budget_income_section = self.visual_functions.insert_into_hierarchy(self.budget_table, "", 'end', row_values=("Income", "", ""), tags=("incexpfont",), display_open=True)
            self.budget_expenses_section = self.visual_functions.insert_into_hierarchy(self.budget_table, "", 'end', row_values=("Expenses", "", ""), tags=("incexpfont",), display_open=True)
            self.display_budget_table_sections(self.template_income_section, self.budget_income_section) 
            self.display_budget_table_sections(self.template_expenses_section, self.budget_expenses_section)
            self.budget_displayed = 1
        else: #budget already displayed, this should not happen
            pass

    def display_budget_table_sections(self, template_section: str, budget_section: str): #NOTE this method extracts the content of the template, but the insert commands reference the budget
        template_section_children = self.visual_functions.get_hierarchy_item_children(self.template_editor, template_section)
        for category in template_section_children:
            category_text = self.visual_functions.get_hierarchy_content(self.template_editor, category, 'text')
            budget_category = self.visual_functions.insert_into_hierarchy(self.budget_table, budget_section, 'end', row_values=[category_text, "----------", "----------"], tags=("catfont",))
            category_children = self.visual_functions.get_hierarchy_item_children(self.template_editor, category)
            for subcat in category_children:
                subcat_text = self.visual_functions.get_hierarchy_content(self.template_editor, subcat, 'text')
                subcat_values = self.visual_functions.get_hierarchy_content(self.template_editor, subcat, 'values')
                if subcat_values[0] == 1: #monthly
                    self.visual_functions.insert_into_hierarchy(self.budget_table, budget_category, 'end', row_values=[subcat_text, "----------", ""], tags=("1",))
                elif subcat_values[0] == 2: #annual
                    self.visual_functions.insert_into_hierarchy(self.budget_table, budget_category, 'end', row_values=[subcat_text, "", "----------"], tags=("2",))
    
    #events (core budget editing logic)
    def budget_table_double_click(self, event): #NOTE: in manager, we use tags to ID hierarchy level.  That may work here as well (if we can add tags at table creation)
        current_focused_item = self.visual_functions.get_hierarchy_focus(self.budget_table)
        focused_item_grand_grandparent = self.visual_functions.get_hierarchy_item_parent(self.budget_table, self.visual_functions.get_hierarchy_item_parent(self.budget_table, current_focused_item))
        self.selected_budget_table_row_tags = self.visual_functions.get_hierarchy_content(self.budget_table, self.visual_functions.get_hierarchy_row(self.budget_table, event.y), 'tags')
        self.selected_budget_table_col = 3-int(self.selected_budget_table_row_tags[0])
        self.selected_budget_table_row = self.visual_functions.get_hierarchy_row(self.budget_table, event.y)
        if self.visual_functions.get_hierarchy_content(self.budget_table, focused_item_grand_grandparent, 'values') == "":
            self.create_new_budget_editor.entry_box_exists = False
            return 'break' #user dbl clicked a non-sub-category, do nothing
        if self.visual_functions.get_hierarchy_content(self.budget_table, focused_item_grand_grandparent, 'values') != "":            
            self.create_new_budget_editor.draw_budget_entry_box()            

    def set_entrybox_location(self)-> tuple[int, int, int, int]:        
        box_location = self.visual_functions.draw_hierarchy_bbox(self.budget_table, self.selected_budget_table_row, col=self.selected_budget_table_col)
        #NOTE: the column where the bbox appears is determined by it being monthly or annual, NOT by the location of the dbl click x-axis
        box_location = (
            int(float(box_location[0]) / self.scaling_factor),
            int(float(box_location[1]) / self.scaling_factor),
            int(float(box_location[2]) / self.scaling_factor),
            int(float(box_location[3]) / self.scaling_factor),
        )        
        return box_location

    def update_budget_table_entry(self, event, entrybox):
        selected_row_data = self.visual_functions.get_hierarchy_content(self.budget_table, self.selected_budget_table_row, 'values')
        try:
            selected_row_data[self.selected_budget_table_col] = '${:,.2f}'.format(float(self.visual_functions.get_entrybox_content(entrybox)))
            self.visual_functions.get_hierarchy_item(self.budget_table, self.selected_budget_table_row, new_values=selected_row_data)
        except ValueError:
            pass
        self.visual_functions.destroy_widget(entrybox)

    #Continue button clicked-check budget table entries
    def check_budget_table(self):
        self.ready_to_continue = False #prevent continue unless error not triggered
        self.blank_annuals = ""
        self.blank_monthlies = ""
        self.subcat_list = [] #creates list of all sub-category_data
        for incexp in self.visual_functions.get_hierarchy_item_children(self.budget_table):
            for cat in self.visual_functions.get_hierarchy_item_children(self.budget_table, incexp):
                for subcat in self.visual_functions.get_hierarchy_item_children(self.budget_table, cat):
                    self.subcat_list.append(subcat) 
        self.check_budget_subcat_values()
        if self.blank_annuals != "" or self.blank_monthlies != "":
            self.create_new_budget_editor.raise_blank_cells_error()
        else:
            self.ready_to_continue = True

    def check_budget_subcat_values(self):
        self.subcat_list_no_values = [] #creates list of all sub-cats with no values
        for subcat in self.subcat_list:
            if self.visual_functions.get_hierarchy_content(self.budget_table, subcat, 'tags')[0] == 1: #monthly, check values[2]
                if self.visual_functions.get_hierarchy_content(self.budget_table, subcat, 'values')[2] == "": #blank entry
                    self.blank_monthlies += self.visual_functions.get_hierarchy_content(self.budget_table, subcat, 'values')[0] + "\n"
                    self.subcat_list_no_values.append(subcat) 
            elif self.visual_functions.get_hierarchy_content(self.budget_table, subcat, 'tags')[0] == 2: #annual, check values[1]
                if self.visual_functions.get_hierarchy_content(self.budget_table, subcat, 'values')[1] == "": #blank entry
                    self.blank_annuals += self.visual_functions.get_hierarchy_content(self.budget_table, subcat, 'values')[0] + "\n"
                    self.subcat_list_no_values.append(subcat)

    def return_to_budget_editor(self, empty_cells_window):
        self.visual_functions.destroy_widget(empty_cells_window)
        self.current_page -= 1

    def fill_empty_cells_with_0(self):  
        for subcat in self.subcat_list_no_values:
            if self.visual_functions.get_hierarchy_content(self.budget_table, subcat, 'tags')[0] == 1: #monthly
                subcat_values = self.visual_functions.get_hierarchy_content(self.budget_table, subcat, 'values') #get current values
                subcat_values[2] = '${:,.2f}'.format(float(0.00)) #replace blank with '$0.00'
                self.visual_functions.get_hierarchy_item(self.budget_table, subcat, new_values=subcat_values) #add new values to table
            elif self.visual_functions.get_hierarchy_content(self.budget_table, subcat, 'tags')[0] == 2: #monthly
                subcat_values = self.visual_functions.get_hierarchy_content(self.budget_table, subcat, 'values') #get current values
                subcat_values[1] = '${:,.2f}'.format(float(0.00)) #replace blank with '$0.00'
                self.visual_functions.get_hierarchy_item(self.budget_table, subcat, new_values=subcat_values) #add new values to table
        self.visual_functions.destroy_widget(self.create_new_budget_editor.blank_cells_window) #destroy blank cells warning window
        self.ready_to_continue = True
        self.visual_functions.raise_panel(self.selected_system_pages[self.current_page])

    #ACCOUNT SELECTION
    def not_checkable(self): #sets checkbox to stay selected if clicked 
            self.visual_functions.checkbox_select(self.create_new_account_selection.account_selection_checkbox_list[0]) 

    def user_selects_account(self):
        checkable_box_checked: bool = False
        for box in self.create_new_account_selection.account_selection_checkbox_list[1:]:
            checkable_box_checked = (self.visual_functions.get_checkbox_status(box) == 1)
            if checkable_box_checked == True:
                break
        if self.visual_functions.get_checkbox_attribute(self.create_new_account_selection.account_selection_checkbox_list[0], "state") == 'normal' and checkable_box_checked == True:
            self.visual_functions.checkbox_deselect(self.create_new_account_selection.account_selection_checkbox_list[0])
            self.visual_functions.configure_widget(self.create_new_account_selection.account_selection_checkbox_list[0], new_state='disabled')
        elif self.visual_functions.get_checkbox_attribute(self.create_new_account_selection.account_selection_checkbox_list[0], "state") == 'disabled' and checkable_box_checked == False:
            self.visual_functions.checkbox_select(self.create_new_account_selection.account_selection_checkbox_list[0])
            self.visual_functions.configure_widget(self.create_new_account_selection.account_selection_checkbox_list[0], new_state='normal')

    def account_selection_confirmed(self):
        self.selected_accounts = []
        for account in self.create_new_account_selection.account_selection_checkbox_list:
            if self.visual_functions.get_checkbox_status(account) == 1:
                self.selected_accounts.append(self.visual_functions.get_checkbox_attribute(account, 'text'))
        self.create_new_account_selection.draw_save_budget_window(self)

    #BUDGET MANAGER
    def set_budget_manager_vars(self):
        self.budget_displayed_in_manager = 0 #indicator: budget is displayed in table
        #self.editor_window_exists: bool = False #keeps track of editor window, to prevent multiple spawns (used when editing more than one transaction)
        self.tab_title_list = ["Annual", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "Yearly Total"]
        self.proper_cell_selected: bool = False

    def display_budget_management_table(self, selected_budget_name): #this triggers on raise, load budget, configure treeviews based on # of accounts
        self.budget_section_list = [] #store list of budget sections in treeview (for easy looping across all tabs)
        self.budget_category_list = [] #store list of budget category_data in treeview 
        self.budget_subcat_list = [] #store list of budget sub-category_data in treeview
        self.visual_functions.configure_widget(self.manage_budget_table.manage_budget_label, new_text="Manage Budget: " + selected_budget_name)
        self.budget_file_path = os.path.join(self.user_files_path, selected_budget_name + ".sqlite")
        self.manage_budget_conn = sqlite3.connect(self.budget_file_path) 
        self.manage_budget_cur = self.manage_budget_conn.cursor()
        self.manage_budget_cur.execute("select Accounts.[Account Name], Accounts.id from Accounts")
        self.budget_accounts_data = self.manage_budget_cur.fetchall()
        self.budget_accounts_name_list = []
        self.budget_table_headings = ["", "Budget"]
        for account in self.budget_accounts_data:
            self.budget_accounts_name_list.append(account[0])
            self.budget_table_headings.append(account[0])
        if len(self.budget_accounts_data) > 1:
            self.budget_table_headings.append("Total")
        for budget_table in self.manage_budget_table.treeview_list:
            for existing_budget_section in self.visual_functions.get_hierarchy_item_children(budget_table):
                self.visual_functions.delete_hierarchy_item(budget_table, existing_budget_section)
            self.visual_functions.configure_hierarchy_options(budget_table, self.budget_table_headings)
            for heading in self.budget_table_headings:
                self.visual_functions.set_hierarchy_heading_text(budget_table, column=heading, text=heading)
                if self.budget_table_headings.index(heading) == 0:
                    self.visual_functions.set_hierarchy_column_options(budget_table, column=heading, stretch=True, width=200)
                else:
                    self.visual_functions.set_hierarchy_column_options(budget_table, column=heading, stretch=True, width=50)  
            self.visual_functions.configure_hierarchy_values(budget_table, "incexpfont", "Calibri", 18, 'underline')
            self.visual_functions.configure_hierarchy_values(budget_table, "catfont", "Calibri", 18, "bold")      
        self.fetch_budget_data()
        self.budget_displayed_in_manager = 1
        self.fetch_transaction_data_from_db()
        self.nav_panel.enable_manager_buttons()
        self.store_budget_structure()
        self.set_active_treeview()

    def fetch_budget_data(self):
        self.manage_budget_cur.execute("select [Income Expense].[Income/Expense], [Income Expense].id from [Income Expense]")
        self.income_expense_data = self.manage_budget_cur.fetchall()
        self.income_expense_str_list: list = []
        for section in self.income_expense_data:
            self.income_expense_str_list.append(section[0])
        self.manage_budget_cur.execute("select [Category Name].Category, [Category Name].Income_expense_id, [Category Name].id from [Category Name]")
        self.category_data = self.manage_budget_cur.fetchall()
        self.manage_budget_cur.execute('''select [Sub-Category Name].[Sub-Category], 
                                       [Budget Amounts].Amount, 
                                       [Sub-Category Name].id,
                                       [Budget Amounts].id,
                                       [Budget Amounts].Sub_Category_id,
                                       [Sub-Category Name].Monthly_annual_id,
                                       [Budget Amounts].Category_id 
                                       from [Sub-Category Name] join [Budget Amounts] on [Budget Amounts].Sub_Category_id = [Sub-Category Name].id''')
        self.subcategory_and_amount_data = self.manage_budget_cur.fetchall()
        self.subcat_budgetamounts = []
        for entry in self.subcategory_and_amount_data:
            self.subcat_budgetamounts.append([entry[0], entry[1], entry[2], entry[5], entry[6]]) #[subcat label, amount, sub-cat-id, monthly-annual, category-id]
        for index, table in enumerate(self.manage_budget_table.treeview_list):
            self.display_budget_data(table, index, self.income_expense_data[0][0], self.income_expense_data[0][1]) #income
            self.display_budget_data(table, index, self.income_expense_data[1][0], self.income_expense_data[1][1]) #expenses

    def display_budget_data(self, table, table_index: int, budget_section_name: str, budget_section_id: str):
            budget_section  = self.visual_functions.insert_into_hierarchy(table, "", 'end', text_to_insert='', row_values=[budget_section_name, "", ""], display_open=True, tags=(budget_section_id, "incexpfont", HierarchyLevel.incexp.value))
            self.budget_section_list.append(budget_section)
            if table_index == 0: #annual tab
                self.display_budget_category_data(table, budget_section, budget_section_id, 'annual')
            elif table_index < 13: #monthly
                self.display_budget_category_data(table, budget_section, budget_section_id, 'monthly')
            elif table_index == 13: #yearly total
                self.display_budget_category_data(table, budget_section, budget_section_id, 'yearly total')
               
    def display_budget_category_data(self, table, budget_section: str, inc_exp_id: str, tab_type: Literal['annual'] | Literal['monthly'] | Literal['yearly total']):
        for category in self.category_data:
            if category[1] == inc_exp_id: #is cat income or expense
                budget_category_labels = [category[0]]
                [budget_category_labels.append("----------") for i in range(1, len(self.budget_table_headings))]
                budget_category = self.visual_functions.insert_into_hierarchy(table, budget_section, 'end', row_values=(budget_category_labels), display_open=True, tags=(category[2], "catfont", HierarchyLevel.category.value))
                self.budget_category_list.append(budget_category)
                for subcat in self.subcat_budgetamounts:
                    if subcat[4] == category[2]: #match subcat's cat id to cat id
                        subcat_display = [subcat[0], subcat[1]] #subcat name, budget amount
                        [subcat_display.append("") for i in range(2, len(self.budget_table_headings))]
                        if tab_type == "yearly total" and subcat[3] == 1: #add monthly, * 12.  Would yearly total, annuals be caught by the 'else' below?
                            subcat_display[1] = '${:,.2f}'.format(float(subcat[1].replace(",", "").strip("$")) * self.month)
                        elif tab_type == "annual" and subcat[3] == 1 or tab_type == 'monthly' and subcat[3] == 2: #annual tab+monthly subcat or monthly tab+annual subcat 
                            subcat_display = [subcat_display[i] if i <= 1 else "----------" for i in range(len(subcat_display))] 
                        current_subcat_values = self.visual_functions.insert_into_hierarchy(table, budget_category, 'end', row_values=(subcat_display), display_open=True, tags=(subcat[2], HierarchyLevel.subcategory.value))     
                        if tab_type == "annual": 
                            self.budget_subcat_list.append(current_subcat_values)
                category_total_rowdata: list = ["Total"]                
                self.visual_functions.insert_into_hierarchy(table, budget_category, 'end', row_values=category_total_rowdata, display_open=True, tags=("category total",))
    
    def fetch_transaction_data_from_db(self):
        '''get transaction data from db, match to each tab (annual/month), 
        \nthen feed list of matches into add_transaction_data_to_table, for matching to subcat and account'''
        self.manage_budget_cur.execute('''select Transactions.id, 
                    Transactions.Amount, 
                    [Category Name].Income_expense_id,
                    Transactions.Category_id, 
                    Transactions.Sub_Category_id, 
                    Transactions.Account_Type_id, 
                    Transactions.Month
                    from Transactions join  [Category Name] on Transactions.Category_id = [Category Name].id''')
        transactions = self.manage_budget_cur.fetchall()
        for tab, table in enumerate(self.manage_budget_table.treeview_list[:-1]): #match transactions to corresponding tab
            matched_transactions = []
            non_matched_transactions = []
            for transaction in transactions:
                if transaction[6] == tab: #match transaction month to corresponding tab
                    matched_transactions.append(transaction)
                else:
                    non_matched_transactions.append(transaction)
            transactions = non_matched_transactions
            self.add_transaction_data_to_table(table, matched_transactions)
    
    def add_transaction_data_to_table(self, table, matched_transactions): #called for each treeview/tab
        '''go through all calls in current table, find matching transactions,
        \nupdate account data and calculate row total (if more than one account in budget)
        \nNote: this includes process to reduce the size of matched transactions list as matches are found'''
        for subcat in self.budget_subcat_list:
            subcat_data = self.visual_functions.get_hierarchy_content(table, subcat, 'values')
            match_found = False
            for account in self.budget_accounts_data:
                transactions_for_current_cell: float = 0
                subcat_acct_non_matched_transactions = []
                for transaction_tab_match in matched_transactions:
                    #if transaction matches on subcat_id and on account 
                    if transaction_tab_match[4] == self.visual_functions.get_hierarchy_content(table, subcat, 'tags')[0] and transaction_tab_match[5] == account[1]: 
                        transactions_for_current_cell += transaction_tab_match[1]
                        match_found = True
                    else:
                        subcat_acct_non_matched_transactions.append(transaction_tab_match)
                if match_found == True: 
                    subcat_data[account[1] + 1] = '${:,.2f}'.format(transactions_for_current_cell)
                    if subcat_data[account[1]] == '': #previous col was left blank (can only happen with more than one acct)
                        subcat_data[account[1]] = '$0.00' #do not leave blank cells, in a row with at least one transaction
                    if len(self.budget_accounts_data) > 1 and account == self.budget_accounts_data[-1]: #there is a total col, and current account is last in list
                        self.calculate_row_totals(subcat_data)
                    matched_transactions = subcat_acct_non_matched_transactions
            self.visual_functions.get_hierarchy_item(table, subcat, new_values=subcat_data)
        self.calculate_column_subtotals(table, self.budget_section_list[0]) #income
        self.calculate_column_subtotals(table, self.budget_section_list[1]) #expenses
                    
    def calculate_row_totals(self, subcat_data: list[str]):
        '''loop through each acct/col, destring and add to total, then restring and add to subcat data'''
        row_transaction_total = 0
        for col in range(2, len(self.budget_accounts_data) + 2): 
            row_transaction_total += float(subcat_data[col].replace(",", "").strip("$"))
        subcat_data[-1] = '${:,.2f}'.format(row_transaction_total)
        
    def calculate_column_subtotals(self, table, section: str): 
        for cat in self.visual_functions.get_hierarchy_item_children(table, section):
            cat_values = self.visual_functions.get_hierarchy_content(table, cat, "values")
            category_totals_list: list[float] = [0 for i in range(len(cat_values)-1)]
            subcat_items = self.visual_functions.get_hierarchy_item_children(table, cat)
            for subcat in subcat_items[:-1]: #excludes total row
                subcat_values: list[str] = self.visual_functions.get_hierarchy_content(table, subcat, "values")
                for i, col in enumerate(category_totals_list):
                    if subcat_values[i+1] == "----------" or subcat_values[i+1] == "":
                        pass #catches non-number cells, dashed or blank NOTE: may want to consider a try except instead
                    else:
                        category_totals_list[i] += float(subcat_values[i+1].replace(",", "").strip("$"))                
            total_row_values = self.visual_functions.get_hierarchy_content(table, subcat_items[-1], "values")
            for total in category_totals_list:
                total_row_values.append('${:,.2f}'.format(total))
            self.visual_functions.get_hierarchy_item(table, subcat_items[-1], new_values=total_row_values)
        
    def calculate_and_display_yearly_totals(self):
        '''called by event:selection of yearly tab, so totals are calculated only when the tab is selected'''
        #disable manager window buttons NOTE: when we explore the possibilty of reviewing years transactions from yearly total tab this will have to be changed
        self.visual_functions.configure_widget(self.nav_panel.add_new_transaction_button, new_state='disabled')
        self.visual_functions.configure_widget(self.nav_panel.edit_transactions_button, new_state='disabled')
        for column, heading in enumerate(self.budget_table_headings[2:]):
            for subcat in self.budget_subcat_list:
                current_yearly_total_cell: float = 0.0
                current_yearly_total_row: list = self.visual_functions.get_hierarchy_content(self.manage_budget_table.treeview_list[13], subcat, 'values')
                for tab in self.manage_budget_table.treeview_list[:self.month + 1]:
                    current_cell: str = self.visual_functions.get_hierarchy_content(tab, subcat, 'values')[column+2]
                    if current_cell == "" or current_cell == "----------": #cell is blank or dashed out, skip
                        pass
                    else:
                        current_cell_flt: float = float(current_cell.replace(",", "").strip("$"))
                        current_yearly_total_cell += current_cell_flt
                current_yearly_total_row[column+2] = '${:,.2f}'.format(current_yearly_total_cell)
                self.visual_functions.get_hierarchy_item(self.manage_budget_table.treeview_list[13], subcat, new_values=current_yearly_total_row)
        self.calculate_column_subtotals(self.manage_budget_table.treeview_list[-1], self.budget_section_list[0]) #income
        self.calculate_column_subtotals(self.manage_budget_table.treeview_list[-1], self.budget_section_list[1]) #expenses
    
    def store_budget_structure(self):
        '''stores the structure of the budgets strings, including income/expense, categories, subcategories and annual/monthly,
        \nthis is used in the editor window to set dropdown values based on their parent in this structure'''
        self.budget_structure = {}
        for incexp in self.income_expense_data:
            temp_section_dict = {}
            for category in self.category_data:
                temp_subcat_list = []
                temp_annual_monthly_list = []
                for subcat in self.subcategory_and_amount_data:
                    if subcat[6] == category[2]:
                        temp_subcat_list.append(subcat[0])
                        temp_annual_monthly_list.append(subcat[5])
                if category[1] == incexp[1]:
                    temp_section_dict[category[0]] = [temp_subcat_list, temp_annual_monthly_list]
            self.budget_structure[incexp[0]] = temp_section_dict
    
    def set_active_treeview(self):
        self.current_tab_num: int = self.visual_functions.get_tab_index(self.manage_budget_table.manage_budget_tabs, 
                                                                   self.visual_functions.get_active_tab(self.manage_budget_table.manage_budget_tabs))
        if self.budget_displayed_in_manager == 1 and self.current_tab_num != 13: #bind cell click functions, (reset manager buttons to disabled)
            self.set_budget_button_status(False)
            self.manage_budget_table.set_bindings(self.current_tab_num)
        elif self.budget_displayed_in_manager == 1 and self.current_tab_num == 13: #do not apply bindings to yearly total tab (prevents editing of this treeview)
            self.calculate_and_display_yearly_totals()
    
    #events
    def budget_manager_single_click(self, event, treeview):
        #ID selected row & col
        self.selected_column = int(self.visual_functions.id_hierarchy_column(treeview, event.x).strip("#"))
        self.selected_row_item = self.visual_functions.id_hierarchy_row(treeview, event.y)
        #these data are needed for cell based functionality (adding,deleting,editing transactions)
        self.selected_row_data: list[str] = self.visual_functions.get_hierarchy_content(treeview, self.selected_row_item, 'values') #store selected row data
        self.selected_row_tags: list[str] = self.visual_functions.get_hierarchy_content(treeview, self.selected_row_item, 'tags')
        self.selected_row_parent: str = self.visual_functions.get_hierarchy_item_parent(treeview, self.selected_row_item) 
        self.selected_row_parent_data: list[str] = self.visual_functions.get_hierarchy_content(treeview, self.selected_row_parent, 'values') #store category data for list and editor windows
        self.selected_row_grandparent: str = self.visual_functions.get_hierarchy_item_parent(treeview, self.selected_row_parent) 
        self.selected_row_parent_tags: list[str] = self.visual_functions.get_hierarchy_content(treeview, self.selected_row_parent, 'tags')
        self.selected_row_grandparent_data: list[str] = self.visual_functions.get_hierarchy_content(treeview, self.selected_row_grandparent, 'values') #store income/expense data for list and editor windows
        self.selected_row_grandparent_tags: list[str] = self.visual_functions.get_hierarchy_content(treeview, self.selected_row_grandparent, 'tags')
        if self.selected_row_item == "": #non-row item selected, do nothing
            return "break"
        if self.manage_budget_table.cell_highlight_exists == True:
            self.visual_functions.destroy_widget(self.manage_budget_table.cell_highlight)
            self.manage_budget_table.cell_highlight_exists = False 
        self.validate_selected_cell()
        self.manage_budget_table.draw_cell_highlight(treeview, self.proper_cell_selected)
        self.set_budget_button_status(self.proper_cell_selected)

    def validate_selected_cell(self): #these 3 conditions together indicate a cell was selected that user can add data to, sets selected cell bool as instance var
        open_subcat: bool =  self.selected_row_tags[-1] == HierarchyLevel.subcategory.value and self.selected_row_data[self.selected_column-1] != "----------" 
        transaction_column: bool =  self.selected_column > 2
        non_total_col: bool = len(self.selected_row_data) == 3 or len(self.selected_row_data) > 3 and self.selected_column < len(self.selected_row_data)
        self.proper_cell_selected: bool = open_subcat and transaction_column and non_total_col

    def set_selected_cell_location(self, treeview) -> Tuple[int, int, int, int]:            
        cell_location = self.visual_functions.draw_hierarchy_bbox(treeview, self.selected_row_item, self.selected_column-1)
        cell_location = (
                        int(float(cell_location[0]) / self.scaling_factor),
                        int(float(cell_location[1]) / self.scaling_factor),
                        int(float(cell_location[2]) / self.scaling_factor),
                        int(float(cell_location[3]) / self.scaling_factor),
                        )
        return cell_location[0], cell_location[1], cell_location[2], cell_location[3]            
        
    def set_budget_button_status(self, proper_cell: bool):
        if proper_cell: #proper cell selected, enable management buttons in nav panel
            self.visual_functions.configure_widget(self.nav_panel.add_new_transaction_button, new_state='normal')
            self.visual_functions.configure_widget(self.nav_panel.edit_transactions_button, new_state='normal')
        else: 
            self.visual_functions.configure_widget(self.nav_panel.add_new_transaction_button, new_state='disabled')
            self.visual_functions.configure_widget(self.nav_panel.edit_transactions_button, new_state='disabled')

    def invoke_manage_budget_buttons(self, event): #dbl click event
        if self.selected_row_item == "":
            return "break"
        if self.proper_cell_selected:
            if self.selected_row_data[self.selected_column-1] == "" or self.selected_row_data[self.selected_column-1] == "$0.00": #empty/0 cell dbl clicked, raise transaction editor
                self.visual_functions.invoke_button(self.nav_panel.add_new_transaction_button)
            elif self.selected_row_data[self.selected_column-1] != "" or self.selected_row_data[self.selected_column-1] != "$0.00": #non-empty cell cbl clicked, raise transaction list
                self.visual_functions.invoke_button(self.nav_panel.edit_transactions_button)

    def clear_manager_close_conn(self):
        for treeview in self.manage_budget_table.treeview_list:
            root_items = self.visual_functions.get_hierarchy_item_children(treeview)
            for item in root_items:
                self.visual_functions.delete_hierarchy_item(treeview, item)
        self.manage_budget_conn.close()

    #TRANSACTION LIST WINDOW
    def get_selected_cell_info(self, add_new_from_navpanel): 
        '''add_new_from_navpanel = 1 means 'add transaction' button was pressed from manager window 
        \nadd_new_from_navpanel = 0 means 'add new' button was pressed in the list window
        In both cases, info about the selected cell is needed, but the sql query is made only if the list window is displayed (add_new_from_navpanel = 0)'''
        #store cell info text and ID [month, account, income/expense, category, subcategory]
        self.selected_cell_info_list = [self.tab_title_list[self.current_tab_num], 
                                        self.budget_accounts_data[self.selected_column-3][0],
                                        self.selected_row_grandparent_data[0],
                                        self.selected_row_parent_data[0],
                                        self.selected_row_data[0]]
        if add_new_from_navpanel == 0: #attempt to load transaction info from database (this func was called from list window)
            self.manage_budget_table.draw_transaction_list_window()
            self.load_cell_transactions_from_db()
        if add_new_from_navpanel == 1: #bypass transaction list, and do not load transactions from database, go to transaction editor passing cell info
            self.manage_budget_table.draw_transaction_editor_window(add_new_button=True, called_by_manager=True)

    def load_cell_transactions_from_db(self):       
        #load transaction information for selected cell from DB (eventually transaction info will include day and entity)        
        self.manage_budget_cur.execute('''select Transactions.id, 
                                        [Category Name].[Income_expense_id],
                                        [Category Name].Category,
                                        [Category Name].id,
                                        [Sub-Category Name].[Sub-Category],
                                        [Sub-Category Name].id, 
                                        Accounts.[Account Name],
                                        Accounts.id,
                                        Transactions.Month, 
                                        Transactions.Amount 
                                        from Transactions join [Category Name] join [Sub-Category Name] join [Accounts]
                                        on Transactions.[Category_id] = [Category Name].id
                                        and Transactions.[Sub_Category_id] = [Sub-Category Name].id
                                        and Transactions.[Account_Type_id] = Accounts.id
                                        where ([Sub_Category_id], 
                                       [Account_Type_id], 
                                       Month) = (?, ?, ?)''',
                                        (self.selected_row_tags[0], 
                                         self.budget_accounts_data[self.selected_column-3][1],
                                         self.current_tab_num))
        self.cell_transactions_from_db: list = self.manage_budget_cur.fetchall()
        self.transaction_list_window.create_transaction_list(self.cell_transactions_from_db)

        #configure transaction list labels to display selected cell info
        self.visual_functions.configure_widget(self.transaction_list_window.transactions_for_info, new_text=self.selected_cell_info_list[0] + ", " + self.selected_cell_info_list[1] + ", " + self.selected_cell_info_list[2])
        self.visual_functions.configure_widget(self.transaction_list_window.transactions_for_info_category, new_text="Category: " + self.selected_cell_info_list[3])
        self.visual_functions.configure_widget(self.transaction_list_window.transactions_for_info_subcategory, new_text="Sub-Category: " + self.selected_cell_info_list[4])

    def user_selects_transaction(self): #called by (de)select of a checkbox
        for i, checkbox in enumerate(self.transaction_list_window.transaction_checkbox_list):
            self.transaction_list_window.checkbox_statuses[i] = self.visual_functions.get_checkbox_status(checkbox)
        if 1 in self.transaction_list_window.checkbox_statuses: #at least one box checked
            self.visual_functions.configure_widget(self.transaction_list_window.transaction_list_edit_button, new_state="normal")
            self.visual_functions.configure_widget(self.transaction_list_window.transaction_list_delete_button, new_state="normal")
        else:
            self.visual_functions.configure_widget(self.transaction_list_window.transaction_list_edit_button, new_state="disabled")
            self.visual_functions.configure_widget(self.transaction_list_window.transaction_list_delete_button, new_state="disabled")

    def edit_transactions(self):
        self.current_transaction_to_edit: int = 0
        for box, transaction in zip(self.transaction_list_window.checkbox_statuses, self.cell_transactions_from_db):
            if box == 1:
                self.current_transaction_to_edit = self.cell_transactions_from_db.index(transaction)
                self.transaction_list_window.draw_transaction_editor_window(add_new_button=False)
                break #found first selected transaction, call editor then end looping (loop continues when editor is closed)

    def delete_transactions_in_list(self):
        for i, box in enumerate(self.transaction_list_window.checkbox_statuses):
            if box == 1:
                transaction_status: str =  self.visual_functions.get_checkbox_attribute(self.transaction_list_window.transaction_checkbox_list[i], 'text')
                if transaction_status.endswith(TrasactionStatuses.new.value):
                    self.visual_functions.configure_widget(self.transaction_list_window.transaction_checkbox_list[i], new_text='${:,.2f}'.format(self.cell_transactions_from_db[i][-1]) + TrasactionStatuses.canceled.value)
                else:
                    self.visual_functions.configure_widget(self.transaction_list_window.transaction_checkbox_list[i], new_text='${:,.2f}'.format(self.cell_transactions_from_db[i][-1]) + TrasactionStatuses.deleted.value)
                self.visual_functions.checkbox_deselect(self.transaction_list_window.transaction_checkbox_list[i])
    
    def confirm_transaction_list(self):
        new_cell_total: float = 0
        transaction_status: str | None = None
        for i, box in enumerate(self.transaction_list_window.transaction_checkbox_list):
            for status in TrasactionStatuses:
                if self.visual_functions.get_checkbox_attribute(box, 'text').endswith(status.value):
                    transaction_status = status.name
                    break
                else:transaction_status = None #indicates no change of transaction
            if False in [self.selected_row_tags[0] == self.cell_transactions_from_db[i][5], 
                         self.selected_row_parent_tags[0] == self.cell_transactions_from_db[i][3], 
                         self.selected_row_grandparent_tags[0] == self.cell_transactions_from_db[i][1], 
                         self.selected_column-2 == self.cell_transactions_from_db[i][7], 
                         self.current_tab_num == self.cell_transactions_from_db[i][8]]:
                cell_changed: bool = True
            else: cell_changed = False
            #DB updates
            if transaction_status == TrasactionStatuses.new.name or transaction_status == TrasactionStatuses.modifiednew.name:
                self.modify_budget_database(0, self.cell_transactions_from_db[i])
            elif transaction_status == TrasactionStatuses.modified.name:
                self.modify_budget_database(1, self.cell_transactions_from_db[i])
            elif transaction_status == TrasactionStatuses.deleted.name:
                self.modify_budget_database(2, self.cell_transactions_from_db[i])
                continue
            elif transaction_status == TrasactionStatuses.canceled.name:
                continue
            #Treeview updates
            if not cell_changed: #transaction_status is None, new, or modified/modifiednew (in current cell)
                new_cell_total += self.cell_transactions_from_db[i][-1]
            elif cell_changed: #transaction_status modified/modified new (moved to other cell)
                new_cell_tabnum: int = self.cell_transactions_from_db[i][8]
                new_cell_subcatid: int = self.cell_transactions_from_db[i][5]
                new_cell_col: int = self.cell_transactions_from_db[i][7]+1
                other_row_item: str = ""
                other_row_data: list = []
                for subcat in self.budget_subcat_list:
                    if self.visual_functions.get_hierarchy_content(self.manage_budget_table.treeview_list[new_cell_tabnum], subcat, 'tags')[0] == new_cell_subcatid:
                        other_row_item: str = subcat
                        other_row_data = self.visual_functions.get_hierarchy_content(self.manage_budget_table.treeview_list[new_cell_tabnum], subcat, 'values')
                        break
                self.update_indicated_cell(self.cell_transactions_from_db[i][-1], True, new_cell_tabnum, other_row_item, other_row_data, new_cell_col)
        self.visual_functions.get_hierarchy_item(self.manage_budget_table.treeview_list[self.current_tab_num], self.selected_row_item, new_values=self.selected_row_data)
        self.update_indicated_cell(new_cell_total)
        self.visual_functions.destroy_widget(self.transaction_list_window)
            
    #TRANSACTION EDITOR
    def set_dropdowns_to_annual_or_month(self, annual: str):
        '''check if user switches from month to annual or inverse.  If switching then set category dropdown string var to 0th entity'''
        if self.tab_title_list[0] == annual and self.current_tab_num != 0: #switching from monthly to annual
            set_dropdown_default = True
        if self.tab_title_list[0] != annual and self.current_tab_num == 0: #switching from annual to monthly
            set_dropdown_default = True
        else:
            set_dropdown_default = False
        self.set_dropdown_categories(self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_incexp), set_dropdown_default)

    def set_dropdown_categories(self, incexp: str, set_default: bool): 
        '''sets the available categories based on selection of income or expenses.  
        \nset_default should be true when changing income/expense or from annual to month or inverse,
        \nit only becomes false if switching between months'''
        self.dropdown_categories_names: list = list(self.budget_structure[incexp].keys())
        self.selected_budget_section: dict = self.budget_structure.get(incexp, dict)
        if self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_category_name) not in self.dropdown_categories_names: #reset category when switching btw income and expenses 
            self.visual_functions.set_string_var(self.transaction_editor_window.dropdown_category_name, self.dropdown_categories_names[0])
        self.visual_functions.configure_dropdown(self.transaction_editor_window.category_dropdown, values=self.dropdown_categories_names)
        selected_category: str = self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_category_name)
        self.set_dropdown_subcategories(selected_category, set_default)

    def set_dropdown_subcategories(self, category: str, set_default: bool): 
        annual = self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_tab_name) == self.tab_title_list[0]
        selected_subcats = []
        for subcat, annual_month in zip(self.selected_budget_section.get(category, list)[0], self.selected_budget_section.get(category, list)[1]):
            if annual and annual_month == 2:
                selected_subcats.append(subcat)
            elif not annual and annual_month == 1:
                selected_subcats.append(subcat)  
        self.visual_functions.configure_dropdown(self.transaction_editor_window.subcategory_dropdown, values=selected_subcats)
        if set_default: 
            if len(selected_subcats) == 0: #not subcats match (likely indicates no annuals in selected category)
                self.visual_functions.set_string_var(self.transaction_editor_window.dropdown_subcat_name, "No Sub-categories Available")    
                self.visual_functions.configure_widget(self.transaction_editor_window.transaction_editor_confirm_button, new_state="disabled")
            else:
                self.visual_functions.set_string_var(self.transaction_editor_window.dropdown_subcat_name, selected_subcats[0])
                self.visual_functions.configure_widget(self.transaction_editor_window.transaction_editor_confirm_button, new_state="normal")

    def close_editor_window(self, add_new: bool, cancel_edit: bool = False):
        if not add_new: #editing
            #resume looping through cell transactions, starting at current selected (which is now de-selected), looking for other selected
            if cancel_edit == True:
                self.visual_functions.checkbox_deselect(self.transaction_list_window.transaction_checkbox_list[self.current_transaction_to_edit])
                self.transaction_list_window.checkbox_statuses[self.current_transaction_to_edit] = 0
                self.visual_functions.configure_widget(self.transaction_list_window.transaction_list_edit_button, new_state='disabled')
                self.visual_functions.configure_widget(self.transaction_list_window.transaction_list_delete_button, new_state='disabled')
            self.visual_functions.destroy_widget(self.transaction_editor_window)
            for box, transaction in zip(self.transaction_list_window.checkbox_statuses[self.current_transaction_to_edit:], self.cell_transactions_from_db[self.current_transaction_to_edit:]):
                if box == 1:
                    self.current_transaction_to_edit = self.cell_transactions_from_db.index(transaction)
                    self.transaction_list_window.draw_transaction_editor_window(add_new)
                    break
        if add_new: #adding new
            self.visual_functions.destroy_widget(self.transaction_editor_window)

    def check_editor_entry_is_number(self):
        try:
            self.transaction_editor_amount: float = round(float(self.visual_functions.extract_str_var(self.transaction_editor_window.entrybox_amount)), 2)
            return True
        except ValueError:
            return False
        
    def confirm_transaction_editor(self, called_by_manager: bool, add_new: bool, event=None):
        '''called by 'confirm button' or a return key event (when focus set to entry box)
        \nchecks if editor was called by manager window (nav panel) or list window,
        \nif manager window: calls add_new_transaction,
        \nif list window addnew button: calls add_new_transaction_to_list
         \nif list window editbutton: calls edit_transaction_in_list (this may just be a delete func, then the add_new_transaction func)'''
        if self.check_editor_entry_is_number() == True:
            if called_by_manager:
                try:
                    new_cell_total: float = float((self.selected_row_data[self.selected_column-1].replace(",", "").strip("$")))
                except ValueError:
                    new_cell_total: float = 0.0
                new_cell_total += self.transaction_editor_amount
                self.update_indicated_cell(new_cell_total)
                new_transaction_data = self.assemble_transaction_data_entry(0)
                self.modify_budget_database(0, new_transaction_data)
            elif not called_by_manager:
                if add_new == True: #add new button used, call add_new_transaction_to_list(), 
                    self.add_new_transaction_to_list()
                if add_new == False: #edit button used, call edit_list_transaction()
                    self.edit_transaction_in_list()
                    #call edit window again
            self.close_editor_window(add_new)
        else:
            return "break" #non-number in entry box, confirm btn does nothing
            
    def update_indicated_cell(self, 
                             new_cell_total: float, 
                             non_selected_cell: bool = False, 
                             new_tab: int = 0, 
                             other_row_item: str = "",
                             other_row_data: list[str] = [], 
                             new_column: int = 0):
        '''this method adds transaction data to the table,
        \ncan be called directly by editor window (passing a single transaction) 
        \nor by list window (passing the sum total of one or more transactions)
        \nif non-selected_cell if True, this indicates that the transaction is moving to another cell,
        \nif this is the case new_tab, other_row_item, other_row_data, and new_colum must be passed as well'''
        if non_selected_cell == False: #currently selected cell is being updated
            #NOTE selected row data can change without a 2nd click event, so need to re-get the row data before and after alterations
            self.selected_row_data: list[str] = self.visual_functions.get_hierarchy_content(self.manage_budget_table.treeview_list[self.current_tab_num], self.selected_row_item, 'values')
            indicated_treeview = self.manage_budget_table.treeview_list[self.current_tab_num]
            indicated_row_item: str = self.selected_row_item
            indicated_row_data: list[str] = self.selected_row_data
            indicated_column: int = self.selected_column-1
        elif non_selected_cell == True:
            indicated_treeview = self.manage_budget_table.treeview_list[new_tab]
            indicated_row_item = other_row_item
            indicated_row_data = other_row_data
            indicated_column = new_column
        try:
            old_cell_value: float = float(indicated_row_data[indicated_column].replace(",", "").strip("$"))
        except ValueError: #cell was a blank string, replace with 0.0
            old_cell_value = 0.0
        new_cell_value: str = '${:,.2f}'.format(round(new_cell_total, 2))
        indicated_row_data[indicated_column] = new_cell_value
        #update selected col cat subtotal
        indicated_row_item_parent = self.visual_functions.get_hierarchy_item_parent(indicated_treeview, indicated_row_item)
        indicated_cell_subtotal_item: str = self.visual_functions.get_hierarchy_item_children(indicated_treeview, indicated_row_item_parent)[-1]
        indicated_cell_cat_subtotal_data: list[str] = self.visual_functions.get_hierarchy_content(indicated_treeview, indicated_cell_subtotal_item, "values")
        old_col_total: float = float(indicated_cell_cat_subtotal_data[indicated_column].replace(",", "").strip("$"))
        new_col_total: float = round(old_col_total + (new_cell_total - old_cell_value), 2)
        indicated_cell_cat_subtotal_data[indicated_column] = '${:,.2f}'.format(new_col_total)
        #if total col exists, make it blank, loop thru row data cols, adding to new total, add it back to row data and update treeview
        if len(indicated_row_data) > 3:             
            new_total_flt: float = 0.0
            new_subtotal_total: float = 0.0
            for i, col in enumerate(indicated_row_data[2:-1]):
                if col == '': #add formated 0 to other cells in row if they are blank
                    indicated_row_data[i+2] = '${:,.2f}'.format(0.00)
                else:
                    new_total_flt += float(col.replace(",", "").strip("$"))
                    new_subtotal_total += float(indicated_cell_cat_subtotal_data[i+2].replace(",", "").strip("$"))
            indicated_row_data[-1] = '${:,.2f}'.format(round(new_total_flt, 2))
            indicated_cell_cat_subtotal_data[-1] = '${:,.2f}'.format(round(new_subtotal_total, 2))        
        self.visual_functions.get_hierarchy_item(indicated_treeview, indicated_row_item, new_values=indicated_row_data)
        self.visual_functions.get_hierarchy_item(indicated_treeview, indicated_cell_subtotal_item, new_values=indicated_cell_cat_subtotal_data)
         #we need to update self.selected row data here if the only cell change is the column
        if non_selected_cell == True and self.selected_row_item == other_row_item and new_tab == self.current_tab_num:
            self.selected_row_data = other_row_data

    def modify_budget_database(self, modification: int, transaction_entry: tuple):
        '''this method modifies the budget sql database, taking a tuple containing the data for the transaction.
        \nthere are 3 options, each using somewhat different parts of transaction_entry:
        \nmodification=0 = adding: -1, 3, 5, 7, 8
        \nmodification=1 = modifying: -1, 3, 5, 7, 8, 0
        \nmodification=2 = deleting: 0'''
        if modification == 0: #add
            self.manage_budget_cur.execute("insert into Transactions (Amount, [Category_id], [Sub_Category_id], [Account_Type_id], Month) Values (?, ?, ?, ?, ?)", 
                                       (transaction_entry[-1], transaction_entry[3], transaction_entry[5], transaction_entry[7], transaction_entry[8]))
        elif modification == 1: #modify
            self.manage_budget_cur.execute("update Transactions set Amount = ?, [Category_id] = ?, [Sub_Category_id] = ?, [Account_Type_id] = ?, Month = ? where id = ?", 
                                        (transaction_entry[-1], transaction_entry[3], transaction_entry[5], transaction_entry[7], transaction_entry[8], transaction_entry[0]))
        elif modification == 2: #delete
            self.manage_budget_cur.execute("delete from Transactions where id = ?", (transaction_entry[0], ))
        self.manage_budget_conn.commit()
    
    def add_new_transaction_to_list(self): 
        '''adds a new transaction to the list window,
        \nassigns 0 as temp transaction id and get [incexp id, cat, cat id, subcat, subcat id, account, account id, month, amount] and add to transactions list '''
        new_transaction_data: tuple = self.assemble_transaction_data_entry(0)
        self.transaction_list_window.add_transaction_to_list(self.transaction_editor_amount)
        self.cell_transactions_from_db.append(new_transaction_data)

    def assemble_transaction_data_entry(self, transaction_id) -> tuple:
        '''this method queries the budget database and references editor window dropdown values and returns a tuple containing:
        \ntransaction id, incexp id,category name, category id, subcategory name, subcategory id, account name, account id, tabnum, transaction editor amount
        \ncan be used to assign id's to new and edited transactions'''
        transaction_incexp: int = 0
        for incexp in self.income_expense_data: #update incexp NOTE will throw exception if not updated sucessfully
                if incexp[0] == self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_incexp):        
                    transaction_incexp = incexp[1]
        cat_name = self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_category_name)
        self.manage_budget_cur.execute('''select [Category Name].id from [Category Name] where ([Category Name].Category, [Category Name].[Income_expense_id]) = (?, ?)''', (cat_name, transaction_incexp))
        cat_id = self.manage_budget_cur.fetchall()[0][0]
        subcat_name = self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_subcat_name)
        self.manage_budget_cur.execute('''select [Sub-Category Name].id  from [Sub-Category Name] where ([Sub-Category Name].[Sub-Category], [Sub-Category Name].[Category_Name_id]) = (?, ?)''', (subcat_name, cat_id))
        subcat_id  = self.manage_budget_cur.fetchall()[0][0]
        acct_name = self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_account_name)
        self.manage_budget_cur.execute('''select Accounts.id  from Accounts where Accounts.[Account Name] = (?)''', (acct_name,))
        acct_id = self.manage_budget_cur.fetchall()[0][0]
        transaction_tab_num: int = self.current_tab_num
        for i, tab in enumerate(self.tab_title_list): #update tab from current if changed in editor window
                if tab == self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_tab_name):
                    transaction_tab_num = i
        return (transaction_id, transaction_incexp, cat_name, cat_id, subcat_name, subcat_id, acct_name, acct_id, transaction_tab_num, self.transaction_editor_amount)

    def edit_transaction_in_list(self): #confirm button in editor clicked (called for each selected transaction)
        '''Check for modifications to currently selected transaction (id'd by self.current_transaction_to_edit)
        \nif modifications found, update the entry in self.cell_transactions_from_db, update checkbox text value, and mark as modified
        \ndeselect checkbox, and update checkbox statuses list (even if no modifications found)'''
        incexp_mod = self.income_expense_data[self.cell_transactions_from_db[self.current_transaction_to_edit][1]-1][0] == self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_incexp)
        category_mod = self.cell_transactions_from_db[self.current_transaction_to_edit][2] == self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_category_name)
        subcategory_mod = self.cell_transactions_from_db[self.current_transaction_to_edit][4] == self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_subcat_name)
        account_mod = self.cell_transactions_from_db[self.current_transaction_to_edit][6] == self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_account_name)
        tab_mod = self.tab_title_list[self.cell_transactions_from_db[self.current_transaction_to_edit][8]] == self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_tab_name)
        amount_mod = self.cell_transactions_from_db[self.current_transaction_to_edit][-1] == round(float(self.visual_functions.extract_str_var(self.transaction_editor_window.entrybox_amount)), 2)

        if False in [incexp_mod, category_mod, subcategory_mod, account_mod, tab_mod, amount_mod]: #modification found                     
            transaction_id: int = self.cell_transactions_from_db[self.current_transaction_to_edit][0] 
            modded_transaction_data: tuple = self.assemble_transaction_data_entry(transaction_id)
            self.cell_transactions_from_db[self.current_transaction_to_edit] = modded_transaction_data
            transaction_status: str = self.visual_functions.get_checkbox_attribute(self.transaction_list_window.transaction_checkbox_list[self.current_transaction_to_edit], 'text')

            if transaction_status.endswith(TrasactionStatuses.new.value):
                self.visual_functions.configure_widget(self.transaction_list_window.transaction_checkbox_list[self.current_transaction_to_edit], new_text='${:,.2f}'.format(self.cell_transactions_from_db[self.current_transaction_to_edit][-1]) + TrasactionStatuses.modifiednew.value)
            else:
                self.visual_functions.configure_widget(self.transaction_list_window.transaction_checkbox_list[self.current_transaction_to_edit], new_text='${:,.2f}'.format(self.cell_transactions_from_db[self.current_transaction_to_edit][-1]) + TrasactionStatuses.modified.value)
        
        self.visual_functions.checkbox_deselect(self.transaction_list_window.transaction_checkbox_list[self.current_transaction_to_edit])
        self.transaction_list_window.checkbox_statuses[self.current_transaction_to_edit] = 0
        
    def set_bindings_to_amount_entry(self, event):
        self.transaction_editor_window.set_returnkey_binding()
        self.focus_set_to_amount_entry: bool = True

    def returnkey_pressed_in_amount_entry(self, event):
        is_num: bool = self.check_editor_entry_is_number()
        if is_num:
            self.visual_functions.invoke_button(self.transaction_editor_window.transaction_editor_confirm_button)
        else:
            pass

    def set_focus_to_entry(self):
        self.visual_functions.set_widget_focus(self.transaction_editor_window.amount_entry)
        self.visual_functions.set_entrybox_cursor(self.transaction_editor_window.amount_entry, 'end')
        self.visual_functions.set_entrybox_selection_range(self.transaction_editor_window.amount_entry, 0, 'end')

    def keep_focus_in_entry(self, event):
        self.visual_functions.set_widget_focus(self.transaction_editor_window.amount_entry)
        self.visual_functions.set_entrybox_cursor(self.transaction_editor_window.amount_entry, 'end')

   