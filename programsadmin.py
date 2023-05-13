import tkinter as tk
import tkinter.ttk as ttk
import pymysql.cursors
from tkinter import messagebox

# Create the main window
root = tk.Tk()
root.geometry("900x700")
root.title("Programs Table")

# Create a label for the programs table
programs_label = tk.Label(root, text="Programs Table", font=("Arial", 16))
programs_label.pack()

# Create a treeview to display the programs table
tree = ttk.Treeview(root)
tree.pack()

# Define the columns for the treeview
tree.column("#0", width=0, stretch=tk.NO)
tree["columns"] = ("program_id", "program_name", "program_price")

# Define column headings
tree.heading("program_id", text="ID")
tree.heading("program_name", text="Name")
tree.heading("program_price", text="Price")
# Create a style object

style = ttk.Style()

# Set the style for the buttons
style.configure('Custom.TButton', 
                background='#7F24DA',
                foreground='#7F24DA',
                font=('Arial', 9, 'bold'),
                borderwidth=0,
                width=15,
                padding=10)

# Connect to the database
connection = pymysql.connect(
    host='********',
    user='********',
    password='********',
    db='********',
    charset='********',
    cursorclass=pymysql.cursors.DictCursor
)

# Retrieve the programs from the database and populate the treeview
try:
    with connection.cursor() as cursor:
        sql = "SELECT * FROM `programs`"
        cursor.execute(sql)
        result = cursor.fetchall()
        for row in result:
            tree.insert("", "end", values=(row['program_id'], row['program_name'], row['program_price']))
except pymysql.Error as e:
    print(f"Error retrieving programs: {str(e)}")

# Create labels and entry fields for editing/adding rows
edit_label = tk.Label(root, text="Edit Selected Row", font=("Arial", 12))
edit_label.place(x=200, y=300)

program_name_label = tk.Label(root, text="Name:")
program_name_label.place(x=50, y=350)
program_name_entry = tk.Entry(root)
program_name_entry.place(x=100, y=350)

program_price_label = tk.Label(root, text="Price:")
program_price_label.place(x=50, y=380)
program_price_entry = tk.Entry(root)
program_price_entry.place(x=100, y=380)



# Create a button for updating the selected row
def update_row():
    # Get the selected row
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a row to edit")
        return
    row_id = tree.item(selected_item)["values"][0]
    
    # Get the new values from the entry fields
    program_name = program_name_entry.get().strip()
    program_price = program_price_entry.get().strip()
    
    # Update the row in the database
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE `programs` SET "
            if program_name:
                sql += "`program_name`=%s, "
            if program_price:
                sql += "`program_price`=%s, "
            # Remove the last comma and space from the query
            sql = sql[:-2] + " WHERE `program_id`=%s"
            
            # Execute the query with the appropriate values
            if program_name and program_price:
                cursor.execute(sql, (program_name, program_price, row_id))
            elif program_name:
                cursor.execute(sql, (program_name, row_id))
            elif program_price:
                cursor.execute(sql, (program_price, row_id))
            
            connection.commit()
            
            # Update the row in the treeview
            new_values = [row_id]
            if program_name:
                new_values.append(program_name)
            else:
                new_values.append(tree.item(selected_item)["values"][1])
            if program_price:
                new_values.append(program_price)
            else:
                new_values.append(tree.item(selected_item)["values"][2])
            tree.item(selected_item, values=tuple(new_values))
            
            # Clear the entry fields
            program_name_entry.delete(0, tk.END)
            program_price_entry.delete(0, tk.END)
            
            messagebox.showinfo("Success", "Row updated successfully")
    except pymysql.Error as e:
        print(f"Error updating row: {str(e)}")
        messagebox.showerror("Error", "An error occurred while updating the row")


def add_row():
    # Get the new values from the entry fields
    program_name = program_name_entry.get().strip()
    program_price = program_price_entry.get().strip()

    # Get the set of all program IDs from the database
    with connection.cursor() as cursor:
        cursor.execute("SELECT program_id FROM programs")
        ids = set(row['program_id'] for row in cursor.fetchall())

    # Find the first free program ID
    next_id = 1
    while next_id in ids:
        next_id += 1

    # Insert the new row into the database
    try:
        with connection.cursor() as cursor:
            # Insert the new row into the 'programs' table
            sql = "INSERT INTO `programs` (`program_id`, `program_name`, `program_price`) VALUES (%s, %s, %s)"
            cursor.execute(sql, (next_id, program_name, program_price))
            connection.commit()

            # Create a new column in the 'program_subscriptions' table with the same name as the program name
            column_name = program_name.lower().replace(' ', '_')
            alter_table_sql = f"ALTER TABLE program_subscriptions ADD COLUMN {column_name} INT DEFAULT 0"
            cursor.execute(alter_table_sql)
            connection.commit()

            # Insert the new row into the treeview
            tree.insert("", "end", text=next_id, values=(next_id, program_name, program_price))

            # Clear the entry fields
            program_name_entry.delete(0, tk.END)
            program_price_entry.delete(0, tk.END)

            tk.messagebox.showinfo("Success", "Row added successfully")
    except pymysql.Error as e:
        print(f"Error adding row: {str(e)}")
        tk.messagebox.showerror("Error", "An error occurred while adding the row")



def delete_row():
    # Get the selected row
    selected_item = tree.selection()
    if not selected_item:
        tk.messagebox.showerror("Error", "Please select a row to delete")
        return
    row_id = tree.item(selected_item)["values"][0]
    program_name = tree.item(selected_item)["values"][1]
    
    # Delete the row from the database
    try:
        with connection.cursor() as cursor:
            # Delete the row from programs table
            sql = "DELETE FROM `programs` WHERE `program_id`=%s"
            cursor.execute(sql, (row_id,))
            
            # Delete the column from program_subscriptions table
            sql = f"ALTER TABLE program_subscriptions DROP COLUMN `{program_name}`"
            cursor.execute(sql)
            
            connection.commit()
            
            # Delete the row from the treeview
            tree.delete(selected_item)
            
            tk.messagebox.showinfo("Success", "Row deleted successfully")
    except pymysql.Error as e:
        print(f"Error deleting row: {str(e)}")
        tk.messagebox.showerror("Error", "An error occurred while deleting the row")




# Create the buttons with images
update_button = ttk.Button(root, text="Update Row",  command=update_row, style='Custom.TButton')
update_button.place(x=100, y=430)

add_button = ttk.Button(root, text="Add Row", command=add_row, style='Custom.TButton')
add_button.place(x=300, y=430)

delete_button = ttk.Button(root, text="Delete Row", command=delete_row, style='Custom.TButton')
delete_button.place(x=500, y=430)



root.mainloop()





