from __future__ import annotations

import itertools
import sys
from collections import Counter
from dataclasses import dataclass
from typing import IO

TUPLE_RANGE9 = TUPLE_0_TO_8 = tuple(range(9))
SET_1_TO_9 = frozenset(range(1, 9+1))
TUPLE_1_TO_9 = tuple(range(1, 9+1))

@dataclass
class SquareInfo:
    value: int  # 0 = unknown
    options: set[int]
    pos: tuple[int, int]

    def fmt(self):
        return str(self.value) if self.value != 0 else str(self.options)


#  0  1  2  3 ...
#  9 10 11 12 ...
# 18 19 20 21 ...
# ...
def idx_to_pos(idx: int) -> tuple[int, int]:
    return idx % 9, idx // 9
def pos_to_idx(pos: tuple[int, int]):
    return pos[0] + pos[1] * 9


class Solver:
    grid: list[SquareInfo]

    def __init__(self, grid: list[int]):
        self.grid = [
            SquareInfo(v, set(SET_1_TO_9) if v == 0 else {v}, idx_to_pos(i))
            for i, v in enumerate(grid)]

    def get_pos(self, pos: tuple[int, int]):
        return self.grid[pos_to_idx(pos)]

    def print(self, file: IO[str]=None, end='\n'):
        if file is None: file = sys.stdout
        for y in range(9):
            for x in range(9):
                print(f'{self.get_pos((x, y)).fmt():<27}',
                      end=' ' if x != 8 else '', file=file)
            print(file=file, end='\n' if y != 8 else end)

    def fmt(self) -> str:
        return '\n'.join(
            ' '.join(f'{self.get_pos((x, y)).fmt():<27}'
                     for x in range(9)) for y in range(9))

    def solve(self):
        self._fill_options()

    def _solve_only_one_occurrence_x(self):
        while self._solve_only_one_occurrence(True):
            ...

    def _solve_only_one_occurrence(self, update_options: bool = True) -> bool:
        changed = False
        for x in range(9):
            if self._solve_1_occurrence_x_col(x, update_options):
                changed = True
        for y in range(9):
            if self._solve_1_occurrence_y_row(y, update_options):
                changed = True
        for ix in range(3):
            for iy in range(3):
                if self._solve_1_occurrence_region(ix, iy, update_options):
                    changed = True
        return changed
    def _solve_1_occurrence_x_col(self, x: int, update_options: bool = True) -> bool:
        return self._handle_1_occurrence_in_seq([self.get_pos((x, y)) for y in TUPLE_RANGE9], update_options)
        # nums_in_col: list[tuple[int, None | int]] = [(0, None)] * 9
        # for y, sq in enumerate(column):
        #     if sq.value != 0: continue
        #     for num in sq.options:
        #         if nums_in_col[num][0] == 0:
        #             nums_in_col[num] = (1, y)  # none yet, so add this
        #         else:
        #             nums_in_col[num] = (2, None)  # already have it, invalidate
        # for num, (_count, y) in enumerate(nums_in_col):
        #     if y is not None:
        #         column[y].value = num
        #         column[y].options = {num}

    def _solve_1_occurrence_y_row(self, y: int, update_options: bool = True) -> bool:
        return self._handle_1_occurrence_in_seq([self.get_pos((x, y)) for x in TUPLE_RANGE9], update_options)

    def _solve_1_occurrence_region(self, r_idx_x: int, r_idx_y: int, update_options: bool = True) -> bool:
        rx0 = r_idx_x * 3
        ry0 = r_idx_y * 3
        return self._handle_1_occurrence_in_seq([
            self.get_pos((x, y)) for x in range(rx0, rx0+3) for y in range(ry0, ry0+3)], update_options)

    def _handle_1_occurrence_in_seq(self, seq: list[SquareInfo], update_options: bool = True) -> bool:
        changed = False
        options_nums: Counter[int] = Counter(itertools.chain.from_iterable(
            # also include if value == 0 because then, it won't try to
            # place a num somewhere else that's already actually in the row
            [v.options for v in seq]))
        for num, count in options_nums.items():
            if count != 1: continue
            # only iterate if we've guaranteed found something
            for sq in seq:
                # only change if nothing already there
                if num in sq.options and sq.value == 0:
                    sq.options = {num}
                    sq.value = num
                    if update_options:
                        self._update_pos(sq.pos)
                    changed = True
                    break
        return changed

    def _update_pos(self, pos: tuple[int, int]):
        x, y = pos
        self._fill_options_x_col(x)
        self._fill_options_y_row(y)
        self._fill_options_region(x // 3, y // 3)

    def _solve_single_possibilities_x(self):
        while self._solve_single_possibilities(True):
            pass

    def _solve_single_possibilities(self, update_options: bool=True) -> bool:
        changed = False
        if not update_options:
            for x in range(9):
                for y in range(9):
                    sq = self.get_pos((x, y))
                    if sq.value == 0 and len(sq.options) == 1:
                        (sq.value,) = sq.options
                        changed = True
        else:
            for x in range(9):
                for y in range(9):
                    sq = self.get_pos((x, y))
                    if sq.value == 0 and len(sq.options) == 1:
                        (sq.value,) = sq.options
                        # can update it inside the loop as usually only one
                        # square per row needs to be changed but it makes
                        # insanely hard to debug
                        self._update_pos((x, y))
                        changed = True
        return changed

    def _fill_options(self):
        for x in range(9):
            self._fill_options_x_col(x)
        for y in range(9):
            self._fill_options_y_row(y)
        for rx in range(3):
            for ry in range(3):
                self._fill_options_region(rx, ry)

    def _fill_options_x_col(self, x: int):
        definite_nums = {self.get_pos((x, y)).value for y in range(9)}
        definite_nums -= {0}
        for y in range(9):
            sq = self.get_pos((x, y))
            if sq.value == 0:
                sq.options -= definite_nums

    def _fill_options_y_row(self, y: int):
        definite_nums = {self.get_pos((x, y)).value for x in range(9)}
        definite_nums -= {0}
        for x in range(9):
            sq = self.get_pos((x, y))
            if sq.value == 0:
                sq.options -= definite_nums

    def _fill_options_region(self, r_idx_x: int, r_idx_y: int):
        rx0 = r_idx_x * 3
        ry0 = r_idx_y * 3
        definite_nums = {self.get_pos((x, y)).value
                         for x in range(rx0, rx0 + 3)
                         for y in range(ry0, ry0 + 3)}
        definite_nums -= {0}
        for x in range(rx0, rx0 + 3):
            for y in range(ry0, ry0 + 3):
                sq = self.get_pos((x, y))
                if sq.value == 0:
                    sq.options -= definite_nums


def perf_it():
    import timeit, io

    sio = io.StringIO()

    def print2(arg):
        print(arg)
        print(arg, file=sio)

    def make_solver():
        return Solver([8, 0, 4, 0, 0, 0, 0, 0, 2,
                       2, 5, 1, 7, 0, 0, 0, 0, 3,
                       0, 9, 0, 2, 0, 1, 8, 0, 7,
                       0, 0, 0, 1, 7, 0, 9, 3, 0,
                       7, 1, 9, 0, 0, 0, 0, 5, 0,
                       0, 6, 0, 9, 0, 4, 7, 8, 0,
                       1, 8, 5, 0, 6, 0, 0, 0, 0,
                       0, 0, 0, 8, 9, 3, 1, 7, 0,
                       0, 0, 0, 0, 0, 2, 4, 0, 8, ])

    print2('_make_solver')
    print2(min(timeit.repeat(make_solver, number=10_000)))
    def make_solver_and_fill_options():
        make_solver()._fill_options()
    print2('_make_solver + _fill_options')
    print2(min(timeit.repeat(make_solver_and_fill_options, number=10_000)))

    def ms_fo_solve_single_possibilities():
        s = make_solver()
        s._fill_options()
        s._solve_single_possibilities(True)
    print2('_make_solver + _fill_options + _solve_single_possibilities(True)')
    print2(min(timeit.repeat(ms_fo_solve_single_possibilities, number=10_000)))

    def ms_fo_solve_single_possibilities_f():
        s = make_solver()
        s._fill_options()
        s._solve_single_possibilities(False)
    print2('_make_solver + _fill_options + _solve_single_possibilities(False)')
    print2(min(timeit.repeat(ms_fo_solve_single_possibilities_f, number=10_000)))

    def ms_fo_solve_1_o():
        s = make_solver()
        s._fill_options()
        s._solve_only_one_occurrence(True)
    print2('_make_solver + _fill_options + _solve_only_one_occurrence(True)')
    print2(min(timeit.repeat(ms_fo_solve_1_o, number=10_000)))

    def ms_fo_solve_1_o_f():
        s = make_solver()
        s._fill_options()
        s._solve_only_one_occurrence(False)
    print2('_make_solver + _fill_options + _solve_only_one_occurrence(False)')
    print2(min(timeit.repeat(ms_fo_solve_1_o_f, number=10_000)))

    with open('perf_result.txt', 'w') as f:
        f.write(sio.getvalue())


def main():
    print('hello world')
    s = Solver([8,0,4,0,0,0,0,0,2,
                2,5,1,7,0,0,0,0,3,
                0,9,0,2,0,1,8,0,7,
                0,0,0,1,7,0,9,3,0,
                7,1,9,0,0,0,0,5,0,
                0,6,0,9,0,4,7,8,0,
                1,8,5,0,6,0,0,0,0,
                0,0,0,8,9,3,1,7,0,
                0,0,0,0,0,2,4,0,8,])
    s._fill_options()
    print('Final:')
    s.print()


    def _write_fill_snap():
        with open('./fill_snapshot.txt', 'w') as f:
            s.print(f, end='')
    # _write_fill_snap()
    with open('./fill_snapshot.txt') as f:
        expected = f.read()
    actual = s.fmt()
    print('Actual')
    print(actual)
    print('Expected')
    print(expected)
    assert actual == expected
    s._solve_single_possibilities(True)
    print('After single possible')
    s.print()
    print('After single possible x')
    s._solve_single_possibilities_x()
    s.print()

    print('After solve_only_one_occurrence')
    s2 = Solver([8, 0, 4, 0, 0, 0, 0, 0, 2,
                2, 5, 1, 7, 0, 0, 0, 0, 3,
                0, 9, 0, 2, 0, 1, 8, 0, 7,
                0, 0, 0, 1, 7, 0, 9, 3, 0,
                7, 1, 9, 0, 0, 0, 0, 5, 0,
                0, 6, 0, 9, 0, 4, 7, 8, 0,
                1, 8, 5, 0, 6, 0, 0, 0, 0,
                0, 0, 0, 8, 9, 3, 1, 7, 0,
                0, 0, 0, 0, 0, 2, 4, 0, 8, ])
    s2._fill_options()
    s2._solve_only_one_occurrence()
    s2.print()
    print('After solve_only_one_occurrence_x')
    s2._solve_only_one_occurrence_x()
    s2.print()
    # perf_it()




if __name__ == '__main__':
    main()