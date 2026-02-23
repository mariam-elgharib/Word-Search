# Importing all modules utilized in the program
import random
import string
import tkinter as tk
from tkinter import simpledialog, messagebox
import os
from PIL import Image, ImageTk

# Setting up the tkinter window
window = tk.Tk()
window.geometry('1200x700')  # tkinter size
window.title("Word Search")  # tkinter window
window.configure(bg='#C5D9D6')
# Initialization of all variables
selected_buttons = []  # List to keep track of selected buttons
selected_positions = []  # List to keep track of the positions of selected letters.
buttons = []  # List to keep references to button widgets
score = 0  # Initialize score
dict_find = {}  # Empty dictionary for storing the index of each word in the grid
g = []
g1 = ''
d = ''  # score (files)
f = []  # score (files)
font_warn = ('Times', 17, 'normal')  # font displayed

GRID_SIZE = 0  # Initiation for grid size

words = []
grid = []
score_label = None  # Declare score_label as a global variable
user_n = ''  # Initialize user_n as an empty string

'''
def set_background():
    # Load the background image
    image_path = "p.jpg"  # Replace with the path to your background image
    image = Image.open(image_path)

    # Get the size of the window
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    # Resize the background image to fit the window size
    #resized_image = image.resize((1200, 700),Image.ANTIALIAS)

    # Convert the resized image to PhotoImage
    photo = ImageTk.PhotoImage(image)

    # Create a label with the resized background image
    background_label = tk.Label(window, image=photo)
    background_label.image = photo
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Bring the label to the background
    background_label.lower()
'''

def save_game():
    global user_n, score, words, grid, word_labels, GRID_SIZE, dict_find, buttons

    # Save user name, score, words found, buttons state (as a dictionary with position tuples as keys)
    found_words = {word: 'found' for word, label in word_labels.items() if label.cget("fg") == "grey"}
    buttons_state = {(row, col): buttons[row][col].cget('bg') for row in range(GRID_SIZE) for col in range(GRID_SIZE)}
    save_data = f"{user_n}\n{score}\n{found_words}\n{GRID_SIZE}\n{repr(dict_find)}\n{buttons_state}\n"
    save_data += '\n'.join(','.join(row) for row in grid)

    with open('saved_game.txt', 'w') as file:
        file.write(save_data)

    messagebox.showinfo("Info", "Game saved successfully.")
# "Save Game" button
save_button = tk.Button(window, text="Save Game", bg='#F9E3E5', command=save_game)
save_button.grid(row=2, column=45, padx=10, pady=10)

def load_game():
    global user_n, score, words, GRID_SIZE, grid, word_labels, dict_find, selected_word, buttons

    try:
        with open('saved_game.txt', 'r') as file:
            user_n = file.readline().strip()
            score = int(file.readline().strip())
            found_words = eval(file.readline().strip())
            GRID_SIZE = int(file.readline().strip())
            dict_find = eval(file.readline().strip())
            buttons_state = eval(file.readline().strip())  # Load the state of all buttons
            grid = [line.strip().split(',') for line in file if line.strip()]

            words = list(dict_find.keys())
            word_labels = {}

            if (len(grid) != GRID_SIZE) or any(len(row) != GRID_SIZE for row in grid):
                messagebox.showerror("Error", "The saved game grid does not match the expected size.")
                return

            # Initialize buttons list
            buttons = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

            # If you don't recreate the button widgets on load, you can skip this part
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if (row, col) in buttons_state:  # Check if the position is in buttons state
                        is_highlighted = buttons_state[row, col] == '#93C99A'  # Check button color for "highlighted"
                        button_state = 'disabled' if is_highlighted else 'normal'
                        # Adjust button state accordingly
                        buttons[row][col] = tk.Button(window, text=grid[row][col], width=3, height=2, relief=tk.RAISED,
                                                      command=lambda r=row, c=col: on_button_click(r, c))
                        buttons[row][col].grid(row=row + 1, column=col + 5, padx=1, pady=1)
                        buttons[row][col].config(bg=buttons_state[row, col], state=button_state)
            check_word_button = tk.Button(window, text="Check Word",font=font_warn, bg='#F9E3E5', command=check_word)
            check_word_button.grid(row=3, column=55, pady=10, sticky='NS')
            messagebox.showinfo("Info", "Game loaded successfully.")

    except FileNotFoundError:
        messagebox.showinfo("Info", "No saved game found.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while loading the game: {e}")

def disable_buttons(word=None):
    global selected_word, buttons, dict_find
    if word is None:
        word = selected_word  # Use the selected_word if no argument is provided

    for row, col in dict_find[word]:
        buttons[row][col].config(bg='#27E331', state='disabled')

    words.remove(word)

    word_labels[word].config(text=f"{word} (found)", fg="grey")

# Function that disables the buttons pressed if correct
def disable_found_words():
    global buttons

    for word, positions in dict_find.items():
        if word in word_labels and word_labels[word].cget("fg") == "grey":
            for pos in positions:
                row, col = pos
                if row >= len(buttons) or col >= len(buttons[0]):
                    messagebox.showerror("Error", f"Invalid button position ({row}, {col}) on loading.")
                    return
                buttons[row][col].config(state='disabled', bg='#27E331')

def take_name():
    global user_n

    user_n = simpledialog.askstring('name', "Enter your name:", parent=window)

    if user_n is None:
        window.destroy()
    else:
        welcome_message = tk.Label(window, font=('Times', 25, 'normal'), text='Hello ' + user_n , bg='#C5D9D6')
        welcome_message.grid(row=0, column=5, columnspan=10, padx=10, pady=10)

    if os.path.exists('saved_game.txt'):
        with open('saved_game.txt', 'r') as file:
            content = file.read().splitlines()
        name_saved = content[0]
        if user_n == name_saved:
            response = tk.messagebox.askyesno("Saved?", "Do you want to resume the last game?")
            if response:
                load_game()
                return True
        return False

# Take level and category from the user
def take_level_and_category():
    global GRID_SIZE, words, user_c, user_l
    valid_categories = ['f', 'a', 'p']
    valid_levels = ['1', '2', '3']

    while True:
        user_c = simpledialog.askstring('category', "Enter the category: (f for fruits and veg, a for animals, p for programming)",
                                        parent=window)
        if user_c is None:
            return None
        if user_c.lower() in valid_categories:
            break
        messagebox.showwarning("Invalid Input", "Please enter a valid category: 'f', 'a', or 'p'.")

    while True:
        user_l = simpledialog.askstring('level', "Enter the level choose 1, 2, 3:",
                                        parent=window)
        if user_l is None:
            user_l = '1'

        if user_l.isdigit() and user_l in valid_levels:
            user_l = int(user_l)
            break
        messagebox.showwarning("Invalid Input", "Please enter a valid level: 1, 2, or 3.")

    read_words(user_c, user_l)

# Read words for the level and category
def read_words(user_c, user_l):
    global words, GRID_SIZE
    w=[]
    file_path = "words.txt"  # Correct file path
    with open(file_path, 'r') as file:

        for line in file:
            if line[:2].lower() == user_c.lower() + str(user_l).lower():
                w.append(line[3:].strip())
        #print(w)
    words=w
    if user_l == 1:
        GRID_SIZE = 10
    elif user_l == 2:
        GRID_SIZE = 12
    elif user_l == 3:
        GRID_SIZE = 14
    display_words()
    create_wordsearch(GRID_SIZE, GRID_SIZE, words)

# Function to display the words the user needs to find
def display_words():
    global word_labels
    indicator_label = tk.Label(window, font=font_warn, text="Find these words:", bg='#C5D9D6')
    indicator_label.grid(row=3, column=40, columnspan=10, padx=10, pady=10)
    row_start = 4
    column = 40
    row_counter = row_start

    for word in words:
        displayed_word = tk.Label(window, font=font_warn, text=word , bg='#C5D9D6')
        displayed_word.grid(row=row_counter, column=column, columnspan=10, padx=10, pady=10)
        word_labels[word] = displayed_word
        row_counter += 1

def on_button_click(row, col):
    global selected_positions,buttons

    if (row, col) not in selected_positions:
        selected_positions.append((row, col))
        buttons[row][col].config(bg='#F8EDC3')
    else:
        selected_positions.remove((row, col))
        buttons[row][col].config(bg='SystemButtonFace')

def check_word():
    global score, selected_positions, score_label, word_labels
    selected_word = ''.join(grid[row][col] for row, col in selected_positions)

    if selected_word in words:
        score += 1
        update_score_label()
        messagebox.showinfo("Correct!", f"You found: {selected_word}")

        for row, col in selected_positions:
            buttons[row][col].config(bg='#93C99A')

        words.remove(selected_word)
        for row, col in selected_positions:
            buttons[row][col].config(state='disabled')
        selected_positions.clear()

        word_label = word_labels[selected_word]
        word_label.config(text=f"{selected_word} (found)", fg="grey")
    else:
        messagebox.showerror("Incorrect", f"{selected_word} is not correct.")
        for row, col in selected_positions:
            buttons[row][col].config(bg='SystemButtonFace')
        selected_positions.clear()
        
def create_wordsearch(rows, cols, letters):
    global buttons, grid, words

    grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            row.append('*')
        grid.append(row)
    add_words(grid, words)
    fill_spaces(grid)

    buttons = [[None for _ in range(cols)] for _ in range(rows)]
    
    display(window, GRID_SIZE, GRID_SIZE, grid)

def add_words(grid, words):

    for word in words:
        placed = False
        while not placed:
            row = random.randint(0, len(grid) - 1)
            col = random.randint(0, len(grid[0]) - 1)
            direction = random.choice([(1, 0), (0, 1), (1, 1), (1, -1)])

            positions = []
            valid_placement = True
            for i in range(len(word)):
                new_row = row + i * direction[0]
                new_col = col + i * direction[1]

                if not (0 <= new_row < len(grid) and 0 <= new_col < len(grid[0])) or grid[new_row][new_col] != '*':
                    valid_placement = False
                    break
                else:
                    positions.append((new_row, new_col))

            if valid_placement:
                for i, (new_row, new_col) in enumerate(positions):
                    grid[new_row][new_col] = word[i]
                placed = True
                dict_find[word] = positions

def fill_spaces(grid):
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if grid[row][col] == '*':
                grid[row][col] = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

def display(parent, rows, cols, grid):
    global buttons
    buttons = [[None for _ in range(cols)] for _ in range(rows)]

    for i in range(rows):
        for j in range(cols):
            if 0 <= i < len(grid) and 0 <= j < len(grid[0]):
                letter_box = tk.Button(parent, text=grid[i][j], font='Times', bg='#F9E3E5', width=3, height=2, relief=tk.RAISED,
                                       command=lambda i=i, j=j: on_button_click(i, j))
                letter_box.grid(row=i + 1, column=j + 5, padx=1, pady=1)
                buttons[i][j] = letter_box

    check_word_button = tk.Button(parent, text="Check Word",font=font_warn, bg='#F9E3E5', command=check_word)
    check_word_button.grid(row=1, column=cols + 6, rowspan=rows, pady=10, sticky='NS')
    
def exit_game(event):
    response = tk.messagebox.askyesno("Exit", "Do you want to save your score?")
    if response:
        save_game()
    else:
        window.destroy()

def update_score_label():
    global score_label, score
    score_label = tk.Label(window, text="Score: 0", font=font_warn ,bg='#C5D9D6')
    score_label.grid(row=1, column=45, padx=10, pady=10)
    score_label.config(text=f"Score: {score}")

def main_():
    global GRID_SIZE, words, word_labels, user_c
    #set_background()
    word_labels = {}  
    load_game_requested = take_name()

    if user_n is not None:
        if not load_game_requested:
            take_level_and_category()

            if GRID_SIZE == 0 or not words:
                messagebox.showinfo("Cancelled", "Game loading has been cancelled.")
                window.quit()
                return

            read_words(user_c, user_l)
            create_wordsearch(GRID_SIZE, GRID_SIZE, words)

        update_score_label()

        display_words()

        window.bind('<Escape>', exit_game)
        window.update()
        window.mainloop()
main_()
