import os
from random import randrange
from time import time

import keyboard

# Direction constants
N = NORTH = "n"
S = SOUTH = "s"
E = EAST = "e"
W = WEST = "w"

# Game state constants
OFF = "off"
ON = "on"
OVER = "over"

# DEBUGGING
RAISE_ERRORS = True
DEBUG_TEXT = True


def report_error(text, error_type=None, raise_err: bool = False):
    if DEBUG_TEXT:
        print(text)
    if RAISE_ERRORS and raise_err:
        if error_type is not None:
            error_type(text)


# Board Data
A = AVAIL = 0
O = OBSTA = 1
F = FOOD = 2

# Store a reference of all snake nodes for easy reference
AllSnakeNodes = []


class Board:
    """The main board controller for the game"""
    def __init__(self, width: int = 30, height: int = 30):
        self.width = width
        self.height = height

        # Set up the grid
        self.grid = []
        for y in range(height):
            row = []
            for x in range(width):
                row.append(AVAIL)
            self.grid.append(row)

        # Food
        self.food_pos = []  # x, y
        self.place_food()

    def pos_lookup(self, x: int, y: int) -> int:
        """Looks up whats at the coords given and returns that
        'A glorified getter'
        """

        if y >= self.height or y < 0:
            return None
        elif x >= self.width or x < 0:
            return None
        else:
            return self.grid[y][x]

    def place_food(self) -> None:
        """Place a bit of food in a random location"""
        y = randrange(0, self.height)
        x = randrange(0, self.width)

        if self.grid[y][x] != AVAIL:
            self.place_food()
            return None
        else:
            for node in AllSnakeNodes:
                if node.X == x and node.Y == y:
                    self.place_food()
                    return None

        self.grid[y][x] = FOOD

        self.food_pos = [x, y]

    def food_ate(self) -> None:
        """Remove the food that is currently on the board and then create a new one."""
        self.grid[self.food_pos[1]][self.food_pos[0]] = AVAIL
        self.place_food()


class SnakeNode:
    """The main snake class"""
    def __init__(self, pos_x: int, pos_y: int, is_head: bool = False):
        self.X = pos_x
        self.Y = pos_y

        self.direction = E  # N S E W
        self.new_direction = E  # Used for updating the position

        self.is_head = is_head

        self.next_node = None
        self.increase_next_move = False

        self.level = 1

    def set_position(self, pos_x: int, pos_y: int) -> None:
        """Set the position to a given coordinate"""
        next_node_pos = (self.X, self.Y)

        # Update pos
        self.X = pos_x
        self.Y = pos_y

        # Update the next node
        if self.next_node is not None:
            self.next_node.set_position(*next_node_pos)
        elif self.increase_next_move:
            node = SnakeNode(*next_node_pos)
            self.next_node = node
            AllSnakeNodes.append(node)

    def update_position(self) -> None:
        """Updates the position based on the objects direction"""
        next_node_pos = (self.X, self.Y)
        if not self.is_head:
            return None
        if self.direction == N:
            self.Y -= 1
        elif self.direction == S:
            self.Y += 1
        elif self.direction == E:
            self.X += 1
        elif self.new_direction == W:
            self.X -= 1
        else:
            # Default to north if there invalid data in the Direction attr
            report_error(f"SnakeNode.Direction ({self.direction}) is not one of the 4 directions required. ({N}, {S}, {E} or {W})",
                         error_type=TypeError, raise_err=True)

            self.direction = N
            self.update_position()
            return None

        # In theory these if statements should never run at the same time. But lets be honest
        # The effect of them both running wouldn't matter as the position would only be set again
        if self.increase_next_move:
            node = SnakeNode(*next_node_pos)
            self.next_node = node
            AllSnakeNodes.append(node)
            self.increase_next_move = False

        if self.next_node is not None:
            self.next_node.set_position(*next_node_pos)

    def update_direction(self, direction) -> bool:
        """Update the Snakes direction"""
        if direction in [N, S, E, W]:
            # Now we check the the player isn't trying to go back on itself
            if direction == N and self.direction == S:
                return False
            elif direction == S and self.direction == N:
                return False
            elif direction == W and self.direction == E:
                return False
            elif direction == E and self.direction == W:
                return False
            else:
                self.new_direction = direction
                return True
        else:
            report_error(f"SnakeNode.Direction is not one of the 4 directions required. ({N}, {S}, {E} or {W})")
            return False

    def cement_direction(self):
        """Sets the direction to the new direction if they aren't already the same"""
        """This function prevents the snake from going back on itself by pressing two directions in a tick"""
        if self.new_direction != self.direction:
            self.direction = self.new_direction

    def level_up(self):
        """Increase the snakes length and level"""
        if self.next_node is not None:
            self.next_node.level_up()
        else:
            self.increase_next_move = True

        # Increase level
        self.level += 1


class Game:
    """The main game handler"""
    def __init__(self, ms_per_update: int = 100, wrapping: bool = True,
                 console_output: bool = False, get_input: bool = False):
        # Tick speed
        # Runs an update every given milliseconds
        self.update_every_ms = ms_per_update
        self.last_update = 0
        self.board_wrapping = wrapping

        # Board
        self.board = Board()

        self.console_output = console_output

        self.get_input = get_input
        self.snake = SnakeNode(int(self.board.width / 2), int(self.board.height / 2), is_head=True)
        AllSnakeNodes.append(self.snake)

        self.GameOn = False
        self.GameState = OFF

    def start_game(self):
        """Initialise the game variables"""
        self.GameOn = True
        self.GameState = ON
        self.last_update = time()

    def game_single_loop(self):
        """Run a single game loop, still checks for tick"""
        if self.GameOn:
            # Move the snake and then check for collision
            cur_time = time()
            if cur_time - self.last_update > self.update_every_ms / 1000:
                self.snake.cement_direction()
                self.snake.update_position()
                if self.collision_detection():
                    self.GameOn = False
                    self.GameState = OVER
                    return None

                self.last_update = time()

                if self.console_output:
                    os.system('cls')
                    self.print_board()

    def game_loop(self):
        """The main game loop"""
        self.GameOn = True

        self.last_update = time()

        while self.GameOn:
            if self.get_input:
                if keyboard.is_pressed('up'):
                    self.snake.update_direction(N)
                elif keyboard.is_pressed('left'):
                    self.snake.update_direction(W)
                elif keyboard.is_pressed('right'):
                    self.snake.update_direction(E)
                elif keyboard.is_pressed('down'):
                    self.snake.update_direction(S)

            # Move the snake and then check for collision
            cur_time = time()
            if cur_time - self.last_update > self.update_every_ms / 1000:
                self.snake.cement_direction()
                self.snake.update_position()
                if self.collision_detection():
                    self.GameOn = False
                    self.GameState = OVER
                    continue

                self.last_update = time()

                if self.console_output:
                    os.system('cls')
                    self.print_board()

        if self.console_output:
            print("\n\n\n\t\tGAME OVER")

    def collision_detection(self):
        """Check if the snake has collided with anything"""

        # Check for self collision, where the snake collides with it self.
        for node in AllSnakeNodes:
            if self.snake.X == node.X and self.snake.Y == node.Y and node.is_head != True:
                return True

        lookup = self.board.pos_lookup(self.snake.X, self.snake.Y)

        if lookup == A:  # Position available
            return False
        elif lookup is None:  # Obstacle or off board
            # TODO: separate off board and obstacle to allow the snake to wrap around the board
            if self.board_wrapping:
                if self.snake.X >= self.board.width:  # X-wrap from right to left
                    self.snake.set_position(0, self.snake.Y)
                elif self.snake.X < 0:  # X-wrap from left to right
                    self.snake.set_position(self.board.width - 1, self.snake.Y)
                elif self.snake.Y >= self.board.height:  # Y wrap from bottom to top
                    self.snake.set_position(self.snake.X, 0)
                elif self.snake.Y < 0:  # Y wrap from top to bottom
                    self.snake.set_position(self.snake.X, self.board.height - 1)
                else:
                    report_error("None returned when no reason for it is observed", error_type=TypeError, raise_err=True)

                self.collision_detection()
                return False
            else:
                return True

        elif lookup == 0:
            return True
        elif lookup == F:  # Food
            # Snake Levels up
            self.snake.level_up()
            self.board.food_ate()
            return False
        else:
            # Debug and throw error if there is not a valid option
            report_error(f"invalid board option detected.", raise_err=True, error_type=TypeError)

    def print_board(self):
        """Placeholder function for outputting the board"""
        print(f"Level: {self.snake.level}")
        for y in range(self.board.height):
            print(" ", end="")
            for x in range(self.board.width):
                node_found = False

                for snakeNode in AllSnakeNodes:
                    if snakeNode.X == x and snakeNode.Y == y:
                        node_found = True
                        if snakeNode.is_head:
                            print("S", end="  ")
                        else:
                            print("s", end="  ")
                        break

                if not node_found:
                    lookup = self.board.pos_lookup(x, y)
                    if lookup == A:
                        print(".", end="  ")
                    elif lookup == O:
                        print("X", end="  ")
                    elif lookup == F:
                        print("*", end="  ")
                    else:
                        print(str(self.board.pos_lookup(x, y)), end="  ")
            print()
        print()


if __name__ == "__main__":
    g = Game(ms_per_update=250, console_output=True, get_input=True)
    g.game_loop()

