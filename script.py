import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from datetime import datetime
import json

# defining color constants
BUTTERSCOTCH_ORANGE = '#E3963E'  # for selected record
BLUE_GRAY = '#7393B3'  # as the background color
ASH_GRAY = '#B2BEB5'  # for the field background in tree view
AQUA_BLUE = '#00FFFF'  # for buttons
ROBIN_EGG_BLUE = '#96DED1'  # for the income
VERDIGRIS_BLUE = '#40B5AD'  # for the expenses
BABY_BLUE = '#89CFF0'  # for the search frame
AZURE_BLUE = '#F0FFFF'
LIGHT_BLUE = '#ADD8E6'

DATE_FORMAT = "%Y-%m-%d"  # YYYY-MM-DD date format for transactions
SPECIAL_CHARS = '\'~!#@$%^*()_+-={}|[]\\:<>?,./'

SMALL_FONT_STYLE = ("Arial", 10, 'bold')
TITLE_FONT_STYLE = ("Times New Roman", 20, "bold")


class finance_tracker:
    def __init__(self, root):
        self.root = root
        self.root.resizable(False, False)
        self.root.title('Personal Finance Tracker')
        self.root.iconbitmap(r'C:\Users\USER\Desktop\SD1_Courseworks\COURSEWORK_03\tracker_icon.ico')
        self.FILE_PATH = 'transactions.json'
        self.transactions = self.load_transaction()
        self.create_widgets()
        self.max_id = max(transaction['id'] for category in self.transactions.values() for transaction in category) if self.transactions else 0
        self.search_transactions()
        self.display_summary()
        self.bulk_transactions()

    # adding data to the screen
    def insert_data(self):
        self.count = 0
        for item in self.transactions.keys():
            for record in self.transactions.get(item):
                if record['type'] == 'Income':
                    self.my_tree.insert(parent='', index='end', iid=self.count, text='',
                                        values=(
                                            record['type'], item, f'{record['amount']:,.2f}', record['date'],
                                            record['id']),
                                        tags=('income_row',))
                elif record['type'] == 'Expense':
                    self.my_tree.insert(parent='', index='end', iid=self.count, text='',
                                        values=(
                                            record['type'], item, f'{record['amount']:,.2f}', record['date'],
                                            record['id']),
                                        tags=('expense_row',))
                self.count += 1  # increment counter

    def create_widgets(self, col=None):

        # create label
        display_title = tk.Label(self.root, text="Manage Your Transactions Here!",
                                 anchor="center", font=TITLE_FONT_STYLE, bg=BLUE_GRAY)
        display_title.pack()

        # Add Some style
        style = ttk.Style()

        # pick a theme
        style.theme_use('clam')  # themes - defaults, alt, clam, vista

        # configure our treeview colors
        style.configure('Treeview',
                        background='White',
                        foreground='Black',
                        rowheight=25,
                        fieldbackground=ASH_GRAY)
        # change selected color
        style.map('Treeview',
                  background=[('selected', BUTTERSCOTCH_ORANGE)])

        # create treeview frame
        tree_frame = tk.Frame(self.root)
        tree_frame.configure(bg=BLUE_GRAY)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # create treeview scroll bar
        tree_scroll = tk.Scrollbar(tree_frame)
        tree_scroll.configure(bg=BLUE_GRAY, relief=tk.FLAT)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # create the tree view
        self.my_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode=tk.EXTENDED)
        self.my_tree.pack(fill=tk.BOTH, padx=10)

        # defining columns
        self.my_tree['columns'] = (
            'Transaction Type', 'Transaction Category', 'Transaction Amount', 'Transaction Date', 'Transaction ID')

        # configure scroll bars
        tree_scroll.configure(command=self.my_tree.yview)

        # format columns
        self.my_tree.column('#0', width=0, stretch=False)
        for col in self.my_tree['columns']:
            self.my_tree.column(col, anchor=tk.CENTER, width=120)

        # create headings
        self.my_tree.heading('#0', text='', anchor=tk.W)
        for col in self.my_tree['columns']:
            self.my_tree.heading(col, text=col, anchor=tk.CENTER,
                                 # set default value to col argument
                                 command=lambda col=col: self.sort_by_column(self.my_tree, col, False))

        # create transaction type based striped row tags
        self.my_tree.tag_configure('income_row', background=ROBIN_EGG_BLUE)
        self.my_tree.tag_configure('expense_row', background=VERDIGRIS_BLUE)

        self.insert_data()  # adding data

        # Add record entry boxes
        data_frame = tk.LabelFrame(self.root, text='Record')
        data_frame.configure(bg=BLUE_GRAY)
        data_frame.pack(fill=tk.X, expand=tk.YES, padx=20)

        # create labels
        type_label = tk.Label(data_frame, text='Transaction Type', font=SMALL_FONT_STYLE, bg=BLUE_GRAY)
        category_label = tk.Label(data_frame, text='Transaction Category', font=SMALL_FONT_STYLE,
                                  bg=BLUE_GRAY)
        amount_label = tk.Label(data_frame, text='Transaction Amount', font=SMALL_FONT_STYLE, bg=BLUE_GRAY)
        date_label = tk.Label(data_frame, text='Transaction Date', font=SMALL_FONT_STYLE, bg=BLUE_GRAY)

        # positioning labels
        type_label.grid(row=0, column=0, padx=50, pady=10)
        category_label.grid(row=0, column=1, padx=50, pady=10)
        amount_label.grid(row=0, column=2, padx=50, pady=10)
        date_label.grid(row=0, column=3, padx=50, pady=10)

        # defining an option menu for transaction type
        self.transaction_options_list = ['Income', 'Expense']
        self.option_variable = tk.StringVar()
        self.option_variable.set('Transaction Type')
        self.transaction_type_option_menu = tk.OptionMenu(data_frame, self.option_variable,
                                                          *self.transaction_options_list)

        # declaring string variables for entry boxes
        self.category_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.date_var = tk.StringVar()

        # create entry boxes
        self.category_box = tk.Entry(data_frame, textvariable=self.category_var)
        self.amount_box = tk.Entry(data_frame, textvariable=self.amount_var)
        self.date_box = tk.Entry(data_frame, textvariable=self.date_var)

        # positioning entries and dropdown menu
        self.transaction_type_option_menu.grid(row=1, column=0, padx=50, pady=10)
        self.category_box.grid(row=1, column=1, padx=50, pady=10)
        self.amount_box.grid(row=1, column=2, padx=50, pady=10)
        self.date_box.grid(row=1, column=3, padx=50, pady=10)

        # Creating buttons frame for adding buttons
        self.button_frame = tk.LabelFrame(self.root, text='Commands')
        self.button_frame.pack(fill=tk.X, expand=tk.YES, padx=20)
        self.button_frame.configure(bg=BLUE_GRAY)

        # creating menu
        menu = tk.Menu(self.root, bg=AZURE_BLUE)
        self.root.configure(menu=menu)

        # creating search submenu
        self.search_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='Search', menu=self.search_menu)

        # creating view submenu
        self.view_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='View', menu=self.view_menu)

        # creating bulk reading submenu
        self.bulk_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='Read', menu=self.bulk_menu)

    # loading data from the JSON file
    def load_transaction(self):
        try:
            with open(self.FILE_PATH, 'r') as file:
                transactions = json.load(file)
                return transactions
        except FileNotFoundError:
            command = tk.messagebox.askyesno('File Does not exist', 'Do you wish to create an empty File?')
            if command is True:
                with open('transactions.json', 'w') as file:
                    tk.messagebox.showinfo('File Creation Success', 'File created successfully in the directory')
                return {}
            elif command is False:
                tk.messagebox.showinfo('Creation Unsuccessful', 'File Creation cancelled')
                self.transactions = {}
                return {}
        except json.JSONDecodeError:
            tk.messagebox.showinfo('Zero Details', 'Zero Details Found. Start Recording Your financial content!!!')
            return {}

    # saving data to JSON file
    def save_transaction(self):
        try:
            with open(self.FILE_PATH, "w") as file:
                json.dump(self.transactions, file, indent=2)  # write data to file with indentation for readability
        except FileNotFoundError:
            tk.messagebox.showerror('File Not Found', 'Transaction File Not Found. Please Check and Retry.')
        except json.JSONDecodeError:
            tk.messagebox.showerror('JSON Decode Error', 'An Error Occurred While Serializing JSON Data')

    # exit GUI
    def exit_program(self):
        self.root.destroy()

    # remove data from GUI
    def remove_tree(self):
        for record in self.my_tree.get_children():  # gets the list of all the children
            self.my_tree.delete(record)

    # search transactions
    def search_transactions(self):

        # enabling rest command after search process
        def enable_reset_command():
            self.search_menu.entryconfigure('Reset', state=tk.NORMAL)

        # disabling other search options after search process
        def disable_search_options():
            self.search_menu.entryconfig('Search By Date', state=tk.DISABLED)
            self.search_menu.entryconfig('Search By Amount', state=tk.DISABLED)
            self.search_menu.entryconfig('Search By Transaction Type', state=tk.DISABLED)
            self.search_menu.entryconfig('Search By Category Type', state=tk.DISABLED)

        # resetting tree after search process
        def reset():
            self.remove_tree()
            self.insert_data()
            self.search_menu.entryconfigure('Reset', state=tk.DISABLED)
            self.search_menu.entryconfig('Search By Date', state=tk.NORMAL)
            self.search_menu.entryconfig('Search By Amount', state=tk.NORMAL)
            self.search_menu.entryconfig('Search By Transaction Type', state=tk.NORMAL)
            self.search_menu.entryconfig('Search By Category Type', state=tk.NORMAL)

        def search_by_date():
            search_toplevel = tk.Toplevel(self.root)
            search_toplevel.title('Search By Date')
            search_toplevel.configure(bg=BABY_BLUE)
            search_toplevel.geometry('400x200')
            search_toplevel.resizable(False, False)
            search_toplevel.iconbitmap(r'C:\Users\USER\Desktop\SD1_Courseworks\COURSEWORK_03\tracker_icon.ico')

            # create label frame
            search_frame = tk.LabelFrame(search_toplevel, text='Date', bg=LIGHT_BLUE)
            search_frame.pack(padx=10, pady=10)

            # create entry box
            search_entry = tk.Entry(search_frame, font=('Helvetica', 18))
            search_entry.pack(padx=20, pady=20)
            search_entry.focus_force()

            def search_records():
                try:
                    lookup_record_str = search_entry.get()
                    date_conversion = datetime.strptime(lookup_record_str, DATE_FORMAT).date()
                    self.lookup_record = date_conversion.strftime(DATE_FORMAT)
                    search_toplevel.destroy()
                    tk.messagebox.showinfo("Search", f"Searching for: {self.lookup_record}")
                    self.remove_tree()
                    for record in self.transactions:
                        for transaction in self.transactions[record]:
                            if transaction['date'] == self.lookup_record:
                                if transaction['type'] == 'Income':
                                    self.my_tree.insert(parent='', index='end', text='',
                                                        values=(transaction['type'], record, transaction['amount'],
                                                                transaction['date'], transaction['id']),
                                                        tags='income_row')

                                elif transaction['type'] == 'Expense':
                                    self.my_tree.insert(parent='', index='end', text='',
                                                        values=(transaction['type'], record, transaction['amount'],
                                                                transaction['date'], transaction['id']),
                                                        tags='expense_row')
                                disable_search_options()
                    if len(self.my_tree.get_children()) == 0:
                        tk.messagebox.showinfo("Search Unsuccessful", 'No Records Were Found')
                        disable_search_options()
                except ValueError:
                    tk.messagebox.showerror('Date Error', 'Please enter a valid date in the format: YYYY-MM-DD')
                    search_entry.delete(0, tk.END)  # Clear the entry box for re-input
                    search_entry.focus()  # Set focus back to the entry box for user input

            enable_reset_command()

            # Add button
            search_button = tk.Button(search_frame, text='Search Records', command=search_records, bg=AQUA_BLUE,
                                      relief=tk.FLAT, font=SMALL_FONT_STYLE)
            search_button.pack(padx=20, pady=20)

        def search_by_amount():
            search_toplevel = tk.Toplevel(self.root)
            search_toplevel.title('Search By Amount')
            search_toplevel.configure(bg=BABY_BLUE)
            search_toplevel.geometry('400x200')
            search_toplevel.resizable(False, False)
            search_toplevel.iconbitmap(r'C:\Users\USER\Desktop\SD1_Courseworks\COURSEWORK_03\tracker_icon.ico')

            # create label frame
            search_frame = tk.LabelFrame(search_toplevel, text='Amount', bg=LIGHT_BLUE)
            search_frame.pack(padx=10, pady=10)

            # create entry box
            search_entry = tk.Entry(search_frame, font=('Helvetica', 18))
            search_entry.pack(padx=20, pady=20)

            search_entry.focus_force()

            def search_records():
                lookup_record_str = search_entry.get()

                if not lookup_record_str.isnumeric():
                    tk.messagebox.showerror('Amount Error',
                                            'Invalid Value for a Amount. Please Enter a Valid Value for the Amount')

                    search_entry.delete(0, tk.END)  # Clear the entry box for re-input
                    search_entry.focus_force()
                    return
                try:
                    self.lookup_record = float(lookup_record_str)
                except ValueError:
                    tk.messagebox.showerror('Amount Error',
                                            'Invalid Value for a Amount. Please Enter a Valid Value for the Amount')
                    search_toplevel.destroy()  # closing the search box
                    search_entry.delete(0, tk.END)  # Clear the entry box for re-input
                    search_entry.focus()  # Set focus back to the entry box for user input
                    return

                search_toplevel.destroy()  # closing the search box
                tk.messagebox.showinfo("Search", f"Searching for: {self.lookup_record}")

                self.remove_tree()

                for record in self.transactions:
                    for transaction in self.transactions[record]:
                        if transaction['amount'] == self.lookup_record:
                            if transaction['type'] == 'Income':
                                self.my_tree.insert(parent='', index='end', text='',
                                                    values=(transaction['type'], record, transaction['amount'],
                                                            transaction['date'], transaction['id']), tags='income_row')

                            elif transaction['type'] == 'Expense':
                                self.my_tree.insert(parent='', index='end', text='',
                                                    values=(transaction['type'], record, transaction['amount'],
                                                            transaction['date'], transaction['id']), tags='expense_row')
                            disable_search_options()
                if len(self.my_tree.get_children()) == 0:
                    tk.messagebox.showinfo("Search Unsuccessful", 'No records matching the search criteria were found.')
                    disable_search_options()

            enable_reset_command()
            # Add button
            search_button = tk.Button(search_frame, text='Search Records', command=search_records, bg=AQUA_BLUE,
                                      relief=tk.FLAT, font=SMALL_FONT_STYLE)
            search_button.pack(padx=20, pady=20)

        # search by transaction type
        def search_by_type():
            search_toplevel = tk.Toplevel(self.root)
            search_toplevel.title('Search By Transaction Type')
            search_toplevel.configure(bg=BABY_BLUE)
            search_toplevel.geometry('400x200')
            search_toplevel.resizable(False, False)
            search_toplevel.iconbitmap(r'C:\Users\USER\Desktop\SD1_Courseworks\COURSEWORK_03\tracker_icon.ico')

            # create label frame
            search_frame = tk.LabelFrame(search_toplevel, text='Transaction Type (Income/Expense)', bg=LIGHT_BLUE)
            search_frame.pack(padx=10, pady=10)

            # create entry box
            search_entry = tk.Entry(search_frame, font=('Helvetica', 18))
            search_entry.pack(padx=20, pady=20)

            search_entry.focus_force()

            def search_records():

                lookup_record_str = search_entry.get().capitalize()
                if lookup_record_str in ['Income', 'Expense']:
                    search_toplevel.destroy()
                    # Proceed with the rest of your logic here
                    tk.messagebox.showinfo("Search", f"Searching for: {lookup_record_str}")

                    for entry in self.my_tree.get_children():  # gets the list of all the children
                        self.my_tree.delete(entry)

                    for record in self.transactions:
                        for transaction in self.transactions[record]:
                            if transaction['type'] == lookup_record_str:
                                if transaction['type'] == 'Income':
                                    self.my_tree.insert(parent='', index='end', text='',
                                                        values=(transaction['type'], record, transaction['amount'],
                                                                transaction['date'], transaction['id']),
                                                        tags='income_row')

                                elif transaction['type'] == 'Expense':
                                    self.my_tree.insert(parent='', index='end', text='',
                                                        values=(transaction['type'], record, transaction['amount'],
                                                                transaction['date'], transaction['id']),
                                                        tags='expense_row')
                                disable_search_options()
                    if len(self.my_tree.get_children()) == 0:
                        tk.messagebox.showinfo("Search Unsuccessful", 'Provided Transaction Type Not Found')
                        disable_search_options()
                else:
                    tk.messagebox.showerror('Invalid Type',
                                            'The transaction type must be either "Income" or "Expense". Please correct the input.')

                    search_entry.delete(0, tk.END)
                    search_entry.focus_force()

            enable_reset_command()
            # Add button
            search_button = tk.Button(search_frame, text='Search Records', command=search_records, bg=AQUA_BLUE,
                                      relief=tk.FLAT, font=SMALL_FONT_STYLE)
            search_button.pack(padx=20, pady=20)

        # search by expense type
        def search_by_expense():
            search_toplevel = tk.Toplevel(self.root)
            search_toplevel.title('Search By Category Type')
            search_toplevel.configure(bg=BABY_BLUE)
            search_toplevel.geometry('400x200')
            search_toplevel.resizable(False, False)

            # create label frame
            search_frame = tk.LabelFrame(search_toplevel, text='Category Type', bg=LIGHT_BLUE)
            search_frame.pack(padx=10, pady=10)

            # create entry box
            search_entry = tk.Entry(search_frame, font=('Helvetica', 18))
            search_entry.pack(padx=20, pady=20)

            search_entry.focus_force()

            def search_records():
                lookup_record_str = search_entry.get()
                if not lookup_record_str:
                    tk.messagebox.showerror('Invalid Transaction Category',
                                            'The Transaction Category Cannot be Empty')
                    search_entry.delete(0, tk.END)
                    search_entry.focus_force()
                elif any(char in SPECIAL_CHARS for char in lookup_record_str):
                    tk.messagebox.showerror('Invalid Transaction Category',
                                            'Please Provide a Valid Transaction Category')
                    search_entry.delete(0, tk.END)
                    search_entry.focus_force()
                elif lookup_record_str.isdigit():
                    tk.messagebox.showerror('Invalid Transaction Category',
                                            'The Transaction Category Cannot Contain Numbers')
                    search_entry.delete(0, tk.END)
                    search_entry.focus_force()
                else:
                    search_toplevel.destroy()
                    # Proceed with the rest of your logic here
                    tk.messagebox.showinfo("Search", f"Searching for: {lookup_record_str}")

                    self.remove_tree()

                    for record in self.transactions:
                        for transaction in self.transactions[record]:
                            if record == lookup_record_str.capitalize():
                                if transaction['type'] == 'Income':
                                    self.my_tree.insert(parent='', index='end', text='',
                                                        values=(transaction['type'], record, transaction['amount'],
                                                                transaction['date'], transaction['id']),
                                                        tags='income_row')

                                elif transaction['type'] == 'Expense':
                                    self.my_tree.insert(parent='', index='end', text='',
                                                        values=(transaction['type'], record, transaction['amount'],
                                                                transaction['date'], transaction['id']),
                                                        tags='expense_row')
                                disable_search_options()
                    if len(self.my_tree.get_children()) == 0:
                        tk.messagebox.showinfo("Search Unsuccessful",
                                               'No Records were Found for the Provided Transaction Category')
                        disable_search_options()

            enable_reset_command()
            # Add button
            search_button = tk.Button(search_frame, text='Search Records', command=search_records, bg=AQUA_BLUE,
                                      relief=tk.FLAT, font=SMALL_FONT_STYLE)
            search_button.pack(padx=20, pady=20)

        # adding search options in the search menu
        self.search_menu.add_command(label='Search By Date', command=search_by_date)
        self.search_menu.add_command(label='Search By Amount', command=search_by_amount)
        self.search_menu.add_command(label='Search By Transaction Type', command=search_by_type)
        self.search_menu.add_command(label='Search By Category Type', command=search_by_expense)
        self.search_menu.add_separator()
        self.search_menu.add_command(label='Reset', command=reset, state=tk.DISABLED)

    # validating inputs using key events
    def shift_focus(self, event):
        if event.keysym == "Tab":
            self.category = self.category_var.get()
            if not self.category:
                tk.messagebox.showerror('Input Error', 'Please Input a Valid Category First')
                self.category_box.focus()
                return 'break'
            elif self.category.isnumeric():
                tk.messagebox.showerror('Input Error', 'Category Cannot Be A Numeral Value')
                self.category_box.delete(0, tk.END)
                self.category_box.focus()
                return 'break'
            if any(char in SPECIAL_CHARS for char in self.category):
                tk.messagebox.showerror('Input Error', 'Category Cannot Contain Special Characters')
                self.category_box.delete(0, tk.END)
                self.category_box.focus()
                return 'break'
            else:
                amount_str = self.amount_var.get()
                if event.widget == self.amount_box:
                    if not amount_str:
                        tk.messagebox.showerror('Input Error', 'Please Input a Valid Amount First')
                        self.amount_box.focus()
                        return 'break'
                    try:
                        self.amount = float(amount_str)
                        if self.amount < 0:
                            tk.messagebox.showerror('Input Error', 'Transaction Amount Cannot Be A Negative Value')
                            self.amount_var.set('')
                            self.amount_box.focus()
                    except ValueError:
                        tk.messagebox.showerror('Input Error', 'Transaction Amount Cannot Be A Textual Value')
                        self.amount_var.set('')
                        self.amount_box.focus()
                        return 'break'
                else:
                    date = self.date_var.get()
                    if event.widget == self.date_box:
                        if not date:
                            tk.messagebox.showerror('Input Error', 'Please Input a Valid Date First')
                            self.date_box.focus()
                            return 'break'
                        try:
                            date_conversion = datetime.strptime(date,
                                                                DATE_FORMAT).date()  # converting str to date object
                            self.date_string = date_conversion.strftime(DATE_FORMAT)
                        except ValueError:
                            tk.messagebox.showerror('Input Error', 'Invalid Date')
                            self.date_box.focus()
                            self.date_var.set('')
                            return 'break'

    # CRUD operations
    def display_transactions(self, transactions):
        # Adds a new record
        def add_record_transaction():
            if self.option_variable.get() == 'Income':
                self.my_tree.insert(parent='', index='end', iid=self.count, text='',
                                    values=(self.option_variable.get(), self.category_box.get(), self.amount_box.get(),
                                            self.date_box.get(), self.max_id), tags='income_row')
            elif self.option_variable.get() == 'Expense':
                self.my_tree.insert(parent='', index='end', iid=self.count, text='',
                                    values=(self.option_variable.get(), self.category_box.get(), self.amount_box.get(),
                                            self.date_box.get(), self.max_id), tags='expense_row')
            self.count += 1

            # clear the entry boxes
            self.category_box.delete(0, tk.END)
            self.amount_box.delete(0, tk.END)
            self.date_box.delete(0, tk.END)

        # saving data
        def save_message():
            transaction_type = self.option_variable.get()
            if transaction_type == 'Transaction Type':
                tk.messagebox.showerror('Input Error', 'Please Check Your Inputs')
                self.category_box.focus_force()
                return
            else:
                save = tk.messagebox.askyesno('Save Confirmation', 'Do you want to save', icon='question')
                if save is True:
                    category = self.category_var.get()
                    amount_str = self.amount_var.get()
                    date_str = self.date_var.get()
                    if not category:
                        tk.messagebox.showerror('Input Error', 'Please Check Your Inputs')
                        self.category_box.focus_force()
                        return

                    try:
                        amount = float(amount_str)
                        date_conversion = datetime.strptime(date_str, DATE_FORMAT).date()
                        date_string = date_conversion.strftime(DATE_FORMAT)
                    except ValueError:
                        tk.messagebox.showerror('Input Error', 'Please Check Your Inputs')
                        self.category_box.focus_force()
                        return
                    try:
                        # checks if the category already exists
                        existing_category = next(
                            (key for key in self.transactions.keys() if key.lower() == category.lower()))
                        # None handles the case where the no existing category is found without causing errors

                        if existing_category is not None:  # If category exists, use the existing category
                            category = existing_category
                    except StopIteration:
                        print('Not found')

                    self.max_id += 1  # increment the transaction ID

                    # create transaction data
                    data = {f'amount': amount, 'date': date_string, 'type': transaction_type, 'id': self.max_id}

                    for char in self.transactions.keys():  # add transaction data to the appropriate category in content
                        if category.lower() in char.lower():  # checks if current category matches the specified key
                            self.transactions[char].append(
                                data)  # Adds data dict to the transaction list in the category
                            break  # Exit the Loop
                    else:
                        self.transactions[category.capitalize()] = [data]
                    self.save_transaction()
                    tk.messagebox.showinfo('Save Success', 'Transaction Added Successfully !')
                elif save is False:
                    tk.messagebox.showinfo('Cancellation ', 'Transaction Save Cancelled')
            add_record_transaction()

        # handles the 'Return' key event for saving
        def save_key_event(event):
            if event.keysym == 'Return':
                save_message()

        # remove every record from treeview and JSON file
        def remove_every_record():
            delete_all = tk.messagebox.askyesno('Delete Confirmation',
                                                'Do you want to delete all transaction records ?')
            if delete_all is True:
                self.transactions.clear()
                self.save_transaction()

                self.remove_tree()

                tk.messagebox.showinfo('Deletion Success', 'Every Recorded Transactions Deleted Successfully')
            elif delete_all is False:
                tk.messagebox.showinfo('Deletion Cancel', 'Deletion Process Aborted. No Transactions were Deleted')

        # removes one selected record from treeview and JSON file
        def remove_selected():
            # WHEN STH NOT SELECTED
            # selected_record = self.my_tree.selection()[0]  # gets the list of all the things selected
            delete_selected = tk.messagebox.askyesno('Delete Confirmation',
                                                     'Do You Want To Delete The Selected Transaction ? ')
            if delete_selected is True:
                selected_record = self.my_tree.focus()  # focus only gives thw value of first selected item
                details = self.my_tree.item(selected_record)
                unique_id = details.get('values')[4]
                print(f'unique_id:- {unique_id}')

                for category in self.transactions:
                    for record in self.transactions[category]:
                        if record['id'] == unique_id:
                            # print(f'Found')
                            # print(f'Record - {record}')
                            self.transactions[category].remove(record)
                self.save_transaction()
                self.my_tree.delete(selected_record)
                tk.messagebox.showinfo('Deletion Success', 'Selected Transaction Deleted Successfully')
            elif delete_selected is False:
                tk.messagebox.showinfo('Deletion Cancel', 'Deletion Process Aborted. Selected Transaction Not Deleted')

        # removes many selected records from treeview and JSON file
        def remove_many_records():
            delete_many = tk.messagebox.askyesno('Delete Confirmation',
                                                 'Do You Want To Delete The Selected Multiple Transactions ? ')

            if delete_many is True:
                selected_items = self.my_tree.selection()
                print(selected_items)
                for record in selected_items:
                    current_record = self.my_tree.item(record)
                    current_text = current_record.get('values')
                    current_id = current_text[-1]
                    # print(current_id)
                    # print(current_text)
                    self.my_tree.delete(record)
                    for category in self.transactions:
                        for record in self.transactions[category]:
                            if record['id'] == current_id:
                                # print(f'Found = {current_id}')
                                # print(f'Records - {record}')
                                self.transactions[category].remove(record)
                self.save_transaction()
                tk.messagebox.showinfo('Deletion Success', 'Selected Transactions Deleted Successfully')
            elif delete_many is False:
                tk.messagebox.showinfo('Deletion Cancel', 'Deletion Process Aborted. Selected Transactions Not Deleted')

        # enabling select record button after selecting a record from the tree
        def enable_select_button(event):
            selected_record = self.my_tree.selection()
            if selected_record:
                select_button.configure(state=tk.NORMAL)
                remove_many.configure(state=tk.NORMAL)
                remove_one.configure(state=tk.NORMAL)
            else:
                select_button.configure(state=tk.DISABLED)

        # selecting record from the tree
        def select_record():
            # clear entry boxes
            self.category_box.delete(0, tk.END)
            self.date_box.delete(0, tk.END)
            self.amount_box.delete(0, tk.END)

            # grab treeview record number
            selected = self.my_tree.focus()

            # grab record values
            self.record_values = self.my_tree.item(selected, 'values')

            # output to entry boxes
            self.transaction_type_option_menu.configure(state=tk.DISABLED)
            self.category_box.insert(0, self.record_values[1])
            self.category_box.configure(state=tk.DISABLED)
            self.amount_box.insert(0, self.record_values[2])
            self.date_box.insert(0, self.record_values[3])

            update_button.configure(state=tk.NORMAL)

        # updating details from the tree and JSON file
        def update_record():

            selected = self.my_tree.focus()
            details = self.my_tree.item(selected)
            unique_id = details.get('values')[4]

            new_amount_str = self.amount_var.get().replace(',', '')
            new_date_str = self.date_var.get()
            new_amount = float(new_amount_str)
            date_conversion = datetime.strptime(new_date_str, DATE_FORMAT).date()
            new_date_string = date_conversion.strftime(DATE_FORMAT)
            update = tk.messagebox.askyesno('Update Confirmation', 'Do you want to update the transaction details ?')
            if update is True:
                for category in self.transactions:
                    for record in self.transactions[category]:

                        if record['id'] == unique_id:
                            record['amount'] = new_amount
                            record['date'] = new_date_string

                self.my_tree.item(selected, text=" ",
                                  values=(self.record_values[0], self.record_values[1].capitalize(),
                                          self.amount_box.get(), self.date_box.get(), self.record_values[4]))

                self.save_transaction()
                tk.messagebox.showinfo('Update Success', 'Transaction Details For The Selected Record Updated')
            else:
                tk.messagebox.showinfo('Update Cancel', 'Update Process Aborted. No Changes Applied.')

            # Enabling the disabled widgets
            self.transaction_type_option_menu.configure(state=tk.ACTIVE)
            self.category_box.configure(state=tk.NORMAL)

            # clear entry boxes
            self.category_box.delete(0, tk.END)
            self.date_box.delete(0, tk.END)
            self.amount_box.delete(0, tk.END)

            self.category_box.focus_force()  # focusing cursor on category box

        # create buttons
        add_record = tk.Button(self.button_frame, text='Create Record', font=SMALL_FONT_STYLE, command=save_message,
                               bg=AQUA_BLUE, relief='flat')  # add new record

        select_button = tk.Button(self.button_frame, text='Select Record', font=SMALL_FONT_STYLE, command=select_record,
                                  bg=AQUA_BLUE, relief='flat', state=tk.DISABLED)  # select a record

        update_button = tk.Button(self.button_frame, text='Update Record', font=SMALL_FONT_STYLE, command=update_record,
                                  bg=AQUA_BLUE, relief='flat', state=tk.DISABLED)  # update a record

        remove_all = tk.Button(self.button_frame, text='Delete All Records', font=SMALL_FONT_STYLE,
                               command=remove_every_record, bg=AQUA_BLUE, relief='flat')  # remove all records

        remove_many = tk.Button(self.button_frame, text='Delete Multiple Records', font=SMALL_FONT_STYLE, bg=AQUA_BLUE,
                                command=remove_many_records, relief='flat',
                                state=tk.DISABLED)  # remove many selected records

        remove_one = tk.Button(self.button_frame, text='Delete Selected Record', font=SMALL_FONT_STYLE,
                               command=remove_selected, bg=AQUA_BLUE, relief='flat',
                               state=tk.DISABLED)  # remove one record
        exit_button = tk.Button(self.button_frame, text='Exit', font=SMALL_FONT_STYLE,
                                command=self.exit_program, bg=AQUA_BLUE, relief='flat')

        # packing buttons
        add_record.grid(row=0, column=0, padx=10, pady=10)
        select_button.grid(row=0, column=1, padx=10, pady=10)
        update_button.grid(row=0, column=2, padx=10, pady=10)
        remove_all.grid(row=0, column=3, padx=10, pady=10)
        remove_many.grid(row=0, column=4, padx=10, pady=10)
        remove_one.grid(row=0, column=5, padx=10, pady=10)
        exit_button.grid(row=0, column=6, padx=10, pady=10)

        self.category_box.focus_force()  # focusing cursor on category box

        # binding keys
        self.category_box.bind('<Tab>', self.shift_focus)
        self.amount_box.bind('<Tab>', self.shift_focus)
        self.date_box.bind('<Tab>', self.shift_focus)
        add_record.bind('<Return>', save_key_event)
        self.my_tree.bind('<<TreeviewSelect>>', enable_select_button)

    # sort each column ascending and descending order
    def sort_by_column(self, tree, col, reverse):
        # Collect data for each row
        data = [(tree.set(row, col), row) for row in tree.get_children()]

        # Check if the column contains numeric values
        is_numeric = all(
            value.replace('.', '', 1).replace(',', '', 1).replace('-', '', 1).isdigit() for value, _ in data)

        if is_numeric:  # If numeric, sort as floats
            data.sort(key=lambda x: float(x[0].replace(',', '')), reverse=reverse)
        else:  # Otherwise, sort as strings
            data.sort(key=lambda x: x[0].lower(), reverse=reverse)

        for index, (val, row) in enumerate(data):
            tree.move(row, '', index)

        # Update heading to toggle sorting order
        tree.heading(col, command=lambda: self.sort_by_column(tree, col, not reverse))

    # viewing summary of all transactions
    def view_summary(self):
        summary_toplevel = tk.Toplevel(self.root)
        summary_toplevel.title('Transaction Summary')
        summary_toplevel.configure(bg=BABY_BLUE)
        summary_toplevel.geometry('800x450')
        summary_toplevel.resizable(False, False)

        summary_toplevel.focus_force()

        summary_label = tk.Label(summary_toplevel, text='Transaction Summary', font=TITLE_FONT_STYLE, bg=BABY_BLUE)
        summary_label.pack(padx=10)

        summary_tree_frame = tk.Frame(summary_toplevel, height=120)
        summary_tree_frame.configure(bg=BABY_BLUE)
        summary_tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        scroll_bar = tk.Scrollbar(summary_tree_frame)
        scroll_bar.configure(bg=BLUE_GRAY, relief=tk.FLAT)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        summary_tree = ttk.Treeview(summary_tree_frame, yscrollcommand=scroll_bar, selectmode=tk.EXTENDED)
        summary_tree.pack(fill=tk.BOTH, padx=10)
        scroll_bar.configure(command=summary_tree.yview)

        summary_tree['columns'] = ('Transaction Category', 'Transaction Category Total')
        summary_tree.column('#0', width=0, stretch=False)
        for col in summary_tree['columns']:
            summary_tree.column(col, anchor=tk.CENTER, width=120)
        summary_tree.heading('#0', text='')
        for col in summary_tree['columns']:
            summary_tree.heading(col, text=col, anchor=tk.CENTER)

        tag = ''
        summary_tree.tag_configure('income_row', background=ROBIN_EGG_BLUE)
        summary_tree.tag_configure('expense_row', background=VERDIGRIS_BLUE)

        # calculating total income and expense
        income = 0
        expense = 0
        category_totals_dict = {}
        for item in self.transactions:
            category_total = 0
            for transaction in self.transactions[item]:
                amount = transaction['amount']
                category_total += amount
                if transaction['type'] == 'Income':
                    income += amount
                    tag = 'income_row'
                elif transaction['type'] == 'Expense':
                    expense += amount
                    tag = 'expense_row'
            category_totals_dict[item] = category_total
            summary_tree.insert(parent='', index='end', text=item, values=(item, f'{category_total:,.2f}',),
                                tags=(tag,))

        # calculating net balance
        balance = income - expense

        # creating label frame for final summary
        summary_frame = tk.LabelFrame(summary_toplevel, text='Total Summary')
        summary_frame.pack(fill=tk.BOTH, expand=tk.YES, padx=10, pady=10)
        summary_frame.configure(bg=BABY_BLUE)

        # Add labels for total income, expenses, balance names
        total_income_name = tk.Label(summary_frame, text='Total Income', bg=BABY_BLUE, font=SMALL_FONT_STYLE)
        total_expense_name = tk.Label(summary_frame, text='Total Expenses', bg=BABY_BLUE, font=SMALL_FONT_STYLE)
        net_balance_name = tk.Label(summary_frame, text='Net Balance', bg=BABY_BLUE, font=SMALL_FONT_STYLE)

        # Add labels for total income, expenses, balance values
        total_income_value = tk.Label(summary_frame, text=f'{income:,.2f}', bg=BABY_BLUE, font=SMALL_FONT_STYLE)
        total_expense_value = tk.Label(summary_frame, text=f'{expense:,.2f}', bg=BABY_BLUE, font=SMALL_FONT_STYLE)
        net_balance_value = tk.Label(summary_frame, text=f'{balance:,.2f}', bg=BABY_BLUE, font=SMALL_FONT_STYLE)

        # positioning name labels
        total_income_name.grid(row=0, column=0, padx=80, pady=10)
        total_expense_name.grid(row=0, column=1, padx=80, pady=10)
        net_balance_name.grid(row=0, column=2, padx=80, pady=10)

        # positioning value labels
        total_income_value.grid(row=1, column=0, padx=80, pady=5)
        total_expense_value.grid(row=1, column=1, padx=80, pady=5)
        net_balance_value.grid(row=1, column=2, padx=80, pady=5)

    # display summary menu
    def display_summary(self):
        self.view_menu.add_command(label='View Summary', command=self.view_summary)

    # bulk reading from text file
    def read_bulk_transactions(self):
        filetype = (('Text Files', '*.txt'),)
        file_name = tk.filedialog.askopenfilename(title='Select A File', filetypes=filetype)

        if not file_name:
            tk.messagebox.showerror('File Not Chosen', 'No File Selected')
            return
        with open(file_name, 'r') as file:
            if file.readline().strip() == '':
                tk.messagebox.showerror('Zero Details', 'No Transaction Details Were Found.')
                return
            file.seek(0)
            for line in file:
                cleared_string = line.strip().split(',')
                if len(cleared_string) >= 4:  # Ensure there are enough elements
                    category, amount, date, i_e_type = cleared_string[:4]
                else:
                    tk.messagebox.showerror('Incomplete Transaction Details',
                                            'One or More Transaction Details are missing. Ensure All Details are Entered')
                    return

                if not category:
                    tk.messagebox.showerror('Invalid Category', 'Category cannot be empty')
                    return
                elif category.isdigit():
                    tk.messagebox.showerror('Invalid Category',
                                            'Transaction Category Cannot Be a Numeral Value')
                    return
                elif any(char in SPECIAL_CHARS for char in category):
                    tk.messagebox.showerror('Invalid Category', 'Category contains special characters')
                    return

                # Validate amount
                try:
                    amount = float(amount)
                    if amount < 0:
                        tk.messagebox.showerror('Invalid Amount', 'Amount Cannot be A Negative Value')
                        return
                except ValueError:
                    tk.messagebox.showerror('Invalid Amount', 'Amount must be a numeric value')
                    return

                # Validate date
                try:
                    date_conversion = datetime.strptime(date, DATE_FORMAT).date()
                    date_string = date_conversion.strftime(DATE_FORMAT)
                except ValueError:
                    tk.messagebox.showerror('Invalid Date', 'Invalid Date format')
                    return

                # Validate income/expense type
                if i_e_type.lower() not in ['income', 'expense']:
                    tk.messagebox.showerror('Invalid Transaction Type', 'Invalid Transaction Type (Income/Expense)')
                    return

                self.max_id += 1

                # Construct transaction data
                data = {'amount': amount, 'date': date_string, 'type': i_e_type, 'id': self.max_id}

                # Update content dictionary
                category_key = category.capitalize()
                self.transactions.setdefault(category_key, []).append(data)

            # Save transactions after processing all lines
            self.save_transaction()
            tk.messagebox.showinfo('Save Success', 'Transactions Added to the JSON file from the text file ')
            self.remove_tree()
            self.insert_data()

    # bulk reading menu
    def bulk_transactions(self):
        self.bulk_menu.add_command(label='Read Bulk Transactions', command=self.read_bulk_transactions)


def main():
    root = tk.Tk()
    app_width = 1000
    app_height = 550

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    middle_x = (screen_width - app_width) / 2
    middle_y = (screen_height - app_height) / 2

    root.geometry(f'{app_width}x{app_height}+{int(middle_x)}+{int(middle_y)}')
    root.configure(bg=BLUE_GRAY)
    app = finance_tracker(root)
    app.display_transactions(app.transactions)
    root.mainloop()


if __name__ == "__main__":
    main()
