import sqlite3
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import json
import os

# A class for main app window
class MainWindow(ctk.CTk):
    def __init__(self, title, windowsize):
        super().__init__()
        self.title(title)
        #self.window_size = windowsize use this to set widget sizes relative to window size if needed
        self.geometry(f'{windowsize[0]}x{windowsize[1]}')

        self.update()
        self.scaling_factor = self.winfo_width() / windowsize[0]
        
        #next: make scaling_factor accessable from enter_budget_amounts
        #then implement adjustment of bounding box based on scaling
        #widgets
        #button panel for create new budget process
        self.button_panel = ctk.CTkFrame(self, bg_color="#3b3b3b")
        self.button_panel.grid_columnconfigure((0,1,2,3), weight=1)
        self.button_panel.grid_rowconfigure(0, weight=1)
        #buttons
        self.button_continue = ctk.CTkButton(self.button_panel, text="Continue", fg_color="#00aaff", font=('calibri', 35), command=self.createnew_or_managebudget_pressed_continue)
        self.button_back = ctk.CTkButton(self.button_panel, text="Back", fg_color="#00aaff", font=('calibri', 35), command=self.createnew_or_managebudget_pressed_back)
        self.add_new_transaction_button = ctk.CTkButton(self.button_panel, text="Add New Transaction", fg_color="#00aaff", font=('calibri', 35), state="disabled")
        self.edit_transactions_button = ctk.CTkButton(self.button_panel, text="Edit Transactions", fg_color="#00aaff", font=('calibri', 35), state="disabled")
        # button panel layout
        self.button_continue.grid(row=0, column=3, sticky="ne", pady=10, padx=10) 
        self.button_back.grid(row=0, column=0, sticky="nw", pady=10, padx=10)

        #pages: manage budget
        self.manage_budget_p1 = RadioButtonMenu(self, "Open Existing Budget")
         
        #pages: create a new budget
        self.create_new_p1 = RadioButtonMenu(self, "Choose a Budget Template")
        self.create_new_p2 = EditBudgetTemplate(self) 

        #main menu
        self.main_menu = MainMenu(self, self.create_new_p1, self.button_panel, self.manage_budget_p1) #need to pass any pages that are accessed by the button on main menu directly (so just the 1st)
        self.main_menu.configure(fg_color="transparent")     

        #final create new budget page (has to come after main menu so that mainmenu is raisable from that page)(same for final manage budget page)
        self.create_new_p3 = EnterBudgetAmounts(self, self.main_menu, self.scaling_factor)
        self.manage_budget_p2 = ManageBudget(self, self.main_menu, self.add_new_transaction_button, self.edit_transactions_button)

        #set commands for transaction buttons in manage_budget_p2
        self.add_new_transaction_button.configure(command=self.transaction_editor_window)
        self.edit_transactions_button.configure(command=self.transaction_list_window)
        
        #layout
        self.main_menu.place(relx=0.5, rely=0, relwidth=1, relheight=1, anchor='n')
        
        self.create_new_p1.place(relx=0.5, rely=0, relwidth=1, relheight=0.9, anchor='n')
        self.create_new_p2.place(relx=0.5, rely=0, relwidth=1, relheight=0.9, anchor='n')
        self.create_new_p3.place(relx=0.5, rely=0, relwidth=1, relheight=0.9, anchor='n')

        self.manage_budget_p1.place(relx=0.5, rely=0, relwidth=1, relheight=0.9, anchor='n')
        self.manage_budget_p2.place(relx=0.5, rely=0, relwidth=1, relheight=0.9, anchor='n')

        self.button_panel.place(relx=0.5, rely=1, relwidth=1, relheight=0.1, anchor='s')

        #other variables 
        #list that tracks pages for button_panel    
        self.create_new_pages = [self.create_new_p1, self.create_new_p2, self.create_new_p3]
        self.current_page_createnew = 0

        #list that tracks pages for button_panel
        self.manage_budget_pages = [self.manage_budget_p1, self.manage_budget_p2]
        self.current_page_manage_budget = 0

        #NOTE directory where user files will be saved may go here
        
        self.main_menu.tkraise() #main menu shows up at launch
        self.mainloop()

    #two functions to check if user pressed create new or manage existing budget
    def createnew_or_managebudget_pressed_back(self):
        if self.main_menu.createnew_or_manage == "create new":
            self.back_button_createnew()
        if self.main_menu.createnew_or_manage == "manage budget":
            self.back_button_managebudget()
    
    def createnew_or_managebudget_pressed_continue(self):
        if self.main_menu.createnew_or_manage == "create new":
            self.continue_button_createnew()
        if self.main_menu.createnew_or_manage == "manage budget":
            self.continue_button_managebudget()
    
    #two sets of functions setting behaviour of continue and back buttons, for the create new and manage existing sections
    def back_button_createnew(self):
        if self.current_page_createnew > 0: 
            if self.current_page_createnew == 1: #current page: 2 (going to 1)
                self.create_new_p2.clear_template() 
            if self.current_page_createnew == 2: #current page: 3 (going to 2)
                self.create_new_p2.set_treeview_style_template_editor()
                self.create_new_p3.clear_budget_table()
            self.create_new_pages[self.current_page_createnew - 1].tkraise()
            self.current_page_createnew -= 1       
        else:
            self.main_menu.tkraise()
    
    def continue_button_createnew(self):
        if self.current_page_createnew == 0: #current page: 1 (going to 2)
            self.create_new_p2.display_template_and_title(self.create_new_p1.template_title.get(), self.create_new_p1.template_list) #display chosen template
            self.create_new_p2.set_treeview_style_template_editor()
        if self.current_page_createnew == 1: #current page 2 (going to 3)
            self.create_new_p3.display_budget_table(self.create_new_p2.template_editor)
            self.create_new_p3.set_treeview_style_table()
        if self.current_page_createnew == 2: #current page 3 (clicking to save budget)
            self.create_new_p3.check_budget_table()
        if self.current_page_createnew < len(self.create_new_pages) - 1:
            self.create_new_pages[self.current_page_createnew + 1].tkraise()
            self.current_page_createnew += 1
    
    def back_button_managebudget(self):
        if self.current_page_manage_budget > 0:
            if self.current_page_manage_budget == 1: #current page 2 (going back to 1)
                self.manage_budget_p2.clear_manage_budget_table()
            self.add_new_transaction_button.grid_forget()
            self.edit_transactions_button.grid_forget()
            self.manage_budget_pages[self.current_page_manage_budget - 1].tkraise()
            self.current_page_manage_budget-=1   
            self.button_continue.configure(text="Continue") 
        else:
            self.main_menu.tkraise()
    
    def continue_button_managebudget(self):
        if self.current_page_manage_budget == 0: #current page:1 (going to 2)
            self.manage_budget_p2.display_budget_management_table(self.manage_budget_p1.budget_filename) #This passes the selected budget file to the budget management table
            self.manage_budget_p2.set_treeview_style_managebudget_table()
            self.button_continue.configure(text="Main Menu")
            self.add_new_transaction_button.grid(row=0, column=1, sticky="nw", pady=10, padx=10)
            self.edit_transactions_button.grid(row=0, column=2, sticky="ne", pady=10, padx=10)
        elif self.current_page_manage_budget == 1: #current page: 2 (returning to main)
            self.manage_budget_p2.clear_manage_budget_table()
            self.add_new_transaction_button.grid_forget()
            self.edit_transactions_button.grid_forget()
            self.button_continue.configure(text="Continue") 
            self.main_menu.tkraise()
        if self.current_page_manage_budget < len(self.manage_budget_pages) - 1: #not at end of pages
            self.manage_budget_pages[self.current_page_manage_budget + 1].tkraise()
            self.current_page_manage_budget += 1
        else: #on last page (return to main and reset page counter)
            self.current_page_manage_budget = 0
            
    
    def transaction_list_window(self):
        self.manage_budget_p2.selected_cell_transaction_list()
    
    def transaction_editor_window(self):
        self.manage_budget_p2.get_selected_cell_info(called_by_manager=1)
            
#a frame that holds the main menu (title, buttons(3), version note)
class MainMenu(ctk.CTkFrame):
    def __init__(self, parent, create_new_frame, create_new_button_panel_frame, manage_budget_frame):
        super().__init__(master=parent)
        self.grid_columnconfigure((0,2), weight=(1), uniform='a')
        self.grid_columnconfigure((1), weight=(4), uniform='a')
        self.grid_rowconfigure((0), weight=2)
        self.grid_rowconfigure((1,2,3), weight=1)
        self.grid_rowconfigure((4), weight=0)
        
        #pass each frame/page/variable that each button in Main menu can raise
        self.create_new_p1 = create_new_frame
        self.button_panel = create_new_button_panel_frame
        self.manage_budget_p1 = manage_budget_frame

        #widgets 1 label,3 buttons, another label
        self.main_menu_label = ctk.CTkLabel(self, text="Manage Your Money", text_color="#00aaff", font=('calibri', 65))
        
        self.create_new_button = ctk.CTkButton(self, text="Create a New Budget", fg_color="#00aaff", font=('calibri', 40), command = self.create_new)
        self.open_existing_button = ctk.CTkButton(self, text="Manage an Existing Budget", fg_color="#00aaff", font=('calibri', 40), command = self.manage_budget)
        self.options_button = ctk.CTkButton(self, text="Options", fg_color="#00aaff", font=('calibri', 40))

        self.version_note = ctk.CTkLabel(self, text="Version 0.2", text_color="#686868")

        #variables
        self.createnew_or_manage = "" #indicator stores one value when 'create new' is pressed, another for 'manage budget'

        #layout
        self.main_menu_label.grid(row=0, column=1, columnspan=1, sticky='ew')

        self.create_new_button.grid(row=1, column=1, padx=50, pady=10, sticky='ns')
        self.open_existing_button.grid(row=2, column=1, padx=50, pady=10, sticky='ns')
        self.options_button.grid(row=3, column=1, padx=10, pady=10, ipadx=110, sticky='ns') 

        self.version_note.grid(row=4, column=2)

    #functions to start budget processes
    def create_new(self):
        self.createnew_or_manage = "create new"
        self.create_new_p1.tkraise()
        self.button_panel.tkraise()
        self.create_new_p1.display_template_list()
    
    def manage_budget(self):
        self.createnew_or_manage = "manage budget"
        self.manage_budget_p1.tkraise()
        self.button_panel.tkraise()
        self.manage_budget_p1.display_budget_files()
       
class RadioButtonMenu(ctk.CTkFrame):
    def __init__(self, parent, menu_title):
        super().__init__(master=parent)
        self.grid_columnconfigure(0, weight=10)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=50)

        #widgets
        self.menu_label = ctk.CTkLabel(self, text=menu_title, text_color="#00aaff", font=('calibri', 55))

        self.scrolling_list = ctk.CTkScrollableFrame(self)

        self.template_title = ctk.StringVar(value="")
        self.budget_filename = ctk.StringVar(value="")
        
        #layout
        self.menu_label.grid(row=0, column=0, sticky='ew', columnspan=2)
    
        self.scrolling_list.grid(row=2, column=0, sticky='nsew', padx=80, columnspan=2)
        self.scrolling_list.grid_columnconfigure(0, weight=1)
        self.scrolling_list.grid_rowconfigure(0, weight=1)


    #functionality:
    #1-read json file and load user generated templates-called when this page is raised
    def display_template_list(self): 
        self.template_list = [default_budget_template]
        try:
            with open('budget templates.json', 'r') as template_import:
                imported_templates = json.load(template_import)
                for user_template in imported_templates:
                    self.template_list.append(user_template)
        except FileNotFoundError:
            print("template json file not found")
        for index, template in enumerate(self.template_list):
            self.template_radiobutton = ctk.CTkRadioButton(self.scrolling_list, text=template.get("Title"), value=template.get("Title"), variable=self.template_title) 
            self.template_radiobutton.grid(row=0+index, column=0, pady=5, sticky='w')
        return self.template_list
    
    #find all sqlite files in cwd, and place them in list - when page is raised
    def display_budget_files(self):
        self.budget_list = []
        self.path = os.getcwd()
        self.file_list = os.listdir(self.path)
        for file in self.file_list:
            if file.endswith(".sqlite") == True:
                self.budget_list.append(file)
        for index, budget in enumerate(self.budget_list):
            budget_name = budget.split(".")[0]
            self.budget_radiobutton = ctk.CTkRadioButton(self.scrolling_list, text=budget_name, value=budget, variable=self.budget_filename)
            self.budget_radiobutton.grid(row=0+index, column=0, pady=5, sticky='w')

class EditBudgetTemplate(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent)
        
        #widgets
        #page labels
        self.edit_template_label = ctk.CTkLabel(self, text="Edit Budget Template", text_color="#00aaff", font=('calibri', 45))
        self.template_title_label = ctk.CTkLabel(self,text_color="#00aaff", font=('calibri', 35))
        
        #main frame: the template editor treeview
        self.budget_template_frame = ctk.CTkFrame(self)

        self.budget_template_frame.bind("<<TreeviewSelect>>", lambda event: self.budget_template_frame.focus())

        self.template_displayed = 0 #inidcator: template has been displayed in treeview
        self.template_editor = ttk.Treeview(self.budget_template_frame, show='tree', selectmode='browse')

        #secondary frame: contextual menu based on selected element of the treeview widget
        #income/expense
        self.context_income_expense = ctk.CTkFrame(self)
        self.income_expense_label = ctk.CTkLabel(self.context_income_expense, text_color='#ffffff', font=('calibri', 15))
        self.category_text_box = ctk.CTkTextbox(self.context_income_expense, height=100) #do we want word based text wrapping? default is character
        #keep track of text box focus
        self.category_text_box_focus = 0

        def return_pressed_in_category_text_box(event=""):
            if self.category_text_box.get("1.0", "end-1c") == "":
                self.category_text_box.delete("0.0", "end")
                self.category_text_box.mark_set("insert", "0.0")
            if self.category_text_box.get("1.0", "end-1c") != "":
                self.template_editor.insert(self.template_editor.focus(), tk.END, text=self.category_text_box.get("1.0", "end-1c")) 
                self.template_editor.selection_set(self.template_editor.get_children(self.template_editor.focus())[-1])
                self.template_editor.focus(self.template_editor.get_children(self.template_editor.focus())[-1])
                self.category_text_box.delete("0.0", "end")
                self.category_text_box.mark_set("insert", "0.0")
            return "break"           
        
        def update_category_textbox_focus(event):
            if self.category_text_box_focus == 0:
                self.category_text_box_focus = 1
                self.category_text_box.bind("<Return>", return_pressed_in_category_text_box)
            elif self.category_text_box_focus == 1:
                self.category_text_box_focus = 0
                self.category_text_box.unbind("<Return>")
        
        self.category_text_box.bind("<FocusIn>", update_category_textbox_focus)
        self.category_text_box.bind("<FocusOut>", update_category_textbox_focus)

        self.add_category_button = ctk.CTkButton(self.context_income_expense, text="Add New Category", fg_color="#00aaff", font=('calibri', 18), command=return_pressed_in_category_text_box)
        
        #category selected
        self.context_category = ctk.CTkFrame(self)
        self.category_label = ctk.CTkLabel(self.context_category, text="Category Selected", text_color='#ffffff')
        self.category_text_box_in_category_menu = ctk.CTkTextbox(self.context_category, height=50)

        def rename_category(event=""):
            self.template_editor.item(self.template_editor.focus(), text=self.category_text_box_in_category_menu.get("1.0", "end-1c"))
            return 'break'
        
        self.category_textbox_in_category_menu_focus = 0

        def update_category_textbox_in_category_menu_focus(event):
            if self.category_textbox_in_category_menu_focus == 0:
                self.category_textbox_in_category_menu_focus = 1
                self.category_text_box_in_category_menu.bind("<Return>", rename_category)
            elif self.category_textbox_in_category_menu_focus == 1:
                self.category_textbox_in_category_menu_focus = 0
                self.category_text_box_in_category_menu.unbind("<Return>")
        
        self.category_text_box_in_category_menu.bind("<FocusIn>", update_category_textbox_in_category_menu_focus)
        self.category_text_box_in_category_menu.bind("<FocusOut>", update_category_textbox_in_category_menu_focus)

        self.rename_category_button = ctk.CTkButton(self.context_category, text="Rename", fg_color="#00aaff", font=('calibri', 18), command=rename_category)
       
        def move_category_up():
            current_category_pos = self.template_editor.index(self.template_editor.focus())
            self.template_editor.move(self.template_editor.focus(), self.template_editor.parent(self.template_editor.focus()), current_category_pos-1)

        def move_category_down():
            current_category_pos = self.template_editor.index(self.template_editor.focus())
            self.template_editor.move(self.template_editor.focus(), self.template_editor.parent(self.template_editor.focus()), current_category_pos+1)

        self.moveup_category_button = ctk.CTkButton(self.context_category, text="Move Up", fg_color="#00aaff", font=('calibri', 18), command=move_category_up)
        self.movedown_category_button = ctk.CTkButton(self.context_category, text="Move Down", fg_color="#00aaff", font=('calibri', 18), command=move_category_down)
        
        def delete_selected_category():
            self.template_editor.delete(self.template_editor.focus())

        self.delete_category_button = ctk.CTkButton(self.context_category, text="Delete Category", fg_color="#00aaff", font=('calibri', 18), command=delete_selected_category)

        self.subcategory_text_box_in_category_menu = ctk.CTkTextbox(self.context_category, height=50)
        #keep track of text box focus
        self.subcategory_text_box_in_category_menu_focus = 0

        def return_pressed_in_category_menu_subcategory_text_box(event=""):
            if self.subcategory_text_box_in_category_menu.get("1.0", "end-1c") == "":
                self.subcategory_text_box_in_category_menu.delete("0.0", "end")
                self.subcategory_text_box_in_category_menu.mark_set("insert", "0.0")
            if self.subcategory_text_box_in_category_menu.get("1.0", "end-1c") != "":
                self.template_editor.insert(self.template_editor.focus(), tk.END, text=self.subcategory_text_box_in_category_menu.get("1.0", "end-1c"), values=(1))
                self.template_editor.item(self.template_editor.focus(), open=True)
                self.template_editor.selection_set(self.template_editor.get_children(self.template_editor.focus())[-1]) 
                self.template_editor.focus(self.template_editor.get_children(self.template_editor.focus())[-1]) 
                self.subcategory_text_box_in_category_menu.delete("0.0", "end")
                self.subcategory_text_box_in_category_menu.mark_set("insert", "0.0")
            return "break"   
        
        def update_category_menu_subcategory_textbox_focus(event):
            if self.subcategory_text_box_in_category_menu_focus == 0:
                self.subcategory_text_box_in_category_menu_focus = 1
                self.subcategory_text_box_in_category_menu.bind("<Return>", return_pressed_in_category_menu_subcategory_text_box)
            elif self.subcategory_text_box_in_category_menu_focus == 1:
                self.subcategory_text_box_in_category_menu_focus = 0
                self.subcategory_text_box_in_category_menu.unbind("<Return>")
        
        self.subcategory_text_box_in_category_menu.bind("<FocusIn>", update_category_menu_subcategory_textbox_focus)
        self.subcategory_text_box_in_category_menu.bind("<FocusOut>", update_category_menu_subcategory_textbox_focus)
        
        self.add_subcategory_button = ctk.CTkButton(self.context_category, text="Add New Sub-Category", fg_color="#00aaff", font=('calibri', 16), command=return_pressed_in_category_menu_subcategory_text_box)
        
        #sub-category selected
        self.context_subcategory = ctk.CTkFrame(self)
        self.subcategory_label = ctk.CTkLabel(self.context_subcategory, text="Sub-category Selected", text_color='#ffffff')
        self.subcategory_textbox = ctk.CTkTextbox(self.context_subcategory, height=50)

        def rename_subcategory(event=""):
            self.template_editor.item(self.template_editor.focus(), text=self.subcategory_textbox.get("1.0", "end-1c"))
            return 'break'
        
        self.subcategory_textbox_focus = 0

        def update_subcategory_textbox_focus(event):
            if self.subcategory_textbox_focus == 0:
                self.subcategory_textbox_focus = 1
                self.subcategory_textbox.bind("<Return>", rename_subcategory)
            elif self.subcategory_textbox_focus == 1:
                self.subcategory_textbox_focus = 0
                self.subcategory_textbox.unbind("<Return>")
        
        self.subcategory_textbox.bind("<FocusIn>", update_subcategory_textbox_focus)
        self.subcategory_textbox.bind("<FocusOut>", update_subcategory_textbox_focus)

        self.rename_subcategory_button = ctk.CTkButton(self.context_subcategory, text="Rename", fg_color="#00aaff", font=('calibri', 18), command=rename_subcategory)

        def move_subcategory_up():
            current_subcategory_pos = self.template_editor.index(self.template_editor.focus())
            self.template_editor.move(self.template_editor.focus(), self.template_editor.parent(self.template_editor.focus()), current_subcategory_pos-1)

        def move_subcategory_down():
            current_subcategory_pos = self.template_editor.index(self.template_editor.focus())
            self.template_editor.move(self.template_editor.focus(), self.template_editor.parent(self.template_editor.focus()), current_subcategory_pos+1)

        self.moveup_subcategory_button = ctk.CTkButton(self.context_subcategory, text="Move Up", fg_color="#00aaff", font=('calibri', 18), command=move_subcategory_up)
        self.movedown_subcategory_button = ctk.CTkButton(self.context_subcategory, text="Move Down", fg_color="#00aaff", font=('calibri', 18), command=move_subcategory_down)
        
        def delete_selected_subcategory():
            self.template_editor.delete(self.template_editor.focus())

        self.delete_subcategory_button = ctk.CTkButton(self.context_subcategory, text="Delete Sub-category", fg_color="#00aaff", font=('calibri', 18), command=delete_selected_subcategory)

        self.monthly_annual = ctk.IntVar()
        def monthly_annual_checkbox_status():
            self.template_editor.item(self.template_editor.focus(), values=self.monthly_annual.get())

        self.subcategory_annual_checkbox= ctk.CTkCheckBox(self.context_subcategory, text="Annual", fg_color="#00aaff", font=('calibri', 18), onvalue=2, offvalue=1, variable=self.monthly_annual, command=monthly_annual_checkbox_status)

        #intro message
        self.context_intro_message = ctk.CTkFrame(self)
        self.intro_message_label = ctk.CTkLabel(self.context_intro_message, text="To Edit Budget,\n Select a Component\n from the Menu")
        #save button
        self.save_button_frame = ctk.CTkFrame(self)

        def save_template():  
            new_template = {"Title" : "temporary title"}
            for incexp in self.template_editor.get_children():
                new_template[self.template_editor.item(incexp).get("text")] = "categories"
                category = {}
                for cat in self.template_editor.get_children(item=incexp):
                    category[self.template_editor.item(cat).get("text")] = "list of lists"
                    subcategories_and_annual = []
                    subcategories = []
                    annual = []
                    for subcat in self.template_editor.get_children(item=cat):
                        subcategories.append(self.template_editor.item(subcat).get("text"))
                        annual.append(self.template_editor.item(subcat).get("values")[0])
                    subcategories_and_annual.append(subcategories)
                    subcategories_and_annual.append(annual)
                    category[self.template_editor.item(cat).get("text")] = subcategories_and_annual
                new_template[self.template_editor.item(incexp).get("text")] = category 
            save_template_window=SaveWindow(self, save_object_type="Save Template", save_object_title=self.template_title, save_object=self.template_list, new_template=new_template)
            save_template_window.focus()
            save_template_window.grab_set()

        self.save_template_button = ctk.CTkButton(self.save_button_frame, text="Save Template", fg_color="#00aaff", font=('calibri', 18), command=save_template)

        #layout
        #page labels
        self.edit_template_label.place(relx=0.5, rely=0, anchor='n')
        self.template_title_label.place(relx=0.5, rely=0.1, anchor='n')
        
        #main frame: the template
        self.budget_template_frame.place(relx=0.08, rely=0.2, relwidth=0.65, relheight=0.80, anchor='nw')
        self.template_editor.pack(expand=True, fill='both', padx=10, pady=10)
        
        #secondary frame: contextual menu
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
        #intro message
        self.context_intro_message.place(relx=0.74, rely=0.2, relwidth=0.18, relheight=0.70, anchor='nw')
        self.intro_message_label.pack()
        #save button
        self.save_button_frame.place(relx=0.74, rely=0.92, relwidth=0.18, relheight=0.08, anchor='nw')
        self.save_template_button.pack(padx=5, pady=5, expand=True, fill='both')

        #bind treeview selection events
        def raise_context_menu(event):
            #income or expense selected
            if self.template_editor.item(self.template_editor.parent(self.template_editor.focus())).get("text") == "":
                self.context_income_expense.tkraise()
                self.income_expense_label.configure(text=self.template_editor.item(self.template_editor.focus()).get("text") + " Selected")
            #category selected
            if self.template_editor.item(self.template_editor.parent((self.template_editor.parent(self.template_editor.focus())))).get("text") == "" and self.template_editor.item(self.template_editor.parent(self.template_editor.focus())).get("text") != "":
                self.context_category.tkraise()
                if self.category_text_box_in_category_menu.get("1.0", "end-1c") != "":
                    self.category_text_box_in_category_menu.delete("0.0", "end")
                    self.category_text_box_in_category_menu.mark_set("insert", "0.0")
                self.category_text_box_in_category_menu.insert('0.0', self.template_editor.item(self.template_editor.focus()).get("text"))
            #subcategory selected
            if self.template_editor.item(self.template_editor.parent((self.template_editor.parent(self.template_editor.focus())))).get("text") != "":
                self.context_subcategory.tkraise()
                if self.subcategory_textbox.get("1.0", "end-1c") != "":
                    self.subcategory_textbox.delete("0.0", "end")
                    self.subcategory_textbox.mark_set("insert", "0.0")
                self.subcategory_textbox.insert('0.0', self.template_editor.item(self.template_editor.focus()).get("text"))
                if self.template_editor.item(self.template_editor.focus()).get("values")[0] == 1:
                    self.subcategory_annual_checkbox.deselect()
                if self.template_editor.item(self.template_editor.focus()).get("values")[0] == 2:
                    self.subcategory_annual_checkbox.select()
           
        self.template_editor.bind("<<TreeviewSelect>>", raise_context_menu)

    def display_template_and_title(self, template_title, template_list): 
        self.template_displayed = 1
        self.template_title_label.configure(text="Selected Template: " + template_title)
        self.income_section = self.template_editor.insert("", 0, text="Income", open=True)
        self.expenses_section = self.template_editor.insert("", 2, text="Expenses", open=True)
        for template in template_list:
            if template.get("Title") == template_title:
                self.display_template_title_income(template.get("Income"))
                self.display_template_title_expenses(template.get("Expenses"))
        self.context_intro_message.tkraise()
        self.template_list = template_list
        self.template_title = template_title
           
    def display_template_title_income(self, income):
        for category in income.keys():
            income_category_id = self.template_editor.insert(self.income_section, tk.END, text=category)
            for subcat, monthly in zip(income.get(category)[0], income.get(category)[1]):
                self.template_editor.insert(income_category_id, tk.END, text=subcat, values=monthly)

    def display_template_title_expenses(self, expenses):
        for category in expenses.keys():
            expense_category_id = self.template_editor.insert(self.expenses_section, tk.END, text=category) 
            for subcat, monthly in zip(expenses.get(category)[0], expenses.get(category)[1]): 
                self.template_editor.insert(expense_category_id, tk.END, text=subcat, values=monthly)

    def set_treeview_style_template_editor(self):
        self.bg_color = self.budget_template_frame._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        self.selected_color = self.budget_template_frame._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.text_color = self.budget_template_frame._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])

        self.template_editor_style = ttk.Style()
        self.template_editor_style.theme_use('default')
        self.template_editor_style.configure("Treeview", fieldbackground=self.bg_color, background=self.bg_color, foreground=self.text_color, font=('calibri', 15), borderwidth=0, rowheight=23)
        self.template_editor_style.map("Treeview", background=[("selected", self.bg_color)], foreground=[("selected", self.selected_color)]) 
    
    def clear_template(self):   
        if self.template_displayed == 1:
            self.template_editor.delete(self.income_section)
            self.template_editor.delete(self.expenses_section)
            self.template_displayed = 0  

class EnterBudgetAmounts(ctk.CTkFrame):
    def __init__(self, parent, main_menu_frame, scaling_factor):
        super().__init__(master=parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)    
        self.grid_rowconfigure(1, weight=50) 

        #main menu is accessible from this class
        self.mainmenu = main_menu_frame

        #widgets
        self.enter_budget_amounts_label = ctk.CTkLabel(self, text="Enter your Monthly and Annual Budget Amounts", text_color="#00aaff", font=('calibri', 35))
        
        self.budget_table_frame = ctk.CTkFrame(self)
        
        self.budget_displayed = 0 #indicator: budget is displayed in table
        self.budget_table = ttk.Treeview(self.budget_table_frame, columns=('category', 'annual', 'monthly'), show='headings', style="Treeview")
        self.budget_table.heading('category', text="Budget Category")
        self.budget_table.heading('annual', text="Annual Amount")
        self.budget_table.heading('monthly', text="Monthly Amount")
        self.budget_table.column('annual', anchor='center')
        self.budget_table.column('monthly', anchor='center')

        def budget_table_double_click(event):
            if self.budget_table.item(self.budget_table.parent(self.budget_table.parent(self.budget_table.focus()))).get("values") == "":
                return "break" #Do nothing, user selected non-selectable cell (not a subcategory)
            if self.budget_table.item(self.budget_table.parent(self.budget_table.parent(self.budget_table.focus()))).get("values") != "": 
                self.row = self.budget_table.identify_row(event.y)
                self.row_data = self.budget_table.item(self.row).get("values")
                if self.budget_table.item(self.row).get("values")[3] == 2: #annual subcat clicked 
                    box_location_annual = self.budget_table.bbox(self.row, column="#2")
                    box_location_annual = (
                        int(box_location_annual[0] / scaling_factor),
                        int(box_location_annual[1] / scaling_factor),
                        int(box_location_annual[2] / scaling_factor),
                        int(box_location_annual[3] / scaling_factor)
                    )
                    self.annual = True
                    self.budget_entry = ctk.CTkEntry(self.budget_table, width=box_location_annual[2], height=box_location_annual[3])
                    self.budget_entry.place(x=box_location_annual[0], y=box_location_annual[1])
                    self.budget_entry.focus()
                    self.budget_entry.bind("<Return>", update_budget_table_entry)
                    self.budget_entry.bind("<FocusOut>", update_budget_table_entry)
                if self.budget_table.item(self.row).get("values")[3] == 1: #monthly subcat clicked
                    box_location_monthly = self.budget_table.bbox(self.row, column="#3")
                    box_location_monthly = (
                        int(box_location_monthly[0] / scaling_factor),
                        int(box_location_monthly[1] / scaling_factor),
                        int(box_location_monthly[2] / scaling_factor),
                        int(box_location_monthly[3] / scaling_factor)
                    )
                    self.annual = False
                    self.budget_entry = ctk.CTkEntry(self.budget_table, width=box_location_monthly[2], height=box_location_monthly[3])
                    self.budget_entry.place(x=box_location_monthly[0], y=box_location_monthly[1])
                    self.budget_entry.focus()
                    self.budget_entry.bind("<Return>", update_budget_table_entry)
                    self.budget_entry.bind("<FocusOut>", update_budget_table_entry)
            return "break"

        def update_budget_table_entry(event):
            if self.annual == True:
                try:
                    self.row_data[1] = '${:,.2f}'.format(float(self.budget_entry.get())) 
                    self.budget_table.item(self.row, values=self.row_data)
                except ValueError:
                    self.budget_entry.destroy() #either box was empyty or user entered non-number
                    return
            elif self.annual == False:
                try:
                    self.row_data[2] = '${:,.2f}'.format(float(self.budget_entry.get()))
                    self.budget_table.item(self.row, values=self.row_data)
                except ValueError:
                    self.budget_entry.destroy()
                    return
            self.budget_entry.destroy()
            
        self.budget_table.bind("<Double-1>", budget_table_double_click)

        #layout
        self.enter_budget_amounts_label.grid(row=0, column=0, sticky='new')

        self.budget_table_frame.grid(row=1, column=0, padx=80, sticky='nsew')
        self.budget_table.pack(expand=True, fill='both', padx=5, pady=5)
    #these functions trigger when comming to this page from template editor

    def display_budget_table(self, budget_template):
        self.budget_displayed = 1
        for inc_exp in budget_template.get_children():
            inc_exp_id = self.budget_table.insert("", tk.END, values=(budget_template.item(inc_exp).get("text"), "", ""), open=True)
            self.budget_table.tag_configure(inc_exp_id, font=("Calibri", 18, "underline"))
            self.budget_table.item(inc_exp_id, tags=(inc_exp_id,))
            for cat in budget_template.get_children(item=inc_exp):
                cat_id = self.budget_table.insert(inc_exp_id, tk.END, values=(budget_template.item(cat).get("text"), "----------", "----------"), open=True)
                self.budget_table.tag_configure(cat_id, font=("Calibri", 18, "bold"))
                self.budget_table.item(cat_id, tags=(cat_id,))
                for subcat in budget_template.get_children(item=cat):
                    if budget_template.item(subcat).get("values")[0] == 1:
                        subcat_id = self.budget_table.insert(cat_id, tk.END, values=(budget_template.item(subcat).get("text"),"----------","", 1), open=True)
                    if budget_template.item(subcat).get("values")[0] == 2:
                        subcat_id = self.budget_table.insert(cat_id, tk.END, values=(budget_template.item(subcat).get("text"),"","----------", 2), open=True)
                    self.budget_table.tag_configure(subcat_id, font=("Calibri", 15))
                    self.budget_table.item(subcat_id, tags=(subcat_id,))

    def set_treeview_style_table(self):
        self.bg_color_table = self.budget_table_frame._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        self.selected_color_table = self.budget_table_frame._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.text_color_table = self.budget_table_frame._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])

        self.template_table_style = ttk.Style(self)
        self.template_table_style.theme_use('default')
        self.template_table_style.configure("Treeview", fieldbackground="#343434", background="#343434", foreground="#ffffff", font=('calibri', 15), borderwidth=0, rowheight=28)
        self.template_table_style.configure("Treeview.Heading", borderwidth=1, relief="ridge", background="#343434", foreground="#ffffff", font=('calibri', 15))
        self.template_table_style.map("Treeview", background=[("selected", "#303030")], foreground=[("selected", self.selected_color_table)])
    #these functions trigger when hitting 'continue' button
    def check_budget_table(self):
        self.blank_cells_found_error_occured = False
        self.blank_annuals = []
        self.blank_monthlies = []
        for inc_exp in self.budget_table.get_children(): #consider using identify_row(y) if loop thru all y's is doable, may require interaction with .index(item)
            for cat in self.budget_table.get_children(inc_exp):
                for subcat in self.budget_table.get_children(cat):
                    if self.budget_table.item(subcat).get("values")[3] == 2 and self.budget_table.item(subcat).get("values")[1] == "":
                        self.blank_annuals.append(self.budget_table.item(subcat).get("values")[0])                     
                    if self.budget_table.item(subcat).get("values")[3] == 1 and self.budget_table.item(subcat).get("values")[2] == "":
                        self.blank_monthlies.append(self.budget_table.item(subcat).get("values")[0])
        if self.blank_annuals != [] or self.blank_monthlies != []:
            self.blank_cells_found_error()
        if self.blank_annuals == [] and self.blank_monthlies == []:
            self.account_selection()

    def blank_cells_found_error(self):
        self.blank_cells_warning_window = ctk.CTkToplevel()
        self.blank_cells_warning_window.title("Blank Budget Categories")
        self.blank_cells_warning_window.geometry("500x250")
        self.blank_cells_warning_window.focus()
        self.blank_cells_warning_window.grab_set()
        self.blank_cells_warning_window.grid_columnconfigure((0, 1), weight=1, uniform='a')
        self.blank_cells_warning_window.grid_rowconfigure(0, weight=1)
        self.blank_cells_warning_window.grid_rowconfigure(1, weight=50)
        self.blank_cells_warning_window.grid_rowconfigure(2, weight=1)

        #variable indicating that blank cells warning occured
        self.blank_cells_found_error_occured = True

        #widgets
        blank_cells_message = ctk.CTkLabel(self.blank_cells_warning_window, text="Some of Your Budget Categories Have No Assigned Values.\nDo You Want to Proceed Anyway?", text_color="#00aaff", font=('calibri', 12))
        
        blank_annual_scrolling_frame = ctk.CTkScrollableFrame(self.blank_cells_warning_window)
        blank_annual_scrolling_frame.grid_columnconfigure(0, weight=1)
        blank_annual_scrolling_frame.grid_rowconfigure(0, weight=1, pad=0)
        for index, cell in enumerate(self.blank_annuals):
            blank_annual_list_title = ctk.CTkLabel(blank_annual_scrolling_frame, text="Annual", font=("calibri", 20, "underline"))
            blank_annual_list_title.grid(row=0, column=0)
            blank_annual_list = ctk.CTkLabel(blank_annual_scrolling_frame, text=cell)
            blank_annual_list.grid(row=1+index, column=0)

        blank_monthly_scrolling_frame = ctk.CTkScrollableFrame(self.blank_cells_warning_window)
        blank_monthly_scrolling_frame.grid_columnconfigure(0, weight=1)
        blank_monthly_scrolling_frame.grid_rowconfigure(0, weight=1)
        for index, cell in enumerate(self.blank_monthlies):
            blank_monthlies_list_title = ctk.CTkLabel(blank_monthly_scrolling_frame, text="Monthly", font=("calibri", 20, "underline"))
            blank_monthlies_list_title.grid(row=0, column=0)
            blank_monthlies_list = ctk.CTkLabel(blank_monthly_scrolling_frame, text=cell)
            blank_monthlies_list.grid(row=1+index, column=0, pady=0)
        
        blank_cells_cancel = ctk.CTkButton(self.blank_cells_warning_window, text="Cancel", fg_color="#00aaff", font=("calibri", 18), command=lambda: self.blank_cells_warning_window.destroy())
        blank_cells_confirm = ctk.CTkButton(self.blank_cells_warning_window, text="Confirm", fg_color="#00aaff", font=("calibri", 18), command=self.fill_empty_cells_with_0)

        #layout
        blank_cells_message.grid(row=0, column=0, columnspan=2, sticky="new") 

        blank_annual_scrolling_frame.grid(row=1, column=0, padx=(10, 5), pady=(10, 0), sticky="nsew")
        blank_monthly_scrolling_frame.grid(row=1, column=1, padx=(0, 10), pady=(10, 0), sticky="nsew")

        blank_cells_cancel.grid(row=2, pady=10, column=0)
        blank_cells_confirm.grid(row=2, pady=10, column=1)
    
    def fill_empty_cells_with_0(self):
        for inc_exp in self.budget_table.get_children(): #consider using identify_row(y) if loop thru all y's is doable, may require interaction with .index(item)
            for cat in self.budget_table.get_children(inc_exp):
                for subcat in self.budget_table.get_children(cat):
                    if self.budget_table.item(subcat).get("values")[3] == 2 and self.budget_table.item(subcat).get("values")[1] == "":
                        annual_row_with_0 = self.budget_table.item(subcat).get("values")
                        annual_row_with_0[1] = '${:,.2f}'.format(float(0.00))   
                        self.budget_table.item(subcat, values=annual_row_with_0)     
                    if self.budget_table.item(subcat).get("values")[3] == 1 and self.budget_table.item(subcat).get("values")[2] == "":
                        self.blank_monthlies.append(self.budget_table.item(subcat).get("values")[0])
                        monthly_row_with_0 = self.budget_table.item(subcat).get("values")
                        monthly_row_with_0[2] = '${:,.2f}'.format(float(0.00))   
                        self.budget_table.item(subcat, values=monthly_row_with_0)
        self.account_selection()                           

    def account_selection(self):
        if self.blank_cells_found_error_occured == True:
            self.blank_cells_warning_window.destroy() 
        self.account_selection_window = ctk.CTkToplevel()
        self.account_selection_window.title("Select Accounts")
        self.account_selection_window.geometry("800x450")
        self.account_selection_window.focus()
        self.account_selection_window.grab_set()
        self.account_selection_window.grid_columnconfigure((0,1), weight=1, uniform='a')
        self.account_selection_window.grid_rowconfigure((0,1,2,3,4), weight=1)
        self.account_selection_window.grid_rowconfigure(5, weight=50)
        self.account_selection_window.grid_rowconfigure(6, weight=20)

        #variables
        self.default_account_list = ["All Accounts", "Chequing", "Savings", "Money Market Account", "Credit Card", "Line of Credit"]

        #widgets
        account_selection_message_0 = ctk.CTkLabel(self.account_selection_window, text="One Last Step...", text_color="#00aaff", font=('calibri', 18))
        account_selection_message_1 = ctk.CTkLabel(self.account_selection_window, text="-If you want to keep track of expenses across more than one account, select the account types from the list below.", text_color="#00aaff", font=('calibri', 15))
        account_selection_message_2 = ctk.CTkLabel(self.account_selection_window, text="-You can also add one if it is not in the provided list (not implemented).", text_color="#00aaff", font=('calibri', 15))
        account_selection_message_3 = ctk.CTkLabel(self.account_selection_window, text="-For each account selected, there will be an additional column in your budget for each month (So don't add too many!).", text_color="#00aaff", font=('calibri', 15))
        account_selection_message_4 = ctk.CTkLabel(self.account_selection_window, text="-If you are new to budgeting \"All Accounts\" is recommended.", text_color="#00aaff", font=('calibri', 15))

        def user_selects_account(): 
            box_checked = False
            for box in self.account_selection_checkbox_list[1:6]:
                if box.get() == 0:
                    box_checked = False
                if box.get() == 1:
                    box_checked = True
                    break
            if self.account_selection_checkbox_list[0].cget("state") == "normal" and box_checked == True:
                self.account_selection_checkbox_list[0].deselect()
                self.account_selection_checkbox_list[0].configure(state=ctk.DISABLED)
            elif self.account_selection_checkbox_list[0].cget("state") == "disabled" and box_checked == False: 
                self.account_selection_checkbox_list[0].configure(state=ctk.NORMAL) 
                self.account_selection_checkbox_list[0].select()
        
        def not_checkable():
            self.account_selection_checkbox_list[0].select()

        account_selection_checklist_frame = ctk.CTkScrollableFrame(self.account_selection_window)
        account_selection_checklist_frame.grid_columnconfigure(0, weight=1)
        account_selection_checklist_frame.grid_rowconfigure(0, weight=1)
        self.account_selection_checkbox_list = []
        for index, account  in enumerate(self.default_account_list):
            if index == 0:
                account_selection_checkbox = ctk.CTkCheckBox(account_selection_checklist_frame, text=account, command=not_checkable)
                account_selection_checkbox.select()
            else:
                account_selection_checkbox = ctk.CTkCheckBox(account_selection_checklist_frame, text=account, command=user_selects_account)
            account_selection_checkbox.grid(row=0+index, column=0, sticky="wn", pady=5, padx=5)
            self.account_selection_checkbox_list.append(account_selection_checkbox)
        
        self.cancel_account_selection_button = ctk.CTkButton(self.account_selection_window, text="Cancel", fg_color="#00aaff", font=("calibri", 22), command=lambda: self.account_selection_window.destroy())
        self.confirm_account_selection_button = ctk.CTkButton(self.account_selection_window, text="Confirm", fg_color="#00aaff", font=("calibri", 22), command=self.account_selection_confirmed)
        #NOTE when user entry of new accounts is implemented: define a function that appends that account name to self.account_selection_checkbox_list

        #layout
        account_selection_message_0.grid(row=0, column=0, columnspan=2, padx=30, pady=0, ipady=0, sticky="n")
        account_selection_message_1.grid(row=1, column=0, columnspan=2, padx=30, pady=0, ipady=0, sticky="nw")
        account_selection_message_2.grid(row=2, column=0, columnspan=2, padx=30, pady=0, ipady=0, sticky="nw")
        account_selection_message_3.grid(row=3, column=0, columnspan=2, padx=30, pady=0, ipady=0, sticky="nw")
        account_selection_message_4.grid(row=4, column=0, columnspan=2, padx=30, pady=0, ipady=0, sticky="nw")

        account_selection_checklist_frame.grid(row=5, column=0, columnspan=2, padx=40, sticky="nsew")

        self.cancel_account_selection_button.grid(row=6, column=0, padx=40, pady=10, sticky="nsw")
        self.confirm_account_selection_button.grid(row=6, column=1, padx=40, pady=10, sticky="nse")

    def account_selection_confirmed(self):
        self.selected_accounts = []
        for account in self.account_selection_checkbox_list:
            if account.get() == 1:
                self.selected_accounts.append(account.cget("text"))
        self.save_budget()

    def save_budget(self):
        self.account_selection_window.destroy()
        self.save_budget_window = ctk.CTkToplevel()
        self.save_budget_window.title("Save Budget")
        self.save_budget_window.geometry("300x150")
        self.save_budget_window.focus()
        self.save_budget_window.grab_set()
        self.save_budget_window.grid_columnconfigure((0, 1), weight=1, uniform='a')
        self.save_budget_window.grid_rowconfigure(0, weight=1)
        self.save_budget_window.grid_rowconfigure(1, weight=50)
        self.save_budget_window.grid_rowconfigure(2, weight=1)

        #widgets
        ask_for_filename_message = ctk.CTkLabel(self.save_budget_window, text="Enter a Title for Your Budget", text_color="#00aaff", font=('calibri', 18))
        
        self.budget_name = ctk.StringVar()
        budget_name_entry = ctk.CTkEntry(self.save_budget_window, textvariable=self.budget_name)
        
        cancel_budget_saving = ctk.CTkButton(self.save_budget_window, text="Cancel", fg_color="#00aaff", font=("calibri", 18), command=lambda: self.save_budget_window.destroy())
        save_budget = ctk.CTkButton(self.save_budget_window, text="Save", fg_color="#00aaff", font=("calibri", 18), command=self.check_if_file_exists)

        #layout
        ask_for_filename_message.grid(row=0, column=0, columnspan=2, sticky='snew')

        budget_name_entry.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10)

        cancel_budget_saving.grid(row=2, column=0, padx=5, pady=10, sticky="n")
        save_budget.grid(row=2, column=1, padx=5, pady=10, sticky="n")

        #event binding
        budget_name_entry.bind("<Return>", command=self.check_if_file_exists)

    def check_if_file_exists(self, event=None):
        if self.budget_name.get() == "":
            return
        if self.budget_name.get() != "":
            self.save_budget_window.destroy()
            self.file_exists_warning_occured = False
            self.path = os.getcwd()
            self.path = self.path + "\\" + self.budget_name.get() + ".sqlite"
            file_exists = os.path.isfile(self.path)
            if file_exists == False:
                self.save_budget_to_database()
            if file_exists == True:
                self.file_exists_warning()

    def file_exists_warning(self):
        self.file_exists_warning_window = ctk.CTkToplevel()
        self.file_exists_warning_window.title("Budget File Already Exists")
        self.file_exists_warning_window.geometry("350x130")
        self.file_exists_warning_window.focus()
        self.file_exists_warning_window.grab_set()
        self.file_exists_warning_window.grid_columnconfigure((0, 1), weight=1, uniform='a')
        self.file_exists_warning_window.grid_rowconfigure(0, weight=1)
        self.file_exists_warning_window.grid_rowconfigure(1, weight=1)

        #variable indicating that warning occured
        self.file_exists_warning_occured = True

        #widgets
        file_exists_message = ctk.CTkLabel(self.file_exists_warning_window, text="A File with that Name Already Exists.\nDo You Want to Overwrite It?", text_color="#00aaff", font=('calibri', 12))
        cancel_save_budget = ctk.CTkButton(self.file_exists_warning_window, text="Cancel", fg_color="#00aaff", font=("calibri", 18), command=lambda : self.file_exists_warning_window.destroy())
        confirm_overwrite_budget = ctk.CTkButton(self.file_exists_warning_window, text="Overwrite", fg_color="#00aaff", font=("calibri", 18), command=self.save_budget_to_database)

        #layout
        file_exists_message.grid(row=0, column=0, columnspan=2, pady=10, sticky="sew")
        cancel_save_budget.grid(row=1, column=0, padx=5, pady=10, sticky="n")
        confirm_overwrite_budget.grid(row=1, column=1, padx=5, pady=10, sticky="n")

    def save_budget_to_database(self):
        if self.file_exists_warning_occured == True:
            self.file_exists_warning_window.destroy()
            os.remove(self.path)
        conn = sqlite3.connect(self.budget_name.get() + ".sqlite")
        cur = conn.cursor()

        cur.executescript('''
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

        ''')#date take form yyyy-mm-dd will likely need to be created from user input for each

        conn.commit()
        #output budget to database
        cur.execute('''INSERT OR IGNORE INTO [Monthly Annual] ([Monthly/Annual]) Values ('Monthly') ''')
        cur.execute('''INSERT OR IGNORE INTO [Monthly Annual] ([Monthly/Annual]) Values ('Annual') ''')

        for inc_exp in self.budget_table.get_children():
            income_expense_section = self.budget_table.item(inc_exp).get("values")[0]
            cur.execute('''INSERT OR IGNORE INTO [Income Expense] ([Income/Expense]) Values (?)''', (income_expense_section, ))
            for cat in self.budget_table.get_children(inc_exp):
                if income_expense_section == "Income":
                    income_expense_id = 1
                if income_expense_section == "Expenses":
                    income_expense_id = 2
                budget_category = self.budget_table.item(cat).get("values")[0]
                cur.execute('''INSERT OR IGNORE INTO [Category Name] ([Category], Income_expense_id) Values (?, ?)''', (budget_category, income_expense_id))
                conn.commit()
                cur.execute('''SELECT id FROM [Category Name] WHERE Category = ?''', (budget_category,))
                cat_id = cur.fetchone()[0]
                for subcat in self.budget_table.get_children(cat):
                    budget_subcategory_name = self.budget_table.item(subcat).get("values")[0]
                    budget_subcategory_annual_monthly = self.budget_table.item(subcat).get("values")[3]
                    budget_subcategory_amount = 0
                    if budget_subcategory_annual_monthly == 2: #subcat is annual
                        budget_subcategory_amount = self.budget_table.item(subcat).get("values")[1]
                    if budget_subcategory_annual_monthly == 1: #subcat is monthly
                        budget_subcategory_amount = self.budget_table.item(subcat).get("values")[2]
                    cur.execute('''INSERT OR IGNORE INTO [Sub-Category Name] ([Sub-Category], [Category_Name_id], [Monthly_annual_id]) VALUES (?, ?, ?)''', (budget_subcategory_name, cat_id, budget_subcategory_annual_monthly))
                    conn.commit()
                    cur.execute('''SELECT id FROM [Sub-Category Name] WHERE ([Sub-Category], [Category_Name_id]) = (?, ?)''', (budget_subcategory_name, cat_id))
                    subcat_id = cur.fetchone()[0]
                    cur.execute('''INSERT INTO [Budget Amounts] (Amount, [Sub_Category_id], [Category_id]) VALUES (?, ?, ?)''', (budget_subcategory_amount, subcat_id, cat_id))
        conn.commit()
        
        #output selected accounts to db
        for account in self.selected_accounts:
            cur.execute('''INSERT OR IGNORE INTO Accounts ([Account Name]) VALUES (?)''', (account, ))
        conn.commit()
        conn.close

        #confirm budget saved
        budget_confirmed = os.path.isfile(self.path)
        if budget_confirmed == False:
            self.save_budget_failed_window = ctk.CTkToplevel()
            self.save_budget_failed_window.title("Save Confirmation Failed")
            self.save_budget_failed_window.geometry("310x150")
            self.save_budget_failed_window.focus()
            self.save_budget_failed_window.grab_set()

            #widgets
            save_budget_failed_message = ctk.CTkLabel(self.save_budget_failed_window, text="Budget Save Could Not be Confirmed.", text_color="#00aaff", font=('calibri', 15))
            save_budget_failed_message_foldercheck = ctk.CTkLabel(self.save_budget_failed_window, text="Please Double Check File Permissions\nOr, Attempt saving to a Different Directory", text_color="#00aaff", font=('calibri', 12))
            save_budget_failed_message_report = ctk.CTkLabel(self.save_budget_failed_window, text="If the Issue Persists, Please File a Bug Report", text_color="#00aaff", font=('calibri', 12))
            ok_button = ctk.CTkButton(self.save_budget_failed_window, text="Ok", fg_color="#00aaff", font=("calibri", 18), command=lambda : self.save_budget_failed_window.destroy())

            #layout
            save_budget_failed_message.pack()
            save_budget_failed_message_foldercheck.pack(pady=5)
            save_budget_failed_message_report.pack()
            ok_button.pack(pady=10)
        
        if budget_confirmed == True:
            self.save_budget_success_window = ctk.CTkToplevel()
            self.save_budget_success_window.title("Save Confirmed")
            self.save_budget_success_window.geometry("440x100")
            self.save_budget_success_window.focus()
            self.save_budget_success_window.grab_set()
            self.save_budget_success_window.grid_columnconfigure((0,1), weight=1, uniform='a')
            self.save_budget_success_window.grid_rowconfigure(0, weight=1)
            self.save_budget_success_window.grid_rowconfigure(1, weight=10)

            #widgets
            save_budget_success_message = ctk.CTkLabel(self.save_budget_success_window, text="Budget Save Confirmed!.", text_color="#00aaff", font=('calibri', 20))
            
            return_to_mainmenu_button = ctk.CTkButton(self.save_budget_success_window, text="Return to Main Menu", fg_color="#00aaff", font=("calibri", 18), command=self.return_to_mainmenu)
            manage_new_budget_button = ctk.CTkButton(self.save_budget_success_window, text="Manage Your New Budget", fg_color="#00aaff", font=("calibri", 18), command=lambda: print("this will send user to manage budget system"))

            #layout
            save_budget_success_message.grid(row=0, column=0, columnspan=2, sticky="sew", pady=5)
            return_to_mainmenu_button.grid(row=1, column=0, sticky="new", padx=5, pady=5)
            manage_new_budget_button.grid(row=1, column=1, sticky="new", padx=5, pady=5)

    def return_to_mainmenu(self):
        self.save_budget_success_window.destroy()
        self.clear_budget_table()
        self.mainmenu.tkraise()
    #this triggers when hitting 'back' button
    def clear_budget_table(self):
        if self.budget_displayed == 1:
            for inc_exp in self.budget_table.get_children():
                self.budget_table.delete(inc_exp)
            self.budget_displayed == 0

class ManageBudget(ctk.CTkFrame):
    def __init__(self, parent, main_menu_frame, add_new_button, edit_button):
        super().__init__(master=parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)    
        self.grid_rowconfigure(1, weight=50) 

        #so main menu is raisable from here and button panel accessable as well
        self.mainmenu = main_menu_frame
        self.add_new_button = add_new_button
        self.edit_button = edit_button

        #widgets
        self.manage_budget_label = ctk.CTkLabel(self, text="Manage Budget: no budget selected", text_color="#00aaff", font=('calibri', 24))
        self.manage_budget_table_frame = ctk.CTkFrame(self)
        
        self.tab_list = ["Annual", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "Yearly Total"]
        self.manage_budget_tabs = ttk.Notebook(self.manage_budget_table_frame)
        for tab in self.tab_list:
            self.tab = ttk.Frame(self.manage_budget_tabs)
            self.manage_budget_tabs.add(self.tab, text=tab)
    
        self.budget_displayed_in_manager = 0 #indicator: budget is displayed in table

        #functionality
        #track active tab, which sets active treeview, and bind single and double click on cell to current tab
        self.manage_budget_tabs.bind("<<NotebookTabChanged>>", self.set_active_treeview)
        
        #layout
        self.manage_budget_label.grid(row=0, column=0, sticky='new')
        self.manage_budget_table_frame.grid(row=1, column=0, padx=80, sticky='nsew')
        self.manage_budget_tabs.pack(expand=True, fill='both')

    def set_active_treeview(self, event):
        self.current_tab = self.manage_budget_tabs.index(self.manage_budget_tabs.select()) #index of current active treeview
        if self.budget_displayed_in_manager == 1: #bind click on cell only if budget is displayed
            self.treeview_list[self.current_tab].bind("<Button-1>", self.activate_budget_buttons)
            self.treeview_list[self.current_tab].bind("<Double-1>", self.manage_budget_double_click)
        if self.current_tab == 13:
            self.calculate_yearly_totals()
  
    def activate_budget_buttons(self, event):
        self.selected_column = int(self.treeview_list[self.current_tab].identify_column(event.x).strip("#"))
        self.selected_row_item = self.treeview_list[self.current_tab].identify_row(event.y)
        self.selected_row_complete = self.treeview_list[self.current_tab].item(self.selected_row_item)
        self.selected_row = self.selected_row_complete.get("values")
        if self.selected_row == "":
            return "break"
        if self.selected_row[0] == "Income" or self.selected_row[0] == "Expenses":
            self.add_new_button.configure(state='disabled')
            self.edit_button.configure(state='disabled')
        elif self.selected_row[2] == "-----":
            self.add_new_button.configure(state='disabled')
            self.edit_button.configure(state='disabled')
        elif len(self.budget_table_headings) == 3 and self.selected_column == 3: #no total column created
            self.add_new_button.configure(state='normal')
            self.edit_button.configure(state='normal')
        elif len(self.budget_table_headings) > 3 and self.selected_column > 2 and self.selected_column < len(self.budget_table_headings):
            self.add_new_button.configure(state='normal')
            self.edit_button.configure(state='normal')
        else:
            self.add_new_button.configure(state='disabled')
            self.edit_button.configure(state='disabled')

    def manage_budget_double_click(self, event):
        if self.selected_row == "":
            return "break"
        if self.selected_row[0] == "Income" or self.selected_row[0] == "Expenses":
            return "break"
        elif self.selected_row[2] == "-----":
            return "break"
        elif len(self.budget_table_headings) == 3 and self.selected_column == 3: #no total column created
            self.edit_button.invoke()
        elif len(self.budget_table_headings) > 3 and self.selected_column > 2 and self.selected_column < len(self.budget_table_headings):
            self.edit_button.invoke()

    #these functions trigger when coming to this page from budget file selection
    def display_budget_management_table(self, budget_filename):
        self.budget_filename = budget_filename
        self.budget_name = self.budget_filename.get().split(".")[0] #set label to filename
        self.manage_budget_label.configure(text="Manage Budget: " + self.budget_name)
        conn = sqlite3.connect(self.budget_filename.get()) 
        cur = conn.cursor()
        #Create treeviews, set cols and headings
        cur.execute("select Accounts.[Account Name], Accounts.id from Accounts")
        self.budget_accounts = cur.fetchall()
        self.budget_table_headings = ["", "Budget"]
        for account in self.budget_accounts:
            self.budget_table_headings.append(account[0])
        if len(self.budget_accounts) > 1:
            self.budget_table_headings.append("Total")
        self.treeview_list = []
        for i in self.tab_list:
            self.budget_table = ttk.Treeview(self.manage_budget_tabs.nametowidget(self.manage_budget_tabs.tabs()[self.tab_list.index(i)]), show='headings', style="Treeview")
            self.treeview_list.append(self.budget_table)
            self.budget_table.configure(columns=self.budget_table_headings)
            #bind treeview select to 0th treeview here using if cond
            for col in self.budget_table_headings:
                self.budget_table.heading(col, text=col)
                if self.budget_table_headings.index(col) == 0:
                    self.budget_table.column(col, stretch=True, width=200)
                else:
                    self.budget_table.column(col, stretch=True, width=50)
            self.budget_table.pack(expand=True, fill='both', pady=5, padx=5)
        self.display_budget_categories(self.treeview_list)

    def display_budget_categories(self, treeview_list):
        conn = sqlite3.connect(self.budget_filename.get()) 
        cur = conn.cursor()
        cur.execute("select [Income Expense].[Income/Expense], [Income Expense].id from [Income Expense]")
        income_expense = cur.fetchall()
        cur.execute("select [Category Name].Category, [Category Name].Income_expense_id, [Category Name].id from [Category Name]")
        categories = cur.fetchall()
        cur.execute('''select [Sub-Category Name].[Sub-Category], [Sub-Category Name].Monthly_annual_id, [Sub-Category Name].id, 
                    [Budget Amounts].Amount, [Budget Amounts].Sub_Category_id, [Budget Amounts].Category_id, [Budget Amounts].id
                    from [Sub-Category Name] join [Budget Amounts] on [Budget Amounts].Sub_Category_id = [Sub-Category Name].id''')
        subcategories_amounts_join = cur.fetchall()
        subcats_budgetamounts = []
        for entry in subcategories_amounts_join:
            subcats_budgetamounts.append([entry[0], entry[3], entry[5], entry[1], entry[2]]) #[subcat label, amount, category-id, monthly-annual, sub-cat-id]
        for table in treeview_list:
            for inc_exp in income_expense:
                income_expense_id = inc_exp[1]
                inc_exp_section = table.insert("", tk.END, values=(inc_exp[0], "", ""), open=True, tags=income_expense_id)                
                for category in categories:
                    if category[1] == income_expense_id:
                        budget_category_labels = [category[0]]
                        [budget_category_labels.append("-----") for i in range(1, len(self.budget_table_headings))]
                        category_id = category[2]
                        budget_category = table.insert(inc_exp_section, tk.END, values=(budget_category_labels), open=True, tags=category_id)
                        for subcat in subcats_budgetamounts:
                            subcat_id = subcat[4]
                            if table == treeview_list[0]: #annual tab
                                if subcat[2] == category_id and subcat[3] == 1: #monthly dashed out
                                    subcat_to_display = [subcat[0], subcat[1]]
                                    [subcat_to_display.append("-----") for i in range(2, len(self.budget_table_headings))]
                                    table.insert(budget_category, tk.END, values=(subcat_to_display), open=True, tags=subcat_id)
                                elif subcat[2] == category_id and subcat[3] == 2: #annual
                                    subcat_to_display = [subcat[0], subcat[1]]
                                    [subcat_to_display.append("") for i in range(2, len(self.budget_table_headings))]
                                    table.insert(budget_category, tk.END, values=(subcat_to_display), open=True, tags=subcat_id)
                            elif table == treeview_list[13] and subcat[2] == category_id: #yearly total tab
                                subcat_budget_value = (subcat[1].replace(",", "")).strip("$")
                                if subcat[3] == 1: 
                                    subcat_budget_value = (float(subcat_budget_value)) * 12
                                    subcat_budget_value = '${:,.2f}'.format(float(subcat_budget_value))
                                    subcat[1] = subcat_budget_value
                                yearly_subcat_to_display = [subcat[0], subcat[1]]
                                [yearly_subcat_to_display.append("") for i in range(2, len(self.budget_table_headings))]
                                table.insert(budget_category, tk.END, values=(yearly_subcat_to_display), open=True, tags=subcat_id) 
                            else: #monthly tabs
                                if subcat[2] == category_id and subcat[3] == 1: #monthly
                                    subcat_to_display = [subcat[0], subcat[1]]
                                    [subcat_to_display.append("") for i in range(2, len(self.budget_table_headings))] 
                                    table.insert(budget_category, tk.END, values=(subcat_to_display), open=True, tags=subcat_id)
                                elif subcat[2] == category_id and subcat[3] == 2: #annual dashed out
                                    subcat_to_display = [subcat[0], subcat[1]]
                                    [subcat_to_display.append("-----") for i in range(2, len(self.budget_table_headings))]
                                    table.insert(budget_category, tk.END, values=(subcat_to_display), open=True, tags=subcat_id)
        self.treeview_list[0].bind("<Button-1>", self.activate_budget_buttons)
        self.treeview_list[0].bind("<Double-1>", self.manage_budget_double_click)
        self.budget_displayed_in_manager = 1

        self.budget_structure = {}
        for incexp in self.treeview_list[0].get_children():
            incexp_text = self.treeview_list[0].item(incexp).get("values")[0]
            cat_subcat_dict = {}
            for cat in self.treeview_list[0].get_children(incexp):
                cat_text = self.treeview_list[0].item(cat).get("values")[0]
                subcat_list = []
                subcat_annual_monthly = []
                for subcat in self.treeview_list[0].get_children(cat):
                    subcat_list.append(self.treeview_list[0].item(subcat).get("values")[0])
                    if self.treeview_list[0].item(subcat).get("values")[2] == "": #annual
                        subcat_annual_monthly.append(2)
                    else:
                        subcat_annual_monthly.append(1)
                cat_subcat_dict[cat_text] = [subcat_list, subcat_annual_monthly]
            self.budget_structure[incexp_text] = cat_subcat_dict
            
        self.load_transaction_data_from_db(self.treeview_list)      
    
    def load_transaction_data_from_db(self, treeview_list):
        conn = sqlite3.connect(self.budget_filename.get()) 
        cur = conn.cursor()
        cur.execute('''select Transactions.id, Transactions.Amount, Transactions.Category_id, Transactions.Sub_Category_id, Transactions.Account_Type_id, Transactions.Month,
                    [Category Name].Income_expense_id 
                    from Transactions join  [Category Name] on Transactions.Category_id = [Category Name].id''')
        transactions = cur.fetchall()
        for tab, table in enumerate(treeview_list[:-1]):
            matched_transactions = []
            non_matched_transactions = []
            for transaction in transactions:
                if transaction[5] == tab:
                    matched_transactions.append(transaction)
                else:
                    non_matched_transactions.append(transaction)
            transactions = non_matched_transactions
            self.add_transaction_data_to_table(table, matched_transactions)
    
    def add_transaction_data_to_table(self, table, matched_transactions):
        for inc_exp in table.get_children():
            for cat in table.get_children(inc_exp):
                for subcat in table.get_children(cat):
                    match_found = False
                    for account in self.budget_accounts:
                        transactions_for_current_cell = 0
                        for transaction_match in matched_transactions:
                            if transaction_match[3] == table.item(subcat).get("tags")[0] and transaction_match[4] == account[1]:
                                transactions_for_current_cell += transaction_match[1]
                                match_found = True
                        if match_found == True:
                            subcat_data = table.item(subcat).get("values") 
                            subcat_data[account[1] + 1] = transactions_for_current_cell
                            transaction_total = 0
                            if len(self.budget_accounts) > 1:
                                for num in range(2, len(self.budget_accounts)+2):
                                    if subcat_data[num] != '':  #NOTE is this if condition needed?
                                        subcat_data[num] = '{:.2f}'.format(float(subcat_data[num]))
                                        subcat_data[num] = float(subcat_data[num])
                                        transaction_total += subcat_data[num]
                                subcat_data[-1] = transaction_total
                            table.item(subcat, values=subcat_data)
    
    def calculate_yearly_totals(self):
        budget_column_list = [] #this is a list that stores a list for each column
        for heading in self.budget_table_headings[2:]:
            column_list = [] #these lists store the $ values for each col
            budget_column_list.append(column_list)
        for tab in self.treeview_list[:13]:
            current_tab = self.treeview_list.index(tab)
            subcat_index = 0
            for inc_exp in tab.get_children():
                for cat in tab.get_children(inc_exp):
                    for subcat in tab.get_children(cat):
                        if current_tab == 0:
                            for index, column in enumerate(tab.item(subcat).get("values")[2:]):
                                if column == "" or column == "-----":
                                    budget_column_list[index].append(0)
                                else:
                                    column = float(column)
                                    budget_column_list[index].append(column)
                        else:
                            for index, column in enumerate(tab.item(subcat).get("values")[2:]):
                                if column == "" or column == "-----":
                                    budget_column_list[index][subcat_index] += 0
                                else:
                                    column = float(column)
                                    budget_column_list[index][subcat_index] += column
                                    budget_column_list[index][subcat_index] = round(budget_column_list[index][subcat_index], 2)
                        subcat_index += 1
        self.display_yearly_totals(budget_column_list)

    def display_yearly_totals(self, budget_column_list):
        subcat_index = 0
        for inc_exp in self.treeview_list[13].get_children():
                for cat in self.treeview_list[13].get_children(inc_exp):
                    for subcat in self.treeview_list[13].get_children(cat):
                        row_data = self.treeview_list[13].item(subcat).get("values")
                        for total, column in zip(row_data[2:], budget_column_list):
                            row_data[row_data.index(total)] = column[subcat_index]
                        self.treeview_list[13].item(subcat, values=row_data)
                        subcat_index += 1

    def set_treeview_style_managebudget_table(self):
        self.bg_color_table = self.manage_budget_table_frame._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        self.selected_color_table = self.manage_budget_table_frame._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.text_color_table = self.manage_budget_table_frame._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])

        self.template_table_style = ttk.Style(self)
        self.template_table_style.theme_use('default')
        self.template_table_style.configure("Treeview", fieldbackground="#343434", background="#343434", foreground="#ffffff", font=('calibri', 15), borderwidth=0, rowheight=28)
        self.template_table_style.configure("Treeview.Heading", borderwidth=1, relief="ridge", background="#343434", foreground="#ffffff", font=('calibri', 15))
        self.template_table_style.map("Treeview", background=[("selected", "#303030")], foreground=[("selected", self.selected_color_table)])

    def selected_cell_transaction_list(self):
        self.transaction_list_window = ctk.CTkToplevel()
        self.transaction_list_window.title("Add New Transaction")
        self.transaction_list_window.geometry("600x550")
        self.transaction_list_window.focus()
        self.transaction_list_window.grab_set()
        self.transaction_list_window.grid_columnconfigure((0,1,2,3,4), weight=1, uniform='a')
        self.transaction_list_window.grid_rowconfigure((0,1,2,3), weight=1, uniform='a')
        self.transaction_list_window.grid_rowconfigure(4, weight=50)
        self.transaction_list_window.grid_rowconfigure(5, weight=10)

        #widgets
        self.transactions_for = ctk.CTkLabel(self.transaction_list_window, text="Transactions for: ", text_color="#00aaff", font=('calibri', 24))
        self.transactions_for_info = ctk.CTkLabel(self.transaction_list_window, text="Annual/Month, Account, Income/Expenses", text_color="#00aaff", font=('calibri', 24))
        self.transactions_for_info_category = ctk.CTkLabel(self.transaction_list_window, text="Category", text_color="#00aaff", font=('calibri', 24))
        self.transactions_for_info_subcategory = ctk.CTkLabel(self.transaction_list_window, text="Sub-Category", text_color="#00aaff", font=('calibri', 24))

        self.cell_transaction_list_frame = ctk.CTkScrollableFrame(self.transaction_list_window)
        self.cell_transaction_list_frame.grid_columnconfigure(0, weight=1)
        self.cell_transaction_list_frame.grid_rowconfigure(0, weight=1)

        self.transaction_list_cancel_button = ctk.CTkButton(self.transaction_list_window, text="Cancel", fg_color="#00aaff", font=('calibri', 24), command=self.transaction_list_window.destroy)
        self.transaction_list_add_new_button = ctk.CTkButton(self.transaction_list_window, text="Add New", fg_color="#00aaff", font=('calibri', 24), command=lambda button="addnew":self.transaction_editor(button))
        self.transaction_list_edit_button = ctk.CTkButton(self.transaction_list_window, text="Edit", fg_color="#00aaff", font=('calibri', 24), state="disabled", command=lambda button="edit": self.transaction_editor(button))
        self.transaction_list_delete_button = ctk.CTkButton(self.transaction_list_window, text="Delete", fg_color="#00aaff", font=('calibri', 24), state="disabled", command=lambda button="delete": self.confirm_transaction_edits(button))
        self.transaction_list_confirm_button = ctk.CTkButton(self.transaction_list_window, text="Confirm", fg_color="#00aaff", font=('calibri', 24), command=self.confirm_transaction_list)

        #layout
        self.transactions_for.grid(row=0, column=0, columnspan=5, sticky="n")
        self.transactions_for_info.grid(row=1, column=0, columnspan=5, sticky="n")
        self.transactions_for_info_category.grid(row=2, column=0, columnspan=5, sticky="n")
        self.transactions_for_info_subcategory.grid(row=3, column=0, columnspan=5, sticky="n")

        self.cell_transaction_list_frame.grid(row=4, column=0, columnspan=5, sticky="nsew", padx=10, pady=(5,0))

        self.transaction_list_cancel_button.grid(row=5, column=0, sticky="ew", padx=(10,5), pady=(0,5))
        self.transaction_list_add_new_button.grid(row=5, column=1, sticky="ew", padx=5, pady=(0,5))
        self.transaction_list_edit_button.grid(row=5, column=2, sticky="ew", padx=5, pady=(0,5))
        self.transaction_list_delete_button.grid(row=5, column=3, sticky="ew", padx=5, pady=(0,5))
        self.transaction_list_confirm_button.grid(row=5, column=4, sticky="ew", padx=(5,10), pady=(0,5))

        self.get_selected_cell_info()

    def get_selected_cell_info(self, called_by_manager = 0): #called_by_manager = 1 means 'add transaction' button was pressed from manager window (not list window)
        #store selected cell treeview data as 3 dictionaries
        selected_cell_incexp_dict =  self.treeview_list[self.current_tab].item(self.treeview_list[self.current_tab].parent(self.treeview_list[self.current_tab].parent(self.selected_row_item)))
        selected_cell_category_dict = self.treeview_list[self.current_tab].item(self.treeview_list[self.current_tab].parent(self.selected_row_item))
        selected_cell_subcategory_dict = self.selected_row_complete
        #form selected cell info into series of length 2 lists
        current_treeview_info = [self.treeview_list[self.current_tab], self.tab_list[self.current_tab], self.current_tab] #the current treeview(can be used to ID tab)
        selected_cell_account_info = [self.budget_accounts[self.selected_column-3][0], self.selected_column - 2]
        selected_cell_incexp_info = [selected_cell_incexp_dict.get("values")[0], selected_cell_incexp_dict.get("tags")[0]]
        selected_cell_category_info = [selected_cell_category_dict.get("values")[0], selected_cell_category_dict.get("tags")[0]]
        selected_cell_subcategory_info = [selected_cell_subcategory_dict.get("values")[0], selected_cell_subcategory_dict.get("tags")[0]]
        #store cell info text and ID 
        self.selected_cell_info_list = [current_treeview_info, selected_cell_account_info, selected_cell_incexp_info, selected_cell_category_info, selected_cell_subcategory_info]

        #set up vars for lists of transaction check boxes and their status
        self.list_of_transaction_checkboxes = []
        self.checkbox_statuses = []

        #vars for selected transaction amount and id with default value = ""/0 when no transaction selected
        self.selected_transaction_amount = ctk.StringVar(value="")
        self.selected_transaction_id = ctk.IntVar(value=0)

        if called_by_manager == 0: #attempt to load transaction info from database (this func was called from list window)
            self.load_cell_transactions_from_database()
        if called_by_manager == 1: #bypass transaction list, and load transactions from database and go to transaction editor (add new was pressed from manager window)
            button="addnew"
            self.transaction_editor(button, called_by_manager)

    def load_cell_transactions_from_database(self):       
        #load transaction information for selected cell from DB (eventually transaction info will include day and entity)        
        conn = sqlite3.connect(self.budget_filename.get()) 
        cur = conn.cursor()
        cur.execute('''select Transactions.id, [Income Expense].[Income/Expense], [Category Name].Category, [Sub-Category Name].[Sub-Category], Accounts.[Account Name],
                    Transactions.Month, Transactions.Amount 
                    from Transactions join  [Category Name] join [Income Expense] join [Sub-Category Name] join [Accounts]
                    on Transactions.Category_id = [Category Name].id 
                    and [Category Name].[Income_Expense_id] = [Income Expense].id
                    and Transactions.[Sub_Category_id] = [Sub-Category Name].id
                    and Transactions.[Account_Type_id] = Accounts.id
                    where ([Income_Expense_id], [Category_id], [Sub_Category_id], [Account_Type_id], Month) = (?, ?, ?, ?, ?)''', (self.selected_cell_info_list[2][1], self.selected_cell_info_list[3][1], self.selected_cell_info_list[4][1], self.selected_cell_info_list[1][1], self.current_tab))
        transactions = cur.fetchall()
        self.cell_info_list = []
        self.transactions_list = []
        for transaction in transactions:
            self.transactions_list.append(list(transaction))

        for index, transaction in enumerate(self.transactions_list):
            transaction_checkbox = ctk.CTkCheckBox(self.cell_transaction_list_frame, text=str(transaction[-1]), command=self.user_selects_transaction)
            self.list_of_transaction_checkboxes.append(transaction_checkbox)
            self.checkbox_statuses.append(0)
            transaction_checkbox.grid(row=0+index, column=0, sticky="wn", pady=5, padx=5)
        #configure transaction list labels to display selected cell info
        self.transactions_for_info.configure(text=self.selected_cell_info_list[0][1] + ", " + self.selected_cell_info_list[1][0] + ", " + self.selected_cell_info_list[2][0])
        self.transactions_for_info_category.configure(text="Category: " + self.selected_cell_info_list[3][0])
        self.transactions_for_info_subcategory.configure(text="Sub-Category: " + self.selected_cell_info_list[4][0])
        
    def user_selects_transaction(self): 
            self.selected_transaction_amount = ctk.StringVar(value="")
            self.selected_transaction_id = ctk.IntVar(value=0) 
            temp_checkbox_statuses = []
            for checkbox in self.checkbox_statuses:
                temp_checkbox_statuses.append(checkbox)
            for index, checkbox in enumerate(self.list_of_transaction_checkboxes):
                if self.checkbox_statuses[index] != checkbox.get(): 
                    temp_checkbox_statuses.pop(index)
                    temp_checkbox_statuses.insert(index, checkbox.get())
                if self.checkbox_statuses[index] == checkbox.get():
                    temp_checkbox_statuses.pop(index)
                    temp_checkbox_statuses.insert(index, 0)
                    if checkbox.get() == 1:
                        checkbox.deselect()     
            self.checkbox_statuses = temp_checkbox_statuses
            for checkbox, transaction in zip(self.checkbox_statuses, self.transactions_list): #store selected transaction amount
                if checkbox == 1:
                    self.selected_transaction_amount = ctk.StringVar(value=transaction[-1])
                    self.selected_transaction_id = ctk.IntVar(value=transaction[0])
            if 1 in self.checkbox_statuses: #activate edit/delete button on selection
                self.transaction_list_edit_button.configure(state="normal")
                self.transaction_list_delete_button.configure(state="normal")
                self.transaction_list_add_new_button.configure(state="disabled")
            else:
                self.transaction_list_edit_button.configure(state="disabled")
                self.transaction_list_delete_button.configure(state="disabled")
                self.transaction_list_add_new_button.configure(state="normal")

    def add_new_transaction(self):
        #update the treeview and DB, only called when 'add new' pressed from manager window
        try:
            self.selected_row[self.selected_column-1] = round((float(self.selected_row[self.selected_column-1]) + self.transaction_editor_amount), 2)
        except ValueError:
            self.selected_row[self.selected_column-1] = round(self.transaction_editor_amount, 2)
        if len(self.budget_accounts) > 1:
            try:
                self.selected_row[-1] = round((float(self.selected_row[-1]) + self.transaction_editor_amount), 2)
            except ValueError:
                self.selected_row[-1] = round(self.transaction_editor_amount, 2)
        self.treeview_list[self.current_tab].item(self.selected_row_item, values=self.selected_row) 
        #Add new transaction to DB
        conn = sqlite3.connect(self.budget_filename.get()) 
        cur = conn.cursor()
        transacation_cat_id = self.selected_cell_info_list[3][1]
        transacation_subcat_id = self.selected_cell_info_list[4][1]
        transacation_account_id = self.selected_cell_info_list[1][1]
        cur.execute("insert into Transactions (Amount, [Category_id], [Sub_Category_id], [Account_Type_id], Month) Values (?, ?, ?, ?, ?)", (self.transaction_editor_amount, transacation_cat_id, transacation_subcat_id, transacation_account_id, self.current_tab))
        conn.commit()          

    def confirm_transaction_list(self):
        new_cell_total = 0
        #run through list of transactions and checkboxes for their status
        for index, transaction in enumerate(self.transactions_list):
            if "new" in self.list_of_transaction_checkboxes[index].cget("text"):
                new_cell_total = round(new_cell_total + transaction[-1], 2)
                self.write_transaction_list_to_database("new", transaction)
            elif "modified" in self.list_of_transaction_checkboxes[index].cget("text"): 
                amount_modified_only = True
                account_only_modified_cat = True
                if transaction[1] != self.selected_cell_info_list[2][0]: #inc/exp
                    amount_modified_only = False
                    account_only_modified_cat = False
                elif transaction[2] != self.selected_cell_info_list[3][0]: #cat
                    amount_modified_only = False
                    account_only_modified_cat = False
                elif transaction[3] != self.selected_cell_info_list[4][0]: #subcat
                    amount_modified_only = False
                    account_only_modified_cat = False
                elif transaction[4] != self.selected_cell_info_list[1][0]: #account
                    amount_modified_only = False
                elif transaction[5] != self.selected_cell_info_list[0][-1]: #tab
                    amount_modified_only = False
                    account_only_modified_cat = False
                if amount_modified_only == True: #modified transaction stays in selected cell
                    new_cell_total = round(new_cell_total + transaction[-1], 2)
                if account_only_modified_cat == True: #modified transaction stays in selected row, amount may or may not be modified
                    for account in self.budget_accounts:
                        if account[0] == transaction[4]:
                            try:
                                self.selected_row[account[1] + 1] = round(float(self.selected_row[account[1] + 1]) + transaction[-1], 2)
                            except ValueError:
                                self.selected_row[account[1] + 1] = transaction[-1] #Note:row total recalculated below
                if amount_modified_only == False and account_only_modified_cat == False: #modified transaction moved to another cell, in a different row
                    for inc_exp in self.treeview_list[transaction[5]].get_children():
                        for cat in self.treeview_list[transaction[5]].get_children(inc_exp):
                            for subcat in self.treeview_list[transaction[5]].get_children(cat):
                                if self.treeview_list[transaction[5]].item(subcat).get("values")[0] == transaction[3]\
                                    and self.treeview_list[transaction[5]].item(cat).get("values")[0] == transaction[2]\
                                    and self.treeview_list[transaction[5]].item(inc_exp).get("values")[0] == transaction[1]:
                                    modified_new_row = subcat
                                    modified_new_row_data = self.treeview_list[transaction[5]].item(subcat).get("values")
                                    if len(self.budget_accounts) > 1:
                                        for account in self.budget_accounts:
                                            if transaction[4] == account[0]:
                                                try:
                                                    modified_new_row_data[account[1] + 1] = round(float(modified_new_row_data[account[1] + 1]) + transaction[-1], 2)
                                                    modified_new_row_data[-1] = round(float(modified_new_row_data[-1]) + transaction[-1], 2)
                                                except ValueError:
                                                    modified_new_row_data[account[1] + 1] = transaction[-1]
                                                    modified_new_row_data[-1] = transaction[-1]
                                    else: #only 1 budget account: use col 3/index=2
                                        try:
                                            modified_new_row_data[2] = round(float(modified_new_row_data[2]) + transaction[-1], 2)
                                        except ValueError:
                                            modified_new_row_data[2] = transaction[-1]
                                    self.treeview_list[transaction[5]].item(modified_new_row, values=modified_new_row_data) 
                                    break 
                self.write_transaction_list_to_database("modified", transaction)
            elif "deleted" in self.list_of_transaction_checkboxes[index].cget("text"):
                self.write_transaction_list_to_database("deleted", transaction)
                continue
            else: #unaltered transactions
                new_cell_total = round(new_cell_total + transaction[-1], 2)
        #update selected row, and col
        self.selected_row[self.selected_column-1] = new_cell_total
        if len(self.budget_accounts) > 1:
            row_total = 0
            for col in self.selected_row[2:-1]:
                try:
                    row_total += float(col)
                except ValueError:
                    row_total += 0 
            self.selected_row[-1] = row_total
        self.treeview_list[self.current_tab].item(self.selected_row_item, values=self.selected_row)
        self.transaction_list_window.destroy()

    def write_transaction_list_to_database(self, modification: str, transaction):
        print(transaction, self.selected_cell_info_list)
        conn = sqlite3.connect(self.budget_filename.get()) 
        cur = conn.cursor()
        if modification == "new":
            transacation_cat_id = self.selected_cell_info_list[3][1]
            transacation_subcat_id = self.selected_cell_info_list[4][1]
            transacation_account_id = self.selected_cell_info_list[1][1]
            cur.execute("insert into Transactions (Amount, [Category_id], [Sub_Category_id], [Account_Type_id], Month) Values (?, ?, ?, ?, ?)", (transaction[-1], transacation_cat_id, transacation_subcat_id, transacation_account_id, transaction[5]))
        elif modification == "modified":
            print(transaction)
            cur.execute("select id from [Category Name] where Category = ?", (transaction[2], ))
            cat_id = cur.fetchone()[0]
            print(cat_id)
            cur.execute("select id from [Sub-Category Name] where ([Sub-Category], [Category_Name_id]) = (?, ?)", (transaction[3], cat_id))
            subcat_id = cur.fetchone()[0]
            print(subcat_id)
            cur.execute("select id from Accounts where [Account Name] = ?", (transaction[4], ))
            account_id = cur.fetchone()[0]
            print(account_id)
            cur.execute("update Transactions set Amount = ?, [Category_id] = ?, [Sub_Category_id] = ?, [Account_Type_id] = ?, Month = ? where id = ?", (transaction[-1], cat_id, subcat_id, account_id, transaction[5], transaction[0]))
        elif modification == "deleted":
            cur.execute("delete from Transactions where id = ?", (transaction[0], ))
        conn.commit()
                
    #update the transaction list when transactions added, edited, and deleted
    def confirm_transaction_edits(self, button, called_by_manager=0):
        if called_by_manager == 1: #addnew was pressed from editor window, skip updating of list window and call add_new_transaction
            self.add_new_transaction()
        if called_by_manager == 0 and button == "addnew": #addnew or edit was pressed from list window, update list window then call add_new_transaction
            new_transaction_checkbox = ctk.CTkCheckBox(self.cell_transaction_list_frame, text=self.entry_var_amount.get() + " new", command=self.user_selects_transaction)
            self.list_of_transaction_checkboxes.append(new_transaction_checkbox)
            new_transaction_checkbox.grid(row=len(self.list_of_transaction_checkboxes), column=0, sticky="wn", pady=5, padx=5)
            self.checkbox_statuses.append(0)
            self.transactions_list.append([0, self.combo_var_incexp.get(), self.combo_var_cat.get(), self.combo_var_subcat.get(), self.combo_var_account.get(), self.combo_var_tab.get(), self.transaction_editor_amount])
        if called_by_manager == 0 and button == "edit": #edit existing transactions
            for index, status in enumerate(self.checkbox_statuses):
                if status == 1:
                    transaction_modified = False
                    if self.transactions_list[index][1] != self.combo_var_incexp.get(): #inc/exp
                        self.transactions_list[index][1] = self.combo_var_incexp.get()
                        transaction_modified = True
                    if self.transactions_list[index][2] != self.combo_var_cat.get(): #cat
                        self.transactions_list[index][2] = self.combo_var_cat.get()
                        transaction_modified = True
                    if self.transactions_list[index][3] != self.combo_var_subcat.get(): #subcat
                        self.transactions_list[index][3] = self.combo_var_subcat.get()
                        transaction_modified = True
                    if self.transactions_list[index][4] != self.combo_var_account.get(): #account
                        self.transactions_list[index][4] = self.combo_var_account.get()
                        transaction_modified = True
                    # combo_var_tab is text, must be convertede back into corresponding number in transactions_list (so it can be output to DB)
                    tab_num = [pair[0] for pair in enumerate(self.tab_list) if pair[1] == self.combo_var_tab.get()][0] 
                    if self.transactions_list[index][5] != tab_num: #tab/month
                        self.transactions_list[index][5] = tab_num
                        transaction_modified = True
                    if self.transactions_list[index][6] != self.transaction_editor_amount: #amount
                        self.transactions_list[index][6] = self.transaction_editor_amount
                        transaction_modified = True
                    if transaction_modified == True:
                        self.list_of_transaction_checkboxes[index].configure(text=self.entry_var_amount.get() + " modified")
                    self.list_of_transaction_checkboxes[index].deselect()
        if called_by_manager == 0 and button == "delete": #delete transactions
            for index, selection in enumerate(self.checkbox_statuses):
                if selection == 1:
                    self.list_of_transaction_checkboxes[index].configure(text=(self.selected_transaction_amount.get() + " deleted"), state="disabled")
                    self.list_of_transaction_checkboxes[index].deselect()
        if called_by_manager == 0: #list window does nto exist
            self.transaction_list_edit_button.configure(state="disabled")
            self.transaction_list_delete_button.configure(state="disabled")
            self.transaction_list_add_new_button.configure(state="normal") 
        #reset selected transaction vars (prevents entry box being filled by last value deleted)
        self.selected_transaction_amount = ctk.StringVar(value="")
        self.selected_transaction_id = ctk.IntVar(value=0)
        if button != "delete":
            self.transaction_editor_window.destroy()

    def transaction_editor(self, button, called_by_manager=0):
        self.transaction_editor_window = ctk.CTkToplevel()
        self.transaction_editor_window.title("Edit Transaction")
        self.transaction_editor_window.geometry("500x550")
        self.transaction_editor_window.focus()
        self.transaction_editor_window.grab_set()
        self.transaction_editor_window.grid_columnconfigure((0,1), weight=1, uniform='a')
        self.transaction_editor_window.grid_rowconfigure((0), weight=1, uniform='a')
        self.transaction_editor_window.grid_rowconfigure(1, weight=50)
        self.transaction_editor_window.grid_rowconfigure(2, weight=10)

        #variables
        #add/edit lists for tab and account, provinding dropdown menu options
        self.annual_month_text_list = self.tab_list[:-1]
        self.budget_accounts_text_list = []
        for account in self.budget_accounts:
            self.budget_accounts_text_list.append(account[0])
        self.income_expense_text_list = []
        [self.income_expense_text_list.append(key) for key in self.budget_structure.keys()]
        
        self.combo_var_tab = ctk.StringVar(value=self.selected_cell_info_list[0][1])
        self.combo_var_account = ctk.StringVar(value=self.selected_cell_info_list[1][0])
        self.combo_var_incexp = ctk.StringVar(value=self.selected_cell_info_list[2][0])
        self.combo_var_cat = ctk.StringVar(value=self.selected_cell_info_list[3][0])
        self.combo_var_subcat = ctk.StringVar(value=self.selected_cell_info_list[4][0])
        self.entry_var_amount = self.selected_transaction_amount
            
        def set_dropdown_categories(incexp, defaults_set=1): 
            self.category_text_list = []
            [self.category_text_list.append(cat) for cat in self.budget_structure[incexp].keys()]
            if defaults_set == 1:
                self.combo_var_cat = ctk.StringVar(value=self.category_text_list[0])
            self.category_dropdown.configure(values=self.category_text_list, variable=self.combo_var_cat)
            set_dropdown_subcategories(self.combo_var_cat.get(), defaults_set)
        
        def set_dropdown_subcategories(category, defaults_set=1): 
            self.subcategory_text_list = []
            if self.combo_var_tab.get() == "Annual": #dropdown=annual
                self.annual_monthly = 2
            if self.combo_var_tab.get() != "Annual": #dropdown=monthly
                self.annual_monthly = 1
            for index, subcat in enumerate(self.budget_structure[self.combo_var_incexp.get()][category][0]):
                if self.budget_structure[self.combo_var_incexp.get()][category][1][index] == self.annual_monthly:
                    self.subcategory_text_list.append(subcat)
            if defaults_set == 1:
                if len(self.subcategory_text_list) == 0: #user selected a cat with no subcats (likely lacking annuals)
                    self.combo_var_subcat = ctk.StringVar(value="")
                    self.transaction_editor_confirm_button.configure(state="disabled")
                else:
                    self.combo_var_subcat = ctk.StringVar(value=self.subcategory_text_list[0])
                    self.transaction_editor_confirm_button.configure(state="normal")
            self.subcategory_dropdown.configure(values=self.subcategory_text_list, variable=self.combo_var_subcat)
            defaults_set = 1
        
        def user_selects_annual_or_month(annual):
            if annual != "Annual" and self.annual_monthly == 2: #switching from annual to month
                defaults_set = 1
            elif annual == "Annual" and self.annual_monthly == 1: #switching from month to annual
                defaults_set = 1
            else: #switching from month to month
                defaults_set = 0
            set_dropdown_categories(self.combo_var_incexp.get(), defaults_set)

        def set_entry_bindings(event):
            self.amount_entry.bind("<Return>", check_entry_is_number)
            self.amount_entry_focused = True

        def click_outside_amount_entry(event):
            widget = self.winfo_containing(event.x, event.y)
            if widget != self.amount_entry and self.amount_entry_focused == True:
                self.amount_entry_focused = False
                widget.focus_force()
                check_entry_is_number(event)

        def check_entry_is_number(event=""):
            try:
                self.transaction_editor_amount = round(float(self.entry_var_amount.get()), 2)
                self.transaction_editor_confirm_button.configure(state="normal")
            except ValueError:
                self.transaction_editor_confirm_button.configure(state="disabled")
                return "break"
            if not event:
                self.confirm_transaction_edits(button, called_by_manager)

        #widgets
        self.transaction_editor_title = ctk.CTkLabel(self.transaction_editor_window, text="Transaction Editor", text_color="#00aaff", font=('calibri', 24))

        self.transaction_form_frame = ctk.CTkFrame(self.transaction_editor_window)
        self.annual_month_label = ctk.CTkLabel(self.transaction_form_frame, text="Annual/Month", text_color="#00aaff", font=('calibri', 24))
        self.annual_month_dropdown = ctk.CTkComboBox(self.transaction_form_frame, width=250, values=self.annual_month_text_list, variable=self.combo_var_tab, command=user_selects_annual_or_month)
        self.account_label = ctk.CTkLabel(self.transaction_form_frame, text="Account", text_color="#00aaff", font=('calibri', 24))
        self.account_dropdown = ctk.CTkComboBox(self.transaction_form_frame, width=250, values=self.budget_accounts_text_list, variable=self.combo_var_account)
        self.income_expense_label = ctk.CTkLabel(self.transaction_form_frame, text="Income or Expense", text_color="#00aaff", font=('calibri', 24))
        self.income_expense_dropdown = ctk.CTkComboBox(self.transaction_form_frame, width=250, values=self.income_expense_text_list, variable=self.combo_var_incexp, command=set_dropdown_categories)
        self.category_label = ctk.CTkLabel(self.transaction_form_frame, text="Category", text_color="#00aaff", font=('calibri', 24))
        self.category_dropdown = ctk.CTkComboBox(self.transaction_form_frame, width=250, values=[], variable=self.combo_var_cat, command=set_dropdown_subcategories)
        self.subcategory_label = ctk.CTkLabel(self.transaction_form_frame, text="Subcategory", text_color="#00aaff", font=('calibri', 24))
        self.subcategory_dropdown = ctk.CTkComboBox(self.transaction_form_frame, width=250, values=[], variable=self.combo_var_subcat)
        self.amount_label = ctk.CTkLabel(self.transaction_form_frame, text="Amount", text_color="#00aaff", font=('calibri', 24))
        self.amount_entry = ctk.CTkEntry(self.transaction_form_frame, width=250, textvariable=self.entry_var_amount)

        self.amount_entry.bind("<FocusIn>", set_entry_bindings)
        self.transaction_form_frame.bind("<Button-1>", click_outside_amount_entry)

        self.amount_entry_focused = False

        self.transaction_editor_cancel_button = ctk.CTkButton(self.transaction_editor_window, text="Cancel", fg_color="#00aaff", font=('calibri', 24), command=self.transaction_editor_window.destroy)
        self.transaction_editor_confirm_button = ctk.CTkButton(self.transaction_editor_window, text="Confirm", fg_color="#00aaff", font=('calibri', 24), command=check_entry_is_number)

        #layout
        self.transaction_editor_title.grid(row=0, column=0, columnspan=2, sticky="n")

        self.transaction_form_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=(5,0))
        self.annual_month_label.pack(pady=5)
        self.annual_month_dropdown.pack()
        self.account_label.pack(pady=5)
        self.account_dropdown.pack()
        self.income_expense_label.pack(pady=5)
        self.income_expense_dropdown.pack()
        self.category_label.pack(pady=5)
        self.category_dropdown.pack()
        self.subcategory_label.pack(pady=5)
        self.subcategory_dropdown.pack()
        self.amount_label.pack(pady=5)
        self.amount_entry.pack()

        self.transaction_editor_cancel_button.grid(row=2, column=0, sticky="w", padx=10, pady=(0,5))
        self.transaction_editor_confirm_button.grid(row=2, column=1, sticky="e", padx=10, pady=(0,5))

        #if no transaction selected, set dropdowns to disabled (user cannot change their values)
        if button == "addnew":
            self.annual_month_dropdown.configure(state="disabled")
            self.account_dropdown.configure(state="disabled")
            self.income_expense_dropdown.configure(state="disabled")
            self.category_dropdown.configure(state="disabled")
            self.subcategory_dropdown.configure(state="disabled")
        #otherwise, edit button was pressed, default = enabled state

        #set default available categories and subcategories in dropdowns  
        set_dropdown_categories(self.combo_var_incexp.get(), defaults_set=0)

    def clear_manage_budget_table(self):
        if self.budget_displayed_in_manager == 1:
            for table in self.treeview_list:
                table.destroy()
            self.budget_displayed_in_manager = 0

class SaveWindow(ctk.CTkToplevel):
    def __init__(self, parent, save_object_type, save_object_title, save_object=None, new_template=None): #when expanding this class for saving of DB, confirm required vs optional arguments
        super().__init__(master=parent)
        self.title("Save")
        self.geometry("400x240")
        self.rowconfigure((0,1,2), weight=1)
        self.columnconfigure(0, weight=1, uniform='a')
        self.columnconfigure(1, weight=3, uniform='a')
        self.columnconfigure(2, weight=1, uniform='a')

        #widgets
        self.save_window_label = ctk.CTkLabel(self, text=save_object_type, text_color="#00aaff", font=('calibri', 24))
        save_title_box_content = ctk.StringVar(value=save_object_title)
        self.save_title_box = ctk.CTkEntry(self, textvariable=save_title_box_content)

        def clear_title_box(*args):
            self.save_title_box.delete('0', 'end')

        self.clear_textbox = ctk.CTkButton(self, text="clear", fg_color='transparent', hover=False, text_color="#00aaff", font=('calibri', 12), command=clear_title_box)
        
        def check_save_object_type(*args):
            if save_title_box_content.get() == "":
                return
            if save_object_type == "Save Template":
                save_template()
            if save_object_type == "Save Budget":
                save_budget()

        def save_template():
            template_exists = False
            for template in save_object:
                if save_title_box_content.get() == template.get("Title") or save_title_box_content.get() == "Default": 
                    template_exists = True
                    template_exists_warning = ctk.CTkToplevel()
                    template_exists_warning.title("Warning")
                    template_exists_warning.geometry("350x120")
                    template_exists_warning.focus()
                    template_exists_warning.grab_set()
                    template_exists_warning_text = ctk.CTkLabel(template_exists_warning, text="A Template with that Name Already Exists.\nPlease Choose a New Name", text_color="#00aaff", font=('calibri', 12))
                    template_exists_warning_ok = ctk.CTkButton(template_exists_warning, text="Ok", fg_color="#00aaff", font=('calibri', 18), command=lambda : (template_exists_warning.destroy(), self.focus(), self.grab_set()))
                    template_exists_warning_text.pack(pady=10, padx=10)
                    template_exists_warning_ok.pack(pady=10, padx=10)
                    break
            if template_exists == False:
                new_template["Title"] = save_title_box_content.get()
                if save_object[0].get("Title") == "Default":
                    save_object.pop(0)
                save_object.append(new_template)
                json_budget_templates = json.dumps(save_object, indent=4)
                with open("budget templates.json", "w") as template_export:
                    template_export.write(json_budget_templates)
                self.destroy()

        def save_budget():
            print("this function will save budget to sql database")

        self.save_window_button = ctk.CTkButton(self, text="Save", fg_color="#00aaff", font=('calibri', 18), command=check_save_object_type)
        
        self.empty_frame = ctk.CTkFrame(self, fg_color='transparent')
        

        #layout
        self.save_window_label.grid(row=0, column=1, sticky='s') 
        self.save_title_box.grid(row=1, column=1, sticky='ew')
        self.clear_textbox.grid(row=1, column=2, sticky='ew')
        self.save_window_button.grid(row=2, column=1, sticky='new')

        self.empty_frame.grid(column=0, row=0, rowspan=3, sticky='ns')

        #change clear button text on hover #004d74
        def on_hover_clear(*args):
            self.clear_textbox.configure(text_color="#004d74")

        def on_leave_clear(*args):
            self.clear_textbox.configure(text_color="#00aaff")
     
        self.clear_textbox.bind("<Enter>", on_hover_clear)
        self.clear_textbox.bind("<Leave>", on_leave_clear)

# #set default sub-categories and their monthly(1)/annual(2) status
default_budget_template = {
                        "Title" : 
                        "Default",
                        "Income" : 
                        {"All Income" : [["Employment", "Rent", "Investments", "Other"], [1,2,1,1]]},
                        "Expenses" : 
                        {"Housing" : [["Rent", "Utilities", "Phone", "Internet", "TV/Streaming Services", "Maintenance", "Home Insurance", "Other"], [1,1,1,1,1,1,2,1]],
                        "Common Living Expenses" : [["Groceries", "Delivery/Take Out", "Coffee/Treats", "Hygeine and Personal Grooming", "Appliances", "Computer Parts", "Entertainment", "Hobbies and Skill Development", "Bank/Credit Card Fees", "Taxes", "Other"], [1,1,1,1,1,1,1,1,1,2,1]],
                        "Transportation" : [["Transit Pass", "Car Share Services", "Fuel", "Insurance", "Maintenance", "Parking"], [1,1,1,2,1,1]],
                        "Clothing" : [["Everyday Use", "Special Occasion", "Other"], [1,1,1]],
                        "Medical" : [["Insurance (life)", "Insurance (Medical)", "Prescription Drugs", "Over the Counter Drugs", "Medical Services", "Paramedical Services", "Dental", "Vision Care", "Skin Care", "Other"], [2,2,1,1,1,1,1,1,1,1]]}
                        }

main_window = MainWindow("Erika's Budget Manager", (1000, 600))

