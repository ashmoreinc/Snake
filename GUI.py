import tkinter as tk
import tkinter.ttk as ttk
from time import time
from tkinter.messagebox import showerror

import PIL.Image
import PIL.ImageTk

import logic as game

FONT_L = ("Helvetica", 24)
FONT_M = ("Helvetica", 20)
FONT_S = ("Helvetica", 18)

COLOURS = {"background": "#333366",
           "foreground": "#333344",
           "snake_head": "#00ee00",
           "snake_tail": "#009900",
           "snake_food": "#cc0000",
           "obstacle": "#000000",
           "button_good": "#009900",
           "button_bad": "#cc0000",
           "button_neutral": "#2222ee",
           "button_default": "#999999"}

GAME = game.Game(settings_file="settings.json")


def restart_game():
    global GAME
    del GAME
    GAME = game.Game(settings_file="settings.json")


class Window (tk.Tk):
    """Window handler"""
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title('Hungry Python')

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
        self.bind("<Key-Up>", self.key_press)
        self.bind("<Key-Left>", self.key_press)
        self.bind("<Key-Right>", self.key_press)
        self.bind("<Key-Down>", self.key_press)
        self.bind("<Key-p>", self.key_press)

    def key_press(self, event):
        if self.CurrentPage == "InProgress":
            if event.keysym == "Right":
                GAME.snake.update_direction("e")
            elif event.keysym == "Left":
                GAME.snake.update_direction("w")
            elif event.keysym == "Up":
                GAME.snake.update_direction("n")
            elif event.keysym == "Down":
                GAME.snake.update_direction("s")
            elif event.keysym == "p" or event.keysym == "P":
                self.set_page(PauseMenu.page_name)

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

        # Split the next section off
        ttk.Separator(input_pane).grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)

        # Colour Mode
        self.colour_mode = tk.IntVar()
        # 1 = Standard
        # 2 = Tritanopia
        # 3 = Deuteranopia
        # 4 = Protanopia


        self.tick_entry = tk.Entry(input_pane, bg="#dddddd", font=FONT_M)
        self.tick_entry.grid(row=3, column=1, padx=5)

        # TODO: Colour configuration.
        # TODO: Colour Blind presets

        # Back button
        tk.Button(self, text="Back", font=FONT_M, bg=COLOURS["button_default"], width=10,
                  command=lambda: controller.set_page(Start.page_name)).pack(side="bottom", pady=10)

        # Update Button
        tk.Button(self, text="Update", font=FONT_M, bg=COLOURS["button_neutral"], width=10,
                  command=lambda: self.update_data()).pack(side="bottom", pady=10)

    def update_data(self):
        """Send the data to the game handler to update"""
        height = int(self.height_entry.get())
        width = int(self.width_entry.get())
        tick = int(self.tick_entry.get())

        if not GAME.update_settings(height=height, width=width, tick_speed=tick):
            showerror("An error has occurred.",
                      "An error occurred when trying to update the settings. Please try again.")
        else:
            GAME.load_settings()

    def populate_data(self):
        """Populate the data inputs with the current data"""
        height = str(GAME.board.height)
        width = str(GAME.board.width)
        tick_speed = str(GAME.update_every_ms)

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
        self.board_area = tk.Frame(self)
        self.board_area.pack(side="top")

        self.board_items = []  # a list of lists, similar to the game board. hols widgets

    def setup_board(self):
        """Create the board and board widgets"""
        self.board_items = []
        for y in range(GAME.board.height):
            row = []
            for x in range(GAME.board.width):
                # TODO: Make the width and height configurable (always keep in a ratio of 2:1)
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
                            self.board_items[y][x].configure(bg=COLOURS["snake_head"], fg=COLOURS["snake_head"])
                        elif place_text == "s":
                            self.board_items[y][x].configure(bg=COLOURS["snake_tail"], fg=COLOURS["snake_tail"])
                        elif place_text == "X":
                            self.board_items[y][x].configure(bg=COLOURS["obstacle"], fg=COLOURS["obstacle"])
                        elif place_text == "O":
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
        self.setup_board()


class PauseMenu(tk.Frame):
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
