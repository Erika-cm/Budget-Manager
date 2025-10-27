from typing import Any
import customtkinter as ctk

from Logic import AppLogic

#main app window for testing
class MainWindow(ctk.CTk):
    def __init__(self, windowsize):
        super().__init__()
        self.geometry(f'{windowsize[0]}x{windowsize[1]}')

        self.app_logic = AppLogic(self)

        #widgets (program components)
        self.navigation_panel = NavigationPanel(self, self.app_logic)
        #testing
        self.main_menu = MainMenu(self, self.app_logic)
        self.comp1_1 = Comp1pg1(self, "System1", self.app_logic)
        self.comp1_2 = Comp1pg2(self, "System1", self.app_logic)
        self.comp2_1 = Comp2pg1(self, "System2", self.app_logic)
        self.comp2_2 = Comp2pg2(self, "System2", self.app_logic)

        #layout
        self.navigation_panel.place(relx=0.5, rely=1, relwidth=1, relheight=0.1, anchor='s')

        self.main_menu.place(relx=0.5, rely=0, relwidth=1, relheight=1, anchor='n')
        self.comp1_1.place(relx=0.5, rely=0, relwidth=1, relheight=0.9, anchor='n')
        self.comp1_2.place(relx=0.5, rely=0, relwidth=1, relheight=0.9, anchor='n')
        self.comp2_1.place(relx=0.5, rely=0, relwidth=1, relheight=0.9, anchor='n')
        self.comp2_2.place(relx=0.5, rely=0, relwidth=1, relheight=0.9, anchor='n')

        self.main_menu.tkraise()
        self.app_logic.give_logic_program_system_access(self.navigation_panel, self.main_menu)
        self.mainloop()

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

#classes for prototyping of navigation panel
class MainMenu(ctk.CTkFrame):
    def __init__(self, master: Any, app_logic: AppLogic):
        super().__init__(master)

        #Panel Chars
        self.grid_columnconfigure((0,2), weight=(1), uniform='a')
        self.grid_columnconfigure((1), weight=(4), uniform='a')
        self.grid_rowconfigure((0), weight=2)
        self.grid_rowconfigure((1,2,3), weight=1)
        self.grid_rowconfigure((4), weight=0)

        #Widgets
        self.main_menu_label = ctk.CTkLabel(self, text="Manage Your Money", text_color="#00aaff", font=('calibri', 65)) 

        self.create_new_button = ctk.CTkButton(self, text="Create a New Budget", fg_color="#00aaff", font=('calibri', 40), command=lambda: app_logic.system_selection("System1"))
        self.open_existing_button = ctk.CTkButton(self, text="Manage an Existing Budget", fg_color="#00aaff", font=('calibri', 40), command = lambda: app_logic.system_selection("System2"))
        self.options_button = ctk.CTkButton(self, text="Options", fg_color="#00aaff", font=('calibri', 40))

        self.version_note = ctk.CTkLabel(self, text="Version 0.2.1", text_color="#686868")

        #layout
        self.main_menu_label.grid(row=0, column=1, columnspan=1, sticky='ew')

        self.create_new_button.grid(row=1, column=1, padx=50, pady=10, sticky='ns')
        self.open_existing_button.grid(row=2, column=1, padx=50, pady=10, sticky='ns')
        self.options_button.grid(row=3, column=1, padx=10, pady=10, ipadx=110, sticky='ns') 

        self.version_note.grid(row=4, column=2)
        
        
class Comp1pg1(ctk.CTkFrame):
    def __init__(self, master: Any, system_name, app_logic: AppLogic):
        super().__init__(master)

        self.label = ctk.CTkLabel(self, text="Sys 1, Page 1").pack()

        app_logic.add_to_nav_map(system_name, self)   

class Comp1pg2(ctk.CTkFrame):
    def __init__(self, master: Any, system_name, app_logic: AppLogic):
        super().__init__(master)

        self.label = ctk.CTkLabel(self, text="Sys 1, Page 2").pack()

        app_logic.add_to_nav_map(system_name, self) 

class Comp2pg1(ctk.CTkFrame):
    def __init__(self, master: Any, system_name, app_logic: AppLogic):
        super().__init__(master)

        self.label = ctk.CTkLabel(self, text="Sys 2, Page 1").pack()

        app_logic.add_to_nav_map(system_name, self) 

class Comp2pg2(ctk.CTkFrame):
    def __init__(self, master: Any, system_name, app_logic: AppLogic):
        super().__init__(master)

        self.label = ctk.CTkLabel(self, text="Sys 2, Page 2").pack()

        app_logic.add_to_nav_map(system_name, self) 

if __name__ == "__main__":
    main_test = MainWindow((1000, 600))