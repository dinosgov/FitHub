import datetime
import tkinter as tk
from tkinter import messagebox
import pymysql.cursors

# Create the main window
root = tk.Tk()
root.geometry("500x300")
root.title("Gym Management System")

# Create a label for the customer ID entry field
customer_id_label = tk.Label(root, text="Customer ID:")
customer_id_label.pack()

# Create an entry field for the customer ID
entry = tk.Entry(root)
entry.pack()

# Create a label for the program selection dropdown
program_label = tk.Label(root, text="Program:")
program_label.pack()

# Create a variable to hold the selected program
selected_program = tk.StringVar(root)


# Create a button for updating the customer's presence and program subscription
update_button = tk.Button(root, text="Update", command=lambda: update_presence())
update_button.pack()


def get_programs():
    # Connect to the database
    connection = pymysql.connect(
        host='********',
        user='********',
        password='********',
        db='********',
        charset='********',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            # Get the program names from the database
            sql = "SELECT `program_name` FROM `programs`"
            cursor.execute(sql)
            result = cursor.fetchall()
            # Extract the program names into a list
            programs = [program['program_name'] for program in result]
            return programs
    except pymysql.Error as e:
        messagebox.showerror("Error", f"Error fetching programs: {str(e)}")
    finally:
        connection.close()

# Create a variable to hold the selected program
selected_program = tk.StringVar(root)
# Retrieve the list of programs from the programs table
programs = get_programs()
# Create a dropdown for selecting the program
program_dropdown = tk.OptionMenu(root, selected_program, *programs)
program_dropdown.pack()





def update_presence():
    global selected_program
    customer_id = entry.get().strip()
    if not customer_id:
        messagebox.showerror("Error", "Please enter a customer ID")
        return

    # Connect to the database
    connection = pymysql.connect(
        host='********',
        user='********',
        password='********',
        db='********',
        charset='********',
        cursorclass=pymysql.cursors.DictCursor
    )

    # Check if the customer has already checked in within the last 1 hour
    now = datetime.datetime.now()
    checkin_threshold = now - datetime.timedelta(hours=1)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT `last_checkin` FROM `customers` WHERE `customer_id` = %s"
            cursor.execute(sql, (customer_id,))
            result = cursor.fetchone()
            if result is not None and result['last_checkin'] is not None:
                last_checkin = result['last_checkin']
                if last_checkin > checkin_threshold:
                    messagebox.showerror("Error", "This customer has already checked in within the last 1 hour")
                    return
    except pymysql.Error as e:
        messagebox.showerror("Error", f"Error checking check-in status: {str(e)}")
        return

    # Prompt the user to select a program
    program = selected_program.get()
    if not program:
        messagebox.showerror("Error", "Please select a program")
        return

    # Check if the customer already has a program subscription
    try:
        with connection.cursor() as cursor:
            sql = f"SELECT * FROM `program_subscriptions` WHERE `customer_id` = %s"
            cursor.execute(sql, (customer_id,))
            result = cursor.fetchone()

        if result is None:
            # Customer does not have a program subscription, create a new row
            with connection.cursor() as cursor:
                sql = f"INSERT INTO `program_subscriptions` (`customer_id`, `{program.lower()}`) VALUES (%s, 1)"
                cursor.execute(sql, (customer_id,))
            connection.commit()
        else:
            # Customer already has a program subscription, update the count for the selected program
            with connection.cursor() as cursor:
                sql = f"UPDATE `program_subscriptions` SET `{program.lower()}` = `{program.lower()}` + 1 WHERE `customer_id` = %s"
                cursor.execute(sql, (customer_id,))
            connection.commit()

        # Get the cost of the selected program
        with connection.cursor() as cursor:
            sql = f"SELECT `program_price` FROM `programs` WHERE `program_name` = %s"
            cursor.execute(sql, (program,))
            result = cursor.fetchone()
            if result is None:
                messagebox.showerror("Error", "Invalid program selected")
                return
        cost = result['program_price']
            # Update the customer's last check-in time and add the cost of the selected program to their balance
        with connection.cursor() as cursor:
            sql = "UPDATE `customers` SET `last_checkin` = %s, `balance` = `balance` + %s WHERE `customer_id` = %s"
            cursor.execute(sql, (now, cost, customer_id))
        connection.commit()        
        # Display a success message
        messagebox.showinfo("Success", f"Customer {customer_id} checked in for program {program} with a cost of {cost}")
    except pymysql.Error as e:
        messagebox.showerror("Error", f"Error updating customer: {str(e)}")
    finally:
        connection.close()

root.mainloop()
