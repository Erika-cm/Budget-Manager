import customtkinter as ctk
import os

from Logic import AppLogic, SystemNames
from Visuals import MainMenu, NavigationPanel, RadioButtonMenu, EditBudgetTemplate, EditBudget, AccountSelection, VisualFunctions, VisualThemes, ManageBudget

#NOTE: to create folding code block: ctrl+k then ctrl+, | to de-fold ctrl+k then ctrl+.

# A class for main app window
class MainWindow(ctk.CTk):
    def __init__(self, title, windowsize):
        super().__init__()
        
        #App window chars
        self.title(title)        
        self.geometry(f'{windowsize[0]}x{windowsize[1]}')
        self.minsize(windowsize[0], windowsize[1])

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
        self.manage_budget_table = ManageBudget(self, SystemNames.manage_budget_system, self.app_logic, self.visual_themes)

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
        self.manage_budget_table.place(relx=0.5, rely=0, relwidth=1, relheight=0.9, anchor='n')

        self.visual_functions.raise_panel(self.main_menu)
        self.app_logic.give_logic_program_system_access(self.visual_functions,
                                                        self.navigation_panel,
                                                        self.main_menu,
                                                        self.create_new_template_selection,
                                                        self.create_new_template_editor,
                                                        self.create_new_budget_editor,
                                                        self.create_new_account_selection,
                                                        self.manage_budget_file_selection,
                                                        self.manage_budget_table)
        self.app_logic.set_user_files_path()
        icon_path = self.app_logic.set_icon_file_path()
        if os.path.isfile(icon_path): #icon found, otherwise use default icon
            self.iconbitmap(icon_path)
        
        #enable adjustment of bounding box for systems that apply UI scaling (fixes Bbox appearing in wrong spot)
        self.visual_functions.update_window_data(self)
        self.app_logic.set_main_window_scaling_factor(self, windowsize[0])

def main()-> None:
    main_window = MainWindow("Manage Your Money", (1000, 600))
    main_window.mainloop()

if __name__ == "__main__":
    main()