import sqlite3
from tkinter import Tk, Listbox, Button, messagebox, Toplevel, Label, Entry, simpledialog, filedialog, END
import datetime
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from tkinter import messagebox, Tk, Button, Label, Listbox, Entry, StringVar, END
from flask import Flask, send_file
# Establish a connection to the database
conn = sqlite3.connect('electric_bills.db')
cursor = conn.cursor()

# Create the Customers table if it does not exist
cursor.execute('''
        CREATE TABLE IF NOT EXISTS Customers (
        CustomerID INTEGER PRIMARY KEY,
        name TEXT,
        Address TEXT,
        AccountNumber TEXT,
        DateOfBill DATE,
        MeterNumber TEXT,
        PresentMeterReading INTEGER,
        FuelClauseAdjustment INTEGER
        )
''')


class ElectricBillSystem:

    def __init__(self, root):
        self.root = root
        self.root.title("Electric Bill System")
        self.conn = sqlite3.connect('electric_bills.db')
        self.cursor = self.conn.cursor()

        self.customer_listbox = Listbox(root, width=50)
        self.customer_listbox.pack(padx=20, pady=20)

        self.add_button = Button(root, text="Add Customer", command=self.add_customer)
        self.add_button.pack()

        self.edit_button = Button(root, text="Edit Customer", command=self.edit_customer)
        self.edit_button.pack()

        self.delete_button = Button(root, text="Delete Customer", command=self.delete_customer)
        self.delete_button.pack()

        print_button = Button(root, text="Print Bill", command=self.print_bill)
        print_button.pack()

        self.load_customers()

    def load_customers(self):
        self.cursor.execute('SELECT CustomerID, name FROM Customers')  # Use 'name' instead of 'CustomerName'
        customers = self.cursor.fetchall()
        for customer in customers:
            self.customer_listbox.insert(END, f"Customer ID: {customer[0]} - Name: {customer[1]}")

    def add_customer(self):
        add_customer_window = Toplevel(self.root)
        add_customer_window.title("Add Customer")

        # Labels and Entry widgets for user input
        Label(add_customer_window, text="Customer Name:").pack()
        name_entry = Entry(add_customer_window)
        name_entry.pack()

        Label(add_customer_window, text="Address:").pack()
        address_entry = Entry(add_customer_window)
        address_entry.pack()

        Label(add_customer_window, text="AccountNumber:").pack()
        accountnumber_entry = Entry(add_customer_window)
        accountnumber_entry.pack()

        Label(add_customer_window, text="DateOfBill:").pack()
        dateofbill_entry = Entry(add_customer_window)
        dateofbill_entry.pack()

        Label(add_customer_window, text="MeterNumber:").pack()
        meternumber_entry = Entry(add_customer_window)
        meternumber_entry.pack()

        Label(add_customer_window, text="PresentMeterReading:").pack()
        presentmeterreading_entry = Entry(add_customer_window)
        presentmeterreading_entry.pack()

        Label(add_customer_window, text="FuelClauseAdjustment:").pack()
        fuelclauseadjustment_entry = Entry(add_customer_window)
        fuelclauseadjustment_entry.pack()

        # Function to handle adding customer to the database
        def add_to_database(add_customer_window):
            name = name_entry.get()
            address = address_entry.get()
            accountnumber = accountnumber_entry.get()
            dateofbill = dateofbill_entry.get()
            meternumber = meternumber_entry.get()
            presentmeterreading = presentmeterreading_entry.get()
            fuelclauseadjustment = fuelclauseadjustment_entry.get()

            if not all(
                    [name, address, accountnumber, dateofbill, meternumber, presentmeterreading, fuelclauseadjustment]):
                messagebox.showerror("Error", "Please fill in all fields")
                return

            try:
                datetime.strptime(dateofbill, '%Y-%m-%d')  # Assuming date format is YYYY-MM-DD
            except ValueError:
                messagebox.showerror("Error", "Date of Bill should be in YYYY-MM-DD format")
                return

            # Insert customer into the Customers table
            self.cursor.execute('''INSERT INTO Customers (name, address, AccountNumber, DateOfBill, MeterNumber, PresentMeterReading, FuelClauseAdjustment) 
                                       VALUES (?, ?, ?, ?, ?, ?, ?)''', (name, address, accountnumber, dateofbill, meternumber, presentmeterreading, fuelclauseadjustment))
            self.conn.commit()

            messagebox.showinfo("Success", f"Customer {name} added successfully.")
            add_customer_window.destroy()  # Close the window after adding customer

            # Refresh the customer list in the main window
            self.customer_listbox.delete(0, 'end')
            self.load_customers()

        # Button to confirm adding customer
        confirm_button = Button(add_customer_window, text="Add Customer",
                                command=lambda: add_to_database(add_customer_window))
        confirm_button.pack()

    def edit_customer(self):
        selected_customer = self.customer_listbox.curselection()
        if not selected_customer:
            messagebox.showerror("Error", "Please select a customer.")
            return

        customer_id = selected_customer[0] + 1 # Customer ID starts from 1 in the database

        # Fetch customer details from the database
        customer_data = self.fetch_customer_details(customer_id)

        # Debugging: Print customer_id and customer_data
        print("Customer ID:", customer_id)
        print("Customer Data:", customer_data)

        # Rest of your edit_customer logic...

        # Create a new window for editing customer details
        edit_window = Toplevel(self.root)
        edit_window.title("Edit Customer")

        # Labels and Entry widgets for editing customer details
        Label(edit_window, text="Name:").grid(row=0, column=0)
        name_entry = Entry(edit_window)
        name_entry.grid(row=0, column=1)
        name_entry.insert(0, customer_data["name"])  # Pre-fill with current name

        Label(edit_window, text="Address:").grid(row=1, column=0)
        address_entry = Entry(edit_window)
        address_entry.grid(row=1, column=1)
        address_entry.insert(0, customer_data["address"])  # Pre-fill with current address

        Label(edit_window, text="AccountNumber:").grid(row=2, column=0)
        accountnumber_entry = Entry(edit_window)
        accountnumber_entry.grid(row=2, column=1)
        accountnumber_entry.insert(0, customer_data["accountnumber"])

        Label(edit_window, text="DateOfBill:").grid(row=3, column=0)
        dateofbill_entry = Entry(edit_window)
        dateofbill_entry.grid(row=3, column=1)
        dateofbill_entry.insert(0, customer_data["dateofbill"])

        Label(edit_window, text="MeterNumber:").grid(row=4, column=0)
        meternumber_entry = Entry(edit_window)
        meternumber_entry.grid(row=4, column=1)
        meternumber_entry.insert(0, customer_data["meternumber"])

        Label(edit_window, text="PresentMeterReading:").grid(row=5, column=0)
        presentmeterreading_entry = Entry(edit_window)
        presentmeterreading_entry.grid(row=5, column=1)
        presentmeterreading_entry.insert(0, customer_data["presentmeterreading"])

        Label(edit_window, text="FuelClauseAdjustment:").grid(row=6, column=0)
        fuelclauseadjustment_entry = Entry(edit_window)
        fuelclauseadjustment_entry.grid(row=6, column=1)
        fuelclauseadjustment_entry.insert(0, customer_data["fuelclauseadjustment"])


        def update_customer_details():
            new_name = name_entry.get()
            new_address = address_entry.get()
            new_accountnumber = accountnumber_entry.get()
            new_dateofbill = dateofbill_entry.get()
            new_meternumber = meternumber_entry.get()
            new_presentmeterreading = presentmeterreading_entry.get()
            new_fuelclauseadjustment = fuelclauseadjustment_entry.get()

            # Update customer details in the database (replace this with actual database update query)
            self.update_customer_in_database(customer_id, new_name, new_address, new_accountnumber, new_dateofbill,
                                             new_meternumber, new_presentmeterreading, new_fuelclauseadjustment)

            messagebox.showinfo("Success", "Customer details updated successfully.")
            edit_window.destroy()  # Close the window after updating customer details

            # Refresh the customer list in the main window
            self.customer_listbox.delete(0, 'end')
            self.load_customers()

        # Button to confirm updating customer details
        confirm_button = Button(edit_window, text="Update Details", command=update_customer_details)
        confirm_button.grid(row=7, columnspan=2)

    def update_customer_in_database(self, customer_id, new_name, new_address, new_accountnumber, new_dateofbill,
                                        new_meternumber, new_presentmeterreading, new_fuelclauseadjustment):
            # Update the customer details in the database based on customer_id
            self.cursor.execute('''UPDATE Customers 
                                   SET name=?, address=?, AccountNumber=?, DateOfBill=?, MeterNumber=?, 
                                       PresentMeterReading=?, FuelClauseAdjustment=? 
                                   WHERE CustomerID=?''',
                                (new_name, new_address, new_accountnumber, new_dateofbill, new_meternumber,
                                 new_presentmeterreading, new_fuelclauseadjustment, customer_id))
            self.conn.commit()

    def delete_customer(self):
        selected_customer = self.customer_listbox.curselection()
        if not selected_customer:
            messagebox.showerror("Error", "Please select a customer.")
            return

        customer_id = selected_customer[0] + 1  # Customer ID starts from 1 in the database

        # Implement the logic to delete the selected customer from the database
        self.cursor.execute('DELETE FROM Customers WHERE CustomerID = ?', (customer_id,))
        self.conn.commit()

        messagebox.showinfo("Delete Customer", f"Customer ID: {customer_id} has been deleted.")
        self.customer_listbox.delete(0, 'end')  # Clear the listbox
        self.load_customers()

    def calculate_bill_for_customer(self, units_consumed):
        # Method to calculate the electricity bill for a customer
        if units_consumed < 50:
            amount = units_consumed * 2.60
            surcharge = 25
        elif units_consumed <= 100:
            amount = 130 + ((units_consumed - 50) * 3.25)
            surcharge = 35
        elif units_consumed <= 200:
            amount = 130 + 162.50 + ((units_consumed - 100) * 5.26)
            surcharge = 45
        else:
            amount = 130 + 162.50 + 526 + ((units_consumed - 200) * 8.45)
            surcharge = 75

        total = amount + surcharge
        return total
    def fetch_customer_details(self, customer_id):
        # Connect to your SQLite database
        conn = sqlite3.connect('electric_bills.db')
        cursor = conn.cursor()

        # Execute the SQL query to fetch customer details based on customer_id
        cursor.execute(
            'SELECT name, address, accountnumber, dateofbill, meternumber, presentmeterreading, fuelclauseadjustment FROM Customers WHERE CustomerID = ?',
            (customer_id,))
        customer_data = cursor.fetchone()

        # Close the database connection
        conn.close()

        # Check if customer_data is not None and format it as a dictionary
        if customer_data:
            keys = ['name', 'address', 'accountnumber', 'dateofbill', 'meternumber', 'presentmeterreading',
                    'fuelclauseadjustment']
            customer_data_dict = dict(zip(keys, customer_data))
            return customer_data_dict
        else:
            return {}  # Return an empty dictionary if customer_id is not found

    def generate_pdf_bill(self, customer_data, filename):
        # Create a PDF document
        pdf_canvas = canvas.Canvas(filename)

        # Set font
        pdf_canvas.setFont("Helvetica", 12)

        # Write bill details to PDF
        pdf_canvas.drawString(100, 800, "----------------------------------------")
        pdf_canvas.drawString(100, 785, "             ELECTRICITY BILL")
        pdf_canvas.drawString(100, 770, "----------------------------------------")
        pdf_canvas.drawString(100, 755, f"Customer ID: {customer_data['CustomerID']}")
        pdf_canvas.drawString(100, 740, f"Name: {customer_data['name']}")
        pdf_canvas.drawString(100, 725, f"Contact Number: {customer_data['address']}")
        pdf_canvas.drawString(100, 710, f"meter_number 1: {customer_data['meter_number 1']}")
        pdf_canvas.drawString(100, 695, f"Meter Number 2: {customer_data['meter_number 2']}")
        pdf_canvas.drawString(100, 680, "----------------------------------------")

        # Get current date for billing period
        now = datetime.now()
        billing_period = now.strftime("%B %Y")
        pdf_canvas.drawString(100, 665, f"Billing Period: {billing_period}")

        pdf_canvas.drawString(100, 650, f"Units Consumed: {customer_data['units_consumed']} kWh")
        pdf_canvas.drawString(100, 635, "Itemized Charges:")
        pdf_canvas.drawString(120, 620, f"   Electricity Charges: ${customer_data['electricity_charge']:.2f}")
        pdf_canvas.drawString(120, 605, f"   Surcharge: ${customer_data['surcharge']:.2f}")
        pdf_canvas.drawString(100, 590, "----------------------------------------")

        total_bill = customer_data['electricity_charge'] + customer_data['surcharge']
        pdf_canvas.drawString(100, 575, f"Total Amount: ${total_bill:.2f}")
        pdf_canvas.drawString(100, 560, "----------------------------------------")

        # Get due date (example: due in 15 days from today)
        due_date = now + timedelta(days=20)
        pdf_canvas.drawString(100, 545, f"Due Date: {due_date.strftime('%B %d, %Y')}")
        pdf_canvas.drawString(100, 530, "----------------------------------------")

        # Save the PDF
        pdf_canvas.save()


    def print_bill(self):

        customer_data = cursor.fetchone()

            # Example filename; replace with a proper filename or path
        filename = 'electric_bill.pdf'

            # Call the generate_pdf_bill method
        self.generate_pdf_bill(customer_data, filename)

            # Add additional logic to open the generated PDF or perform other actions
        print("Bill printed successfully.")


    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = Tk()
    app = ElectricBillSystem(root)
    app.run()

    print_button = Button(root, text="Print Bill", command=app.print_bill)
    print_button.pack()
