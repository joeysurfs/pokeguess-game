#!/usr/bin/env python3
import json
import random
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# ANSI color codes for console output
RED_BG = "\033[41m"
YELLOW_BG = "\033[43m"
GREEN_BG = "\033[42m"
WHITE_TEXT = "\033[97m"
RESET = "\033[0m"

def color_cell(text, bg):
    """Wrap text in ANSI codes for colored background."""
    return f"{bg}{WHITE_TEXT}{str(text).center(15)}{RESET}"

def load_pokemon_data(path):
    """Load JSON and return a dict mapping lowercase names to data dicts."""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {p['name'].lower(): p for p in data}

def compare(target, guess):
    """Compare two Pokémon dicts and return a mapping of category → color code."""
    res = {}
    # Exact comparisons
    res['type1'] = GREEN_BG if guess['type1'] == target['type1'] else RED_BG
    # Some JSON use "None" string
    t2g = guess['type2'] if guess['type2'] != "None" else None
    t2t = target['type2'] if target['type2'] != "None" else None
    res['type2'] = GREEN_BG if t2g == t2t else RED_BG
    res['evolution_stage'] = GREEN_BG if guess['evolution_stage'] == target['evolution_stage'] else RED_BG
    res['fully_evolved'] = GREEN_BG if guess['fully_evolved'] == target['fully_evolved'] else RED_BG
    # Lists: colors & habitats
    gcols = {c.strip().lower() for c in guess['colors']}
    tcols = {c.strip().lower() for c in target['colors']}
    if gcols & tcols:
        res['colors'] = GREEN_BG if gcols == tcols else YELLOW_BG
    else:
        res['colors'] = RED_BG
    # Habitats may be comma‑separated inside each list item
    ghab = {h.strip().lower() for entry in guess['habitats'] for h in entry.split(',')}
    thab = {h.strip().lower() for entry in target['habitats'] for h in entry.split(',')}
    if ghab & thab:
        res['habitats'] = GREEN_BG if ghab == thab else YELLOW_BG
    else:
        res['habitats'] = RED_BG
    res['generation'] = GREEN_BG if guess['generation'] == target['generation'] else RED_BG
    return res

class PokedleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokedle - Pokémon Guessing Game")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        # Load Pokémon data
        base = os.path.dirname(__file__)
        path = os.path.join(base, "pokemon_info.json")
        self.pokedex = load_pokemon_data(path)
        self.target = random.choice(list(self.pokedex.values()))
        self.attempts = 0
        self.hint_level = 0
        
        # Column width definitions
        self.column_widths = {
            "Name": 100,
            "Type1": 80,
            "Type2": 80,
            "Stage": 60,
            "Full Evo?": 70,
            "Colors": 120,
            "Habitats": 150,
            "Gen": 50
        }
        
        # Headers
        self.headers = ["Name", "Type1", "Type2", "Stage", "Full Evo?", "Colors", "Habitats", "Gen"]
        
        # Configure the style for the combobox
        self.style = ttk.Style()
        self.style.configure("TCombobox", 
                      fieldbackground="#ffffff",
                      background="#ffffff",
                      foreground="#000000",
                      selectbackground="#e3f2fd",
                      selectforeground="#000000",
                      insertcolor="#000000",
                      font=("Arial", 14))
        self.style.map('TCombobox', 
                fieldbackground=[('readonly', '#ffffff')],
                selectbackground=[('readonly', '#e3f2fd')])

        # Create UI elements
        self.create_widgets()

    def create_widgets(self):
        # Header
        self.header_frame = tk.Frame(self.root, bg="#4CAF50", pady=10)
        self.header_frame.pack(fill="x")
        
        # Title and game info in header
        title_frame = tk.Frame(self.header_frame, bg="#4CAF50")
        title_frame.pack(pady=(0, 5))
        tk.Label(title_frame, text="Welcome to Pokedle!", font=("Arial", 20, "bold"), fg="white", bg="#4CAF50").pack(side=tk.LEFT, padx=20)
        
        # Hint button and label in header
        self.hint_frame = tk.Frame(self.header_frame, bg="#4CAF50")
        self.hint_frame.pack(fill="x", padx=20)
        
        # Add hint button
        self.hint_button = tk.Button(
            self.hint_frame, 
            text="Get Hint", 
            font=("Arial", 12), 
            command=self.show_hint,
            bg="#FFC107",  # Amber color for hint button
            fg="black"
        )
        self.hint_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Add hint display label
        self.hint_label = tk.Label(
            self.hint_frame, 
            text="Hints will appear here", 
            font=("Arial", 12, "italic"),
            fg="white", 
            bg="#4CAF50"
        )
        self.hint_label.pack(side=tk.LEFT)
        
        # Instructions below the header
        tk.Label(
            self.header_frame, 
            text="Guess a Pokémon by name. Green=match, Yellow=partial, Red=no match.",
            font=("Arial", 12), 
            fg="white", 
            bg="#4CAF50"
        ).pack(pady=(5, 0))

        # Input field and buttons (streamlined)
        self.input_frame = tk.Frame(self.root, bg="#f0f0f0", pady=15)
        self.input_frame.pack(fill="x", padx=20)
        
        # Create a better layout for input controls
        input_controls = tk.Frame(self.input_frame, bg="#f0f0f0")
        input_controls.pack()
        
        # Get sorted list of Pokemon names for autocomplete
        pokemon_names = sorted([p['name'] for p in self.pokedex.values()])
        
        # Create the combobox for Pokemon selection with autocomplete
        self.guess_entry = ttk.Combobox(
            input_controls,
            values=pokemon_names,
            font=("Arial", 14),
            width=30,
            height=15  # Show 15 suggestions at once
        )
        self.guess_entry.grid(row=0, column=0, padx=10)
        
        # Configure the combobox
        self.guess_entry.option_add('*TCombobox*Listbox.font', ('Arial', 12))
        self.guess_entry.option_add('*TCombobox*Listbox.selectBackground', '#e3f2fd')
        self.guess_entry.option_add('*TCombobox*Listbox.selectForeground', '#000000')
        
        # Bind events for filtering suggestions as user types
        self.guess_entry.bind('<KeyRelease>', self.filter_pokemon_names)
        self.guess_entry.bind('<Return>', lambda event: self.submit_guess())
        
        # Button frame for alignment
        button_frame = tk.Frame(input_controls, bg="#f0f0f0")
        button_frame.grid(row=0, column=1)
        
        tk.Button(
            button_frame, 
            text="Submit", 
            font=("Arial", 12), 
            command=self.submit_guess,
            bg="#2196F3", 
            fg="white",
            width=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, 
            text="Reset", 
            font=("Arial", 12), 
            command=self.reset_game,
            bg="#f44336", 
            fg="white",
            width=8
        ).pack(side=tk.LEFT, padx=5)

        # Results area with scrolling capability
        self.results_frame = tk.Frame(self.root)
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create a canvas with a scrollbar for results
        self.canvas = tk.Canvas(self.results_frame, bg="#f0f0f0")
        self.scrollbar = tk.Scrollbar(self.results_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Create container for results inside canvas
        self.results_container = tk.Frame(self.canvas, bg="#f0f0f0")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.results_container, anchor="nw")
        
        # Configure canvas scrolling
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        self.results_container.bind('<Configure>', self.on_frame_configure)
        
        # Create header row
        self.create_header_row()
        
        # Set focus to entry field
        self.guess_entry.focus_set()
        
    def filter_pokemon_names(self, event):
        """Filter the Pokémon names in the dropdown based on what the user types."""
        # Don't filter for navigation keys
        if event.keysym in ('Up', 'Down', 'Left', 'Right', 'Return', 'Escape'):
            return
            
        typed_text = self.guess_entry.get().lower()
        
        if typed_text == '':
            # If empty, show all Pokémon (sorted)
            pokemon_names = sorted([p['name'] for p in self.pokedex.values()])
            self.guess_entry['values'] = pokemon_names
        else:
            # Filter Pokémon names that contain the typed text
            filtered_names = [name for name in self.pokedex.values() 
                            if typed_text in name['name'].lower()]
            
            # Sort filtered names for better user experience
            filtered_names = sorted([p['name'] for p in filtered_names])
            
            # Limit to a reasonable number
            if len(filtered_names) > 15:
                filtered_names = filtered_names[:15]
                
            self.guess_entry['values'] = filtered_names
            
            # Update the dropdown without forcing focus to it
            # Do not automatically show dropdown - let user press Down key if they want to see suggestions
            # This keeps typing ability intact

    def on_canvas_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # Make sure the window width matches the canvas width
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        
    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def show_hint(self):
        """Show a progressive hint of the target Pokémon's name."""
        target_name = self.target['name']
        
        if self.hint_level >= len(target_name):
            self.hint_label.config(text=f"Full name: {target_name}")
            return
            
        self.hint_level += 1
        revealed = target_name[:self.hint_level]
        hidden = "?" * (len(target_name) - self.hint_level)
        hint_text = f"Hint: {revealed}{hidden}"
        
        self.hint_label.config(text=hint_text)

    def create_header_row(self):
        header_frame = tk.Frame(self.results_container, bg="#333333")
        header_frame.pack(fill="x")
        
        for i, header in enumerate(self.headers):
            header_cell = tk.Frame(header_frame, bg="#333333", width=self.column_widths.get(header, 100), height=30)
            header_cell.grid(row=0, column=i, padx=1, pady=1)
            header_cell.grid_propagate(False)
            
            header_label = tk.Label(header_cell, text=header, bg="#333333", fg="white", font=("Arial", 10, "bold"))
            header_label.place(relx=0.5, rely=0.5, anchor="center")

    def submit_guess(self):
        guess_name = self.guess_entry.get().strip().lower()
        if guess_name not in self.pokedex:
            messagebox.showerror("Error", f"'{guess_name}' not found. Try again.")
            return

        guess = self.pokedex[guess_name]
        self.attempts += 1

        colors = compare(self.target, guess)
        self.display_feedback(guess, colors)

        if guess['name'].lower() == self.target['name'].lower():
            messagebox.showinfo("Congratulations!", f"You found {self.target['name']} in {self.attempts} tries.")
            self.reset_game()

    def display_feedback(self, guess, colors):
        # Create row frame for this guess
        results_row = tk.Frame(self.results_container, bg="#f0f0f0")
        results_row.pack(fill="x", pady=1)
        
        # Create colored cells for each attribute
        row_data = [
            ("Name", guess['name'], None),
            ("Type1", guess['type1'], colors['type1']),
            ("Type2", guess['type2'], colors['type2']),
            ("Stage", guess['evolution_stage'], colors['evolution_stage']),
            ("Full Evo?", "Yes" if guess['fully_evolved'] else "No", colors['fully_evolved']),
            ("Colors", ", ".join(guess['colors']), colors['colors']),
            ("Habitats", ", ".join(guess['habitats']), colors['habitats']),
            ("Gen", guess['generation'], colors['generation'])
        ]
        
        # Create a colored grid to display results
        for i, (header, value, color_code) in enumerate(row_data):
            bg_color = "#FFFFFF"  # Default white for name
            text_color = "black"  # Default text color
            
            if color_code:
                if color_code == GREEN_BG:
                    bg_color = "#4CAF50"  # Green
                    text_color = "white"
                elif color_code == YELLOW_BG:
                    bg_color = "#FFEB3B"  # Yellow
                    text_color = "black"  # Better contrast on yellow
                elif color_code == RED_BG:
                    bg_color = "#F44336"  # Red
                    text_color = "white"
                
            cell_frame = tk.Frame(results_row, bg=bg_color, width=self.column_widths.get(header, 100), height=30)
            cell_frame.grid(row=0, column=i, padx=1, pady=1)
            cell_frame.grid_propagate(False)
            
            label = tk.Label(cell_frame, text=value, bg=bg_color, fg=text_color, font=("Arial", 9))
            label.place(relx=0.5, rely=0.5, anchor="center")

    def reset_game(self):
        self.target = random.choice(list(self.pokedex.values()))
        self.attempts = 0
        self.hint_level = 0
        
        # Reset hint text
        self.hint_label.config(text="Hints will appear here")
        
        # Clear all widgets from the results container
        for widget in self.results_container.winfo_children():
            widget.destroy()
            
        # Recreate the header row
        self.create_header_row()
        
        # Clear the entry field
        self.guess_entry.delete(0, tk.END)
        self.guess_entry.focus_set()

if __name__ == "__main__":
    root = tk.Tk()
    app = PokedleApp(root)
    root.mainloop()
