import os

import mini_snapshot
import unittest

from solver import Solver

UPDATE = False
def setUpModule():
    if UPDATE:
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


if __name__ == '__main__':
    unittest.main()
