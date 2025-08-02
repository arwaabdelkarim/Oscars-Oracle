import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from db import insert_user, check_credentials, user_exists

try:
    from tkcalendar import DateEntry
    HAS_TKCALENDAR = True
except ImportError:
    HAS_TKCALENDAR = False
import sys, os

# main_menu.py
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import font

menu_options = [
    "➕ Add a new nomination",
    "👁️ View my nominations",
    "👁️ View the top nominated movies by the system users",
    "🔎 See total nominations and oscars for a person",
    "🌍 Top 5 birth countries for Best Leading Actor Award Winners",
    "🔎 See all the nominated staff members born in a given country",
    "👁️ Living Dream Team",
    "👁️ Top 5 production companies by the number of won Oscars",
    "🌍🎬 List all non-english speaking movies that ever won an oscar, along with the year"
]

def menu_action(index,root,bg_photo,username):
    if index == 0:  # "Add a new user nomination..."
        open_movie_nomination_window(root, bg_photo, username)
    elif index == 1:
        open_user_nominations_window(root, bg_photo, username)
    elif index == 2:
        open_top_nominated_movies_window(root, bg_photo)
    elif index == 3:  # First option - Add nomination
        open_nomination_window(root, bg_photo)
    elif index == 4:
        open_top_5_birth_countries_window(root, bg_photo)
    elif index == 5:
        open_staff_by_country_window(root, bg_photo)
    elif index == 6:
        open_dream_team_window(root, bg_photo)
    elif index == 7:
        open_top_production_companies_window(root, bg_photo)
    elif index == 8:
        open_non_english_oscar_winners_window(root, bg_photo)


def perform_search(search_text, results_box, status_label):
    from db import search_staff

    try:
        staff_members = search_staff(search_text)
        results_box.delete(0, tk.END)

        if staff_members:
            for staff in staff_members:
                fname, lname = staff
                results_box.insert(tk.END, f"{fname} {lname}")
        else:
            if status_label:
                status_label.config(text="No matching staff found")

    except Exception as e:
        if status_label:
            status_label.config(text=f"Search error: {str(e)}")
search_after_id = None

def update_search_results(search_var, results_box, status_label=None, parent_window=None):
    global search_after_id
    search_text = search_var.get().strip()

    # Cancel previous scheduled search
    if search_after_id and parent_window:
        parent_window.after_cancel(search_after_id)

    # Clear results and show initial message
    results_box.delete(0, tk.END)

    if len(search_text) < 3:
        if status_label:
            status_label.config(text="")
        return


    # Schedule new search with 300ms delay
    search_after_id = parent_window.after(300, lambda:
    perform_search(search_text, results_box, status_label))

def display_nomination_details(event, results_box, tree, count_label):
    from db import get_staff_nomination

    # Clear previous data
    for item in tree.get_children():
        tree.delete(item)

    # Get selected staff
    selected_indices = results_box.curselection()
    if not selected_indices:
        return

    selected_text = results_box.get(selected_indices[0])

    name_parts = selected_text.split(" ")
    if len(name_parts) < 2:
        return

    fname = name_parts[0]

    # Handle various formatting possibilities
    if "(" in selected_text:
        # Extract last name before the parenthesis
        lname_part = selected_text.split("(")[0].strip()
        lname = " ".join(lname_part.split(" ")[1:])
    elif "-" in selected_text:
        # Extract last name before the dash
        lname_part = selected_text.split("-")[0].strip()
        lname = " ".join(lname_part.split(" ")[1:])
    else:
        # Just get everything after the first name
        lname = " ".join(name_parts[1:])

    data = get_staff_nomination(fname, lname)
    count_label.config(
        text=f"Total Nominations: {data['total_nominations']} | Oscars Won: {data['total_oscars']}"
    )

    # Clear previous data
    for item in tree.get_children():
        tree.delete(item)

    # Populate tree with nominations
    for nom in data['nominations']:
        tree.insert('', tk.END, values=nom)


def select_staff_member(event, results_box, entry, window):
    selected_indices = results_box.curselection()
    if not selected_indices:
        return

    selected = results_box.get(selected_indices[0])

    # Extract name for further processing
    name_parts = selected.split(" ")
    fname = name_parts[0]
    lname = " ".join(name_parts[1:]).split("(")[0].strip() if "(" in selected else " ".join(name_parts[1:])



def create_search_interface(parent_frame, window):
    # Frame for search bar
    search_container = tk.Frame(parent_frame, bg="#d6c97a")
    search_container.pack(fill="x", padx=20, pady=10)

    tk.Label(search_container, text="Staff Name:", font=("Arial", 12),
             bg="#d6c97a", fg="#000000").pack(side=tk.LEFT, padx=(0, 10))

    # Variable to track input
    search_var = tk.StringVar()
    search_var.trace("w", lambda name, index, mode, sv=search_var: update_search_results(sv, results_box, None, window))

    # Create search entry
    search_entry = tk.Entry(search_container, textvariable=search_var,
                            font=("Arial", 12), width=30)
    search_entry.pack(side=tk.LEFT)
    search_entry.focus_set()

    # Create listbox for results
    results_frame = tk.Frame(parent_frame, bg="#d6c97a")
    results_frame.pack(fill="both", expand=True, padx=20, pady=(5, 10))

    # Scrollbar for results
    scrollbar = tk.Scrollbar(results_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    results_box = tk.Listbox(results_frame, width=60, height=8,
                             font=("Arial", 11),
                             bg="#d6c97a",
                             yscrollcommand=scrollbar.set)
    results_box.pack(fill="both", expand=True)
    scrollbar.config(command=results_box.yview)

    # Treeview style for nomination output
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview",
                    background="#d6c97a",
                    fieldbackground="#d6c97a",
                    rowheight=25)
    style.configure("Custom.Treeview.Heading",
                    background="#d6c97a",
                    foreground="#000000",
                    font=("Arial", 10, "bold"))
    # Frame for nomination details
    details_frame = tk.Frame(parent_frame, bg="#d6c97a")
    details_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Label for nomination count
    nomination_count = tk.Label(details_frame, text="Total Nominations: 0",
                                font=("Arial", 12, "bold"), bg="#d6c97a", fg="#000000")
    nomination_count.pack(anchor="w")

    # Table for nomination records
    columns = ('Movie Name', 'Release Year', 'Iteration', 'Category', 'Won')
    tree = ttk.Treeview(details_frame, columns=columns, show='headings', height=6, style="Custom.Treeview")


    for col in columns:
        tree.heading(col, text=col.title())
        tree.column(col, width=100, anchor='center')

    tree.pack(fill="both", expand=True, pady=5)

    # Bind selection event
    results_box.bind('<<ListboxSelect>>',
                     lambda event: display_nomination_details(event, results_box, tree, nomination_count))

    # Double-click to select
    results_box.bind('<Double-1>',
                     lambda event: select_staff_member(event, results_box, search_entry, window))


def open_nomination_window(root, bg_photo):
    # Create a new top-level window
    nom_window = tk.Toplevel(root)
    nom_window.title("Add New User Nomination")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    nom_window.geometry(f"{screen_width}x{screen_height}+0+0")

    # Use the same Oscar background
    canvas = tk.Canvas(nom_window, width=800, height=600, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    # Create a WIDER yellow frame (increased width from 500 to 650)
    search_frame = tk.Frame(nom_window, bg="#d6c97a", bd=2, relief="solid")
    search_frame.place(relx=0.5, rely=0.5, anchor="center", width=1200, height=800)

    # Add title
    tk.Label(search_frame, text="Search for Staff Member", font=("Arial", 16, "bold"),
             bg="#d6c97a", fg="#000000").pack(pady=10)

    # Create search box and results display
    create_search_interface(search_frame, nom_window)

    # Keep reference to prevent garbage collection
    nom_window.bg_photo = bg_photo


def open_movie_nomination_window(root, bg_photo, username):
    """Open window to search for actors by movie name and add nominations"""
    # Create new window
    nom_window = tk.Toplevel(root)
    nom_window.title("Add Nomination")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    nom_window.geometry(f"{screen_width}x{screen_height}+0+0")

    # Set background
    canvas = tk.Canvas(nom_window, width=900, height=600, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    # Create gold frame
    movie_frame = tk.Frame(nom_window, bg="#d6c97a", bd=2, relief="solid")
    movie_frame.place(relx=0.5, rely=0.5, anchor="center", width=1200, height=700)


    # Create interface
    create_movie_search_interface(movie_frame, nom_window, username)

    # Keep reference to prevent garbage collection
    nom_window.bg_photo = bg_photo


def create_movie_search_interface(parent_frame, window, username):
    """Create the search interface for movies and actors"""
    # Frame for search bar
    search_container = tk.Frame(parent_frame, bg="#d6c97a")
    search_container.pack(fill="x", padx=20, pady=10)

    tk.Label(search_container, text="Movie Name:", font=("Arial", 12),
             bg="#d6c97a", fg="#000000").pack(side=tk.LEFT, padx=(0, 10))

    # Create search entry
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_container, textvariable=search_var,
                            font=("Arial", 12), width=30)
    search_entry.pack(side=tk.LEFT)
    search_entry.focus_set()

    # Status label
    status_label = tk.Label(search_container,
                            font=("Arial", 10, "italic"), bg="#d6c97a", fg="#444444")
    status_label.pack(side=tk.LEFT, padx=(10, 0))

    # Search button
    search_button = tk.Button(search_container, text="Search",
                              font=("Arial", 10, "bold"), bg="#000000", fg="#ffffff",
                              command=lambda: perform_movie_search(search_var.get(), results_tree, status_label))
    search_button.pack(side=tk.RIGHT, padx=(0, 10))

    # Frame for results
    results_frame = tk.Frame(parent_frame, bg="#d6c97a")
    results_frame.pack(fill="both", expand=True, padx=20, pady=(5, 10))

    # Set up treeview style
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Custom.Treeview",
                    background="#d6c97a",
                    fieldbackground="#d6c97a",
                    rowheight=25)
    style.configure("Custom.Treeview.Heading",
                    background="#d6c97a",
                    foreground="#000000",
                    font=("Arial", 10, "bold"))

    # Table for movie actor results
    columns = ('Movie Name', 'Release Year', 'Iteration', 'Category', 'First Name', 'Last Name')
    results_tree = ttk.Treeview(results_frame, columns=columns, show='headings',
                                height=12, style="Custom.Treeview")

    # Configure columns
    for col in columns:
        results_tree.heading(col, text=col)
        results_tree.column(col, width=85, anchor='center')

    results_tree.pack(fill="both", expand=True, pady=5)

    # Nominate button
    button_frame = tk.Frame(parent_frame, bg="#d6c97a")
    button_frame.pack(fill="x", padx=20, pady=10)

    nominate_button = tk.Button(button_frame, text="Nominate Selected",
                                font=("Arial", 12, "bold"), bg="#000000", fg="#ffffff",
                                command=lambda: nominate_selected(results_tree, username, status_label, window))
    nominate_button.pack(side=tk.RIGHT, padx=10)


def perform_movie_search(movie_name, results_tree, status_label):
    """Search for movie and display results"""
    from db import search_movie

    # Clear previous results
    for item in results_tree.get_children():
        results_tree.delete(item)

    if len(movie_name) < 2:
        status_label.config(text="")
        return
    try:
        results = search_movie(movie_name)

        if results:
            # Populate tree
            for row in results:
                if len(row) == 6:
                    results_tree.insert('', tk.END, values=row)
                else:
                    print("", row)

        else:
            status_label.config(text="No movies found with that name")

    except Exception as e:
        status_label.config(text=f"Error: {str(e)}")


def nominate_selected(results_tree, username, status_label, window):
    """Add the selected nomination to the usernom table"""
    from db import add_user_nomination

    # Get selected item
    selected_items = results_tree.selection()
    if not selected_items:
        status_label.config(text="Please select a nomination to add")
        return

    # Get values from selected row
    values = results_tree.item(selected_items[0], 'values')
    if not values or len(values) < 6:
        status_label.config(text="")
        return

    movie_name = values[0]
    release_year = values[1]
    iteration = values[2]
    category = values[3]
    fname = values[4]
    lname = values[5]

    # Add to database
    success = add_user_nomination(username, movie_name, release_year, iteration, category, fname, lname)

    if success:
        status_label.config(text=f"Successfully added nomination!")
        # tk.messagebox.showinfo("Success", f"Nomination added for {fname} {lname} in {movie_name}")
    else:
        status_label.config(text="Error adding nomination to database")
        tk.messagebox.showerror("Error", "Failed to add nomination to database")

def open_user_nominations_window(root, bg_photo, username):
    nom_window = tk.Toplevel(root)
    nom_window.title("My Nominations")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    nom_window.geometry(f"{screen_width}x{screen_height}+0+0")

    canvas = tk.Canvas(nom_window, width=800, height=500, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    frame = tk.Frame(nom_window, bg="#d6c97a", bd=2, relief="solid")
    frame.place(relx=0.5, rely=0.5, anchor="center", width=1200, height=800)

    tk.Label(frame, text="My Nominations", font=("Arial", 16, "bold"),
             bg="#d6c97a", fg="#000000").pack(pady=10)

    # Table for nominations
    columns = ('Movie Name', 'Release Year', 'Iteration', 'Category', 'First Name', 'Last Name')
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Custom.Treeview",
                    background="#d6c97a",
                    fieldbackground="#d6c97a",
                    rowheight=25)
    style.configure("Custom.Treeview.Heading",
                    background="#d6c97a",
                    foreground="#000000",
                    font=("Arial", 10, "bold"))

    tree = ttk.Treeview(frame, columns=columns, show='headings', height=12, style="Custom.Treeview")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor='center')
    tree.pack(fill="both", expand=True, pady=5)

    # Fetch and display the user's nominations
    from db import get_user_nominations
    nominations = get_user_nominations(username)
    for nom in nominations:
        tree.insert('', tk.END, values=nom)

    nom_window.bg_photo = bg_photo  # Prevent garbage collection

def open_top_nominated_movies_window(root, bg_photo):
    from db import get_all_nominated_categories
    win = tk.Toplevel(root)
    win.title("Top Nominated Movies")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    win.geometry(f"{screen_width}x{screen_height}+0+0")

    canvas = tk.Canvas(win, width=1000, height=600, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    frame = tk.Frame(win, bg="#d6c97a", bd=2, relief="solid")
    frame.place(relx=0.5, rely=0.5, anchor="center", width=1200, height=800)

    tk.Label(frame, text="Top Nominated Movies by Category / Year", font=("Arial", 16, "bold"),
             bg="#d6c97a", fg="#000000").pack(pady=10)

    # Filter controls
    filter_frame = tk.Frame(frame, bg="#d6c97a")
    filter_frame.pack(pady=10)

    # Iteration (year) entry
    tk.Label(filter_frame, text="Iteration (Year):", bg="#d6c97a").pack(side=tk.LEFT)
    iteration_var = tk.StringVar()
    iteration_entry = tk.Entry(filter_frame, textvariable=iteration_var, width=10)
    iteration_entry.pack(side=tk.LEFT, padx=5)

    # Category dropdown
    tk.Label(filter_frame, text="Category:", bg="#d6c97a").pack(side=tk.LEFT)
    category_var = tk.StringVar()
    category_combo = ttk.Combobox(filter_frame, textvariable=category_var, width=25)
    category_combo['values'] = get_all_nominated_categories()  # See db.py below
    category_combo.pack(side=tk.LEFT, padx=5)

    # Show button
    show_btn = tk.Button(filter_frame, text="Show", bg="#000000", fg="white",
                         command=lambda: update_top_movies_table(tree, iteration_var.get(), category_var.get()))
    show_btn.pack(side=tk.LEFT, padx=10)

    # Results table
    columns = ('Nominations','Movie Name','ReleaseYear', 'Iteration', 'Category')
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Custom.Treeview",
                    background="#d6c97a",
                    fieldbackground="#d6c97a",
                    rowheight=25)
    style.configure("Custom.Treeview.Heading",
                    background="#d6c97a",
                    foreground="#000000",
                    font=("Arial", 10, "bold"))

    tree = ttk.Treeview(frame, columns=columns, show='headings', height=12, style="Custom.Treeview")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=180, anchor='center')
    tree.pack(fill="both", expand=True, padx=10, pady=5)

    # Initial load (show all)
    update_top_movies_table(tree, '', '')

    win.bg_photo = bg_photo  # Prevent garbage collection

def update_top_movies_table(tree, iteration, category):
    from db import get_top_nominated_movies
    # Clear previous results
    for item in tree.get_children():
        tree.delete(item)
    # Get new results
    results = get_top_nominated_movies(iteration, category)
    # Insert into treeview
    for row in results:
        tree.insert('', tk.END, values=row)

def open_top_5_birth_countries_window(root, bg_photo):
    from db import get_top_5_birth_countries
    win = tk.Toplevel(root)
    win.title("Top 5 Birth Countries for Best Actor Winners")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    win.geometry(f"{screen_width}x{screen_height}+0+0")

    canvas = tk.Canvas(win, width=800, height=400, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    frame = tk.Frame(win, bg="#d6c97a", bd=2, relief="solid")
    frame.place(relx=0.5, rely=0.5, anchor="center", width=800, height=300)

    tk.Label(frame, text="Top 5 Birth Countries for Best Leading Actor Award Winners", font=("Arial", 16, "bold"),
             bg="#d6c97a", fg="#000000").pack(pady=20)

    # Table with one column
    columns = ('Country',)
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Custom.Treeview",
                    background="#d6c97a",
                    fieldbackground="#d6c97a",
                    rowheight=30)
    style.configure("Custom.Treeview.Heading",
                    background="#d6c97a",
                    foreground="#000000",
                    font=("Arial", 12, "bold"))

    tree = ttk.Treeview(frame, columns=columns, show='headings', height=5, style="Custom.Treeview")
    tree.heading('Country', text='Country')
    tree.column('Country', width=300, anchor='center')
    tree.pack(fill="both", expand=True, pady=10)

    # Fetch and display results
    countries = get_top_5_birth_countries()
    for country in countries:
        tree.insert('', tk.END, values=(country,))

    win.bg_photo = bg_photo  # Prevent garbage collection

def open_staff_by_country_window(root, bg_photo):
    from db import get_countries_and_staff_data
    win = tk.Toplevel(root)
    win.title("Staff Nominated by Country")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    win.geometry(f"{screen_width}x{screen_height}+0+0")

    canvas = tk.Canvas(win, width=900, height=500, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    frame = tk.Frame(win, bg="#d6c97a", bd=2, relief="solid")
    frame.place(relx=0.5, rely=0.5, anchor="center", width=900, height=800)

    tk.Label(frame, text="Select a Country", font=("Arial", 16, "bold"),
             bg="#d6c97a", fg="#000000").pack(pady=10)

    # Country entry
    entry_frame = tk.Frame(frame, bg="#d6c97a")
    entry_frame.pack()
    tk.Label(entry_frame, text="Country:", bg="#d6c97a").pack(side=tk.LEFT)

    # Table
    columns = ('First Name', 'Last Name', 'Categories', 'Nominations', 'Oscars')
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Custom.Treeview",
                    background="#d6c97a",
                    fieldbackground="#d6c97a",
                    rowheight=60)
    style.configure("Custom.Treeview.Heading",
                    background="#d6c97a",
                    foreground="#000000",
                    font=("Arial", 10, "bold"))

    tree = ttk.Treeview(frame, columns=columns, show='headings', height=12, style="Custom.Treeview")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=130, anchor='center')
    tree.pack(fill="both", expand=True, pady=5)

    # Get countries for the dropdown using the combined function
    data = get_countries_and_staff_data()
    countries = data["countries"]

    # Create the dropdown with countries
    country_var = tk.StringVar()
    country_combo = ttk.Combobox(entry_frame, textvariable=country_var, width=20, values=countries)
    country_combo.pack(side=tk.LEFT, padx=5)

    # When a country is selected, get the data
    def show_results(event=None):
        selected_country = country_var.get()

        # Clear previous results
        for item in tree.get_children():
            tree.delete(item)

        if not selected_country:
            return

        # Explicitly set the combobox value to ensure it displays
        country_combo.set(selected_country)

        # Get staff data using the same function with country parameter
        data = get_countries_and_staff_data(selected_country)
        staff_data = data["staff_data"]

        for row in staff_data:
            # Format categories with newlines for wrapping
            formatted_row = list(row)
            if formatted_row[2]:
                formatted_row[2] = formatted_row[2].replace(',', '\n')
            tree.insert('', tk.END, values=formatted_row)

    # Bind dropdown selection to show results
    country_combo.bind("<<ComboboxSelected>>", show_results)


def open_dream_team_window(root, bg_photo):
    from db import get_dream_team

    win = tk.Toplevel(root)
    win.title("Dream Team - Best Movie Ever Cast")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    win.geometry(f"{screen_width}x{screen_height}+0+0")

    canvas = tk.Canvas(win, width=900, height=600, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    frame = tk.Frame(win, bg="#d6c97a", bd=2, relief="solid")
    frame.place(relx=0.5, rely=0.5, anchor="center", width=800, height=400)

    dream_team = get_dream_team()

    # Display results
    output_frame = tk.Frame(frame, bg="#d6c97a")
    output_frame.place(relx=0.5, rely=0.5, anchor='center')

    tk.Label(output_frame, text="Dream Team", font=("Arial", 20, "bold"),
             bg="#d6c97a", fg="#000000").pack(pady=(0, 20))

    roles = ["Director", "Leading Actor", "Leading Actress", "Supporting Actor",
             "Supporting Actress", "Producer", "Singer"]


    for i, role in enumerate(roles):
        role_frame = tk.Frame(output_frame, bg="#d6c97a")
        role_frame.pack(pady=5, anchor='center')

        tk.Label(role_frame, text=f"{role}:", width=15, anchor="e",
                 bg="#d6c97a", font=("Arial", 12, "bold", "underline")).pack(side=tk.LEFT, padx=5)

        if i < len(dream_team) and dream_team[i]:
            name = f"{dream_team[i][0]} {dream_team[i][1]}"
            wins = f"({dream_team[i][2]} Oscar{'s' if dream_team[i][2] > 1 else ''})"
            tk.Label(role_frame, text=f"{name} {wins}",
                     bg="#d6c97a", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        else:
            tk.Label(role_frame, text="No living winner found",
                     bg="#d6c97a", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)

    win.bg_photo = bg_photo  # Prevent garbage collection


def open_top_production_companies_window(root, bg_photo):
    from db import get_top_production_companies

    win = tk.Toplevel(root)
    win.title("Top Production Companies by Oscar Wins")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    win.geometry(f"{screen_width}x{screen_height}+0+0")

    canvas = tk.Canvas(win, width=900, height=600, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    frame = tk.Frame(win, bg="#d6c97a", bd=2, relief="solid")
    frame.place(relx=0.5, rely=0.5, anchor="center", width=800, height=300)

    tk.Label(frame, text="Top 5 Production Companies by the Number of Oscars Won",
             font=("Arial", 16, "bold"), bg="#d6c97a", fg="#000000").pack(pady=10)

    # Create a Treeview widget
    columns = ('Production Company', 'Oscars Won')
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Custom.Treeview",
                    background="#d6c97a",
                    fieldbackground="#d6c97a",
                    rowheight=30)
    style.configure("Custom.Treeview.Heading",
                    background="#d6c97a",
                    foreground="#000000",
                    font=("Arial", 12, "bold"))

    tree = ttk.Treeview(frame, columns=columns, show='headings', height=5, style="Custom.Treeview")
    for col in columns:
        tree.heading(col, text=col)

    tree.column('Production Company', width=400, anchor='center')
    tree.column('Oscars Won', width=200, anchor='center')

    tree.pack(pady=20)

    # Get the data and populate the tree
    companies = get_top_production_companies()

    for i, company in enumerate(companies):
        tree.insert('', tk.END, values=(company[0], company[1]))

    win.bg_photo = bg_photo  # Prevent garbage collection

def open_non_english_oscar_winners_window(root, bg_photo):
    from db import get_non_english_movies

    win = tk.Toplevel(root)
    win.title("Non-English Oscar-Winning Movies")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    win.geometry(f"{screen_width}x{screen_height}+0+0")

    canvas = tk.Canvas(win, width=700, height=500, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    frame = tk.Frame(win, bg="#d6c97a", bd=2, relief="solid")
    frame.place(relx=0.5, rely=0.5, anchor="center", width=1200, height=800)

    tk.Label(frame, text="Non-English Speaking Oscar-Winning Movies", font=("Arial", 16, "bold"),
             bg="#d6c97a", fg="#000000").pack(pady=10)

    columns = ('Movie Name', 'Release Year', 'Iteration')
    style = ttk.Style()
    style.theme_use('clam')  # 'clam' is best for custom colors

    style.configure("Custom.Treeview",
                    background="#d6c97a",
                    fieldbackground="#d6c97a",
                    foreground="black",
                    rowheight=30
                    )
    style.configure("Custom.Treeview.Heading",
                    background="#d6c97a",
                    foreground="black",
                    font=("Arial", 12, "bold")
                    )
    tree = ttk.Treeview(frame, columns=columns, show='headings', height=15, style="Custom.Treeview")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=180 if col == 'Movie Name' else 80, anchor='center')
    tree.pack(fill="both", expand=True, pady=10)

    results = get_non_english_movies()
    for row in results:
        tree.insert('', tk.END, values=row)

    win.bg_photo = bg_photo  # Prevent garbage collection


def show_main_menu(root, bg_photo,username):
    # Remove all widgets from root
    for widget in root.winfo_children():
        widget.place_forget()
        widget.pack_forget()
        widget.grid_forget()
    menu_canvas = tk.Canvas(root, width=root.winfo_width(), height=root.winfo_height(), highlightthickness=0, bg="#222222")
    menu_canvas.place(x=0, y=0, relwidth=1, relheight=1)
    menu_canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    # Grid setup
    cols, rows = 3, 3
    spacing = 60
    margin_x = 60
    margin_y = 100
    canvas_width = root.winfo_width()
    canvas_height = root.winfo_height()

    rect_width = (canvas_width - 2 * margin_x - (cols - 1) * spacing) // cols
    rect_height = (canvas_height - 2 * margin_y - (rows - 1) * spacing) // rows

    for i, option in enumerate(menu_options):
        row = i // cols
        col = i % cols
        x0 = margin_x + col * (rect_width + spacing)
        y0 = margin_y + row * (rect_height + spacing)
        x1 = x0 + rect_width
        y1 = y0 + rect_height

        rect = menu_canvas.create_rectangle(
            x0, y0, x1, y1,
            fill="#d6c97a", outline="#000000", width=2, tags=(f"rect{i}", "menu_rect")
        )
        text = menu_canvas.create_text(
            (x0 + x1) // 2, (y0 + y1) // 2,
            text=option, font=("Arial", 13, "bold"), fill="#222222",
            width=rect_width-30, tags=(f"text{i}",)
        )
        # Bind click to rectangle and text
        menu_canvas.tag_bind(rect, "<Button-1>", lambda e, idx=i: menu_action(idx, root, bg_photo, username))
        menu_canvas.tag_bind(text, "<Button-1>", lambda e, idx=i: menu_action(idx, root, bg_photo, username))

    menu_canvas.bg_photo = bg_photo  # Prevent garbage collection

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Country list (full) ---
countries = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua & Deps", "Argentina",
    "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh",
    "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia Herzegovina",
    "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina", "Burundi", "Cambodia", "Cameroon",
    "Canada", "Cape Verde", "Central African Rep", "Chad", "Chile", "China", "Colombia",
    "Comoros", "Congo", "Congo {Democratic Rep}", "Costa Rica", "Croatia", "Cuba", "Cyprus",
    "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "East Timor",
    "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia",
    "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece",
    "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hungary",
    "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy", "Ivory Coast",
    "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea North", "Korea South",
    "Kosovo", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya",
    "Liechtenstein", "Lithuania", "Luxembourg", "Macedonia", "Madagascar", "Malawi", "Malaysia",
    "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico",
    "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique",
    "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger",
    "Nigeria", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay",
    "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russian Federation",
    "Rwanda", "St Kitts & Nevis", "St Lucia", "Saint Vincent & the Grenadines", "Samoa",
    "San Marino", "Sao Tome & Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles",
    "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia",
    "South Africa", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Swaziland",
    "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Togo",
    "Tonga", "Trinidad & Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda",
    "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay",
    "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
]

# --- Utility ---
def clear_form():
    for widget in form_frame.winfo_children():
        widget.destroy()

# --- Show Login Form ---
def show_login():
    clear_form()
    back_arrow.place_forget()
    form_frame.config(width=350, height=320)
    form_frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(form_frame, text="👤 username:", font=("Arial", 16, "bold"),
             fg="#000000", bg="#d6c97a", anchor="w").pack(pady=(20, 5))
    username_entry = tk.Entry(form_frame, font=("Arial", 16), width=28,
                              bg="#ffffff", fg="#000000", insertbackground="#000000",
                              insertofftime=300, insertontime=600, relief="flat")
    username_entry.pack(pady=(0, 15))
    username_entry.focus_set()

    tk.Label(form_frame, text="🔑 password:", font=("Arial", 16, "bold"),
             fg="#000000", bg="#d6c97a", anchor="w").pack(pady=(0, 5))
    password_entry = tk.Entry(form_frame, font=("Arial", 16), show="*", width=28,
                              bg="#ffffff", fg="#000000", insertbackground="#000000",
                              insertofftime=300, insertontime=600, relief="flat")
    password_entry.pack(pady=(0, 15))

    def handle_login():
        username = username_entry.get()
        password = password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return
        user = check_credentials(username, password)
        if user:
            show_main_menu(root, bg_photo,username)
            def on_resize(event):
                if hasattr(root, "menu_canvas") and root.menu_canvas.winfo_ismapped():
                    show_main_menu(root, bg_photo,username)

            root.bind("<Configure>", on_resize)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    tk.Button(form_frame, text="Login", font=("Arial", 14, "bold"),
              bg="#000000", fg="#ffffff", width=20,
              command=handle_login, relief="flat").pack(pady=(20, 25))

    link_frame = tk.Frame(form_frame, bg="#d6c97a")
    link_frame.pack(pady=(0, 15))
    tk.Label(link_frame, text="New User?", font=("Arial", 10),
             fg="#000000", bg="#d6c97a").pack(side="left")

    def on_enter(e): signup_label.config(font=("Arial", 10, "underline"), fg="#4a90e2")
    def on_leave(e): signup_label.config(font=("Arial", 10), fg="#4a90e2")

    signup_label = tk.Label(link_frame, text="SignUp", font=("Arial", 10),
                            fg="#4a90e2", bg="#d6c97a", cursor="hand2")
    signup_label.pack(side="left", padx=(3, 0))
    signup_label.bind("<Button-1>", lambda e: show_signup())
    signup_label.bind("<Enter>", on_enter)
    signup_label.bind("<Leave>", on_leave)

# --- Show Signup Form ---
def show_signup():
    clear_form()
    back_arrow.place(x=20, y=20)
    form_frame.config(width=400, height=540)
    form_frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(form_frame, text="username:", font=("Arial", 14, "bold"),
             fg="#000000", bg="#d6c97a", anchor="w").pack(pady=(20, 2))
    username_entry = tk.Entry(form_frame, font=("Arial", 14), width=28,
                              bg="#ffffff", insertbackground="#000000",
                              insertofftime=300, insertontime=600, relief="flat")
    username_entry.pack(pady=(0, 8))
    username_entry.focus_set()

    tk.Label(form_frame, text="gender:", font=("Arial", 14, "bold"),
             fg="#000000", bg="#d6c97a", anchor="w").pack(pady=(0, 2))
    gender_var = tk.StringVar()
    gender_menu = ttk.Combobox(form_frame, textvariable=gender_var, values=["Male", "Female", "Prefer not to say"],
                               font=("Arial", 14), width=26, state="readonly")
    gender_menu.pack(pady=(0, 8))

    tk.Label(form_frame, text="country:", font=("Arial", 14, "bold"),
             fg="#000000", bg="#d6c97a", anchor="w").pack(pady=(0, 2))
    country_var = tk.StringVar()
    country_menu = ttk.Combobox(form_frame, textvariable=country_var, values=countries,
                                font=("Arial", 14), width=26, state="readonly")
    country_menu.pack(pady=(0, 8))

    tk.Label(form_frame, text="email address:", font=("Arial", 14, "bold"),
             fg="#000000", bg="#d6c97a", anchor="w").pack(pady=(0, 2))
    email_entry = tk.Entry(form_frame, font=("Arial", 14), width=28,
                           bg="#ffffff", insertbackground="#000000",
                           insertofftime=300, insertontime=600, relief="flat")
    email_entry.pack(pady=(0, 8))

    tk.Label(form_frame, text="date of birth:", font=("Arial", 14, "bold"),
             fg="#000000", bg="#d6c97a", anchor="w").pack(pady=(0, 2))

    dob_entry = tk.Entry(form_frame, font=("Arial", 14), width=28,
                         bg="#ffffff", fg="gray", insertbackground="#000000", relief="flat")
    dob_entry.pack(pady=(0, 8))

    placeholder = "yyyy-mm-dd"
    dob_entry.insert(0, placeholder)

    def on_entry_focus_in(event):
        if dob_entry.get() == placeholder:
            dob_entry.delete(0, tk.END)
            dob_entry.config(fg="black")

    def on_entry_focus_out(event):
        if not dob_entry.get():
            dob_entry.insert(0, placeholder)
            dob_entry.config(fg="gray")

    dob_entry.bind("<FocusIn>", on_entry_focus_in)
    dob_entry.bind("<FocusOut>", on_entry_focus_out)

    tk.Label(form_frame, text="password:", font=("Arial", 14, "bold"),
             fg="#000000", bg="#d6c97a", anchor="w").pack(pady=(0, 2))
    password_entry = tk.Entry(form_frame, font=("Arial", 14), show="*", width=28,
                              bg="#ffffff", insertbackground="#000000", relief="flat")
    password_entry.pack(pady=(0, 8))

    tk.Label(form_frame, text="confirm password:", font=("Arial", 14, "bold"),
             fg="#000000", bg="#d6c97a", anchor="w").pack(pady=(0, 2))
    confirm_entry = tk.Entry(form_frame, font=("Arial", 14), show="*", width=28,
                             bg="#ffffff", insertbackground="#000000", relief="flat")
    confirm_entry.pack(pady=(0, 20))

    def handle_signup():
        username = username_entry.get()
        gender = gender_var.get()
        country = country_var.get()
        email = email_entry.get()
        dob = dob_entry.get()
        password = password_entry.get()
        confirm = confirm_entry.get()

        if not username or not email or not password:
            messagebox.showerror("Error", "Username, email and password are required")
            return
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        if user_exists(username):
            messagebox.showerror("Error", "Username already exists")
            return
        if insert_user(username, gender, country, email, dob, password):
            messagebox.showinfo("Success", f"Account created for {username}!")
            show_login()
        else:
            messagebox.showerror("Database Error", "Could not create user. Please try again.")

    tk.Button(form_frame, text="Sign Up", font=("Arial", 14, "bold"),
              bg="#000000", fg="#ffffff", width=20,
              command=handle_signup, relief="flat").pack(pady=(0, 10))

# --- Resize Background ---
def resize_bg(event):
    global bg_photo
    if event.widget != root:
        return
    new_width, new_height = event.width, event.height
    resized = original_bg.resize((new_width, new_height), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(resized)
    canvas.delete("all")
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")
    form_frame.place(relx=0.5, rely=0.5, anchor="center")

# --- Main Window and Setup ---
root = tk.Tk()
root.title("Oscar Oracle")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}+0+0")
root.configure(bg="#222222")

original_bg = Image.open(resource_path("background.jpg"))
bg_image = original_bg.resize((900, 600), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)


canvas = tk.Canvas(root, width=900, height=600, highlightthickness=0)
canvas.place(x=0, y=0, relwidth=1, relheight=1)
canvas.create_image(0, 0, anchor="nw", image=bg_photo)
canvas.image = bg_photo

form_frame = tk.Frame(root, width=350, height=320, bg="#d6c97a",
                      borderwidth=0, highlightbackground="#000000", highlightthickness=2)
form_frame.place(relx=0.5, rely=0.5, anchor="center")
form_frame.pack_propagate(0)

back_arrow = tk.Label(root, text="←", font=("Arial", 24, "bold"),
                      fg="#000000", bg="#d6c97a", cursor="hand2")
back_arrow.bind("<Button-1>", lambda e: show_login())

show_login()
root.bind("<Configure>", resize_bg)
root.mainloop()

