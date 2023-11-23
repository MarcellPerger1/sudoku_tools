from backend import GeneratorBackend, Board
import tkinter as tk
from tkinter import filedialog
import csv


def idx_to_pos(idx: int) -> tuple[int, int]:
    return idx % 9, idx // 9
def pos_to_idx(pos: tuple[int, int]):
    return pos[0] + pos[1] * 9


class TkinterFrontendApp:
    def __init__(self):
        self.backend = GeneratorBackend()
        self.orig_board = self.backend.generate_random_board()
        self.board = self.orig_board.copy()
        self.root = tk.Tk()
        self.root.title('Sudoku generator frontend (tkinter)')
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)

        self.table_container = tk.Frame(self.root, highlightthickness=1, highlightbackground='black')
        self._create_9x9_table()
        self.table_container.grid(row=1,column=1, padx=5, pady=5., columnspan=2)
        self.button_save_csv = tk.Button(self.root, text='Save as CSV', command=self.save_as_csv)
        self.button_save_csv.grid(row=2, column=1)

        self.update_colors()
        self.root.bind_all('<Button-1>', self.onclick)
        self.root.bind_all('<Button-3>', self.on_right_click)

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
            # universal newline on python so use unix dialect with \n (\r\n would be converted to \n\n)
            csv.writer(f, csv.unix_dialect).writerows(Board.flat_to_nested(self.board.grid))

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


if __name__ == '__main__':
    import time
    t0 = time.perf_counter()
    print(GeneratorBackend().find_boards_matching([*range(15)], print_progress=20,stop_after=10_000))
    t1 = time.perf_counter()
    print(t1 - t0)
    TkinterFrontendApp().root.mainloop()
