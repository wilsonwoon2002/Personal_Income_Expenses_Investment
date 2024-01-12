import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import Calendar
import datetime
import re
import csv
import uuid


# Today's or Computer's Date
current_date = datetime.date.today()
current_year = current_date.year
current_month = current_date.month
current_day = current_date.day

# Create the folder to hold the transaction data files
folder_name = 'salary_transaction_data'


def calendar_select(calendar_var):
    def update_date():
        selected_date = calendar.selection_get()
        calendar_var.set(selected_date.strftime('%d-%b-%Y'))
        calendar_window.destroy()

    calendar_window = tk.Toplevel(window)
    calendar_window.title('Calendar')
    #calendar = tkcalendar.Calendar(calendar_window, selectmode='day', year=current_year, month=current_month,
    #                              day=current_day)
    calendar = Calendar(calendar_window, selectmode='day', year=current_year, month=current_month,
                                   day=current_day)
    calendar.pack(padx=10, pady=10)
    ok_button = ttk.Button(calendar_window, text='OK', command=update_date)
    ok_button.pack(pady=10)

def generate_transaction_id():
    transaction_id = uuid.uuid4()
    return str(transaction_id)


def calculate_net_salary(*args):
    try:
        gross = float(gross_salary_var.get().strip().replace(',', ''))
        mpf_employee = float(mpf_employee_var.get().strip().replace(',', ''))
        gratuity = float(gratuity_var.get().strip().replace(',', ''))
        misc = float(misc_var.get().strip().replace(',', ''))
        net_salary = gross - mpf_employee + gratuity + misc
        net_salary_formatted = f"{net_salary:,.2f}"  # Format the net_salary with thousand separators
        net_salary_var.set(net_salary_formatted)
    except ValueError:
        pass


def format_entry_with_separator(event):
    entry = event.widget
    try:
        # Check if the widget is misc_entry and preserve the sign
        if entry == misc_entry:
            sign = ''
            value = entry.get().strip().replace(',', '')
            if value.startswith('+') or value.startswith('-'):
                sign = value[0]
                value = value[1:]
            value = float(value)
            entry.delete(0, tk.END)
            entry.insert(0, f"{sign}{value:,.2f}")
        else:
            value = float(entry.get().replace(',', ''))
            entry.delete(0, tk.END)
            entry.insert(0, f"{value:,.2f}")
    except ValueError:
        pass


def clear_input_fields():
    date_var.set(current_date.strftime('%d-%b-%Y'))
    gross_salary_var.set('')
    mpf_employee_var.set('')
    mpf_employer_var.set('')
    gratuity_var.set('0')
    others_var.set('0')
    misc_var.set('+0')
    net_salary_var.set('')
    remarks_var.set('')
    # Return the cursor to its original focus
    gross_salary_entry.focus()


def save_button_clicked():
    # Generate a UUID for the transaction_id
    transaction_id = generate_transaction_id()

    # Parse the date and store day, month, and year in their respective variables
    date_input = datetime.datetime.strptime(date_var.get(), '%d-%b-%Y')
    day, month, year = date_input.day, date_input.month, date_input.year

    # Format the date as desired (in this case, '%m/%d/%Y')
    date = date_input.strftime('%m/%d/%Y')

    gross = gross_salary_var.get().strip().replace(',', '')
    mpf_employee = mpf_employee_var.get().strip().replace(',', '')
    mpf_employer = mpf_employer_var.get().strip().replace(',', '')
    gratuity = gratuity_var.get().strip().replace(',', '')
    others = others_var.get().strip().replace(',', '')
    misc = misc_var.get().strip().replace(',', '')
    net_salary = net_salary_var.get().strip().replace(',', '')
    remarks = remarks_var.get().strip()

    if not gross or not re.match(r'^\d+(\.\d{1,2})?$', gross):
        messagebox.showerror("Input Error", "Please enter a valid amount for Gross Salary")
        return

    if not mpf_employee or not re.match(r'^\d+(\.\d{1,2})?$', mpf_employee):
        messagebox.showerror("Input Error", "Please enter a valid amount for Employee MPF")
        return

    if not mpf_employer or not re.match(r'^\d+(\.\d{1,2})?$', mpf_employer):
        messagebox.showerror("Input Error", "Please enter a valid amount for Employer MPF")
        return

    if gratuity.strip() == "":
        messagebox.showerror("Input Error", "Please enter an amount for Gratuity")
        return

    if gratuity and not re.match(r'^\d+(\.\d{1,2})?$', gratuity):
        messagebox.showerror("Input Error", "Please enter a valid amount for Gratuity")
        return

    if others.strip() == "":
        messagebox.showerror("Input Error", "Please enter a amount for Other Benefits")
        return

    if others and not re.match(r'^\d+(\.\d{1,2})?$', others):
        messagebox.showerror("Input Error", "Please enter a valid amount for Other Benefits")
        return

    if not re.match(r'^[+-]\d+(\.\d{1,2})?$', misc):
        messagebox.showerror("Input Error",
                             "Please enter a valid amount for Misc. (must start with + or -)")
        return

    if not net_salary or not re.match(r'^\d+(\.\d{1,2})?$', net_salary):
        messagebox.showerror("Input Error", "Please enter a valid amount for Net Salary")
        return

    # Remove the '+' sign from Misc. if it exists
    if misc.startswith('+'):
        misc = misc[1:]

    # Insert a column for Tax Assessment Year
    # In HK, the fiscal year runs from 1 April of a year to 31 March of the following year
    # Determine the start and end of the fiscal year
    if month < 4:
        # fiscal year starts in the previous year
        start_fiscal_year = datetime.datetime(year - 1, 4, 1)
        end_fiscal_year = datetime.datetime(year, 3, 31)
    else:
        # fiscal year starts in the current year
        start_fiscal_year = datetime.datetime(year, 4, 1)
        end_fiscal_year = datetime.datetime(year + 1, 3, 31)

    # format the start and end of the fiscal year as yyyy_yyyy
    fiscal_year = f"{start_fiscal_year.year}_{end_fiscal_year.year}"

    # Create a new row of data
    row = [transaction_id, date, 'HKD', gross, net_salary, mpf_employee, mpf_employer, fiscal_year, gratuity, misc, 'HKUST', remarks]

    # Verify the folder to hold the salary data files exists
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Save the data into the following file
    file_name = f'{folder_name}/salary_in_{date.split("/")[-1]}.csv'

    # Check if file exists
    file_exists = os.path.isfile(file_name)
    with open(file_name, 'a', newline='') as f:
        writer = csv.writer(f)

        # Write header row if file does not exist
        if not file_exists:
            writer.writerow(['transaction_id', 'date', 'currency', 'gross', 'net', 'mpf_employee', 'mpf_employer', 'fiscal_year',
                            'gratuity', 'misc', 'location', 'remarks'])

        # Instead of leaving the remarks column blank, save Nil if there is nothing included in the Remarks
        # input field
        if not remarks:
            remarks = "Nil"

        writer.writerow(row)

    messagebox.showinfo('Save Successful', 'Salary saved successfully')

    clear_input_fields()


def display_transactions():
    # Get the current year
    date = datetime.datetime.strptime(date_var.get(), '%d-%b-%Y').strftime('%m/%d/%Y')

    # Set the file name based on the current year
    file_name = f'{folder_name}/salary_in_{date.split("/")[-1]}.csv'

    # Check if the file exists
    try:
        with open(file_name, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            transactions = [row for row in reader][-5:]
    except FileNotFoundError:
        messagebox.showerror('File Not Found', f'There is no record of your salary. Please create one first')
        return

    # Create a new window to display the transactions
    display_window = tk.Toplevel(window)
    display_window.title('Last 3 months salary')

    # Create a treeview widget to display the data in a table
    tree = ttk.Treeview(display_window, columns=headers, show='headings')
    tree.pack(side='left')

    # Add columns to the treeview
    for header in headers:
        tree.heading(header, text=header, anchor='w')
        tree.column(header, width=100, anchor='w')

    # Add the last 3 transactions to the treeview
    num_transactions = min(len(transactions), 5)
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
window.title('Salary')

# Date input
date_label = ttk.Label(window, text='Date', anchor='e')
date_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
date_var = tk.StringVar(value=current_date.strftime('%d-%b-%Y'))
date_entry = ttk.Entry(window, textvariable=date_var, state='readonly', width=15)
date_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
calendar_button = ttk.Button(window, text='Select', command=lambda: calendar_select(date_var))
calendar_button.grid(row=0, column=2, padx=5, pady=5)

# Gross Salary input
gross_salary_label = ttk.Label(window, text='Gross Salary', anchor='e')
gross_salary_label.grid(row=5, column=0, padx=5, pady=5, sticky='e')
gross_salary_var = tk.StringVar(value='')
gross_salary_entry = ttk.Entry(window, textvariable=gross_salary_var, validate='focusout', width=12)
gross_salary_entry.grid(row=5, column=1, padx=5, pady=5, sticky='w')
gross_salary_entry.focus()
gross_salary_entry.bind("<FocusOut>", format_entry_with_separator)

currency_label_in_front = ttk.Label(window, text='HKD', font=('Arial', 8), foreground='#999999')
currency_label_in_front.place(x=188, y=41)

# Create a label frame for the benefits section
benefits_label_frame = ttk.LabelFrame(window, text='Benefits:', borderwidth=4, relief="solid")

# MPF (Employee) input
mpf_employee_label = ttk.Label(benefits_label_frame, text='MPF (Employee)', anchor='e')
mpf_employee_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
mpf_employee_var = tk.StringVar(value='')
mpf_employee_entry = ttk.Entry(benefits_label_frame, textvariable=mpf_employee_var, validate='focusout', width=12)
mpf_employee_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
mpf_employee_entry.bind("<FocusOut>", format_entry_with_separator)

currency_label_in_front = ttk.Label(benefits_label_frame, text='HKD', font=('Arial', 8), foreground='#999999')
currency_label_in_front.grid(row=0, column=2, padx=0, pady=5)

# MPF (Employer) input
mpf_employer_label = ttk.Label(benefits_label_frame, text='MPF (Employer)', anchor='e')
mpf_employer_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')
mpf_employer_var = tk.StringVar(value='')
mpf_employer_entry = ttk.Entry(benefits_label_frame, textvariable=mpf_employer_var, validate='focusout', width=12)
mpf_employer_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')
mpf_employer_entry.bind("<FocusOut>", format_entry_with_separator)

currency_label_in_front = ttk.Label(benefits_label_frame, text='HKD', font=('Arial', 8), foreground='#999999')
currency_label_in_front.grid(row=1, column=2, padx=0, pady=5)

# Gratuity input
gratuity_label = ttk.Label(benefits_label_frame, text='Gratuity', anchor='e')
gratuity_label.grid(row=2, column=0, padx=5, pady=5, sticky='e')
gratuity_var = tk.StringVar(value='0')
gratuity_entry = ttk.Entry(benefits_label_frame, textvariable=gratuity_var, validate='focusout', width=12)
gratuity_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')
gratuity_entry.bind("<FocusOut>", format_entry_with_separator)

currency_label_in_front = ttk.Label(benefits_label_frame, text='HKD', font=('Arial', 8), foreground='#999999')
currency_label_in_front.grid(row=2, column=2, padx=0, pady=5)

# Others input
others_label = ttk.Label(benefits_label_frame, text='Others', anchor='e')
others_label.grid(row=3, column=0, padx=5, pady=5, sticky='e')
others_var = tk.StringVar(value='0')
others_entry = ttk.Entry(benefits_label_frame, textvariable=others_var, validate='focusout', width=12)
others_entry.grid(row=3, column=1, padx=5, pady=5, sticky='w')
others_entry.bind("<FocusOut>", format_entry_with_separator)

currency_label_in_front = ttk.Label(benefits_label_frame, text='HKD', font=('Arial', 8), foreground='#999999')
currency_label_in_front.grid(row=3, column=2, padx=0, pady=5)

# Add the benefits label frame to the grid layout
benefits_label_frame.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

# Misc. input
misc_label = ttk.Label(window, text='Misc. (+/-)', anchor='e')
misc_label.grid(row=7, column=0, padx=5, pady=5, sticky='e')
misc_var = tk.StringVar(value='+0')
misc_entry = ttk.Entry(window, textvariable=misc_var, validate='focusout', width=12)
misc_entry.grid(row=7, column=1, padx=5, pady=5, sticky='w')
misc_entry.bind("<FocusOut>", format_entry_with_separator)

currency_label_in_front = ttk.Label(window, text='HKD', font=('Arial', 8), foreground='#999999')
currency_label_in_front.place(x=188, y=230)

# Net Salary input
net_salary_label = ttk.Label(window, text='Net Salary', anchor='e')
net_salary_label.grid(row=8, column=0, padx=5, pady=5, sticky='e')
net_salary_var = tk.StringVar(value='')
net_salary_entry = ttk.Entry(window, textvariable=net_salary_var, width=12)
net_salary_entry.grid(row=8, column=1, padx=5, pady=5, sticky='w')

currency_label_in_front = ttk.Label(window, text='HKD', font=('Arial', 8), foreground='#999999')
currency_label_in_front.place(x=188, y=260)

# Add trace to each variable to calculate Net Salary dynamically
gross_salary_var.trace_add("write", calculate_net_salary)
mpf_employee_var.trace_add("write", calculate_net_salary)
gratuity_var.trace_add("write", calculate_net_salary)
misc_var.trace_add("write", calculate_net_salary)

# Remarks input
remarks_label = ttk.Label(window, text='Remarks', anchor='e')
remarks_label.grid(row=9, column=0, padx=5, pady=5, sticky='e')
remarks_var = tk.StringVar(value='')
remarks_entry = ttk.Entry(window, textvariable=remarks_var, width=15)
remarks_entry.grid(row=9, column=1, padx=5, pady=5, sticky='w')

# Create a new frame for the Save and Back buttons
button_frame = tk.Frame(window)

# Place the button frame in the grid layout
button_frame.grid(row=11, column=0, columnspan=2, pady=10)

# Save button
save_button = ttk.Button(button_frame, text='Save')
save_button.grid(row=0, column=0, padx=5, pady=15, sticky='w')
save_button.config(command=save_button_clicked)

# Display button
display_button = ttk.Button(button_frame, text='Display', command=display_transactions)
display_button.grid(row=0, column=1, padx=5)

# Back button
back_button = ttk.Button(button_frame, text='Back', command=window.destroy)
back_button.grid(row=0, column=2, padx=2, pady=15)


window.mainloop()

# import PySimpleGUI as sg
# import csv
# import datetime
# import calendar
# import re
#
#
# # Define a function to validate the date
# def validate_date(day, month, year):
#     try:
#         max_day = calendar.monthrange(year, month)[1]
#         if int(day) > max_day:
#             return f"Error: {calendar.month_name[month]} has a maximum of {max_day} days"
#         else:
#             return None
#     except ValueError:
#         return "Error: Invalid Date"
#
# # Set the dark theme
# sg.theme('Dark')
#
# # Set the copyright and version number
# copyright = 'Copyright (c) 2023 Wilson Woon. All rights reserved.'
# version = 'Version 1.0'
#
# # Get the current date
# now = datetime.datetime.now()
# current_day = now.day
# current_month = now.month
# current_year = now.year
#
# # Define the layout of the Salary menu
# layout = [
#     [sg.Text('Salary', font=('Arial', 20))],
#     [sg.Text('Date:'),
#      sg.DropDown(values=[str(i) for i in range(1, 32)], default_value=str(current_day), size=(3, 1), key='day'),
#      sg.DropDown(values=[str(i) for i in range(1, 13)], default_value=str(current_month), size=(3, 1), key='month'),
#      sg.DropDown(values=[str(i) for i in range(2020, 2031)], default_value=str(current_year), size=(5, 1), key='year')],
#     [sg.Text('Currency: HKD')],
#     [sg.Text('Gross Salary:'), sg.InputText(key='gross', size=(15, 1), focus=True)],
#     [sg.Text('Net Salary:'), sg.InputText(key='net', size=(15, 1))],
#     [sg.Text('MPF (Employee):'), sg.InputText(key='mpf_employee', size=(15, 1))],
#     [sg.Text('MPF (Employer):'), sg.InputText(key='mpf_employer', size=(15, 1))],
#     #[sg.Text('Tax Payment:'), sg.InputText(default_text='0', key='tax_payment', size=(15, 1))],
#     #[sg.Text('Tax Refund:'), sg.InputText(default_text='0', key='tax_refund', size=(15, 1))],
#     [sg.Text('Gratuity:'), sg.InputText(default_text='0', key='gratuity', size=(15, 1))],
#     [sg.Text('Misc.:'), sg.DropDown(values=['+', '-'], default_value='+', key='misc_dropdown', size=(2, 1)), sg.InputText(default_text='0', key='misc_amount', size=(10, 1))],
#     [sg.Text('Remarks:'), sg.InputText(default_text='Nil', key='remarks', size=(30,1))],
#     [sg.Button('Save'), sg.Button('Back')],
#     [sg.Text(copyright)],
#     [sg.Text(version)]
# ]
#
# # Create the Apartment Expenses window
# window = sg.Window('Salary', layout)
#
# # Loop to process events and get user input
# while True:
#     event, values = window.read()
#     if event == sg.WIN_CLOSED or event == 'Back':
#         # Close the window when the Back button or X button is clicked
#         break
#     elif event == 'Save':
#         # Get the user input and save the data into a CSV file
#         day = int(values['day'])
#         month = int(values['month'])
#         year = int(values['year'])
#         date = '{}/{}/{}'.format(month, day, year)
#
#         gross = values['gross']
#         net = values['net']
#         mpf_employee = values['mpf_employee']
#         mpf_employer = values['mpf_employer']
#         #tax_payment = values['tax_payment']
#         #tax_refund = values['tax_refund']
#         gratuity = values['gratuity']
#         misc_dropdown = values['misc_dropdown']
#         misc_amount = values['misc_amount']
#         remarks = values.get('remarks', '')[:200]  #
#
#         # Validate the Transaction Date
#         error_message = validate_date(day, month, year)
#         if error_message is not None:
#             sg.popup(f"{error_message}", title='Validation Error')
#             continue
#
#         # Validate Gross amount input
#         # Check if amount is a valid number
#         if not re.match(r'^\d*\.?\d{0,2}$', gross) or not gross or float(gross) < 0:
#             sg.popup('Invalid Gross Salary. Please enter a valid amount with at most 2 decimal places.',
#                     title='Validation Error')
#             continue
#
#         # Validate Net amount input
#         # Check if amount is a valid number
#         if not re.match(r'^\d*\.?\d{0,2}$', net) or not net or float(net) < 0:
#             sg.popup('Invalid Net Salary. Please enter a valid amount with at most 2 decimal places.',
#                     title='Validation Error')
#             continue
#
#         # Ensure Net Salary is less than or equal to Gross Salary
#         if float(net) > float(gross):
#             sg.popup('Net Salary cannot be greater than Gross Salary. Please enter a valid salary.',
#                      title='Validation Error')
#             continue
#
#         # Validate MPF Employee and Employer input
#         # Check if amount is a valid number
#         if not re.match(r'^\d*\.?\d{0,2}$', mpf_employee) or not mpf_employee or float(mpf_employee) < 0:
#             sg.popup('Invalid Employee MPF. Please enter a valid amount with at most 2 decimal places.',
#                     title='Validation Error')
#             continue
#
#         if not re.match(r'^\d*\.?\d{0,2}$', mpf_employer) or not mpf_employer or float(mpf_employer) < 0:
#             sg.popup('Invalid Employer MPF. Please enter a valid amount with at most 2 decimal places.',
#                     title='Validation Error')
#             continue
#
#         # Validate Tax Payment and Refund input
#         # Check if amount is a valid number
#         #if not re.match(r'^\d*\.?\d{0,2}$', tax_payment) or not tax_payment or float(tax_payment) < 0:
#         #    sg.popup('Invalid Tax Payment. Please enter a valid amount with at most 2 decimal places.',
#         #            title='Validation Error')
#         #    continue
#
#         #if not re.match(r'^\d*\.?\d{0,2}$', tax_refund) or not tax_refund or float(tax_refund) < 0:
#         #    sg.popup('Invalid Tax Refund. Please enter a valid amount with at most 2 decimal places.',
#         #            title='Validation Error')
#         #    continue
#
#         # Validate Gratuity input
#         # Check if amount is a valid number
#         if not re.match(r'^\d*\.?\d{0,2}$', gratuity) or not gratuity or float(gratuity) < 0:
#             sg.popup('Invalid Gratuity. Please enter a valid amount with at most 2 decimal places.',
#                     title='Validation Error')
#             continue
#
#         # Validate Misc. input
#         # Check if amount is a valid number
#         if not re.match(r'^\d*\.?\d{0,2}$', misc_amount) or not misc_amount or float(misc_amount) < 0:
#             sg.popup('Invalid Misc. Please enter a valid amount with at most 2 decimal places.',
#                     title='Validation Error')
#             continue
#
#         # Concatenate the misc input values
#         if(misc_dropdown == '-'):
#             misc = '-' + misc_amount
#         else:
#             misc = misc_amount
#
#         # Insert a column for Tax Assessment Year
#         # In HK, the fiscal year runs from 1 April of a year to 31 March of the following year
#         # Determine the start and end of the fiscal year
#         if month < 4:
#             # fiscal year starts in the previous year
#             start_fiscal_year = datetime.datetime(year - 1, 4, 1)
#             end_fiscal_year = datetime.datetime(year, 3, 31)
#         else:
#             # fiscal year starts in the current year
#             start_fiscal_year = datetime.datetime(year, 4, 1)
#             end_fiscal_year = datetime.datetime(year + 1, 3, 31)
#
#         # format the start and end of the fiscal year as yyyy_yyyy
#         fiscal_year = f"{start_fiscal_year.year}_{end_fiscal_year.year}"
#
#         # Create a new row of data
#         row = [date, gross, net, mpf_employee, mpf_employer, fiscal_year, gratuity, misc, 'HKUST', remarks]
#
#         # Append the row to the CSV file
#         filename = f'salary_{year}.csv'
#         with open(filename, 'a', newline='') as csv_file:
#             writer = csv.writer(csv_file)
#             if csv_file.tell() == 0:
#                 # Write the header row if the file is empty
#                 writer.writerow(['date', 'gross', 'net', 'mpf_employee', 'mpf_employer', 'fiscal_year',
#                                  'gratuity', 'misc', 'location', 'remarks'])
#             writer.writerow(row)
#
#         # Display a message to indicate that the data has been saved
#         sg.popup('Salary saved successfully!', title='Success')
#
#         # Clear or reset all the input values to their default values
#         values['day'] = str(current_day)
#         values['month'] = str(current_month)
#         values['year'] = str(current_year)
#         values['gross'] = ''
#         values['net'] = ''
#         values['mpf_employee'] = ''
#         values['mpf_employer'] = ''
#         #values['tax_payment'] = '0'
#         #values['tax_refund'] = '0'
#         values['gratuity'] = '0'
#         values['misc_dropdown'] = '+'
#         values['misc_amount'] = '0'
#         values['remarks'] = 'Nil'
#
#         # Update the window with the cleared or default values
#         window['day'].update(value=str(current_day))
#         window['month'].update(value=str(current_month))
#         window['year'].update(value=str(current_year))
#         window['gross'].update(value='')
#         window['net'].update(value='')
#         window['mpf_employee'].update(value='')
#         window['mpf_employer'].update(value='')
#         #window['tax_payment'].update(value='0')
#         #window['tax_refund'].update(value='0')
#         window['gratuity'].update(value='0')
#         window['misc_dropdown'].update(value='+')
#         window['misc_amount'].update(value='0')
#         window['remarks'].update(value='Nil')
#         window['gross'].set_focus()
#
# # Close the window
# window.close()