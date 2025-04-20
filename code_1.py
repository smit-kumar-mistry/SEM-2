# Library Management System with Fallback Recommendations
import os
import json
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import random
from datetime import timedelta

# Try to import Gemini API, but have fallback if it's not available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Configuration
DATA_DIR = "library_data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
BOOKS_FILE = os.path.join(DATA_DIR, "books.json")
ISSUES_FILE = os.path.join(DATA_DIR, "issues.json")
PROFILE_DIR = os.path.join(DATA_DIR, "profiles")

# Configure Gemini API if available
GEMINI_API_KEY = "AIzaSyAFLVcrKqEnw6RN5cw5sQ1MusOxTySCCqU"
if GEMINI_AVAILABLE:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        GEMINI_AVAILABLE = False

# Initialize data directory
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PROFILE_DIR, exist_ok=True)

# Sample book recommendations based on mood
MOOD_RECOMMENDATIONS = {
    "happy": [
        {"title": "The Happiness Project", "author": "Gretchen Rubin"},
        {"title": "Born a Crime", "author": "Trevor Noah"},
        {"title": "The House in the Cerulean Sea", "author": "TJ Klune"}
    ],
    "sad": [
        {"title": "When Things Fall Apart", "author": "Pema Chödrön"},
        {"title": "Man's Search for Meaning", "author": "Viktor E. Frankl"},
        {"title": "The Boy, the Mole, the Fox and the Horse", "author": "Charlie Mackesy"}
    ],
    "anxious": [
        {"title": "Dare", "author": "Barry McDonagh"},
        {"title": "The Worry Trick", "author": "David Carbonell"},
        {"title": "Hope and Help for Your Nerves", "author": "Claire Weekes"}
    ],
    "bored": [
        {"title": "Ready Player One", "author": "Ernest Cline"},
        {"title": "The Night Circus", "author": "Erin Morgenstern"},
        {"title": "Dark Matter", "author": "Blake Crouch"}
    ],
    "inspired": [
        {"title": "Atomic Habits", "author": "James Clear"},
        {"title": "Educated", "author": "Tara Westover"},
        {"title": "Becoming", "author": "Michelle Obama"}
    ],
    "relaxed": [
        {"title": "The Thursday Murder Club", "author": "Richard Osman"},
        {"title": "The Midnight Library", "author": "Matt Haig"},
        {"title": "Project Hail Mary", "author": "Andy Weir"}
    ]
}

# Sample book information database
BOOK_INFO = {
    "To Kill a Mockingbird": "A powerful story about racial injustice in the American South during the 1930s, told through the eyes of a young girl named Scout Finch. Her father, lawyer Atticus Finch, defends a Black man falsely accused of raping a white woman. The novel explores themes of moral growth, compassion, and justice.",
    "1984": "George Orwell's dystopian classic depicts a totalitarian society where the government, led by Big Brother, controls every aspect of citizens' lives including their thoughts. The protagonist Winston Smith rebels by keeping a diary and falling in love. The novel introduced concepts like 'thoughtcrime,' 'doublethink,' and 'Newspeak' that remain relevant in discussions about surveillance and authoritarianism.",
    "Pride and Prejudice": "Jane Austen's beloved novel follows Elizabeth Bennet as she navigates issues of manners, upbringing, and marriage in 19th-century England. When she meets the wealthy, proud Mr. Darcy, their mutual prejudices create a series of misunderstandings before they eventually overcome their pride to find love and understanding.",
    "The Hobbit": "J.R.R. Tolkien's fantasy adventure follows Bilbo Baggins, a comfort-loving hobbit who reluctantly joins a quest with thirteen dwarves to reclaim their mountain home from the dragon Smaug. Throughout his journey, Bilbo discovers courage, wisdom, and a magical ring that will later become central to 'The Lord of the Rings'."
}

# Initialize data files if they don't exist
def initialize_data():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({"admin": {"password": "admin123", "profile_pic": "", "role": "admin"}}, f)
    
    if not os.path.exists(BOOKS_FILE):
        sample_books = {
            "B001": {"title": "To Kill a Mockingbird", "author": "Harper Lee", "genre": "Classic", "available": True},
            "B002": {"title": "1984", "author": "George Orwell", "genre": "Dystopian", "available": True},
            "B003": {"title": "The Hobbit", "author": "J.R.R. Tolkien", "genre": "Fantasy", "available": True},
            "B004": {"title": "Pride and Prejudice", "author": "Jane Austen", "genre": "Romance", "available": True},
            "B005": {"title": "The Alchemist", "author": "Paulo Coelho", "genre": "Fiction", "available": True}
        }
        with open(BOOKS_FILE, 'w') as f:
            json.dump(sample_books, f)
    
    if not os.path.exists(ISSUES_FILE):
        with open(ISSUES_FILE, 'w') as f:
            json.dump({}, f)

# Helper functions for data management
def load_data(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_data(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f)

# Book recommendations (with fallback if AI not available)
def get_book_recommendations(mood):
    # Try to use Gemini if available
    if GEMINI_AVAILABLE:
        try:
            # Try different model names that might be available
            model_names = ['gemini-pro', 'gemini-1.5-pro', 'models/gemini-pro']
            
            for model_name in model_names:
                try:
                    model = genai.GenerativeModel(model_name)
                    prompt = f"I'm feeling {mood}. Recommend 3 books that would suit my mood. For each book, provide just the title and author."
                    response = model.generate_content(prompt)
                    return response.text
                except Exception as e:
                    print(f"Failed with model {model_name}: {e}")
                    continue
        except Exception as e:
            print(f"Error using Gemini API: {e}")
    
    # Fallback recommendation system
    mood = mood.lower()
    
    # Check if we have recommendations for this specific mood
    if mood in MOOD_RECOMMENDATIONS:
        books = MOOD_RECOMMENDATIONS[mood]
    else:
        # Find most similar mood or pick random mood
        all_moods = list(MOOD_RECOMMENDATIONS.keys())
        for known_mood in all_moods:
            if known_mood in mood or mood in known_mood:
                books = MOOD_RECOMMENDATIONS[known_mood]
                break
        else:
            # If no match, pick random mood
            random_mood = random.choice(all_moods)
            books = MOOD_RECOMMENDATIONS[random_mood]
    
    # Format the recommendations
    recommendations = f"Based on your mood '{mood}', here are some recommendations:\n\n"
    for i, book in enumerate(books, 1):
        recommendations += f"{i}. '{book['title']}' by {book['author']}\n"
    
    return recommendations

# Book information (with fallback if AI not available)
def get_book_info(title):
    # Try to use Gemini if available
    if GEMINI_AVAILABLE:
        try:
            # Try different model names that might be available
            model_names = ['gemini-pro', 'gemini-1.5-pro', 'models/gemini-pro']
            
            for model_name in model_names:
                try:
                    model = genai.GenerativeModel(model_name)
                    prompt = f"Give me a brief summary and key information about the book '{title}'. Keep it to 100 words."
                    response = model.generate_content(prompt)
                    return response.text
                except Exception as e:
                    print(f"Failed with model {model_name}: {e}")
                    continue
        except Exception as e:
            print(f"Error using Gemini API: {e}")
    
    # Fallback information system
    # Check if we have info for this specific title
    for book_title, info in BOOK_INFO.items():
        if title.lower() in book_title.lower() or book_title.lower() in title.lower():
            return info
    
    # If not found, provide generic response
    return f"Information about '{title}' is not available in our local database. This book might be newer or less well-known. Consider checking online resources like Goodreads or Google Books for more information."

# Calculate fine amount
def calculate_fine(return_date, due_date):
    if return_date > due_date:
        days = (return_date - due_date).days
        return days * 5  # 5 rupees per day
    return 0

# Main Application
class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        self.current_user = None
        initialize_data()
        self.show_login_frame()
    
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_frame(self):
        self.clear_window()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True, fill="both")
        
        ttk.Label(frame, text="Library Management System", font=("Arial", 16, "bold")).pack(pady=20)
        
        ttk.Label(frame, text="Username:").pack(pady=5)
        self.username_entry = ttk.Entry(frame, width=30)
        self.username_entry.pack(pady=5)
        
        ttk.Label(frame, text="Password:").pack(pady=5)
        self.password_entry = ttk.Entry(frame, width=30, show="*")
        self.password_entry.pack(pady=5)
        
        ttk.Button(frame, text="Login", command=self.login).pack(pady=10)
        ttk.Button(frame, text="Register", command=self.show_register_frame).pack(pady=5)
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        users = load_data(USERS_FILE)
        
        if username in users and users[username]["password"] == password:
            self.current_user = username
            messagebox.showinfo("Login Successful", f"Welcome, {username}!")
            self.show_main_menu()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
    
    def show_register_frame(self):
        self.clear_window()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True, fill="both")
        
        ttk.Label(frame, text="Register New User", font=("Arial", 16, "bold")).pack(pady=20)
        
        ttk.Label(frame, text="Username:").pack(pady=5)
        self.reg_username = ttk.Entry(frame, width=30)
        self.reg_username.pack(pady=5)
        
        ttk.Label(frame, text="Password:").pack(pady=5)
        self.reg_password = ttk.Entry(frame, width=30, show="*")
        self.reg_password.pack(pady=5)
        
        ttk.Label(frame, text="Profile Picture:").pack(pady=5)
        self.profile_pic_path = tk.StringVar()
        ttk.Label(frame, textvariable=self.profile_pic_path).pack(pady=5)
        ttk.Button(frame, text="Browse...", command=self.browse_profile_pic).pack(pady=5)
        
        ttk.Button(frame, text="Register", command=self.register_user).pack(pady=10)
        ttk.Button(frame, text="Back to Login", command=self.show_login_frame).pack(pady=5)
    
    def browse_profile_pic(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if file_path:
            self.profile_pic_path.set(file_path)
    
    def register_user(self):
        username = self.reg_username.get()
        password = self.reg_password.get()
        profile_pic = self.profile_pic_path.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return
        
        users = load_data(USERS_FILE)
        
        if username in users:
            messagebox.showerror("Error", "Username already exists")
            return
        
        # Save profile picture
        pic_path = ""
        if profile_pic:
            ext = os.path.splitext(profile_pic)[1]
            dest = os.path.join(PROFILE_DIR, f"{username}{ext}")
            try:
                img = Image.open(profile_pic)
                img.thumbnail((200, 200))
                img.save(dest)
                pic_path = dest
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save profile picture: {str(e)}")
        
        # Add user
        users[username] = {"password": password, "profile_pic": pic_path, "role": "user"}
        save_data(users, USERS_FILE)
        
        messagebox.showinfo("Success", "Registration successful. You can now log in.")
        self.show_login_frame()
    
    def show_main_menu(self):
        self.clear_window()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True, fill="both")
        
        # Display profile picture if available
        users = load_data(USERS_FILE)
        pic_path = users[self.current_user].get("profile_pic", "")
        
        if pic_path and os.path.exists(pic_path):
            try:
                img = Image.open(pic_path)
                img.thumbnail((100, 100))
                photo = ImageTk.PhotoImage(img)
                label = ttk.Label(frame, image=photo)
                label.image = photo  # Keep a reference
                label.pack(pady=10)
            except Exception as e:
                print(f"Failed to load profile picture: {str(e)}")
        
        ttk.Label(frame, text=f"Welcome, {self.current_user}!", font=("Arial", 16, "bold")).pack(pady=10)
        
        buttons = [
            ("View Available Books", self.show_books),
            ("Get Book Recommendations", self.show_recommendation_page),
            ("Search Book Information", self.show_book_search),
            ("My Borrowed Books", self.show_borrowed_books),
            ("Logout", self.show_login_frame)
        ]
        
        # Add admin-only buttons
        if users[self.current_user].get("role") == "admin":
            buttons.insert(-1, ("Add New Book", self.show_add_book))
            buttons.insert(-1, ("Manage Returns", self.show_manage_returns))
        
        for text, command in buttons:
            ttk.Button(frame, text=text, width=30, command=command).pack(pady=8)
    
    def show_books(self):
        self.clear_window()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True, fill="both")
        
        ttk.Label(frame, text="Available Books", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Create Treeview
        columns = ("ID", "Title", "Author", "Genre", "Status")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Load books
        books = load_data(BOOKS_FILE)
        
        for book_id, book in books.items():
            status = "Available" if book["available"] else "Borrowed"
            tree.insert("", "end", values=(book_id, book["title"], book["author"], book["genre"], status))
        
        tree.pack(pady=20, fill="both", expand=True)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Borrow Book", command=lambda: self.borrow_book(tree)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Back to Menu", command=self.show_main_menu).pack(side="left", padx=5)
    
    def borrow_book(self, tree):
        selection = tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a book to borrow")
            return
        
        book_id = tree.item(selection[0])["values"][0]
        
        books = load_data(BOOKS_FILE)
        issues = load_data(ISSUES_FILE)
        
        if not books[book_id]["available"]:
            messagebox.showerror("Error", "This book is not available for borrowing")
            return
        
        # Set book as borrowed
        books[book_id]["available"] = False
        save_data(books, BOOKS_FILE)
        
        # Record issue
        issue_date = datetime.datetime.now()
        due_date = issue_date + timedelta(days=14)  # 2 weeks
        
        if self.current_user not in issues:
            issues[self.current_user] = {}
        
        issues[self.current_user][book_id] = {
            "issue_date": issue_date.strftime("%Y-%m-%d"),
            "due_date": due_date.strftime("%Y-%m-%d"),
            "returned": False
        }
        
        save_data(issues, ISSUES_FILE)
        messagebox.showinfo("Success", f"Book borrowed successfully. Due date: {due_date.strftime('%Y-%m-%d')}")
        self.show_books()
    
    def show_recommendation_page(self):
        self.clear_window()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True, fill="both")
        
        ttk.Label(frame, text="Book Recommendations", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(frame, text="How are you feeling today?").pack(pady=5)
        
        mood_entry = ttk.Entry(frame, width=30)
        mood_entry.pack(pady=10)
        
        result_text = tk.Text(frame, height=15, width=70, wrap=tk.WORD)
        result_text.pack(pady=10)
        result_text.config(state=tk.DISABLED)
        
        def get_recommendations():
            mood = mood_entry.get()
            if not mood:
                messagebox.showerror("Error", "Please enter your mood")
                return
            
            result_text.config(state=tk.NORMAL)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, "Getting recommendations...\n\n")
            result_text.config(state=tk.DISABLED)
            self.root.update()
            
            recommendations = get_book_recommendations(mood)
            
            result_text.config(state=tk.NORMAL)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, recommendations)
            result_text.config(state=tk.DISABLED)
        
        ttk.Button(frame, text="Get Recommendations", command=get_recommendations).pack(pady=10)
        ttk.Button(frame, text="Back to Menu", command=self.show_main_menu).pack(pady=5)
    
    def show_book_search(self):
        self.clear_window()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True, fill="both")
        
        ttk.Label(frame, text="Search Book Information", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(frame, text="Enter Book Title:").pack(pady=5)
        
        title_entry = ttk.Entry(frame, width=30)
        title_entry.pack(pady=10)
        
        result_text = tk.Text(frame, height=15, width=70, wrap=tk.WORD)
        result_text.pack(pady=10)
        result_text.config(state=tk.DISABLED)
        
        def search_book():
            title = title_entry.get()
            if not title:
                messagebox.showerror("Error", "Please enter a book title")
                return
            
            result_text.config(state=tk.NORMAL)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, "Searching...\n\n")
            result_text.config(state=tk.DISABLED)
            self.root.update()
            
            info = get_book_info(title)
            
            result_text.config(state=tk.NORMAL)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, info)
            result_text.config(state=tk.DISABLED)
        
        ttk.Button(frame, text="Search", command=search_book).pack(pady=10)
        ttk.Button(frame, text="Back to Menu", command=self.show_main_menu).pack(pady=5)
    
    def show_borrowed_books(self):
        self.clear_window()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True, fill="both")
        
        ttk.Label(frame, text="My Borrowed Books", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Create Treeview
        columns = ("Book ID", "Title", "Issue Date", "Due Date", "Status")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Load books and issues
        books = load_data(BOOKS_FILE)
        issues = load_data(ISSUES_FILE)
        
        user_issues = issues.get(self.current_user, {})
        
        for book_id, issue in user_issues.items():
            if book_id in books:
                status = "Returned" if issue["returned"] else "Borrowed"
                tree.insert("", "end", values=(
                    book_id, 
                    books[book_id]["title"], 
                    issue["issue_date"], 
                    issue["due_date"], 
                    status
                ))
        
        tree.pack(pady=20, fill="both", expand=True)
        ttk.Button(frame, text="Back to Menu", command=self.show_main_menu).pack(pady=10)
    
    def show_add_book(self):
        self.clear_window()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True, fill="both")
        
        ttk.Label(frame, text="Add New Book", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Book details
        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=10)
        
        fields = ["Book ID", "Title", "Author", "Genre"]
        entries = {}
        
        for i, field in enumerate(fields):
            ttk.Label(form_frame, text=f"{field}:").grid(row=i, column=0, sticky="w", pady=5)
            entries[field] = ttk.Entry(form_frame, width=30)
            entries[field].grid(row=i, column=1, pady=5, padx=10)
        
        def add_book():
            book_data = {field: entries[field].get() for field in fields}
            
            if not all(book_data.values()):
                messagebox.showerror("Error", "All fields are required")
                return
            
            books = load_data(BOOKS_FILE)
            
            if book_data["Book ID"] in books:
                messagebox.showerror("Error", "Book ID already exists")
                return
            
            books[book_data["Book ID"]] = {
                "title": book_data["Title"],
                "author": book_data["Author"],
                "genre": book_data["Genre"],
                "available": True
            }
            
            save_data(books, BOOKS_FILE)
            messagebox.showinfo("Success", "Book added successfully")
            
            # Clear entries
            for entry in entries.values():
                entry.delete(0, tk.END)
        
        ttk.Button(frame, text="Add Book", command=add_book).pack(pady=10)
        ttk.Button(frame, text="Back to Menu", command=self.show_main_menu).pack(pady=5)
    
    def show_manage_returns(self):
        self.clear_window()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True, fill="both")
        
        ttk.Label(frame, text="Manage Book Returns", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Create Treeview
        columns = ("User", "Book ID", "Title", "Issue Date", "Due Date")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Load books and issues
        books = load_data(BOOKS_FILE)
        issues = load_data(ISSUES_FILE)
        
        for user, user_issues in issues.items():
            for book_id, issue in user_issues.items():
                if not issue["returned"] and book_id in books:
                    tree.insert("", "end", values=(
                        user,
                        book_id, 
                        books[book_id]["title"], 
                        issue["issue_date"], 
                        issue["due_date"]
                    ))
        
        tree.pack(pady=20, fill="both", expand=True)
        
        def process_return():
            selection = tree.selection()
            if not selection:
                messagebox.showerror("Error", "Please select a book")
                return
            
            values = tree.item(selection[0])["values"]
            user = values[0]
            book_id = values[1]
            
            # Update book status
            books = load_data(BOOKS_FILE)
            issues = load_data(ISSUES_FILE)
            
            if book_id in books:
                books[book_id]["available"] = True
            
            # Calculate fine if any
            due_date = datetime.datetime.strptime(issues[user][book_id]["due_date"], "%Y-%m-%d")
            return_date = datetime.datetime.now()
            fine = calculate_fine(return_date, due_date)
            
            # Update issue record
            issues[user][book_id]["returned"] = True
            issues[user][book_id]["return_date"] = return_date.strftime("%Y-%m-%d")
            issues[user][book_id]["fine"] = fine
            
            save_data(books, BOOKS_FILE)
            save_data(issues, ISSUES_FILE)
            
            fine_message = f"Fine: {fine} rupees" if fine > 0 else "No fine"
            messagebox.showinfo("Success", f"Book returned successfully. {fine_message}")
            self.show_manage_returns()
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Process Return", command=process_return).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Back to Menu", command=self.show_main_menu).pack(side="left", padx=5)

# Main entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()
