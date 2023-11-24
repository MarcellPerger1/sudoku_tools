from __future__ import annotations

from collections import UserList
from collections.abc import MutableSequence
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar('T')

@dataclass
class Board:
    grid: list[int]

    def __post_init__(self):
        if not isinstance(self.grid, (list, UserList, MutableSequence)):
            raise TypeError("grid must be a list")
        if len(self.grid) != 81:
            raise ValueError("grid must have 81 elements (9x9)")
        if not all(v in range(0, 10) for v in self.grid):
            raise ValueError("Each element of grid must be 0-9")

    @classmethod
    def swap_rows(cls, nested: list[list[T]]) -> list[list[T]]:
        return [[nested[x][y] for x in range(9)] for y in range(9)]
    to_printable_order = swap_rows

    @classmethod
    def nested_to_flat(cls, nested: list[list[T]]) -> list[T]:
        assert len(nested) == 9 and all(len(v) == 9 for v in nested)
        return [v for y_list in nested for v in y_list]

    @classmethod
    def flat_to_nested(cls, flat: list[T]) -> list[list[T]]:
        assert len(flat) == 81
        return [[flat[cls.pos_to_idx((x, y))] for y in range(9)] for x in range(9)]

    def copy(self):
        return Board(self.grid.copy())

    def __getitem__(self, item: tuple[int, int] | int | slice):
        if isinstance(item, (int, slice)):
            return self.grid[item]
        return self.grid[self.pos_to_idx(item)]

    def __setitem__(self, key: tuple[int, int] | int | slice, value: int):
        if isinstance(key, (int, slice)):
            self.grid[key] = value
            return
        self.grid[self.pos_to_idx(key)] = value

    @classmethod
    def idx_to_pos(cls, idx: int) -> tuple[int, int]:
        return idx % 9, idx // 9

    @classmethod
    def pos_to_idx(cls, pos: tuple[int, int]):
        return pos[0] + pos[1] * 9