import os
import sys
import types
import unittest

# Create a lightweight "manticore" package to avoid importing optional
# dependencies required by the real top-level package.
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
package_root = os.path.join(repo_root, "manticore")
m_pkg = types.ModuleType("manticore")
m_pkg.__path__ = [package_root]
sys.modules.setdefault("manticore", m_pkg)
w_pkg = types.ModuleType("manticore.wasm")
w_pkg.__path__ = [os.path.join(package_root, "wasm")]
sys.modules.setdefault("manticore.wasm", w_pkg)
sys.path.insert(0, repo_root)

from manticore.wasm.structure import MemInst, PAGESIZE
from manticore.core.smtlib import BitVec, Operators, ConstraintSet, SelectedSolver


class DummyState:
    """Minimal state object providing solver utilities for memory tests."""

    def __init__(self):
        self.constraints = ConstraintSet()
        self._solver = SelectedSolver.instance()

    def solve_n(self, expr, n):
        return self._solver.get_all_values(self.constraints, expr, n, silent=True)

    def must_be_true(self, expr):
        return self._solver.must_be_true(self.constraints, expr)

    def can_be_true(self, expr):
        return self._solver.can_be_true(self.constraints, expr)

    def copy(self):
        other = DummyState()
        for c in self.constraints:
            other.constraints.add(c)
        return other


class TestSymbolicMemory(unittest.TestCase):
    def test_symbolic_read(self):
        mem = MemInst([0x0] * PAGESIZE)
        state = DummyState()
        idx = BitVec(32, "idx")
        state.constraints.add(Operators.ULT(idx, 2))
        mem.write_bytes(0, [0xAA, 0xBB])

        st0 = state.copy()
        st0.constraints.add(idx == 0)
        val0 = mem.read_bytes(idx, 1, state=st0)[0]
        self.assertEqual(st0.solve_n(val0, 1)[0], 0xAA)

        st1 = state.copy()
        st1.constraints.add(idx == 1)
        val1 = mem.read_bytes(idx, 1, state=st1)[0]
        self.assertEqual(st1.solve_n(val1, 1)[0], 0xBB)

    def test_symbolic_write(self):
        mem = MemInst([0x0] * PAGESIZE)
        state = DummyState()
        idx = BitVec(32, "idx")
        state.constraints.add(Operators.ULT(idx, 2))
        mem.write_bytes(idx, [0xCC], state=state)

        st0 = state.copy()
        st0.constraints.add(idx == 0)
        b0 = mem.read_bytes(0, 1, state=st0)[0]
        b1 = mem.read_bytes(1, 1, state=st0)[0]
        self.assertEqual(st0.solve_n(b0, 1)[0], 0xCC)
        self.assertEqual(st0.solve_n(b1, 1)[0], 0x00)

        st1 = state.copy()
        st1.constraints.add(idx == 1)
        b0_1 = mem.read_bytes(0, 1, state=st1)[0]
        b1_1 = mem.read_bytes(1, 1, state=st1)[0]
        self.assertEqual(st1.solve_n(b0_1, 1)[0], 0x00)
        self.assertEqual(st1.solve_n(b1_1, 1)[0], 0xCC)


if __name__ == "__main__":
    unittest.main()

