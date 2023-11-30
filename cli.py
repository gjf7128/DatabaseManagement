import db_basic_functions

def register():
    print("Welcome to the CKF Library System!")
    fname = input("Please Enter Your First Name: ")
    lname = input("Please Enter Your Last Name: ")
    email = input("Please Enter Your Email: ")
    uname = input("Please Enter a Username: ")
    password = input("Please Enter a Password: ")
    db_basic_functions.register(uname, password, fname, lname, email)
    return login(uname, password)

def login(uname="", password=""):
    if(uname == "" and password == ""):
        uname = input("Enter Username: ")
        password = input("Enter Password: ")
    return db_basic_functions.login(uname, password)

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

def read(user_id):
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
    db_basic_functions.read_book(bookID, user_id, start, end)

def collection(user_id):
    print("Manage Collections:")
    command = input("Enter Command (or help):").lower()
    while(True):
        if(command == "help"):
            print("""Collections Commands:\n
                        \tview: View Your Collections\n
                        \tcreate: Create New Collection\n
                        \tdelete: Delete Collection\n
                        \tadd: Add Book to Collection\n
                        \tchange name: Change Name of Collection\n
                        \trate: Rate a book\n
                        \tremove: Remove Book from Collection\n""")
        elif(command == "view"):
            print("Here is all of your Collections:")
            print(db_basic_functions.get_collections(user_id))
        elif(command == "create"):
            cname = input("Enter Collection Name: ")
            # put create collection here #
            db_basic_functions.create_collection(user_id, cname)
        elif (command == "rate"):
            db_basic_functions.rate_book(user_id)
        elif (command == "change name"):
            db_basic_functions.change_name_of_collection(user_id)
        elif(command == "delete"):
            db_basic_functions.delete_collection(user_id)
        elif(command == "add"):
            db_basic_functions.add_book_to_collection(user_id)
        elif(command == "remove"):
            db_basic_functions.delete_book_from_collection(user_id)
        elif(command == "quit"):
            break
        command = input("Enter Command (Collection):").lower()

def follow(user_id):
    print("Follow Users:")
    command = input("Enter Command (or help):").lower()
    while(True):
        if(command == "help"):
            print("""Follow Commands:\n
                        \tFollow: Follow the Indicated User\n
                        \tUnfollow: Unfollow the Indicated User""")
        elif(command == "follow"):
            email = input("Enter Email: ")
            db_basic_functions.follow_user(user_id, email)
        elif(command == "unfollow"):
            email = input("Enter Email: ")
            db_basic_functions.unfollow_user(user_id, email)
        elif(command == "quit"):
            break

def recommendations(user_id):
    print("Book Recommendation System:")
    command = input("Enter Command (or help):").lower()
    while(True):
        if(command == "help"):
            print("""Recommendations Commands:\n
                        \t90: Display Most Popular Books of the last 90 Days\n
                        \tFollowers: Most Popular Books Among Your Followers\n
                        \tMonth: Most Popular Books of this Month\n
                        \tGenre: Books Based on Your Read History (By Genre)\n
                        \tAuthor: Books Based on Your Read History (By Author)\n
                    `   \tQuit: Quit to Main Menu""")
        elif(command == "90"):
            print(db_basic_functions.most_pop_90_days())
        elif(command == "followers"):
            print(db_basic_functions.most_pop_among_followers(user_id))
        elif(command == "month"):
            print(db_basic_functions.top_5_calendar_month())
        elif(command == "genre"):
            print(db_basic_functions.recommend_genre_history(user_id))
        elif(command == "author"):
            print(db_basic_functions.recommend_author_history(user_id))
        elif(command == "quit"):
            break

def main():
    print("Welcome to the CKF Library System!")
    command = input("Please Enter Your Username (or register to sign up):")
    user_id = -1
    if(command == "register"):
        user_id = register()
    else:
        user_id = login()

    # Primary CLI loop
    command = input("Enter a Command (or help):").lower()
    while(True):
        if(command == "help"):
            help()
        elif(command == "search"):
            search()
        elif(command == "read"):
            read(user_id)
        elif(command == "collection"):
            collection(user_id)
        elif(command == "follow"):
            follow(user_id)
        elif(command == "quit"):
            print("Thank You for using our system, have a nice day!")
            break
        command = input("Enter a Command (or help):").lower()

main()