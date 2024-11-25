import sqlite3
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import json
import os

# A class for main app window (contains main menu)
class MainWindow(ctk.CTk):
    def __init__(self, title, windowsize):
        super().__init__()
        self.title(title)
        self.geometry(f'{windowsize[0]}x{windowsize[1]}')

        #widgets
        #button panel for create new budget process
        create_new_button_panel = ctk.CTkFrame(self)
        create_new_button_panel.grid_columnconfigure((0,1,2), weight=1)
        create_new_button_panel.grid_rowconfigure(0, weight=1)
        #buttons
        button_continue = ctk.CTkButton(create_new_button_panel, text="Continue", fg_color="#00aaff", font=('calibri', 35), command=self.continue_button)
        button_back = ctk.CTkButton(create_new_button_panel, text="Back", fg_color="#00aaff", font=('calibri', 35), command=self.back_button)
        # button panel layout
        button_continue.grid(row=0, column=2, sticky="ne", pady=10, padx=80) #this should not appear until a selection is made
        button_back.grid(row=0, column=0, sticky="nw", pady=10, padx=80)

        #pages: create a new budget
        self.create_new_p1 = ChooseBudgetTemplate(self)
        self.create_new_p2 = EditBudgetTemplate(self) 

        #main menu
        self.main_menu = MainMenu(self, self.create_new_p1, create_new_button_panel) #need to pass any pages that are accessed by the button on main menu directly (so just the 1st)
        self.main_menu.configure(fg_color="transparent")     

        #final create new budget page (has to come after main menu so that mainmenu is raisable from that page)
        self.create_new_p3 = EnterBudgetAmounts(self, self.main_menu)

        #layout
        self.main_menu.place(relx=0.5, rely=0, relwidth=1, relheight=1, anchor='n')
        
        self.create_new_p1.place(relx=0.5, rely=0, relwidth=1, relheight=0.9, anchor='n')
        self.create_new_p2.place(relx=0.5, rely=0, relwidth=1, relheight=0.9, anchor='n')
        self.create_new_p3.place(relx=0.5, rely=0, relwidth=1, relheight=0.9, anchor='n')

        create_new_button_panel.place(relx=0.5, rely=1, relwidth=1, relheight=0.1, anchor='s')

        #other variables 
        #list that tracks pages for create_new_button_panel    
        self.create_new_pages = [self.create_new_p1, self.create_new_p2, self.create_new_p3]
        self.current_page_createnew = 0

        #NOTE directory where user files will be saved may go here
        
        self.main_menu.tkraise() #main menu shows up at launch
        self.mainloop()

    def back_button(self):
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
    
    def continue_button(self):
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

#a frame that holds the main menu (title, buttons(3), version note)
class MainMenu(ctk.CTkFrame):
    def __init__(self, parent, create_new_frame, create_new_button_panel_frame):
        super().__init__(master=parent)
        self.grid_columnconfigure((0,2), weight=(1), uniform='a')
        self.grid_columnconfigure((1), weight=(4), uniform='a')
        self.grid_rowconfigure((0), weight=2)
        self.grid_rowconfigure((1,2,3), weight=1)
        self.grid_rowconfigure((4), weight=0)
        
        #pass each frame/page that each button in Main menu can raise
        self.create_new_p1 = create_new_frame
        self.button_panel = create_new_button_panel_frame

        #widgets 1 label,3 buttons, another label
        self.main_menu_label = ctk.CTkLabel(self, text="Erika's Budget Manager", text_color="#00aaff", font=('calibri', 65))
        
        self.create_new_button = ctk.CTkButton(self, text="Create a New Budget", fg_color="#00aaff", font=('calibri', 40), command = self.create_new)
        self.open_existing_button = ctk.CTkButton(self, text="Manage an Existing Budget", fg_color="#00aaff", font=('calibri', 40))
        self.options_button = ctk.CTkButton(self, text="Options", fg_color="#00aaff", font=('calibri', 40))

        self.version_note = ctk.CTkLabel(self, text="Version 0.2", text_color="#686868")

        #layout
        self.main_menu_label.grid(row=0, column=1, columnspan=1, sticky='ew')

        self.create_new_button.grid(row=1, column=1, padx=50, pady=10, sticky='ns')
        self.open_existing_button.grid(row=2, column=1, padx=50, pady=10, sticky='ns')
        self.options_button.grid(row=3, column=1, padx=10, pady=10, ipadx=110, sticky='ns') 

        self.version_note.grid(row=4, column=2)

    #initiate create new
    def create_new(self):
        self.create_new_p1.tkraise()
        self.button_panel.tkraise()
        self.create_new_p1.display_template_list()
       
class ChooseBudgetTemplate(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(master=parent)
        self.grid_columnconfigure(0, weight=10)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=50)

        #widgets
        self.create_new_budget_label = ctk.CTkLabel(self, text="Choose a Budget Template", text_color="#00aaff", font=('calibri', 55))

        self.scrolling_list = ctk.CTkScrollableFrame(self)

        self.template_title = ctk.StringVar(value="")
        #self.template_list = self.display_template_list()
        
        #layout
        self.create_new_budget_label.grid(row=0, column=0, sticky='ew', columnspan=2)
    
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
            self.radiobutton = ctk.CTkRadioButton(self.scrolling_list, text=template.get("Title"), value=template.get("Title"), variable=self.template_title) 
            self.radiobutton.grid(row=0+index, column=0, pady=5, sticky='w')
        return self.template_list
        
#may want to set the default to be selected upon entering (so user cannot proceed without a template selected)

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

        def return_pressed_in_category_text_box(*args):
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

        def rename_category(*args):
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
       
        def move_category_up(*args):
            current_category_pos = self.template_editor.index(self.template_editor.focus())
            self.template_editor.move(self.template_editor.focus(), self.template_editor.parent(self.template_editor.focus()), current_category_pos-1)

        def move_category_down(*args):
            current_category_pos = self.template_editor.index(self.template_editor.focus())
            self.template_editor.move(self.template_editor.focus(), self.template_editor.parent(self.template_editor.focus()), current_category_pos+1)

        self.moveup_category_button = ctk.CTkButton(self.context_category, text="Move Up", fg_color="#00aaff", font=('calibri', 18), command=move_category_up)
        self.movedown_category_button = ctk.CTkButton(self.context_category, text="Move Down", fg_color="#00aaff", font=('calibri', 18), command=move_category_down)
        
        self.subcategory_text_box_in_category_menu = ctk.CTkTextbox(self.context_category, height=50)
        #keep track of text box focus
        self.subcategory_text_box_in_category_menu_focus = 0

        def return_pressed_in_category_menu_subcategory_text_box(*args):
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

        def rename_subcategory(*args):
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

        def move_subcategory_up(*args):
            current_subcategory_pos = self.template_editor.index(self.template_editor.focus())
            self.template_editor.move(self.template_editor.focus(), self.template_editor.parent(self.template_editor.focus()), current_subcategory_pos-1)

        def move_subcategory_down(*args):
            current_subcategory_pos = self.template_editor.index(self.template_editor.focus())
            self.template_editor.move(self.template_editor.focus(), self.template_editor.parent(self.template_editor.focus()), current_subcategory_pos+1)

        self.moveup_subcategory_button = ctk.CTkButton(self.context_subcategory, text="Move Up", fg_color="#00aaff", font=('calibri', 18), command=move_subcategory_up)
        self.movedown_subcategory_button = ctk.CTkButton(self.context_subcategory, text="Move Down", fg_color="#00aaff", font=('calibri', 18), command=move_subcategory_down)
        
        self.monthly_annual = ctk.IntVar()
        def monthly_annual_checkbox_status(*args):
            self.template_editor.item(self.template_editor.focus(), values=self.monthly_annual.get())

        self.subcategory_annual_checkbox= ctk.CTkCheckBox(self.context_subcategory, text="Annual", fg_color="#00aaff", font=('calibri', 18), onvalue=2, offvalue=1, variable=self.monthly_annual, command=monthly_annual_checkbox_status)

        #intro message
        self.context_intro_message = ctk.CTkFrame(self)
        self.intro_message_label = ctk.CTkLabel(self.context_intro_message, text="To Edit Budget,\n Select a Component\n from the Menu")
        #save button
        self.save_button_frame = ctk.CTkFrame(self)

        def save_template(*args):  #do we want to refactor this?
            new_template = {"Title" : "temporary title"}
            for child in self.template_editor.get_children():
                new_template[self.template_editor.item(child).get("text")] = "categories"
                category = {}
                for cat in self.template_editor.get_children(item=child):
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
                new_template[self.template_editor.item(child).get("text")] = category 
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
        self.subcategory_text_box_in_category_menu.pack(padx=10, pady=5)
        self.add_subcategory_button.pack(padx=10, pady=5)
        #sub-category selected
        self.context_subcategory.place(relx=0.74, rely=0.2, relwidth=0.18, relheight=0.70, anchor='nw')
        self.subcategory_label.pack()
        self.subcategory_textbox.pack(padx=10, pady=5)
        self.rename_subcategory_button.pack(padx=10, pady=5)
        self.moveup_subcategory_button.pack(padx=10, pady=5)
        self.movedown_subcategory_button.pack(padx=10, pady=5)
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
    def __init__(self, parent, main_menu_frame):
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
                print("Non-sub-category") 
            if self.budget_table.item(self.budget_table.parent(self.budget_table.parent(self.budget_table.focus()))).get("values") != "": 
                self.row = self.budget_table.identify_row(event.y)
                self.row_data = self.budget_table.item(self.row).get("values")
                if self.budget_table.item(self.row).get("values")[3] == 2: #annual subcat clicked 
                    box_location_annual = self.budget_table.bbox(self.row, column="#2")
                    self.annual = True
                    self.budget_entry = ctk.CTkEntry(self.budget_table, width=box_location_annual[2], height=box_location_annual[3])
                    self.budget_entry.place(x=box_location_annual[0], y=box_location_annual[1])
                    self.budget_entry.focus()
                    self.budget_entry.bind("<Return>", update_budget_table_entry)
                    self.budget_entry.bind("<FocusOut>", update_budget_table_entry)
                if self.budget_table.item(self.row).get("values")[3] == 1: #monthly subcat clicked
                    box_location_monthly = self.budget_table.bbox(self.row, column="#3")
                    self.annual = False
                    self.budget_entry = ctk.CTkEntry(self.budget_table, width=box_location_monthly[2], height=box_location_monthly[3])
                    self.budget_entry.place(x=box_location_monthly[0], y=box_location_monthly[1])
                    self.budget_entry.focus()
                    self.budget_entry.bind("<Return>", update_budget_table_entry)
                    self.budget_entry.bind("<FocusOut>", update_budget_table_entry)
            return "break"

        def update_budget_table_entry(*args):
            if self.annual == True:
                try:
                    self.row_data[1] = '${:,.2f}'.format(float(self.budget_entry.get())) 
                    self.budget_table.item(self.row, values=self.row_data)
                except ValueError:
                    print("value error")
            if self.annual == False:
                try:
                    self.row_data[2] = '${:,.2f}'.format(float(self.budget_entry.get()))
                    self.budget_table.item(self.row, values=self.row_data)
                except ValueError:
                    print('value error')
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
        blank_annuals = []
        blank_monthlies = []
        for inc_exp in self.budget_table.get_children(): #consider using identify_row(y) if loop thru all y's is doable, may require interaction with .index(item)
            for cat in self.budget_table.get_children(inc_exp):
                for subcat in self.budget_table.get_children(cat):
                    if self.budget_table.item(subcat).get("values")[3] == 2 and self.budget_table.item(subcat).get("values")[1] == "":
                        blank_annuals.append(self.budget_table.item(subcat).get("values")[0])                     
                    if self.budget_table.item(subcat).get("values")[3] == 1 and self.budget_table.item(subcat).get("values")[2] == "":
                        blank_monthlies.append(self.budget_table.item(subcat).get("values")[0])
        if blank_annuals != [] or blank_monthlies != []:
            self.blank_cells_found_error(blank_annuals, blank_monthlies)
        if blank_annuals == [] and blank_monthlies == []:
            self.account_selection()

    def blank_cells_found_error(self, blank_annuals, blank_monthlies):
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
        for index, cell in enumerate(blank_annuals):
            blank_annual_list_title = ctk.CTkLabel(blank_annual_scrolling_frame, text="Annual", font=("calibri", 20, "underline"))
            blank_annual_list_title.grid(row=0, column=0)
            blank_annual_list = ctk.CTkLabel(blank_annual_scrolling_frame, text=cell)
            blank_annual_list.grid(row=1+index, column=0)

        blank_monthly_scrolling_frame = ctk.CTkScrollableFrame(self.blank_cells_warning_window)
        blank_monthly_scrolling_frame.grid_columnconfigure(0, weight=1)
        blank_monthly_scrolling_frame.grid_rowconfigure(0, weight=1)
        for index, cell in enumerate(blank_monthlies):
            blank_monthlies_list_title = ctk.CTkLabel(blank_monthly_scrolling_frame, text="Monthly", font=("calibri", 20, "underline"))
            blank_monthlies_list_title.grid(row=0, column=0)
            blank_monthlies_list = ctk.CTkLabel(blank_monthly_scrolling_frame, text=cell)
            blank_monthlies_list.grid(row=1+index, column=0, pady=0)
        
        blank_cells_cancel = ctk.CTkButton(self.blank_cells_warning_window, text="Cancel", fg_color="#00aaff", font=("calibri", 18), command=lambda: self.blank_cells_warning_window.destroy())
        blank_cells_confirm = ctk.CTkButton(self.blank_cells_warning_window, text="Confirm", fg_color="#00aaff", font=("calibri", 18), command=self.account_selection)

        #layout
        blank_cells_message.grid(row=0, column=0, columnspan=2, sticky="new") 

        blank_annual_scrolling_frame.grid(row=1, column=0, padx=(10, 5), pady=(10, 0), sticky="nsew")
        blank_monthly_scrolling_frame.grid(row=1, column=1, padx=(0, 10), pady=(10, 0), sticky="nsew")

        blank_cells_cancel.grid(row=2, pady=10, column=0)
        blank_cells_confirm.grid(row=2, pady=10, column=1)
    
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
        account_selection_message_2 = ctk.CTkLabel(self.account_selection_window, text="-You can also add one if it is not in the provided list.", text_color="#00aaff", font=('calibri', 15))
        account_selection_message_3 = ctk.CTkLabel(self.account_selection_window, text="-For each account you choose, there will be an additional column for each month in your budget (So don't add too many!).", text_color="#00aaff", font=('calibri', 15))
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
                          Amount INTEGER,
                          Category_id integer,
                          Sub_Category_id integer, 
                          Date DATE
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
                          Amount integer, 
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
