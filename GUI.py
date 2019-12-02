import json
import tkinter as tk
import tkinter.ttk as ttk
from time import time
from tkinter.messagebox import showerror

import PIL.Image
import PIL.ImageTk

import logic as game

# from tkinter.colorchooser import askcolor

FONT_L = ("Helvetica", 24)
FONT_M = ("Helvetica", 20)
FONT_S = ("Helvetica", 18)

COLOURS = {"background": "#ffffff",
           "foreground": "#333344",
           "snake_head": "#00ee00",
           "snake_tail": "#009900",
           "snake_food": "#cc0000",
           "obstacle": "#000000",
           "button_good": "#009900",
           "button_bad": "#cc0000",
           "button_neutral": "#2222ee",
           "button_default": "#999999"}

COLOURS_COLBLIND = {"snake_tail": "#0a284b",
                    "snake_head": "#235fa4",
                    "snake_food": "#ff4242"}

COLOUR_BLIND_MODE = False

BUTTONS = {"left":"Left",
           "right":"Right",
           "up":"Up",
           "down":"Down"}


def load_settings(filename="settings.json"):
    global COLOUR_BLIND_MODE
    """Loads the settings into memory"""
    filepath = "Files/Settings/" + filename

    try:
        with open(filepath, "r") as file:
            data = json.load(file)
    except Exception as e:
        print(e)
        showerror("Error loading settings data",
                  "An error occurred when trying to fetch settings data. Reverting to default data.")
        return None

    if "colour_blind" in data:
        if type(data["colour_blind"]) is bool:
            COLOUR_BLIND_MODE = data["colour_blind"]

    if "control_up" in data:
        BUTTONS["up"] = data["control_up"]

    if "control_down" in data:
        BUTTONS["down"] = data["control_down"]

    if "control_left" in data:
        BUTTONS["left"] = data["control_left"]

    if "control_right" in data:
        BUTTONS["right"] = data["control_right"]


def save_settings(filename: str = "settings.json", colour_blind: bool = None,
                  control_left: str = None, control_right: str = None,
                  control_up: str = None, control_down: str = None) -> bool:
    """Update the settings file"""

    filepath = "Files/Settings/" + filename

    try:
        with open(filepath, "r") as file:
            data = json.load(file.read())
    except:
        data = {}

    if colour_blind is not None:
        data["colour_blind"] = colour_blind

    if control_left is not None:
        data["control_left"] = control_left

    if control_right is not None:
        data["control_right"] = control_right

    if control_up is not None:
        data["control_up"] = control_up

    if control_down is not None:
        data["control_down"] = control_down

    with open(filepath, "w") as file:
        json.dump(data, file)

    return True


GAME = game.Game(settings_file="game_settings.json")


def restart_game():
    global GAME
    del GAME
    GAME = game.Game(settings_file="game_settings.json")


class Window(tk.Tk):
    """Window handler"""

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title('Hungry Python')
        self.iconbitmap(r'Files/Images/icon.ico')
        # Main Container
        container = tk.Frame(self)
        container.pack(side="top", fill="both")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.Pages = {}
        self.CurrentPage = ""
        for page in (Start, Settings, InProgress, PauseMenu, EndGame):
            page_name = page.page_name

            # Create and store page
            p = page(container, self)
            self.Pages[page_name] = p

            p.configure(bg=COLOURS["background"])

            # Display the page.
            p.grid(row=0, column=0, sticky="nsew")

            # Run any initialisation that a page may have
            p.initialise()

        self.set_page(Start.page_name)

        # Set up the event manager
        self.last_key = None
        self.bind("<Key>", self.key_press)

    def key_press(self, event):
        if self.CurrentPage == "InProgress":
            if event.keysym.lower() == BUTTONS["right"].lower():
                GAME.snake.update_direction("e")
            elif event.keysym.lower() == BUTTONS["left"].lower():
                GAME.snake.update_direction("w")
            elif event.keysym.lower() == BUTTONS["up"].lower():
                GAME.snake.update_direction("n")
            elif event.keysym.lower() == BUTTONS["down"].lower():
                GAME.snake.update_direction("s")
            elif event.keysym.lower() == "p":
                self.set_page(PauseMenu.page_name)
        if self.CurrentPage == "Settings":
            self.Pages[self.CurrentPage].on_key_event(event)

        self.last_key = event
        # print(event)

    def set_page(self, page_name: str) -> bool:
        """Update the page to the page with the given name"""
        if page_name in self.Pages:
            self.Pages[page_name].on_show()
            self.Pages[page_name].tkraise()
            self.CurrentPage = page_name
            return True
        else:
            return False


class Start(tk.Frame):
    page_name = "Start"

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Pad the whole page
        # self.grid(padx=50, pady=25)

        # Title image
        img = PIL.Image.open("Files/Images/Title.png")
        photo = PIL.ImageTk.PhotoImage(img)

        title = tk.Label(self, image=photo, bg=COLOURS["background"])
        title.image = photo
        title.pack(side="top", pady=50)

        # Start Button
        tk.Button(self, text="Start", height=1, width=20, font=FONT_M, bg=COLOURS["button_good"],
                  command=lambda: self.start()).pack(side="top", pady=10)

        # Settings Button
        tk.Button(self, text="Settings", height=1, width=20, font=FONT_M, bg=COLOURS["button_default"],
                  command=lambda: controller.set_page(Settings.page_name)).pack(side="top", pady=10)

        # Exit
        tk.Button(self, text="Exit", height=1, width=20, font=FONT_M, bg=COLOURS["button_bad"],
                  command=lambda: controller.destroy()).pack(side="top", pady=10)

    def start(self):
        GAME.start_game()
        self.controller.set_page("InProgress")

    def on_show(self):
        """Runs when this page is shown"""
        pass

    def initialise(self):
        pass


class Settings(tk.Frame):
    """Settings page"""
    page_name = "Settings"

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller

        # Title
        tk.Label(self, text="Settings", font=FONT_L, bg=COLOURS["background"]).pack(side="top", pady=25)

        # Board width
        input_pane = tk.Frame(self, bg=COLOURS["background"])
        input_pane.pack(side="top", pady=10)

        # Label the width
        tk.Label(input_pane, text="Board Width", font=FONT_M,
                 bg=COLOURS["background"]).grid(row=0, column=0, sticky="w", padx=5)

        self.width_entry = tk.Entry(input_pane, bg="#dddddd", font=FONT_M)
        self.width_entry.grid(row=0, column=1, padx=5)

        # Height
        # Label the Height
        tk.Label(input_pane, text="Board Height", font=FONT_M,
                 bg=COLOURS["background"]).grid(row=1, column=0, sticky="w", padx=5)

        self.height_entry = tk.Entry(input_pane, bg="#dddddd", font=FONT_M)
        self.height_entry.grid(row=1, column=1, padx=5)

        # Split the next section off
        ttk.Separator(input_pane).grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)

        # Tick Speed
        # Label tick speed
        tk.Label(input_pane, text="Tick Speed", font=FONT_M,
                 bg=COLOURS["background"]).grid(row=3, column=0, sticky="w", padx=5)

        self.tick_entry = tk.Entry(input_pane, bg="#dddddd", font=FONT_M)
        self.tick_entry.grid(row=3, column=1, padx=5)

        # Colour blind section
        self.col_blind_var = tk.IntVar()

        # Label
        tk.Label(input_pane, text="Colour blind mode", font=FONT_M, bg=COLOURS["background"]).grid(row=5, column=0)

        tk.Checkbutton(input_pane, variable=self.col_blind_var, bg=COLOURS["background"]).grid(row=5, column=1)

        # Split the next section off
        ttk.Separator(input_pane).grid(row=6, column=0, columnspan=2, sticky="ew", pady=10)

        # Input
        tk.Label(input_pane, text="Control Input",
                 font=FONT_M, bg=COLOURS["background"]).grid(row=7, column=0, columnspan=2, stick="ew")

        # Use dict() so that is a copy, not a reference
        self.new_buttons = dict(BUTTONS)

        self.last_key_press = None  # Stores the last key press
        self.bind("<Key>", self.on_key_event)
        self.key_wait = None  # Stores which key we are waiting to set

        row = 7

        self.input_labels = {}
        self.update_buttons = {}
        self.set_buttons = {}
        self.cancel_buttons = {}
        for direction in ["up", "down", "left", "right"]:
            row += 1
            frame = tk.LabelFrame(input_pane, text=direction.capitalize() + " key",
                                  font=FONT_M, bg=COLOURS["background"])
            frame.grid(row=row, column=0, columnspan=2, sticky="nsew")

            # Create and store the Label
            label = tk.Label(frame, text=BUTTONS[direction], width=7, font=FONT_M, bg=COLOURS["background"])
            label.grid(row=0, column=0, sticky="nsw")

            self.input_labels[direction] = label

            # Create and store the change button
            change = tk.Button(frame, text="Change", font=FONT_M, bg=COLOURS["button_neutral"],
                               command=lambda d=direction: self.update_control(d))
            change.grid(row=0, column=1, sticky="nsew", pady=5, padx=5)

            self.update_buttons[direction] = change

            # Create and store the set buttons
            _set = tk.Button(frame, text="Set", font=FONT_M, bg=COLOURS["button_good"], state="disabled",
                             command=lambda d=direction: self.set_control(d))
            _set.grid(row=0, column=2, sticky="nsew", pady=5)

            self.set_buttons[direction] = _set

            # Create and store the cancel button
            canc = tk.Button(frame, text="Cancel", font=FONT_M, bg=COLOURS["button_bad"], state="disabled",
                             command=lambda: self.reset_control())
            canc.grid(row=0, column=3, sticky="nsew", pady=5, padx=5)

            self.cancel_buttons[direction] = canc

        # Back button
        tk.Button(self, text="Back", font=FONT_M, bg=COLOURS["button_default"], width=10,
                  command=lambda: controller.set_page(Start.page_name)).pack(side="bottom", pady=10)

        # Update Button
        tk.Button(self, text="Update", font=FONT_M, bg=COLOURS["button_neutral"], width=10,
                  command=lambda: self.update_data()).pack(side="bottom", pady=10)

    def on_key_event(self, event):
        """Handles key press events"""
        self.last_key_press = event

        if self.key_wait is not None:
            self.input_labels[self.key_wait].configure(text=event.keysym)

    def update_control(self, dirct):
        """Update the which key controls which snake function (up, down etc)"""
        if self.key_wait is not None:
            self.reset_control()

        # Now set the new buttons
        self.key_wait = dirct

        self.set_buttons[dirct].configure(state="normal")
        self.cancel_buttons[dirct].configure(state="normal")
        self.update_buttons[dirct].configure(state="disabled")

    def reset_control(self):
        """Cancel the input control"""
        self.key_wait = None
        # Reset all the buttons
        for dirct in ["up", "down", "left", "right"]:
            self.cancel_buttons[dirct].configure(state="disabled")
            self.set_buttons[dirct].configure(state="disabled")
            self.update_buttons[dirct].configure(state="normal")

            self.input_labels[dirct].configure(text=self.new_buttons[dirct])

    def set_control(self, dirct):
        """Set the last pressed key as the control for the given direction"""
        global BUTTONS
        if self.last_key_press is not None:
            key = self.last_key_press.keysym
            self.new_buttons[dirct] = key
            self.input_labels[dirct].configure(text=key)

        self.reset_control()

    def update_data(self):
        """Send the data to the game handler to update"""
        global COLOUR_BLIND_MODE
        # Colour blindness
        col_blind = self.col_blind_var.get()

        if col_blind == 1:
            COLOUR_BLIND_MODE = True
        else:
            COLOUR_BLIND_MODE = False

        # Controls
        if len(self.new_buttons) > 0:
            for dirct in self.new_buttons:
                BUTTONS[dirct] = self.new_buttons[dirct]

        # Game settings
        height = int(self.height_entry.get())
        width = int(self.width_entry.get())
        tick = int(self.tick_entry.get())

        if not GAME.update_settings(height=height, width=width, tick_speed=tick):
            showerror("An error has occurred.",
                      "An error occurred when trying to update the game settings. Please try again.")
        else:
            GAME.load_settings()

        col_blind = True if col_blind == 1 else False

        save_settings(colour_blind=col_blind, control_down=BUTTONS["down"], control_up=BUTTONS["up"],
                      control_left=BUTTONS["left"], control_right=BUTTONS["right"])

    def populate_data(self):
        """Populate the data inputs with the current data"""
        height = str(GAME.board.height)
        width = str(GAME.board.width)
        tick_speed = str(GAME.update_every_ms)

        colour_blind = 0
        if COLOUR_BLIND_MODE:
            colour_blind = 1

        self.col_blind_var.set(colour_blind)

        # Clear all the inputs
        self.height_entry.delete(0, tk.END)
        self.width_entry.delete(0, tk.END)
        self.tick_entry.delete(0, tk.END)

        # Insert data
        self.height_entry.insert(0, height)
        self.width_entry.insert(0, width)
        self.tick_entry.insert(0, tick_speed)

    def on_show(self):
        """Runs when this page is shown"""
        self.populate_data()

    def initialise(self):
        pass


class InProgress(tk.Frame):
    page_name = "InProgress"

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.configure(bg=COLOURS["foreground"])

        self.last_update = time()

        stats_bar = tk.Frame(self, bg=COLOURS["foreground"])
        stats_bar.pack(side="top", fill="x")

        # Score section. Contains a label identifying what it is and a dynamic label which will hold the score
        # Embedded in a frame for formatting
        score_section = tk.Frame(stats_bar, bg=COLOURS["foreground"])
        score_section.pack(side="left")

        # Identifier
        tk.Label(score_section, text="Score: ", font=FONT_M,
                 bg=COLOURS["foreground"], fg="#ffffff").grid(row=0, column=0, sticky="nsew")

        self.ScoreText = tk.Label(score_section, text="", bg=COLOURS["foreground"], fg="#ffffff", font=FONT_M)
        self.ScoreText.grid(row=0, column=1, sticky="nsew")

        # Pause menu
        pause_button = tk.Button(stats_bar, text="Pause", font=FONT_M, bg=COLOURS["button_neutral"],
                                 command=lambda: controller.set_page(PauseMenu.page_name))
        pause_button.pack(side="right")

        # TODO: Board redraw on window size change
        #       Make the board size proportional to the window size.
        #       Alternatively, lock the window size.
        #       Though, with a contrasting background, it is not as important
        # Board Set up
        self.board_area = tk.Frame(self, bg=COLOURS["foreground"])
        self.board_area.pack(side="top")

        self.board_items = []  # a list of lists, similar to the game board. hols widgets

    def setup_board(self):
        """Create the board and board widgets"""
        self.board_items = []

        for child in self.board_area.winfo_children():
            child.destroy()

        for y in range(GAME.board.height):
            row = []
            for x in range(GAME.board.width):
                # TODO: Make the width and height of label configurable (always keep in a ratio of 2:1)
                w = tk.Label(self.board_area, width=16, height=8, font=("Helvetica", 1),
                             text=GAME.board.pos_lookup(x, y))
                w.grid(row=y, column=x, sticky="nsew")
                row.append(w)
            self.board_items.append(row)

    def board_update(self):
        """Update the visuals on the board"""
        if GAME.last_update > self.last_update:
            self.last_update = time()

            score = GAME.snake.level
            self.ScoreText.configure(text=str(score))
            # We loop through each grid place, anc check for changes, if there isn't changes, dont update
            for y in range(GAME.board.height):
                for x in range(GAME.board.width):
                    place_text = ""

                    node_found = False

                    for snakeNode in game.AllSnakeNodes:
                        if snakeNode.X == x and snakeNode.Y == y:
                            node_found = True
                            if snakeNode.is_head:
                                place_text = "S"
                            else:
                                place_text = "s"
                            break

                    if not node_found:
                        lookup = GAME.board.pos_lookup(x, y)
                        if lookup == game.A:
                            place_text = ""
                        elif lookup == game.O:
                            place_text = "X"
                        elif lookup == game.F:
                            place_text = "O"
                        else:
                            place_text = str(GAME.board.pos_lookup(x, y))

                    if self.board_items[y][x]['text'] != place_text:
                        if place_text == "S":
                            if COLOUR_BLIND_MODE:
                                self.board_items[y][x].configure(bg=COLOURS_COLBLIND["snake_head"],
                                                                 fg=COLOURS_COLBLIND["snake_head"])
                            else:
                                self.board_items[y][x].configure(bg=COLOURS["snake_head"], fg=COLOURS["snake_head"])
                        elif place_text == "s":
                            if COLOUR_BLIND_MODE:
                                self.board_items[y][x].configure(bg=COLOURS_COLBLIND["snake_tail"],
                                                                 fg=COLOURS_COLBLIND["snake_tail"])
                            else:
                                self.board_items[y][x].configure(bg=COLOURS["snake_tail"], fg=COLOURS["snake_tail"])
                        elif place_text == "X":
                            self.board_items[y][x].configure(bg=COLOURS["obstacle"], fg=COLOURS["obstacle"])
                        elif place_text == "O":
                            if COLOUR_BLIND_MODE:
                                self.board_items[y][x].configure(bg=COLOURS_COLBLIND["snake_food"],
                                                                 fg=COLOURS_COLBLIND["snake_food"])
                            else:
                                self.board_items[y][x].configure(bg=COLOURS["snake_food"], fg=COLOURS["snake_food"])
                        else:
                            self.board_items[y][x].configure(bg=COLOURS["background"], fg=COLOURS["background"])

                        self.board_items[y][x].configure(text=place_text)
        else:
            pass

    def on_show(self):
        """Runs when this page is shown"""
        self.setup_board()

    def initialise(self):
        self.configure(bg=COLOURS["foreground"])
        self.setup_board()


class PauseMenu(tk.Frame):
    """Pause Menu page"""
    page_name = "PauseMenu"

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller

        # Page title
        tk.Label(self, text="Game Paused", font=FONT_L, bg=COLOURS["background"]).pack(side="top", pady=25)

        # Continue playing button
        tk.Button(self, text="Continue Playing", font=FONT_M, height=1, width=20, bg=COLOURS["button_good"],
                  command=lambda: controller.set_page(InProgress.page_name)).pack(side="top", pady=10)

        # Restart button
        tk.Button(self, text="Restart Game", font=FONT_M, height=1, width=20, bg=COLOURS["button_bad"],
                  command=lambda: self.restart_game()).pack(side="top", pady=10)

        # Quit Button
        tk.Button(self, text="Quit", bg=COLOURS["button_bad"], height=1, width=20,
                  font=FONT_M, command=lambda: controller.destroy()).pack(side="top", pady=40)

    def restart_game(self):
        """Restart the game and return to the hope page"""
        restart_game()

        self.controller.set_page(Start.page_name)

    def on_show(self):
        """Runs when this page is shown"""
        pass

    def initialise(self):
        pass


class EndGame(tk.Frame):
    page_name = "EndGame"

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller

        title = tk.Label(self, text="GAME OVER", font=FONT_L, bg=COLOURS["background"])
        title.pack(side="top", pady=25, fill="x")

        score_frame = tk.Frame(self)
        score_frame.pack(side="top", pady=25)

        # Score label
        tk.Label(score_frame, text="You died at the length of: ", font=FONT_M,
                 bg=COLOURS["background"]).grid(row=0, column=0)

        self.score_label = tk.Label(score_frame, text="", font=FONT_M, bg=COLOURS["background"])
        self.score_label.grid(row=0, column=1)

        # Restart Button
        tk.Button(self, text="Try Again", bg=COLOURS["button_good"], height=1, width=20,
                  font=FONT_S, command=lambda: self.restart_game()).pack(side="bottom", pady=10)

        # Quit Button
        tk.Button(self, text="Quit", bg=COLOURS["button_bad"], height=1, width=20,
                  font=FONT_S, command=lambda: controller.destroy()).pack(side="bottom", pady=20)

    def restart_game(self):
        """Onclick function for restarting the GAME"""
        restart_game()

        self.controller.set_page(Start.page_name)

    def game_over(self):
        """Sets up the page based on the data"""
        score = GAME.snake.level

        self.score_label.configure(text=str(score))

    def on_show(self):
        """Runs when this page is shown"""
        self.game_over()

    def initialise(self):
        pass


if __name__ == "__main__":
    load_settings()
    win = Window()

    # Tie the game loop to the GUI mainloop.
    # Should not affect game speed as it runs based off of its own independent time evaluations
    def loop_tasks():
        global GAME
        if win.CurrentPage == InProgress.page_name:

            if GAME.GameOn:
                GAME.game_single_loop()
                win.Pages["InProgress"].board_update()
            if GAME.GameState == game.OVER:
                win.set_page(EndGame.page_name)
        win.update_idletasks()
        win.after(0, loop_tasks)


    win.after(10, loop_tasks)
    win.mainloop()
