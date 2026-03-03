from __future__ import annotations
from typing import Any, Literal, Tuple, TYPE_CHECKING
from enum import Enum

import os
import sys
import json
import sqlite3
import datetime
if TYPE_CHECKING:
    from Visuals import MainMenu, NavigationPanel, RadioButtonMenu, EditBudgetTemplate, EditBudget, AccountSelection, VisualFunctions, SaveNameWindow, WarningWindow, ManageBudget, TransactionListWindow, TransactionEditorWindow
    from ctk_date_picker import CTkDatePicker

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
                                     transaction_editor_window: "TransactionEditorWindow | None" = None,
                                     date_picker: "CTkDatePicker | None" = None):
        '''Gives logic access to the members of temporary windows/toplevels
        \nLogic.py requires the class to be imported under TYPECHECKING, and a reference to the class instance added as an optional parameter
        \nA call to this method must appear in the __init__ for the given class, passing self for the appropriate argument'''
        if save_window != None:
            self.save_window = save_window
        if transaction_list_window != None:
            self.transaction_list_window = transaction_list_window
        if transaction_editor_window != None:
            self.transaction_editor_window = transaction_editor_window
        if date_picker != None:
            self.date_picker = date_picker
    
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
            self.nav_panel.disable_manager_buttons()
            self.visual_functions.raise_panel(self.main_menu)
            self.visual_functions.configure_widget(self.nav_panel.button_continue, new_text="Continue")
            self.clear_manager_close_conn_reset_yearly_calc_switch()            
        if self.at_system_end == True and self.selected_system_name == SystemNames.create_new_system.name: #at account selection,user can return to main or go to manager
            self.account_selection_confirmed()

    def nav_panel_back_button(self): #NOTE, the page if conds should appear in inverse of the continue button (counting down)  
        if self.current_page == 1: #returning to radiobutton menu #0, reload template/budget list  
            self.selected_system_methods[self.current_page - 1]()
            if self.selected_system_name == SystemNames.manage_budget_system.name: #at manager, reconfig nav buttons, and clear treeview
                self.nav_panel.disable_manager_buttons()
                self.visual_functions.configure_widget(self.nav_panel.button_continue, new_text="Continue")
                self.clear_manager_close_conn_reset_yearly_calc_switch()
                
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
                          Monthly_annual_id integer,
                          Most_recent_entity_id, integer
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
        self.create_new_budget_editor.entry_box_exists = False

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
        self.budget_displayed_in_manager:bool = False #indicator: budget is displayed in table
        #self.editor_window_exists: bool = False #keeps track of editor window, to prevent multiple spawns (used when editing more than one transaction)
        self.tab_title_list = ["Annual", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "Yearly Total"]
        self.proper_cell_selected: bool = False

    def display_budget_management_table(self, selected_budget_name): #this triggers on raise, load budget, configure treeviews based on # of accounts
        self.yearly_total_tab_selected: bool = False #switch indicating that yearly total tab had loaded (if loaded it can be updated when modifications are made to budget)
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
        self.budget_table_headings.append("Surplus/Shortfall")
        self.manage_budget_table.create_management_treeviews()
        for budget_table in self.manage_budget_table.treeview_list:            
            self.visual_functions.configure_hierarchy_options(budget_table, self.budget_table_headings)
            for heading in self.budget_table_headings:
                self.visual_functions.set_hierarchy_heading_text(budget_table, column=heading, text=heading)
                if self.budget_table_headings.index(heading) == 0:
                    self.visual_functions.set_hierarchy_column_options(budget_table, column=heading, stretch=True, width=180)
                else:
                    self.visual_functions.set_hierarchy_column_options(budget_table, column=heading, stretch=True, width=60)  
            self.visual_functions.configure_hierarchy_values(budget_table, "incexpfont", "Calibri", 16, 'bold')
            self.visual_functions.configure_hierarchy_values(budget_table, "catfont", "Calibri", 15, "bold")      
            self.visual_functions.configure_hierarchy_values(budget_table, "subcatfont", "Calibri", 13) 
        if self.manage_budget_table.cell_highlight_exists == True:
            self.visual_functions.destroy_widget(self.manage_budget_table.cell_highlight)
            self.manage_budget_table.cell_highlight_exists = False  
        self.visual_functions.set_active_tab(self.manage_budget_table.manage_budget_tabs, self.tab_title_list[self.month])
        self.fetch_budget_data()        
        self.fetch_transaction_data_from_db()
        self.budget_displayed_in_manager = True
        self.nav_panel.enable_manager_buttons()
        self.store_budget_structure()
        self.set_active_treeview()       

    def fetch_budget_data(self):
        self.manage_budget_cur.execute("select [Income Expense].[Income/Expense], [Income Expense].id from [Income Expense]")
        self.income_expense_data = self.manage_budget_cur.fetchall()
        self.income_expense_str_list: list = [] 
        self.income_expense_treeview_str_list: list = [] #NOTE this is only used when outputing income/expense rows to a treeview in manager window, when retreiving from treeview, either matchi with above list or strip/replace "Total "
        for section in self.income_expense_data:
            self.income_expense_str_list.append(section[0])
            self.income_expense_treeview_str_list.append("Total " + section[0])
        self.manage_budget_cur.execute("select [Category Name].Category, [Category Name].Income_expense_id, [Category Name].id from [Category Name]")
        self.category_data: list = self.manage_budget_cur.fetchall()
        self.manage_budget_cur.execute("pragma table_info([Sub-Category Name]);") #check for subcatname table cols (backwards compatibility)
        subcat_table_cols: list = self.manage_budget_cur.fetchall()
        most_recent_entity_col_found: bool = False
        for col in subcat_table_cols:
            if col[1] == 'Most_recent_entity_id': 
                most_recent_entity_col_found =True
                break
        if not most_recent_entity_col_found:
            self.manage_budget_cur.execute("alter table [Sub-Category Name] add Most_recent_entity_id integer;")    
            self.manage_budget_conn.commit()            
        self.manage_budget_cur.execute('''select [Sub-Category Name].[Sub-Category], 
                                       [Budget Amounts].Amount, 
                                       [Sub-Category Name].id,
                                       [Budget Amounts].id,
                                       [Budget Amounts].Sub_Category_id,
                                       [Sub-Category Name].Monthly_annual_id,
                                       [Budget Amounts].Category_id,
                                       [Sub-Category Name].[Most_recent_entity_id] 
                                       from [Sub-Category Name] join [Budget Amounts] on [Budget Amounts].Sub_Category_id = [Sub-Category Name].id''')
        self.subcategory_and_amount_data = self.manage_budget_cur.fetchall()
        self.subcat_budgetamounts: list = []
        for entry in self.subcategory_and_amount_data:
            self.subcat_budgetamounts.append([entry[0], entry[1], entry[2], entry[5], entry[6]]) #[subcat label, amount, sub-cat-id, monthly-annual, category-id]
        self.manage_budget_cur.execute("select Entity.Description, Entity.id from Entity")
        self.entity_data: list = self.manage_budget_cur.fetchall()      
        if ('None', 1) not in self.entity_data: #None not in entity data, add it
            self.manage_budget_cur.execute('''insert into Entity (Description) Values (?)''', ("None",))
            self.manage_budget_conn.commit()
            self.manage_budget_cur.execute("select Entity.Description, Entity.id from Entity")
            self.entity_data = self.manage_budget_cur.fetchall()        
        for index, table in enumerate(self.manage_budget_table.treeview_list):
            self.display_budget_data(table, index, self.income_expense_treeview_str_list[0], self.income_expense_data[0][1]) #income 
            self.display_budget_data(table, index, self.income_expense_treeview_str_list[1], self.income_expense_data[1][1]) #expenses

    def display_budget_data(self, table, table_index: int, budget_section_name: str, budget_section_id: str):
            '''Displays the budget data for each major section individually
            \ntable = the treeview reference
            \ntable_index = the reference treeviews index position used to differentiate annual, monthly, and yearly total tabs
            \nbudget_section_name = a string that fills the section heading in each table (income/expenses)
            \nbudget_section_id = a string ID associated with each section in database (str is manadatory for insert method)'''
            budget_section  = self.visual_functions.insert_into_hierarchy(table, "", 'end', text_to_insert='', row_values=[budget_section_name], display_open=True, tags=(budget_section_id, "incexpfont", "incexpfontred", HierarchyLevel.incexp.value))
            if len(self.budget_section_list) < 2:
                self.budget_section_list.append(budget_section)
            if table_index == 0: #annual tab
                self.display_budget_category_data(table, budget_section, budget_section_id, 'annual')
            elif table_index < 13: #monthly
                self.display_budget_category_data(table, budget_section, budget_section_id, 'monthly')
            elif table_index == 13: #yearly total
                self.display_budget_category_data(table, budget_section, budget_section_id, 'yearly total')
               
    def display_budget_category_data(self, table, budget_section: str, inc_exp_id: str, tab_type: Literal['annual'] | Literal['monthly'] | Literal['yearly total']):
        '''This inserts the budget template (category labels, sub-category labels and their budget amounts) to the manager tables'''
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
                        if tab_type == "yearly total" and subcat[3] == 1: #initial table creation, defaults to current month calculations
                            subcat_display[1] = '${:,.2f}'.format(float(subcat[1].replace(",", "").strip("$")) * self.month)                        
                        elif tab_type == "annual" and subcat[3] == 1 or tab_type == 'monthly' and subcat[3] == 2: #annual tab+monthly subcat or monthly tab+annual subcat 
                            subcat_display = [subcat_display[i] if i <= 1 else "----------" for i in range(len(subcat_display))] 
                        current_subcat_values = self.visual_functions.insert_into_hierarchy(table, budget_category, 'end', row_values=(subcat_display), display_open=True, tags=(subcat[2], "subcatfont", HierarchyLevel.subcategory.value))     
                        if tab_type == "annual": 
                            self.budget_subcat_list.append(current_subcat_values)
                category_total_rowdata: list = ["Total"]                
                self.visual_functions.insert_into_hierarchy(table, budget_category, 'end', row_values=category_total_rowdata, display_open=True, tags=("category total",))
                category_total_rowitem: str = self.visual_functions.get_hierarchy_item_children(table, budget_category)[-1]
                self.budget_subcat_list.append(category_total_rowitem)            
    
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
            #run per-tab calculations for budget summary data
            for section in self.budget_section_list[:2]: #first two section ID's for income/expenses
                self.calculate_section_totals(table, section) 
                self.calculate_surplus_shortfall_column(table, section)    
                for category in self.visual_functions.get_hierarchy_item_children(table, section):
                    for subcat in self.visual_functions.get_hierarchy_item_children(table, category):
                        self.calculate_surplus_shortfall_column(table, subcat)
    
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
                    
    def calculate_row_totals(self, subcat_data: list[str]):
        '''loop through each acct/col, destring and add to total, then restring and add to subcat data'''
        row_transaction_total = 0
        for col in range(2, len(self.budget_accounts_data) + 2): 
            row_transaction_total += float(subcat_data[col].replace(",", "").strip("$"))
        subcat_data[-2] = '${:,.2f}'.format(row_transaction_total)

    def calculate_section_totals(self, table, section: str):       
        section_categories: tuple[str, ...] = self.visual_functions.get_hierarchy_item_children(table, section) 
        section_totals_list: list[float] = [0 for i in range(len(self.visual_functions.get_hierarchy_content(table, section_categories[0], "values"))-1)]
        for cat in section_categories:
            cat_col_totals: list[float] = self.calculate_category_subtotals(table, cat) 
            for i, col in enumerate(cat_col_totals):
                section_totals_list[i] += col
        section_row_values = self.visual_functions.get_hierarchy_content(table, section, 'values')
        for i, total in enumerate(section_totals_list):
            if len(section_row_values) > i+1: #matching col exists, replace
                section_row_values[i+1] = '${:,.2f}'.format(total)
            else: ##matching does not exist yet, append
                section_row_values.append('${:,.2f}'.format(total))
        self.visual_functions.get_hierarchy_item(table, section, new_values=section_row_values, display_open=True)

    def calculate_category_subtotals(self, table, cat: str)-> list[float]:        
        cat_values = self.visual_functions.get_hierarchy_content(table, cat, "values")
        category_totals_list: list[float] = [0 for i in range(len(cat_values)-1)]
        subcat_items = self.visual_functions.get_hierarchy_item_children(table, cat)        
        for subcat in subcat_items[:-1]: #excludes total row
            subcat_values: list[str] = self.visual_functions.get_hierarchy_content(table, subcat, "values")            
            for i, col in enumerate(category_totals_list):
                if "----------" in subcat_values or subcat_values[i+1] == "":
                    pass #catches blank cells, and monthly in annual tab, or annual in monthly tab
                else:
                    category_totals_list[i] += float(subcat_values[i+1].replace(",", "").strip("$"))              
        total_row_values = self.visual_functions.get_hierarchy_content(table, subcat_items[-1], "values")
        for i, total in enumerate(category_totals_list):
            if len(total_row_values) > i+1: #matching col exists, replace
                total_row_values[i+1] = '${:,.2f}'.format(total)
            else: #matching col does not exist yet, append  
                total_row_values.append('${:,.2f}'.format(total))        
        self.visual_functions.get_hierarchy_item(table, subcat_items[-1], new_values=total_row_values)
        return category_totals_list
    
    def calculate_surplus_shortfall_column(self, table, row_item: str):   
        row_item_data: list[str] = self.visual_functions.get_hierarchy_content(table, row_item, "values")
        #if subcat, determine if income set section ID (returns empty if not subcat)
        row_item_section: str = self.visual_functions.get_hierarchy_item_parent(table, self.visual_functions.get_hierarchy_item_parent(table, row_item))
        if row_item_data[1] == "----------" or row_item_data[-2] == "----------":
            pass #dashed out row, do nothing
        else:
            try:
                budgeted_amount: float = float(row_item_data[1].replace(",", "").strip("$"))
                actual_amount: float = float(row_item_data[-2].replace(",", "").strip("$"))
            except ValueError:
                budgeted_amount = 0.0
                actual_amount = 0.0
            if row_item == self.budget_section_list[0] or row_item_section == self.budget_section_list[0]: #income 
                ss_value = actual_amount - budgeted_amount
            else: #expenses
                ss_value = budgeted_amount - actual_amount
            row_item_data[-1] = '${:,.2f}'.format(ss_value)            
            self.visual_functions.get_hierarchy_item(table, row_item, new_values=row_item_data, display_open=True)

    def calculate_or_update_surplus_shortfall_summary(self, indicated_treeview):
        '''calculates the overall budgeted and actual surplus/shortfall values on selection of tab
        \ncalled by set_active_treeview which itself is called after all other budget calculations'''
        income_row_data: list[str] = self.visual_functions.get_hierarchy_content(indicated_treeview, self.budget_section_list[0], "values")
        expenses_row_data: list[str] = self.visual_functions.get_hierarchy_content(indicated_treeview, self.budget_section_list[1], "values")
        try:
            budgeted_income: float = float(income_row_data[1].replace(",", "").strip("$"))
            actual_income: float = float(income_row_data[-2].replace(",", "").strip("$"))
            budgeted_expenses: float = float(expenses_row_data[1].replace(",", "").strip("$"))
            actual_expenses: float = float(expenses_row_data[-2].replace(",", "").strip("$"))
        except ValueError as e:
            print(f"Error: {e}")
            budgeted_income = 0.0
            actual_income = 0.0
            budgeted_expenses = 0.0
            actual_expenses = 0.0
        budgeted_surplus_shortfall: str = '${:,.2f}'.format(budgeted_income - budgeted_expenses)
        actual_surplus_shortfall: str = '${:,.2f}'.format(actual_income - actual_expenses)
        if budgeted_income - budgeted_expenses < -20: #budgeted shortfall more than $20
            self.visual_functions.configure_widget(self.manage_budget_table.budgeted_surplus_shortfall_amount, new_text=budgeted_surplus_shortfall, new_text_color="#CC0000")
        elif budgeted_income - budgeted_expenses < 0 and budgeted_income - budgeted_expenses >= -20: #budgeted shortfall less than or equal to $20
            self.visual_functions.configure_widget(self.manage_budget_table.budgeted_surplus_shortfall_amount, new_text=budgeted_surplus_shortfall, new_text_color="#EBA000")
        else: #budgeted surplus
            self.visual_functions.configure_widget(self.manage_budget_table.budgeted_surplus_shortfall_amount, new_text=budgeted_surplus_shortfall, new_text_color="#00CC00")
        if actual_income - actual_expenses < -20: #actual shortfall more than $20
            self.visual_functions.configure_widget(self.manage_budget_table.actual_surplus_shortfall_amount, new_text=actual_surplus_shortfall, new_text_color="#CC0000")
        elif actual_income - actual_expenses < 0 and actual_income - actual_expenses >= -20: #actual shortfall less than or equal to $20
            self.visual_functions.configure_widget(self.manage_budget_table.actual_surplus_shortfall_amount, new_text=actual_surplus_shortfall, new_text_color="#EBA000")
        else: #actual surplus
            self.visual_functions.configure_widget(self.manage_budget_table.actual_surplus_shortfall_amount, new_text=actual_surplus_shortfall, new_text_color="#00CC00")
            
    def calculate_and_display_yearly_totals(self, yearly_total_treeview, section: str, mode: int = 0):
        '''called by event:selection of yearly tab, so totals are calculated only when the tab is selected for the first time
        \nsubsequent selections of the tab do not re-calculate, instead modifications are made using self.update_indicated_cell()'''                    
        month = self.month
        if mode == 1: #year mode
            month = 12        
        for category in self.visual_functions.get_hierarchy_item_children(yearly_total_treeview, section):                
            for column, heading in enumerate(self.budget_table_headings[2:-1]): #exclude label col, and surplus/shortfall col
                for subcat in self.visual_functions.get_hierarchy_item_children(yearly_total_treeview, category)[:-1]: #exclude total row (handled by calculate_section_totals)
                    current_yearly_total_cell: float = 0.0
                    current_yearly_total_row_data: list = self.visual_functions.get_hierarchy_content(yearly_total_treeview, subcat, 'values')
                    for tab in self.manage_budget_table.treeview_list[:month + 1]:
                        current_cell: str = self.visual_functions.get_hierarchy_content(tab, subcat, 'values')[column+2]
                        if current_cell == "" or current_cell == "----------": 
                            pass #cell is blank or dashed out, skip NOTE: unlike calculate_column_subtotals we want both annual and monthly budget amounts
                        else:
                            current_cell_flt: float = float(current_cell.replace(",", "").strip("$"))
                            current_yearly_total_cell += current_cell_flt
                    current_yearly_total_row_data[column+2] = '${:,.2f}'.format(current_yearly_total_cell)
                    self.visual_functions.get_hierarchy_item(yearly_total_treeview, subcat, new_values=current_yearly_total_row_data)            
        self.calculate_section_totals(yearly_total_treeview, section)  
        self.calculate_surplus_shortfall_column(yearly_total_treeview, section)    
        for category in self.visual_functions.get_hierarchy_item_children(yearly_total_treeview, section):
            for subcat in self.visual_functions.get_hierarchy_item_children(yearly_total_treeview, category):
                self.calculate_surplus_shortfall_column(yearly_total_treeview, subcat) 

    def update_yearly_total_budget_amounts(self, yearly_total_treeview, mode: int):  
        '''This method updates the budgeted amount in the yearly total tab, when switching btw current month and whole year modes'''      
        yearly_total_subcat_list: list = []
        for section in self.budget_section_list:
            for category in self.visual_functions.get_hierarchy_item_children(yearly_total_treeview, section):
                for subcat in self.visual_functions.get_hierarchy_item_children(yearly_total_treeview, category)[:-1]:
                    yearly_total_subcat_list.append(subcat)
        for i, subcat_item in enumerate(yearly_total_subcat_list):
            subcat_data: list = self.visual_functions.get_hierarchy_content(yearly_total_treeview, subcat_item, 'values')
            subcat_budget_amt: str = self.subcat_budgetamounts[i][1]
            subcat_annual_monthly: int = self.subcat_budgetamounts[i][3]
            if subcat_annual_monthly == 2: #budget amt is annual (amount not multiplied)
                subcat_data[1] = subcat_budget_amt
            elif subcat_annual_monthly == 1 and mode == 0: #month mode
                subcat_data[1] = '${:,.2f}'.format(float(subcat_budget_amt.replace(",", "").strip("$")) * self.month)
            elif subcat_annual_monthly == 1 and mode == 1: #year mode
                subcat_data[1] = '${:,.2f}'.format(float(subcat_budget_amt.replace(",", "").strip("$")) * 12)
            self.visual_functions.get_hierarchy_item(yearly_total_treeview, subcat_item, new_values=subcat_data)
     
    def switch_yearly_total_calculations(self, mode):
        '''called by yearly_calculation_switch in ManageBudget class, changes calculation of yearly total data
        \nbetween two modes, including upto current month, vs whole year (mode)'''
        self.update_yearly_total_budget_amounts(self.manage_budget_table.treeview_list[13], mode)        
        self.calculate_and_display_yearly_totals(self.manage_budget_table.treeview_list[13], self.budget_section_list[0], mode)
        self.calculate_and_display_yearly_totals(self.manage_budget_table.treeview_list[13], self.budget_section_list[1], mode)
        self.calculate_or_update_surplus_shortfall_summary(self.manage_budget_table.treeview_list[13])  
        if mode == 0: #month mode
            self.visual_functions.configure_widget(self.manage_budget_table.yearly_calculation_switch, new_text="to Current Month")                               
        if mode == 1: #year mode
            self.visual_functions.configure_widget(self.manage_budget_table.yearly_calculation_switch, new_text="for Whole Year")              
            
    def store_budget_structure(self):
        '''stores the structure of the budgets strings, including income/expense, categories, subcategories and annual/monthly,
        \nthis is used in the editor window to set dropdown values based on their parent in this structure'''
        self.budget_structure: dict = {}
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
        if self.manage_budget_table.cell_highlight_exists == True:
            self.visual_functions.destroy_widget(self.manage_budget_table.cell_highlight)
            self.manage_budget_table.cell_highlight_exists = False
        self.current_tab_num: int = self.visual_functions.get_tab_index(self.manage_budget_table.manage_budget_tabs, 
                                                                   self.visual_functions.get_active_tab(self.manage_budget_table.manage_budget_tabs))        
        self.manage_budget_table.set_bindings(self.current_tab_num) 
        if self.budget_displayed_in_manager == True and self.current_tab_num != 13: #bind cell click functions, (reset manager buttons to disabled)
            self.set_budget_button_status(False) #set buttons to disabled when switching tabs  
            self.manage_budget_table.set_yearly_total_switch_visible(False)                    
            self.visual_functions.configure_widget(self.nav_panel.edit_transactions_button, new_text="Edit Transactions")
        elif self.budget_displayed_in_manager == True and self.current_tab_num == 13: #do not apply bindings to yearly total tab (prevents editing of this treeview)
            #disable manager window buttons (and rename edit button)
            self.set_budget_button_status(False)
            self.manage_budget_table.set_yearly_total_switch_visible(True)
            self.visual_functions.configure_widget(self.nav_panel.edit_transactions_button, new_text="Transactions List")
            if self.yearly_total_tab_selected == False:
                self.calculate_and_display_yearly_totals(self.manage_budget_table.treeview_list[13], self.budget_section_list[0]) #income
                self.calculate_and_display_yearly_totals(self.manage_budget_table.treeview_list[13], self.budget_section_list[1]) #expenses
                self.yearly_total_tab_selected = True
        self.calculate_or_update_surplus_shortfall_summary(self.manage_budget_table.treeview_list[self.current_tab_num])
    
    #events
    def budget_manager_single_click(self, event, treeview):
        '''Stores data on the cell selected by single click
        \nNOTE the word "Total" is stripped from selected_row_grandparent_data because it doesn't belong in the transaction editor/list windows'''
        #ID selected row & col (converted from treeview number to 0 indexed version (the -1))
        self.selected_column = int(self.visual_functions.id_hierarchy_column(treeview, event.x).strip("#"))-1
        self.selected_row_item = self.visual_functions.id_hierarchy_row(treeview, event.y)
        if self.selected_row_item == "": #non-row item selected, do nothing
            return "break"
        #these data are needed for cell based functionality (adding,deleting,editing transactions)
        self.selected_row_data: list[str] = self.visual_functions.get_hierarchy_content(treeview, self.selected_row_item, 'values') #store selected row data
        self.selected_row_tags: list[str] = self.visual_functions.get_hierarchy_content(treeview, self.selected_row_item, 'tags')
        self.selected_row_parent: str = self.visual_functions.get_hierarchy_item_parent(treeview, self.selected_row_item) 
        if self.selected_row_parent == "": #selected row, has no parent
            return 'break'
        self.selected_row_parent_data: list[str] = self.visual_functions.get_hierarchy_content(treeview, self.selected_row_parent, 'values') #store category data for list and editor windows
        self.selected_row_grandparent: str = self.visual_functions.get_hierarchy_item_parent(treeview, self.selected_row_parent) 
        if self.selected_row_grandparent == "": #selected row, has no grandparent
            return 'break'
        self.selected_row_parent_tags: list[str] = self.visual_functions.get_hierarchy_content(treeview, self.selected_row_parent, 'tags')
        self.selected_row_grandparent_data: list[str] = self.visual_functions.get_hierarchy_content(treeview, self.selected_row_grandparent, 'values') #store income/expense data for list and editor windows
        self.selected_row_grandparent_data[0] = self.selected_row_grandparent_data[0].replace("Total ", "") 
        self.selected_row_grandparent_tags: list[str] = self.visual_functions.get_hierarchy_content(treeview, self.selected_row_grandparent, 'tags')        
        if self.manage_budget_table.cell_highlight_exists == True:
            self.visual_functions.destroy_widget(self.manage_budget_table.cell_highlight)
            self.manage_budget_table.cell_highlight_exists = False 
        self.validate_selected_cell()
        self.manage_budget_table.draw_cell_highlight(treeview, self.proper_cell_selected)
        self.set_budget_button_status(self.proper_cell_selected)

    def validate_selected_cell(self): 
        '''these 3 conditions together indicate a cell was selected that user can add data to, sets selected cell bool as instance var
        \nopen_subcat: selected row is a sub-category AND it is not dashed out (indicating annual/monthly)
        \ntransaction_column: seletected column is not the row label, Nor the budgeted amount col
        \nnon-total_col: captures 2 scenarios 1-budget has one account, and user did not select the shortfall/surplus column (indicated by -1)
        \n2-budget has more than one account, and user did not select the shortfall/surplus column or the total column (indicated by -2)'''
        open_subcat: bool =  self.selected_row_tags[-1] == HierarchyLevel.subcategory.value and self.selected_row_data[self.selected_column] != "----------" 
        non_label_budget_column: bool =  self.selected_column > 1
        non_total_or_ss_col: bool = (len(self.selected_row_data) == 4 and self.selected_column <len(self.selected_row_data)-1) or (len(self.selected_row_data) > 4 and self.selected_column < len(self.selected_row_data)-2)
        self.proper_cell_selected: bool = open_subcat and non_label_budget_column and non_total_or_ss_col

    def set_selected_cell_location(self, treeview) -> Tuple[int, int, int, int]:            
        cell_location = self.visual_functions.draw_hierarchy_bbox(treeview, self.selected_row_item, self.selected_column)
        cell_location = (
                        int(float(cell_location[0]) / self.scaling_factor),
                        int(float(cell_location[1]) / self.scaling_factor),
                        int(float(cell_location[2]) / self.scaling_factor),
                        int(float(cell_location[3]) / self.scaling_factor),
                        )
        return cell_location[0], cell_location[1], cell_location[2], cell_location[3]            
        
    def set_budget_button_status(self, proper_cell: bool):
        if proper_cell: #proper cell selected, enable management buttons in nav panel
            if self.current_tab_num != 13: #only activate edit button if tab is not yearly total
                self.visual_functions.configure_widget(self.nav_panel.add_new_transaction_button, new_state='normal')            
            self.visual_functions.configure_widget(self.nav_panel.edit_transactions_button, new_state='normal')
        else: 
            self.visual_functions.configure_widget(self.nav_panel.add_new_transaction_button, new_state='disabled')
            self.visual_functions.configure_widget(self.nav_panel.edit_transactions_button, new_state='disabled')

    def invoke_manage_budget_buttons(self, event): #dbl click event
        if self.selected_row_item == "":
            return "break"
        if self.proper_cell_selected:
            if self.selected_row_data[self.selected_column] == "" or self.selected_row_data[self.selected_column] == "$0.00": #empty/0 cell dbl clicked, raise transaction editor
                self.visual_functions.invoke_button(self.nav_panel.add_new_transaction_button)
            elif self.selected_row_data[self.selected_column] != "" or self.selected_row_data[self.selected_column] != "$0.00": #non-empty cell cbl clicked, raise transaction list
                self.visual_functions.invoke_button(self.nav_panel.edit_transactions_button)

    def clear_manager_close_conn_reset_yearly_calc_switch(self):
        self.manage_budget_table.destroy_management_treeviews()
        self.budget_displayed_in_manager = False
        #NOTE: could reset tab selection here if desired (could also do it on load of budget: display_budget_management_table)
        self.manage_budget_cur.close()
        self.manage_budget_conn.close()
        self.visual_functions.switch_deselect(self.manage_budget_table.yearly_calculation_switch)

    #TRANSACTION LIST WINDOW
    def get_selected_cell_info(self, add_new_from_navpanel): 
        '''add_new_from_navpanel = 1 means 'add transaction' button was pressed from manager window 
        \nadd_new_from_navpanel = 0 means 'add new' button was pressed in the list window
        In both cases, info about the selected cell is needed, but the sql query is made only if the list window is displayed (add_new_from_navpanel = 0)'''
        #store cell info text and ID [month, account, income/expense, category, subcategory]
        self.selected_cell_info_list = [self.tab_title_list[self.current_tab_num], 
                                        self.budget_accounts_data[self.selected_column-2][0],
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
        if self.current_tab_num == 13: #if yearly total tab, load ALL transactions
            self.manage_budget_cur.execute('''select Transactions.id, 
                                        [Category Name].[Income_expense_id],
                                        [Category Name].Category,
                                        [Category Name].id,
                                        [Sub-Category Name].[Sub-Category],
                                        [Sub-Category Name].id, 
                                        Accounts.[Account Name],
                                        Accounts.id,
                                        Transactions.Month,
                                        Transactions.Day, 
                                        Entity.Description,
                                        Transactions.[Entity_id],                                        
                                        Transactions.Amount 
                                        from Transactions 
                                       join [Category Name] on Transactions.[Category_id] = [Category Name].id
                                       join [Sub-Category Name] on Transactions.[Sub_Category_id] = [Sub-Category Name].id
                                       join [Accounts] on Transactions.[Account_Type_id] = Accounts.id
                                       left join [Entity] on Transactions.[Entity_id] = Entity.id
                                       where ([Sub_Category_id], 
                                              [Account_Type_id]) = (?, ?)''',
                                        (self.selected_row_tags[0], 
                                         self.budget_accounts_data[self.selected_column-2][1]))
        else: #load transactions doe corresponding month
            self.manage_budget_cur.execute('''select Transactions.id, 
                                            [Category Name].[Income_expense_id],
                                            [Category Name].Category,
                                            [Category Name].id,
                                            [Sub-Category Name].[Sub-Category],
                                            [Sub-Category Name].id, 
                                            Accounts.[Account Name],
                                            Accounts.id,
                                            Transactions.Month,
                                            Transactions.Day, 
                                            Entity.Description,
                                            Transactions.[Entity_id],                                        
                                            Transactions.Amount 
                                            from Transactions 
                                        join [Category Name] on Transactions.[Category_id] = [Category Name].id
                                        join [Sub-Category Name] on Transactions.[Sub_Category_id] = [Sub-Category Name].id
                                        join [Accounts] on Transactions.[Account_Type_id] = Accounts.id
                                        left join [Entity] on Transactions.[Entity_id] = Entity.id
                                        where ([Sub_Category_id], 
                                                [Account_Type_id], 
                                                Month) = (?, ?, ?)''',
                                            (self.selected_row_tags[0], 
                                            self.budget_accounts_data[self.selected_column-2][1],
                                            self.current_tab_num))
        self.cell_transactions_from_db: list = self.manage_budget_cur.fetchall()
        self.transaction_list_window.create_transaction_list(self.cell_transactions_from_db)
        if self.current_tab_num == 13: 
            self.transaction_list_window.disable_list_window_widgets()

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
        if self.current_tab_num == 13: #list in yearly total tab, only for viewing, no updates neeeded
            self.visual_functions.destroy_widget(self.transaction_list_window)
            return 'break'
        new_cell_total: float = 0
        transaction_status: str | None = None
        for i, box in enumerate(self.transaction_list_window.transaction_checkbox_list):
            for status in TrasactionStatuses:
                if self.visual_functions.get_checkbox_attribute(box, 'text').endswith(status.value):
                    transaction_status = status.name
                    break
                else:transaction_status = None #indicates no change of transaction
            if False in [self.selected_row_tags[0] == self.cell_transactions_from_db[i][5], #check for change of cell
                         self.selected_row_parent_tags[0] == self.cell_transactions_from_db[i][3], 
                         self.selected_row_grandparent_tags[0] == self.cell_transactions_from_db[i][1], 
                         self.selected_column-1 == self.cell_transactions_from_db[i][7], #NOTE index adjustment needed to match selected col (0 indexed, with 0,1 reserved) to DB account ID# with initial value = 1
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
            if not cell_changed: #transaction_status is None, new, or modified/modifiednew (in current cell, add all transactions from list that stay in selectec cell, then call update_indicated_cell with that sum)
                new_cell_total += self.cell_transactions_from_db[i][-1]
            elif cell_changed: #transaction_status modified/modified new (moved to other cell-for each moved transaction id destination cell's value, add moved transaction, then call update_indicated_cell new cell total)   
                new_other_cell_total: float = 0.0
                new_cell_transaction_value: float = self.cell_transactions_from_db[i][-1]             
                new_cell_tabnum: int = self.cell_transactions_from_db[i][8]
                new_cell_subcatid: int = self.cell_transactions_from_db[i][5]
                new_cell_col: int = self.cell_transactions_from_db[i][7]+1 #NOTE the inverse of the index adjustment above
                other_row_item: str = ""
                other_row_data: list[str] = []
                for subcat in self.budget_subcat_list:
                    if self.visual_functions.get_hierarchy_content(self.manage_budget_table.treeview_list[new_cell_tabnum], subcat, 'tags')[0] == new_cell_subcatid:
                        other_row_item: str = subcat
                        other_row_data:list[str] = self.visual_functions.get_hierarchy_content(self.manage_budget_table.treeview_list[new_cell_tabnum], other_row_item, 'values')
                        try:
                            new_other_cell_total += float(other_row_data[new_cell_col].replace(",", "").strip("$")) + new_cell_transaction_value
                        except ValueError: #dest cell was blank
                            new_other_cell_total += new_cell_transaction_value
                        break
                self.update_indicated_cell(new_other_cell_total, cell_changed, new_cell_tabnum, other_row_item, other_row_data, new_cell_col)
        #after updating non-selected cell(s), this method continues to loop skipping those with changed cell
        self.visual_functions.get_hierarchy_item(self.manage_budget_table.treeview_list[self.current_tab_num], self.selected_row_item, new_values=self.selected_row_data)        
        self.update_indicated_cell(new_cell_total, False, self.current_tab_num, self.selected_row_item, self.selected_row_data, self.selected_column)
        self.visual_functions.destroy_widget(self.transaction_list_window)
    
    #TRANSACTION EDITOR
    def set_dropdowns_to_annual_or_month(self, annual: str, add_new: bool):
        '''annual is the string value selected from the dropdown,
        \ncheck if user switches from month to annual or inverse.  If switching then set category dropdown string var to 0th entity
        \n'''
        if self.tab_title_list[0] == annual and self.current_tab_num != 0: #switching from monthly to annual, datepicker set to 0's
            set_dropdown_default = True
            month_selected = False
            self.date_picker.set_month_and_day(0, 0)
            self.visual_functions.configure_widget(self.date_picker.calendar_button, new_state="disabled")
        elif self.tab_title_list[0] != annual and self.current_tab_num == 0: #switching from annual to monthly
            set_dropdown_default = True
            month_selected: bool = True
        else:
            set_dropdown_default = False #switched from month to month
            month_selected = True
        #assign matching index based on dropdown month/annual selected
        if month_selected:
            self.visual_functions.configure_widget(self.date_picker.calendar_button, new_state="normal")
            for i, tab_name in enumerate(self.tab_title_list): 
                if tab_name == annual and i == self.month: #selected dropdown matches selected tab AND month is this month
                    self.date_picker.set_month_and_day(i, self.day) #use today                
                    break
                elif tab_name == annual and i != self.month: #selected tab matches but month is not this month
                    self.date_picker.set_month_and_day(i, 1) #Do NOT use today                
                    break
        self.set_dropdown_categories(self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_incexp), set_dropdown_default, add_new)

    def set_dropdown_categories(self, incexp: str, set_default: bool, add_new: bool): 
        '''sets the available categories based on selection of income or expenses.  
        \nset_default should be true when changing income/expense or from annual to month or inverse,
        \nit only becomes false if switching between months'''
        self.dropdown_categories_names: list = list(self.budget_structure[incexp].keys())
        self.selected_budget_section: dict = self.budget_structure.get(incexp, dict)
        if self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_category_name) not in self.dropdown_categories_names: #reset category when switching btw income and expenses 
            self.visual_functions.set_string_var(self.transaction_editor_window.dropdown_category_name, self.dropdown_categories_names[0])
        self.visual_functions.configure_dropdown(self.transaction_editor_window.category_dropdown, values=self.dropdown_categories_names)
        selected_category: str = self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_category_name)
        self.set_dropdown_subcategories(selected_category, set_default, add_new)

    def set_dropdown_subcategories(self, category: str, set_default: bool, add_new: bool): 
        annual = self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_tab_name) == self.tab_title_list[0]
        selected_subcats = []
        for subcat, annual_month in zip(self.selected_budget_section.get(category, list)[0], self.selected_budget_section.get(category, list)[1]):
            if annual and annual_month == 2:
                selected_subcats.append(subcat)
            elif not annual and annual_month == 1:
                selected_subcats.append(subcat)  
        self.visual_functions.configure_dropdown(self.transaction_editor_window.subcategory_dropdown, values=selected_subcats)
        if set_default: 
            if len(selected_subcats) == 0: #no subcats match (likely indicates no annuals in selected category)
                self.visual_functions.set_string_var(self.transaction_editor_window.dropdown_subcat_name, "No Sub-categories Available")    
                self.visual_functions.configure_widget(self.transaction_editor_window.transaction_editor_confirm_button, new_state="disabled")
            else:
                self.visual_functions.set_string_var(self.transaction_editor_window.dropdown_subcat_name, selected_subcats[0])
                self.visual_functions.configure_widget(self.transaction_editor_window.transaction_editor_confirm_button, new_state="normal")
        self.set_dropdown_entities(add_new)

    def set_dropdown_entities(self, add_new: bool):                  
        self.entity_dropdown_list: list[str] = []
        for entity in self.entity_data:
            self.entity_dropdown_list.append(entity[0])
        self.visual_functions.configure_dropdown(self.transaction_editor_window.entity_dropdown, values=self.entity_dropdown_list)
        #set default dropdown value to None or using current transaction Data (if available)
        if add_new: #set string var and dropdown to None or most recent entity
            most_recent_entity_set: bool = self.set_default_entity_as_most_recent()
            if most_recent_entity_set == False: #failed to find most recent entity
                self.visual_functions.set_string_var(self.transaction_editor_window.dropdown_entity_name, new_value=self.entity_dropdown_list[0])
        elif not add_new and self.cell_transactions_from_db[self.current_transaction_to_edit][10] == None: #None Type(Null in DB) assign the string "None", or most recent entity
            most_recent_entity_set: bool = self.set_default_entity_as_most_recent()
            if most_recent_entity_set == False: #failed to find most recent entity
                self.visual_functions.set_string_var(self.transaction_editor_window.dropdown_entity_name, new_value=self.entity_dropdown_list[0])
        elif not add_new and self.cell_transactions_from_db[self.current_transaction_to_edit][10] != None: #entity was not None Type(Null), use transaction data (str)
            self.visual_functions.set_string_var(self.transaction_editor_window.dropdown_entity_name, new_value=self.cell_transactions_from_db[self.current_transaction_to_edit][10])
        #user cannot delete 'None' from entity data        
        self.set_entity_delete_btn_status()

    def set_default_entity_as_most_recent(self) -> bool:
        '''called when editor window opened'''
        default_set: bool = False
        selected_subcat_id = self.assemble_transaction_data_entry(0, True)    
        self.manage_budget_cur.execute("select [Sub-Category Name].[Most_recent_entity_id] from [Sub-Category Name] where id = (?)", (selected_subcat_id,))
        most_recent_entity_id = self.manage_budget_cur.fetchall()
        for i, entity in enumerate(self.entity_data):
            if entity[1] == most_recent_entity_id[0][0]:
                self.visual_functions.set_string_var(self.transaction_editor_window.dropdown_entity_name, new_value=self.entity_dropdown_list[i])
                default_set = True
                break
        return default_set

    def set_entity_delete_btn_status(self, event=None): 
        entity_name = self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_entity_name)
        if entity_name == self.entity_data[0][0]: #name is "None", disable
                self.visual_functions.configure_widget(self.transaction_editor_window.entity_delete_button, new_state="disabled")
        else: #not "None"
            for entity in self.entity_data:
                if entity_name == entity[0] and entity != self.entity_data[0][0]: #name is in list but not "None", enable
                    self.visual_functions.configure_widget(self.transaction_editor_window.entity_delete_button, new_state="normal")
                    break
                else: #name not in list, disable (prevent user confusion-delete would delete previous selection)
                    self.visual_functions.configure_widget(self.transaction_editor_window.entity_delete_button, new_state="disabled")                
            
    def delete_currently_selected_entity_from_db(self):
        for i, entity in enumerate(self.entity_data):
            if entity[0] == self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_entity_name):               
                self.manage_budget_cur.execute('''delete from Entity where id = ?''', (entity[1],))
                self.manage_budget_conn.commit()
                self.entity_data.pop(i)
                self.entity_dropdown_list.pop(i)
                self.visual_functions.set_string_var(self.transaction_editor_window.dropdown_entity_name, new_value=self.entity_data[0][0])
                self.visual_functions.delete_dropdown_entry(self.transaction_editor_window.entity_dropdown, 0, 'end')
                self.visual_functions.insert_into_dropdown(self.transaction_editor_window.entity_dropdown, 0, 'None')
                self.transaction_editor_window.entity_dropdown.update()
                self.visual_functions.configure_dropdown(self.transaction_editor_window.entity_dropdown, values=self.entity_dropdown_list) 
                self.visual_functions.grid_forget_widget(self.transaction_editor_window.confirm_entity_delete_button)                             
                break

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
        \nif manager window: calls modify_budget_database,
        \nif list window addnew button: calls add_new_transaction_to_list
         \nif list window editbutton: calls edit_transaction_in_list (this may just be a delete func, then the modify_budget_database func)'''
        if self.check_editor_entry_is_number() == True:
            if called_by_manager:
                try:                    
                    new_cell_total: float = float((self.selected_row_data[self.selected_column].replace(",", "").strip("$")))
                except ValueError:
                    new_cell_total: float = 0.0
                new_cell_total += self.transaction_editor_amount
                self.update_indicated_cell(new_cell_total, False, self.current_tab_num, self.selected_row_item, self.selected_row_data, self.selected_column)
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
                             non_selected_cell: bool, 
                             indicated_tab: int, 
                             indicated_row_item: str,
                             indicated_row_data: list[str], 
                             indicated_column: int,
                             update_count: int = 0):
        '''this method adds, removes or modifies transaction data in the tables,
        \ncan be called directly by editor window or by list window (passing the sum total of one or more transactions)
        \nnew_cell_total: is either the sum of all transaction in list window or the existing cell value + new transaction data
        \nnon_selected_cell: this indicates if the transaction is moving to another cell
        \nindicated_tab: indicates the destination tab/month
        \nindicated_row_item: indicates the destination treeview item
        \nindicated_row_data: the list of strings containing the rows current values (this is what is modified)
        \nindicated_column: is the position of the modified cell in the row data
        \nupdate_count: this prevents infinite recursive method calls(when yearly total tab is loaded)
        \nThis should NEVER be passed by an external call'''
        indicated_treeview = self.manage_budget_table.treeview_list[indicated_tab]
        try:
            old_cell_value: float = float(indicated_row_data[indicated_column].replace(",", "").strip("$"))
        except ValueError: #cell was a blank string, replace with 0.0
            old_cell_value = 0.0
        new_cell_value: str = '${:,.2f}'.format(round(new_cell_total, 2))
        indicated_row_data[indicated_column] = new_cell_value
        #update selected col cat subtotal
        indicated_row_item_parent = self.visual_functions.get_hierarchy_item_parent(indicated_treeview, indicated_row_item)
        indicated_cell_subtotal_item: str = self.visual_functions.get_hierarchy_item_children(indicated_treeview, indicated_row_item_parent)[-1]
        indicated_cell_cat_subtotal_data: list[str] = self.update_budget_totals_data(indicated_cell_subtotal_item, indicated_treeview, indicated_column, new_cell_total, old_cell_value)
        #update selected col section total
        indicated_row_section_item = self.visual_functions.get_hierarchy_item_parent(indicated_treeview, indicated_row_item_parent)
        indicated_row_section_data: list[str] = self.update_budget_totals_data(indicated_row_section_item, indicated_treeview, indicated_column, new_cell_total, old_cell_value)       
        #if total col exists, make it blank, loop thru row data cols, adding to new total, add it back to row data and update treeview
        if len(indicated_row_data) > 4:             
            new_total_flt: float = 0.0
            new_subtotal_total: float = 0.0
            new_section_total: float = 0.0
            for i, col in enumerate(indicated_row_data[2:-2]):
                if col == '': #add formated 0 to other cells in row if they are blank
                    indicated_row_data[i+2] = '${:,.2f}'.format(0.00)                                        
                else:
                    new_total_flt += float(col.replace(",", "").strip("$"))
                new_subtotal_total += float(indicated_cell_cat_subtotal_data[i+2].replace(",", "").strip("$")) #these totals are never ''
                new_section_total += float(indicated_row_section_data[i+2].replace(",", "").strip("$"))
            indicated_row_data[-2] = '${:,.2f}'.format(round(new_total_flt, 2))
            indicated_cell_cat_subtotal_data[-2] = '${:,.2f}'.format(round(new_subtotal_total, 2)) 
            indicated_row_section_data[-2] = '${:,.2f}'.format(round(new_section_total, 2)) 
        #update surplus shortfall column (using updated row data's)
        self.update_surplus_shortfall_column(indicated_row_data, indicated_row_section_item)
        self.update_surplus_shortfall_column(indicated_cell_cat_subtotal_data, indicated_row_section_item)
        self.update_surplus_shortfall_column(indicated_row_section_data, indicated_row_section_item)
        #update indicated cell, its category subtotal, and its section total       
        self.visual_functions.get_hierarchy_item(indicated_treeview, indicated_row_item, new_values=indicated_row_data)
        self.visual_functions.get_hierarchy_item(indicated_treeview, indicated_cell_subtotal_item, new_values=indicated_cell_cat_subtotal_data)
        self.visual_functions.get_hierarchy_item(indicated_treeview, indicated_row_section_item, new_values=indicated_row_section_data, display_open=True)
        self.calculate_or_update_surplus_shortfall_summary(indicated_treeview)
         #we need to update self.selected row data here if the only cell change is the column
        if non_selected_cell == True and self.selected_row_item == indicated_row_item and indicated_tab == self.current_tab_num: #I think this may be redundant?
            self.selected_row_data = indicated_row_data 
        self.selected_row_data = self.visual_functions.get_hierarchy_content(self.manage_budget_table.treeview_list[self.current_tab_num], self.selected_row_item, 'values')
        if self.yearly_total_tab_selected == True and update_count == 0: #yearly tab has loaded, and has not yet been updated
                update_count = 1 #ensure this value is passed to overwrite the default
                indicated_row_data = self.visual_functions.get_hierarchy_content(self.manage_budget_table.treeview_list[-1], indicated_row_item, "values")
                try:
                    yearly_totals_cell_total: float = float((indicated_row_data[indicated_column].replace(",", "").strip("$")))
                except ValueError:
                    yearly_totals_cell_total: float = 0.0
                new_cell_total = (new_cell_total - old_cell_value) + yearly_totals_cell_total
                self.update_indicated_cell(new_cell_total, non_selected_cell, -1, indicated_row_item, indicated_row_data, indicated_column, update_count)        

    def update_budget_totals_data(self, indicated_treeview_item: str, indicated_treeview, indicated_column: int, new_cell_total: float, old_cell_value: float)-> list[str]:
        '''calculates either new category subotal values or section total values when a cell is modified
        \nonly used by update_indicated_cell()'''
        indicated_total_data: list[str] = self.visual_functions.get_hierarchy_content(indicated_treeview, indicated_treeview_item, "values")
        #update the col being altered
        old_col_total: float = float(indicated_total_data[indicated_column].replace(",", "").strip("$"))
        new_col_total: float = round(old_col_total + (new_cell_total - old_cell_value), 2)
        indicated_total_data[indicated_column] = '${:,.2f}'.format(new_col_total)
        return indicated_total_data
    
    def update_surplus_shortfall_column(self, row_data: list[str], row_section_item)-> list[str]:    
        budgeted_amount: float = float(row_data[1].replace(",", "").strip("$"))
        actual_amount: float = float(row_data[-2].replace(",", "").strip("$"))
        if row_section_item == self.budget_section_list[0]:
            new_surplus_shorfall_value: float = actual_amount - budgeted_amount
        elif row_section_item == self.budget_section_list[1]:
            new_surplus_shorfall_value: float = budgeted_amount - actual_amount
        else:
            new_surplus_shorfall_value: float = float(row_data[-1].replace(",", "").strip("$"))
        row_data[-1] = '${:,.2f}'.format(new_surplus_shorfall_value)
        return row_data

    def modify_budget_database(self, modification: int, transaction_entry: tuple):
        '''this method modifies the budget sql database, taking a tuple containing the data for the transaction.
        \nthere are 3 options, each using somewhat different parts of transaction_entry:
        \nmodification=0 = adding: -1, 3, 5, 7, 8, 9, 11
        \nmodification=1 = modifying: -1, 3, 5, 7, 8, 9, 11, 0
        \nmodification=2 = deleting: 0'''
        if modification == 0: #add
            self.manage_budget_cur.execute("insert into Transactions (Amount, [Category_id], [Sub_Category_id], [Account_Type_id], Month, Day, [Entity_id]) Values (?, ?, ?, ?, ?, ?, ?)", 
                                       (transaction_entry[-1], transaction_entry[3], transaction_entry[5], transaction_entry[7], transaction_entry[8], transaction_entry[9], transaction_entry[11]))
            self.update_subcat_most_recent_entity(transaction_entry[5], transaction_entry[11]) #subcat id, entity id            
        elif modification == 1: #modify 
            self.manage_budget_cur.execute("update Transactions set Amount = ?, [Category_id] = ?, [Sub_Category_id] = ?, [Account_Type_id] = ?, Month = ?, Day = ?, Entity_id = ? where id = ?", 
                                        (transaction_entry[-1], transaction_entry[3], transaction_entry[5], transaction_entry[7], transaction_entry[8], transaction_entry[9], transaction_entry[11], transaction_entry[0]))
            self.update_subcat_most_recent_entity(transaction_entry[5], transaction_entry[11]) #subcat id, entity id            
        elif modification == 2: #delete
            self.manage_budget_cur.execute("delete from Transactions where id = ?", (transaction_entry[0], ))
        self.manage_budget_conn.commit()

    def update_subcat_most_recent_entity(self, subcat_id: int, entity_id: int):
        self.manage_budget_cur.execute("select Most_recent_entity_id from [Sub-Category Name] where [Sub-Category Name].id = (?)", (subcat_id,))
        if self.manage_budget_cur.fetchall()[0][0] == entity_id: #current most recent entity matches, do nothing
            pass
        else: #current entity id does NOT match, update it            
            self.manage_budget_cur.execute("update [Sub-Category Name] set Most_recent_entity_id = ? where id = ?", (entity_id, subcat_id))
            self.manage_budget_conn.commit()
        
    def reload_entity_data_from_db(self):
        '''This is called whenever a new entity is have been added to the db inside assemble_transaction_data_entry()
        \nIf we decide that entity changes should happen when list window is confirmed, the call may be moved to modify_budget_database()'''
        self.manage_budget_cur.execute("select Entity.Description, Entity.id from Entity")
        self.entity_data = self.manage_budget_cur.fetchall()       
    
    def add_new_transaction_to_list(self): 
        '''adds a new transaction to the list window,
        \nassigns 0 as temp transaction id and get [incexp id, cat, cat id, subcat, subcat id, account, account id, month, day, amount] and add to transactions list '''
        new_transaction_data: tuple = self.assemble_transaction_data_entry(0)
        self.transaction_list_window.add_transaction_to_list(new_transaction_data[-1], new_transaction_data[10], new_transaction_data[8], new_transaction_data[9])
        self.cell_transactions_from_db.append(new_transaction_data)

    def assemble_transaction_data_entry(self, transaction_id: int, subcat_id_only: bool = False) -> tuple:
        '''this method queries the budget database and references editor window dropdown values and returns a tuple containing:
        \ntransaction id, incexp id,category name, category id, subcategory name, subcategory id, account name, account id, tabnum, day, entity, transaction editor amount
        \ncan be used to assign id's to new and edited transactions
        \nis also called when setting entity defaults for editor (returning only subcat id)'''
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
        if subcat_id_only:
            return subcat_id
        acct_name = self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_account_name)
        self.manage_budget_cur.execute('''select Accounts.id  from Accounts where Accounts.[Account Name] = (?)''', (acct_name,))
        acct_id = self.manage_budget_cur.fetchall()[0][0]
        transaction_tab_num: int = self.current_tab_num                
        for i, tab in enumerate(self.tab_title_list): #update tab from current if changed in editor window
                if tab == self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_tab_name):
                    transaction_tab_num = i
        transaction_day: int = int(self.visual_functions.get_entrybox_content(self.transaction_editor_window.date_selector.date_entry).split("/")[0])
        entity_id: int | None = None
        entity_name: str = self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_entity_name)
        for entity in self.entity_data: #look for string that matches stringvar
            if entity[0] == entity_name:
                entity_id = entity[1]
                break
        if entity_id == None: #no matching entity name was in list, add it to DB, 
            self.manage_budget_cur.execute('''insert into Entity (Description) Values (?)''', (entity_name,))
            self.manage_budget_conn.commit()
            self.reload_entity_data_from_db()
        #select and assign entity id
        self.manage_budget_cur.execute('''select Entity.id from Entity where (Entity.Description) = (?)''', (entity_name,))
        entity_id = self.manage_budget_cur.fetchall()[0][0]
        return (transaction_id, transaction_incexp, cat_name, cat_id, subcat_name, subcat_id, acct_name, acct_id, transaction_tab_num, transaction_day, entity_name, entity_id, self.transaction_editor_amount)

    def edit_transaction_in_list(self): #confirm button in editor clicked (called for each selected transaction)
        '''Check for modifications to currently selected transaction (id'd by self.current_transaction_to_edit)
        \nif modifications found, update the entry in self.cell_transactions_from_db, update checkbox text value, and mark as modified
        \ndeselect checkbox, and update checkbox statuses list (even if no modifications found)'''
        incexp_mod: bool = self.income_expense_data[self.cell_transactions_from_db[self.current_transaction_to_edit][1]-1][0] == self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_incexp)
        category_mod: bool = self.cell_transactions_from_db[self.current_transaction_to_edit][2] == self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_category_name)
        subcategory_mod: bool = self.cell_transactions_from_db[self.current_transaction_to_edit][4] == self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_subcat_name)
        account_mod: bool = self.cell_transactions_from_db[self.current_transaction_to_edit][6] == self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_account_name)
        tab_mod: bool = self.tab_title_list[self.cell_transactions_from_db[self.current_transaction_to_edit][8]] == self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_tab_name)
        day_mod: bool = self.cell_transactions_from_db[self.current_transaction_to_edit][9] == int(self.visual_functions.get_entrybox_content(self.transaction_editor_window.date_selector.date_entry).split("/")[0])
        entity_mod: bool = self.cell_transactions_from_db[self.current_transaction_to_edit][10] == self.visual_functions.extract_str_var(self.transaction_editor_window.dropdown_entity_name)
        amount_mod: bool = self.cell_transactions_from_db[self.current_transaction_to_edit][-1] == round(float(self.visual_functions.extract_str_var(self.transaction_editor_window.entrybox_amount)), 2)

        if False in [incexp_mod, category_mod, subcategory_mod, account_mod, tab_mod, day_mod, entity_mod, amount_mod]: #modification found                     
            transaction_id: int = self.cell_transactions_from_db[self.current_transaction_to_edit][0] 
            modded_transaction_data: tuple = self.assemble_transaction_data_entry(transaction_id)
            self.cell_transactions_from_db[self.current_transaction_to_edit] = modded_transaction_data
            transaction_status: str = self.visual_functions.get_checkbox_attribute(self.transaction_list_window.transaction_checkbox_list[self.current_transaction_to_edit], 'text')
            if transaction_status.endswith(TrasactionStatuses.new.value):
                self.visual_functions.configure_widget(self.transaction_list_window.transaction_checkbox_list[self.current_transaction_to_edit], new_text='${:,.2f}'.format(self.cell_transactions_from_db[self.current_transaction_to_edit][-1]) + TrasactionStatuses.modifiednew.value, new_font=("Calibri", 18))
            else:
                self.visual_functions.configure_widget(self.transaction_list_window.transaction_checkbox_list[self.current_transaction_to_edit], new_text='${:,.2f}'.format(self.cell_transactions_from_db[self.current_transaction_to_edit][-1]) + TrasactionStatuses.modified.value, new_font=("Calibri", 18))
            self.visual_functions.configure_widget(self.transaction_list_window.transaction_entity_label_list[self.current_transaction_to_edit], new_text=self.cell_transactions_from_db[self.current_transaction_to_edit][10], new_font=("Calibri", 18))
            self.visual_functions.configure_widget(self.transaction_list_window.transaction_date_label_list[self.current_transaction_to_edit], new_text=f"{self.cell_transactions_from_db[self.current_transaction_to_edit][9]}/{self.cell_transactions_from_db[self.current_transaction_to_edit][8]}", new_font=("Calibri", 18))
        self.visual_functions.checkbox_deselect(self.transaction_list_window.transaction_checkbox_list[self.current_transaction_to_edit])
        self.transaction_list_window.checkbox_statuses[self.current_transaction_to_edit] = 0
    
    def select_entity_text_on_focus(self, event):
        self.visual_functions.set_dropdown_cursor(self.transaction_editor_window.entity_dropdown, 'end')
        self.visual_functions.set_dropdown_selection_range(self.transaction_editor_window.entity_dropdown, 0, 'end')        

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


   