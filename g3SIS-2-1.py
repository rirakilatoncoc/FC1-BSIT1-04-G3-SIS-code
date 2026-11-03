# ============================================================
# DIGITAL STUDENT INFORMATION SYSTEM
# CONSOLE-BASED SYSTEM
# ============================================================

from datetime import datetime, date
import re

WIDTH = 60
MAX_ID_LENGTH = 12

# Common courses / fields (students may also type their own)
COURSES = [
    ("BSIT", "BS Information Technology"),
    ("BSCS", "BS Computer Science"),
    ("BSIS", "BS Information Systems"),
    ("BSBA", "BS Business Administration"),
    ("BSA", "BS Accountancy"),
    ("BSED", "BS Education"),
    ("BSN", "BS Nursing"),
    ("BSCE", "BS Civil Engineering"),
    ("BSHM", "BS Hospitality Management"),
]

# Lists for accounts
student_accounts = []
registrar_accounts = []
instructor_accounts = []

# Student information
student_ids = []
student_names = []
student_status = []
student_registered = []
student_courses = []
student_birthdays = []

# Student records
student_schedules = []
student_attendance = []


# ============================================================
# DISPLAY / FORMAT HELPERS
# ============================================================

def line():
    print("=" * WIDTH)


def current_datetime():
    # Example: October 09, 2026 | 02:30 PM
    return datetime.now().strftime("%B %d, %Y | %I:%M %p")


def title(text, show_date=False):
    line()
    print(text.center(WIDTH))
    if show_date:
        print(current_datetime().center(WIDTH))
    line()


def pause():
    input("\nPress ENTER to continue...")


def ask(prompt):
    # Input with extra spaces removed from both ends
    return input(prompt).strip()


def fit(text, width):
    # Keep long values from breaking the table layout.
    text = str(text)
    if width <= 3:
        return text[:width]
    if len(text) > width:
        return text[:width - 3] + "..."
    return text


def print_table(headers, rows, widths, aligns=None):
    # Draws a clean console table with aligned columns and a distinct header.
    # widths are the inner widths of the columns.
    # aligns supports "l" (left), "c" (center), and "r" (right).

    if not headers:
        print("No table columns to display.")
        return

    if len(headers) != len(widths):
        raise ValueError("The number of headers must match the number of column widths.")

    if aligns is None:
        aligns = ["l"] * len(widths)
    else:
        aligns = list(aligns[:len(widths)])
        aligns.extend(["l"] * (len(widths) - len(aligns)))

    # Use consistent minimum widths and safely handle incomplete rows.
    widths = [max(1, int(width)) for width in widths]
    border = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
    header_border = "+" + "+".join("=" * (width + 2) for width in widths) + "+"

    def make_row(cells):
        cells = list(cells)
        if len(cells) < len(widths):
            cells.extend([""] * (len(widths) - len(cells)))

        parts = []
        for i, width in enumerate(widths):
            value = fit(cells[i], width)
            if aligns[i] == "r":
                value = value.rjust(width)
            elif aligns[i] == "c":
                value = value.center(width)
            else:
                value = value.ljust(width)
            parts.append(" " + value + " ")
        return "|" + "|".join(parts) + "|"

    print(border)
    print(make_row(headers))
    print(header_border)

    if not rows:
        print(make_row(["No records found."] + [""] * (len(widths) - 1)))
    else:
        for row in rows:
            print(make_row(row))
            print(border)
        return

    print(border)


def clean_spaces(text):
    # "  juan    dela cruz " -> "juan dela cruz"
    return " ".join(text.split())


def format_name(name):
    # "  juan   DELA cruz " -> "Juan Dela Cruz"
    return clean_spaces(name).title()


def format_subject(subject):
    # "math 101" -> "Math 101", but "IT 101" stays "IT 101"
    words = clean_spaces(subject).split(" ")
    return " ".join(word[:1].upper() + word[1:] for word in words)


def is_valid_username(username):
    # 4-30 characters; special characters are allowed, but spaces are not.
    # Examples: rich.glenn_01, rich@glenn!, Glenn#2026
    if not re.fullmatch(r"\S{4,30}", username):
        print("Invalid username. Use 4-30 characters with no spaces. Special characters are allowed.")
        print("Example: rich.glenn_01 or Glenn@2026!")
        return False
    return True


def is_valid_password(password):
    if len(password) < 6 or any(ch.isspace() for ch in password):
        print("Invalid password. Use at least 6 characters with no spaces.")
        print("Special characters are allowed. Example: Glenn@2026!")
        return False
    return True


def is_valid_schedule(schedule):
    # Required format: Mon, Wed, Fri 08:00 AM - 09:30 AM
    pattern = r"^([A-Za-z]+(?:\s*,\s*[A-Za-z]+)*)\s+(\d{1,2}:\d{2}\s*(?:AM|PM))\s*-\s*(\d{1,2}:\d{2}\s*(?:AM|PM))$"
    match = re.fullmatch(pattern, clean_spaces(schedule), re.IGNORECASE)
    if not match:
        print("Invalid schedule format. Use: Mon, Wed, Fri 08:00 AM - 09:30 AM")
        return False
    valid_days = {"mon", "monday", "tue", "tues", "tuesday", "wed", "wednesday",
                  "thu", "thur", "thurs", "thursday", "fri", "friday",
                  "sat", "saturday", "sun", "sunday"}
    days = [day.strip().lower() for day in match.group(1).split(",")]
    if any(day not in valid_days for day in days):
        print("Invalid day. Use day names such as Mon, Monday, or Friday.")
        return False
    if len({day[:3] for day in days}) != len(days):
        print("Duplivcate day. Each day can only appear once.")
        return False
    try:
        start = datetime.strptime(match.group(2).upper().replace(" ", ""), "%I:%M%p")
        end = datetime.strptime(match.group(3).upper().replace(" ", ""), "%I:%M%p")
    except ValueError:
        print("Invalid time. Use a valid 12-hour time such as 08:30 AM.")
        return False
    if end <= start:
        print("Invalid time range. End time must be later than start time.")
        return False
    return True


def parse_birthday(text):
    # Accepts MM/DD/YYYY. Returns a date, or None if invalid.
    try:
        return datetime.strptime(text.strip(), "%m/%d/%Y").date()
    except ValueError:
        return None


def compute_age(birthday):
    today = date.today()
    had_birthday = (today.month, today.day) >= (birthday.month, birthday.day)
    return today.year - birthday.year - (0 if had_birthday else 1)


def format_birthday(birthday):
    # Example: March 15, 2005
    return birthday.strftime("%B %d, %Y")


def is_valid_birthday(text):
    birthday = parse_birthday(text)
    if birthday is None:
        print("Invalid birthday. Use MM/DD/YYYY. Example: 03/15/2005")
        return False
    if birthday > date.today():
        print("Birthday cannot be in the future.")
        return False
    if not 5 <= compute_age(birthday) <= 100:
        print("Invalid birthday. Student age must be between 5 and 100 years old.")
        return False
    return True


def ask_birthday():
    # Keeps asking until valid. ENTER = cancel (returns None).
    print("Birthday format: MM/DD/YYYY  (Example: 03/15/2005)")

    while True:

        text = ask("Birthday (ENTER = cancel): ")

        if text == "":
            return None

        if is_valid_birthday(text):
            return parse_birthday(text)


def course_label(course):
    # "BSIT" -> "BSIT - BS Information Technology"; custom courses stay as typed.
    for code, name in COURSES:
        if code == course:
            return code + " - " + name
    return course


def ask_course():
    # Keeps asking until valid. ENTER = cancel (returns None).
    print("\nCOURSE / FIELD")

    for number, (code, name) in enumerate(COURSES, 1):
        print("{:>2}. {} - {}".format(number, code, name))

    other = len(COURSES) + 1
    print("{:>2}. Other (type your own)".format(other))

    while True:

        choice = ask("\nChoose course/field (ENTER = cancel): ")

        if choice == "":
            return None

        if is_whole_number(choice) and 1 <= int(choice) <= len(COURSES):
            return COURSES[int(choice) - 1][0]

        if choice == str(other):
            custom = format_subject(ask("Enter course/field (ENTER = back): "))

            if custom == "":
                continue

            if len(custom) < 2 or len(custom) > 40 or not any(ch.isalpha() for ch in custom):
                print("Invalid course/field. Use 2-40 characters with at least one letter.")
                continue

            # If they typed a known code (e.g. "bsit"), use the standard code.
            for code, name in COURSES:
                if custom.upper() == code:
                    return code

            return custom

        print("Invalid choice. Enter a number from the list.")


def is_whole_number(text):
    return text.isascii() and text.isdigit()


def ask_number(prompt):
    # Keeps asking until a whole number is typed. ENTER = cancel (returns None).
    while True:

        value = ask(prompt)

        if value == "":
            return None

        if is_whole_number(value):
            return int(value)

        print("Numbers only.")


def ask_choice(prompt, options, allow_cancel=False):
    # Keeps asking until the answer is one of the options.
    # With allow_cancel=True, ENTER returns None.
    while True:

        choice = ask(prompt)

        if allow_cancel and choice == "":
            return None

        if choice in options:
            return choice

        print("Invalid choice. Please enter one of: " + ", ".join(options) + ".")


def ask_yes_no(prompt):
    # Keeps asking until the answer is Y or N. Returns True for yes.
    while True:

        answer = ask(prompt + " (Y/N): ").lower()

        if answer in ("y", "yes"):
            return True

        if answer in ("n", "no"):
            return False

        print("Please type Y or N.")


def ask_name(label="Student Name"):
    # Keeps asking until valid. ENTER = cancel (returns None).
    print("Name format: Last Name, First Name Middle Initial")
    print("Example: Kilaton, Rich Glenn R.")

    while True:

        name = ask(label + " (ENTER = cancel): ")

        if name == "":
            return None

        if is_valid_name(name):
            return format_name(name)


def ask_subject():
    # Keeps asking until valid. ENTER = cancel (returns None).
    while True:

        subject = format_subject(ask("Subject (ENTER = cancel): "))

        if subject == "":
            return None

        if len(subject) > 40 or not any(ch.isalpha() for ch in subject) or " - " in subject:
            print("Invalid subject. Use up to 40 characters with at least one letter.")
            continue

        return subject


def ask_schedule(prompt="Schedule"):
    # Keeps asking until valid. ENTER = cancel (returns None).
    print("Format: Mon, Wed, Fri 08:00 AM - 09:30 AM")

    while True:

        schedule = clean_spaces(ask(prompt + " (ENTER = cancel): "))

        if schedule == "":
            return None

        if is_valid_schedule(schedule):
            return schedule


def ask_attendance_numbers():
    # Returns (total_days, present, absent), or None if cancelled.
    while True:

        total_days = ask_number("Total Days (ENTER = cancel): ")

        if total_days is None:
            return None

        if total_days == 0:
            print("Total days must be at least 1.")
            continue

        break

    while True:

        present = ask_number("Total Present (ENTER = cancel): ")

        if present is None:
            return None

        absent = ask_number("Total Absent (ENTER = cancel): ")

        if absent is None:
            return None

        if present + absent == total_days:
            return total_days, present, absent

        print("Present + Absent must equal Total Days ({}). Enter them again.".format(total_days))


def ask_new_account(accounts):
    # Keeps asking until username and password are valid.
    # ENTER = cancel (returns None). Returns [username, password].
    while True:

        username = ask("Create Username (ENTER = cancel): ")

        if username == "":
            return None

        if not is_valid_username(username):
            continue

        if any(account[0].lower() == username.lower() for account in accounts):
            print("Username taken. Try another.")
            continue

        break

    while True:

        password = ask("Create Password (ENTER = cancel): ")

        if password == "":
            return None

        if is_valid_password(password):
            return [username, password]


# ============================================================
# CREATE ACCOUNT
# ============================================================

def create_account():

    title("CREATE ACCOUNT")

    print("1. Student")
    print("2. Registrar")
    print("3. Instructor")
    print("4. Back")

    choice = ask_choice("\nChoose account type: ", ("1", "2", "3", "4"))

    if choice == "4":
        return

    if choice == "1":
        accounts, label = student_accounts, "Student"
    elif choice == "2":
        accounts, label = registrar_accounts, "Registrar"
    else:
        accounts, label = instructor_accounts, "Instructor"

    print("\nUsername: 4-30 characters, no spaces (special characters allowed).")
    print("Password: at least 6 characters, no spaces.\n")

    account = ask_new_account(accounts)

    if account is None:
        print("\nAccount creation cancelled.")
        pause()
        return

    accounts.append(account)
    print("\n{} account created!".format(label))

    pause()


# ============================================================
# LOGIN
# ============================================================

def login(accounts):
    # Keeps asking until the login is correct. ENTER on username = cancel.

    while True:

        username = ask("Username (ENTER = cancel): ")

        if username == "":
            return False

        password = ask("Password: ")

        for account in accounts:

            if account[0].lower() == username.lower() and account[1] == password:
                return True

        print("Invalid username or password. Try again.")


# ============================================================
# VALIDATION
# ============================================================

def is_valid_name(name):
    # Required format: Last Name, First Name Middle Initial
    name = clean_spaces(name)
    if not name:
        print("Name is required.")
        return False
    if len(name) < 3 or len(name) > 60 or "," not in name:
        print("Invalid name format. Use: Last Name, First Name Middle Initial")
        print("Example: Kilaton, Rich Glenn R.")
        return False

    last_name, given_names = name.split(",", 1)
    if not last_name.strip() or not given_names.strip():
        print("Invalid name format. Use: Last Name, First Name Middle Initial")
        print("Example: Kilaton, Rich Glenn R.")
        return False

    if any(not (ch.isalpha() or ch in " ,.-'") for ch in name):
        print("Invalid name. Use letters, spaces, commas, apostrophes, periods, or hyphens only.")
        return False

    if not any(ch.isalpha() for ch in last_name) or not any(ch.isalpha() for ch in given_names):
        print("Invalid name. Enter a valid last name and first name.")
        return False

    return True


def id_format_ok(text):
    # Quiet check (no messages): 1-8 digits, or the format 2024-0001.
    return re.fullmatch(r"(?:\d{1,8}|\d{4}-\d{4})", text, re.ASCII) is not None


def is_valid_id(student_id):
    if not student_id:
        print("ID is required.")
        return False
    if not id_format_ok(student_id):
        print("Invalid ID. Use 12345 or the format 2024-0001.")
        return False
    return True


def ask_student_id(label="Student ID"):
    # Keeps asking until the ID is valid. ENTER on empty = cancel.
    while True:

        student_id = ask(label + " (ENTER = cancel): ")

        if student_id == "":
            return None

        if is_valid_id(student_id):
            return student_id


# ============================================================
# FIND / SELECT STUDENT
# ============================================================

def find_student(student_id):

    for i in range(len(student_ids)):

        if student_ids[i] == student_id:
            return i

    return -1


def show_student_list(indexes=None, heading="REGISTERED STUDENTS"):
    # Shows students so the user does not have to remember or guess the ID.
    # Pass a list of indexes to show only those students (e.g. search results).

    print("\n" + heading)

    if len(student_ids) == 0:
        print("No students registered yet.")
        return False

    if indexes is None:
        indexes = list(range(len(student_ids)))

    rows = []

    for number, i in enumerate(indexes, 1):

        rows.append([
            str(number),
            student_ids[i],
            student_names[i],
            student_courses[i]
        ])

    print_table(
        ["No.", "Student ID", "Name", "Course / Field"],
        rows,
        [3, 10, 19, 14],
        ["c", "l", "l", "l"]
    )

    if len(indexes) == len(student_ids):
        print("Total students:", len(student_ids))
    else:
        print("Matches found: {} of {}".format(len(indexes), len(student_ids)))

    return True


def search_students(keyword):
    # Every word typed must appear somewhere in the student's
    # ID, name, course/field, or birthday (case-insensitive).
    words = keyword.lower().split()
    matches = []

    for i in range(len(student_ids)):

        text = " ".join([
            student_ids[i],
            student_names[i],
            student_courses[i],
            course_label(student_courses[i]),
            format_birthday(student_birthdays[i])
        ]).lower()

        if all(word in text for word in words):
            matches.append(i)

    return matches


def select_from_matches(matches):
    # Show the matches and let the user pick one by ID.
    # Returns the student's index, or -1 if the user goes back.

    show_student_list(matches, "SEARCH RESULTS")
    print()

    while True:

        student_id = ask("Enter Student ID to select (ENTER = back): ")

        if student_id == "":
            return -1

        index = find_student(student_id)

        if index in matches:
            return index

        print("That ID is not in the search results.")


def pick_student(show_list=True):
    # Returns the student's index, or -1 if cancelled.
    # The user can type an ID directly, or type words to search
    # (name, course/field, birthday, or part of an ID).

    if len(student_ids) == 0:
        print("\nNo students registered yet.")
        pause()
        return -1

    if show_list:
        show_student_list()
        print()

    print("Type a Student ID, or search by name, course, or birthday.")
    print("Examples: 2024-0001 | kilaton | BSIT | march")

    while True:

        entry = ask("Student ID or search (ENTER = cancel): ")

        if entry == "":
            return -1

        if id_format_ok(entry):

            index = find_student(entry)

            if index != -1:
                return index

        matches = search_students(entry)

        if len(matches) == 0:
            print('No student found for "{}". Try again.'.format(entry))
            continue

        index = select_from_matches(matches)

        if index != -1:
            return index


# ============================================================
# DISPLAY STUDENT INFORMATION
# ============================================================

def display_student(index):

    print("\nSTUDENT INFORMATION")

    print_table(
        ["Field", "Details"],
        [
            ["Student ID", student_ids[index]],
            ["Name", student_names[index]],
            ["Course / Field", course_label(student_courses[index])],
            ["Birthday", format_birthday(student_birthdays[index])],
            ["Age", str(compute_age(student_birthdays[index]))],
            ["Status", student_status[index]],
            ["Registered", student_registered[index]]
        ],
        [14, 39]
    )


def show_schedules(index):

    rows = []

    for i in range(len(student_schedules[index])):

        # Stored as "Subject - Schedule"
        parts = student_schedules[index][i].split(" - ", 1)

        subject = parts[0]
        schedule = parts[1] if len(parts) > 1 else ""

        rows.append([str(i + 1), subject, schedule])

    print_table(
        ["No.", "Subject", "Schedule"],
        rows,
        [4, 18, 28],
        ["c", "l", "l"]
    )


def find_schedule(index, subject):
    # Match the exact subject (not just the first letters)

    prefix = subject.lower() + " - "

    for i in range(len(student_schedules[index])):

        if student_schedules[index][i].lower().startswith(prefix):
            return i

    return -1


def show_attendance(index):

    rows = []

    for record in student_attendance[index]:

        subject = record[0]
        total_days = record[1]
        present = record[2]
        absent = record[3]

        if total_days > 0:
            percentage = (present / total_days) * 100
        else:
            percentage = 0

        rows.append([
            subject,
            total_days,
            present,
            absent,
            "{:.1f}%".format(percentage)
        ])

    print_table(
        ["Subject", "Days", "Present", "Absent", "Rate"],
        rows,
        [19, 5, 7, 6, 7],
        ["l", "c", "c", "c", "r"]
    )


def display_full_record(index):
    # Personal information + class schedule + attendance in one view.

    display_student(index)

    print("\nCLASS SCHEDULE")

    if len(student_schedules[index]) == 0:
        print("No class schedule yet.")
    else:
        show_schedules(index)

    print("\nATTENDANCE")

    if len(student_attendance[index]) == 0:
        print("No attendance records yet.")
    else:
        show_attendance(index)


# ============================================================
# STUDENT MENU
# ============================================================

def student_menu():

    title("STUDENT LOGIN")

    if len(student_accounts) == 0:

        print("No student accounts yet.")
        pause()
        return

    if not login(student_accounts):
        return

    print("\nLogin successful!\n")

    while True:

        student_id = ask_student_id("Your Student ID")

        if student_id is None:
            return

        index = find_student(student_id)

        if index != -1:
            break

        print("ID not found. Try again.")

    while True:

        title("STUDENT PORTAL", True)

        print("Welcome,", student_names[index])
        print()
        print("1. View Personal Information")
        print("2. View Attendance")
        print("3. View Class Schedule")
        print("4. Logout")

        choice = ask("\nChoose an option: ")

        # PERSONAL INFORMATION
        if choice == "1":

            display_student(index)
            pause()

        # ATTENDANCE
        elif choice == "2":

            title("MY ATTENDANCE")

            if len(student_attendance[index]) == 0:

                print("No attendance records.")

            else:

                show_attendance(index)

            pause()

        # CLASS SCHEDULE
        elif choice == "3":

            title("MY CLASS SCHEDULE")

            if len(student_schedules[index]) == 0:

                print("No class schedule.")

            else:

                show_schedules(index)

            pause()

        # LOGOUT
        elif choice == "4":

            print("Logging out...")
            break

        else:

            print("Invalid choice.")
            pause()


# ============================================================
# REGISTRAR - ADD STUDENT
# ============================================================

def add_student():

    title("ADD STUDENT")

    while True:

        student_id = ask_student_id()

        if student_id is None:
            return

        if find_student(student_id) == -1:
            break

        print("ID already exists. Enter a different ID.")

    name = ask_name()

    if name is None:
        print("Cancelled.")
        pause()
        return

    course = ask_course()

    if course is None:
        print("Cancelled.")
        pause()
        return

    print()
    birthday = ask_birthday()

    if birthday is None:
        print("Cancelled.")
        pause()
        return

    print("\n1. Regular")
    print("2. Irregular")

    choice = ask_choice("Choose status (ENTER = cancel): ", ("1", "2"), True)

    if choice is None:
        print("Cancelled.")
        pause()
        return

    status = "Regular" if choice == "1" else "Irregular"

    student_ids.append(student_id)
    student_names.append(name)
    student_courses.append(course)
    student_birthdays.append(birthday)
    student_status.append(status)
    student_registered.append(datetime.now().strftime("%B %d, %Y"))

    student_schedules.append([])
    student_attendance.append([])

    print("\nStudent added!")
    display_student(len(student_ids) - 1)

    pause()


# ============================================================
# REGISTRAR / INSTRUCTOR - VIEW / SEARCH STUDENT
# ============================================================

def view_student():
    # One screen for both viewing and searching:
    # pick from the list, type an ID, or type S to search.

    title("VIEW / SEARCH STUDENT")

    if len(student_ids) == 0:

        print("No students registered yet.")
        pause()
        return

    index = pick_student()

    if index == -1:
        return

    display_full_record(index)
    pause()


# ============================================================
# REGISTRAR - UPDATE STUDENT
# ============================================================

def update_student():

    title("UPDATE STUDENT")

    index = pick_student()

    if index == -1:
        return

    while True:

        title("UPDATE INFORMATION")

        print("Student:", student_names[index])
        print()
        print("1. Update Student ID")
        print("2. Update Student Name")
        print("3. Update Course / Field")
        print("4. Update Birthday")
        print("5. Update Status")
        print("6. Back")

        choice = ask("\nChoose an option: ")

        if choice == "1":

            while True:

                new_id = ask_student_id("New Student ID")

                if new_id is None:
                    print("Cancelled.")
                    break

                if new_id == student_ids[index]:

                    print("Same as current ID. Enter a different ID.")

                elif find_student(new_id) != -1:

                    print("ID already exists. Enter a different ID.")

                else:

                    student_ids[index] = new_id
                    print("ID updated.")
                    break

            pause()

        elif choice == "2":

            new_name = ask_name("New Student Name")

            if new_name is None:

                print("Cancelled.")

            else:

                student_names[index] = new_name
                print("Name updated.")

            pause()

        elif choice == "3":

            print("Current:", course_label(student_courses[index]))

            course = ask_course()

            if course is None:

                print("Cancelled.")

            else:

                student_courses[index] = course
                print("Course / Field updated.")

            pause()

        elif choice == "4":

            print("Current:", format_birthday(student_birthdays[index]))

            birthday = ask_birthday()

            if birthday is None:

                print("Cancelled.")

            else:

                student_birthdays[index] = birthday
                print("Birthday updated.")

            pause()

        elif choice == "5":

            print("\n1. Regular")
            print("2. Irregular")

            status = ask_choice("Choose status (ENTER = cancel): ", ("1", "2"), True)

            if status is None:

                print("Cancelled.")

            else:

                student_status[index] = "Regular" if status == "1" else "Irregular"
                print("Status updated.")

            pause()

        elif choice == "6":

            break

        else:

            print("Invalid choice.")
            pause()


# ============================================================
# REGISTRAR - REMOVE STUDENT
# ============================================================

def remove_student():

    title("REMOVE STUDENT")

    index = pick_student()

    if index == -1:
        return

    display_student(index)

    print("\nThis will also delete the student's schedule and attendance.")
    if not ask_yes_no("Remove this student?"):

        print("Removal cancelled.")
        pause()
        return

    student_ids.pop(index)
    student_names.pop(index)
    student_courses.pop(index)
    student_birthdays.pop(index)
    student_status.pop(index)
    student_registered.pop(index)
    student_schedules.pop(index)
    student_attendance.pop(index)

    print("Student removed.")
    pause()


# ============================================================
# REGISTRAR / INSTRUCTOR - MANAGE SCHEDULE
# ============================================================

def add_schedule(index):

    while True:

        subject = ask_subject()

        if subject is None:
            print("Cancelled.")
            return

        if find_schedule(index, subject) != -1:
            print("Subject already scheduled. Enter a different subject.")
            continue

        schedule = ask_schedule()

        if schedule is None:
            print("Cancelled.")
            return

        student_schedules[index].append(subject + " - " + schedule)
        print("Schedule added.")
        return


def ask_schedule_position(index):
    # Shows the student's schedules and asks for a number.
    # Returns the list position, or None if there is nothing / cancelled.

    if len(student_schedules[index]) == 0:
        print("No schedules yet.")
        return None

    print()
    show_schedules(index)
    print()

    while True:

        number = ask_number("Schedule number (ENTER = cancel): ")

        if number is None:
            print("Cancelled.")
            return None

        if 1 <= number <= len(student_schedules[index]):
            return number - 1

        print("Invalid number. Choose a number from the list.")


def update_schedule(index):

    position = ask_schedule_position(index)

    if position is None:
        return

    new_schedule = ask_schedule("New Schedule")

    if new_schedule is None:
        print("Cancelled.")
        return

    subject = student_schedules[index][position].split(" - ", 1)[0]
    student_schedules[index][position] = subject + " - " + new_schedule
    print("Schedule updated.")


def delete_schedule(index):

    position = ask_schedule_position(index)

    if position is None:
        return

    if ask_yes_no("Delete this schedule?"):
        student_schedules[index].pop(position)
        print("Schedule deleted.")
    else:
        print("Cancelled.")


def manage_schedule():
    # Used by both the Registrar and the Instructor.

    title("MANAGE CLASS SCHEDULE")

    index = pick_student()

    if index == -1:
        return

    while True:

        print("\nStudent:", student_names[index])
        print()
        print("1. Add Schedule")
        print("2. Update Schedule")
        print("3. Delete Schedule")
        print("4. View Schedule")
        print("5. Back")

        choice = ask_choice("\nChoose an option: ", ("1", "2", "3", "4", "5"))

        if choice == "5":
            return

        if choice == "1":
            add_schedule(index)

        elif choice == "2":
            update_schedule(index)

        elif choice == "3":
            delete_schedule(index)

        else:

            if len(student_schedules[index]) == 0:
                print("No schedule yet.")
            else:
                print()
                show_schedules(index)

        pause()


# ============================================================
# REGISTRAR MENU
# ============================================================

def registrar_menu():

    title("REGISTRAR LOGIN")

    if len(registrar_accounts) == 0:

        print("No registrar accounts yet.")
        pause()
        return

    if not login(registrar_accounts):
        return

    print("\nLogin successful!")

    while True:

        title("REGISTRAR PORTAL", True)

        print("1. Add Student")
        print("2. View / Search Student")
        print("3. Update Student Information")
        print("4. Manage Class Schedule")
        print("5. Remove Student")
        print("6. Logout")

        choice = ask("\nChoose an option: ")

        if choice == "1":

            add_student()

        elif choice == "2":

            view_student()

        elif choice == "3":

            update_student()

        elif choice == "4":

            manage_schedule()

        elif choice == "5":

            remove_student()

        elif choice == "6":

            print("Logging out...")
            break

        else:

            print("Invalid choice.")
            pause()


# ============================================================
# INSTRUCTOR - ATTENDANCE
# ============================================================

def manage_attendance():

    title("ATTENDANCE MANAGEMENT")

    index = pick_student()

    if index == -1:
        return

    print("\nStudent:", student_names[index])

    subject = ask_subject()

    if subject is None:

        print("Cancelled.")
        pause()
        return

    print("\nEnter Attendance")

    numbers = ask_attendance_numbers()

    if numbers is None:

        print("Cancelled.")
        pause()
        return

    total_days, present, absent = numbers

    found = False

    for record in student_attendance[index]:

        if record[0].lower() == subject.lower():

            record[1] = total_days
            record[2] = present
            record[3] = absent

            found = True

    if found:

        print("\nAttendance updated.")

    else:

        student_attendance[index].append(
            [subject, total_days, present, absent]
        )

        print("\nAttendance added.")

    print("\nCurrent attendance for", student_names[index])
    show_attendance(index)

    pause()


# ============================================================
# INSTRUCTOR MENU
# ============================================================

def instructor_menu():

    title("INSTRUCTOR LOGIN")

    if len(instructor_accounts) == 0:

        print("No instructor accounts yet.")
        pause()
        return

    if not login(instructor_accounts):
        return

    print("\nLogin successful!")

    while True:

        title("INSTRUCTOR PORTAL", True)

        print("1. Add / Update Attendance")
        print("2. Manage Class Schedule")
        print("3. View / Search Student")
        print("4. Logout")

        choice = ask("\nChoose an option: ")

        if choice == "1":

            manage_attendance()

        elif choice == "2":

            manage_schedule()

        elif choice == "3":

            view_student()

        elif choice == "4":

            print("Logging out...")
            break

        else:

            print("Invalid choice.")
            pause()


# ============================================================
# MAIN MENU
# ============================================================

def run_system():

    while True:

        title("DIGITAL STUDENT INFORMATION SYSTEM", True)

        print("1. Create Account")
        print("2. Student Login")
        print("3. Registrar Login")
        print("4. Instructor Login")
        print("5. Exit")

        choice = ask("\nChoose an option: ")

        if choice == "1":

            create_account()

        elif choice == "2":

            student_menu()

        elif choice == "3":

            registrar_menu()

        elif choice == "4":

            instructor_menu()

        elif choice == "5":

            print("\nThank you for using the system!")
            break

        else:

            print("Invalid choice.")
            pause()


def main():
    # Closes cleanly on Ctrl+C / Ctrl+D instead of crashing with an error.
    try:
        run_system()
    except (KeyboardInterrupt, EOFError):
        print("\n\nSystem closed. Goodbye!")


# ============================================================
# START SYSTEM
# ============================================================

if __name__ == "__main__":
    main()
