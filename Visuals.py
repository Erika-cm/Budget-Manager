from typing import Any, Tuple
import customtkinter as ctk
from tkinter import ttk
from enum import Enum
from typing import Literal, overload

from Logic import AppLogic, SystemNames, SaveObjectTypes

class VisualFunctions(ctk.CTkBaseClass):
    '''
    A class to store wrappers of tkinter functions to be called by Logic:
    \nupdate_window_data(): updates all specified window data outside of mainloop using .update()
    \nraise_panel(): raises a ctk.CTkFrame using tkraise()
    \nconfigure_widget(): alters the indicated parameter of a ctk widget using .configure()
    \nget_widget_width(): returns the current width of the widget in pixels using .winfo_width()
    \nget_widget_focus(): returns the widget that currently has focus using focus_get()
    \nset_widget_focus(): sets input focus to the passed widget using focus_set()
    \ndestroy_widget(): destroys the passed widget using .destroy()
    \ninsert_into_treeview(): inserts text and values into a ttk Treeview widget using .insert()
    \ndelete_treeview_item(): deletes a treeview item and all its children using .delete()
    \nget_hierarchy_item(): will either query or modify a treeview item using .item()
    \nget_hierarchy_parent_item(): will return ID of the parent of a treeview item using .parent()
    \nget_hierarchy_content(): returns either a string or list of text or values for a treeview item using .get()
    \nget_or_set_hierarchy_focus(): called by <<TreeviewSelect>> event, either sets focus to specified item, or returns current focus item using ttk's .focus()
    \nget_hierarchy_row(): returns string ID of treeview row at Y position, using identify_row()
    \nget_hierarchy_column(): returns string ID of treeview column at X position, using identify_column()
    \nconfigure_hierarchy_values(): allows configuration of the tags element of a treeview item using tag_configure()
    \ntextbox_insert(): inserts text into text box using .insert()
    \ntextbox_delete(): deletes text from a text box using .delete()
    \ntextbox_get(): returns the text from a text box using .get()
    \ntextbox_markset_insert():  places a mark at specficied index of a textbox, in this case limited to an 'insert' type, using .mark_set()
    \nentrybox_delete(): deletes text from an entry box using .delete()
    \nget_entrybox_content(): returns the content of specified entry box, using .get()
    \ncheckbox_select(): sets the variable linked to a checkbox to the checkbox's value using .select()
    \ncheckbox_deselect(): unsets the variable linked to a checkbox to the checkbox's value using .deselect()
    '''
    def __init__(self, master):
        super().__init__(master)

    #GENERAL
    def update_window_data(self, window: ctk.CTk):
        '''forces an update of all pending window characteristics prior to mainloop'''
        window.update()

    def raise_panel(self, panel: ctk.CTkFrame):
        '''employ function tkraise to raise the indicated ctk frame'''
        panel.tkraise()

    def configure_widget(self, widget: ctk.CTkBaseClass, new_text: str | None = None, new_text_color: str | None = None):
        '''employ .configure to alter ctk widgets'''
        if new_text != None and new_text_color == None: #only new text passed
            widget.configure(text=new_text)
        elif new_text == None and new_text_color != None: #only new text color passed
            widget.configure(text_color=new_text_color)
        else: #both new text and new text color passed
            widget.configure(text=new_text, text_color=new_text_color)

    def get_widget_width(self, widget: ctk.CTk):
        return widget.winfo_width()

    def get_widget_focus(self, widget: ctk.CTk):
        widget.focus_get()

    def set_widget_focus(self, widget: ctk.CTk):
        widget.focus_set()

    def destroy_widget(self, widget: ctk.CTk | Any):
        '''will destroy a CTk widget, will throw exception of non-CTk widget is passed'''
        widget.destroy()

    def extract_int_var(self, int_var: ctk.IntVar) -> list[int]:
        '''extracts list[int] from a tkinter Intvar'''
        extracted_int: list[int] = [int_var.get()]
        return extracted_int
    
    def extract_str_var(self, str_var: ctk.StringVar) -> str:
        extracted_string: str = str_var.get()
        return extracted_string

    #TREEVIEW
    @overload
    def insert_into_hierarchy(self, hierarchy_name: ttk.Treeview, parent_item, index_location: int | Literal['end'], text_to_insert: str="", row_values: list | tuple=[], tags: tuple[str, ...] = ("",), display_open: bool=True) -> str: ...
    @overload
    def insert_into_hierarchy(self, hierarchy_name: ttk.Treeview, parent_item, index_location: int | Literal['end'], text_to_insert: str="", row_values: list | tuple=[], tags: None = None, display_open: bool=True) -> str: ...
    def insert_into_hierarchy(self, hierarchy_name: ttk.Treeview, parent_item, index_location: int | Literal['end'], text_to_insert: str="", row_values: list | tuple=[], tags: tuple[str, ...] | None = None, display_open: bool=True) -> str:
        if tags == None: #tag not passed, insert without
            hierarchy_object_id = hierarchy_name.insert(parent=parent_item, index=index_location, text=text_to_insert, values=row_values, open=display_open)
        else: #tags passed, insert with
            hierarchy_object_id = hierarchy_name.insert(parent=parent_item, index=index_location, text=text_to_insert, values=row_values, tags=tags, open=display_open)
        return hierarchy_object_id
        
    def delete_hierarchy_item(self, hierarchy_name: ttk.Treeview, hierarchy_item: str):
        hierarchy_name.delete(hierarchy_item)

    @overload
    def get_hierarchy_item(self, hierarchy_name: ttk.Treeview, item_name: str | int, new_text: str = "", new_values: list | None=None, new_tags: list[str] | tuple[str] | None=None,  display_open: bool=False): ...
    @overload
    def get_hierarchy_item(self, hierarchy_name: ttk.Treeview, item_name: str | int, new_text: str | None=None, new_values: list=[], new_tags: list[str] | tuple[str] | None=None,  display_open: bool=False): ...
    @overload
    def get_hierarchy_item(self, hierarchy_name: ttk.Treeview, item_name: str | int, new_text: str | None=None, new_values: list | tuple | None=None, new_tags: list[str] | tuple[str] = [""],  display_open: bool=False): ...
    def get_hierarchy_item(self, hierarchy_name: ttk.Treeview, item_name: str | int, new_text: str | None=None, new_values: list | tuple | None=None, new_tags: list[str] | tuple[str] | None=None,  display_open: bool=False):
        '''NOTE: returns a treeview item dict, and allows editing of existing item's content with 'new_values', 'new_text', and 'new_tags' args'''
        hierarchy = hierarchy_name.item(item=item_name, open=display_open) #no data passed, simply return the hierarchy item
        if new_text != None: #text was passed
            hierarchy = hierarchy_name.item(item=item_name, text=new_text, open=display_open)
        if new_values != None: #values were passed
            hierarchy = hierarchy_name.item(item=item_name, values=new_values, open=display_open)
        if new_tags != None: #tags were passed
            hierarchy = hierarchy_name.item(item=item_name, tags=new_tags, open=display_open)
        return hierarchy
        
    def get_hierarchy_item_parent(self, hierarchy_name: ttk.Treeview, item_name: str | int) -> str:
        '''NOTE: arg: dict defaults to False.  If True, returns a treeview item dict.  If False, returns a treeview Item ID as a str'''
        return hierarchy_name.parent(item=item_name)
    
    def get_hierarchy_item_children(self, hierarchy_name: ttk.Treeview, item_name: str | int | None = None) -> tuple[str, ...]:
        return hierarchy_name.get_children(item=item_name)
    
    def get_hierarchy_item_index(self, hierarchy_name: ttk.Treeview, item_name: str | int) -> int:
        return hierarchy_name.index(item=item_name)
    
    def move_hierarchy_item(self, hierarchy_name: ttk.Treeview, item_name: str | int, new_index: int | Literal['end']):
        hierarchy_name.move(item=item_name, parent=self.get_hierarchy_item_parent(hierarchy_name, item_name), index=new_index)
    
    @overload
    def get_hierarchy_content(self, hierarchy_name: ttk.Treeview, item_name: str | int, content: Literal["text"]) -> str: ...
    @overload
    def get_hierarchy_content(self, hierarchy_name: ttk.Treeview, item_name: str | int, content: Literal["values"]) -> list[Any]: ...
    @overload
    def get_hierarchy_content(self, hierarchy_name: ttk.Treeview, item_name: str | int, content: Literal["tags"]) -> list[str]: ...

    def get_hierarchy_content(self, hierarchy_name: ttk.Treeview, item_name: str | int, content: Literal['text'] | Literal['values'] | Literal['tags']) -> str | list[Any] | list[str]:
        hierarchy_name.item
        if content == "text":
            hierarchy_content = hierarchy_name.item(item=item_name).get("text")
        elif content == 'values':
            hierarchy_content = hierarchy_name.item(item=item_name).get("values")
        elif content == 'tags':
            hierarchy_content = hierarchy_name.item(item=item_name).get("tags")
        else:
            hierarchy_content = ""
        return hierarchy_content    
    
    def get_hierarchy_focus(self, hierarchy_name: ttk.Treeview):
        '''Returns treeview item ID: str of current item with focus'''
        return hierarchy_name.focus()
    
    def get_hierarchy_row(self, hierarchy_name: ttk.Treeview, y_pos: int) -> str:
        '''use y_pos=event.y when triggered by event'''
        return hierarchy_name.identify_row(y=y_pos)
    
    def get_hierarchy_column(self, hierarchy_name: ttk.Treeview, x_pos) -> str:
        '''use x_pos=event.x when triggered by event'''
        return hierarchy_name.identify_column(x=x_pos)
        
    def set_hierarchy_focus(self, hierarchy_name: ttk.Treeview, item_name: None | str | int ):
        '''takes a treeview item ID, and sets focus to it'''
        hierarchy_name.focus(item=item_name)
    
    def set_hierarchy_single_selection(self, hierarchy_name: ttk.Treeview, item: str| int):
        hierarchy_name.selection_set(item)

    def configure_hierarchy_values(self, hierarchy_name: ttk.Treeview, font_name: str, font_family: str, size: int = 12, font_modifier: str = ""):
        '''configures a font that can be applied to the inserted values for the indicated treeview
         \napplied using tags= option in .insert (.insert_into_hierarchy) or .item(.get_hierarchy_item) methods (uses tag_configure)
         \n to apply: hierarchy_name.insert("", 'end', values=(text to be entered), tags = (font name (as a string),))
        \nfont modifiers: bold, italic, underline, overstrike'''
        hierarchy_name.tag_configure(font_name, font=(font_family, size, font_modifier))

    def draw_hierarchy_bbox(self, hierarchy_name: ttk.Treeview, item_name: str, col: str | int) -> tuple[int, int, int, int] | Literal['']:
        '''returns location and dimensions of a bounding box, for a treeview item, and specificly for the seleted cell if col is specified'''
        return hierarchy_name.bbox(item=item_name, column=col)
        
    #TEXTBOX
    def textbox_insert(self, textbox: ctk.CTkTextbox, index: str, text: str, tags: None | str = None):
        '''insert text into specified textbox BEFORE characters at index, add tags as optional arg'''
        textbox.insert(index=index, text=text, tags=tags)

    def textbox_delete(self, textbox: ctk.CTkTextbox, index1: str, index2: str | None):
        '''delete chars between index1(inclusive) and index 2(not inclusive). Can pass string literal "end" for index 2'''
        textbox.delete(index1=index1, index2=index2)

    def textbox_get(self, textbox: ctk.CTkTextbox, index1: str, index2: str | None) -> str:
        '''return chars between index1(inclusive) and index 2(not inclusive). Can pass string literal "end-1c" for index 2'''
        return textbox.get(index1=index1, index2=index2)

    def textbox_markset_insert(self, textbox: ctk.CTkTextbox, index: str):
        '''add an 'insert' mark at index in specified textbox'''
        textbox.mark_set(mark="insert", index=index)

    #ENTRYBOX
    def entrybox_delete(self, entrybox: ctk.CTkEntry, index1: str, index2: str | None):
        '''delete chars between index1(inclusive) and index 2(not inclusive). Can pass string literal "end" for index 2'''
        entrybox.delete(first_index=index1, last_index=index2)

    def get_entrybox_content(self, entrybox: ctk.CTkEntry) -> str:
        return entrybox.get()

    #CHECKBOX
    def checkbox_select(self, checkbox: ctk.CTkCheckBox) -> None:
        checkbox.select()

    def checkbox_deselect(self, checkbox: ctk.CTkCheckBox) -> None:
        checkbox.deselect()
    #general: .focus_set NOTE .focus is an older but compatible version of this, could update all general tkinter widget .focus function calls with focus_set()

class VisualThemes(ctk.CTkBaseClass):
    '''Contains methods to set visual themes for program widgets
    \nThemes included:
    \nHierarchical Menu (Treeview)
    \nData Table (currently Treeview)
    '''
    def __init__(self, master):
        super().__init__(master)
    
    def apply_style_hierarchical_menu(self, widget: ctk.CTkFrame):
        self.bg_color = widget._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        self.selected_color = widget._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.text_color = widget._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])

        self.template_editor_style = ttk.Style()
        self.template_editor_style.theme_use('default')
        self.template_editor_style.configure("Treeview", fieldbackground=self.bg_color, background=self.bg_color, foreground=self.text_color, font=('calibri', 15), borderwidth=0, rowheight=23)
        self.template_editor_style.map("Treeview", background=[("selected", self.bg_color)], foreground=[("selected", self.selected_color)]) 

    def apply_style_table(self, widget: ctk.CTkFrame):
        self.bg_color_table = widget._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        self.selected_color_table = widget._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.text_color_table = widget._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])

        self.template_table_style = ttk.Style(self)
        self.template_table_style.theme_use('default')
        self.template_table_style.configure("Treeview", fieldbackground=self.bg_color_table, background=self.bg_color_table, foreground=self.text_color_table, font=('calibri', 15), borderwidth=0, rowheight=28)
        self.template_table_style.configure("Treeview.Heading", borderwidth=1, relief="ridge", background=self.bg_color_table, foreground=self.text_color_table, font=('calibri', 15))
        self.template_table_style.map("Treeview", background=[("selected", "#303030")], foreground=[("selected", self.selected_color_table)]) #unlike hierarchy, selected cell should be lighter than ctkframe default color

class NavigationPanel(ctk.CTkFrame):
    def __init__(self, master: Any, app_logic: AppLogic):
        super().__init__(master)
        self.configure(bg_color="#3b3b3b")
        self.grid_columnconfigure((0,1,2,3), weight=1)
        self.grid_rowconfigure(0, weight=1)

        #widgets    
        #buttons
        self.button_continue = ctk.CTkButton(self, text="Continue", fg_color="#00aaff", font=('calibri', 35), command=app_logic.nav_panel_continue_button)
        self.button_back = ctk.CTkButton(self, text="Back", fg_color="#00aaff", font=('calibri', 35), command=app_logic.nav_panel_back_button)
        self.add_new_transaction_button = ctk.CTkButton(self, text="Add New Transaction", fg_color="#00aaff", font=('calibri', 35), state="disabled")
        self.edit_transactions_button = ctk.CTkButton(self, text="Edit Transactions", fg_color="#00aaff", font=('calibri', 35), state="disabled")
        
        #layout
        self.button_continue.grid(row=0, column=3, sticky="ne", pady=10, padx=10) 
        self.button_back.grid(row=0, column=0, sticky="nw", pady=10, padx=10)

class MainMenu(ctk.CTkFrame):
    def __init__(self, master: Any, create_new_system: SystemNames, manage_budget_system: SystemNames, app_logic: AppLogic):
        super().__init__(master)

        #Panel Chars
        self.grid_columnconfigure((0,2), weight=(1), uniform='a')
        self.grid_columnconfigure((1), weight=(4), uniform='a')
        self.grid_rowconfigure((0), weight=2)
        self.grid_rowconfigure((1,2,3), weight=1)
        self.grid_rowconfigure((4), weight=0)

        #Widgets
        self.main_menu_label = ctk.CTkLabel(self, text="Manage Your Money", text_color="#00aaff", font=('calibri', 65)) 
        #NOTE: ensure that the string passed into system_selction matches str passed into corresponding instance
        self.create_new_button = ctk.CTkButton(self, text="Create a New Budget", fg_color="#00aaff", font=('calibri', 40), command=lambda: app_logic.system_selection(create_new_system))
        self.open_existing_button = ctk.CTkButton(self, text="Manage an Existing Budget", fg_color="#00aaff", font=('calibri', 40), command = lambda: app_logic.system_selection(manage_budget_system))
        self.options_button = ctk.CTkButton(self, text="Options", fg_color="#00aaff", font=('calibri', 40))

        self.version_note = ctk.CTkLabel(self, text="Version 0.3.0", text_color="#686868")

        #layout
        self.main_menu_label.grid(row=0, column=1, columnspan=1, sticky='ew')

        self.create_new_button.grid(row=1, column=1, padx=50, pady=10, sticky='ns')
        self.open_existing_button.grid(row=2, column=1, padx=50, pady=10, sticky='ns')
        self.options_button.grid(row=3, column=1, padx=10, pady=10, ipadx=110, sticky='ns') 

        self.version_note.grid(row=4, column=2)
        
class RadioButtonMenu(ctk.CTkFrame):
    def __init__(self, parent, system_name: SystemNames, app_logic: AppLogic, menu_title: str):
        super().__init__(master=parent)
        self.grid_columnconfigure(0, weight=10)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=50)

        #variables for visuals
        self.selected_template_name_widget_str = ctk.StringVar(value="")

        #widgets
        self.menu_label = ctk.CTkLabel(self, text=menu_title, text_color="#00aaff", font=('calibri', 55))

        self.scrolling_list = ctk.CTkScrollableFrame(self)
        
        #layout
        self.menu_label.grid(row=0, column=0, sticky='ew', columnspan=2)
    
        self.scrolling_list.grid(row=2, column=0, sticky='nsew', padx=80, columnspan=2)
        self.scrolling_list.grid_columnconfigure(0, weight=1)
        self.scrolling_list.grid_rowconfigure(0, weight=1)

        app_logic.add_to_nav_map(system_name.value, self)
            
    #create radiobuttons from file/template list
    def create_radiobuttons(self, file_or_template_names: list[str]):
        for i, file_template in enumerate(file_or_template_names):
            self.radiobutton = ctk.CTkRadioButton(self.scrolling_list, text=file_template, value=file_template, variable=self.selected_template_name_widget_str)
            self.radiobutton.grid(row=0+i, column=0, pady=5, sticky="w")

class EditBudgetTemplate(ctk.CTkFrame):
    def __init__(self, parent, system_name: SystemNames, app_logic: AppLogic, visual_themes: VisualThemes):
        super().__init__(master=parent)

        #Variables
        self.monthly_annual = ctk.IntVar()
        self.app_logic = app_logic
        self.context_menu_text_box_focus = 0 #keep track of text box focus for context menu

        #Widgets
        #page labels
        self.template_editor_title = ctk.CTkLabel(self, text="Edit Budget Template", text_color="#00aaff", font=('calibri', 45))
        self.template_title_label = ctk.CTkLabel(self, text_color="#00aaff", font=('calibri', 35))

        #template editor frame
        self.budget_template_frame = ctk.CTkFrame(self)
        self.template_editor = ttk.Treeview(self.budget_template_frame, show='tree', selectmode='browse')

        #contextual menu 
        #intro message
        self.context_intro_message = ctk.CTkFrame(self)
        self.intro_message_label = ctk.CTkLabel(self.context_intro_message, text="To Edit Budget,\n Select a Component\n from the Menu")

        #income/expense selected
        self.context_income_expense = ctk.CTkFrame(self)
        self.income_expense_label = ctk.CTkLabel(self.context_income_expense, text_color='#ffffff', font=('calibri', 15))
        self.category_text_box = ctk.CTkTextbox(self.context_income_expense, height=100) #do we want word based text wrapping? default is character

        self.add_category_button = ctk.CTkButton(self.context_income_expense, text="Add New Category", fg_color="#00aaff", font=('calibri', 18), command=lambda widget=self.category_text_box : app_logic.add_textbox_content_to_template_editor(widget))

        #category selected
        self.context_category = ctk.CTkFrame(self)
        self.category_label = ctk.CTkLabel(self.context_category, text="Category Selected", text_color='#ffffff')
        
        self.category_text_box_in_category_menu = ctk.CTkTextbox(self.context_category, height=50)
        self.rename_category_button = ctk.CTkButton(self.context_category, text="Rename", fg_color="#00aaff", font=('calibri', 18), command=lambda widget=self.category_text_box_in_category_menu : app_logic.rename_hierachy_item(widget))
        self.moveup_category_button = ctk.CTkButton(self.context_category, text="Move Up", fg_color="#00aaff", font=('calibri', 18), command=app_logic.move_hierarchy_item_up)
        self.movedown_category_button = ctk.CTkButton(self.context_category, text="Move Down", fg_color="#00aaff", font=('calibri', 18), command=app_logic.move_hierarchy_item_down)
        self.delete_category_button = ctk.CTkButton(self.context_category, text="Delete Category", fg_color="#00aaff", font=('calibri', 18), command=app_logic.delete_selected_hierarchy_item)

        self.subcategory_text_box_in_category_menu = ctk.CTkTextbox(self.context_category, height=50)
        self.add_subcategory_button = ctk.CTkButton(self.context_category, text="Add New Sub-Category", fg_color="#00aaff", font=('calibri', 16), command=lambda widget=self.subcategory_text_box_in_category_menu : app_logic.add_textbox_content_to_template_editor(widget))

        #sub-category selected
        self.context_subcategory = ctk.CTkFrame(self)
        self.subcategory_label = ctk.CTkLabel(self.context_subcategory, text="Sub-category Selected", text_color='#ffffff')
        
        self.subcategory_textbox = ctk.CTkTextbox(self.context_subcategory, height=50)
        self.rename_subcategory_button = ctk.CTkButton(self.context_subcategory, text="Rename", fg_color="#00aaff", font=('calibri', 18), command=lambda widget=self.subcategory_textbox : app_logic.rename_hierachy_item(widget))
        self.moveup_subcategory_button = ctk.CTkButton(self.context_subcategory, text="Move Up", fg_color="#00aaff", font=('calibri', 18), command=app_logic.move_hierarchy_item_up)
        self.movedown_subcategory_button = ctk.CTkButton(self.context_subcategory, text="Move Down", fg_color="#00aaff", font=('calibri', 18), command=app_logic.move_hierarchy_item_down)
        self.delete_subcategory_button = ctk.CTkButton(self.context_subcategory, text="Delete Sub-category", fg_color="#00aaff", font=('calibri', 18), command=app_logic.delete_selected_hierarchy_item)

        self.subcategory_annual_checkbox= ctk.CTkCheckBox(self.context_subcategory, text="Annual", fg_color="#00aaff", font=('calibri', 18), onvalue=2, offvalue=1, variable=self.monthly_annual, command=app_logic.set_monthly_annual_checkbox_status)

        #save button
        self.save_button_frame = ctk.CTkFrame(self)
        self.save_template_button = ctk.CTkButton(self.save_button_frame, text="Save Template", fg_color="#00aaff", font=('calibri', 18), command=lambda: self.raise_save_template_window(app_logic))

        #Layout
        #page labels
        self.template_editor_title.place(relx=0.5, rely=0, anchor='n')
        self.template_title_label.place(relx=0.5, rely=0.1, anchor='n')

        #main frame: the template
        self.budget_template_frame.place(relx=0.08, rely=0.2, relwidth=0.65, relheight=0.80, anchor='nw')
        self.template_editor.pack(expand=True, fill='both', padx=10, pady=10)
        
        #contextual menu
        #intro message
        self.context_intro_message.place(relx=0.74, rely=0.2, relwidth=0.18, relheight=0.70, anchor='nw')
        self.intro_message_label.pack()
        #income/expense
        self.context_income_expense.place(relx=0.74, rely=0.2, relwidth=0.18, relheight=0.70, anchor='nw')
        self.income_expense_label.pack()
        self.category_text_box.pack(padx=10, pady=5)
        self.add_category_button.pack(padx=10, pady=5)
        #category selected
        self.context_category.place(relx=0.74, rely=0.2, relwidth=0.18, relheight=0.70, anchor='nw')
        self.category_label.pack()
        self.category_text_box_in_category_menu.pack(padx=10, pady=5)
        self.rename_category_button.pack(padx=10, pady=5)
        self.moveup_category_button.pack(padx=10, pady=5)
        self.movedown_category_button.pack(padx=10, pady=5)
        self.delete_category_button.pack(padx=10, pady=5)
        self.subcategory_text_box_in_category_menu.pack(padx=10, pady=5)
        self.add_subcategory_button.pack(padx=10, pady=5)
        #sub-category selected
        self.context_subcategory.place(relx=0.74, rely=0.2, relwidth=0.18, relheight=0.70, anchor='nw')
        self.subcategory_label.pack()
        self.subcategory_textbox.pack(padx=10, pady=5)
        self.rename_subcategory_button.pack(padx=10, pady=5)
        self.moveup_subcategory_button.pack(padx=10, pady=5)
        self.movedown_subcategory_button.pack(padx=10, pady=5)
        self.delete_subcategory_button.pack(padx=10, pady=5)
        self.subcategory_annual_checkbox.pack(padx=10, pady=5)
        #save button
        self.save_button_frame.place(relx=0.74, rely=0.92, relwidth=0.18, relheight=0.08, anchor='nw')
        self.save_template_button.pack(padx=5, pady=5, expand=True, fill='both')

        #Events
        #raise context menu on select of template component
        self.template_editor.bind("<<TreeviewSelect>>", app_logic.raise_context_menu)

        #income/expense focus
        self.category_text_box.bind("<FocusIn>", lambda event: self.add_context_menu_textbox_focus(event, self.category_text_box))
        self.category_text_box.bind("<FocusOut>", lambda event: self.remove_context_menu_textbox_focus(event, self.category_text_box))

        # #category focus
        self.category_text_box_in_category_menu.bind("<FocusIn>", lambda event: self.add_context_menu_textbox_focus(event, self.category_text_box_in_category_menu))
        self.category_text_box_in_category_menu.bind("<FocusOut>", lambda event: self.remove_context_menu_textbox_focus(event, self.category_text_box_in_category_menu))

        self.subcategory_text_box_in_category_menu.bind("<FocusIn>", lambda event: self.add_context_menu_textbox_focus(event, self.subcategory_text_box_in_category_menu))
        self.subcategory_text_box_in_category_menu.bind("<FocusOut>", lambda event: self.remove_context_menu_textbox_focus(event, self.subcategory_text_box_in_category_menu))

        #subcategory focus 
        self.subcategory_textbox.bind("<FocusIn>", lambda event: self.add_context_menu_textbox_focus(event, self.subcategory_textbox))
        self.subcategory_textbox.bind("<FocusOut>", lambda event: self.remove_context_menu_textbox_focus(event, self.subcategory_textbox))

        self.textbox_dict = {self.category_text_box : lambda event, widget=self.category_text_box : app_logic.add_textbox_content_to_template_editor(widget, event), 
                        self.category_text_box_in_category_menu : lambda event, widget=self.category_text_box_in_category_menu : app_logic.rename_hierachy_item(widget, event),
                        self.subcategory_text_box_in_category_menu : lambda event, widget=self.subcategory_text_box_in_category_menu : app_logic.add_textbox_content_to_template_editor(widget, event),
                        self.subcategory_textbox : lambda event, widget=self.subcategory_textbox : app_logic.rename_hierachy_item(widget, event)}
        
        app_logic.add_to_nav_map(system_name.value, self)
        visual_themes.apply_style_hierarchical_menu(self.budget_template_frame)

    def add_context_menu_textbox_focus(self, event, widget: ctk.CTkTextbox):
        if self.context_menu_text_box_focus == 0:
            self.context_menu_text_box_focus = 1
            widget.bind("<Return>", self.textbox_dict.get(widget, Any))
    
    def remove_context_menu_textbox_focus(self, event, widget: ctk.CTkTextbox):
        if self.context_menu_text_box_focus == 1:
            self.context_menu_text_box_focus = 0
            widget.unbind("<Return>")

    def raise_save_template_window(self, app_logic: AppLogic):
        self.save_template_window = SaveNameWindow(self, SaveObjectTypes.template, app_logic.selected_template_title, app_logic)
        self.save_template_window.focus()
        self.save_template_window.grab_set()    

class EditBudget(ctk.CTkFrame):
    def __init__(self, parent, system_name: SystemNames, app_logic: AppLogic, visual_themes: VisualThemes):
        super().__init__(master=parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)    
        self.grid_rowconfigure(1, weight=50) 

        #variables
        self.app_logic = app_logic

        #widgets
        self.enter_budget_amounts_label = ctk.CTkLabel(self, text="Enter Monthly and Annual Budget Amounts", text_color="#00aaff", font=('calibri', 35))
        
        self.budget_table_frame = ctk.CTkFrame(self)
        
        self.budget_displayed = 0 #indicator: budget is displayed in table NOTE this will likely be need in logic, not here
        self.budget_table = ttk.Treeview(self.budget_table_frame, columns=('category', 'annual', 'monthly'), show='headings')#, style="Treeview")
        self.budget_table.heading('category', text="Budget Category")
        self.budget_table.heading('annual', text="Annual Amount")
        self.budget_table.heading('monthly', text="Monthly Amount")
        self.budget_table.column('annual', anchor='center')
        self.budget_table.column('monthly', anchor='center')

        #self.budget_table.bind("<Double-1>", budget_table_double_click)

        #layout
        self.enter_budget_amounts_label.grid(row=0, column=0, sticky='new')

        self.budget_table_frame.grid(row=1, column=0, padx=80, sticky='nsew')
        self.budget_table.pack(expand=True, fill='both', padx=5, pady=5)

        app_logic.add_to_nav_map(system_name.value, self)
        visual_themes.apply_style_table(self)

        #events
        self.budget_table.bind("<Double-1>", lambda event: self.app_logic.budget_table_double_click(event))

    #create entry boxes on dbl click
    def draw_budget_entry_box(self, hierarchy_name: ttk.Treeview, width: int, height: int, x_pos: int, y_pos: int):
        self.budget_entry = ctk.CTkEntry(hierarchy_name, width=width, height=height)
        self.budget_entry.place(x=x_pos, y=y_pos)
        self.budget_entry.focus()
        self.budget_entry.bind("<Return>", lambda event: self.app_logic.update_budget_table_entry(event, self.budget_entry))
        self.budget_entry.bind("<FocusOut>", lambda event: self.app_logic.update_budget_table_entry(event, self.budget_entry))

    #func to call save budget window

class SaveNameWindow(ctk.CTkToplevel):
    def __init__(self, master: Any, save_object_type: SaveObjectTypes, save_object_title: str, app_logic: AppLogic):
        super().__init__(master)

        #panel chars
        self.title("Save")
        self.geometry("400x240")
        self.grid_columnconfigure((0), weight=1, uniform="a")
        self.grid_columnconfigure((1), weight=3, uniform="a")
        self.grid_columnconfigure((2), weight=3, uniform="a")
        self.grid_columnconfigure((3), weight=1, uniform="a")
        self.grid_rowconfigure((0,1,2), weight=1, uniform="a")

        #variables
        self.object_name_text = ctk.StringVar(value=save_object_title)

        #widgets
        self.save_object_label = ctk.CTkLabel(self, text="Save " + save_object_type.value, text_color="#00aaff", font=('calibri', 30))
        
        self.object_title_box = ctk.CTkEntry(self, textvariable=self.object_name_text)
        self.clear_titlebox = ctk.CTkButton(self, text="clear", fg_color='transparent', hover=False, text_color="#00aaff", font=('calibri', 12), command=lambda : app_logic.clear_title_box(self.object_title_box)) 
        
        self.cancel_button = ctk.CTkButton(self, text="Cancel", fg_color="#00aaff", font=('calibri', 22), command=self.destroy)
        self.save_button = ctk.CTkButton(self, text="Save", fg_color="#00aaff", font=('calibri', 22), command=lambda: app_logic.call_save_methods(save_object_type))

        #layout
        self.save_object_label.grid(row=0, column=1, columnspan=2, sticky="sew")

        self.object_title_box.grid(row=1, column=1, columnspan=2, sticky="ew")
        self.clear_titlebox.grid(row=1, column=3, sticky="e")

        self.cancel_button.grid(row=2, column=1, sticky="new", padx=5)
        self.save_button.grid(row=2, column=2, sticky="new", padx=5)

        app_logic.give_logic_temp_window_acess(self) #allow logic access to save window members once they exist 

        #events
        self.clear_titlebox.bind("<Enter>", lambda event: app_logic.on_hover_clear(event, self.clear_titlebox))
        self.clear_titlebox.bind("<Leave>", lambda event: app_logic.on_leave_clear(event, self.clear_titlebox))


