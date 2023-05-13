import tkinter as tk
from tkinter import ttk
import uuid
import pymysql.cursors
from tkinter import messagebox
#from PIL import Image, ImageTk
import datetime
import pymysql
import docx




def extract_to_word(event=None):
    # Get the current date and time
    now = datetime.datetime.now()
    # Open a new Word document
    doc = docx.Document()
    # Connect to your database
    with pymysql.connect(
        host='********',
        user='********',
        password='********',
        db='********',
        charset='********',
        cursorclass=pymysql.cursors.DictCursor
    ) as connection:
        with connection.cursor() as cursor:
            # Execute a SELECT query to get all the data from your table
            cursor.execute("SELECT * FROM `customers`")
            data = cursor.fetchall()
            # Create a table in the Word document with column headers
            table = doc.add_table(rows=1, cols=len(data[0]))
            hdr_cells = table.rows[0].cells
            for i, key in enumerate(data[0]):
                hdr_cells[i].text = key
            # Write the data to the table
            for row in data:
                row_cells = table.add_row().cells
                for i, value in enumerate(row.values()):
                    row_cells[i].text = str(value)
    # Save the Word document with the current date and time as its name
    doc.save(f"{now.strftime('%Y-%m-%d_%H-%M')}.docx")#-%S




class Gym(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Gym Application")
        #self.master.geometry('800x600')
        self.pack()
        self.create_widgets()
        self.style = ttk.Style()
        self.style.configure('Red.TButton', foreground='red')
   
#------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def create_widgets(self):
        # Πίνακας
        self.table = tk.ttk.Treeview(self)
        self.table.column("#0", width=0, stretch=tk.NO)
        self.table['columns'] = ('customer_id', 'name', 'surname', 'date_of_birth', 'subscription', 'balance') #'presence'
        self.table.heading("customer_id", text="ID")
        self.table.heading("name", text="First Name")
        self.table.heading("surname", text="Last Name")
        self.table.heading("date_of_birth", text="Date of Birth")
        self.table.heading("subscription", text="Subscription")
        self.table.heading("balance", text="Balance")
        #self.table.heading("presence", text="Presence")
        self.table.pack(side="left") 
        # Πλαίσιο εισαγωγής
        self.insert_frame = tk.Frame(self)
        self.insert_frame.pack(side="top") 
        #tk.Label(self.insert_frame, text="id").grid(row=0, column=0)
        tk.Label(self.insert_frame, text="First Name").grid(row=0, column=0)
        tk.Label(self.insert_frame, text="Last Name").grid(row=1, column=0)
        tk.Label(self.insert_frame, text="Date of Birth").grid(row=2, column=0)
        tk.Label(self.insert_frame, text="Subscription").grid(row=3, column=0)
        tk.Label(self.insert_frame, text="Balance").grid(row=4, column=0)
        #tk.Label(self.insert_frame, text="Presence").grid(row=5, column=0) 
        #self.id_entry = tk.Entry(self.insert_frame)
        self.name_entry = tk.Entry(self.insert_frame)
        self.surname_entry = tk.Entry(self.insert_frame)
        self.date_of_birth_entry= tk.Entry(self.insert_frame)
        self.subscription_entry = tk.Entry(self.insert_frame)
        self.balance_entry = tk.Entry(self.insert_frame)
        #self.presence_entry = tk.Entry(self.insert_frame)
        #self.id_entry.grid(row=0, column=1)
        self.name_entry.grid(row=0, column=1)
        self.surname_entry.grid(row=1, column=1)
        self.date_of_birth_entry.grid(row=2, column=1)
        self.subscription_entry.grid(row=3, column=1)
        self.balance_entry.grid(row=4, column=1)
        #self.presence_entry.grid(row=5, column=1) 
        # Πλήκτρα εισαγωγής, ενημέρωσης, διαγραφής και αναζήτησης
        self.insert_button = tk.Button(self.insert_frame, text="Insert", command=self.insert_data, bg="green")
        self.update_button = tk.Button(self.insert_frame, text="Update", command=self.update_data)
        self.delete_button = ttk.Button(self.insert_frame, text="Delete", command=lambda: self.delete_customer(), style='Red.TButton')
        self.extract_to_word = ttk.Button(self.insert_frame, text="Extract", command=extract_to_word, style='Red.TButton') 
        #self.search_button = tk.Button(self.insert_frame, text="Search", command=self.search_data)
        self.insert_button.grid(row=7, column=0)
        self.update_button.grid(row=7, column=1)
        self.delete_button.grid(row=7, column=2)
        self.extract_to_word.grid(row=7, column=3)
       # self.search_button.grid(row=7, column=3)
        self.customers = []  # Δημιουργία της λίστας self.customers
        self.show_customers()  # Φόρτωση των πελατών από το αρχείο CSV
#        



    def insert_data(self):
        # Get customer details from user input
        name = self.name_entry.get()
        surname = self.surname_entry.get()
        date_of_birth = self.date_of_birth_entry.get()
        subscription = self.subscription_entry.get()
        balance = self.balance_entry.get()

        # Check if customer already exists in database
        with pymysql.connect(
                host='********',
                user='********',
                password='********',
                db='********',
                charset='********',
                cursorclass=pymysql.cursors.DictCursor
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM customers WHERE name=%s AND surname=%s", (name, surname))
                result = cursor.fetchone()
                if result:
                    # Customer already exists, show error message
                    tk.messagebox.showerror("Error", "Customer already exists in database.")
                    return

        # Insert new customer into database
        with pymysql.connect(
                host='********',
                user='********',
                password='********',
                db='********',
                charset='********',
                cursorclass=pymysql.cursors.DictCursor
        ) as connection:
            with connection.cursor() as cursor:
                # Generate a new customer id
                customer_id = self.get_available_customer_id()

                # Insert the new customer into the database
                cursor.execute("INSERT INTO customers (customer_id, name, surname, date_of_birth, subscription, balance) VALUES (%s, %s, %s, %s, %s, %s)",
                               (customer_id, name, surname, date_of_birth, subscription, balance))
                connection.commit()

                # Insert a new row in program_subscriptions with the same customer_id
                cursor.execute("INSERT INTO program_subscriptions (customer_id) VALUES (%s)", (customer_id,))
                connection.commit()

                # Show success message
                tk.messagebox.showinfo("Success", "Customer added successfully.")

                # Clear the input fields
                self.name_entry.delete(0, tk.END)
                self.surname_entry.delete(0, tk.END)
                self.date_of_birth_entry.delete(0, tk.END)
                self.subscription_entry.delete(0, tk.END)
                self.balance_entry.delete(0, tk.END)

                # Reload the customer list
                self.show_customers()


    

#-------------------------------------------------------------------------------------------------------------------------------------------------------
    def update_data(self):
            # Get the selected row from the table
        selected_row = self.table.selection()
        if not selected_row:
            tk.messagebox.showerror("Error", "Please select a row to update")
            return

        # Get the ID of the selected customer
        customer_id = self.table.item(selected_row)['values'][0]

        # Get the new data entered by the user from the text fields
        name = self.name_entry.get().strip()
        surname = self.surname_entry.get().strip()
        date_of_birth = self.date_of_birth_entry.get().strip()
        subscription = self.subscription_entry.get().strip()
        balance = self.balance_entry.get().strip()
        #presence = self.presence_entry.get().strip()

        # Update the database
        with pymysql.connect(
                host='********',
                user='********',
                password='********',
                db='********',
                charset='********',
                cursorclass=pymysql.cursors.DictCursor
        ) as connection:
            with connection.cursor() as cursor:
                # Find the customer we want to update
                cursor.execute("SELECT * FROM customers WHERE customer_id=%s", (customer_id,))
                customer = cursor.fetchone()

                # Check if the customer was found
                if not customer:
                    tk.messagebox.showerror("Error", f"No customer found with id {customer_id}")
                    return

                # Update the customer's data
                if name:
                    cursor.execute("UPDATE customers SET name=%s WHERE customer_id=%s", (name, customer_id))
                    connection.commit()
                if surname:
                    cursor.execute("UPDATE customers SET surname=%s WHERE customer_id=%s", (surname, customer_id))
                    connection.commit()
                if date_of_birth:
                    cursor.execute("UPDATE customers SET date_of_birth=%s WHERE customer_id=%s", (date_of_birth, customer_id))
                    connection.commit()
                if subscription:
                    cursor.execute("UPDATE customers SET subscription=%s WHERE customer_id=%s", (subscription, customer_id))
                    connection.commit()
                if balance:
                    cursor.execute("UPDATE customers SET balance=%s WHERE customer_id=%s", (balance, customer_id))
                    connection.commit()
                #if presence:
                #    cursor.execute("UPDATE customers SET presence=%s WHERE customer_id=%s", (presence, customer_id))
                #    connection.commit()

                # Update the table with the new customer data
                self.name_entry.delete(0, tk.END)
                self.surname_entry.delete(0, tk.END)
                self.date_of_birth_entry.delete(0, tk.END)
                self.subscription_entry.delete(0, tk.END)
                self.balance_entry.delete(0, tk.END)
                #self.presence_entry.delete(0, tk.END)
                self.show_customers()
                tk.messagebox.showinfo("Success", "Customer data updated successfully")


#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def delete_customer(self):
        # Get the ID of the selected customer
        selected_row = self.table.selection()
        if not selected_row:
            messagebox.showerror("Error", "Please select a customer to delete")
            return
        customer_id = self.table.item(selected_row)['values'][0]
    
        # Connect to the database
        with pymysql.connect(
                host='********',
                user='********',
                password='********',
                db='********',
                charset='********',
                cursorclass=pymysql.cursors.DictCursor
        ) as connection:
            with connection.cursor() as cursor:
                # Find the customer we want to delete
                cursor.execute("SELECT * FROM customers WHERE customer_id=%s", (customer_id,))
                customer = cursor.fetchone()
    
                # Check if the customer was found
                if not customer:
                    messagebox.showerror("Error", f"No customer found with id {customer_id}")
                    return
    
                # Add the deleted customer ID to the deleted_ids table
                cursor.execute("INSERT INTO deleted_ids (id) VALUES (%s)", (customer_id,))
                connection.commit()
    
                # Delete the customer from the customers table
                cursor.execute("DELETE FROM customers WHERE customer_id=%s", (customer_id,))
                connection.commit()
    
                # Delete the program subscription for the customer from the program_subscriptions table
                cursor.execute("DELETE FROM program_subscriptions WHERE customer_id=%s", (customer_id,))
                connection.commit()
    
        # Remove the selected row from the table
        self.table.delete(selected_row)
    
        messagebox.showinfo("Success", f"Customer with ID {customer_id} deleted successfully")
        self.show_customers()  # Reload the customers from the database
    


#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def show_customers(self):
        # Καθαρισμός του πίνακα
        for i in self.table.get_children():
            self.table.delete(i)

        # Σύνδεση με τη βάση δεδομένων και εκτέλεση ερωτήματος
        connection = pymysql.connect(host='********',
                                     user='********',
                                     password='********',
                                     db='********')
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `customers` ORDER BY surname ASC"
            cursor.execute(sql)
            result = cursor.fetchall()

            # Προσθήκη καθε μιας εγγραφής στον πίνακα
            for row in result:
                self.table.insert("", "end", text=row[0], values=row[0:])

        # Κλείσιμο της σύνδεσης
        connection.close()


#--------------------------------------------------------------------------------------------------------------------------------------------------------------

    def get_available_customer_id(self):
        with pymysql.connect(
                host='********',
                user='********',
                password='********',
                db='********',
                charset='********',
                cursorclass=pymysql.cursors.DictCursor
        ) as connection:
            with connection.cursor() as cursor:
                # Check if there are any deleted ids available
                cursor.execute("SELECT id FROM deleted_ids")
                result = cursor.fetchone()
                if result:
                    # If there are deleted ids, use the smallest one
                    new_id = result['id']
                    cursor.execute("DELETE FROM deleted_ids WHERE id = %s", (new_id,))
                    connection.commit()
                else:
                    # If there are no deleted ids, generate a new one
                    cursor.execute("SELECT MAX(customer_id) FROM customers")
                    result = cursor.fetchone()
                    max_id = result["MAX(customer_id)"] or 0
                    new_id = max_id + 1

                return new_id



#---------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = Gym(master=root)
    app.mainloop()


