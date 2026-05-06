import json
import math
from datetime import datetime, date, timedelta


def begin_program():
    '''loads the data from json file and chooses the appropriate introduction sequence'''

    try:
        with open('books.json', encoding='utf-8') as f:
            books = []
            books = json.load(f)
    except FileNotFoundError:
        # If new user, initialize the user's first book
        books = []
        first_introduction()
        add_book(books)
    else:
        # If returning user, load a simpler introduction
        print(f'Welcome to the FinishBook app! Nice to see you again!') #, {name}!')
    
    active = True

    return books, active 


def first_introduction():
    print('''
Hello, welcome to FinishBook! 😃

Since it's your first time here, let's get started by adding your first book.
''')
    about_this_app = '' # add later
    licence = '' # add later
    # faq_loader() # add later


def load_main_options_screen():
    user_input = input('''
MAIN MENU: 
            What would you like to do?
            Enter 1 to add a new reading session for an existing book
            Enter 2 to check your prediction for an existing book
            Enter 3 to add a new book
            Enter 'quit' to quit

>''')
    return user_input


def add_book(books):
    # Get book details from user and store in an intermediate structure
    title = input('❓ What is the name of your book? > ').strip().strip('.').title()
    author = input('❓ Who is the author of your book? > ').strip().strip('.').title()
    pages = int(input('❓ How many pages does your book have? (If your book has introductory pages numbered in roman numerals that you also intend to read, add the number of those pages that you intend to read to the book\'s total page count.) > '))
    str_desired_finish_date = input('''
    ❓ Do you have an intended finish date? (e.g. your book club meeting)
    If not, press ENTER
    Please enter in the format: DD-MM-YYYY.
    > ''')

    book_details = {
            'title': title,
            'author': author,
            'pages': pages,
            'str_desired_finish_date': str_desired_finish_date,
        }

    # If user has already stored a book, ask if they want to enter new stats. If not, get data from last stored book
    if books:
        user_input = input(
            '''
    ❓ Do you want to add reading stats (speed, frequency, avg session length) specific to this book, or just use your most recently updated stats from your last book?
    If you want to add new stats, enter 1
    If you want to use your most recently updated stats, enter 2
> ''')

        if user_input == '1':
            speed, frequency, avg_session_length = get_new_patterns_from_user()
            reading_patterns = {
                'speed': speed,
                'frequency': frequency,
                'avg_session_length': avg_session_length,
            }
        if user_input == '2':
            reading_patterns = books[-1]['reading_patterns']
    else:
        speed, frequency, avg_session_length = get_new_patterns_from_user()
        reading_patterns = {
                'speed': speed,
                'frequency': frequency,
                'avg_session_length': avg_session_length,
            }
    
    # Amalgamate and store new book
    new_book = {'book_details': book_details, 'reading_patterns': reading_patterns}
    prediction = calc_latest_prediction(new_book)
    predictions = [prediction]
    new_book['predictions'] = predictions
    books.append(new_book)

    with open('books.json', 'w', encoding='utf-8') as f:
        json.dump(books, f)

    input('Your book was successfully added! Press ENTER to return to the main options menu.')

    return None


def get_new_patterns_from_user():
    speed = int(input('''
    💨 Let's get your personalized reading speed!

Every person has a different reading speed, but every person also has varying reading speeds per type of book. (Genre fiction tends to read faster than literary fiction, a memoir will read faster than a book on philosophy, etc.)
If you don't know your reading speed, choose from one of our defaults:
15 pages per hour (slower)
25 pages per hour (medium)
35 pages per hour (faster)

❓ What is your estimate of your reading speed for this book, in pages per hour? Please only enter digits.
> '''))
    frequency = int(input('''
    🏋 Let's get your reading frequency for this book.

Your reading frequency is how often you will pick up this book, measured in days between reading sessions.
If you're not sure what your reading frequency will be, choose from one of our defaults:
3 days between sessions if you read infrequently (about two times per week).
2 days between sessions if you read four times per week (roughly every other day).
1 day between sessions if you read daily.

❓ Enter your frequency estimate, in days between sessions. Please only enter digits.
> '''))
    avg_session_length = int(input('''
    ⏱️ Your average session length is how long you usually read for when you pick up a book to read. This is currently measured in minutes.

If you're not sure of your average session length, choose from one of our defaults:
20 minutes (short sessions)
60 mins (most common session length)
90 mins (longer sessions)

Don't worry about this personal stat too much; as you log reading sessions, the algorithm will replace this with your real session lengths.

❓ On average, how long do you read for when you pick up a book to read, measured in minutes?
> '''))
    return speed, frequency, avg_session_length


def calc_latest_prediction(working_book):
    # Load the right data
    pages = working_book['book_details']['pages']
    speed = working_book['reading_patterns']['speed']
    frequency = working_book['reading_patterns']['frequency']
    avg_session_length = working_book['reading_patterns']['avg_session_length']
    str_desired_finish_date = working_book['book_details']['str_desired_finish_date']

    # Do the calculations (not using logs or desired finish date, for now)
    predicted_pages_per_session = speed * (avg_session_length / 60)
    needed_reading_sessions = math.ceil(pages / predicted_pages_per_session)
    
    days_to_finish = 0
    for i in range(needed_reading_sessions):
        days_to_finish += frequency # Assumes you're not having a reading session today, since today is when you added the book. It's also more conservative.
    today = date.today()
    raw_predicted_end_date = today + timedelta(days=days_to_finish)
    str_predicted_end_date = raw_predicted_end_date.strftime("%d-%m-%Y")

    try:
        raw_desired_finish_date = datetime.strptime(str_desired_finish_date, "%d-%m-%Y").date()
    except ValueError:
        pass
    else:
        days_early = raw_desired_finish_date - raw_predicted_end_date # Assumes early for now
        days_early = days_early.total_seconds() / 60 / 60 / 24
        if days_early > 0:
            on_track = True
            print(f"Congrats! You are on track to finish {days_early} days early.")

    print(f'''
⏳⏳ PREDICTION ⏳⏳:

    You are predicted to read {predicted_pages_per_session} pages per reading session of {avg_session_length} minutes.
    You will need {needed_reading_sessions} reading sessions to finish the book.
    At your current frequency, your predicted finish date is: {str_predicted_end_date}.
''')

    # Store the prediction
    prediction = {
                'predicted_pages_per_session': predicted_pages_per_session,
                'needed_reading_sessions': needed_reading_sessions,
                'str_predicted_end_date': str_predicted_end_date,
                }
    
    return prediction


def end_program():
    print('Thank you for using FinishBook! Goodbye and happy reading!')



books, active = begin_program()

while active:
    user_input = load_main_options_screen()
    if user_input == '1':
        print('This feature is coming soon. Please choose a different option for now.')
    elif user_input == '2':
        title = input('Which previously entered book would you like to get the prediction for? > ').strip().strip('.').title()
        working_book = next((book for book in books if book['book_details']['title'] == title), None)
        if working_book == None:
            print("Sorry, we couldn't find your book! Are you sure you've added it before? If you are, check your spelling and try again.")
        else:
            latest_prediction = working_book['predictions'][-1]['str_predicted_end_date']
            print(f"🏁 This is your most updated predicted finish date: {latest_prediction}.")
            input('Press ENTER to return to the main options menu.')
            load_main_options_screen()

    elif user_input == '3':
        add_book(books)
    elif user_input.lower() == 'quit':
        # load_goodbye_sequence()?
        active = False
        continue
    else:
        print('Please enter a valid input.')

end_program()