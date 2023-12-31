import csv
from multiprocessing.pool import Pool
import os
import random
from typing import TYPE_CHECKING, Iterable, Literal

if TYPE_CHECKING:
    from _typeshed import SupportsWrite, SupportsRead

from solver import Board, Solver, SolverMethod, BoardClass

BASE_BOARD = Board([
    1,2,3,4,5,6,7,8,9,
    4,5,6,7,8,9,1,2,3,
    7,8,9,1,2,3,4,5,6,
    5,6,4,8,9,7,2,3,1,
    2,3,1,5,6,4,8,9,7,
    8,9,7,2,3,1,5,6,4,
    3,1,2,9,7,8,6,4,5,
    9,7,8,6,4,5,3,1,2,
    6,4,5,3,1,2,9,7,8,
])
def _check_base_board():
    s = Solver(BASE_BOARD)
    assert s.check_validity()
    assert s.is_solved()

_check_base_board()


class GeneratorBackend:
    def find_hard_sudoku_parallel(
            self, max_tries: int = 1_000,
            initial_n: int = 12, initial_step: int = 4,
            print_every: int = 0, pretty_progress=False, cores=None,
            use_sys_rand = False):
        if cores is None:
            cores = (os.cpu_count() or 4) // 2
        sys_rand = random.SystemRandom()
        args_list: list[tuple[int, random.Random, int, int, int, bool]] = [
            (max_tries // cores,  # max_tries
             'system' if use_sys_rand else random.Random(sys_rand.getrandbits(32)),
             initial_n, initial_step,
             # only print from thread 1
             print_every if i == 0 else 0, pretty_progress)
            for i in range(cores)]
        with Pool(cores) as ppool:
            results_it = ppool.imap_unordered(self._find_hard_sudoku_worker, args_list)
            for res in results_it:
                if res is not None:
                    return res
        if pretty_progress and print_every != 0:
            # Ensure that we're on a new line as printing process might
            # not have been the one to find it,
            # so it might've been .terminated()d without printing \n
            print()
        return None

    def _find_hard_sudoku_worker(self, args: tuple[int, random.Random | Literal['system'], int, int, int, bool]):
        return self.find_hard_sudoku(*args)

    def find_hard_sudoku(self, max_tries: int = 1_000, r: random.Random | Literal['system'] = None,
                         initial_n: int = 12, initial_step: int = 4,
                         print_every: int = 0, pretty_progress=False):
        if r is None:
            r = random.Random()
        if r == 'system':
            r = random.SystemRandom()
        if print_every != 0 and pretty_progress:
            def on_done(): print()
        else:
            def on_done(): pass
        for i in range(max_tries):
            if print_every != 0 and i % print_every == 0:
                if pretty_progress:
                    # don't overwrite prev line
                    start_s = '' if i == 0 else '\r'
                    print(f'{start_s}{i/max_tries*100:>4.1f}% ({i}/{max_tries})', end='')
                elif i != 0:
                    print(f'{i/max_tries*100:>4.1f}% progress ({i}/{max_tries} done)')
            board = BASE_BOARD.copy()
            initial_rm = r.sample(tuple(range(81)), initial_n)
            for pos in initial_rm:
                board[pos] = 0
            match self.classify_board(board, debug=False):
                case BoardClass.unsolvable:
                    continue
                case BoardClass.hard:
                    on_done()
                    return board
            prev = board.copy()
            rm_now: list[int] | None = None
            for j in range(0, 80, initial_step):
                rm_now = r.sample(tuple(range(81)), initial_n)
                for pos in rm_now:
                    board[pos] = 0
                match self.classify_board(board, debug=False):
                    case BoardClass.hard:
                        on_done()
                        return board
                    case BoardClass.unsolvable:
                        break  # try to backtrack
                prev = board
                board = board.copy()
            # try to backtrack
            # assert self.classify_board(board) == BoardClass.unsolvable
            # assert self.classify_board(prev) == BoardClass.easy
            # assert rm_now
            board = prev  # load backup prev board
            for rm in rm_now:
                board[rm] = 0
                match self.classify_board(board, debug=False):
                    case BoardClass.hard:
                        on_done()
                        return board
                    case BoardClass.unsolvable:
                        break  # backtrack failed - no hard 'region'
            # Here, no hard 'region' so nothing to return so try next
            # assert self.classify_board(board) == BoardClass.unsolvable
        on_done()
        return None

    def is_easy(self, b: Board):
        return Solver(b).solve_f(include=[SolverMethod.one_occurrence_in])

    def classify_board(self, b: Board, debug: bool = True) -> BoardClass:
        return Solver(b, debug).classify_board()

    def load_board_csv(self, f: Iterable[str]) -> Board:
        reader = csv.reader(f, csv.unix_dialect)
        rows = [[int(sv) for sv in s_row] for s_row in reader]
        grid_flat = Board.nested_to_flat(rows)
        return Board(grid_flat)

    def store_board_csv(self, f: 'SupportsWrite[str]', board: Board | list[int]):
        grid_flat = board.grid if isinstance(board, Board) else board
        rows = Board.to_printable_order(Board.flat_to_nested(grid_flat))
        # universal newline on python so use unix dialect
        # with \n (\r\n would be converted to \n\n)
        csv.writer(f, csv.unix_dialect).writerows(rows)

    def solve_board(self, board: Board) -> tuple[bool, Board]:
        s = Solver(board)
        solvable = s.solve()
        return solvable, Board([sq.value for sq in s.grid])

    def find_boards_matching_parallel(
            self, removal_order: list[int | tuple[int, int]],
            cores: int = None, want_min: int = 8, stop_after=1_000,
            print_progress=0) -> tuple[bool, Board]:
        solved, best_i, best_b = self._find_boards_matching_parallel(
            removal_order, cores, want_min, stop_after, print_progress)
        return solved, best_b

    def _find_boards_matching_parallel(
            self, removal_order: list[int | tuple[int, int]],
            cores: int = None, want_min: int = 8, stop_after=1_000,
            print_progress=0) -> tuple[bool, int, Board]:
        if cores is None:
            cores = (os.cpu_count() or 4) // 2
        sys_rand = random.SystemRandom()
        with Pool(cores) as ppool:
            async_result_list = [
                ppool.apply_async(
                    self._find_boards_matching, args=(
                        removal_order, want_min, stop_after // cores,
                        random.Random(sys_rand.getrandbits(32)),
                        print_progress if i == 0 else 0
                    )  # only print from 1 process
                ) for i in range(cores)
            ]
            result_list = [ar.get() for ar in async_result_list]
        return self._merge_proc_results(result_list)

    def _merge_proc_results(self, results: list[tuple[bool, int, Board | None]]) -> tuple[bool, int, Board]:
        def largest_i(r: tuple[bool, int, Board]):
            return r[1]
        return max([r for r in results if r[2] is not None],
                   key=largest_i, default=(False, 0, None))

    def find_boards_matching(self, removal_order: list[int | tuple[int, int]],
                             want_min: int = 8, stop_after=1_000, r: random.Random = None,
                             print_progress=0) -> tuple[bool, Board]:
        solved, best_i, best_b = self._find_boards_matching(
            removal_order, want_min, stop_after, r, print_progress)
        return solved, best_b

    def _find_boards_matching(self, removal_order: list[int | tuple[int, int]],
                             want_min: int = 8, stop_after=1_000, r: random.Random = None,
                             print_progress=0) -> tuple[bool, int, Board]:
        assert len(removal_order) >= want_min
        best_board = None
        best_i = 0
        for i in range(stop_after):
            if print_progress != 0 and i != 0 and i % print_progress == 0:
                print(f'{i/stop_after*100:>4.1f}% progress ({i}/{stop_after} done)')
            rand_board = self.generate_random_board(r)
            # remove minimum acceptable things (optimisation)
            for rm_pos in removal_order[:want_min]:
                rand_board[rm_pos] = 0
            if not self.is_solvable(rand_board): continue
            # TODO: optim: remove 2/3/4 at a time then narrow it down? - more complex
            for rm_i, rm_pos in enumerate(removal_order[want_min:], start=want_min):
                was_at_pos = rand_board[rm_pos]
                rand_board[rm_pos] = 0
                if not self.is_solvable(rand_board):
                    last_i_solvable = rm_i - 1
                    rand_board[rm_pos] = was_at_pos  # restore it (need curr num so that its solvable)
                    break
            else:  # (meaning if no break), fully solvable
                last_i_solvable = len(removal_order) - 1
            # if none yet or better than prev best...
            if best_board is None or last_i_solvable > best_i:
                # ... set this as best
                best_i = last_i_solvable
                best_board = rand_board
            if best_i >= len(removal_order) - 1:
                assert best_i == len(removal_order) - 1
                return True, best_i, best_board  # fulfilled request
        return False, best_i, best_board

    def _with_x_col_shuffled(self, board: Board, x0: int, new_cols: list[int]):
        new_board = board.copy()
        for xi, new_xi in enumerate(new_cols):
            old_x = x0 + xi
            new_x = x0 + new_xi
            for y in range(9):
                new_board[new_x, y] = board[old_x, y]
        return new_board

    def _with_y_row_shuffled(self, board: Board, y0: int, new_rows: list[int]):
        new_board = board.copy()
        for yi, new_yi in enumerate(new_rows):
            old_y = y0 + yi
            new_y = y0 + new_yi
            for x in range(9):
                new_board[new_y, x] = board[old_y, x]
        return new_board

    # [[nodiscard]]
    def _shuffled_x_cols_in_x_region(self, board: Board, r: random.Random, r_idx_x: int) -> Board:
        x0 = r_idx_x * 3
        new_cols = [0, 1, 2]
        r.shuffle(new_cols)
        return self._with_x_col_shuffled(board, x0, new_cols)

    # [[nodiscard]]
    def _shuffled_y_rows_in_y_region(self, board: Board, r: random.Random, r_idx_y: int) -> Board:
        y0 = r_idx_y * 3
        new_rows = [0, 1, 2]
        r.shuffle(new_rows)
        return self._with_y_row_shuffled(board, y0, new_rows)

    # [[nodiscard]]
    def _shuffled_x_region_cols(self, board: Board, r: random.Random) -> Board:
        new_cols_nested = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        # shuffle the nested list so that the regions stay together, then flatten
        r.shuffle(new_cols_nested)
        new_cols_flat = [item for sublist in new_cols_nested for item in sublist]
        return self._with_x_col_shuffled(board, 0, new_cols_flat)

    # [[nodiscard]]
    def _shuffled_y_region_rows(self, board: Board, r: random.Random) -> Board:
        new_rows_nested = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        # shuffle the nested list so that the regions stay together, then flatten
        r.shuffle(new_rows_nested)
        new_cols_flat = [item for sublist in new_rows_nested for item in sublist]
        return self._with_y_row_shuffled(board, 0, new_cols_flat)

    def _shuffled_numbers(self, board: Board, r: random.Random):
        old_to_new_nums = [*range(1, 9+1)]
        r.shuffle(old_to_new_nums)
        # `- 1` to convert from 1-9 to 0-8
        return Board([0 if board[i] == 0 else old_to_new_nums[board[i] - 1] for i in range(81)])

    def generate_random_board(self, r: random.Random = None):
        return self.shuffled_board(BASE_BOARD, r)

    def shuffled_board(self, board: Board, r: random.Random = None):
        if r is None:
            r = random.Random()
        # we start from a known solution and try and change it in ways
        # that preserve the property of being a sudoku solution
        # I'm not sure if this can generate all possible sudoku solutions
        # but it's good enough
        board = board.copy()
        for rx in range(3):
            board = self._shuffled_x_cols_in_x_region(board, r, rx)
        for ry in range(3):
            board = self._shuffled_y_rows_in_y_region(board, r, ry)
        board = self._shuffled_x_region_cols(board, r)
        board = self._shuffled_y_region_rows(board, r)
        board = self._shuffled_numbers(board, r)  # not sure if this is necessary
        return board

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
