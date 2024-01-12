import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import Calendar
import datetime
import re
import uuid
import csv

# Today's or Computer's Date
current_date = datetime.date.today()
current_year = current_date.year
current_month = current_date.month
current_day = current_date.day

# Create the folder to hold the transaction data files
folder_name = 'stock_transaction_data'

def generate_transaction_id():
    transaction_id = uuid.uuid4()
    return str(transaction_id)


def calendar_select(calendar_var):
    def update_date():
        selected_date = calendar.selection_get()
        calendar_var.set(selected_date.strftime('%d-%b-%Y'))
        calendar_window.destroy()

    calendar_window = tk.Toplevel(window)
    calendar_window.title('Calendar')
    calendar = Calendar(calendar_window, selectmode='day', year=current_year, month=current_month, day=current_day)
    calendar.pack(padx=10, pady=10)
    ok_button = ttk.Button(calendar_window, text='OK', command=update_date)
    ok_button.pack(pady=10)


def update_currency(*args):
    location = location_var.get()
    currency_mapping = {
        'Hong Kong': 'HKD',
        'Malaysia': 'MYR',
        'USA': 'USD',
        'Europe': 'EUR',
        'China': 'CNY',
        'Singapore': 'SGD',
        'UK': 'GBP',
        'Japan': 'JPY'
    }
    currency_var.set(currency_mapping.get(location))


def update_amount_default(*args):
    category = category_var.get()
    if category in ('Bonus Shares', 'Drip'):
        amount_var.set('0.00')
    else:
        amount_var.set('')


def update_total_shares_default(*args):
    category = category_var.get()
    if category == 'Dividend':
        total_shares_var.set('0')
    else:
        total_shares_var.set('')


def is_valid_total_shares(total_shares, category):
    if not total_shares.isdigit():
        return False
    total_shares = int(total_shares)
    if total_shares < 0:
        return False
    if category == "Dividend" and total_shares != 0:
        return False
    if category != "Dividend" and total_shares == 0:
        return False
    return True


def clear_input_fields():
    # Clear all input data and return the input field to their default values
    date_var.set(current_date.strftime('%d-%b-%Y'))
    stock_code_var.set('')
    category_var.set('Dividend')
    total_shares_var.set('')
    location_var.set('Hong Kong')
    currency_var.set('HKD')
    transaction_cost_var.set('')
    amount_var.set('')
    description_var.set('')

    # Return the cursor to its original focus
    stock_code_entry.focus()


def save_button_clicked():
    # Generate a UUID for the transaction_id
    transaction_id = generate_transaction_id()

    stock_code = stock_code_var.get().strip()
    location = location_var.get()
    currency = currency_var.get()
    transaction_cost = transaction_cost_var.get().strip()
    amount = amount_var.get().strip()
    total_shares = total_shares_var.get().strip()
    category = category_var.get()
    seller_broker = broker_var.get()
    description = description_var.get().strip()

    if not stock_code:
        messagebox.showerror("Input Error", "Stock Code cannot be empty")
        return

    if not transaction_cost or not re.match(r'^\d+(\.\d{1,2})?$', transaction_cost):
        messagebox.showerror("Input Error", "Please enter a valid Transaction Cost")
        return

    if not amount or not re.match(r'^\d+(\.\d{1,2})?$', amount):
        messagebox.showerror("Input Error", "Please enter a valid Amount")
        return

    if category in ('Drip', 'Bonus Shares') and float(amount) != 0:
        messagebox.showerror("Input Error", "Amount must be 0 if Category is Drip or Bonus Shares")
        return

    if category in ('Buy', 'Sell', 'Dividend') and float(amount) == 0:
        messagebox.showerror("Input Error", "Amount cannot be 0 if Category is Buy, Sell or Dividend")
        return

    if not is_valid_total_shares(total_shares, category):
        messagebox.showerror("Input Error",
                             "Please enter a valid Total Shares. For Dividend, the Total Shares must be 0."
                             "For other Category, it must not be 0")
        return

    # Save the transaction to a file
    date = datetime.datetime.strptime(date_var.get(), '%d-%b-%Y').strftime('%m/%d/%Y')

    # Verify the folder to hold the transaction data files exists
    #folder_name = 'stock_transaction_data'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Save the data into the following file
    file_name = f'{folder_name}/stock_transactions_{date.split("/")[-1]}.csv'

    # Check if file exists
    file_exists = os.path.isfile(file_name)
    with open(file_name, 'a', newline='') as f:
        writer = csv.writer(f)

        # Write header row if file does not exist
        if not file_exists:
            writer.writerow(['transaction_id', 'date', 'stock_code', 'investment_category', 'transaction_type', 'total_shares', 'currency',
                             'transaction_costs', 'amount', 'location', 'owner', 'seller_broker', 'remarks'])

        # Instead of leaving the remarks column blank, save Nil if there is nothing included in the Description
        # input field
        if not description:
            description = "Nil"

        writer.writerow([transaction_id, date, stock_code, 'Stocks', category, total_shares, currency, transaction_cost, amount,
                         location, 'Wilson', seller_broker, description])

    messagebox.showinfo('Save Successful', 'Investment transaction saved successfully')

    clear_input_fields()


def display_transactions():
    # Get the current year
    date = datetime.datetime.strptime(date_var.get(), '%d-%b-%Y').strftime('%m/%d/%Y')

    # Set the file name based on the current year
    file_name = f'{folder_name}/stock_transactions_{date.split("/")[-1]}.csv'

    # Check if the file exists
    try:
        with open(file_name, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            transactions = [row for row in reader]
    except FileNotFoundError:
        messagebox.showerror('File Not Found', f'There is no record of your transactions. Please create one first')
        return

    # Create a new window to display the transactions
    display_window = tk.Toplevel(window)
    display_window.title('Show Last 10 Transactions')

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

    # Add a button to close the window
    close_button = ttk.Button(display_window, text='Close', command=display_window.destroy)
    close_button.pack(pady=10)


window = tk.Tk()
window.title('Stock Investments')

# Create the image object from the icon file
#icon = tk.PhotoImage(file='Icon for Program - Money.png')
# Set the window icon
#window.iconphoto(True, icon)

# Date input
date_label = ttk.Label(window, text='Date', anchor='w')
date_label.grid(row=0, column=0, padx=5, pady=5)
date_var = tk.StringVar(value=current_date.strftime('%d-%b-%Y'))
date_entry = ttk.Entry(window, textvariable=date_var, state='readonly', width=15)
date_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
calendar_button = ttk.Button(window, text='Select', command=lambda: calendar_select(date_var))
calendar_button.grid(row=0, column=2, padx=5, pady=5)

# Category input
category_label = ttk.Label(window, text='Category', anchor='w')
category_label.grid(row=1, column=0, padx=5, pady=5)
category_var = tk.StringVar(value='Dividend')
category_combobox = ttk.Combobox(window, textvariable=category_var, state='readonly', width=15)
category_combobox['values'] = ('Buy', 'Sell', 'Dividend', 'Drip', 'Bonus Shares')
category_combobox.grid(row=1, column=1, padx=5, pady=5, sticky='w')

# Stock Code input
stock_code_label = ttk.Label(window, text='Stock Code', anchor='w')
stock_code_label.grid(row=2, column=0, padx=5, pady=5)
stock_code_var = tk.StringVar()
stock_code_entry = ttk.Entry(window, textvariable=stock_code_var, width=15)
stock_code_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')
stock_code_entry.focus()

# Location input
location_label = ttk.Label(window, text='Location', anchor='w')
location_label.grid(row=3, column=0, padx=5, pady=5)
location_var = tk.StringVar(value='Hong Kong')
location_combobox = ttk.Combobox(window, textvariable=location_var, state='readonly', width=15)
location_combobox['values'] = ('Hong Kong', 'Malaysia', 'USA', 'Europe', 'China', 'Singapore', 'UK', 'Japan')
location_combobox.grid(row=3, column=1, padx=5, pady=5, sticky='w')

# Currency input
currency_label = ttk.Label(window, text='Currency', anchor='w')
currency_label.grid(row=4, column=0, padx=5, pady=5)
currency_var = tk.StringVar(value='HKD')
currency_combobox = ttk.Combobox(window, textvariable=currency_var, width=15)
currency_combobox['values'] = ('HKD', 'MYR', 'USD', 'EUR', 'CNY', 'SGD', 'GBP', 'JPY', 'Other')
currency_combobox.grid(row=4, column=1, padx=5, pady=5, sticky='w')

# Transaction Cost input
transaction_cost_label = ttk.Label(window, text='Transaction Costs', anchor='w')
transaction_cost_label.grid(row=5, column=0, padx=5, pady=5)
transaction_cost_var = tk.StringVar(value='')
transaction_cost_entry = ttk.Entry(window, textvariable=transaction_cost_var, validate='focusout', width=12)
transaction_cost_entry.grid(row=5, column=1, padx=5, pady=5, sticky='w')

currency_label_in_front = ttk.Label(window, textvariable=currency_var, font=('Arial', 8), foreground='#999999')
currency_label_in_front.place(x=175, y=165)

location_var.trace('w', update_currency)

# Amount input
amount_label = ttk.Label(window, text='Amount', anchor='w')
amount_label.grid(row=6, column=0, padx=5, pady=5)
amount_var = tk.StringVar()
amount_entry = ttk.Entry(window, textvariable=amount_var, validate='focusout', width=12)
amount_entry.grid(row=6, column=1, padx=5, pady=5, sticky='w')

currency_label_for_amount = ttk.Label(window, textvariable=currency_var, font=('Arial', 8), foreground='#999999')
currency_label_for_amount.place(x=175, y=196)

# Broker input
broker_label = ttk.Label(window, text='Broker', anchor='w')
broker_label.grid(row=7, column=0, padx=5, pady=5)
broker_var = tk.StringVar(value='BOOM')
broker_combobox = ttk.Combobox(window, textvariable=broker_var, state='readonly', width=10)
broker_combobox['values'] = ('BOOM', 'Gaven')
broker_combobox.grid(row=7, column=1, padx=5, pady=5, sticky='w')

# Total Shares input
total_shares_label = ttk.Label(window, text='Total Shares', anchor='w')
total_shares_label.grid(row=8, column=0, padx=5, pady=5)
total_shares_var = tk.StringVar()
total_shares_entry = ttk.Entry(window, textvariable=total_shares_var, validate='focusout', width=12)
total_shares_entry.grid(row=8, column=1, padx=5, pady=5, sticky='w')

# Description input
description_label = ttk.Label(window, text='Description', anchor='w')
description_label.grid(row=9, column=0, padx=5, pady=5)
description_var = tk.StringVar()
description_entry = ttk.Entry(window, textvariable=description_var, width=20)
description_entry.grid(row=9, column=1, padx=5, pady=5, sticky='w')

# Button frame
button_frame = ttk.Frame(window)
button_frame.grid(row=9, column=0, columnspan=2, padx=5, pady=15)

# Save button
save_button = ttk.Button(button_frame, text='Save')
save_button.grid(row=0, column=0, padx=5)
save_button.config(command=save_button_clicked)

# Display button
display_button = ttk.Button(button_frame, text='Display', command=display_transactions)
display_button.grid(row=0, column=1, padx=5)

# Back button
def close_window():
    window.destroy()


back_button = ttk.Button(button_frame, text='Back', command=close_window)
back_button.grid(row=0, column=2, padx=5)


window.mainloop()