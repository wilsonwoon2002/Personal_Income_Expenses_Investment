import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import tkcalendar
import datetime
import re
import uuid
import csv

# Today's or Computer's Date
current_date = datetime.date.today()
current_year = current_date.year
current_month = current_date.month
current_day = current_date.day

# Define the folder name as a global variable
folder_name = 'personal_expenses_transaction_data'
apartment_expenses_folder_name = 'apartment_expenses_transaction_data'


def calendar_select(calendar_var):
    def update_date():
        selected_date = calendar.selection_get()
        calendar_var.set(selected_date.strftime('%d-%b-%Y'))
        calendar_window.destroy()

    calendar_window = tk.Toplevel(window)
    calendar_window.title('Calendar')
    calendar = tkcalendar.Calendar(calendar_window, selectmode='day', year=current_year, month=current_month,
                                   day=current_day)
    calendar.pack(padx=10, pady=10)
    ok_button = ttk.Button(calendar_window, text='OK', command=update_date)
    ok_button.pack(pady=10)


def generate_transaction_id():
    transaction_id = uuid.uuid4()
    return str(transaction_id)


def on_category_selected(event):
    selected_category = category_var.get()
    if selected_category == 'Transportation':
        payment_var.set('Octopus')
    elif selected_category == 'Mortgage Loan':
        payment_var.set('Bank Transfer')
    else:
        payment_var.set('Credit Cards')


def format_entry_with_separator(event):
    entry = event.widget
    try:
        value = float(entry.get().replace(',', ''))
        entry.delete(0, tk.END)
        entry.insert(0, f"{value:,.2f}")
    except ValueError:
        pass


def create_folder_if_not_exists():
    # Check if folder exists and create it if it doesn't
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


def check_apartment_transactions_folder():
    # Check if folder exists and create it if it doesn't
    if not os.path.exists(apartment_expenses_folder_name):
        os.makedirs(apartment_expenses_folder_name)


def save_data():
    amount = amount_entry.get().strip().replace(',', '')
    if not re.match(r'^\d+(\.\d{1,2})?$', amount):
        messagebox.showwarning('Validation Error', 'Invalid amount. Please enter a valid number with at most 2 decimal places.')
        return

    foreign_transaction = foreign_transaction_var.get()
    foreign_transaction_currency_amount = foreign_currency_amount_entry.get().strip().replace(',', '')

    if foreign_transaction == 'Yes':
        if not foreign_currency_amount_entry.get().strip():
            messagebox.showwarning('Validation Error', 'Foreign currency amount is required.')
            return

        if not re.match(r'^\d+(\.\d{1,2})?$', foreign_transaction_currency_amount):
            messagebox.showwarning('Validation Error',
                                   'Invalid foreign currency transaction amount. Please enter a valid number with at most 2 decimal places.')
            return

    transaction_id = generate_transaction_id()

    date = datetime.datetime.strptime(date_var.get(), '%d-%b-%Y').strftime('%m/%d/%Y')
    category = category_var.get()
    payment_mode = payment_var.get()
    tax_deductible = tax_deductible_var.get()
    foreign_transaction_currency = foreign_currency_var.get()
    foreign_transaction_currency_amount = foreign_currency_amount_entry.get()
    description = description_entry.get().strip()

    # Create the folder if it doesn't exist
    create_folder_if_not_exists()

    file_name = f'{folder_name}/expenses_data_{date.split("/")[-1]}.csv'

    # Check if file exists
    file_exists = os.path.isfile(file_name)

    with open(file_name, 'a', newline='') as f:
        writer = csv.writer(f)

        # Write header row if file does not exist
        if not file_exists:
            writer.writerow(['transaction_id', 'date', 'category', 'payment_mode', 'currency', 'amount', 'tax_deductible',
                             'remarks', 'foreign_transaction', 'foreign_currency', 'foreign_currency_amount'])

        if foreign_transaction == 'No':
            foreign_transaction_currency = 'nil'
            foreign_transaction_currency_amount = 'nil'
        else:
            if not foreign_currency_amount_entry.get().strip():
                messagebox.showwarning('Validation Error', 'Foreign currency amount is required.')
                return

        writer.writerow([transaction_id, date, category, payment_mode, 'HKD', amount, tax_deductible, description,
                         foreign_transaction, foreign_transaction_currency, foreign_transaction_currency_amount])

    # Save the transaction in apartment expenses file, if applicable
    apartment_transaction = apartment_transaction_var.get()

    if apartment_transaction == 'Yes':
        apartment_transaction_item = apartment_transaction_item_var.get()

        check_apartment_transactions_folder()

        apartment_transactions_file_name = f'{apartment_expenses_folder_name}/apartment_expenses_data_{date.split("/")[-1]}.csv'

        # Check if file exists
        apartment_transactions_file_exists = os.path.isfile(apartment_transactions_file_name)

        with open(apartment_transactions_file_name, 'a', newline='') as f:
            writer = csv.writer(f)

            # Write header row if file does not exist
            if not apartment_transactions_file_exists:
                writer.writerow(
                    ['transaction_id', 'date', 'category', 'payment_mode', 'currency', 'amount',
                     'remarks', 'foreign_transaction', 'foreign_currency', 'foreign_currency_amount',
                     'item', 'paid_by'])

            writer.writerow([transaction_id, date, category, payment_mode, 'HKD', amount, description,
                             foreign_transaction, foreign_transaction_currency, foreign_transaction_currency_amount,
                             apartment_transaction_item, 'Wilson'])

    messagebox.showinfo('Save Successful', 'Expense saved successfully.')

    # Clear all input fields and reset default values
    date_var.set(current_date.strftime('%d-%b-%Y'))
    category_var.set('Food')
    payment_var.set('Credit Cards')
    amount_entry.delete(0, 'end')
    description_entry.delete(0, 'end')
    tax_deductible_var.set('No')
    foreign_transaction_var.set('No')
    foreign_currency_var.set('USD')
    foreign_currency_amount_entry.delete(0, 'end')
    apartment_transaction_var.set('No')
    #apartment_transaction_category_var.set('Mortgage Loan')
    apartment_transaction_item_var.set('Principle Repayment')
    amount_entry.focus()

    # Reset visibility of currency and amount inputs
    foreign_currency_label.grid_remove()
    foreign_currency_dropdown.grid_remove()
    foreign_currency_amount_label.grid_remove()
    foreign_currency_amount_label.grid_remove()
    foreign_currency_amount_entry.grid_remove()
    foreign_currency_dropdown.configure(state='disabled')
    #apartment_transaction_category_label.grid_remove()
    #apartment_transaction_category_dropdown.grid_remove()
    #apartment_transaction_category_label.grid_remove()
    #apartment_transaction_category_dropdown.grid_remove()
    apartment_transaction_item_label.grid_remove()
    apartment_transaction_item_dropdown.grid_remove()
    apartment_transaction_item_label.grid_remove()
    apartment_transaction_item_dropdown.grid_remove()


def show_last_50_transactions(transactions, headers):
    # Create a new window to display the transactions
    last_50_window = tk.Toplevel(window)
    last_50_window.title('Last 50 Transactions')

    # Create a treeview widget to display the data in a table
    last_50_tree = ttk.Treeview(last_50_window, columns=headers, show='headings')
    last_50_tree.pack(side='left')

    # Add columns to the treeview
    for header in headers:
        last_50_tree.heading(header, text=header, anchor='w')
        last_50_tree.column(header, width=100, anchor='w')

    # Add the last 30 transactions to the treeview
    num_transactions = min(len(transactions), 50)
    for i in range(num_transactions):
        row = transactions[-num_transactions + i]
        last_50_tree.insert('', 'end', values=row)

    # Add a scrollbar to the treeview
    scrollbar = ttk.Scrollbar(last_50_window, orient='vertical', command=last_50_tree.yview)
    scrollbar.pack(side='right', fill='y')
    last_50_tree.configure(yscrollcommand=scrollbar.set)

    # Add a button to close the window
    close_button = ttk.Button(last_50_window, text='Close', command=last_50_window.destroy)
    close_button.pack(pady=10)


def display_transactions():
    # Get the current year
    date = datetime.datetime.strptime(date_var.get(), '%d-%b-%Y').strftime('%m/%d/%Y')

    # Set the file name based on the current year
    file_name = f'{folder_name}/expenses_data_{date.split("/")[-1]}.csv'

    # Check if the file exists
    try:
        with open(file_name, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            transactions = [row for row in reader][-20:]
    except FileNotFoundError:
        messagebox.showerror('File Not Found', f'There is no record of your expenses. Please create one first')
        return

    # Create a new window to display the transactions
    display_window = tk.Toplevel(window)
    display_window.title('Last 20 Transactions')

    # Create a treeview widget to display the data in a table
    tree = ttk.Treeview(display_window, columns=headers, show='headings')
    tree.pack(side='left')

    # Add columns to the treeview
    for header in headers:
        tree.heading(header, text=header, anchor='w')
        tree.column(header, width=100, anchor='w')

    # Add the last 10 transactions to the treeview
    num_transactions = min(len(transactions), 10)
    for i in range(num_transactions):
        row = transactions[-num_transactions + i]
        tree.insert('', 'end', values=row)

    # Add a scrollbar to the treeview
    scrollbar = ttk.Scrollbar(display_window, orient='vertical', command=tree.yview)
    scrollbar.pack(side='right', fill='y')
    tree.configure(yscrollcommand=scrollbar.set)

    # Add a button to display the last 20 transactions
    more_button = ttk.Button(display_window, text='More',
                             command=lambda: show_last_50_transactions(transactions, headers))
    more_button.pack(pady=10)

    # Add a button to close the window
    close_button = ttk.Button(display_window, text='Close', command=display_window.destroy)
    close_button.pack(pady=10)


window = tk.Tk()
window.title('Personal Expenses')

# Default values for the Fields
category_var = tk.StringVar(value='Food')
payment_var = tk.StringVar(value='Credit Cards')
tax_deductible_var = tk.StringVar(value='No')
foreign_currency_transaction_var = tk.StringVar(value='No')
foreign_currency_var =  tk.StringVar(value='USD')
foreign_transaction_var = tk.StringVar(value='No')
apartment_transaction_var = tk.StringVar(value='No')
apartment_transaction_category_var = tk.StringVar(value='Mortgage Loan')
apartment_transaction_item_var = tk.StringVar(value='Principle Repayment')

# Date input
date_label = ttk.Label(window, text='Date', anchor='e')
date_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
date_var = tk.StringVar(value=current_date.strftime('%d-%b-%Y'))
date_entry = ttk.Entry(window, textvariable=date_var, state='readonly')
date_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
calendar_button = ttk.Button(window, text='Select', command=lambda: calendar_select(date_var))
calendar_button.grid(row=0, column=2, padx=5, pady=5)

# Category input
category_label = ttk.Label(window, text='Category', anchor='e')
category_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')
category_entry = ttk.Combobox(window, textvariable=category_var, values=['Food', 'Transportation', 'Utilities', 'Groceries',
                                                                         'Mortgage Loan', 'Education', 'Medical', 'Donation',
                                                                         'Gambling', 'Grooming', 'Insurance', 'Entertainment',
                                                                         'Toiletries', 'Software', 'Gift', 'Repair & Maintenance',
                                                                         'Takeaway Fees', 'Sports & Leisure', 'Stationary & Printing',
                                                                         'Clothing & Fashion', 'Delivery Fees', 'Misc. Fees',
                                                                         'Holiday & Travel', 'Computer & Electronics', 'Allowance for Parents',
                                                                         'Income Tax'])
category_entry.grid(row=1, column=1, padx=5, pady=5)
category_entry.bind("<<ComboboxSelected>>", on_category_selected)


# Payment mode input
payment_label = ttk.Label(window, text='Payment Mode', anchor='e')
payment_label.grid(row=2, column=0, padx=5, pady=5, sticky='e')
payment_entry = ttk.Combobox(window, textvariable=payment_var, values=['Credit Cards', 'Octopus', 'Cash', 'Cheque',
                                                                       'Mobile Payments', 'Bank Transfer', 'Other'], width=17)
payment_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')

# Amount input
amount_label = ttk.Label(window, text='Amount', anchor='e')
amount_label.grid(row=3, column=0, padx=5, pady=5, sticky='e')
amount_entry = ttk.Entry(window)
amount_entry.grid(row=3, column=1, padx=5, pady=5, sticky='w')
amount_entry.focus()
amount_entry.bind("<FocusOut>", format_entry_with_separator)

currency_label_in_front = ttk.Label(window, font=('Arial', 8, 'bold'), text = "HKD", foreground='#999999')
currency_label_in_front.place(x=228, y=103)

# Tax deductible input
tax_deductible_label = ttk.Label(window, text='Tax Deductible?', anchor='e')
tax_deductible_label.grid(row=4, column=0, padx=5, pady=5, sticky='e')
tax_deductible_yes_radio = ttk.Radiobutton(window, text='Yes', variable=tax_deductible_var, value='Yes')
tax_deductible_yes_radio.grid(column=1, row=4, padx=5, pady=5, sticky='w')

tax_deductible_no_radio = ttk.Radiobutton(window, text='No', variable=tax_deductible_var, value='No')
tax_deductible_no_radio.grid(column=1, row=4)

# Foreign Currency Transaction Input
foreign_transaction_label = ttk.Label(window, text='Foreign Transaction?', anchor='e')
foreign_transaction_label.grid(row=5, column=0, padx=5, pady=5, sticky='e')
foreign_transaction_yes_radio = ttk.Radiobutton(window, text='Yes', variable=foreign_transaction_var, value='Yes',
                                             command=lambda: toggle_currency_visibility(True))
foreign_transaction_yes_radio.grid(column=1, row=5, padx=5, pady=5, sticky='w')

foreign_transaction_no_radio = ttk.Radiobutton(window, text='No', variable=foreign_transaction_var, value='No',
                                            command=lambda: toggle_currency_visibility(False))
foreign_transaction_no_radio.grid(column=1, row=5)

# Currency input (initially invisible)
foreign_currency_label = ttk.Label(window, text='Currency', anchor='e')
foreign_currency_label.grid(row=6, column=0, padx=5, pady=5, sticky='e')
foreign_currency_dropdown = ttk.Combobox(window, textvariable=foreign_currency_var, values=['USD', 'JPY', 'GBP', 'EUR', 'MYR', 'CNY', 'TWD'], width=5)
foreign_currency_dropdown.grid(row=6, column=1, padx=5, pady=5, sticky='w')
foreign_currency_dropdown.configure(state='disabled')
foreign_currency_label.grid_remove()
foreign_currency_dropdown.grid_remove()

# Foreign Currency Amount input (initially invisible)
foreign_currency_amount_label = ttk.Label(window, text='Amount', anchor='e')
foreign_currency_amount_label.grid(row=7, column=0, padx=5, pady=5, sticky='e')
foreign_currency_amount_entry = ttk.Entry(window)
foreign_currency_amount_entry.grid(row=7, column=1, padx=5, pady=5, sticky='w')
foreign_currency_amount_entry.bind("<FocusOut>", format_entry_with_separator)
foreign_currency_amount_label.grid_remove()
foreign_currency_amount_entry.grid_remove()


def toggle_currency_visibility(show_currency):
    if show_currency:
        foreign_currency_label.grid()
        foreign_currency_dropdown.grid()
        foreign_currency_dropdown.configure(state='readonly')
        foreign_currency_amount_label.grid()
        foreign_currency_amount_entry.grid()
    else:
        foreign_currency_label.grid_remove()
        foreign_currency_dropdown.grid_remove()
        foreign_currency_dropdown.configure(state='disabled')
        foreign_currency_amount_label.grid_remove()
        foreign_currency_amount_entry.grid_remove()


# Apartment Related Expenses Input
apartment_transaction_label = ttk.Label(window, text='Flat Expense?', anchor='e')
apartment_transaction_label.grid(row=8, column=0, padx=5, pady=5, sticky='e')
apartment_transaction_yes_radio = ttk.Radiobutton(window, text='Yes', variable=apartment_transaction_var, value='Yes',
                                             command=lambda: toggle_apartment_visibility(True))
apartment_transaction_yes_radio.grid(column=1, row=8, padx=5, pady=5, sticky='w')

apartment_transaction_no_radio = ttk.Radiobutton(window, text='No', variable=apartment_transaction_var, value='No',
                                            command=lambda: toggle_apartment_visibility(False))
apartment_transaction_no_radio.grid(column=1, row=8)

# Apartment Transaction Category input (initially invisible)
#apartment_transaction_category_label = ttk.Label(window, text='Category', anchor='e')
#apartment_transaction_category_label.grid(row=9, column=0, padx=5, pady=5, sticky='e')
#apartment_transaction_category_dropdown = ttk.Combobox(window, textvariable=apartment_transaction_category_var,
#                                                       values=['Mortgage Loan', 'Utilities', 'Renovation',
#                                                               'Repair & Maintenance', 'Insurance'],
#                                                       width=20)
#apartment_transaction_category_dropdown.grid(row=9, column=1, padx=5, pady=5, sticky='w')
#apartment_transaction_category_dropdown.configure(state='disabled')
#apartment_transaction_category_label.grid_remove()
#apartment_transaction_category_dropdown.grid_remove()

# Apartment Transaction Item input (initially invisible)
apartment_transaction_item_label = ttk.Label(window, text='Item', anchor='e')
apartment_transaction_item_label.grid(row=9, column=0, padx=5, pady=5, sticky='e')
apartment_transaction_item_dropdown = ttk.Combobox(window, textvariable=apartment_transaction_item_var,
                                                       values=['Principle Repayment', 'Interest Payment',
                                                               'Rates & Gov. Rent', 'Water', 'Gas', 'Maintenance Fees',
                                                               'Electricity', 'Repair and Maintenance', 'Internet', 'Home Insurance',
                                                               'Fire Insurance'],
                                                       width=20)
apartment_transaction_item_dropdown.grid(row=9, column=1, padx=5, pady=5, sticky='w')
apartment_transaction_item_dropdown.configure(state='disabled')
apartment_transaction_item_label.grid_remove()
apartment_transaction_item_dropdown.grid_remove()


def toggle_apartment_visibility(show_apartment_transactions_options):
    if show_apartment_transactions_options:
        #apartment_transaction_category_label.grid()
        #apartment_transaction_category_dropdown.grid()
        #apartment_transaction_category_dropdown.configure(state='readonly')

        apartment_transaction_item_label.grid()
        apartment_transaction_item_dropdown.grid()
        apartment_transaction_item_dropdown.configure(state='readonly')
    else:
        #apartment_transaction_category_label.grid_remove()
        #apartment_transaction_category_dropdown.grid_remove()
        #apartment_transaction_category_dropdown.configure(state='disabled')

        apartment_transaction_item_label.grid_remove()
        apartment_transaction_item_dropdown.grid_remove()
        apartment_transaction_item_dropdown.configure(state='disabled')


# Description input
description_label = ttk.Label(window, text='Description', anchor='e')
description_label.grid(row=10, column=0, padx=5, pady=5, sticky = 'e')
description_entry = ttk.Entry(window)
description_entry.grid(row=10, column=1, padx=5, pady=5, sticky='w')

# Create a new frame for the Save and Back buttons
button_frame = tk.Frame(window)

# Place the button frame in the grid layout
button_frame.grid(row=11, column=0, columnspan=2, pady=10)

# Save button
save_button = ttk.Button(button_frame, text='Save', command=save_data)
save_button.grid(row=0, column=0, padx=5, pady=15, sticky='w')

# Display button
display_button = ttk.Button(button_frame, text='Display Record', command=display_transactions)
display_button.grid(row=0, column=1, padx=2, pady=15)

# Delete button
#delete_button = ttk.Button(button_frame, text='Delete Record', command=delete_data)
#delete_button.grid(row=0, column=2, padx=5, pady=5)

# Back button
back_button = ttk.Button(button_frame, text='Back', command=window.destroy)
back_button.grid(row=0, column=2, padx=2, pady=15)


window.mainloop()