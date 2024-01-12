import tkinter as tk
import subprocess

# Define the main window
root = tk.Tk()
root.title("Income & Expenses Tracker")

# Set the window size
window_width = 320
window_height = 340
root.geometry(f"{window_width}x{window_height}")

# Create a frame to hold the menu buttons
menu_frame = tk.Frame(root)
menu_frame.pack()

button_font = ("Arial", 14)  # Set the desired font and size for the button labels

# Create and place the menu buttons
personal_expenses_button = tk.Button(menu_frame, text="Personal Expenses", font=button_font, command=lambda:
subprocess.run(["python", "personal_expenses.py"]))
personal_expenses_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

#apartment_expenses_button = tk.Button(menu_frame, text="Apartment Expenses", font=button_font, command=lambda:
#apartment_expenses())
#apartment_expenses_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

salary_button = tk.Button(menu_frame, text="Salary", font=button_font, command=lambda:
subprocess.run(["python", "salary.py"]))
salary_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

investment_income_button = tk.Button(menu_frame, text="Investment Income", font=button_font, command=lambda:
subprocess.run(["python", "stocks.py"]))
investment_income_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

exit_button = tk.Button(menu_frame, text="Exit", font=button_font, command=root.destroy)
exit_button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

# Add the copyright notice and version information
copyright_label = tk.Label(root, text="© 2023-2024 Wilson Woon. All rights reserved.")
copyright_label.pack()

version_label = tk.Label(root, text="Version 2.0")
version_label.pack()


# Define the functions for remaining menu buttons (apartment expenses, salary, investment income)
def apartment_expenses():
    # Implement your code for handling apartment expenses
    pass


def salary():
    # Implement your code for handling salary
    pass


def investment_income():
    # Implement your code for handling investment income
    pass


# Start the mainloop
root.mainloop()