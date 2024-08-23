import os
from tkinter import *
from tkinter import messagebox, simpledialog
import sqlite3
from sqlite3 import Error
import sys
from cryptography.fernet import Fernet, InvalidToken

# Store Master password
master_password = sys.argv[1]

# Path to the key file
KEY_FILE = "secret.key"

# Function to load or generate the encryption key
def load_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as key_file:
            return key_file.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        return key

# Load the encryption key
key = load_key()
cipher = Fernet(key)

# Function to connect to the SQL Database
def sql_connection():
    try:
        con = sqlite3.connect('passwordManager.db')
        return con
    except Error:
        print(Error)

# Function to create table
def sql_table(con):
    cursorObj = con.cursor()
    cursorObj.execute(
        "CREATE TABLE IF NOT EXISTS passwords( website text, username text, pass text)")
    con.commit()

# Call functions to connect to database and create table
con = sql_connection()
sql_table(con)

# Encrypt function
def encrypt_password(password):
    return cipher.encrypt(password.encode()).decode()

# Decrypt function with exception handling
def decrypt_password(encrypted_password):
    try:
        return cipher.decrypt(encrypted_password.encode()).decode()
    except InvalidToken:
        return encrypted_password

# Create submit function for database
def submit(con):
    cursor = con.cursor()
    # Insert Into Table
    if website.get() != "" and username.get() != "" and password.get() != "":
        encrypted_password = encrypt_password(password.get())  # Encrypt the password
        cursor.execute("INSERT INTO passwords VALUES (:website, :username, :password)",
                       {
                           'website': website.get(),
                           'username': username.get(),
                           'password': encrypted_password  # Store the encrypted password
                       }
                       )
        con.commit()
        # Message box
        messagebox.showinfo("Info", "Record Added in Database!")

        # After data entry clear the text boxes
        website.delete(0, END)
        username.delete(0, END)
        password.delete(0, END)

    else:
        messagebox.showinfo("Alert", "Please fill all details!")

# Create Query Function
def query(con):
    password = simpledialog.askstring("Password", "Enter Master Password")
    print(f"Entered password: {password}")  # Debugging: Print entered password
    print(f"Master password: {master_password}")  # Debugging: Print stored master password

    if password == master_password:
        query_btn.configure(text="Hide Records", command=hide)
        cursor = con.cursor()
        cursor.execute("SELECT *, oid FROM passwords")
        records = cursor.fetchall()

        p_records = 'ID'.ljust(10) + 'Website'.ljust(40) + \
            'Username'.ljust(70)+'Password'.ljust(100)+'\n'

        for record in records:
            decrypted_password = decrypt_password(record[2])  # Decrypt the stored password
            single_record = ""
            single_record += (str(record[3]).ljust(10) +
                              str(record[0]).ljust(40)+str(record[1]).ljust(70)+str(decrypted_password).ljust(100))
            single_record += '\n'
            p_records += single_record
        query_label['text'] = p_records
        con.commit()
        p_records = ""

    else:
        messagebox.showinfo("Failed!", "Authentication failed!")

# Create Delete Function
def delete(con):
    password = simpledialog.askstring("Password", "Enter Master Password")
    print(f"Entered password: {password}")  # Debugging: Print entered password
    print(f"Master password: {master_password}")  # Debugging: Print stored master password

    if password == master_password:
        delete_id = simpledialog.askinteger("Delete Record", "Enter ID of record to delete")
        if delete_id:
            cursor = con.cursor()
            cursor.execute("DELETE FROM passwords WHERE oid = ?", (delete_id,))
            con.commit()
            messagebox.showinfo("Info", f"Record with ID {delete_id} deleted!")
            query(con)  # Update displayed records
    else:
        messagebox.showinfo("Failed!", "Authentication failed!")

# Create Function to Hide Records
def hide():
    query_label['text'] = ""
    query_btn.configure(text="Show Records", command=lambda: query(con))

root = Tk()
root.title("Password | Manager")
root.geometry("500x400")
root.minsize(600, 400)
root.maxsize(600, 400)

frame = Frame(root, bg="#774A9F", bd=2)
frame.place(relx=0.50, rely=0.50, relwidth=0.98, relheight=0.45, anchor="n")

# Create Text Boxes
website = Entry(root, width=30)
website.grid(row=1, column=1, padx=20, pady=5)
username = Entry(root, width=30)
username.grid(row=2, column=1, padx=20, pady=5)
password = Entry(root, width=30)
password.grid(row=3, column=1, padx=20, pady=5)

# Create Text Box Labels
website_label = Label(root, text="Website:")
website_label.grid(row=1, column=0)
username_label = Label(root, text=" Username:")
username_label.grid(row=2, column=0)
password_label = Label(root, text="Password:")
password_label.grid(row=3, column=0)

# Create Buttons
submit_btn = Button(root, text="Add Password", command=lambda: submit(con))
submit_btn.grid(row=5, column=1, pady=5, padx=15, ipadx=35)
query_btn = Button(root, text="Show All", command=lambda: query(con))
query_btn.grid(row=6, column=1, pady=5, padx=5, ipadx=35)
delete_btn = Button(root, text="Delete Record", command=lambda: delete(con))
delete_btn.grid(row=7, column=1, pady=5, padx=5, ipadx=25)

# Create a Label to show stored passwords
global query_label
query_label = Label(frame, anchor="nw", justify="left")
query_label.place(relwidth=1, relheight=1)

def main():
    root.mainloop()

if __name__ == '__main__':
    main()
