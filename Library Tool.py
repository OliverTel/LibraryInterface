import sqlite3
import hashlib
import datetime

# LIBRARY MANAGEMENT UTILITY
# A couple of notes:
# At the time of writing, I have no Tkinter experience. As a result, this
# version operates using a CLI, to ensure that the basics are functional.
# I will begin learning Tkinter and try to create a CLI in a future commit.

# I use SQLite here simply because it's easiest to work with quickly.
# In the real world, I would adapt to whatever version of SQL the client needs.
connection = sqlite3.connect("Library.db")
cursor = connection.cursor()

def register():
    email = input("Email address: ")
    fName = input("First name: ")
    sName = input("Surname: ")
    
    # Set up password confirmation to avoid typos in login details.
    password = "A"
    conPass = "B"
    while password != conPass:
        password = input("Password: ")
        conPass = input("Confirm password: ")
        if (password != conPass):
            print("Passwords do not match. Please try again.")

    # Hash the password for security.
    password = hashlib.sha256(password.encode("utf-8")).hexdigest()

    cursor.execute("INSERT INTO Users (firstName, lastName, email, pass) VALUES ('"+fName+"', '"+sName+"', '"+email+"', '"+password+"');")
    connection.commit()
    
    userID = cursor.execute("SELECT userID FROM Users WHERE email = '"+email+"' AND pass = '"+password+"';").fetchone()[0]
    return userID

def login():
    login = False

    # Allow for several attempts at login.
    while login == False:
        email = input("Email address: ")
        password = input("Password: ")
        # Hash the password to compare it to the saved hash value.
        password = hashlib.sha256(password.encode("utf-8")).hexdigest()

        verify = cursor.execute("SELECT userID FROM Users WHERE email = '"+email+"' AND pass = '"+password+"';").fetchone()
        if verify != None:
            login = True
            print("Login successful.")
            return verify[0]
        else:
            print("Login unsuccessful. Please try again.")

def display(filt):
    valid = True
    if filt == "available":
        books = cursor.execute("SELECT bookName FROM Books WHERE borrowedBy IS NULL").fetchall()
    elif filt == "borrowed":
        books = cursor.execute("SELECT bookName FROM Books WHERE borrowedBy IS NOT NULL").fetchall()
    elif filt == "today":
        books = cursor.execute("SELECT bookName FROM Books WHERE returnDate = '"+datetime.date.today().strftime("%d/%m/%y")+"';").fetchall()
    else:
        print("Invalid filter.")
        valid = False

    if valid == True:
        # Prints five at a time for better readability.
        for i in range(0, len(books), 5):
            for x in range(0, 5):
                if (i + x < len(books)):
                    print("- "+books[i+x][0])
            input("Press enter to view more.")
            
def search(query):
    results = cursor.execute("SELECT bookName, borrowedBy FROM Books WHERE bookName LIKE '%"+query+"%';").fetchall()
    if len(results) > 0:
        for book in results:
            if book[1] != None:
                if book[1] == user:
                    print("- "+book[0]+" - Borrowed by you.")
                else:
                    print("- "+book[0]+" - Borrowed.")
            else:
                print("- "+book[0])

def inspect(title):
    book = cursor.execute("SELECT * FROM Books WHERE bookName = '"+title+"';").fetchone()
    print(book[1])
    print(book[2])
    if book[4] != None:
        borrower = cursor.execute("SELECT firstName, lastName, email FROM Users WHERE userID = "+str(book[4])+";").fetchone()
        print("Borrowed by: "+borrower[0], borrower[1], "("+borrower[2]+")")
        print("Due to be returned on: "+book[5])
def borrow(title):
    borrowed = cursor.execute("SELECT borrowedBy FROM Books WHERE bookName = '"+title+"';").fetchone()
    if borrowed[0] == None:
        returnDate = str((datetime.date.today()+datetime.timedelta(days=7)).strftime("%d/%m/%y"))
        cursor.execute("UPDATE Books SET borrowedBy = "+str(user)+", returnDate = '"+returnDate+"' WHERE bookName = '"+title+"';")
        connection.commit()
        print("Book successfully borrowed. Please return by: "+returnDate)
    else:
        print("Book is already borrowed.")
def bookReturn(title):
    borrower = cursor.execute("SELECT borrowedBy FROM Books WHERE bookName = '"+title+"';").fetchone()
    if borrower[0] == user:
        cursor.execute("UPDATE Books SET borrowedBy = NULL, returnDate = NULL WHERE bookName = '"+title+"';")
        connection.commit()
        print("Book successfully returned.")
    else:
        print("Book is not borrowed by you.")

print("LIBRARY MANAGEMENT UTILITY")

option = ""

while option != "r" and option != "l":
    # Ensure that input is in lowercase to avoid simple errors.
    option = input("Register or log in? (R/L): ").lower()
# Registration.
if option == "r":
    user = register()
elif option == "l":
    user = login()
else:
    print("Invalid command.")

while option != "exit":
    option = input("Please input your command (type 'help' for a list, all commands case sensitive): ")

    if option == "help":
        print('''LIST OF COMMANDS:
search "[string]" - Find a book by keyword in title.
display [available/borrowed/today] - List all books under the specified filter.
inspect "[title]" - Examine the specified book in greater detail, and see who has borrowed it.
borrow "[title of unborrowed book]" - Borrows the specified book.
return "[title of book borrowed by you]" - Returns the specified book.
exit - Log out.
''')
    elif option.startswith("search"):
        if " " in option:
            search(option.split('"')[1])
    elif option.startswith("display"):
        if " " in option:
            display(option.split()[1])
    elif option.startswith("inspect"):
        if " " in option and '"' in option:
            inspect(option.split('"')[1])
    elif option.startswith("borrow"):
        if " " in option and '"' in option:
            borrow(option.split('"')[1])
    elif option.startswith("return"):
        if " " in option and '"' in option:
            bookReturn(option.split('"')[1])
    elif option == "exit":
        continue
    else:
        print("Invalid command.")

connection.close()
