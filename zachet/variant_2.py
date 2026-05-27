START_CELL = "S"
EXIT_CELL = "E"
WALL_CELL = "#"
EMPTY_CELL = "."
PLAYER_CELL = "P"

MOVES = {
    "w": (-1, 0),
    "a": (0, -1),
    "s": (1, 0),
    "d": (0, 1),
}

BASE_MAZE = [
    list("#########"),
    list("#S..#...#"),
    list("#.#.#.#.#"),
    list("#.#...#.#"),
    list("#.#.###.#"),
    list("#...#...#"),
    list("###.#.###"),
    list("#.....E.#"),
    list("#########"),
]


SUPPORTED_COMMANDS = (
    "w - move up",
    "a - move left",
    "s - move down",
    "d - move right",
    "restart - restart the game",
    "exit - quit the game",
)


def copy_maze(maze):
    return [row[:] for row in maze]


def find_cell(maze, target):
    for row_index, row in enumerate(maze):
        for col_index, cell in enumerate(row):
            if cell == target:
                return row_index, col_index

    raise ValueError(f"Cell {target!r} was not found in the maze.")


def create_game_state():
    """Create a new game state."""
    maze = copy_maze(BASE_MAZE)
    player_position = find_cell(maze, START_CELL)
    exit_position = find_cell(maze, EXIT_CELL)

    return {
        "maze": maze,
        "player_position": player_position,
        "exit_position": exit_position,
        "moves_count": 0,
        "finished": False,
    }


def print_intro():
    print("Console Maze")
    print("============")
    print("Move from S to E. Walls are marked with #.")
    print("Available commands:")

    for command in SUPPORTED_COMMANDS:
        print(f"  {command}")


def render_maze(state):
    maze = state["maze"]
    player_row, player_col = state["player_position"]

    print("\nCurrent maze:")

    for row_index, row in enumerate(maze):
        rendered_row = []

        for col_index, cell in enumerate(row):
            is_player_cell = (
                row_index == player_row
                and col_index == player_col
            )
            rendered_row.append(PLAYER_CELL if is_player_cell else cell)

        print(" ".join(rendered_row))

    print(f"Moves made: {state['moves_count']}")


def is_inside_maze(maze, row, col):
    return 0 <= row < len(maze) and 0 <= col < len(maze[row])


def can_move_to(maze, row, col):
    if not is_inside_maze(maze, row, col):
        return False

    return maze[row][col] != WALL_CELL


def get_block_reason(maze, row, col):
    if not is_inside_maze(maze, row, col):
        return "You cannot leave the maze borders."

    if maze[row][col] == WALL_CELL:
        return "You cannot move through a wall."

    return "This move is not allowed."


def move_player(state, command):
    row_change, col_change = MOVES[command]
    current_row, current_col = state["player_position"]
    new_row = current_row + row_change
    new_col = current_col + col_change
    maze = state["maze"]

    if not can_move_to(maze, new_row, new_col):
        return get_block_reason(maze, new_row, new_col)

    state["player_position"] = (new_row, new_col)
    state["moves_count"] += 1

    if state["player_position"] == state["exit_position"]:
        state["finished"] = True
        return "You reached the exit. You win!"

    return "Move accepted."


def ask_restart_after_win():
    while True:
        command = input("Start again? [y/n]: ").strip().lower()

        if command in ("y", "yes"):
            return True

        if command in ("n", "no", "exit"):
            return False

        print("Please enter y or n.")


def handle_command(state, command):
    if command == "restart":
        print("Game restarted.")
        return create_game_state()

    if command == "exit":
        state["finished"] = True
        state["exit_requested"] = True
        return state

    if command not in MOVES:
        print("Unknown command. Use w, a, s, d, restart or exit.")
        return state

    print(move_player(state, command))
    return state


def play_game():
    print_intro()
    state = create_game_state()
    state["exit_requested"] = False

    while True:
        render_maze(state)

        if state["finished"]:
            if state.get("exit_requested"):
                print("Goodbye!")
                return

            if ask_restart_after_win():
                state = create_game_state()
                state["exit_requested"] = False
                continue

            print("Goodbye!")
            return

        command = input("Enter command: ").strip().lower()
        state = handle_command(state, command)


if __name__ == "__main__":
    play_game()
