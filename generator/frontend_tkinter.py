from backend import GeneratorBackend, Board
import tkinter as tk


def idx_to_pos(idx: int) -> tuple[int, int]:
    return idx % 9, idx // 9
def pos_to_idx(pos: tuple[int, int]):
    return pos[0] + pos[1] * 9


class TkinterFrontendApp:
    def __init__(self):
        self.board = Board([
            1,2,3,4,5,6,7,8,9,
            4,5,6,7,8,9,1,2,3,
            7,8,9,1,2,3,4,5,6,
            5,6,4,8,9,7,2,3,1,
            2,3,1,5,6,4,8,9,7,
            8,9,7,2,3,1,5,6,4,
            3,1,2,9,7,8,6,4,5,
            9,7,8,6,4,5,3,1,2,
            6,4,5,3,1,2,9,7,8, ])
        self.root = tk.Tk()
        self.root.title('Sudoku generator frontend (tkinter)')

        self.table_container = tk.Frame(self.root)
        self._create_9x9_table()
        self.table_container.grid(row=1,column=1, padx=5, pady=5)

    def _create_9x9_table(self):
        self.tb_elements = []
        for i in range(9):
            self.table_container.columnconfigure(i, minsize=25, weight=1)
            self.table_container.rowconfigure(i, minsize=25, weight=1)
        for x in range(9):
            for y in range(9):
                num_label = tk.Label(self.table_container, text=str(self.board[(x,y)]), highlightthickness=1, highlightcolor='black', highlightbackground='black')
                num_label.grid(row=x, column=y, sticky='NSEW')
                self.tb_elements.append(num_label)
        ...

if __name__ == '__main__':
    TkinterFrontendApp().root.mainloop()
