import logic as game
from time import time
from os import system

GAME = game.Game()


class GUIHandler:
    """Handles the GUI"""
    def __init__(self):
        self.last_update = 0

    def mainloop(self):
        while True:
            system('cls')
            if GAME.GameOn:
                if GAME.last_update > self.last_update:
                    self.print_board()
                    self.last_update = time()
            else:
                print('Game Over')
                print(f'Final Score: {GAME.snake.level}')

    def print_board(self):
        """Outputs the board"""
        print(f"Level: {GAME.snake.level}")

        for y in range(GAME.board.height):
            print(" ", end="")
            for x in range(GAME.board.width):
                node_found = False

                for snakeNode in game.AllSnakeNodes:
                    if snakeNode.X == x and snakeNode.Y == y:
                        node_found = True
                        if snakeNode.is_head:
                            print("S", end="  ")
                        else:
                            print("s", end="  ")
                        break

                if not node_found:
                    lookup = GAME.board.pos_lookup(x, y)
                    if lookup == game.A:
                        print(".", end="  ")
                    elif lookup == game.O:
                        print("X", end="  ")
                    elif lookup == game.F:
                        print("*", end="  ")
                    else:
                        print(str(GAME.board.pos_lookup(x, y)), end="  ")
            print()
        print()


if __name__ == "__main__":
    GUI = GUIHandler()
    GUI.mainloop()
    # TODO: run parallel
    # Not working as both loops need to run simultaneously. Consider threading or async(io)
    GAME.game_loop()
