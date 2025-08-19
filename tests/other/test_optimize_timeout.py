import unittest
from unittest.mock import patch

from manticore.core.smtlib import ConstraintSet
from manticore.core.smtlib.solver import Z3Solver
from manticore import config


class OptimizeTimeoutTest(unittest.TestCase):
    def test_generic_returns_model_on_timeout(self):
        consts = config.get_group("smt")
        solver = Z3Solver.instance()
        with consts.temp_vals():
            consts.timeout = 0
            consts.optimize = False
            consts.return_on_timeout = True
            cs = ConstraintSet()
            a = cs.new_bitvec(32)
            cs.add(a > 0)
            cs.add(a < 10)
            value = solver.max(cs, a)
            self.assertTrue(0 < value < 10)

    def test_fancy_returns_model_on_timeout(self):
        consts = config.get_group("smt")
        solver = Z3Solver.instance()
        cs = ConstraintSet()
        a = cs.new_bitvec(32)
        cs.add(a > 0)
        cs.add(a < 10)
        with consts.temp_vals():
            consts.optimize = True
            consts.return_on_timeout = True
            with patch.object(solver._smtlib, "recv", return_value="unknown"), \
                 patch.object(solver, "_getvalue", return_value=7):
                self.assertEqual(solver.max(cs, a), 7)

