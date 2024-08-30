import sqlite3
import tkinter as tk
import customtkinter

#create a new budget file. this creates the sql db (need file location to be set by user)
#also this needs to create the default budget categories
conn = sqlite3.connect("test.sqlite")
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
                  [Income/Expense] bit
    );

create table if not exists [Monthly Annual] (
                  id integer not null primary key autoincrement unique, 
                  [Monthly/Annual] bit
    )                                                                                                 

''')#date take form yyyy-mm-dd will likely need to be created from user input for each

#set default budget categories
#could have this command in a separate function, and allow user to alter the default
cur.executescript('''
            insert or ignore into [Category Name] (Category, Income_expense_id) Values ('Income', 1);
            insert or ignore into [Category Name] (Category, Income_expense_id) Values ('Housing', 2);
            insert or ignore into [Category Name] (Category, Income_expense_id) Values ('Regular Living Expenses', 2);
            insert or ignore into [Category Name] (Category, Income_expense_id) Values ('Transportation', 2);
            insert or ignore into [Category Name] (Category, Income_expense_id) Values ('Clothing', 2);
            insert or ignore into [Category Name] (Category, Income_expense_id) Values ('Medical', 2)          
''')

conn.commit()

#set default sub-categories and their monthly(1)/annual(2) status
default_sub_categories = {
                        "Income" : [["Employment", "Rent", "Investments", "Other"], [1,2,1,1]],
                        "Housing" : [["Rent", "Utilities", "Phone", "Internet", "TV/Streaming Services", "Maintenance", "Home Insurance", "Other"], [1,1,1,1,1,1,1,1]],
                        "Regular Living Expenses" : [["Groceries", "Delivery/Take Out", "Coffee/Treats", "Hygeine and Personal Grooming", "Appliances", "Computer Parts", "Entertainment", "Hobbies and Skill Development", "Bank/Credit Card Fees", "Taxes", "Other"], [1,1,1,1,1,1,1,1,1,2,1]],
                        "Transportation" : [["Transit Pass", "Car Share Services", "Fuel", "Insurance", "Maintenance", "Parking"], [1,1,1,2,1,1]],
                        "Clothing" : [["Everyday Use", "Special Occasion", "Other"], [1,1,1]],
                        "Medical" : [["Insurance (life)", "Insurance (Medical)", "Prescription Drugs", "Over the Counter Drugs", "Medical Services", "Paramedical Services", "Dental", "Vision Care", "Skin Care", "Other"], [2,2,1,1,1,1,1,1,1,1]]
                        }

for cat in default_sub_categories.items():
    print(cat[0])
    print(cat[1])
    cur.execute("select id from [Category Name] where Category = (?)", (cat[0], ))
    category_name_id = cur.fetchone()[0]
    print(category_name_id)
    print(cat[1][0])
    print(cat[1][1])
    for entry in range(len(cat[1][0])):
        print(cat[1][0][entry], cat[1][1][entry])
        cur.execute("insert into [Sub-Category Name] ([Sub-Category], Category_Name_id, Monthly_annual_id) Values (?, ?, ?)", (cat[1][0][entry], category_name_id, cat[1][1][entry]))
        conn.commit()
        

#add text to income expense and monthly annual tables directly 
#NOTE: never insert or ignore into these, so that id nums do not advnace beyond 1 and 2.
cur.execute("insert into [Income Expense] ([Income/Expense]) Values ('Income')")
cur.execute("insert into [Income Expense] ([Income/Expense]) Values ('Expense')")

cur.execute("insert into [Monthly Annual] ([Monthly/Annual]) Values ('Monthly')")
cur.execute("insert into [Monthly Annual] ([Monthly/Annual]) Values ('Annual')")
conn.commit()
