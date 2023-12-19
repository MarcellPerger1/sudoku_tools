from pathlib import Path

from backend import GeneratorBackend, Board
import tkinter as tk
from tkinter import filedialog

from solver import Solver, SolverMethod


def idx_to_pos(idx: int) -> tuple[int, int]:
    return idx % 9, idx // 9
def pos_to_idx(pos: tuple[int, int]):
    return pos[0] + pos[1] * 9


class TkinterFrontendApp:
    def __init__(self, orig_board: Board = None, curr_board: Board = None):
        self.backend = GeneratorBackend()
        if curr_board is None:
            self.orig_board = (orig_board if orig_board is not None
                               else self.backend.generate_random_board())
            self.board = self.orig_board.copy()
        else:
            self.orig_board = (orig_board if orig_board is not None
                               else self._curr_to_orig_board(curr_board))
            self.board = curr_board.copy()
        self.root = tk.Tk()
        self.root.title('Sudoku generator frontend (tkinter)')
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)

        self.table_container = tk.Frame(self.root, highlightthickness=1, highlightbackground='black')
        self._create_9x9_table()
        self.table_container.grid(row=1,column=1, padx=5, pady=5., columnspan=2)
        self.easy_lb = tk.Label(self.root, text='Easy: yes', fg='green')
        self.easy_lb.grid(row=2, columnspan=2, column=1)
        self.button_save_csv = tk.Button(self.root, text='Save as CSV', command=self.save_as_csv)
        self.button_save_csv.grid(row=3, column=1)

        self.update_colors()
        self.root.bind_all('<Button-1>', self.onclick)
        self.root.bind_all('<Button-3>', self.on_right_click)
        self._update_info()

    def _update_info(self):
        is_easy = self.backend.is_easy(self.board)
        if is_easy:
            self.easy_lb.configure(text='Easy: yes', fg='green')
        else:
            self.easy_lb.configure(text='Easy: NO', fg='orange')

    def _curr_to_orig_board(self, curr_board):
        is_solvable, solution = self.backend.solve_board(curr_board)
        if not is_solvable:
            raise ValueError("only curr_board was specified and its "
                             "not solvable so there is no orig_board")
        return solution

    def get_table_entry(self, x: int, y: int):
        return self.tb_elements[pos_to_idx((x, y))]

    def _create_9x9_table(self):
        self.tb_elements = []
        for i in range(9):
            self.table_container.columnconfigure(i, minsize=25, weight=1)
            self.table_container.rowconfigure(i, minsize=25, weight=1)
        for x in range(9):
            for y in range(9):
                num_label = tk.Label(
                    self.table_container, text=str(self.board[(x,y)]),
                    highlightthickness=1, highlightbackground='black')
                num_label.grid(row=x, column=y, sticky='NSEW')
                self.tb_elements.append(num_label)

    def update_colors(self):
        removables = self.backend.get_removable_numbers(self.board)
        for i in range(81):
            bg = 'white' if removables[i] is None else 'green' if removables[i] else 'red'
            text_color = 'gray' if self.board[i] == 0 else 'black'
            self.tb_elements[i].configure(
                background=bg, text=str(self.orig_board[i]), foreground=text_color)

    def save_as_csv(self, _event=None):
        filename = filedialog.asksaveasfilename(
            filetypes=(('CSV files', '*.csv'), ('All files', '*.*')),
            defaultextension='.csv', parent=self.root, title='Save sudoku as CSV')
        if not filename: return
        with open(filename, 'w') as f:
            self.backend.store_board_csv(f, self.board)

    def _get_event_sq_idx(self, event: 'tk.Event[tk.Misc]') -> int | None:
        if not isinstance(event.widget, tk.Label):
            return
        if self.root.nametowidget(event.widget.winfo_parent()) != self.table_container:
            return
        return self.tb_elements.index(event.widget)

    def on_right_click(self, event: 'tk.Event[tk.Misc]'):
        if (idx := self._get_event_sq_idx(event)) is not None:
            self.board[idx] = self.orig_board[idx]
            self.update_colors()

    def onclick(self, event: 'tk.Event[tk.Misc]'):
        idx = self._get_event_sq_idx(event)
        if idx is None:
            return
        can_remove = self.backend.can_remove_number(self.board, idx)
        if can_remove is None: return
        if not can_remove:
            self.root.bell()
            print("Can't remove this!")
            return
        self.board[idx] = 0
        self.update_colors()


def main():
    import time, cProfile
    def w_list(y: int, row: list[int]) -> list[tuple[int, int]]:
        return [(x, y) for x in row]
    basic_want: list[tuple[int, int] | int] = [
        *w_list(0, [2, 3, 5, 6]),
        *w_list(1, [1, 2, 3, 5, 6, 7]),
        *w_list(2, [0, 1, 2, 6, 7, 8]),
        *w_list(4, [0, 8]),
        *w_list(5, [0, 1, 7, 8]),
        *w_list(6, [0, 1, 4, 7, 8]),
        *w_list(7, [0, 3, 4, 5, 8]),
        *w_list(8, [0, 2, 3, 4, 5, 6, 8]),
    ]
    extra_want = [
        *w_list(1, [0, 8]),
        *w_list(0, [1, 7]),
        *w_list(0, [0, 8])
    ]
    def find_it():
        return GeneratorBackend().find_boards_matching(
            basic_want + extra_want, want_min=len(basic_want),
            print_progress=200, stop_after=10_000)
    def find_it_mp():
        return GeneratorBackend().find_boards_matching_parallel(
            basic_want + extra_want, want_min=len(basic_want),
            print_progress=200, stop_after=10_000)
    # with cProfile.Profile() as p:
    #     t0 = time.perf_counter()
    #     matches, board = find_it()
    #     t1 = time.perf_counter()
    # print(matches, board)
    # print(t1 - t0)
    board = None
    if 0 or 0:
        t0 = time.perf_counter()
        matches, board = find_it_mp()
        t1 = time.perf_counter()
        print(t1 - t0)
        print(matches, board)
    board = Board([
        0, 0, 2, 0, 0, 0, 0, 9, 0,
        4, 9, 6, 0, 0, 0, 0, 3, 7,
        0, 8, 0, 0, 0, 0, 5, 0, 0,
        0, 6, 0, 0, 1, 0, 2, 0, 0,
        0, 0, 0, 0, 7, 5, 0, 6, 0,
        2, 0, 7, 0, 3, 0, 9, 0, 0,
        0, 3, 0, 6, 0, 0, 0, 0, 0,
        7, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 3, 0, 9, 0, 0, 0,
    ])
    def is_easy(b: Board):
        return Solver(b.copy()).solve_f(include=[SolverMethod.one_occurrence_in])
    # p.print_stats(sort='cumtime')
    # p.dump_stats('./find_boards.prof')
    print(is_easy(board))
    board = None
    def is_simple(filename: str | Path):
        with open(filename) as f:
            b = GeneratorBackend().load_board_csv(f)
            s = Solver(b)
            can_s = s.solve_filtered(include=[SolverMethod.one_occurrence_in])
            print(f'{Path(filename).with_suffix("").name}: one_occurrence:', can_s, s.grid)
    for p in Path('../out/').iterdir():
        if p.suffix != '.csv': continue
        is_simple(p)
    with cProfile.Profile() as p:
        t0 = time.perf_counter()
        board = GeneratorBackend().find_hard_sudoku(initial_n=30)
        t1 = time.perf_counter()
    print(board)
    print(t1 - t0)
    p.print_stats(sort='cumtime')
    p.dump_stats('./find_boards.prof')
    TkinterFrontendApp(curr_board=board).root.mainloop()


if __name__ == '__main__':
    main()
