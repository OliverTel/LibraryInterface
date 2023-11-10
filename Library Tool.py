import sqlite3
import hashlib
import datetime
import tkinter as tk
from PIL import ImageTk, Image

# LIBRARY MANAGEMENT UTILITY
# If you would prefer a CLI, see the previous commit.

# I use SQLite here simply because it's easiest to work with quickly.
# In the real world, I would adapt to whatever version of SQL the client needs.
# Given more time, in the real world, I would also add countermeasures for
# SQL injection, because if this program were used in real life, personal
# information could theoretically be at risk.
connection = sqlite3.connect("Library.db")
cursor = connection.cursor()

# A counter to be used for neater, scalable book displays.
bookCount = 0
# A list of books for display.
bookList = []

# Begin logged out.
user = None

def register():
    # Clear the window of buttons.
    regButton.destroy()
    loginButton.destroy()
    
    # Set up strings for the entry fields.
    emailString = tk.StringVar()
    fNameString = tk.StringVar()
    sNameString = tk.StringVar()
    passString = tk.StringVar()
    conPassString = tk.StringVar()

    # Set up and position the widgets in the window.
    emailText = tk.Label(text = "Email:")
    emailText.grid(row=1, column = 0)
    email = tk.Entry(window, textvariable = emailString)
    email.grid(row = 1, column = 1)
    fNameText = tk.Label(text = "First Name:")
    fNameText.grid(row = 2, column = 0)
    fName = tk.Entry(window, textvariable = fNameString)
    fName.grid(row = 2, column = 1)
    sNameText = tk.Label(text = "Surname:")
    sNameText.grid(row = 3, column = 0)
    sName = tk.Entry(window, textvariable = sNameString)
    sName.grid(row = 3, column = 1)
    passText = tk.Label(text = "Password:")
    passText.grid(row = 4, column = 0)
    # Password field is censored for privacy.
    password = tk.Entry(window, textvariable = passString, show = "*")
    password.grid(row = 4, column = 1)
    conPassText = tk.Label(text = "Confirm Password:")
    conPassText.grid(row = 5, column = 0)
    conPass = tk.Entry(window, textvariable = conPassString, show = "*")
    conPass.grid(row = 5, column = 1)
    # Using a lambda to pass variables through the submit function.
    submit = tk.Button(window, text = "Register", command = lambda: submitReg(emailString, fNameString, sNameString, passString, conPassString))
    submit.grid(row = 7, column = 0)

def submitReg(emailString, fNameString, sNameString, passString, conPassString):
    global user
    if passString.get() == conPassString.get():
        # Hash the password for security.
        password = hashlib.sha256(passString.get().encode("utf-8")).hexdigest()

        cursor.execute("INSERT INTO Users (firstName, lastName, email, pass) VALUES ('"+fNameString.get()+"', '"+sNameString.get()+"', '"+emailString.get()+"', '"+password+"');")
        connection.commit()
        
        # Gather the user ID for persistence while logged in.
        userID = cursor.execute("SELECT userID FROM Users WHERE email = '"+emailString.get()+"' AND pass = '"+password+"';").fetchone()[0]
        user = userID

        setupWindow()        

def login():
    # This method is functionally similar to registration.
    regButton.destroy()
    loginButton.destroy()

    emailString = tk.StringVar()
    passString = tk.StringVar()

    emailText = tk.Label(text = "Email:")
    emailText.grid(row=1, column = 0)
    email = tk.Entry(window, textvariable = emailString)
    email.grid(row = 1, column = 1)
    passText = tk.Label(text = "Password:")
    passText.grid(row = 2, column = 0)
    password = tk.Entry(window, textvariable = passString, show = "*")
    password.grid(row = 2, column = 1)
    submit = tk.Button(window, text = "Log In", command = lambda: submitLogin(emailString, passString))
    submit.grid(row = 4, column = 0)

def submitLogin(emailString, passString):
    global user
    password = hashlib.sha256(passString.get().encode("utf-8")).hexdigest()

    # Check the database for matching credentials.
    # For now, issues may occur if identical accounts are made.
    # In the future, add a method to prevent the same email being used again.
    verify = cursor.execute("SELECT userID FROM Users WHERE email = '"+emailString.get()+"' AND pass = '"+password+"';").fetchone()
    if verify != None:
        user = verify[0]
        
        setupWindow()
        
def setupWindow():
    # Setting up global variables so that functions can modify text.
    global title, desc, borrower, returnBy, imageDisplay, bookButtons, borrowButton, returnButton
    
    # Clear the entire window of widgets, for a blank slate.
    for child in window.winfo_children():
        child.destroy()

    # The search bar's string variable.
    searchString = tk.StringVar()

    # Add all of the necessary widgets.
    windowName = tk.Label(text = "LIBRARY MANAGEMENT UTILITY")
    windowName.grid(row = 0, column = 0, columnspan = 5, sticky = "nsew")
    searchBar = tk.Entry(window, textvariable = searchString)
    searchBar.grid(row = 1, column = 0, columnspan = 2)
    searchButton = tk.Button(window, text = "Search", command = lambda: search(searchString.get()))
    searchButton.grid(row = 1, column = 2)
    availableButton = tk.Button(window, text = "Available", command = lambda: display("available"))
    availableButton.grid(row = 2, column = 0, sticky = "nsew")
    borrowedButton = tk.Button(window, text = "Borrowed", command = lambda: display("borrowed"))
    borrowedButton.grid(row = 2, column = 1, sticky = "nsew")
    todayButton = tk.Button(window, text = "Returning Today", command = lambda: display("today"))
    todayButton.grid(row = 2, column = 2, sticky = "nsew")
    upButton = tk.Button(window, text = "Up", command = scrollUp)
    upButton.grid(row = 3, column = 2, sticky = "nsew")
    downButton = tk.Button(window, text = "Down", command = scrollDown)
    downButton.grid(row = 4, column = 2, sticky = "nsew")
    title = tk.Label(text = "Select a book.")
    title.grid(row = 3, column = 3, columnspan = 2, sticky = "nsew")
    desc = tk.Label(text = "The description will appear here.")
    desc.grid(row = 4, column = 3, columnspan = 2, sticky = "nsew")
    borrower = tk.Label()
    borrower.grid(row = 5, column = 3, columnspan = 2, sticky = "nsew")
    returnBy = tk.Label()
    returnBy.grid(row = 6, column = 3, columnspan = 2, sticky = "nsew")
    borrowButton = tk.Button(text = "Borrow")
    returnButton = tk.Button(text = "Return")

    bookButtons = [tk.Button(window, text = "") for i in range(5)]
    
    bookImage = ImageTk.PhotoImage(Image.open("Images/Missing.png"))
    # Requires both the below lines to display an image.
    imageDisplay = tk.Label(image = bookImage)
    imageDisplay.image = bookImage
    imageDisplay.grid(row = 1, column = 3, rowspan = 2, columnspan = 2, sticky = "nsew")

def scrollUp():
    global bookCount, bookList, bookButtons

    # To avoid any weirdness with pressing the buttons when nothing's displayed.
    if len(bookList) > 0:
        if bookCount < 5:
            bookCount = 0
        else:
            bookCount -= 5

        # Essentially iterate through the buttons, to change them all at once.
        for i in range(0, len(bookButtons)):
            if (bookCount + i) < len(bookList):
                # Set the button's text to the correct book title.
                bookButtons[i].config(text = bookList[bookCount + i][0])
                # Display the button.
                bookButtons[i].grid(row = (3 + i), column = 0, columnspan = 2)
                # Configure the button to lead to the correct book information.
                # I use a separate variable, "index", to store the value of "i" once it leaves scope.
                bookButtons[i].config(command = lambda index = i: inspect(bookList[bookCount + index][0]))
            else:
                # Remove the button from display as it contains no book.
                bookButtons[i].grid_remove()
    else:
        # Display no options.
        for button in bookButtons:
            button.grid_remove()
        
def scrollDown():
    # Functionally the same as scrollUp, but essentially inverted.
    global bookCount, bookList, bookButtons
    
    if len(bookList) > 0:
        if bookCount >= (len(bookList) - 5):
            pass
        else:
            bookCount = len(bookList) - 1

        for i in range(0, len(bookButtons)):
            if (bookCount + i) < len(bookList):
                bookButtons[i].config(text = bookList[bookCount + i][0])
                bookButtons[i].grid(row = (3 + i), column = 0, columnspan = 2)
                bookButtons[i].config(command = lambda index = i: inspect(bookList[bookCount + index][0]))
            else:
                bookButtons[i].grid_remove()
    else:
        for button in bookButtons:
            button.grid_remove()

def display(filt):
    global bookCount, bookList
    
    if filt == "available":
        bookList = cursor.execute("SELECT bookName FROM Books WHERE borrowedBy IS NULL").fetchall()
    elif filt == "borrowed":
        bookList = cursor.execute("SELECT bookName FROM Books WHERE borrowedBy IS NOT NULL").fetchall()
    elif filt == "today":
        bookList = cursor.execute("SELECT bookName FROM Books WHERE returnDate = '"+datetime.date.today().strftime("%d/%m/%y")+"';").fetchall()

    # Reset the book display to show the filtered results.
    bookCount = 0
    scrollUp()
            
def search(query):
    global bookCount, bookList
    
    bookList = cursor.execute("SELECT bookName FROM Books WHERE bookName LIKE '%"+query+"%';").fetchall()

    bookCount = 0
    scrollUp()

def inspect(query):
    global user, title, desc, imageDisplay, borrower, returnBy, borrowButton, returnButton
    book = cursor.execute("SELECT * FROM Books WHERE bookName = '"+query+"';").fetchone()
    title.config(text = book[1])
    desc.config(text = book[2])
    # If there is an image, display it.
    if book[3] != None:
        # For testing, there are only two books with images, and they share the same one.
        image = ImageTk.PhotoImage(Image.open("Images/"+book[3]))
        imageDisplay.config(image = image)
        imageDisplay.image = image
    else:
        # Display an imagine signifying a missing image.
        image = ImageTk.PhotoImage(Image.open("Images/Missing.png"))
        imageDisplay.config(image = image)
        imageDisplay.image = image

    # Check if the book is already borrowed.
    if book[4] != None:
        # Configure the borrower info to display correctly.
        borrowedBy = cursor.execute("SELECT firstName, lastName, email FROM Users WHERE userID = "+str(book[4])+";").fetchone()
        borrower.config(text = (borrowedBy[0], borrowedBy[1], "("+borrowedBy[2]+")"))
        borrower.grid(row = 5, column = 3, columnspan = 2, sticky = "nsew")
        returnBy.config(text = "Due to be returned on:"+book[5])
        returnBy.grid(row = 6, column = 3, columnspan = 2, sticky = "nsew")

        if book[4] == user:
            # Show and set up the return button.
            borrowButton.grid_remove()
            returnButton.grid(row = 7, column = 3, columnspan = 2)
            returnButton.config(command = lambda: bookReturn(book[1]))
        else:
            # Otherwise, hide both buttons.
            returnButton.grid_remove()
            borrowButton.grid_remove()
            
    else:
        # Clear any previous borrower info.
        borrower.grid_remove()
        returnBy.grid_remove()
        # Show and set up the borrow button.
        returnButton.grid_remove()
        borrowButton.grid(row = 7, column = 3, columnspan = 2)
        borrowButton.config(command = lambda: borrow(book[1]))

def borrow(title):
    global bookCount
    
    borrowed = cursor.execute("SELECT borrowedBy FROM Books WHERE bookName = '"+title+"';").fetchone()
    returnDate = str((datetime.date.today()+datetime.timedelta(days=7)).strftime("%d/%m/%y"))
    cursor.execute("UPDATE Books SET borrowedBy = "+str(user)+", returnDate = '"+returnDate+"' WHERE bookName = '"+title+"';")
    connection.commit()

    bookCount = 0
    scrollUp()
    inspect(title)

def bookReturn(title):
    global bookCount
    
    borrower = cursor.execute("SELECT borrowedBy FROM Books WHERE bookName = '"+title+"';").fetchone()
    cursor.execute("UPDATE Books SET borrowedBy = NULL, returnDate = NULL WHERE bookName = '"+title+"';")
    connection.commit()

    bookCount = 0
    scrollUp()
    inspect(title)

# Create the initial window.
window = tk.Tk()

# Set up the window's initial layout.
windowName = tk.Label(text = "LIBRARY MANAGEMENT UTILITY")
windowName.grid(row = 0, column = 0, sticky = "nsew")
regButton = tk.Button(window, text = "Register", command = register)
regButton.grid(row = 1, column = 0, sticky = "nsew")
loginButton = tk.Button(window, text = "Log In", command = login)
loginButton.grid(row = 2, column = 0, sticky = "nsew")

window.mainloop()

connection.close()
