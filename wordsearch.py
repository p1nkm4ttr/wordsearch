import tkinter as tk
from tkinter import simpledialog, messagebox
import random


class CrosswordGame:
    def __init__(self, root, size, word_list):
        """Initialize the game state and UI components."""
        self.size = size  # Size of the grid
        self.word_list = word_list  # List of words to be placed in the grid
        self.original_word_list = list(word_list)  # Backup of the original word list
        self.grid = [[' ' for _ in range(size)] for _ in range(size)]  # Create empty grid with spaces
        self.grid_labels = [[None for _ in range(size)] for _ in range(size)]  # UI placeholders for grid cells
        self.selected_cells = []  # List to keep track of selected cells
        self.score = 0  # Player's score

        self.root = root  # The main Tkinter window
        self.root.title("Crossword Game")  # Set window title
        self.create_widgets()  # Create UI components (buttons, labels, etc.)
        self.generate()  # Generate the crossword grid with the words
        self.fill_empty_spaces()  # Fill remaining grid spaces with random letters
        self.update_grid_display()  # Update the grid display with the current state

    def can_place_word(self, word, row, col, direction):
        """Check if the word can be placed at the specified location."""
        if direction == 'horizontal':
            if col + len(word) > self.size:
                return False  # Word doesn't fit in the row
            for i in range(len(word)):
                if self.grid[row][col + i] not in (' ', word[i]):
                    return False  # If the space is occupied or mismatches, return False
        elif direction == 'vertical':
            if row + len(word) > self.size:
                return False  # Word doesn't fit in the column
            for i in range(len(word)):
                if self.grid[row + i][col] not in (' ', word[i]):
                    return False  # If the space is occupied or mismatches, return False
        return True

    def place_word(self, word, row, col, direction):
        """Place the word in the grid at the given position."""
        if direction == 'horizontal':
            for i in range(len(word)):
                self.grid[row][col + i] = word[i]
        elif direction == 'vertical':
            for i in range(len(word)):
                self.grid[row + i][col] = word[i]

    def expand_grid(self):
        """Expand the grid if there isn't enough space to place a word."""
        self.size += 1  # Increase grid size
        self.grid = [row + [' '] for row in self.grid]  # Add a new column
        self.grid.append([' '] * self.size)  # Add a new row

        # Update the grid labels (UI components)
        for row in self.grid_labels:
            row.append(None)
        self.grid_labels.append([None] * self.size)

    def recursive_place_word(self, word, depth=0):
        """Attempt to place a word recursively."""
        if depth > 50:  # Prevent infinite recursion by limiting depth
            self.expand_grid()  # Expand the grid if needed
            depth = 0  # Reset depth after expanding

        direction = random.choice(['horizontal', 'vertical'])  # Randomly choose a direction
        row = random.randint(0, self.size - 1)  # Randomly choose a row
        col = random.randint(0, self.size - 1)  # Randomly choose a column

        if self.can_place_word(word, row, col, direction):  # Check if the word can be placed
            self.place_word(word, row, col, direction)  # Place the word in the grid
            return True
        else:
            return self.recursive_place_word(word, depth + 1)  # Retry if placement fails

    def generate(self):
        """Generate the crossword grid by placing words recursively."""
        for word in self.word_list:
            self.recursive_place_word(word)  # Attempt to place each word

    def fill_empty_spaces(self):
        """Fill empty spaces in the grid with random letters."""
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] == ' ':
                    self.grid[row][col] = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')  # Random letters

    def create_widgets(self):
        """Create the UI components like the grid display, score, and buttons."""
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollable canvas for the grid
        self.canvas = tk.Canvas(self.main_frame)
        self.grid_frame = tk.Frame(self.canvas)

        self.scrollbar_y = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar_x = tk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")

        self.grid_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Clue and score sections
        self.clue_frame = tk.Frame(self.root)
        self.clue_frame.pack(pady=10)

        self.clue_label = tk.Label(self.clue_frame, text="Words:", font=('Helvetica', 14))
        self.clue_label.pack()

        self.clue_text = tk.Text(self.clue_frame, height=10, width=40, state='disabled')
        self.clue_text.pack()

        self.score_label = tk.Label(self.root, text="Score: 0", font=('Helvetica', 14))
        self.score_label.pack(pady=10)

        self.check_button = tk.Button(self.root, text="Check Word", command=self.check_selected_word)
        self.check_button.pack(pady=5)

    def update_grid_display(self):
        """Update the grid display in the UI with the current grid state."""
        for r in range(self.size):
            for c in range(self.size):
                if self.grid_labels[r][c] is None:  # If the label does not exist, create it
                    label = tk.Label(
                        self.grid_frame,
                        text=self.grid[r][c],
                        width=2,
                        height=1,
                        font=('Helvetica', 16),
                        relief='solid'
                    )
                    label.grid(row=r, column=c, padx=2, pady=2)
                    label.bind("<Button-1>", lambda e, r=r, c=c: self.on_cell_click(r, c))  # Bind click event
                    self.grid_labels[r][c] = label
                else:
                    self.grid_labels[r][c]['text'] = self.grid[r][c]  # Update label with current grid value

    def show_clues(self):
        """Display the list of words to find."""
        self.clue_text.config(state='normal')
        self.clue_text.delete(1.0, tk.END)  # Clear previous clues
        for i, word in enumerate(self.word_list):
            self.clue_text.insert(tk.END, f"{i + 1}. {word}\n")  # Insert each word as a clue
        self.clue_text.config(state='disabled')

    def on_cell_click(self, row, col):
        """Handle clicking on a grid cell to select/deselect it."""
        if (row, col) not in self.selected_cells:
            if not self.selected_cells or max(abs(row - self.selected_cells[-1][0]), abs(col - self.selected_cells[-1][1])) == 1:
                self.selected_cells.append((row, col))
                self.grid_labels[row][col].config(bg='yellow')  # Highlight selected cell
            else:
                self.reset_selection()  # Deselect if the cells are not adjacent
        else:
            self.selected_cells.remove((row, col))  # Deselect the cell
            self.grid_labels[row][col].config(bg='white')

    def check_selected_word(self):
        """Check if the selected word is valid."""
        selected_word = ''.join(self.grid[r][c] for r, c in self.selected_cells)  # Build word from selected cells

        if selected_word in self.word_list:  # If the word is valid
            self.score += 10  # Increase score
            self.score_label.config(text=f"Score: {self.score}")  # Update score display
            self.word_list.remove(selected_word)  # Remove word from word list
            for r, c in self.selected_cells:
                self.grid_labels[r][c].config(bg='lightgreen')  # Highlight valid word in light green
            self.show_clues()  # Update clues
            if not self.word_list:  # If all words are found
                self.win_game()  # Call win function
        else:
            print(f"{selected_word} is not a valid word.")  # Print invalid word to console
        self.reset_selection()  # Reset selection

    def win_game(self):
        """Display a win message and ask if the player wants to play again."""
        response = messagebox.askyesno("YOU WIN!", "Congratulations! You found all the words!\nPlay again?")
        if response:
            self.restart_game()  # Restart the game if the player wants to play again
        else:
            self.root.destroy()  # Close the game window

    def restart_game(self):
        """Restart the game with a new word list and grid."""
        self.word_list = get_word_list()  # Get a new word list
        self.original_word_list = list(self.word_list)  # Backup the new word list
        self.size = 10  # Reset grid size
        self.grid = [[' ' for _ in range(self.size)] for _ in range(self.size)]  # Create a new empty grid
        self.grid_labels = [[None for _ in range(self.size)] for _ in range(self.size)]  # Reset grid labels
        self.score = 0  # Reset score
        self.score_label.config(text="Score: 0")  # Update score display
        for widget in self.grid_frame.winfo_children():
            widget.destroy()  # Destroy old grid UI elements
        self.generate()  # Generate new crossword grid
        self.fill_empty_spaces()  # Fill grid with random letters
        self.update_grid_display()  # Update grid UI
        self.show_clues()  # Show the new clues

    def reset_selection(self):
        """Reset the selected cells after checking a word."""
        for r, c in self.selected_cells:
            self.grid_labels[r][c].config(bg='white')  # Reset cell background color
        self.selected_cells = []  # Clear selected cells


def get_word_list():
    """Prompt the user for a list of words."""
    response = messagebox.askquestion("Choose Word List", "Do you want to use predefined words?")
    if response == "yes":
        return ["PYTHON", "JAVA", "CODE", "PUZZLE", "CROSSWORD"]  # Predefined words
    else:
        word_count = simpledialog.askinteger("Custom Words", "How many words would you like to input?")
        return [simpledialog.askstring("Input Word", "Enter a word:").upper() for _ in range(word_count)]  # Custom words


# Main program starts here
root = tk.Tk()
size = 10  # Initial grid size
words = get_word_list()  # Get word list from user
game = CrosswordGame(root, size, words)  # Start the game
game.show_clues()  # Show the clues
root.mainloop()  # Run the Tkinter event loop
