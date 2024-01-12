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
folder_name = 'apartment_expenses_transaction_data'


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


window = tk.Tk()
window.title('Apartment Related Expenses')