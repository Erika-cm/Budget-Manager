import sqlite3
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import json
import os
import sys
from enum import Enum

from Logic import AppLogic, SystemNames, SaveObjectTypes
from Visuals import MainMenu, NavigationPanel, SaveNameWindow, RadioButtonMenu, EditBudgetTemplate, EditBudget, AccountSelection, VisualFunctions, VisualThemes

#NOTE: to create folding code block: ctrl+k then ctrl+,, to de-fold ctrl+k then ctrl+.

# A class for main app window
class MainWindow(ctk.CTk):
    def __init__(self, title, windowsize):
        super().__init__()
        
        #App window chars
        self.title(title)        
        self.geometry(f'{windowsize[0]}x{windowsize[1]}')

        #widgets
        #program components
        self.app_logic = AppLogic(self)
        self.visual_themes = VisualThemes(self)
        self.visual_functions = VisualFunctions(self)
        self.navigation_panel = NavigationPanel(self, self.app_logic)
        self.main_menu = MainMenu(self, SystemNames.create_new_system, SystemNames.manage_budget_system, self.app_logic)

        #system: create a new budget
        self.create_new_template_selection = RadioButtonMenu(self, SystemNames.create_new_system, self.app_logic, "Select A Budget Template")
        self.create_new_template_editor = EditBudgetTemplate(self, SystemNames.create_new_system, self.app_logic, self.visual_themes)
        self.create_new_budget_editor = EditBudget(self, SystemNames.create_new_system, self.app_logic, self.visual_themes)
        self.create_new_account_selection = AccountSelection(self, SystemNames.create_new_system, self.app_logic)

        #system: manage an existing budget
        self.manage_budget_file_selection = RadioButtonMenu(self, SystemNames.manage_budget_system, self.app_logic, "Open Existing Budget")

        #layout
        self.navigation_panel.place(relx=0.5, rely=1, relwidth=1, relheight=0.1, anchor='s')
        self.main_menu.place(relx=0.5, rely=0, relwidth=1, relheight=1, anchor='n')

        #system: create a new budget
        self.create_new_template_selection.place(relx=0.5, rely=0, relwidth=1, relheight=0.9, anchor='n')
        self.create_new_template_editor.place(relx=0.5, rely=0, relwidth=1, relheight=0.9, anchor='n')
        self.create_new_budget_editor.place(relx=0.5, rely=0, relwidth=1, relheight=0.9, anchor='n')
        self.create_new_account_selection.place(relx=0.5, rely=0, relwidth=1, relheight=0.9, anchor='n')

        #system: manage an existing budget
        self.manage_budget_file_selection.place(relx=0.5, rely=0, relwidth=1, relheight=0.9, anchor='n')

        self.visual_functions.raise_panel(self.main_menu)
        self.app_logic.give_logic_program_system_access(self.visual_functions, self.navigation_panel, self.main_menu, self.create_new_template_selection, self.create_new_template_editor, self.create_new_budget_editor, self.create_new_account_selection, self.manage_budget_file_selection)
        self.app_logic.set_user_files_path()
        icon_path = self.app_logic.set_icon_file_path()
        if os.path.isfile(icon_path): #icon found, otherwise use default icon
            self.iconbitmap(icon_path)
        
        #enable adjustment of bounding box for systems that apply UI scaling (fixes Bbox appearing in wrong spot)
        self.visual_functions.update_window_data(self)
        self.app_logic.set_main_window_scaling_factor(self, windowsize[0])
            
    
    '''def transaction_list_window(self):
        self.manage_budget_p2.selected_cell_transaction_list()
    
    def transaction_editor_window(self):
        self.manage_budget_p2.get_selected_cell_info(called_by_manager=1)'''


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
        self.budget_file_path = user_files_path + "\\" + self.budget_filename.get()
        conn = sqlite3.connect(self.budget_file_path) 
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
        conn = sqlite3.connect(self.budget_file_path) 
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
        conn = sqlite3.connect(self.budget_file_path) 
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
        conn = sqlite3.connect(self.budget_file_path) 
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
        conn = sqlite3.connect(self.budget_file_path) 
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
        conn = sqlite3.connect(self.budget_file_path) 
        cur = conn.cursor()
        if modification == "new":
            transacation_cat_id = self.selected_cell_info_list[3][1]
            transacation_subcat_id = self.selected_cell_info_list[4][1]
            transacation_account_id = self.selected_cell_info_list[1][1]
            cur.execute("insert into Transactions (Amount, [Category_id], [Sub_Category_id], [Account_Type_id], Month) Values (?, ?, ?, ?, ?)", (transaction[-1], transacation_cat_id, transacation_subcat_id, transacation_account_id, transaction[5]))
        elif modification == "modified":
            cur.execute("select id from [Category Name] where Category = ?", (transaction[2], ))
            cat_id = cur.fetchone()[0]
            cur.execute("select id from [Sub-Category Name] where ([Sub-Category], [Category_Name_id]) = (?, ?)", (transaction[3], cat_id))
            subcat_id = cur.fetchone()[0]
            cur.execute("select id from Accounts where [Account Name] = ?", (transaction[4], ))
            account_id = cur.fetchone()[0]
            cur.execute("update Transactions set Amount = ?, [Category_id] = ?, [Sub_Category_id] = ?, [Account_Type_id] = ?, Month = ? where id = ?", (transaction[-1], cat_id, subcat_id, account_id, transaction[5], transaction[0]))
        elif modification == "deleted":
            cur.execute("delete from Transactions where id = ?", (transaction[0], ))
        conn.commit()
                
    #update the transaction list when transactions added, edited, and deleted
    def confirm_transaction_edits(self, button, called_by_manager=0):
        # combo_var_tab is text, must be converted back into corresponding number in transactions_list (so it can be output to DB)
        tab_num = [pair[0] for pair in enumerate(self.tab_list) if pair[1] == self.combo_var_tab.get()][0]
        if called_by_manager == 1: #addnew was pressed from editor window, skip updating of list window and call add_new_transaction
            self.add_new_transaction()
        if called_by_manager == 0 and button == "addnew": #addnew or edit was pressed from list window, update list window then call add_new_transaction
            new_transaction_checkbox = ctk.CTkCheckBox(self.cell_transaction_list_frame, text=self.entry_var_amount.get() + " new", command=self.user_selects_transaction)
            self.list_of_transaction_checkboxes.append(new_transaction_checkbox)
            new_transaction_checkbox.grid(row=len(self.list_of_transaction_checkboxes), column=0, sticky="wn", pady=5, padx=5)
            self.checkbox_statuses.append(0)
            self.transactions_list.append([0, self.combo_var_incexp.get(), self.combo_var_cat.get(), self.combo_var_subcat.get(), self.combo_var_account.get(), tab_num, self.transaction_editor_amount])
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

def main()-> None:
    main_window = MainWindow("Manage Your Money", (1000, 600))
    main_window.mainloop()

if __name__ == "__main__":
    main()