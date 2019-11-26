import tkinter as tk
from time import time

import PIL.Image
import PIL.ImageTk

import logic as game

GAME = game.Game()


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
        for page in (Start, InProgress, EndGame):
            self.Pages[page.page_name] = page(container, self)
            self.Pages[page.page_name].grid(row=0, column=0, sticky="nsew")

            # Run any initialisation that a page may have
            self.Pages[page.page_name].initialise()

        self.set_page(Start.page_name)

        # Set up the event manager
        self.bind("<Key-Up>", self.key_press)
        self.bind("<Key-Left>", self.key_press)
        self.bind("<Key-Right>", self.key_press)
        self.bind("<Key-Down>", self.key_press)

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

    def set_page(self, page_name: str) -> bool:
        """Update the page to the page with the given name"""
        if page_name in self.Pages:
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
        self.grid(padx=50, pady=25)

        # Title image
        img = PIL.Image.open("Files/Images/Title.png")
        photo = PIL.ImageTk.PhotoImage(img)

        title = tk.Label(self, image=photo)
        title.image = photo
        title.pack(side="top", pady=50)

        # Start Button
        tk.Button(self, text="Start", height=1, width=20, font=('Ariel', 20), bg="#00ee00",
                  command=lambda: self.start()).pack(side="top", pady=10)

        # Settings Button
        tk.Button(self, text="Settings", height=1, width=20, font=('Ariel', 20), bg="#999999",
                  state='disabled').pack(side="top", pady=10)
        # TODO: Create the Settings page

        # Exit
        tk.Button(self, text="Exit", height=1, width=20, font=('Ariel', 20), bg="#ee0000",
                  command=lambda: controller.destroy()).pack(side="top", pady=10)

    def start(self):
        GAME.start_game()
        self.controller.set_page("InProgress")

    def initialise(self):
        pass


class InProgress(tk.Frame):
    page_name = "InProgress"

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.last_update = time()

        self.board_area = tk.Frame(self)
        self.board_area.pack(side="top", fill="x")

        self.board_items = []  # a list of lists, similar to the game board. hols widgets

    def setup_board(self):
        """Create the board and board widgets"""
        self.board_items = []
        for y in range(GAME.board.height):
            row = []
            for x in range(GAME.board.width):
                w = tk.Label(self.board_area, width=2, height=1, text=GAME.board.pos_lookup(x, y))
                w.grid(row=y, column=x, sticky="nsew")
                row.append(w)
            self.board_items.append(row)

    def board_update(self):
        """Update the visuals on the board"""
        if GAME.last_update > self.last_update:
            self.last_update = time()

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
                            self.board_items[y][x].configure(bg="#00ee00", fg="#00ee00")
                        elif place_text == "s":
                            self.board_items[y][x].configure(bg="#009900", fg="#009900")
                        elif place_text == "X":
                            self.board_items[y][x].configure(bg="#000000", fg="#000000")
                        elif place_text == "O":
                            self.board_items[y][x].configure(bg="#cc0000", fg="#cc0000")
                        else:
                            self.board_items[y][x].configure(bg="#ffffff", fg="#ffffff")

                        self.board_items[y][x].configure(text=place_text)
        else:
            pass

    def initialise(self):
        self.setup_board()


class EndGame(tk.Frame):
    page_name = "EndGame"

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller

        title = tk.Label(self, text="GAME OVER", font=("Verdana", 24))
        title.pack(side="top", pady=25, fill="x")

        score_frame = tk.Frame(self)
        score_frame.pack(side="top", pady=25)

        # Score label
        tk.Label(score_frame, text="You died at the length of: ", font=("Verdana", 20)).grid(row=0, column=0)

        self.score_label = tk.Label(score_frame, text="", font=("Verdana", 20))
        self.score_label.grid(row=0, column=1)

        # Restart Button
        tk.Button(self, text="Try Again", bg="#00ee00", height=1, width=20,
                  state="disabled", font=("Verdana", 18)).pack(side="bottom", pady=10)

        # Quit Button
        tk.Button(self, text="Quit", bg="#ee0000", height=1, width=20,
                  font=("Verdana", 18), command=lambda: controller.destroy()).pack(side="bottom", pady=20)

    def game_over(self):
        """Sets up the page based on the data"""

        score = GAME.snake.level

        self.score_label.configure(text=str(score))

    def initialise(self):
        pass


if __name__ == "__main__":
    win = Window()

    # Tie the game loop to the GUI mainloop.
    # Should not affect game speed as it runs based off of its own independent time evaluations
    def loop_tasks():
        GAME.game_single_loop()
        if GAME.GameOn:
            win.Pages["InProgress"].board_update()
        if GAME.GameState == game.OVER:
            win.Pages[EndGame.page_name].game_over()
            win.set_page(EndGame.page_name)
        win.update_idletasks()
        win.after(0, loop_tasks)

    win.after(10, loop_tasks)
    win.mainloop()
