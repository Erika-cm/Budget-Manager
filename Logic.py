from __future__ import annotations
from typing import Any, TYPE_CHECKING
from enum import Enum

import os
import sys
import json
if TYPE_CHECKING:
    from Visuals import MainMenu, NavigationPanel, RadioButtonMenu, EditBudgetTemplate, EditBudget, VisualFunctions, SaveNameWindow

#program system names
class SystemNames(Enum):
    create_new_system = "CreateNew"
    manage_budget_system = "Manage"

#save object types
class SaveObjectTypes(Enum):
    template = "Budget Template"
    budget = "Budget"

class AppLogic():
    '''
    System List:
    \nMETHODS: general app methods
    \nNAVIGATION PANEL: creates a map of the app, and enables navigation
    \nRADIOBUTTON MENU: creates a list of radiobuttons for files and templates, acts as a file loading system 
    \nTEMPLATE EDITOR: enables editing of the budget template (adding/removing/renaming) (sub)categories
    \nSAVE WINDOW: creates a window for entering a name and saving a template or a budget
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
        self.set_budget_editor_vars()
        
        
    #GENERAL METHODS
    def give_logic_program_system_access(self, 
                                         visual_functions: "VisualFunctions", 
                                         nav_panel: "NavigationPanel", 
                                         main_menu: "MainMenu", 
                                         create_new_template_radiobuttons: "RadioButtonMenu", 
                                         create_new_template_editor: "EditBudgetTemplate", 
                                         create_new_budget_editor: "EditBudget", 
                                         manage_budget_file_radiobuttons: "RadioButtonMenu"): #this will allow logic to access program systems not included in nav_map dict
        self.visual_functions = visual_functions
        self.nav_panel = nav_panel
        self.main_menu = main_menu
        self.create_new_template_radiobuttons = create_new_template_radiobuttons
        self.create_new_template_editor = create_new_template_editor
        self.create_new_budget_editor = create_new_budget_editor
        self.manage_budget_file_radiobuttons = manage_budget_file_radiobuttons

    def give_logic_temp_window_acess(self, save_window: "SaveNameWindow"):
        self.save_window = save_window
        
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

    def system_selection(self, system_name: SystemNames):
        self.selected_system_pages: list = self.nav_map.get(system_name.value, [])
        self.current_page = 0
        self.visual_functions.raise_panel(self.selected_system_pages[self.current_page])
        self.visual_functions.raise_panel(self.nav_panel)
        if system_name == SystemNames.create_new_system:
            self.display_template_list()
        elif system_name == SystemNames.manage_budget_system:
            self.display_budget_files()

    def nav_panel_continue_button(self): #NOTE: this throws exception when navigating from budget file version of radiobutton menu (it needs to be abstacted, or unique methods need to be added)
        if self.current_page < len(self.selected_system_pages) - 1: #not at end of pages, adv current page and raise corresponding page
            self.current_page += 1
            self.visual_functions.raise_panel(self.selected_system_pages[self.current_page])
            if self.current_page == 1: #at radiobutton menu, adv to next page(template editor) 
                if self.template_displayed == 0: #no template currently dispalyed, display current selection
                    self.selected_template_title: str = self.visual_functions.extract_str_var(self.create_new_template_radiobuttons.selected_template_name_widget_str)
                    self.selected_template_dict = self.store_selected_template_dict(self.selected_template_title)
                    self.display_template_and_title(self.selected_template_title, self.selected_template_dict)
                else:
                    pass #template already displayed, do nothing
            if self.current_page == 2:
                self.display_budget_table()
        elif self.current_page == len(self.selected_system_pages) - 1: # at end, continue does nothing
            pass

    def nav_panel_back_button(self): #NOTE, the page if conds should appear in inverse of the continue button (counting down)
        if self.current_page == 2:
            self.clear_budget_table()
        elif self.current_page == 1: #currently at template editor, return to radiobutton menu #0, reload template list  
            self.clear_template()
            self.display_template_list()
        if self.current_page > 0: #not at first page, go to previous page
            self.visual_functions.raise_panel(self.selected_system_pages[self.current_page - 1])
            self.current_page -= 1  
        elif self.current_page == 0: #currently on radiobutton menu,return to main menu
            self.visual_functions.raise_panel(self.main_menu)

    #RADIOBUTTON MENU NOTE: these functions, and the radiobutton menu class will be extended to work with budget files (remember to try to make these methods abstract where possible)
    def display_template_list(self): #this for example could apply to templates and budget files
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
        self.template_editor = self.create_new_template_editor.template_editor #create instance var ref of the template editor when tempalte displayed
        if self.template_displayed == 0: #no template currently displayed
            self.template_displayed = 1
            self.visual_functions.configure_widget(self.create_new_template_editor.template_title_label, new_text="Selected Template: " + template_title)
            self.template_income_section = self.visual_functions.insert_into_hierarchy(self.template_editor, "", 0, text_to_insert="Income", display_open=True)
            self.template_expenses_section = self.visual_functions.insert_into_hierarchy(self.template_editor, "", 2, text_to_insert="Expenses", display_open=True)
            if type(template) == dict:
                self.display_template_section(template.get("Income", {}), self.template_income_section)
                self.display_template_section(template.get("Expenses", {}), self.template_expenses_section)
            else: #no template selected
                pass
            self.visual_functions.raise_panel(self.create_new_template_editor.context_intro_message)
        else: #a template already displayed (something went wrong, that should not happen)
            pass
    
    def display_template_section(self, template_section: dict, template_editor_section: str):
        for category in template_section.keys():
            section_category_id = self.visual_functions.insert_into_hierarchy(self.template_editor, template_editor_section, 'end', text_to_insert=category, display_open=False)
            for subcat, monthly in zip(template_section.get(category, [])[0], template_section.get(category, [])[1]):
                self.visual_functions.insert_into_hierarchy(self.template_editor, section_category_id, 'end', text_to_insert=subcat, row_values=monthly, display_open=False)

    def clear_template(self):   
        if self.template_displayed == 1:
            self.visual_functions.delete_hierarchy_item(self.create_new_template_editor.template_editor, self.template_income_section)
            self.visual_functions.delete_hierarchy_item(self.create_new_template_editor.template_editor, self.template_expenses_section)
            self.template_displayed = 0 

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
        self.visual_functions.get_hierarchy_item(self.template_editor, self.current_focused_item, new_values=self.visual_functions.extract_int_var(self.create_new_template_editor.monthly_annual))
    
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
            self.save_budget_template()
        elif save_object_type == SaveObjectTypes.budget:
            print("saving a budget")

    #save object: template
    def save_budget_template(self):
        self.save_budget_template_title = self.visual_functions.extract_str_var(self.save_window.object_name_text)
        if self.save_budget_template_title in self.template_title_list:
            print("Template Exists, spawning warning window")
        elif self.save_budget_template_title == "": #no text entered, do nothing
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
    #NOTE: place save budget logic here

    #BUDGET CREATOR
    def set_budget_editor_vars(self):
        self.budget_displayed = 0

    def display_budget_table(self):
        self.budget_table = self.create_new_budget_editor.budget_table
        if self.budget_displayed == 0:
            self.visual_functions.configure_hierarchy_values(self.budget_table, "incexpfont", "Calibri", 18, 'underline')
            self.visual_functions.configure_hierarchy_values(self.budget_table, "catfont", "Calibri", 18, "bold")
            self.budget_income_section = self.visual_functions.insert_into_hierarchy(self.budget_table, "", 'end', row_values=("Income", "", ""), tags=("incexpfont",), display_open=True)
            self.budget_expenses_section = self.visual_functions.insert_into_hierarchy(self.budget_table, "", 'end', row_values=("Expenses", "", ""), tags=("incexpfont",), display_open=True)
            self.display_budget_table_income_section(self.budget_income_section)
            self.display_budget_table_income_section(self.budget_expenses_section)
            self.budget_displayed = 1
        else: #budget already displayed, this should not happen
            pass

    def display_budget_table_income_section(self, budget_section: str):
        budget_section_children = self.visual_functions.get_hierarchy_item_children(self.template_editor, budget_section)
        for category in budget_section_children:
            category_text = self.visual_functions.get_hierarchy_content(self.template_editor, category, 'text')
            self.visual_functions.insert_into_hierarchy(self.budget_table, budget_section, 'end', row_values=[category_text, "----------", "----------"], tags=("catfont",))
            category_children = self.visual_functions.get_hierarchy_item_children(self.template_editor, category)
            for subcat in category_children:
                subcat_text = self.visual_functions.get_hierarchy_content(self.template_editor, subcat, 'text')
                subcat_values = self.visual_functions.get_hierarchy_content(self.template_editor, subcat, 'values')
                if subcat_values[0] == 1: #monthly
                    self.visual_functions.insert_into_hierarchy(self.budget_table, category, 'end', row_values=[subcat_text, "----------", ""], tags=("1",))
                elif subcat_values[0] == 2: #annual
                    self.visual_functions.insert_into_hierarchy(self.budget_table, category, 'end', row_values=[subcat_text, "", "----------"], tags=("2",))
    
    def clear_budget_table(self):
        if self.budget_displayed == 1:
            for inc_exp in self.visual_functions.get_hierarchy_item_children(self.budget_table):
                self.visual_functions.delete_hierarchy_item(self.budget_table, inc_exp)
            self.budget_displayed = 0
    
    #events (core budget editing logic)
    def budget_table_double_click(self, event):
        current_focused_item = self.visual_functions.get_hierarchy_focus(self.budget_table)
        focused_item_grand_grandparent = self.visual_functions.get_hierarchy_item_parent(self.budget_table, self.visual_functions.get_hierarchy_item_parent(self.budget_table, current_focused_item))
        if self.visual_functions.get_hierarchy_content(self.budget_table, focused_item_grand_grandparent, 'values') == "":
            return 'break' #user dbl clicked a non-sub-category, do nothing
        if self.visual_functions.get_hierarchy_content(self.budget_table, focused_item_grand_grandparent, 'values') != "":
            selected_row_tags = self.visual_functions.get_hierarchy_content(self.budget_table, self.visual_functions.get_hierarchy_row(self.budget_table, event.y), 'tags')
            self.set_entrybox_location(event, int(selected_row_tags[0]))

    def set_entrybox_location(self, event, row_tag_num: int):
        self.selected_table_col = 3-row_tag_num #this flips the number to ID the proper column
        self.selected_row = self.visual_functions.get_hierarchy_row(self.budget_table, event.y)
        box_location = self.visual_functions.draw_hierarchy_bbox(self.budget_table, self.selected_row, col=self.selected_table_col)
        #NOTE: the column where the bbox appears is determined by it being monthly or annual, NOT by the location of the dbl click
        box_location = (
            int(float(box_location[0]) / self.scaling_factor),
            int(float(box_location[1]) / self.scaling_factor),
            int(float(box_location[2]) / self.scaling_factor),
            int(float(box_location[3]) / self.scaling_factor),
        )
        self.create_new_budget_editor.draw_budget_entry_box(self.budget_table, box_location[2], box_location[3], box_location[0], box_location[1])

    def update_budget_table_entry(self, event, entrybox):
        selected_row_data = self.visual_functions.get_hierarchy_content(self.budget_table, self.selected_row, 'values')
        try:
            selected_row_data[self.selected_table_col] = '${:,.2f}'.format(float(self.visual_functions.get_entrybox_content(entrybox)))
            self.visual_functions.get_hierarchy_item(self.budget_table, self.selected_row, new_values=selected_row_data)
        except ValueError:
            pass
        self.visual_functions.destroy_widget(entrybox)
