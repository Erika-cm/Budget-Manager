import json

user_generated_template_1 = {
                        "Title" : 
                        "User Template 1",
                        "Income" : 
                        {"All Income" : [["Employment", "Rent", "Other"], [1,2,1]]},
                        "Expenses" : 
                        {"Housing" : [["Condo Fees", "Utilities", "Phone", "Internet", "TV/Streaming Services", "Maintenance", "Home Insurance", "Other"], [1,1,1,1,1,1,1,1]],
                        "Regular Living Expenses" : [["Groceries", "Delivery/Take Out", "Coffee/Treats", "Hygeine and Personal Grooming", "Appliances", "Computer Parts", "Entertainment", "Hobbies and Skill Development", "Bank/Credit Card Fees", "Taxes", "Other"], [1,1,1,1,1,1,1,1,1,2,1]],
                        "Transportation" : [["Transit Pass", "Car Share Services", "Fuel", "Insurance", "Maintenance", "Parking"], [1,1,1,2,1,1]],
                        "Clothing" : [["Everyday Use", "Special Occasion", "Other"], [1,1,1]],
                        "Medical" : [["Insurance (life)", "Insurance (Medical)", "Prescription Drugs", "Over the Counter Drugs", "Medical Services", "Paramedical Services", "Dental", "Vision Care", "Skin Care", "Other"], [2,2,1,1,1,1,1,1,1,1]]}
                        }

user_generated_template_2 = {
                        "Title" : 
                        "User Template 2",
                        "Income" : 
                        {"All Income" : [["Employment", "Investments", "Business", "Other"], [1,1,1,1]]},
                        "Expenses" : 
                        {"Housing" : [["Rent", "Utilities", "Phone", "Internet", "TV/Streaming Services", "Maintenance", "Other"], [1,1,1,1,1,1,1]],
                        "Regular Living Expenses" : [["Groceries", "Delivery/Take Out", "Coffee/Treats", "Hygeine and Personal Grooming", "Appliances", "Computer Parts", "Entertainment", "Hobbies and Skill Development", "Bank/Credit Card Fees", "Taxes", "Other"], [1,1,1,1,1,1,1,1,1,2,1]],
                        "Transportation" : [["Transit Pass", "Car Share Services", "Fuel", "Insurance", "Maintenance", "Parking"], [1,1,1,2,1,1]],
                        "Clothing" : [["Everyday Use", "Special Occasion", "Other"], [1,1,1]],
                        "Medical" : [["Insurance (life)", "Insurance (Medical)", "Prescription Drugs", "Over the Counter Drugs", "Medical Services", "Paramedical Services", "Dental", "Vision Care", "Skin Care", "Other"], [2,2,1,1,1,1,1,1,1,1]]}
                        }

user_templates = [user_generated_template_1, user_generated_template_2]

json_objects = json.dumps(user_templates, indent=4)

with open('budget templates.json', 'w') as outfile:
    outfile.write(json_objects)

#code for reading JSON adding user templates
# default_sub_categories = {
#                         "Title" : "Default",
#                         "Income" : [["Employment", "Rent", "Investments", "Other"], [1,2,1,1]],
#                         "Housing" : [["Rent", "Utilities", "Phone", "Internet", "TV/Streaming Services", "Maintenance", "Home Insurance", "Other"], [1,1,1,1,1,1,1,1]],
#                         "Regular Living Expenses" : [["Groceries", "Delivery/Take Out", "Coffee/Treats", "Hygeine and Personal Grooming", "Appliances", "Computer Parts", "Entertainment", "Hobbies and Skill Development", "Bank/Credit Card Fees", "Taxes", "Other"], [1,1,1,1,1,1,1,1,1,2,1]],
#                         "Transportation" : [["Transit Pass", "Car Share Services", "Fuel", "Insurance", "Maintenance", "Parking"], [1,1,1,2,1,1]],
#                         "Clothing" : [["Everyday Use", "Special Occasion", "Other"], [1,1,1]],
#                         "Medical" : [["Insurance (life)", "Insurance (Medical)", "Prescription Drugs", "Over the Counter Drugs", "Medical Services", "Paramedical Services", "Dental", "Vision Care", "Skin Care", "Other"], [2,2,1,1,1,1,1,1,1,1]]
#                         }

# template_list = [default_sub_categories]
# try:
#     with open('budget templates.json', 'r') as infile:
#         json_readbudgets = json.load(infile)
#         for template in json_readbudgets:
#             template_list.append(template)
# except ValueError:
#     print("oops!")

# print(template_list) #this is a list
# print("")

# for entry in template_list:
#     print(entry)
#     print("")
    # for line in entry.items():
    #     print(line)
    #     print("")