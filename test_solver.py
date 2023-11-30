import os
import sys
import traceback
from dataclasses import dataclass
from unittest import TestCase

import mini_snapshot
import unittest

from solver import Solver


@dataclass
class _SettingsT:
    update: bool | None = None


SETTINGS = _SettingsT()


def setup_settings():
    if SETTINGS.update is None:
        try:
            with open('.snap_update.txt') as f:
                text = f.read().strip().lower()
        except (FileNotFoundError, IsADirectoryError):
            print('.snap_update.txt file not found, assuming update=False', file=sys.stderr)
            traceback.print_exc()
            text = 'no'
        if text in ('0', 'false', 'no', ''):
            SETTINGS.update = False
        elif text in ('1', 'yes', 'true'):
            SETTINGS.update = True
        else:
            SETTINGS.update = False
            print("Unknown contents of .snap_update.txt, assuming don't update",
                  file=sys.stderr)


# noinspection PyPep8Naming
def setUpModule():
    setup_settings()
    if SETTINGS.update:
        os.environ.setdefault('PY_SNAPSHOTTEST_UPDATE', '1')


class TestSolverFillOptions(mini_snapshot.SnapshotTestCase):
    def test_fill_options(self):
        s = Solver([8, 0, 4, 0, 0, 0, 0, 0, 2,
                    2, 5, 1, 7, 0, 0, 0, 0, 3,
                    0, 9, 0, 2, 0, 1, 8, 0, 7,
                    0, 0, 0, 1, 7, 0, 9, 3, 0,
                    7, 1, 9, 0, 0, 0, 0, 5, 0,
                    0, 6, 0, 9, 0, 4, 7, 8, 0,
                    1, 8, 5, 0, 6, 0, 0, 0, 0,
                    0, 0, 0, 8, 9, 3, 1, 7, 0,
                    0, 0, 0, 0, 0, 2, 4, 0, 8, ])
        s._fill_options()
        self.assertMatchesSnapshot(s.fmt())


class TestSolver(mini_snapshot.SnapshotTestCase):
    def test__solve_single_possibilities_x(self):
        s = Solver([8, 0, 4, 0, 0, 0, 0, 0, 2,
                    2, 5, 1, 7, 0, 0, 0, 0, 3,
                    0, 9, 0, 2, 0, 1, 8, 0, 7,
                    0, 0, 0, 1, 7, 0, 9, 3, 0,
                    7, 1, 9, 0, 0, 0, 0, 5, 0,
                    0, 6, 0, 9, 0, 4, 7, 8, 0,
                    1, 8, 5, 0, 6, 0, 0, 0, 0,
                    0, 0, 0, 8, 9, 3, 1, 7, 0,
                    0, 0, 0, 0, 0, 2, 4, 0, 8, ])
        s._fill_options()
        s._solve_single_possibilities_x()
        self.assertMatchesSnapshot(s.fmt())

    def test_solve_only_one_occurrence_x(self):
        s = Solver([8, 0, 4, 0, 0, 0, 0, 0, 2,
                    2, 5, 1, 7, 0, 0, 0, 0, 3,
                    0, 9, 0, 2, 0, 1, 8, 0, 7,
                    0, 0, 0, 1, 7, 0, 9, 3, 0,
                    7, 1, 9, 0, 0, 0, 0, 5, 0,
                    0, 6, 0, 9, 0, 4, 7, 8, 0,
                    1, 8, 5, 0, 6, 0, 0, 0, 0,
                    0, 0, 0, 8, 9, 3, 1, 7, 0,
                    0, 0, 0, 0, 0, 2, 4, 0, 8, ])
        s._fill_options()
        s._solve_single_possibilities_x()
        self.assertMatchesSnapshot(s.fmt())

    def test_solve(self):
        s = Solver([8, 0, 4, 0, 0, 0, 0, 0, 2,
                    2, 5, 1, 7, 0, 0, 0, 0, 3,
                    0, 9, 0, 2, 0, 1, 8, 0, 7,
                    0, 0, 0, 1, 7, 0, 9, 3, 0,
                    7, 1, 9, 0, 0, 0, 0, 5, 0,
                    0, 6, 0, 9, 0, 4, 7, 8, 0,
                    1, 8, 5, 0, 6, 0, 0, 0, 0,
                    0, 0, 0, 8, 9, 3, 1, 7, 0,
                    0, 0, 0, 0, 0, 2, 4, 0, 8, ])
        s.solve()
        self.assertTrue(s.has_solution)
        self.assertTrue(s.is_solved())
        self.assertTrue(s.check_validity())
        self.assertMatchesSnapshot(s.fmt())

    def test__solve_only_in_single_line_in_region_x(self):
        s = Solver([8, 0, 4, 0, 0, 0, 0, 0, 2,
                    2, 5, 1, 7, 0, 0, 0, 0, 3,
                    0, 9, 0, 2, 0, 1, 8, 0, 7,
                    0, 0, 0, 1, 7, 0, 9, 3, 0,
                    7, 1, 9, 0, 0, 0, 0, 5, 0,
                    0, 6, 0, 9, 0, 4, 7, 8, 0,
                    1, 8, 5, 0, 6, 0, 0, 0, 0,
                    0, 0, 0, 8, 9, 3, 1, 7, 0,
                    0, 0, 0, 0, 0, 2, 4, 0, 8, ])
        s._fill_options()
        s._solve_only_in_single_line_in_region_x()
        self.assertMatchesSnapshot(s.fmt())
        s.solve()
        self.assertTrue(s.has_solution)
        self.assertTrue(s.is_solved())
        self.assertTrue(s.check_validity())
        s2 = Solver([8, 0, 4, 0, 0, 0, 0, 0, 2,
                     2, 5, 1, 7, 0, 0, 0, 0, 3,
                     0, 9, 0, 2, 0, 1, 8, 0, 7,
                     0, 0, 0, 1, 7, 0, 9, 3, 0,
                     7, 1, 9, 0, 0, 0, 0, 5, 0,
                     0, 6, 0, 9, 0, 4, 7, 8, 0,
                     1, 8, 5, 0, 6, 0, 0, 0, 0,
                     0, 0, 0, 8, 9, 3, 1, 7, 0,
                     0, 0, 0, 0, 0, 2, 4, 0, 8, ])
        s2.solve()
        self.assertEqual(s.fmt(), s2.fmt())


if __name__ == '__main__':
    unittest.main()
