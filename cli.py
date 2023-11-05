import db_basic_functions

def register():
    print("Welcome to the CKF Library System!")
    fname = input("Please Enter Your First Name: ")
    lname = input("Please Enter Your Last Name: ")
    email = input("Please Enter Your Email: ")
    uname = input("Please Enter a Username: ")
    password = input("Please Enter a Password: ")
    # Put in the register function here #
    return login()

def login(uname="", password=""):
    if(uname == "" and password == ""):
        uname = input("Enter Username: ")
        password = input("Enter Password: ")
    # Put in Login function here #
    return -1

def help():
    print("""CKF Main Menu Commands: \n
                \tSearch: Searching for New Books\n
                \tRead: Reading Books\n
                \tCollection: Create/Manage Collections of Books\n
                \tFollow: Follow Other Users\n
                \tHelp: Bring Up This Menu\n
                \tQuit: Quit Out of the System""")

def search():
    print("Search for Books:")
    command = input("Enter Command (or help):").lower()
    while(True):
        if(command == "help"):
            print("""Search Commands:\n
                        \tTitle: Search By Title\n
                        \tDate: Search by Release Date\n
                        \tAuthor: Search by Author\n
                        \tEditor: Search by Editor\n
                        \tPublisher: Search by Publisher\n
                        \tGenre: Search by Genre""")
        elif(command == "title"):
            title = input("Input a Title:")
            print("Here's What I Found:")
            print(db_basic_functions.search_books_by_title(title))
        elif(command == "date"):
            date = input("Input a Date:")
            print("Here's What I Found:")
            print(db_basic_functions.search_books_by_release_date_after(date))
        elif(command == "author"):
            author = input("Input the Name:")
            print("Here's What I Found:")
            print(db_basic_functions.search_books_by_author(author))
        elif(command == "editor"):
            editor = input("Input the Name:")
            print("Here's What I Found:")
            print(db_basic_functions.search_books_by_editor(editor))
        elif(command == "publisher"):
            publisher = input("Input the Name:")
            print("Here's What I Found:")
            print(db_basic_functions.search_books_by_publisher(publisher))
        elif(command == "genre"):
            genre = input("Input the Genre (or Help for a list):")
            if(genre == help):
                print("""Here's a list of possible genres:\n
                        Sci-Fi, Mystery, Romance, Horror, Adventure, Fantasy, Classics, NonFiction, History, Thriller
                        YA, Science, Biography, Self-Help, Crime, Comedy, Drama, Music, Travel, Cooking""")
                genre = input("Input the Genre:")
            print("Here's What I Found:")
            print(db_basic_functions.search_books_by_genre(genre))
        command = input("Enter Command (Search):").lower()

def read(userID):
    while(True):
        title = input("Enter the Title of the Book You Read: ")
        if(title == "quit"):
            return
        book = db_basic_functions.search_books_by_title(title)[0]
        if(book != None):
            bookID = book[0]
            break
        else:
            print("We Could not Find that book, Please Try again (or quit)")
    start = input("What Page did you start on?: ")
    end = input("What Page did you end on?: ")
    db_basic_functions.read_book(bookID, userID, start, end)

def collection(userID):
    print("Manage Collections:")
    command = input("Enter Command (or help):").lower()
    while(True):
        if(command == "help"):
            print("""Collections Commands:\n
                        \tView: View Your Collections\n
                        \tCreate: Create New Collection\n
                        \tDelete: Delete Collection\n
                        \tAdd: Add Book to Collection\n
                        \tRemove: Remove Book from Collection\n""")
        elif(command == "view"):
            print("Here is all of your Collections:")
            print(db_basic_functions.get_collections(userID))
        elif(command == "create"):
            cname = input("Enter Collection Name: ")
            # put create collection here #
        elif(command == "delete"):
            cname = input("Enter Collection Name: ")
            # put delete collection here #
        elif(command == "add"):
            cname = input("Enter Collection Name: ")
            bname = input("Enter Book Name Here: ")
            # put add to collection here #
        elif(command == "remove"):
            cname = input("Enter Collection Name: ")
            bname = input("Enter Book Name Here: ")
            # put remove from collection here #
        elif(command == "quit"):
            break
        command = input("Enter Command (Collection):").lower()

def follow(userID):
    print("Follow Users:")
    command = input("Enter Command (or help):").lower()
    while(True):
        if(command == "help"):
            print("""Collections Commands:\n
                        \tFollow: View Your Collections\n
                        \tUnfollow: Create New Collection\n
                        \tSearch: Delete Collection""")
        elif(command == "follow"):
            email = input("Enter Email: ")
            # put follow here #
        elif(command == "unfollow"):
            email = input("Enter Email: ")
            # put unfollow here #
        elif(command == "search"):
            email = input("Enter Email: ")
            # put get user by email here #
        elif(command == "quit"):
            break

def main():
    print("Welcome to the CKF Library System!")
    command = input("Please Enter Your Username (or register to sign up):")
    userID = -1
    if(command == "register"):
        userID = register()
    else:
        userID = login()

    # Primary CLI loop
    command = input("Enter a Command (or help):").lower()
    while(True):
        if(command == "help"):
            help()
        elif(command == "search"):
            search()
        elif(command == "read"):
            read(userID)
        elif(command == "collection"):
            collection(userID)
        elif(command == "follow"):
            follow(userID)
        elif(command == "quit"):
            print("Thank You for using our system, have a nice day!")
            break
        command = input("Enter a Command (or help):").lower()

main()