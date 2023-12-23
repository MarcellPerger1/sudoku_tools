from __future__ import annotations

import contextlib
from dataclasses import dataclass
from enum import StrEnum
from typing import Self, Generic, TypeVar, TypeAlias, Callable, Iterable

from board import Board
from solver import Solver, SolverMethod, SolverFilterDefault


class BaseSolutionStep:
    method: SolverMethod  # ClassVar
    pos: tuple[int, int]

    def fmt(self) -> str:
        raise NotImplementedError('BaseSolutionStep.fmt')


T = TypeVar('T')
U = TypeVar('U')


class FromInto(Generic[T]):
    def clone_self(self):
        """Hook to allow mutable classes to use .copy etc. to be cloned"""
        return self

    @classmethod
    def cant_convert(cls, other: object):
        """Hook to customise default message"""
        raise NotImplementedError(
            f"Unknown conversion from {type(other).__name__} to {cls.__name__}")

    @classmethod
    def from_(cls, other: Self | T) -> Self:
        if isinstance(other, cls):
            return other.clone_self()
        cls.cant_convert(other)

    def into(self, target: type[U]) -> U:
        return target.from_(self)


LineDirnF: TypeAlias = 'LineDirn'


class SeqDirn(FromInto[LineDirnF], StrEnum):
    row = 'row'
    column = 'column'
    region = 'region'

    @classmethod
    def from_(cls, other: Self | LineDirn) -> Self:
        if isinstance(other, LineDirn):
            match other:
                case LineDirn.row: return cls.row
                case LineDirn.column: return cls.column
        return super().from_(other)


class LineDirn(FromInto[SeqDirn], StrEnum):
    row = 'row'
    column = 'column'

    @classmethod
    def from_(cls, other: SeqDirn | Self) -> Self:
        if isinstance(other, SeqDirn):
            match other:
                case SeqDirn.row: return cls.row
                case SeqDirn.column: return cls.column
                case _: raise TypeError("Can't convert SeqDirn.region to LineDirn")
        return super().from_(other)


@dataclass(frozen=True)
class SinglePossibilityStep(BaseSolutionStep):
    method = SolverMethod.single_possibility

    pos: tuple[int, int]
    num: int

    def fmt(self) -> str:
        return f'SinglePossi: at {self.pos}, only value: num={self.num}'


@dataclass(frozen=True)
class OneOccurrenceStep(BaseSolutionStep):
    method = SolverMethod.one_occurrence_in

    pos: tuple[int, int]
    num: int
    dirn: SeqDirn

    def fmt(self):
        return f'OneOccurrence: in {self.dirn}, num={self.num} only at {self.pos}'


@dataclass(frozen=True)
class LineInRegionStep(BaseSolutionStep):
    method = SolverMethod.line_in_region

    pos: tuple[int, int]
    source_region: tuple[int, int]
    line_dirn: LineDirn
    line_i: int
    removed: int

    def fmt(self) -> str:
        return (f'LineInRegion: in region {self.source_region}, num={self.removed}'
                f' is only in {self.line_i}th {self.line_dirn} => removed it from {self.pos}')


TraceHandlerT: TypeAlias = 'Callable[[TracingSolver, tuple[int, int]], None]'
SinglePossibDataT: TypeAlias = 'SeqDirn'
LineInRegionDataT: TypeAlias = 'tuple[LineDirn, tuple[int, int]]'
AnyDataT: TypeAlias = 'SinglePossibDataT | LineInRegionDataT | None'
TRACE_HANDLERS: dict[SolverMethod, TraceHandlerT] = {}


def add_handler(method: SolverMethod, **_kw):
    assert not _kw
    def decorator(orig_func: TraceHandlerT):
        TRACE_HANDLERS[method] = orig_func
        return orig_func
    return decorator

class TracingSolver(Solver):
    def __init__(self,  board: list[int] | Board, debug: bool = True):
        super().__init__(board, debug)
        self._curr_method: SolverMethod | None = None
        self._curr_data: AnyDataT = None
        self.output: list[BaseSolutionStep] = []

    def get_solution_steps(self):
        self.solve()
        return self.output

    def get_solution_steps_f(self, default: SolverFilterDefault = None,
                include: Iterable[SolverMethod] = None,
                exclude: Iterable[SolverMethod] = None):
        self.solve_filtered(default, include, exclude)
        return self.output

    @contextlib.contextmanager
    def _step_context(self, method: SolverMethod, data: AnyDataT):
        orig_ctx = self._curr_method, self._curr_data
        self._curr_method = method
        self._curr_data = data
        try:
            yield self
        finally:
            self._curr_method, self._curr_data = orig_ctx

    def _solve_single_possibilities(self, update_options: bool=True) -> bool:
        with self._step_context(SolverMethod.single_possibility, None):
            return super()._solve_single_possibilities(update_options)

    def _solve_1_occurrence_x_col(self, x: int, update_options: bool = True) -> bool:
        with self._step_context(SolverMethod.one_occurrence_in, SeqDirn.column):
            return super()._solve_1_occurrence_x_col(x, update_options)

    def _solve_1_occurrence_y_row(self, y: int, update_options: bool = True) -> bool:
        with self._step_context(SolverMethod.one_occurrence_in, SeqDirn.row):
            return super()._solve_1_occurrence_y_row(y, update_options)

    def _solve_1_occurrence_region(self, r_idx_x: int, r_idx_y: int, update_options: bool = True) -> bool:
        with self._step_context(SolverMethod.one_occurrence_in, SeqDirn.region):
            return super()._solve_1_occurrence_region(r_idx_x, r_idx_y, update_options)

    def _solve_single_x_col_in_region(self, r_idx_x: int, r_idx_y: int, update_options=True):
        data = (LineDirn.column, (r_idx_x, r_idx_y))
        with self._step_context(SolverMethod.line_in_region, data):
            return super()._solve_single_x_col_in_region(r_idx_x, r_idx_y, update_options)

    def _solve_single_y_row_in_region(self, r_idx_x: int, r_idx_y: int, update_options=True):
        data = (LineDirn.row, (r_idx_x, r_idx_y))
        with self._step_context(SolverMethod.line_in_region, data):
            return super()._solve_single_y_row_in_region(r_idx_x, r_idx_y, update_options)

    def _get_handler(self) -> TraceHandlerT:
        return TRACE_HANDLERS[self._curr_method]

    def _update_pos(self, pos: tuple[int, int]):
        self._get_handler()(self, pos)
        return super()._update_pos(pos)

    @add_handler(SolverMethod.single_possibility)
    def _trace_single_possibility(self, pos: tuple[int, int]):
        self.output.append(SinglePossibilityStep(pos, self.get_pos(pos)))

    @add_handler(SolverMethod.one_occurrence_in)
    def _trace_one_occurrence(self, pos: tuple[int, int]):
        self.output.append(OneOccurrenceStep(pos, self.get_pos(pos), self._curr_data))

    @add_handler(SolverMethod.line_in_region)
    def _trace_line_in_region(self, pos: tuple[int, int]):
        line_dirn: LineDirn
        region: tuple[int, int]
        line_dirn, region = self._curr_data
        match line_dirn:
            case LineDirn.row:  # x dirn => idx=y value
                _, line_i = pos
            case LineDirn.column:  # y dirn => idx=x value
                line_i, _ = pos
            case _: raise TypeError("Expected line_dirn to be LineDirn")
        self.output.append(LineInRegionStep(pos, region, line_dirn, line_i, self._trace_removed_))
