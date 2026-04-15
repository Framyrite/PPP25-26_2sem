from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple, Type

BOARD_SIZE = 8
FILES = "abcdefgh"
RANKS = "12345678"

RESET = "\033[0m"
BOLD = "\033[1m"

WHITE_PIECE = "\033[38;5;231m"
BLACK_PIECE = "\033[38;5;16m"

LIGHT_CELL = "\033[48;5;255m"
DARK_CELL = "\033[48;5;110m"
HIGHLIGHT_CELL = "\033[48;5;226m"
THREAT_CELL = "\033[48;5;203m"

TEXT_DARK = "\033[38;5;16m"
TEXT_LIGHT = "\033[38;5;231m"


@dataclass
class Move:
    start: Tuple[int, int]
    end: Tuple[int, int]
    piece_name: str
    piece_color: str
    captured_piece: Optional["Piece"] = None
    was_first_move: bool = False
    prev_en_passant_target: Optional[Tuple[int, int]] = None
    is_en_passant: bool = False
    en_passant_captured_pos: Optional[Tuple[int, int]] = None
    promotion_from: Optional[str] = None
    promotion_to: Optional[str] = None
    rook_move: Optional[Tuple[Tuple[int, int], Tuple[int, int], bool]] = None

    def to_notation(self) -> str:
        return f"{coord_to_str(self.start)}->{coord_to_str(self.end)}"


class Piece:
    symbol = "?"
    value_name = "Piece"

    def __init__(self, color: str, position: Tuple[int, int]):
        self.color = color
        self.position = position
        self.has_moved = False

    @property
    def enemy_color(self) -> str:
        return "black" if self.color == "white" else "white"

    def copy(self) -> "Piece":
        cls: Type[Piece] = self.__class__
        new_piece = cls(self.color, self.position)
        new_piece.has_moved = self.has_moved
        return new_piece

    def display(self) -> str:
        return self.symbol.upper() if self.color == "white" else self.symbol.lower()

    def pretty_symbol(self) -> str:
        symbols = {
            ("white", "King"): "♔",
            ("white", "Queen"): "♕",
            ("white", "Rook"): "♖",
            ("white", "Bishop"): "♗",
            ("white", "Knight"): "♘",
            ("white", "Pawn"): "♙",
            ("black", "King"): "♚",
            ("black", "Queen"): "♛",
            ("black", "Rook"): "♜",
            ("black", "Bishop"): "♝",
            ("black", "Knight"): "♞",
            ("black", "Pawn"): "♟",
            ("white", "Chancellor"): "C",
            ("white", "Archbishop"): "A",
            ("white", "Camel"): "M",
            ("black", "Chancellor"): "c",
            ("black", "Archbishop"): "a",
            ("black", "Camel"): "m",
        }
        return symbols.get((self.color, self.value_name), self.display())

    def get_candidate_moves(self, board: "Board") -> List[Tuple[int, int]]:
        raise NotImplementedError

    def get_attack_squares(self, board: "Board") -> List[Tuple[int, int]]:
        return self.get_candidate_moves(board)


class SlidingPiece(Piece):
    directions: List[Tuple[int, int]] = []

    def get_candidate_moves(self, board: "Board") -> List[Tuple[int, int]]:
        moves = []
        row, col = self.position
        for dr, dc in self.directions:
            r, c = row + dr, col + dc
            while board.is_in_bounds((r, c)):
                target = board.get_piece((r, c))
                if target is None:
                    moves.append((r, c))
                else:
                    if target.color != self.color:
                        moves.append((r, c))
                    break
                r += dr
                c += dc
        return moves


class King(Piece):
    symbol = "k"
    value_name = "King"

    def get_candidate_moves(self, board: "Board") -> List[Tuple[int, int]]:
        moves = []
        row, col = self.position
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                pos = (row + dr, col + dc)
                if board.is_in_bounds(pos):
                    target = board.get_piece(pos)
                    if target is None or target.color != self.color:
                        moves.append(pos)
        moves.extend(board.get_castling_moves(self))
        return moves

    def get_attack_squares(self, board: "Board") -> List[Tuple[int, int]]:
        attacks = []
        row, col = self.position
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                pos = (row + dr, col + dc)
                if board.is_in_bounds(pos):
                    attacks.append(pos)
        return attacks


class Queen(SlidingPiece):
    symbol = "q"
    value_name = "Queen"
    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, -1), (-1, 1), (1, -1), (1, 1),
    ]


class Rook(SlidingPiece):
    symbol = "r"
    value_name = "Rook"
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]


class Bishop(SlidingPiece):
    symbol = "b"
    value_name = "Bishop"
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]


class Knight(Piece):
    symbol = "n"
    value_name = "Knight"

    def get_candidate_moves(self, board: "Board") -> List[Tuple[int, int]]:
        moves = []
        row, col = self.position
        jumps = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1),
        ]
        for dr, dc in jumps:
            pos = (row + dr, col + dc)
            if board.is_in_bounds(pos):
                target = board.get_piece(pos)
                if target is None or target.color != self.color:
                    moves.append(pos)
        return moves


class Pawn(Piece):
    symbol = "p"
    value_name = "Pawn"

    def direction(self) -> int:
        return -1 if self.color == "white" else 1

    def start_row(self) -> int:
        return 6 if self.color == "white" else 1

    def get_candidate_moves(self, board: "Board") -> List[Tuple[int, int]]:
        moves = []
        row, col = self.position

        one = (row + self.direction(), col)
        if board.is_in_bounds(one) and board.get_piece(one) is None:
            moves.append(one)
            two = (row + 2 * self.direction(), col)
            if row == self.start_row() and board.is_in_bounds(two) and board.get_piece(two) is None:
                moves.append(two)

        for dc in (-1, 1):
            diag = (row + self.direction(), col + dc)
            if not board.is_in_bounds(diag):
                continue
            target = board.get_piece(diag)
            if target is not None and target.color != self.color:
                moves.append(diag)

        if board.en_passant_target is not None:
            ep_row, ep_col = board.en_passant_target
            if ep_row == row + self.direction() and abs(ep_col - col) == 1:
                moves.append(board.en_passant_target)

        return moves

    def get_attack_squares(self, board: "Board") -> List[Tuple[int, int]]:
        row, col = self.position
        attacks = []
        for dc in (-1, 1):
            pos = (row + self.direction(), col + dc)
            if board.is_in_bounds(pos):
                attacks.append(pos)
        return attacks


class Chancellor(Piece):
    symbol = "c"
    value_name = "Chancellor"

    def get_candidate_moves(self, board: "Board") -> List[Tuple[int, int]]:
        rook_like = Rook(self.color, self.position).get_candidate_moves(board)
        knight_like = Knight(self.color, self.position).get_candidate_moves(board)
        return deduplicate_positions(rook_like + knight_like)


class Archbishop(Piece):
    symbol = "a"
    value_name = "Archbishop"

    def get_candidate_moves(self, board: "Board") -> List[Tuple[int, int]]:
        bishop_like = Bishop(self.color, self.position).get_candidate_moves(board)
        knight_like = Knight(self.color, self.position).get_candidate_moves(board)
        return deduplicate_positions(bishop_like + knight_like)


class Camel(Piece):
    symbol = "m"
    value_name = "Camel"

    def get_candidate_moves(self, board: "Board") -> List[Tuple[int, int]]:
        moves = []
        row, col = self.position
        jumps = [
            (-3, -1), (-3, 1), (3, -1), (3, 1),
            (-1, -3), (-1, 3), (1, -3), (1, 3),
        ]
        for dr, dc in jumps:
            pos = (row + dr, col + dc)
            if board.is_in_bounds(pos):
                target = board.get_piece(pos)
                if target is None or target.color != self.color:
                    moves.append(pos)
        return moves


class Board:
    def __init__(self) -> None:
        self.grid: List[List[Optional[Piece]]] = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.history: List[Move] = []
        self.en_passant_target: Optional[Tuple[int, int]] = None
        self.mode = "classic"

    def is_in_bounds(self, pos: Tuple[int, int]) -> bool:
        row, col = pos
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def get_piece(self, pos: Tuple[int, int]) -> Optional[Piece]:
        row, col = pos
        return self.grid[row][col]

    def set_piece(self, pos: Tuple[int, int], piece: Optional[Piece]) -> None:
        row, col = pos
        self.grid[row][col] = piece
        if piece is not None:
            piece.position = pos

    def place_piece(self, piece: Piece) -> None:
        self.set_piece(piece.position, piece)

    def setup_classic(self) -> None:
        self.mode = "classic"
        self.grid = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.history.clear()
        self.en_passant_target = None

        back_rank = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col, cls in enumerate(back_rank):
            self.place_piece(cls("black", (0, col)))
            self.place_piece(cls("white", (7, col)))

        for col in range(BOARD_SIZE):
            self.place_piece(Pawn("black", (1, col)))
            self.place_piece(Pawn("white", (6, col)))

    def setup_fantasy(self) -> None:
        self.setup_classic()
        self.mode = "fantasy"
        self.set_piece((7, 1), Chancellor("white", (7, 1)))
        self.set_piece((7, 2), Camel("white", (7, 2)))
        self.set_piece((7, 6), Archbishop("white", (7, 6)))
        self.set_piece((0, 1), Chancellor("black", (0, 1)))
        self.set_piece((0, 2), Camel("black", (0, 2)))
        self.set_piece((0, 6), Archbishop("black", (0, 6)))

    def display(self, highlighted: Optional[List[Tuple[int, int]]] = None) -> None:
        highlighted = highlighted or []
        highlight_set = set(highlighted)
        threatened_white = set(self.get_threatened_positions("white"))
        threatened_black = set(self.get_threatened_positions("black"))

        print()
        print(f"{BOLD}      a   b   c   d   e   f   g   h{RESET}")
        print("    ┌───┬───┬───┬───┬───┬───┬───┬───┐")

        for row in range(BOARD_SIZE):
            line = f"{BOLD} {8 - row} {RESET} │"
            for col in range(BOARD_SIZE):
                pos = (row, col)
                piece = self.get_piece(pos)

                base_bg = LIGHT_CELL if (row + col) % 2 == 0 else DARK_CELL
                empty_fg = TEXT_DARK if (row + col) % 2 == 0 else TEXT_LIGHT

                if pos in highlight_set and piece is None:
                    base_bg = HIGHLIGHT_CELL
                    empty_fg = TEXT_DARK

                if piece is not None and (
                    (piece.color == "white" and pos in threatened_white)
                    or (piece.color == "black" and pos in threatened_black)
                ):
                    base_bg = THREAT_CELL

                if piece is None:
                    symbol = "•" if pos in highlight_set else " "
                    line += f"{base_bg}{empty_fg} {symbol} {RESET}│"
                else:
                    piece_color = WHITE_PIECE if piece.color == "white" else BLACK_PIECE
                    line += f"{base_bg}{piece_color}{BOLD} {piece.pretty_symbol()} {RESET}│"

            line += f" {BOLD}{8 - row}{RESET}"
            print(line)

            if row != BOARD_SIZE - 1:
                print("    ├───┼───┼───┼───┼───┼───┼───┼───┤")

        print("    └───┴───┴───┴───┴───┴───┴───┴───┘")
        print(f"{BOLD}      a   b   c   d   e   f   g   h{RESET}")
        print()

    def get_all_pieces(self, color: Optional[str] = None) -> List[Piece]:
        pieces = []
        for row in self.grid:
            for piece in row:
                if piece is None:
                    continue
                if color is None or piece.color == color:
                    pieces.append(piece)
        return pieces

    def find_king(self, color: str) -> Optional[King]:
        for piece in self.get_all_pieces(color):
            if isinstance(piece, King):
                return piece
        return None

    def is_square_attacked(self, pos: Tuple[int, int], by_color: str) -> bool:
        for piece in self.get_all_pieces(by_color):
            if pos in piece.get_attack_squares(self):
                return True
        return False

    def is_in_check(self, color: str) -> bool:
        king = self.find_king(color)
        if king is None:
            return False
        return self.is_square_attacked(king.position, king.enemy_color)

    def get_threatened_positions(self, color: str) -> List[Tuple[int, int]]:
        threatened = []
        for piece in self.get_all_pieces(color):
            if self.is_square_attacked(piece.position, piece.enemy_color):
                threatened.append(piece.position)
        return threatened

    def get_castling_moves(self, king: King) -> List[Tuple[int, int]]:
        if king.has_moved or self.is_in_check(king.color):
            return []
        row, col = king.position
        if col != 4:
            return []

        result = []
        for rook_col, step, through_cols in ((7, 1, [5, 6]), (0, -1, [3, 2])):
            rook = self.get_piece((row, rook_col))
            if not isinstance(rook, Rook) or rook.color != king.color or rook.has_moved:
                continue
            if any(self.get_piece((row, c)) is not None for c in through_cols):
                continue
            squares_to_check = [(row, col + step), (row, col + 2 * step)]
            if any(self.is_square_attacked(square, king.enemy_color) for square in squares_to_check):
                continue
            result.append((row, col + 2 * step))
        return result

    def get_legal_moves_for_piece(self, piece: Piece) -> List[Tuple[int, int]]:
        legal_moves = []
        for target in piece.get_candidate_moves(self):
            move = self.make_move(piece.position, target)
            if move is None:
                continue
            if not self.is_in_check(piece.color):
                legal_moves.append(target)
            self.undo_last_move()
        return legal_moves

    def has_legal_move(self, color: str) -> bool:
        for piece in self.get_all_pieces(color):
            if self.get_legal_moves_for_piece(piece):
                return True
        return False

    def make_move(
        self,
        start: Tuple[int, int],
        end: Tuple[int, int],
        promotion_choice: str = "Q",
    ) -> Optional[Move]:
        piece = self.get_piece(start)
        if piece is None:
            return None
        if end not in piece.get_candidate_moves(self):
            return None

        old_en_passant = self.en_passant_target
        self.en_passant_target = None

        move = Move(
            start=start,
            end=end,
            piece_name=piece.value_name,
            piece_color=piece.color,
            captured_piece=None,
            was_first_move=not piece.has_moved,
            prev_en_passant_target=old_en_passant,
        )

        target_piece = self.get_piece(end)
        if target_piece is not None:
            move.captured_piece = target_piece.copy()

        if isinstance(piece, Pawn) and target_piece is None and start[1] != end[1] and old_en_passant == end:
            captured_pos = (start[0], end[1])
            captured_piece = self.get_piece(captured_pos)
            if isinstance(captured_piece, Pawn) and captured_piece.color != piece.color:
                move.is_en_passant = True
                move.en_passant_captured_pos = captured_pos
                move.captured_piece = captured_piece.copy()
                self.set_piece(captured_pos, None)

        if isinstance(piece, King) and abs(end[1] - start[1]) == 2:
            if end[1] > start[1]:
                rook_start = (start[0], 7)
                rook_end = (start[0], 5)
            else:
                rook_start = (start[0], 0)
                rook_end = (start[0], 3)
            rook = self.get_piece(rook_start)
            if isinstance(rook, Rook):
                move.rook_move = (rook_start, rook_end, rook.has_moved)
                self.set_piece(rook_end, rook)
                self.set_piece(rook_start, None)
                rook.has_moved = True

        self.set_piece(end, piece)
        self.set_piece(start, None)
        piece.has_moved = True

        if isinstance(piece, Pawn) and abs(end[0] - start[0]) == 2:
            middle_row = (start[0] + end[0]) // 2
            self.en_passant_target = (middle_row, start[1])

        if isinstance(piece, Pawn) and (end[0] == 0 or end[0] == 7):
            promoted = self.create_promotion_piece(piece.color, end, promotion_choice)
            move.promotion_from = "Pawn"
            move.promotion_to = promoted.value_name
            promoted.has_moved = True
            self.set_piece(end, promoted)

        self.history.append(move)
        return move

    def undo_last_move(self) -> bool:
        if not self.history:
            return False

        move = self.history.pop()
        moved_piece = self.get_piece(move.end)
        if moved_piece is None:
            return False

        if move.promotion_from is not None:
            moved_piece = Pawn(move.piece_color, move.end)
            moved_piece.has_moved = True

        self.set_piece(move.start, moved_piece)
        moved_piece.has_moved = not move.was_first_move
        self.set_piece(move.end, None)

        if move.captured_piece is not None:
            if move.is_en_passant and move.en_passant_captured_pos is not None:
                self.set_piece(move.en_passant_captured_pos, move.captured_piece)
            else:
                self.set_piece(move.end, move.captured_piece)

        if move.rook_move is not None:
            rook_start, rook_end, rook_was_moved = move.rook_move
            rook = self.get_piece(rook_end)
            if rook is not None:
                self.set_piece(rook_start, rook)
                self.set_piece(rook_end, None)
                rook.has_moved = rook_was_moved

        self.en_passant_target = move.prev_en_passant_target
        return True

    def create_promotion_piece(self, color: str, pos: Tuple[int, int], choice: str) -> Piece:
        classic_mapping = {
            "Q": Queen,
            "R": Rook,
            "B": Bishop,
            "N": Knight,
        }

        fantasy_mapping = {
            "Q": Queen,
            "R": Rook,
            "B": Bishop,
            "N": Knight,
            "C": Chancellor,
            "A": Archbishop,
            "M": Camel,
        }

        mapping = fantasy_mapping if self.mode == "fantasy" else classic_mapping
        cls = mapping.get(choice.upper(), Queen)
        return cls(color, pos)


class Game:
    def __init__(self) -> None:
        self.board = Board()
        self.current_player = "white"

    def setup(self) -> None:
        print(f"{BOLD}Добро пожаловать в шахматы{RESET}")
        print("Выберите режим: classic / fantasy")

        while True:
            mode = input("> ").strip().lower()

            if mode == "classic":
                self.board.setup_classic()
                return

            if mode == "fantasy":
                self.board.setup_fantasy()
                return

            print("Некорректный режим. Введите только: classic или fantasy.")

    def switch_player(self) -> None:
        self.current_player = "black" if self.current_player == "white" else "white"

    def print_status(self) -> None:
        enemy = "black" if self.current_player == "white" else "white"
        if self.board.is_in_check(self.current_player):
            print(f"{BOLD}Шах игроку {self.current_player}!{RESET}")
        if not self.board.has_legal_move(self.current_player):
            if self.board.is_in_check(self.current_player):
                print(f"{BOLD}Мат. Победил {enemy}.{RESET}")
            else:
                print(f"{BOLD}Пат.{RESET}")
            raise SystemExit

    def ask_promotion_choice(self) -> str:
        allowed = ["Q", "R", "B", "N"]
        names = {
            "Q": "Ферзь",
            "R": "Ладья",
            "B": "Слон",
            "N": "Конь",
            "C": "Канцлер",
            "A": "Архиепископ",
            "M": "Верблюд",
        }

        if self.board.mode == "fantasy":
            allowed.extend(["C", "A", "M"])

        print("Превращение пешки.")
        for key in allowed:
            print(f"{key} - {names[key]}")

        while True:
            choice = input("Введите букву фигуры > ").strip().upper() or "Q"
            if choice in allowed:
                return choice
            print("Недопустимый выбор для текущего режима.")

    def run(self) -> None:
        self.setup()
        while True:
            self.board.display()
            self.print_status()
            print(f"{BOLD}Ход: {self.current_player}{RESET}")
            print("Команды: move e2 e4 | hint e2 | undo | history | exit")
            raw = input("> ").strip()
            if not raw:
                continue

            parts = raw.split()
            command = parts[0].lower()

            if command == "exit":
                print("Выход из игры.")
                return

            if command == "history":
                if not self.board.history:
                    print("История пуста.")
                else:
                    for idx, move in enumerate(self.board.history, start=1):
                        extra = ""
                        if move.promotion_to:
                            extra = f" (превращение в {move.promotion_to})"
                        elif move.is_en_passant:
                            extra = " (взятие на проходе)"
                        elif move.rook_move:
                            extra = " (рокировка)"
                        print(f"{idx}. {move.piece_color} {move.piece_name}: {move.to_notation()}{extra}")
                continue

            if command == "undo":
                if self.board.undo_last_move():
                    self.switch_player()
                    print("Последний ход отменён.")
                else:
                    print("История пуста.")
                continue

            if command == "hint" and len(parts) == 2:
                try:
                    pos = parse_coord(parts[1])
                except ValueError as exc:
                    print(exc)
                    continue
                piece = self.board.get_piece(pos)
                if piece is None:
                    print("На этой клетке нет фигуры.")
                    continue
                if piece.color != self.current_player:
                    print("Это не ваша фигура.")
                    continue
                moves = self.board.get_legal_moves_for_piece(piece)
                print("Допустимые ходы:", ", ".join(coord_to_str(m) for m in moves) or "нет")
                self.board.display(highlighted=moves)
                continue

            if command == "move" and len(parts) >= 3:
                try:
                    start = parse_coord(parts[1])
                    end = parse_coord(parts[2])
                except ValueError as exc:
                    print(exc)
                    continue

                piece = self.board.get_piece(start)
                if piece is None:
                    print("На стартовой клетке нет фигуры.")
                    continue
                if piece.color != self.current_player:
                    print("Сейчас ход другого игрока.")
                    continue

                legal_moves = self.board.get_legal_moves_for_piece(piece)
                if end not in legal_moves:
                    print("Недопустимый ход.")
                    continue

                promotion_choice = "Q"
                if isinstance(piece, Pawn) and (end[0] == 0 or end[0] == 7):
                    promotion_choice = self.ask_promotion_choice()

                move = self.board.make_move(start, end, promotion_choice=promotion_choice)
                if move is None:
                    print("Ход не выполнен.")
                    continue

                self.switch_player()
                continue

            print("Неизвестная команда.")


def parse_coord(text: str) -> Tuple[int, int]:
    text = text.strip().lower()
    if len(text) != 2 or text[0] not in FILES or text[1] not in RANKS:
        raise ValueError("Координата должна быть в формате e2")
    col = FILES.index(text[0])
    row = 8 - int(text[1])
    return row, col


def coord_to_str(pos: Tuple[int, int]) -> str:
    row, col = pos
    return f"{FILES[col]}{8 - row}"


def deduplicate_positions(positions: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    result = []
    seen = set()
    for pos in positions:
        if pos not in seen:
            result.append(pos)
            seen.add(pos)
    return result


if __name__ == "__main__":
    game = Game()
    game.run()
