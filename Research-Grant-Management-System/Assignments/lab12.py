"""Acceptance demonstration for the supplied Lab 12 implementation."""
from pathlib import Path
import sys
SUPPORT = Path(__file__).resolve().parents[1] / "Course_Project" / "Lab_Support"
sys.path.insert(0, str(SUPPORT))


import unittest

if __name__ == "__main__":
    suite = unittest.TestSuite()
    for name in ['test_lab12_governance']:
        suite.addTests(unittest.defaultTestLoader.discover(str(SUPPORT / "tests"), pattern=name + ".py"))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
