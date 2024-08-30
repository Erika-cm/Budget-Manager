import pandas as pd
from tabulate import tabulate #used to display budget to user
import xlsxwriter as xls

#create default budget template as dataframes
budgetgroup_income = pd.DataFrame({
    "Income": 
    [
    "Employment",
    "Transfers from Investments"    
    ],
    "Is Annual": [
        0,0 #add an annual for testing
    ] 
})  

budget_groups = []

#set up default budget expense groups and categories
for n in range(0,2):
    if n==0:
        budgetgroup_expenses = pd.DataFrame({
        "Housing":
        [
        "Rent",
        "Utilities",
        "Phone",
        "Internet",
        "Streaming Services",
        "Maintenance (Cleaning, Repairs, Tools)",
        "Insurance"
        ],
        "Is Annual": [
            0,0,0,0,0,0,1
        ]
        })
        budgetgroup_expenses.name = budgetgroup_expenses.columns[0]
        budget_groups.append(budgetgroup_expenses)
    if n==1:
        budgetgroup_expenses = pd.DataFrame({
        "Regular Living Expenses": 
        [
        "Groceries",   
        "Delivery/Takeout",
        "Alcohol",
        "Coffee and Treats",
        "Hygeine and Personal Grooming",
        "Appliances and Furniture",
        "Computer Parts/Devices",
        "Entertainment",
        "Hobbies and Skill Development",
        "Bank/Credit Card Fees/Interest",
        "Cash",
        "Donations",
        "Taxes"
        ],
        "Is Annual": [
            0,0,0,0,0,0,0,0,0,0,0,0,1
        ]
        })
        budgetgroup_expenses.name = budgetgroup_expenses.columns[0]
        budget_groups.append(budgetgroup_expenses)

#this function will be called on program start
#BUG - if user input anything other than c or o, program ends
def mainmenu():
    mainmenu_options = input("Options: \n Create New Budget [C] \n Open an Existing Budget [O] \n Type [C] or [O]: ")
    if mainmenu_options.lower().startswith("c"):
        create_budget()
    if mainmenu_options.lower().startswith("o"):
        print("that option doesn't exist yet")
        mainmenu() #this will eventually call a function that opens an existing budget

#user wants to create new buget
def create_budget():
    
    print("\n Here are the Default Budget Categories \n")

    print(tabulate(budgetgroup_income.loc[:, budgetgroup_income.columns != "Is Annual"], showindex=False, headers="keys"))
    print("\nExpenses\n")
    print(tabulate(budget_groups[0].loc[:, budget_groups[0].columns != "Is Annual"], showindex=False, headers="keys"))
    print("")
    print(tabulate(budget_groups[1].loc[:, budget_groups[1].columns != "Is Annual"], showindex=False, headers="keys"))
    
    #user accepts default or chooses to edit
    print("\nDo you want to use the default categories?")
    default_accept = input("Type [Y] to accept, [N] to edit: ")
    print("You chose: " + default_accept)

    #if user accepts default call function to output to excel
    if default_accept.lower().startswith("y"):
        enter_budget() #process to define budget amounts 
        #need process to deal with annual budget items here
        export_budget()
    
    #if user selects no, call budget edit function
    if default_accept.lower().startswith("n"):
        edit_budget()

def enter_budget():
    print("\nEnter Monthly Amounts for Income/Expenses. \nHit 'Enter' to Advance to Next Category")
    print("\nIncome")
    budget_continue = ""
    global annual_detected #other functions need to know if annual is present
    annual_detected = 0 #indictor: presense of at least 1 annual budget item
    global annual_entered #same with whether an annual amount was entered
    annual_entered = 0

    while budget_continue.lower().startswith("a") == False:
        #process to enter income amounts
        blank_category = 0
        annual_income_entered = 0
        for row in budgetgroup_income.index:
            if budgetgroup_income.loc[row,  "Is Annual"] == 1: #is annual
                annual_detected = 1
                if "Annual Budget" not in budgetgroup_income.columns:
                    budgetgroup_income.insert(1, "Annual Budget", "")
                b_category = budgetgroup_income["Income"][row]
                budgetgroup_income.loc[row, ["Budget"]] = ""
                try:
                    print("\nNote: The next Category is Classified as an Annual Budget Item")
                    budget_amount = float(input("Enter amount for " + b_category + ": "))
                    budget_amount = "{:.2f}".format(budget_amount)
                    annual_income_entered = 1
                except ValueError:
                    budget_amount = ""
                budgetgroup_income.loc[row, ["Annual Budget"]] = budget_amount
            else: #is not annual
                b_category = budgetgroup_income["Income"][row]
                try:
                    budget_amount = float(input("Enter amount for " + b_category + ": "))
                    budget_amount = "{:.2f}".format(budget_amount)
                except ValueError:
                    blank_category = 1
                    budget_amount = ""
                budgetgroup_income.loc[row, ["Budget"]] = budget_amount
        if blank_category == 1:
            print("\nWarning! This Budget Group Contains a Blank Category")
            input("Hit Enter to Continue: ")
        if annual_detected == 1 and annual_income_entered == 0:
            print("\nWarning! This Budget Group Contains a Blank Annual Category")
            input("Hit Enter to Continue: ")
        print("\nSummary of Current Budget for Income: \n")
        print(tabulate(budgetgroup_income.loc[:, budgetgroup_income.columns != "Is Annual"], showindex=False, headers="keys")) 
        print("")  
        budget_continue = input("\nEnter [A] to Accept, or [R] to Restart: ")
        if budget_continue.lower().startswith("a"):
            annual_entered = annual_income_entered
        if budget_continue.lower().startswith("r"):
            continue

    #process to enter expense amounts
    print("\nExpenses")
    for group in budget_groups:
        budget_continue = ""
        print("Budget Group: " + group.name)
        while budget_continue.lower().startswith("a") == False:
            blank_category = 0
            annual_expense_entered = 0
            for row in group.index:
                if group.loc[row, "Is Annual"] == 1: #is annual
                    annual_detected = 1
                    if "Annual Budget" not in group.columns:
                        group.insert(1, "Annual Budget", "")
                    b_category = group[group.name][row]
                    group.loc[row, ["Budget"]] = ""
                    try:
                        print("\nNote: The next Category is Classified as an Annual Budget Item")
                        budget_amount = float(input("Enter amount for " + b_category + ": "))
                        budget_amount = "{:.2f}".format(budget_amount)
                        annual_expense_entered = 1
                    except ValueError:
                        budget_amount = ""
                    group.loc[row, ["Annual Budget"]] = budget_amount
                else: #is not annual
                    b_category = group[group.name][row]
                    try:
                        budget_amount = float(input("Enter amount for " + b_category + ": "))
                        budget_amount = "{:.2f}".format(budget_amount)
                    except ValueError:
                        blank_category = 1
                        budget_amount = ""
                    group.loc[row, ["Budget"]] = budget_amount
            if blank_category == 1:
                print("\nWarning! This Budget Group Contains a Blank Category")
                input("Hit Enter to Continue: ")
            if annual_detected == 1 and annual_expense_entered == 0:
                print("\nWarning! This Budget Group Contains a Blank Annual Category")
                input("Hit Enter to Continue: ")
            print("\nSummary of Current Budget for: " + group.name + "\n")
            print(tabulate(group.loc[:, group.columns != "Is Annual"], showindex=False, headers="keys"))
            print("")
            budget_continue = input("\n Enter [A] to Accept, or [R] to Restart: \n")
            if budget_continue.lower().startswith("a"):
                if annual_entered == 0: #only update annual entered if not already = 1
                    annual_entered = annual_expense_entered
            if budget_continue.lower().startswith("r"):
                continue
    #add annual col to groups without their own if annual present in any and...
    #add 'Other' as empty row to each group
    input("Adding Annual Column and 'Other' Row, hit enter: ")
    if annual_detected == 1:
        if "Annual Budget" not in budgetgroup_income.columns:
            budgetgroup_income.insert(1, "Annual Budget", "")
            budgetgroup_income.loc[len(budgetgroup_income.index)] = ["Other", "", "", ""]
        for group in budget_groups:
            if "Annual Budget" not in group.columns:
                group.insert(1, "Annual Budget", "")
            group.loc[len(group.index)] = ["Other", "", "", ""]
    if annual_detected == 0: #no annual item, so empty row is 3 cols wide
        budgetgroup_income.loc[len(budgetgroup_income.index)] = ["Other", "", ""]
        for group in budget_groups:
            group.loc[len(group.index)] = ["Other", "", ""]


                
def edit_budget():
    #need process to add/remove budget categories
    #need process to define budget amounts here
    #need process to deal with annual budget items here
    print("This function doeen't exist yet")
    mainmenu()

def export_budget():
    #write budget to excel
    #This is where warnings about blank ANNUAL categories would appear
    #plan: present completed budget to user
    #then: warn that annual cat is present but left empty (note that empty monthlys are normal)
    #then: If user accepts output budget without the annual col
    #if user does not give options return to mainmenu(), create_budget(), or enter_budget()
    set_budgetfilename()
    #temp code: display comepleted budget
    if annual_detected == 1 and annual_entered == 1:
        print("Here is your completed budget:\n")
        print(tabulate(budgetgroup_income.loc[:, budgetgroup_income.columns != "Is Annual"], showindex=False, headers="keys")) 
        print("")  
        for group in budget_groups:
            print(tabulate(group.loc[:, group.columns != "Is Annual"], showindex=False, headers="keys"))
            print("")
    if annual_detected == 1 and annual_entered == 0: #do not display annual col, if all annual amounts left blank
        print("Here is your completed budget:\n")
        print(tabulate(budgetgroup_income.loc[:, ~budgetgroup_income.columns.isin(["Is Annual", "Annual Budget"])], showindex=False, headers="keys")) 
        print("")  
        for group in budget_groups:
            print(tabulate(group.loc[:, ~group.columns.isin(["Is Annual", "Annual Budget"])], showindex=False, headers="keys"))
    print("\nExporting Budget to Excel...eventually")
    
#this function will define the filename, 
#and should be called just prior to exporting
#eventually this will have directory selection
def set_budgetfilename():
    global budget_filename
    budget_filename = input("Choose Filename: ")

#if user selects N, allow user to remove categories, and add new ones
#to add catgories:maybe use pd.concat([seriesname], ignore_index=True <-"this resets the resulting index")
#maybe use list comprehensions to create new list/dataframe from old exclusing those selected.

#greeting to user, and present basic options
print("\nHello!, Welcome to Erika's Budget Manager.\n")
mainmenu()