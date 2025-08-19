import unittest
from manticore.native.memory import LazySMemory32
from manticore.core.smtlib import ConstraintSet


class ScanMemTest(unittest.TestCase):
    def test_scan_mem_symbolic(self):
        cs = ConstraintSet()
        mem = LazySMemory32(cs)
        mem.mmap(0, 0x1000, "rwx", name="map")

        # Write concrete pattern
        mem.write(0, b"ABAB")

        # Region with symbolic bytes that could match
        s1 = cs.new_bitvec(8)
        s2 = cs.new_bitvec(8)
        mem.write(100, [s1, s2])

        # Region with symbolic bytes that cannot match due to constraints
        s3 = cs.new_bitvec(8)
        s4 = cs.new_bitvec(8)
        cs.add(s3 != ord('A'))
        cs.add(s4 == ord('B'))
        mem.write(200, [s3, s4])

        hits = set(mem.scan_mem(b"AB"))
        self.assertIn(0, hits)
        self.assertIn(2, hits)
        self.assertIn(100, hits)
        self.assertNotIn(200, hits)


if __name__ == "__main__":
    unittest.main()
