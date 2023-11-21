from solver import Board, Solver


class GeneratorBackend:
    def is_solvable(self, board: Board) -> bool:
        return Solver(board).solve()

    def can_remove_number(self, board: Board, location: tuple[int, int] | int) -> bool | None:
        if board[location] == 0:
            return None
        board_copy = board.copy()
        board_copy[location] = 0
        return self.is_solvable(board_copy)

    def get_removable_numbers(self, board: Board) -> list[bool | None]:
        return [self.can_remove_number(board, idx) for idx in range(81)]

    def get_removable_numbers_nested(self, board: Board) -> list[list[bool | None]]:
        return Board.flat_to_nested(self.get_removable_numbers(board))
